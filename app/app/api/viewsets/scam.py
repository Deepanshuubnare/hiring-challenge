from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from app.serializers import input, output
from app.models.scam import ScamRecord
from django.db import transaction

# --- 1. IMPORT THE INTERACTION MODEL ---
from app.models.interaction import Interaction

class CreateScamRecord(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    input_serializer_class = input.CreateScamRecordInputSerializer
    output_serializer_class = output.ScamRecordOutputSerializer

    def post(self, request):
        # We need to pass the request context to the serializer
        input_serializer = self.input_serializer_class(
            data=request.data, 
            context={'request': request}
        )
        input_serializer.is_valid(raise_exception=True)
        user = request.user
        
        with transaction.atomic():
            try:
                scam = ScamRecord.objects.create(
                    reported_by=user,
                    created_by=user,
                    updated_by=user,
                    **input_serializer.validated_data
                )

                # --- 2. ADD THIS LOGIC ---
                # This links Part 1 to Part 2.
                # It creates an Interaction record for the dashboard.
                Interaction.objects.create(
                    initiator=user,
                    receiver_phone_number=scam.phone_number, # <-- Correct field name
                    interaction_type='spam' # <-- Correct field name
                )
                
                # --- End of new logic ---

                output_serializer = self.output_serializer_class(scam)
            except Exception as e:
                return Response({'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
