import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .models import PrivateConversation, PrivateMessage
# from urllib.parse import parse_qs
# import jwt
# from django.conf import settings
# from http.cookies import SimpleCookie
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        headers = dict(self.scope['headers'])

        cookie_header = headers.get(b'cookie', b'').decode()
        print("RAW COOKIE:", cookie_header)

        token = None

        for c in cookie_header.split('; '):
            if c.startswith('access_token='):
                token = c.split('=', 1)[1]
                break

        print("Token from cookie:", token)

        if not token:
            await self.close()
            return
        
        try:
            validated_token = UntypedToken(token)
            user_id = int(validated_token["user_id"])

            self.user = await database_sync_to_async(User.objects.get)(id=user_id)

            print("Authenticated:", self.user)

        except (InvalidToken, TokenError) as e:
            print("JWT ERROR:", e)
            await self.close()
            return
        
        
        
        
        if not self.user.is_authenticated: 
            await self.close() 
            return
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        
        is_participant = await self.check_participant()

        if not is_participant:
            await self.close()
            return
        
        self.room_group_name = f'private_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
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