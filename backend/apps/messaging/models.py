"""
Messaging and notification models
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from apps.properties.models import Property

User = get_user_model()


class Conversation(BaseModel):
    """
    Direct messaging conversation between buyer and vendor
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='conversations',
        null=True,
        blank=True
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_as_buyer'
    )
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_as_vendor'
    )
    last_message_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        unique_together = ('property', 'buyer', 'vendor')

    def __str__(self):
        return f"Conversation: {self.buyer.email} - {self.vendor.email}"


class Message(BaseModel):
    """
    Individual messages within a conversation
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    attachment_url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.email} in {self.conversation}"


class Enquiry(BaseModel):
    """
    Property enquiry from buyer
    """
    ENQUIRY_STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('site_visit_scheduled', 'Site Visit Scheduled'),
        ('negotiating', 'Negotiating'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='enquiries'
    )
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enquiries_made')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enquiries_received')
    message = models.TextField()
    buyer_name = models.CharField(max_length=255)
    buyer_phone = models.CharField(max_length=20)
    buyer_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=ENQUIRY_STATUS_CHOICES,
        default='new'
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'enquiries'
        verbose_name = 'Enquiry'
        verbose_name_plural = 'Enquiries'

    def __str__(self):
        return f"Enquiry for {self.property.title} by {self.buyer.email}"


class SiteVisit(BaseModel):
    """
    Site visit scheduling and tracking
    """
    SITE_VISIT_STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enquiry = models.OneToOneField(
        Enquiry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='site_visit'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='site_visits'
    )
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='site_visits_requested')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='site_visits_scheduled')
    requested_date = models.DateTimeField()
    confirmed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=SITE_VISIT_STATUS_CHOICES,
        default='requested'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'site_visits'
        verbose_name = 'Site Visit'
        verbose_name_plural = 'Site Visits'

    def __str__(self):
        return f"Site visit for {self.property.title} on {self.requested_date}"


class Notification(BaseModel):
    """
    In-app notifications
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('enquiry', 'Enquiry'),
        ('message', 'Message'),
        ('site_visit', 'Site Visit'),
        ('property_approved', 'Property Approved'),
        ('subscription', 'Subscription'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='message'
    )
    data = models.JSONField(default=dict, blank=True)  # Extra data like IDs, links
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"