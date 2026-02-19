from rest_framework import serializers
from django.contrib.auth.models import User
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
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
    

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserListSerializer(many = True, read_only = True)
    class Meta:
        model = Conversetion
        fields = ('id', 'participants', 'created_at')

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            return representation
    
class MessageSerializer(serializers.ModelSerializer):
    sender = UserListSerializer()
    participants = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'timestamp', 'participants' )

        def get_participants(self, obj):
            return UserListSerializer(obj.conversation.participants.all(), many = True).data
        

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('conversation', 'content' )

