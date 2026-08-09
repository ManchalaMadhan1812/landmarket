"""
Messaging API views - stub for Phase 1
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Enquiry, SiteVisit, Notification


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Conversation/messaging endpoints - TODO: Implement WebSocket integration
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implement proper queryset filtering
        return Conversation.objects.none()


class EnquiryViewSet(viewsets.ModelViewSet):
    """
    Property enquiry endpoints
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implement enquiry endpoints
        return Enquiry.objects.none()


class SiteVisitViewSet(viewsets.ModelViewSet):
    """
    Site visit scheduling endpoints
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implement site visit endpoints
        return SiteVisit.objects.none()


class NotificationViewSet(viewsets.ModelViewSet):
    """
    In-app notification endpoints
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implement notification endpoints
        return Notification.objects.none()