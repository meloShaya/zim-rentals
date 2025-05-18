import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Listing, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.listing_id = self.scope['url_route']['kwargs']['listing_id']
        self.room_group_name = f'chat_{self.listing_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'message':
                message = text_data_json['message']
                user = self.scope['user']
                
                if not user.is_authenticated:
                    await self.send(text_data=json.dumps({
                        'error': 'Authentication required'
                    }))
                    return
                
                # Before saving a new message, mark all unread messages in this chat as read
                # This assumes that if the user is sending a message, they have read all previous messages
                await self.mark_all_messages_read()
                
                # Save message to database
                saved_message = await self.save_message(message, user.id)
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': saved_message.id,
                        'message': message,
                        'user_id': user.id,
                        'username': user.username,
                        'created_at': saved_message.created_at.isoformat(),
                        'is_read': saved_message.is_read,
                        'read_at': saved_message.read_at.isoformat() if saved_message.read_at else None
                    }
                )
            elif message_type == 'mark_read':
                message_id = text_data_json.get('message_id')
                if message_id:
                    await self.mark_message_read(message_id)
                    
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message_id': event['message_id'],
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'created_at': event['created_at'],
            'is_read': event['is_read'],
            'read_at': event['read_at']
        }))

    async def message_read(self, event):
        # Send read status update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'read_status',
            'message_id': event['message_id'],
            'is_read': event['is_read'],
            'read_at': event['read_at']
        }))

    @database_sync_to_async
    def save_message(self, message, user_id):
        listing = Listing.objects.get(id=self.listing_id)
        user = User.objects.get(id=user_id)
        return ChatMessage.objects.create(
            listing=listing,
            user=user,
            message=message
        )

    async def mark_message_read(self, message_id):
        try:
            message = await self.get_message(message_id)
            if message and message.user != self.scope['user']:  # Only mark as read if not the sender
                await self.update_message_read_status(message)
                
                # Notify the sender that their message was read
                await self.channel_layer.group_send(
                    f'chat_{self.listing_id}',
                    {
                        'type': 'message_read',
                        'message_id': message_id,
                        'is_read': True,
                        'read_at': message.read_at.isoformat()
                    }
                )
        except ChatMessage.DoesNotExist:
            pass

    @database_sync_to_async
    def get_message(self, message_id):
        try:
            return ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            return None

    @database_sync_to_async
    def update_message_read_status(self, message):
        message.is_read = True
        message.read_at = timezone.now()
        message.save()

    async def mark_all_messages_read(self):
        """Mark all unread messages in the current chat as read."""
        try:
            user = self.scope['user']
            listing_id = self.listing_id
            
            # Get all unread messages in this chat that were not sent by the current user
            messages = await self.get_unread_messages(listing_id, user.id)
            
            # Mark each message as read
            for message in messages:
                await self.update_message_read_status(message)
                
                # Notify the sender that their message was read
                await self.channel_layer.group_send(
                    f'chat_{self.listing_id}',
                    {
                        'type': 'message_read',
                        'message_id': message.id,
                        'is_read': True,
                        'read_at': message.read_at.isoformat()
                    }
                )
        except Exception as e:
            print(f"Error marking all messages as read: {e}")

    @database_sync_to_async
    def get_unread_messages(self, listing_id, user_id):
        """Get all unread messages in a chat not sent by the current user."""
        return list(ChatMessage.objects.filter(
            listing_id=listing_id,
            is_read=False
        ).exclude(user_id=user_id))

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for handling real-time notifications
    """
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            # Reject connection if user is not authenticated
            await self.close()
            return
        
        # Create a user-specific notification group
        self.notification_group_name = f'notifications_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Could be used for acknowledgements, etc.
        pass
    
    # Receive message from notification group
    async def notification_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        })) 