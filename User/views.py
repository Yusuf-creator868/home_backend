from django.shortcuts import render
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import *
from .serializer import *
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
import requests
from .utils import *

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
  
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens["access"]
            refresh_token = tokens["refresh"]

            res = Response()
            res.data = {"success": True}

            res.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,          # 🔥 MUST be True in production
                samesite="None",      # 🔥 CRITICAL
                path="/"
            )
            res.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                path="/"
            )   
            return res

    
    

    

class CusromRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token
            
            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed': True}

            res.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,          # 🔥 MUST be True in production
                samesite="None",      # 🔥 CRITICAL
                path="/"
            )
            return res

        # except:
        #     return Response({'refreshed': False})
        

@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    token = request.data.get('token')
    
    if not token:
        return Response({'error': "No token provided"}, status=404)
    
    google_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
    response = requests.get(google_url)
    
    if response.status_code != 200:
        return Response({"error": "Invalid token"}, status=400)
    
    data = response.json()
    
    email = data.get('email')
    name = data.get('name')
    
    if not email:
        return Response({"error": "Email not available"}, status=400)
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": email}
    )
    
    response = Response({"success": True})
    
    return set_jwt_cookies(response, user)

        

@api_view(["POST"])
def logout(request):
    try:
        res = Response()
        res.data = {"success": True}
        res.delete_cookie("access_token", path="/")
        res.delete_cookie("refresh_token", path="/")
        return res
    except:
        return Response({"success": False})
    

    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({"authenticated": True})


@api_view(["POST"])
# @permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def private_conversation(request):
    user1 = request.user
    user2_id = request.data.get("user_id")
    
    user2 = get_object_or_404(User, id=user2_id)
        
    conversation = PrivateConversation.objects.filter(participants = user1).filter(participants = user2).first()     
    
    if not conversation:
        conversation = PrivateConversation.objects.create()
        conversation.participants.add(user1, user2)
    
    serializer = PrivateConversationSerializer(conversation, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rooms(request):
    user = request.user
    rooms = PrivateConversation.objects.filter(participants = user)
    serializer = PrivateConversationSerializer(rooms, many=True,  context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def private_messages(request, conversation_id):

    conversation = get_object_or_404(
    PrivateConversation,
    id=conversation_id,
    participants=request.user
)

    messages = conversation.messages.all().order_by("timestamp")

    serializer = PrivateMessageSerializer(messages, many=True, context={'request': request})

    return Response(serializer.data)