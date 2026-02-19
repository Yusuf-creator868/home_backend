from django.urls import path
from .views import *
from Homes.views import userhomes


urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CusromRefreshTokenView.as_view(), name="token_refresh"),
    path("logout/", logout, name="logout"),
    path("register/", register),
    path("authenticated/", is_authenticated),
    path('userhomes/', userhomes, name='user-posts'),

    path('conversations/', ConversationListCreateView.as_view(), name = 'conversations_list'),
    path('conversations/<int:conversation_id>/messages/', MessageListCreateView.as_view(), name = 'message_list_create'),
    path('conversations/<int:conversation_id>/messages/<int:pk>/', MessageRetrievDestroyView.as_view(), name = 'message_detail_destroy'),


]