from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from django.db.models import Count
from app.models.interaction import Interaction
from app.serializers.output.interaction import InteractionOutputSerializer

# --- Endpoint 1: Recent Interactions ---

class RecentInteractionsView(ListAPIView):
    """
    Retrieves a paginated list of recent interactions (calls, messages, etc.)
    for the currently authenticated user.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = InteractionOutputSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # Get the logged-in user
        user = self.request.user
        
        # Filter by interaction type if the query param 'type' is provided
        interaction_type = self.request.query_params.get('type', None)
        
        # Build the query: filter by the user who initiated the interaction
        queryset = Interaction.objects.filter(initiator=user)
        
        if interaction_type in Interaction.InteractionType.values:
            queryset = queryset.filter(interaction_type=interaction_type)
            
        # The ordering ('-created_at') is handled by the model's Meta class
        return queryset

# --- Endpoint 2: Top Contacts ---

class TopContactsView(APIView):
    """
    Identifies a user's most frequently contacted phone numbers
    based on their interaction history.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # Get the logged-in user
        user = self.request.user
        
        # Get the 'top_n' query param, default to 5
        try:
            top_n = int(request.query_params.get('top_n', 5))
        except ValueError:
            top_n = 5 # Fallback if 'top_n' is not a valid number
        
        # This is an aggregation query:
        # 1. Filter interactions by the logged-in user
        # 2. Group by the 'receiver_phone_number'
        # 3. Annotate (add) a 'interaction_count' for each group
        # 4. Order by the count in descending order
        # 5. Take the top N results
        top_contacts = Interaction.objects.filter(
            initiator=user
        ).values(
            'receiver_phone_number'
        ).annotate(
            interaction_count=Count('id')
        ).order_by(
            '-interaction_count'
        )[:top_n]
        
        return Response(top_contacts)

# --- Endpoint 3: Spam Report Statistics ---

class SpamReportStatsView(APIView):
    """
    Aggregates spam reports, showing counts per phone number.
    Can be filtered by date.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # Get query params for date range filtering
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        # Start with all spam reports
        queryset = Interaction.objects.filter(
            interaction_type=Interaction.InteractionType.SPAM_REPORT
        )
        
        # Apply date filters if provided
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        # This is another aggregation query:
        # 1. Group by 'receiver_phone_number'
        # 2. Annotate a 'report_count' for each group
        # 3. Order by the count
        spam_stats = queryset.values(
            'receiver_phone_number'
        ).annotate(
            report_count=Count('id')
        ).order_by(
            '-report_count'
        )
        
        return Response(spam_stats)
