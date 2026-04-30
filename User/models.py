from django.db import models
from django.contrib.auth.models import User

class PrivateConversation(models.Model):
    participants = models.ManyToManyField(User, related_name='private_chats')
    created_at = models.DateTimeField(auto_now_add=True)


    

class PrivateMessage(models.Model):
    conversation = models.ForeignKey(PrivateConversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} : {self.body}'
    
    class Meta:
        ordering = ['timestamp']
        
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    action = models.CharField(max_length=100)
    # e.g. "view_property", "save_property", "send_message"

    object_id = models.IntegerField(null=True, blank=True)
    # property id or chat id etc.

    metadata = models.JSONField(null=True, blank=True)
    # extra info like city, price, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user} activity'