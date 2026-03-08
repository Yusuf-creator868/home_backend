import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .models import PrivateConversation, PrivateMessage
from urllib.parse import parse_qs
import jwt
from django.conf import settings

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
    
        # Authenticate user
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")

        if not token:
           await self.close()
           return
        try: 
            decoded = jwt.decode(token[0], settings.SECRET_KEY, algorithms=["HS256"])
            self.user = await database_sync_to_async(User.objects.get)(id=decoded["user_id"])
        except Exception:
            await self.close()
            return
        
        
        if not self.user.is_authenticated: 
            await self.close() 
            return
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'private_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_body = data.get('body')

        if message_body:
            message = await self.create_message(message_body)

            # Send message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'sender': message.sender.username,
                        'body': message.body,
                        'timestamp': str(message.timestamp)
                    }
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    # DB methods
    @database_sync_to_async
    def check_participant(self):
        try:
            conversation = PrivateConversation.objects.get(id=self.conversation_id)
            return self.user in conversation.participants.all()
        except PrivateConversation.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, body):
        conversation = PrivateConversation.objects.get(id=self.conversation_id)
        return PrivateMessage.objects.create(
            conversation=conversation,
            sender=self.user,
            body=body
        )