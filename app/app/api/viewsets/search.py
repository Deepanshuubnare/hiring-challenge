from rest_framework.response import Response
from app.models.user import User
from app.models.contact import Contact
# We no longer need TrigramSimilarity, but we still need Q and Value
from django.db.models import Q, Value, IntegerField
from app.serializers import output
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from app.utils import normalize_phone_number # Import our phone utility
from rest_framework.pagination import PageNumberPagination
from app.models.scam import ScamRecord
import uuid # For the detail view

# This helper function is still good
def get_query_type(query):
    try:
        # Check if query consists only of digits, '+', '(', ')', '-'
        if all(c in '0123456789+-()' for c in query):
            return 'phone_number'
        else:
            return 'name'
    except Exception:
        return None

# Use a standard Django paginator
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SearchView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    output_serializer_class = output.SearchOutputSerializer
    pagination_class = StandardResultsSetPagination

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or None.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def get(self, request):
        query = request.query_params.get('q', None)

        if not query:
            return Response({'error': 'Search query is required.'}, status=400)
        
        search_type = get_query_type(query)
        
        # A list to hold all our results
        final_results = []
        # A set to track phone numbers we've already added, to prevent duplicates
        seen_phone_numbers = set()

        # Helper function to add results and de-duplicate
        def add_to_results(queryset):
            for item in queryset:
                if item.phone_number not in seen_phone_numbers:
                    final_results.append(item)
                    seen_phone_numbers.add(item.phone_number)

        if search_type == 'phone_number':
            # --- Phone Search Logic ---
            normalized_phone = normalize_phone_number(query)
            
            # Rank 1: Exact match in Users
            users_exact = User.objects.filter(
                phone_number=normalized_phone
            ).annotate(rank=Value(1, IntegerField()))
            add_to_results(users_exact)
            
            # Rank 2: Exact match in Contacts
            contacts_exact = Contact.objects.filter(
                phone_number=normalized_phone
            ).annotate(rank=Value(2, IntegerField()))
            add_to_results(contacts_exact)

        elif search_type == 'name':
            # --- Name Search Logic (Using 'icontains' for SQLite) ---

            # --- THIS IS THE MODIFIED QUERY ---
            # Rank 3: Users whose name contains the query
            users_by_name = User.objects.annotate(
                rank=Value(3, IntegerField())
            ).filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by('first_name') # Order alphabetically
            add_to_results(users_by_name)
            
            # --- THIS IS THE MODIFIED QUERY ---
            # Rank 4: Contacts whose name contains the query
            contacts_by_name = Contact.objects.annotate(
                rank=Value(4, IntegerField())
            ).filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by('first_name') # Order alphabetically
            add_to_results(contacts_by_name)

        # Paginate the final, de-duplicated, ranked list
        if self.paginator:
            page = self.paginator.paginate_queryset(final_results, request, view=self)
            if page is not None:
                output_serializer = self.output_serializer_class(page, many=True)
                return self.paginator.get_paginated_response(output_serializer.data)

        # Fallback if paginator is not set (should not happen)
        output_serializer = self.output_serializer_class(final_results, many=True)
        return Response(output_serializer.data)


class SearchDetailsView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    output_user_serializer_class = output.SearchDetailsUserOutputSerializer
    output_contact_serializer_class = output.ContactOutputSerializer

    def get(self, request, id):
        # We must try to find a User first.
        try:
            # We must convert the string 'id' from the URL into a UUID object
            user_uuid = uuid.UUID(str(id), version=4)
            user = User.objects.get(id=user_uuid)
            
            # We found a registered User. Now check for privacy.
            is_contact_of_user = Contact.objects.filter(
                created_by=request.user, 
                phone_number=user.phone_number
            ).exists()
            
            output_serializer = self.output_user_serializer_class(user)
            data = output_serializer.data
            
            # If the user is NOT in the searcher's contact list, hide the email.
            if not is_contact_of_user:
                data.pop('email', None) # Remove email if it exists
                
            # Add spam count
            data['spam_count'] = ScamRecord.objects.filter(phone_number=user.phone_number).count()
            return Response(data)

        except User.DoesNotExist:
            # If a User is not found, it must be a Contact.
            try:
                contact_uuid = uuid.UUID(str(id), version=4)
                contact = Contact.objects.get(id=contact_uuid)
                
                output_serializer = self.output_contact_serializer_class(contact)
                data = output_serializer.data
                
                # Add spam count
                data['spam_count'] = ScamRecord.objects.filter(phone_number=contact.phone_number).count()
                return Response(data)
                
            except (Contact.DoesNotExist, ValueError):
                # If neither is found, or the ID is not a valid UUID
                return Response({'error': 'Record not found.'}, status=404)
        
        except ValueError:
             # This catches if the 'id' from the URL is not a valid UUID
             return Response({'error': 'Invalid ID format.'}, status=400)

