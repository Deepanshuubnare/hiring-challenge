from rest_framework import serializers
from app.utils import normalize_phone_number
from app.models.scam import ScamRecord

class CreateScamRecordInputSerializer(serializers.Serializer):
    # Remove length checks
    phone_number = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_phone_number(self, value):
        # Normalize the phone number
        normalized_phone = normalize_phone_number(value)
        
        # Optional: Add a check for duplicate spam reports by this user
        user = self.context['request'].user
        if ScamRecord.objects.filter(reported_by=user, phone_number=normalized_phone).exists():
            raise serializers.ValidationError("You have already reported this number as spam.")
            
        return normalized_phone

    
