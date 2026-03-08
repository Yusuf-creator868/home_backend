from django.urls import path
from . import consumers

websockets_urlpatterns = [
      path('ws/chat/<int:conversation_id>/', consumers.PrivateChatConsumer.as_asgi()),
]