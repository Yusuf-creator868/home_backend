from django.urls import path
from . import consumers

websockets_urlpatterns = [
      path('wss/chat/<int:conversation_id>/', consumers.PrivateChatConsumer.as_asgi()),
]