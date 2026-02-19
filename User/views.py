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
                value= access_token,
                httponly=True,
                secure=True,     # only over HTTPS
                samesite="None",
                path="/"
            )
            res.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,     # only over HTTPS
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
                value=  access_token ,
                httponly= True,
                secure=True,
                samesite = "None",
                path="/"
            )
            return res

        # except:
        #     return Response({'refreshed': False})
        


        

@api_view(["POST"])
def logout(request):
    try:
        res = Response()
        res.data = {"success": True}
        res.delete_cookie("access_token", path="/", samesite = "None")
        res.delete_cookie("refresh_token", path="/", samesite = "None")
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


class ConversationListCreateView(generics.ListCreateAPIView):
     
     serializer_class = ConversationSerializer
     permission_classes = [IsAuthenticated]

     def get_queryset(self):
          return (Conversetion.objects.filter(participants = self.request.user).prefetch_related('participants'))

     def create(self, request, *args, **kwargs):
        participants_data = request.data.get('participants', [])

        if len(participants_data) != 2:
             return Response(
                  {'error': "A conversetion need exactly two particiapants"},
                  status = status.HTTP_400_BAD_REQUEST
             )
        
        if str(request.user.id) not in map(str, participants_data):
             return Response(
                  {'error': "You are not a participant of this conversation"},
                  status = status.HTTP_403_FORBIDDEN
             )
        
        users = User.objects.filter(id__in = participants_data)
        if users.count() != 2:
             return Response(
                  {'error': "A conversetion need exactly two particiapants"},
                  status = status.HTTP_400_BAD_REQUEST
             )
        
        existing_conversation = Conversetion.objects.filter(
             participants__id = participants_data[0]
        ).filter(
              participants__id = participants_data[1]
        ).distinct()

        if existing_conversation.exists():
             return Response(
                  {'error': "A conversetion already exists between these particiapants"},
                  status = status.HTTP_400_BAD_REQUEST
             )
        
        conversetion = Conversetion.objects.create()
        conversetion.participants.set(users)

        serializer = self.get_serializer(conversetion)
        return Response(serializer.data, status = status.HTTP_201_CREATED)

class MessageListCreateView(generics.ListCreateAPIView):
     permission_classes = [IsAuthenticated]

     def get_queryset(self):
          conversation_id = self.kwargs['converstaion_id']
          converstion = self.get_conversation(conversation_id)

          return converstion.messages.order_by('timestamp')
     
     def get_serializer_class(self):
          if self.request.method == "POST":
               return CreateMessageSerializer
          return MessageSerializer
     
     def perform_create(self, serializer):
        print("Imcoming conversation", self.request.data)
        conversation_id = self.kwargs['converstaion_id']
        converstion = self.get_conversation(conversation_id)
        serializer.save(sender = self.request.user, conversation = converstion)

     def get_conversation(self, conversation_id):
          conversation = get_object_or_404(Conversetion, id=conversation_id)
          if self.request.user not in conversation.participants.all():
               raise PermissionDenied("You are not a participant of this conversation")
          return conversation
     
class MessageRetrievDestroyView(generics.RetrieveDestroyAPIView):
     permission_classes = [IsAuthenticated]
     serializer_class = MessageSerializer

     def get_queryset(self):
          conversation_id = self.kwargs['conversation_id']
          return Message.objects.filter(conversation_id=conversation_id)
     
     def perform_destroy(self, instance):
          if instance.sender != self.request.user:
               raise PermissionDenied("You are not the sender of this message")
          instance.delete()
          return Response(status = status.HTTP_204_NO_CONTENT)