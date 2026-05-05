from django.urls import re_path
from . import consumers

websockets_urlpatterns = [
      re_path('ws/chat/<int:conversation_id>/', consumers.PrivateChatConsumer.as_asgi()),
]