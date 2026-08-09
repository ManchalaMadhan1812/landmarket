"""
Custom permissions for chat functionality.
"""
from rest_framework import permissions
from .models import ChatRoom, ChatParticipant


class IsChatParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant in the chat room.
    """
    
    def has_permission(self, request, view):
        """Check permission at view level."""
        chat_room_id = view.kwargs.get('chat_room_pk') or view.kwargs.get('pk')
        
        if not chat_room_id:
            return True
        
        # Check if user is a participant
        return ChatParticipant.objects.filter(
            chat_room_id=chat_room_id,
            user=request.user,
            left_at__isnull=True
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        """Check permission at object level."""
        # For chat rooms
        if isinstance(obj, ChatRoom):
            return ChatParticipant.objects.filter(
                chat_room=obj,
                user=request.user,
                left_at__isnull=True
            ).exists()
        
        # For messages
        from .models import Message
        if isinstance(obj, Message):
            return ChatParticipant.objects.filter(
                chat_room=obj.chat_room,
                user=request.user,
                left_at__isnull=True
            ).exists()
        
        # For other objects, check if related to chat room where user is participant
        if hasattr(obj, 'chat_room'):
            return ChatParticipant.objects.filter(
                chat_room=obj.chat_room,
                user=request.user,
                left_at__isnull=True
            ).exists()
        
        return True


class IsChatRoomAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin in the chat room.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is admin in the chat room."""
        chat_room = obj
        
        if isinstance(obj, ChatRoom):
            chat_room = obj
        elif hasattr(obj, 'chat_room'):
            chat_room = obj.chat_room
        else:
            return False
        
        return ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=request.user,
            is_admin=True,
            left_at__isnull=True
        ).exists()


class IsMessageSender(permissions.BasePermission):
    """
    Permission to check if user is the sender of the message.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the message sender."""
        from .models import Message
        
        if not isinstance(obj, Message):
            return False
        
        return obj.sender == request.user


class CanEditMessage(permissions.BasePermission):
    """
    Permission to check if user can edit a message.
    Messages can only be edited within 5 minutes of sending.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can edit the message."""
        from .models import Message
        from django.utils import timezone
        
        if not isinstance(obj, Message):
            return False
        
        # Check if user is the sender
        if obj.sender != request.user:
            return False
        
        # Check time limit (5 minutes)
        time_since_creation = (timezone.now() - obj.created_at).total_seconds()
        return time_since_creation <= 300  # 5 minutes


class CanAccessPropertyChat(permissions.BasePermission):
    """
    Permission to check if user can access property-related chat.
    Property owners/agents and interested buyers can access property chats.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access property chat."""
        from .models import ChatRoom
        
        if not isinstance(obj, ChatRoom):
            return False
        
        # User is always allowed if they're a participant
        if ChatParticipant.objects.filter(
            chat_room=obj,
            user=request.user,
            left_at__isnull=True
        ).exists():
            return True
        
        # For property chats, check if user is property owner/agent or has permission
        if obj.property:
            property_obj = obj.property
            is_owner_or_agent = (
                property_obj.owner == request.user or
                property_obj.agent == request.user
            )
            
            # Property owners/agents can join property chats
            if is_owner_or_agent:
                return True
            
            # Check if user has expressed interest in the property
            # (This would need to be implemented in property models)
            # For now, we'll assume only participants can access
        
        return False