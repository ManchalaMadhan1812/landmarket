"""
API views for chat functionality.
"""
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Max, Subquery, OuterRef
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.core.permissions import IsChatParticipant, IsChatRoomAdmin
from .models import ChatRoom, ChatParticipant, Message, ChatNotification, CallLog
from .serializers import (
    ChatRoomSerializer, MessageSerializer, ChatNotificationSerializer,
    CallLogSerializer, CreateChatRoomSerializer, SendMessageSerializer,
    UpdateChatRoomSerializer, AddParticipantSerializer, UpdateParticipantSerializer,
    MarkMessagesReadSerializer
)
from apps.properties.models import Property
from apps.users.models import User


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for chat rooms.
    
    Supports:
    - List user's chat rooms
    - Create new chat rooms
    - Retrieve chat room details
    - Update chat room settings
    - Delete/leave chat rooms
    - Add/remove participants
    - Mark messages as read
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer
    
    def get_queryset(self):
        """Get chat rooms where user is an active participant."""
        user = self.request.user
        
        # Subquery for last message timestamp
        last_message_subquery = Message.objects.filter(
            chat_room=OuterRef('pk'),
            is_deleted=False
        ).order_by('-created_at').values('created_at')[:1]
        
        # Get chat rooms where user is active participant
        queryset = ChatRoom.objects.filter(
            participants__user=user,
            participants__left_at__isnull=True,
            is_active=True
        ).annotate(
            last_activity=Subquery(last_message_subquery),
            unread_count=Count(
                'messages',
                filter=Q(
                    messages__created_at__gt=Subquery(
                        ChatParticipant.objects.filter(
                            chat_room=OuterRef('pk'),
                            user=user
                        ).values('last_read_at')[:1]
                    ),
                    messages__sender__id__ne=user.id,
                    messages__is_deleted=False
                )
            )
        ).order_by('-last_activity')
        
        # Apply filters
        room_type = self.request.query_params.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        property_id = self.request.query_params.get('property_id')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(participants__user__first_name__icontains=search) |
                Q(participants__user__last_name__icontains=search) |
                Q(property__title__icontains=search)
            ).distinct()
        
        return queryset
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        """List user's chat rooms."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new chat room."""
        serializer = CreateChatRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        room_type = data.get('room_type', 'direct')
        name = data.get('name', '')
        property_id = data.get('property_id')
        participant_ids = data['participant_ids']
        
        # Add current user to participants if not already included
        if request.user.id not in [str(pid) for pid in participant_ids]:
            participant_ids.append(request.user.id)
        
        # Get user objects
        participants = User.objects.filter(id__in=participant_ids)
        if len(participants) != len(participant_ids):
            missing = set(participant_ids) - set(p.id for p in participants)
            return Response(
                {'error': f'Users not found: {missing}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get property if provided
        property_obj = None
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
            except Property.DoesNotExist:
                return Response(
                    {'error': 'Property not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create chat room
        chat_room = ChatRoom.objects.create(
            room_type=room_type,
            name=name,
            property=property_obj
        )
        
        # Add participants
        for user in participants:
            role = 'buyer'
            if user == request.user and room_type == 'property':
                role = 'seller'  # Property owner/agent
            elif user.user_type == 'agent':
                role = 'agent'
            
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=user,
                role=role,
                is_admin=(user == request.user)  # Creator is admin
            )
        
        # Send system message
        if room_type == 'group':
            system_message = f"{request.user.get_full_name()} created this group."
        elif room_type == 'property' and property_obj:
            system_message = f"Chat started about property: {property_obj.title}"
        else:
            system_message = "Chat started"
        
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            message_type='system',
            content=system_message
        )
        
        # Serialize and return
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve chat room details with messages."""
        chat_room = self.get_object()
        
        # Check if user is participant
        if not ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=request.user,
            left_at__isnull=True
        ).exists():
            return Response(
                {'error': 'You are not a participant in this chat room'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark user's unread count as zero
        participant = ChatParticipant.objects.get(
            chat_room=chat_room,
            user=request.user
        )
        participant.unread_count = 0
        participant.last_read_at = timezone.now()
        participant.save(update_fields=['unread_count', 'last_read_at'])
        
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update chat room settings."""
        chat_room = self.get_object()
        
        # Check if user is admin
        if not ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=request.user,
            is_admin=True,
            left_at__isnull=True
        ).exists():
            return Response(
                {'error': 'Only admins can update chat room settings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UpdateChatRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Update fields
        if 'name' in data:
            chat_room.name = data['name']
        if 'is_active' in data:
            chat_room.is_active = data['is_active']
        
        chat_room.save()
        
        # Send system message if name changed
        if 'name' in data and data['name']:
            Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                message_type='system',
                content=f"{request.user.get_full_name()} renamed the group to: {data['name']}"
            )
        
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Leave or delete chat room."""
        chat_room = self.get_object()
        participant = get_object_or_404(
            ChatParticipant,
            chat_room=chat_room,
            user=request.user
        )
        
        # If user is admin and only participant, delete room
        if participant.is_admin and chat_room.participants.count() == 1:
            chat_room.is_active = False
            chat_room.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Otherwise, mark participant as left
        participant.left_at = timezone.now()
        participant.save()
        
        # Send system message
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            message_type='system',
            content=f"{request.user.get_full_name()} left the chat"
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add participant to chat room."""
        chat_room = self.get_object()
        
        # Check if user is admin
        if not ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=request.user,
            is_admin=True,
            left_at__isnull=True
        ).exists():
            return Response(
                {'error': 'Only admins can add participants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AddParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user_id = data['user_id']
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is already a participant
        if ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=user,
            left_at__isnull=True
        ).exists():
            return Response(
                {'error': 'User is already a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add participant
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=user,
            role=data.get('role', 'buyer'),
            is_admin=data.get('is_admin', False)
        )
        
        # Send system message
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            message_type='system',
            content=f"{request.user.get_full_name()} added {user.get_full_name()} to the chat"
        )
        
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove participant from chat room."""
        chat_room = self.get_object()
        
        # Check if user is admin
        if not ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=request.user,
            is_admin=True,
            left_at__isnull=True
        ).exists():
            return Response(
                {'error': 'Only admins can remove participants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get participant
        participant = get_object_or_404(
            ChatParticipant,
            chat_room=chat_room,
            user_id=user_id,
            left_at__isnull=True
        )
        
        # Cannot remove yourself (use leave endpoint instead)
        if participant.user == request.user:
            return Response(
                {'error': 'Use the leave endpoint to remove yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark participant as removed
        participant.left_at = timezone.now()
        participant.save()
        
        # Send system message
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            message_type='system',
            content=f"{request.user.get_full_name()} removed {participant.user.get_full_name()} from the chat"
        )
        
        return Response({'success': True})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark messages as read in chat room."""
        chat_room = self.get_object()
        
        # Check if user is participant
        participant = get_object_or_404(
            ChatParticipant,
            chat_room=chat_room,
            user=request.user,
            left_at__isnull=True
        )
        
        serializer = MarkMessagesReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        message_ids = data.get('message_ids', [])
        up_to_message_id = data.get('up_to_message_id')
        
        if message_ids:
            # Mark specific messages as read
            messages = Message.objects.filter(
                id__in=message_ids,
                chat_room=chat_room,
                is_deleted=False
            )
            
            for message in messages:
                message.mark_as_read_by(request.user)
        
        elif up_to_message_id:
            # Mark all messages up to this one as read
            try:
                last_message = Message.objects.get(
                    id=up_to_message_id,
                    chat_room=chat_room
                )
                
                messages = Message.objects.filter(
                    chat_room=chat_room,
                    created_at__lte=last_message.created_at,
                    is_deleted=False
                ).exclude(sender=request.user)
                
                for message in messages:
                    message.mark_as_read_by(request.user)
                    
            except Message.DoesNotExist:
                pass
        
        # Update participant's unread count
        participant.unread_count = 0
        participant.last_read_at = timezone.now()
        participant.save(update_fields=['unread_count', 'last_read_at'])
        
        return Response({'success': True})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get total unread message count across all chat rooms."""
        total_unread = ChatParticipant.objects.filter(
            user=request.user,
            left_at__isnull=True,
            chat_room__is_active=True
        ).aggregate(total=Count('unread_count'))['total'] or 0
        
        return Response({'total_unread': total_unread})


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for chat messages.
    
    Supports:
    - List messages in chat room
    - Send new message
    - Edit message
    - Delete message
    - React to message
    """
    
    permission_classes = [IsAuthenticated, IsChatParticipant]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Get messages for the specified chat room."""
        chat_room_id = self.kwargs.get('chat_room_pk')
        return Message.objects.filter(
            chat_room_id=chat_room_id,
            is_deleted=False
        ).select_related('sender', 'property').prefetch_related('read_receipts').order_by('created_at')
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        context['chat_room_id'] = self.kwargs.get('chat_room_pk')
        return context
    
    def list(self, request, *args, **kwargs):
        """List messages in chat room."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Send new message."""
        chat_room_id = self.kwargs.get('chat_room_pk')
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id, is_active=True)
        
        # Check if user is participant
        if not ChatParticipant.objects.filter(
            chat_room=chat_room,
            user=request.user,
            left_at__isnull=True
        ).exists():
            return Response(
                {'error': 'You are not a participant in this chat room'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Create message
        message = Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            message_type=data.get('message_type', 'text'),
            content=data['content']
        )
        
        # Add extra data based on message type
        if data.get('message_type') == 'image':
            message.file_url = data.get('file_url', '')
            message.file_name = data.get('file_name', '')
            message.file_size = data.get('file_size')
        
        elif data.get('message_type') == 'property_link' and data.get('property_id'):
            try:
                property_obj = Property.objects.get(id=data['property_id'])
                message.property = property_obj
            except Property.DoesNotExist:
                pass
        
        elif data.get('message_type') == 'location':
            message.location_lat = data.get('location_lat')
            message.location_lng = data.get('location_lng')
            message.location_name = data.get('location_name', '')
        
        if data.get('parent_message_id'):
            try:
                parent_message = Message.objects.get(id=data['parent_message_id'])
                message.parent_message = parent_message
            except Message.DoesNotExist:
                pass
        
        message.save()
        
        # Update chat room last message
        chat_room.update_last_message(message.content)
        
        # Serialize and return
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Edit message."""
        message = self.get_object()
        
        # Check if user is the sender
        if message.sender != request.user:
            return Response(
                {'error': 'You can only edit your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if message can be edited (within time limit)
        time_since_creation = (timezone.now() - message.created_at).total_seconds()
        if time_since_creation > 300:  # 5 minutes
            return Response(
                {'error': 'Messages can only be edited within 5 minutes of sending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SendMessageSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Update message
        if 'content' in data:
            message.content = data['content']
            message.is_edited = True
        
        message.save()
        
        # Update chat room last message if this was the last message
        if message.chat_room.last_message == message.content:
            message.chat_room.update_last_message(message.content)
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete message (soft delete)."""
        message = self.get_object()
        
        # Check if user is the sender
        if message.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete
        message.delete_message(soft_delete=True)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """React to message."""
        message = self.get_object()
        reaction = request.data.get('reaction')
        
        if not reaction:
            return Response(
                {'error': 'reaction is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize reactions dict if empty
        if not message.reactions:
            message.reactions = {}
        
        # Add or remove reaction
        reactions = message.reactions
        user_reactions = reactions.get(str(request.user.id), [])
        
        if reaction not in user_reactions:
            user_reactions.append(reaction)
        else:
            user_reactions.remove(reaction)
        
        if user_reactions:
            reactions[str(request.user.id)] = user_reactions
        else:
            reactions.pop(str(request.user.id), None)
        
        message.reactions = reactions
        message.save(update_fields=['reactions'])
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)


class ChatNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for chat notifications.
    
    Supports:
    - List user's notifications
    - Mark notifications as read
    - Clear notifications
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ChatNotificationSerializer
    
    def get_queryset(self):
        """Get user's notifications."""
        return ChatNotification.objects.filter(
            user=self.request.user
        ).select_related('chat_room', 'message').order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'success': True})
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Clear all notifications."""
        ChatNotification.objects.filter(user=request.user).delete()
        
        return Response({'success': True})


class CallLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for call logs.
    
    Supports:
    - List user's call logs
    - Retrieve call log details
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = CallLogSerializer
    
    def get_queryset(self):
        """Get user's call logs."""
        user = self.request.user
        return CallLog.objects.filter(
            Q(caller=user) | Q(recipient=user)
        ).select_related('chat_room', 'caller', 'recipient').order_by('-started_at')


class ChatSearchViewSet(viewsets.GenericViewSet):
    """
    ViewSet for chat-related search.
    
    Supports:
    - Search for users to chat with
    - Search for property-related chats
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def search_users(self, request):
        """Search for users to start a chat with."""
        search_query = request.query_params.get('q', '').strip()
        
        if not search_query or len(search_query) < 2:
            return Response({'results': []})
        
        # Search users
        users = User.objects.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        ).exclude(id=request.user.id).select_related('profile')[:20]
        
        results = []
        for user in users:
            # Check if direct chat already exists
            existing_chat = ChatRoom.objects.filter(
                room_type='direct',
                participants=request.user,
                is_active=True
            ).filter(participants=user).first()
            
            results.append({
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name(),
                'user_type': user.user_type,
                'avatar_url': user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else None,
                'existing_chat_id': str(existing_chat.id) if existing_chat else None
            })
        
        return Response({'results': results})
    
    @action(detail=False, methods=['get'])
    def property_chats(self, request):
        """Get all chats related to user's properties."""
        user = request.user
        
        # Get properties where user is owner/agent
        user_properties = Property.objects.filter(
            Q(owner=user) | Q(agent=user)
        )
        
        # Get chat rooms for these properties
        chat_rooms = ChatRoom.objects.filter(
            property__in=user_properties,
            is_active=True
        ).distinct()
        
        # Get latest message for each chat room
        latest_messages = Message.objects.filter(
            chat_room__in=chat_rooms,
            is_deleted=False
        ).order_by('chat_room', '-created_at').distinct('chat_room')
        
        results = []
        for message in latest_messages:
            chat_room = message.chat_room
            other_participants = chat_room.participants.exclude(id=user.id)
            
            results.append({
                'chat_room_id': str(chat_room.id),
                'property_id': str(chat_room.property.id) if chat_room.property else None,
                'property_title': chat_room.property.title if chat_room.property else None,
                'last_message': message.content[:100],
                'last_message_at': message.created_at.isoformat(),
                'other_participants': [
                    {
                        'id': str(p.id),
                        'full_name': p.get_full_name()
                    }
                    for p in other_participants
                ]
            })
        
        return Response({'results': results})