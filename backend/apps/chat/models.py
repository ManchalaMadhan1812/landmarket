from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.properties.models import Property
import uuid

class ChatRoom(models.Model):
    """
    Chat room model for property-related conversations.
    Can be between buyer-seller, buyer-agent, or multiple participants.
    """
    
    ROOM_TYPES = [
        ('direct', 'Direct Message'),
        ('property', 'Property Inquiry'),
        ('group', 'Group Chat'),
        ('support', 'Customer Support'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='direct')
    name = models.CharField(max_length=255, blank=True)
    
    # Property reference for property-related chats
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_rooms'
    )
    
    # Participants in the chat
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChatParticipant',
        related_name='chat_rooms'
    )
    
    # Room metadata
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['room_type', 'is_active']),
            models.Index(fields=['property', 'is_active']),
            models.Index(fields=['last_message_at']),
        ]
    
    def __str__(self):
        if self.property:
            return f"Chat about {self.property.title}"
        elif self.name:
            return self.name
        else:
            return f"Chat Room {self.id}"
    
    def get_participant_names(self, exclude_user=None):
        """Get names of all participants except excluded user"""
        participants = self.participants.all()
        if exclude_user:
            participants = participants.exclude(id=exclude_user.id)
        return [participant.get_full_name() for participant in participants]
    
    def update_last_message(self, message_text):
        """Update last message info for the room"""
        self.last_message = message_text[:100]  # Truncate if too long
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message', 'last_message_at', 'updated_at'])


class ChatParticipant(models.Model):
    """
    Intermediate model for chat room participants with additional metadata.
    """
    
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('agent', 'Agent'),
        ('support', 'Support Agent'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    is_admin = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Read status
    last_read_at = models.DateTimeField(auto_now_add=True)
    unread_count = models.IntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['chat_room', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.chat_room}"
    
    def mark_as_read(self):
        """Mark all messages as read for this participant"""
        from .models import Message
        
        # Update read status for unread messages
        Message.objects.filter(
            chat_room=self.chat_room,
            created_at__gt=self.last_read_at
        ).exclude(sender=self.user).update(is_read=True)
        
        self.unread_count = 0
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at', 'unread_count'])


class Message(models.Model):
    """
    Chat message model with support for different message types.
    """
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('property_link', 'Property Link'),
        ('location', 'Location'),
        ('system', 'System Message'),
        ('call', 'Voice/Video Call'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    
    # For file messages
    file_url = models.URLField(blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    
    # For property links
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages'
    )
    
    # For location messages
    location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Reactions (stored as JSON)
    reactions = models.JSONField(default=dict, blank=True)
    
    # Parent message for replies
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read', 'created_at']),
            models.Index(fields=['message_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        """Override save to update chat room's last message"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.is_deleted:
            # Update chat room's last message
            self.chat_room.update_last_message(self.content)
            
            # Increment unread count for other participants
            participants = ChatParticipant.objects.filter(
                chat_room=self.chat_room
            ).exclude(user=self.sender)
            
            for participant in participants:
                participant.unread_count += 1
                participant.save(update_fields=['unread_count'])
    
    def delete_message(self, soft_delete=True):
        """Delete message (soft or hard delete)"""
        if soft_delete:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at'])
        else:
            super().delete()


class MessageReadReceipt(models.Model):
    """
    Track who has read which messages (for group chats).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        ordering = ['-read_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} read message at {self.read_at}"


class ChatNotification(models.Model):
    """
    Store chat notifications for users (for when they're offline).
    """
    
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('mention', 'Mention'),
        ('room_created', 'Chat Room Created'),
        ('participant_added', 'New Participant'),
        ('participant_removed', 'Participant Removed'),
        ('call_missed', 'Missed Call'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_notifications')
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    # Notification data (JSON)
    data = models.JSONField(default=dict, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user}: {self.title}"


class CallLog(models.Model):
    """
    Log of voice/video calls made through the chat system.
    """
    
    CALL_TYPES = [
        ('voice', 'Voice Call'),
        ('video', 'Video Call'),
    ]
    
    CALL_STATUS = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('answered', 'Answered'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='calls')
    
    call_type = models.CharField(max_length=20, choices=CALL_TYPES)
    call_status = models.CharField(max_length=20, choices=CALL_STATUS, default='initiated')
    
    # Participants
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='outgoing_calls')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='incoming_calls')
    
    # Call metadata
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # WebRTC/SIP details (encrypted)
    session_id = models.CharField(max_length=255, blank=True)
    sdp_offer = models.TextField(blank=True)
    sdp_answer = models.TextField(blank=True)
    
    # Call quality metrics
    audio_quality_score = models.IntegerField(null=True, blank=True)
    video_quality_score = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['chat_room', 'started_at']),
            models.Index(fields=['caller', 'started_at']),
            models.Index(fields=['recipient', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.call_type} call from {self.caller} to {self.recipient}"
    
    def end_call(self, status='completed', duration_seconds=None):
        """End the call with status and duration"""
        self.call_status = status
        self.ended_at = timezone.now()
        
        if duration_seconds:
            self.duration_seconds = duration_seconds
        else:
            if self.started_at:
                duration = (self.ended_at - self.started_at).total_seconds()
                self.duration_seconds = int(duration)
        
        self.save(update_fields=['call_status', 'ended_at', 'duration_seconds'])