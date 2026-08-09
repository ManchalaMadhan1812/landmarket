"""
WebSocket consumers for real-time chat functionality.
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import ChatRoom, Message, ChatParticipant, MessageReadReceipt
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat functionality.
    Handles real-time messaging, typing indicators, read receipts, etc.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Get chat room ID from URL
        self.room_id = self.scope['url_route']['kwargs'].get('room_id')
        if not self.room_id:
            await self.close()
            return
        
        # Validate user can access this chat room
        if not await self.validate_user_access():
            await self.close()
            return
        
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Mark user as online in this room
        await self.mark_user_online(True)
        
        # Send online status to other users
        await self.send_online_status(True)
        
        await self.accept()
        
        # Send recent messages
        await self.send_recent_messages()
        
        # Send list of online users
        await self.send_online_users()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Mark user as offline
            await self.mark_user_online(False)
            
            # Send offline status to other users
            await self.send_online_status(False)
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            # Handle different message types
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            elif message_type == 'call_signal':
                await self.handle_call_signal(data)
            elif message_type == 'call_ended':
                await self.handle_call_ended(data)
            elif message_type == 'reaction':
                await self.handle_reaction(data)
            elif message_type == 'delete_message':
                await self.handle_delete_message(data)
            elif message_type == 'edit_message':
                await self.handle_edit_message(data)
            else:
                await self.send_error('Unknown message type')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_message(self, data):
        """Handle new message from user."""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        parent_id = data.get('parent_message_id')
        
        if not content and message_type == 'text':
            await self.send_error('Message content cannot be empty')
            return
        
        # Create message in database
        message = await self.create_message(
            content=content,
            message_type=message_type,
            parent_id=parent_id,
            extra_data=data.get('data', {})
        )
        
        if not message:
            await self.send_error('Failed to create message')
            return
        
        # Broadcast message to room
        message_data = await self.serialize_message(message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data,
                'sender_id': str(self.user.id)
            }
        )
        
        # Send delivery confirmation to sender
        await self.send(json.dumps({
            'type': 'message_sent',
            'message_id': str(message.id),
            'timestamp': message.created_at.isoformat()
        }))
    
    async def handle_typing(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)
        
        # Broadcast typing status to room (except sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name(),
                'is_typing': is_typing
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle read receipt for messages."""
        message_id = data.get('message_id')
        
        if not message_id:
            return
        
        # Mark message as read
        await self.mark_message_read(message_id)
        
        # Broadcast read receipt to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name(),
                'read_at': timezone.now().isoformat()
            }
        )
    
    async def handle_call_signal(self, data):
        """Handle WebRTC signaling for calls."""
        signal_type = data.get('signal_type')  # offer, answer, candidate
        call_data = data.get('data', {})
        
        # Forward signaling data to target user
        target_user_id = data.get('target_user_id')
        if target_user_id:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_signal',
                    'signal_type': signal_type,
                    'data': call_data,
                    'from_user_id': str(self.user.id),
                    'target_user_id': target_user_id
                }
            )
    
    async def handle_call_ended(self, data):
        """Handle call ended event."""
        call_id = data.get('call_id')
        call_data = data.get('call_data', {})
        
        # Broadcast call ended to all participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_ended',
                'call_id': call_id,
                'call_data': call_data,
                'ended_by': str(self.user.id)
            }
        )
    
    async def handle_reaction(self, data):
        """Handle message reactions."""
        message_id = data.get('message_id')
        reaction = data.get('reaction')
        
        if not message_id or not reaction:
            return
        
        # Update reaction in database
        updated = await self.update_message_reaction(message_id, reaction)
        
        if updated:
            # Broadcast reaction update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_reaction',
                    'message_id': message_id,
                    'reaction': reaction,
                    'user_id': str(self.user.id),
                    'user_name': self.user.get_full_name()
                }
            )
    
    async def handle_delete_message(self, data):
        """Handle message deletion."""
        message_id = data.get('message_id')
        
        if not message_id:
            return
        
        # Delete message (soft delete)
        deleted = await self.delete_message(message_id)
        
        if deleted:
            # Broadcast deletion
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id,
                    'deleted_by': str(self.user.id)
                }
            )
    
    async def handle_edit_message(self, data):
        """Handle message editing."""
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()
        
        if not message_id or not new_content:
            return
        
        # Update message in database
        updated = await self.edit_message(message_id, new_content)
        
        if updated:
            # Broadcast edit
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_edited',
                    'message_id': message_id,
                    'new_content': new_content,
                    'edited_by': str(self.user.id),
                    'edited_at': timezone.now().isoformat()
                }
            )
    
    # WebSocket event handlers for group messages
    async def chat_message(self, event):
        """Receive chat message from group."""
        # Don't send message back to sender
        if str(self.user.id) == event['sender_id']:
            return
        
        await self.send(json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        """Receive typing indicator from group."""
        # Don't send typing indicator to sender
        if str(self.user.id) == event['user_id']:
            return
        
        await self.send(json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))
    
    async def read_receipt(self, event):
        """Receive read receipt from group."""
        await self.send(json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'read_at': event['read_at']
        }))
    
    async def call_signal(self, event):
        """Receive call signaling from group."""
        # Only send to target user
        if str(self.user.id) != event['target_user_id']:
            return
        
        await self.send(json.dumps({
            'type': 'call_signal',
            'signal_type': event['signal_type'],
            'data': event['data'],
            'from_user_id': event['from_user_id']
        }))
    
    async def call_ended(self, event):
        """Receive call ended event from group."""
        await self.send(json.dumps({
            'type': 'call_ended',
            'call_id': event['call_id'],
            'call_data': event['call_data'],
            'ended_by': event['ended_by']
        }))
    
    async def message_reaction(self, event):
        """Receive reaction update from group."""
        await self.send(json.dumps({
            'type': 'message_reaction',
            'message_id': event['message_id'],
            'reaction': event['reaction'],
            'user_id': event['user_id'],
            'user_name': event['user_name']
        }))
    
    async def message_deleted(self, event):
        """Receive message deletion from group."""
        await self.send(json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'deleted_by': event['deleted_by']
        }))
    
    async def message_edited(self, event):
        """Receive message edit from group."""
        await self.send(json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'new_content': event['new_content'],
            'edited_by': event['edited_by'],
            'edited_at': event['edited_at']
        }))
    
    async def user_online_status(self, event):
        """Receive user online status from group."""
        # Don't send status to self
        if str(self.user.id) == event['user_id']:
            return
        
        await self.send(json.dumps({
            'type': 'user_online_status',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_online': event['is_online'],
            'timestamp': event['timestamp']
        }))
    
    # Helper methods
    async def send_error(self, error_message):
        """Send error message to client."""
        await self.send(json.dumps({
            'type': 'error',
            'message': error_message
        }))
    
    async def send_recent_messages(self):
        """Send recent messages when user joins."""
        messages = await self.get_recent_messages()
        await self.send(json.dumps({
            'type': 'initial_messages',
            'messages': messages
        }))
    
    async def send_online_users(self):
        """Send list of online users."""
        online_users = await self.get_online_users()
        await self.send(json.dumps({
            'type': 'online_users',
            'users': online_users
        }))
    
    async def send_online_status(self, is_online):
        """Send user's online status to other users in room."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_online_status',
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name(),
                'is_online': is_online,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    # Database operations
    @database_sync_to_async
    def validate_user_access(self):
        """Validate user has access to this chat room."""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id, is_active=True)
            return ChatParticipant.objects.filter(
                chat_room=chat_room,
                user=self.user,
                left_at__isnull=True
            ).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_user_online(self, is_online):
        """Mark user as online/offline in chat room."""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            participant, created = ChatParticipant.objects.get_or_create(
                chat_room=chat_room,
                user=self.user,
                defaults={'role': 'buyer'}
            )
            # Here you might want to update online status in Redis or separate table
            # For simplicity, we're just updating the last_read_at
            if is_online:
                participant.last_read_at = timezone.now()
                participant.save(update_fields=['last_read_at'])
        except ChatRoom.DoesNotExist:
            pass
    
    @database_sync_to_async
    def create_message(self, content, message_type='text', parent_id=None, extra_data=None):
        """Create message in database."""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            
            parent_message = None
            if parent_id:
                try:
                    parent_message = Message.objects.get(id=parent_id, chat_room=chat_room)
                except Message.DoesNotExist:
                    pass
            
            message_data = {
                'chat_room': chat_room,
                'sender': self.user,
                'message_type': message_type,
                'content': content,
                'parent_message': parent_message
            }
            
            # Add extra data based on message type
            if message_type == 'image' and extra_data:
                message_data['file_url'] = extra_data.get('url', '')
                message_data['file_name'] = extra_data.get('name', '')
                message_data['file_size'] = extra_data.get('size')
            elif message_type == 'property_link' and extra_data:
                from apps.properties.models import Property
                try:
                    property_id = extra_data.get('property_id')
                    if property_id:
                        property_obj = Property.objects.get(id=property_id)
                        message_data['property'] = property_obj
                except Property.DoesNotExist:
                    pass
            elif message_type == 'location' and extra_data:
                message_data['location_lat'] = extra_data.get('lat')
                message_data['location_lng'] = extra_data.get('lng')
                message_data['location_name'] = extra_data.get('name', '')
            
            message = Message.objects.create(**message_data)
            return message
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message for WebSocket."""
        return MessageSerializer(message).data
    
    @database_sync_to_async
    def get_recent_messages(self, limit=50):
        """Get recent messages for the chat room."""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            messages = Message.objects.filter(
                chat_room=chat_room,
                is_deleted=False
            ).select_related('sender', 'property').prefetch_related('read_receipts')[:limit]
            
            # Mark user's messages as read
            for message in messages:
                if message.sender != self.user and not message.is_read:
                    # Check if user has already read this message
                    has_read = MessageReadReceipt.objects.filter(
                        message=message,
                        user=self.user
                    ).exists()
                    
                    if not has_read:
                        MessageReadReceipt.objects.create(
                            message=message,
                            user=self.user
                        )
                        message.is_read = True
            
            return MessageSerializer(messages, many=True).data
        except ChatRoom.DoesNotExist:
            return []
    
    @database_sync_to_async
    def get_online_users(self):
        """Get list of online users in chat room."""
        # This is a simplified version - in production you'd use Redis
        # to track online users across multiple WebSocket connections
        
        # For now, return participants who have been active recently
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            active_time = timezone.now() - timezone.timedelta(minutes=5)
            
            participants = ChatParticipant.objects.filter(
                chat_room=chat_room,
                left_at__isnull=True,
                last_read_at__gte=active_time
            ).exclude(user=self.user).select_related('user')[:20]
            
            return [{
                'id': str(p.user.id),
                'name': p.user.get_full_name(),
                'role': p.role
            } for p in participants]
        except ChatRoom.DoesNotExist:
            return []
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark message as read by user."""
        try:
            message = Message.objects.get(id=message_id, chat_room_id=self.room_id)
            
            # Create read receipt
            receipt, created = MessageReadReceipt.objects.get_or_create(
                message=message,
                user=self.user,
                defaults={'read_at': timezone.now()}
            )
            
            # Update participant's unread count
            participant = ChatParticipant.objects.get(
                chat_room_id=self.room_id,
                user=self.user
            )
            if participant.unread_count > 0:
                participant.unread_count -= 1
                participant.save(update_fields=['unread_count'])
            
            return True
        except (Message.DoesNotExist, ChatParticipant.DoesNotExist):
            return False
    
    @database_sync_to_async
    def update_message_reaction(self, message_id, reaction):
        """Update message reaction."""
        try:
            message = Message.objects.get(id=message_id, chat_room_id=self.room_id)
            
            # Initialize reactions dict if empty
            if not message.reactions:
                message.reactions = {}
            
            # Add or update reaction from this user
            reactions = message.reactions
            user_reactions = reactions.get(str(self.user.id), [])
            
            if reaction not in user_reactions:
                user_reactions.append(reaction)
            else:
                user_reactions.remove(reaction)
            
            if user_reactions:
                reactions[str(self.user.id)] = user_reactions
            else:
                reactions.pop(str(self.user.id), None)
            
            message.reactions = reactions
            message.save(update_fields=['reactions'])
            return True
        except Message.DoesNotExist:
            return False
    
    @database_sync_to_async
    def delete_message(self, message_id):
        """Soft delete message."""
        try:
            message = Message.objects.get(
                id=message_id,
                chat_room_id=self.room_id,
                sender=self.user  # Only allow sender to delete
            )
            message.delete_message(soft_delete=True)
            return True
        except Message.DoesNotExist:
            return False
    
    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        """Edit message content."""
        try:
            message = Message.objects.get(
                id=message_id,
                chat_room_id=self.room_id,
                sender=self.user,  # Only allow sender to edit
                is_deleted=False
            )
            message.content = new_content
            message.is_edited = True
            message.save(update_fields=['content', 'is_edited', 'updated_at'])
            return True
        except Message.DoesNotExist:
            return False