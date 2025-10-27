from rest_framework import serializers
from app.utils import normalize_phone_number
from app.models.contact import Contact

class CreateContactInputSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    # Remove length checks, we will normalize it instead
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        # Normalize the phone number
        normalized_phone = normalize_phone_number(value)
        
        # Optional: Add a check for duplicate contacts by this user
        user = self.context['request'].user
        if Contact.objects.filter(created_by=user, phone_number=normalized_phone).exists():
             raise serializers.ValidationError("You have already added this contact.")
            
        return normalized_phone