"""
Messaging URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet,
    EnquiryViewSet,
    SiteVisitViewSet,
    NotificationViewSet,
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'enquiries', EnquiryViewSet, basename='enquiry')
router.register(r'site-visits', SiteVisitViewSet, basename='site-visit')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]