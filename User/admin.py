from django.contrib import admin
from .models import *

admin.site.register(PrivateConversation)
admin.site.register(PrivateMessage)
admin.site.register(UserActivity)

# Register your models here.
