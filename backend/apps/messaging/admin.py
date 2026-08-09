"""
Admin configuration for messaging models
"""

from django.contrib import admin
from .models import Conversation, Message, Enquiry, SiteVisit, Notification


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'vendor', 'property', 'last_message_at', 'created_at')
    list_filter = ('is_archived', 'created_at')
    search_fields = ('buyer__email', 'vendor__email', 'property__title')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('sender__email', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('property', 'buyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'buyer__email', 'buyer_email')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('property', 'buyer', 'requested_date', 'status', 'created_at')
    list_filter = ('status', 'requested_date', 'created_at')
    search_fields = ('property__title', 'buyer__email')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('id', 'created_at', 'updated_at')