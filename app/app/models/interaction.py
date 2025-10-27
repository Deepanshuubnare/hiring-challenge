from django.db import models
from django.conf import settings
import uuid

class Interaction(models.Model):
    """
    Model to store all user interactions (calls, messages, etc.)
    """
    
    class InteractionType(models.TextChoices):
        CALL = 'call', 'Call'
        MESSAGE = 'message', 'Message'
        SPAM_REPORT = 'spam_report', 'Spam Report'

    # Standard fields from your other models
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")
    
    # Initiator: The logged-in user who starts the action
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_interactions'
    )
    
    # Receiver: We store the phone number, as the receiver might
    # not be a registered user (e.g., a contact).
    receiver_phone_number = models.CharField(max_length=20)
    
    # Type of interaction
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices
    )
    
    # Timestamp (we can just use created_at for this)
    
    # Metadata: For storing things like call duration
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at'] # Show newest interactions first

    def __str__(self):
        return f"{self.initiator} -> {self.receiver_phone_number} ({self.get_interaction_type_display()})"
