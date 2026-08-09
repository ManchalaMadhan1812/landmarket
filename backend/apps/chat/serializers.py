"""
Serializers for chat models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatParticipant, Message, MessageReadReceipt, ChatNotification, CallLog
from apps.properties.serializers import PropertyListSerializer
from apps.users.serializers import UserProfileSerializer

User = get_user_model()


class UserChatSerializer(serializers.ModelSerializer):
    """Serializer for user information in chat context."""
    
    full_name = serializers.CharField(source='get_full_name')
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'avatar_url',
            'phone_number', 'user_type'
        ]
        read_only_fields = fields
    
    def get_avatar_url(self, obj):
        """Get user avatar URL."""
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url
        return None


class ChatParticipantSerializer(serializers.ModelSerializer):
    """Serializer for chat participants."""
    
    user = UserChatSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user'
    )
    
    class Meta:
        model = ChatParticipant
        fields = [
            'id', 'user', 'user_id', 'role', 'is_admin', 'is_muted',
            'email_notifications', 'push_notifications',
            'last_read_at', 'unread_count', 'joined_at', 'left_at'
        ]
        read_only_fields = ['id', 'last_read_at', 'unread_count', 'joined_at', 'left_at']


class MessageReadReceiptSerializer(serializers.ModelSerializer):
    """Serializer for message read receipts."""
    
    user = UserChatSerializer(read_only=True)
    
    class Meta:
        model = MessageReadReceipt
        fields = ['id', 'message', 'user', 'read_at']
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    sender = UserChatSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='sender',
        required=False
    )
    
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='property',
        required=False,
        allow_null=True
    )
    
    parent_message = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        required=False,
        allow_null=True
    )
    
    replies_count = serializers.IntegerField(read_only=True)
    read_receipts = MessageReadReceiptSerializer(many=True, read_only=True)
    has_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'chat_room', 'sender', 'sender_id', 'message_type',
            'content', 'file_url', 'file_name', 'file_size',
            'property', 'property_id', 'location_lat', 'location_lng', 'location_name',
            'is_read', 'is_edited', 'is_deleted', 'reactions',
            'parent_message', 'replies_count', 'read_receipts',
            'has_read', 'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = [
            'id', 'is_read', 'is_edited', 'is_deleted', 'replies_count',
            'read_receipts', 'has_read', 'created_at', 'updated_at', 'deleted_at'
        ]
    
    def get_has_read(self, obj):
        """Check if current user has read this message."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_receipts.filter(user=request.user).exists()
        return False
    
    def validate(self, data):
        """Validate message data."""
        message_type = data.get('message_type', 'text')
        content = data.get('content', '').strip()
        
        # Validate based on message type
        if message_type == 'text':
            if not content:
                raise serializers.ValidationError({'content': 'Text messages cannot be empty.'})
        
        elif message_type == 'image':
            file_url = data.get('file_url', '')
            if not file_url:
                raise serializers.ValidationError({'file_url': 'Image messages require a file URL.'})
        
        elif message_type == 'property_link':
            if not data.get('property'):
                raise serializers.ValidationError({'property': 'Property link messages require a property.'})
        
        elif message_type == 'location':
            if not all([data.get('location_lat'), data.get('location_lng')]):
                raise serializers.ValidationError({
                    'location': 'Location messages require latitude and longitude.'
                })
        
        # Ensure user is participant in chat room
        chat_room = data.get('chat_room')
        sender = data.get('sender') or self.context.get('request').user
        
        if chat_room and sender:
            is_participant = ChatParticipant.objects.filter(
                chat_room=chat_room,
                user=sender,
                left_at__isnull=True
            ).exists()
            
            if not is_participant:
                raise serializers.ValidationError(
                    'User is not a participant in this chat room.'
                )
        
        return data


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms."""
    
    participants = ChatParticipantSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        many=True,
        source='participants',
        required=False
    )
    
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='property',
        required=False,
        allow_null=True
    )
    
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()
    other_participants = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'room_type', 'name', 'property', 'property_id',
            'participants', 'participant_ids', 'messages',
            'is_active', 'last_message', 'last_message_at',
            'unread_count', 'other_participants',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'messages', 'last_message', 'last_message_at',
            'created_at', 'updated_at'
        ]
    
    def get_unread_count(self, obj):
        """Get unread message count for current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                participant = ChatParticipant.objects.get(
                    chat_room=obj,
                    user=request.user,
                    left_at__isnull=True
                )
                return participant.unread_count
            except ChatParticipant.DoesNotExist:
                return 0
        return 0
    
    def get_other_participants(self, obj):
        """Get other participants in the chat room."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participants = obj.participants.exclude(id=request.user.id)
            return UserChatSerializer(other_participants, many=True).data
        return []
    
    def validate(self, data):
        """Validate chat room data."""
        room_type = data.get('room_type', 'direct')
        participants = data.get('participants', [])
        
        # Validate participant count based on room type
        if room_type == 'direct':
            if len(participants) != 2:
                raise serializers.ValidationError({
                    'participants': 'Direct messages must have exactly 2 participants.'
                })
        elif room_type == 'group':
            if len(participants) < 2:
                raise serializers.ValidationError({
                    'participants': 'Group chats must have at least 2 participants.'
                })
        
        # Ensure participants are unique
        if len(participants) != len(set(participants)):
            raise serializers.ValidationError({
                'participants': 'Duplicate participants are not allowed.'
            })
        
        # Check for existing direct chat room between participants
        if room_type == 'direct' and len(participants) == 2:
            user1, user2 = participants
            
            existing_rooms = ChatRoom.objects.filter(
                room_type='direct',
                participants=user1,
                is_active=True
            ).filter(participants=user2)
            
            if existing_rooms.exists():
                raise serializers.ValidationError({
                    'participants': 'A direct chat room already exists between these users.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create chat room with participants."""
        participants = validated_data.pop('participants', [])
        chat_room = ChatRoom.objects.create(**validated_data)
        
        # Add participants with default role
        for participant in participants:
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user=participant,
                role='buyer'  # Default role
            )
        
        return chat_room


