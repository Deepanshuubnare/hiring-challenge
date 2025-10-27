from rest_framework import serializers
from app.models.interaction import Interaction

class InteractionOutputSerializer(serializers.ModelSerializer):
    """
    Serializer to display a user's interactions.
    """
    
    # We use get_interaction_type_display() to show the
    # human-readable value (e.g., "Call") instead of the
    # database value (e.g., "call").
    interaction_type = serializers.CharField(source='get_interaction_type_display')
    
    class Meta:
        model = Interaction
        # These are the fields we want to show in the API
        fields = [
            'id',
            'created_at',
            'receiver_phone_number',
            'interaction_type',
            'metadata'
        ]
