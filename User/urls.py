from django.urls import path
from .views import *
from Homes.views import *


urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CusromRefreshTokenView.as_view(), name="token_refresh"),
    path("logout/", logout, name="logout"),
    path("register/", register),
    path("authenticated/", is_authenticated),
    path('userhomes/', userhomes, name='user-posts'),
    # path('chatview/', chat_view, name = 'chat_view'),
    # path('chatpost/', chat_post, name = 'chat_post'),

]