class ChatNotificationSerializer(serializers.ModelSerializer):
    """Serializer for chat notifications."""
    
    chat_room = ChatRoomSerializer(read_only=True)
    message = MessageSerializer(read_only=True)
    
    class Meta:
        model = ChatNotification
        fields = [
            'id', 'notification_type', 'chat_room', 'message',
            'title', 'body', 'data', 'is_read', 'created_at'
        ]
        read_only_fields = fields


class CallLogSerializer(serializers.ModelSerializer):
    """Serializer for call logs."""
    
    chat_room = ChatRoomSerializer(read_only=True)
    caller = UserChatSerializer(read_only=True)
    recipient = UserChatSerializer(read_only=True)
    
    class Meta:
        model = CallLog
        fields = [
            'id', 'chat_room', 'call_type', 'call_status',
            'caller', 'recipient', 'started_at', 'ended_at',
            'duration_seconds', 'session_id',
            'audio_quality_score', 'video_quality_score',
            'created_at'
        ]
        read_only_fields = fields


# WebSocket serializers
class WebSocketMessageSerializer(serializers.Serializer):
    """Serializer for WebSocket messages."""
    
    type = serializers.CharField(required=True)
    content = serializers.CharField(required=False, allow_blank=True)
    message_type = serializers.CharField(default='text')
    message_id = serializers.UUIDField(required=False)
    parent_message_id = serializers.UUIDField(required=False)
    data = serializers.DictField(required=False, default=dict)


class TypingIndicatorSerializer(serializers.Serializer):
    """Serializer for typing indicators."""
    
    type = serializers.CharField(default='typing')
    is_typing = serializers.BooleanField(required=True)


class ReadReceiptSerializer(serializers.Serializer):
    """Serializer for read receipts."""
    
    type = serializers.CharField(default='read_receipt')
    message_id = serializers.UUIDField(required=True)


class ReactionSerializer(serializers.Serializer):
    """Serializer for message reactions."""
    
    type = serializers.CharField(default='reaction')
    message_id = serializers.UUIDField(required=True)
    reaction = serializers.CharField(required=True, max_length=10)


class CallSignalSerializer(serializers.Serializer):
    """Serializer for WebRTC signaling."""
    
    type = serializers.CharField(default='call_signal')
    signal_type = serializers.CharField(required=True)  # offer, answer, candidate
    target_user_id = serializers.UUIDField(required=True)
    data = serializers.DictField(required=True)


class CallEndedSerializer(serializers.Serializer):
    """Serializer for call ended events."""
    
    type = serializers.CharField(default='call_ended')
    call_id = serializers.UUIDField(required=True)
    call_data = serializers.DictField(required=False, default=dict)


# API request serializers
class CreateChatRoomSerializer(serializers.Serializer):
    """Serializer for creating chat rooms."""
    
    room_type = serializers.ChoiceField(choices=ChatRoom.ROOM_TYPES, default='direct')
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    property_id = serializers.UUIDField(required=False, allow_null=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        min_length=1
    )


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending messages."""
    
    content = serializers.CharField(required=True)
    message_type = serializers.ChoiceField(choices=Message.MESSAGE_TYPES, default='text')
    parent_message_id = serializers.UUIDField(required=False, allow_null=True)
    
    # For file messages
    file_url = serializers.URLField(required=False, allow_blank=True)
    file_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    file_size = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    
    # For property link messages
    property_id = serializers.UUIDField(required=False, allow_null=True)
    
    # For location messages
    location_lat = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=10,
        decimal_places=8
    )
    location_lng = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=11,
        decimal_places=8
    )
    location_name = serializers.CharField(required=False, allow_blank=True, max_length=255)


class UpdateChatRoomSerializer(serializers.Serializer):
    """Serializer for updating chat rooms."""
    
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    is_active = serializers.BooleanField(required=False)


class AddParticipantSerializer(serializers.Serializer):
    """Serializer for adding participants to chat room."""
    
    user_id = serializers.UUIDField(required=True)
    role = serializers.ChoiceField(choices=ChatParticipant.ROLE_CHOICES, default='buyer')
    is_admin = serializers.BooleanField(default=False)


class UpdateParticipantSerializer(serializers.Serializer):
    """Serializer for updating participant settings."""
    
    role = serializers.ChoiceField(choices=ChatParticipant.ROLE_CHOICES, required=False)
    is_admin = serializers.BooleanField(required=False)
    is_muted = serializers.BooleanField(required=False)
    email_notifications = serializers.BooleanField(required=False)
    push_notifications = serializers.BooleanField(required=False)


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read."""
    
    message_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list
    )
    up_to_message_id = serializers.UUIDField(required=False, allow_null=True)