from asgiref.sync import sync_to_async
import json
import jwt
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import *
from urllib.parse import parse_qs

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
      async def connect(self):
            query_string = self.scope['query_string'].decode('utf-8')
            params = parse_qs(query_string)
            token = params.get('token', [None])[0]

            if token:
                  try:
                        decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                        self.user = await self.get_user(decode_data['user_id'])
                        self.scope['user'] = self.user
                  except jwt.ExpiredSignatureError:
                        await self.close(code=4000)
                        return
                  except jwt.InvalidTokenError:
                        await self.close(code=4001)
                        return
            else:
                  await self.close(code=4002)
                  return
            
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
            self.room_group_name = f"caht_{self.conversation_id}"


            
            # Add channel to the group
            
            await self.channel_layer.group_add(
                  self.room_group_name,
                  self.channel_name
            )

            # Accept websocket connections

            await self.accept()

            user_data = await self.get_user_data(self.user)
            await self.channel_layer.group_send(
                  self.room_group_name,
                  {
                        'type': 'online_status',
                        'online_users': [user_data],
                        'status': 'online',
                  }
            )
      
      async def disconnect(self, close_code):
            if hasattr(self, 'room_group_name'):
                  user_data = await self.get_user_data(self.scope["user"])
                  await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                              'type': 'online_status',
                              'online_users': [user_data],
                              'status': 'offline',
                        }
                  )

                  await self.channel_layer.group_discard(
                        self.room_group_name,
                        self.channel_name
                  )
      
      async def receive(self, text_data ):
            text_data_json = json.load(text_data)
            event_type = text_data_json.get('type')

            if event_type == 'chat_message':
                  message_content = text_data_json.get('message')
                  user_id = text_data_json.get('user')

                  try:
                        user = await self.get_user(user_id)
                        conversation = await self.get_conversation(self.conversation_id)
                        from .serializer import UserListSerializer
                        user_data = UserListSerializer(user).data

                        # say message to the group/database

                        message = await self.save_message(conversation, user, message_content)

                        # broadcast the message to the group

                        await self.channel_layer.group_send(
                              self.room_group_name,
                              {
                                    'type': 'chat_message',
                                    'message': message.content,
                                    'user': user_data,
                                    'timestamp': message.timestamp.isoformat(),
                              }
                        )
                  except Exception as e:
                        print(f"Error saving message: {e}")

            elif event_type == "typing":
                  try:
                        user_data = await self.get_user_data(self.scope['user'])
                        receiver_id = text_data_json.get('receiver')

                        if receiver_id is not None:

                              if isinstance(receiver_id, (str, int, float)):
                                    receiver_id = int(receiver_id)

                                    if receiver_id != self.scope['user'].id:
                                          print(F'{user_data['username']} is typing for Receiver: {receiver_id}')
                                          await self.channel_layer.group_send(
                                                self.room_group_name,
                                                {
                                                      'type': 'typing',
                                                      'user': user_data,
                                                      'receiver': receiver_id,
                                                }
                                          )
                                    else:
                                          print(f"User is typing for themselves")

                              else:
                                    print(f"Invalid receiver ID: {type(receiver_id)}")

                        else:
                              print(f"No receiver ID provided")

                  except ValueError as e:
                         print(f"Error parsing receiver ID: {e}")
                  
                  except Exception as e:
                         print(f"Error getting user data: {e}")

      
      # helper fumction

      async def chat_message(self, event):
            message = event['message']
            user = event['user']
            timestamp = event['timestamp']
            await self.send(text_data = json.dumps({
                  'type': "chat_message",
                  'message': message,
                  'user': user,
                  'timestamp': timestamp,
            }))

      
      async def typing(self, event):
            user = event['user'],
            receiver = event.get('receiver')
            is_typing = event.get('is_typing', False)
            await self.send(text_data = json.dumps({
                  'type': "typing",
                  'user': user,
                  'receiver': receiver,
                  'is_typing': is_typing,
            }))

      async def online_status(self, event):
            await self.send(text_data = json.dumps(event))

      @sync_to_async
      def get_user(self, user_id):
            return User.objects.get(id = user_id)
      
      @sync_to_async
      def get_user_data(self, user):
            from .serializer import UserListSerializer
            return UserListSerializer(user).data
      
      @sync_to_async
      def get_conversation(self, conversation_id):
            try:
                  return Conversetion.objects.get(id = conversation_id)
            except Conversetion.DoesNotExist:
                  print(f"Conversetion with id {conversation_id} does not exist")
                  return None
      

      @sync_to_async
      def save_message(self, conversation, user, content):
            message = Message.objects.create(
                  conversation = conversation,
                  sender = user,
                  content = content,
            )
            return message





            


      
