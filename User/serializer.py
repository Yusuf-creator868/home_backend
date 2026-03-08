from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from .models import *

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User(
            username = validated_data["username"],
            email = validated_data["email"]
         )
        user.set_password(validated_data["password"])
        user.save() 
        return user
    


class PrivateMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()  # or username

    class Meta:
        model = PrivateMessage
        fields = ['id', 'sender', 'body', 'timestamp']

class PrivateConversationSerializer(serializers.ModelSerializer):
    messages = PrivateMessageSerializer(many=True, read_only=True)
    participants = serializers.StringRelatedField(many=True)

    class Meta:
        model = PrivateConversation
        fields = ['id', 'participants', 'messages']
        
class PrivateConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = PrivateConversation
        fields = ['id', 'other_user']
        
    def get_other_user(self, obj):
        user = self.context['request'].user
        other = obj.participants.exclude(id = user.id).first()
        return {
            "id": other.id,
            "username": other.username
        }



