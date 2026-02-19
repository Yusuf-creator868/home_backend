from django.db import models
from django.contrib.auth.models import User
from django.db.models import Prefetch


class ConversetionManager(models.Manager):
      def get_queryset(self):
            return super().get_queryset().prefetch_related(
                  Prefetch('participants', queryset=User.objects.only('id', 'username'))
            )
    
class Conversetion(models.Model):
      participants = models.ManyToManyField(User, related_name = 'conversations')
      created_at = models.DateTimeField(auto_now_add = True)
      objects = ConversetionManager()

      def __str__(self):
            participant_names = " ,".join([user.username for user in self.participants.all()]) 
            return f"Conversation with {participant_names}"
      
class Message(models.Model):
      conversation = models.ForeignKey(Conversetion, on_delete = models.CASCADE, related_name = 'message')
      sender = models.ForeignKey(User, on_delete = models.CASCADE)
      content = models.TextField()
      timestamp = models.DateTimeField(auto_now_add = True)

      def __str__(self):
            return f"Message from {self.sender.username} in {self.content[:20]}"