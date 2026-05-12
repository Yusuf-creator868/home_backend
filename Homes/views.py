from django.shortcuts import render
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializer import *
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny 
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import (SearchVector, SearchQuery, SearchRank, TrigramSimilarity)
from django.db.models import Q
from User.HellperFunctionActive import *
from django.utils import timezone
from datetime import timedelta
from User.serializer import *
from django.db.models import Count


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_home(request):
    user = request.user
    home = Home.objects.create(user = user, status = 'draft')
    return Response({'id': home.id}, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_home(request, pk):
    home = Home.objects.get(id = pk, user = request.user)
    
    serializer = HomesSerializer(
        home,
        data=request.data,
        partial=True  # IMPORTANT for PATCH
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_images(request, pk):
    home = Home.objects.get(id=pk, user=request.user)

    images = request.FILES.getlist("images")

    for img in images:
        Images.objects.create(home=home, image=img)

    return Response({"message": "Images uploaded"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def publish_home(request, pk):
    home = Home.objects.get(id = pk, user = request.user)
    home.status = 'published'
    home.save()
    return Response({
        "message": "Home published successfully",
        "status": home.status
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_profile(request):
    serializer = ProfileSerializer(data = request.data, context = {"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_profile(request):
    try:
        profile = Profile.objects.get(users=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
    



    

@api_view(["GET"])
def HomePage(request):
    cache_key = 'homepage_data'
    data = cache.get(cache_key)
    print("CACHE HIT:", data is not None)
    print("CACHE VALUE:", data)
    if data is None:
        home = Home.objects.all()[:6]
        serializer = HomeSerializer(home, many = True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60*20)
        
    return Response(data)



@api_view(["GET"])
def HomeDetailPage(request, id):
    home = Home.objects.get(id = id)
    ip = request.META.get("REMOTE_ADDR")
    
    # Views Feature
    if request.user.is_authenticated:
        
        already_viewed = PropertyView.objects.filter(
            property=home,
            user=request.user,
        ).exists()
        
        if not already_viewed:
            PropertyView.objects.create(
                property=home,
                user=request.user,
                ip_address=ip
            )
    else:
        already_viewed = PropertyView.objects.filter(
            property=home,
            ip_address=ip
        ).exists()
        
        if not already_viewed:
            PropertyView.objects.create(
                property=home,
                ip_address=ip
            )
        
            
    if request.user.is_authenticated:         
    # Recent activities feature 
        recent = UserActivity.objects.filter(
            user=request.user,
            action="view_property",
            object_id=home.id,
            created_at__gte=timezone.now() - timedelta(minutes=30)).exists()
    
        if not recent:
            log_activity(request.user, 'view_property', home.id, {
                'title': home.district,
                'city': home.city,
            })
        

    serializer = HomeDetailSerializer(home)       
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_activity(request):
    activity = UserActivity.objects.filter(user = request.user).order_by('-created_at')[:4]
    serializer = SerializerUserActivity(activity, many = True)
    return Response(serializer.data)

@api_view(["POST"])
def AddItem(request):
    try:
        fav_code = request.data.get("fav_code")
        home_id = request.data.get("home_id")

        cart, created = FavoriteCart.objects.get_or_create(fav_code = fav_code )
        home= Home.objects.get(id=home_id)

        cartitem, created = FavoriteItems.objects.get_or_create(favcart = cart, homes = home )
        cartitem.quantity = 1
        cartitem.save()

        serializer = FavoriteCartItemSerializer(cartitem)

        return Response({"data": serializer.data, "massage": "Cart Item created successfully!"} )
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(["GET"])
def product_in_card(request):
    fav_code = request.query_params.get("fav_code")
    home_id = request.query_params.get("home_id")

    cart = FavoriteCart.objects.get(fav_code = fav_code)
    home= Home.objects.get(id=home_id)

    product_exists_in_card = FavoriteItems.objects.filter(favcart=cart, homes = home).exists()

    return Response({"product_in_cart": product_exists_in_card})


@api_view(["GET"])
def get_cart(request):
    fav_code = request.query_params.get('fav_code')
    cart = FavoriteCart.objects.get(fav_code = fav_code)
    serializer = FavoritCartSerializer(cart)
    return Response(serializer.data)

@api_view(["GET"])
def get_gallary(request, pk):
    image = get_object_or_404(Images, id=pk)
    home = image.home
    serializer = HomeImageGallary(home)
    return Response(serializer.data)

@api_view(["DELETE"])
def delhome(request, pk):
    delete = FavoriteItems.objects.get(id = pk)
    delete.delete()
    return Response({"message": "Deleted successfully"})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def userdelhome(request, pk):
    userdelete = request.user.userhome.get(id = pk)
    userdelete.delete()
    return Response({"message": "Deleted successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def userhomes(request):
    userhomes = request.user.userhome.all()
    userhomesserializer = HomeSerializer(userhomes, many = True)
    return Response(userhomesserializer.data)


@api_view(['GET'])
def property_search(request):
    query = request.GET.get('q', '')
    
    vector = (
        SearchVector('district', weight = 'A')
    )
    
    search_query = SearchQuery(query)
    
    if len(query) < 4:
        results = Home.objects.filter(
        district__icontains=query
    )[:20]
    else:
        results = Home.objects.annotate(
            rank = SearchRank(vector, search_query),
            similarity = (
                TrigramSimilarity('district', query)
            )
    ).filter(
        Q(rank__gt = 0.1) | Q(similarity__gt = 0.2)
    ).order_by('-rank', '-similarity')[:20]
    
    serializer = HomeSerializer(results, many = True)
    return Response(serializer.data)

