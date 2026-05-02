from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Homes.views import *
from User.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", HomePage, name = "homepage"),
    path("api/", include("User.urls")),
    path("home/<int:id>", HomeDetailPage, name = "HomeDetaiPage" ),
    path("get_cart/", get_cart, name = "favcart"),
    path("product_in_cart/", product_in_card, name="product_in_cart"),
    path("add_items/", AddItem, name = "AddItem"),
    path("delete/<int:pk>", delhome, name="delhome"),
    
    path("create_home/", create_home, name="createhome"),
    path('update_home/<int:pk>', update_home, name='update_home'),
    path('uploadimage_home/<int:pk>', upload_images, name='upload_image'),
    path('upload_home/<int:pk>', publish_home, name = 'publish_home'),
    
    path('get_user_activity/', get_user_activity, name = 'get_user_activity'),
    
    path("api/create_profile/", create_profile, name="createhome"),
    path("api/get_my_profile/", get_my_profile, name="createhome"),
    path('userdelethome/<int:pk>', userdelhome, name='userdeletehome'),
    path("get_gallary/<int:pk>", get_gallary),
    path("private/rooms/", get_rooms),
    path('private_conversation', private_conversation, name = 'private_conversation'),
    path('private_messages/<int:conversation_id>', private_messages, name = 'private_conversation'),
    path("auth/google/", google_login),
    path("api/search/", property_search),
    
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)