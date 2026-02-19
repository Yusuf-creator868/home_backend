from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Home, Images, FavoriteCart, FavoriteItems, Profile
from .serializer import HomeSerializer, FavoritCartSerializer, FavoriteCartItemSerializer, HomeDetailSerializer, ProfileSerializer, HomeImageGallary
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny 
from django.shortcuts import get_object_or_404



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_home(request):
    user = request.user
    district = request.data.get("district")
    rooms = request.data.get("rooms")
    bedrooms = request.data.get("bedrooms")
    bedrooms_descrip = request.data.get('bedrooms_descrip')
    bathrooms = request.data.get("bathrooms")
    bathrooms_descrip = request.data.get("bathrooms_descrip")
    livingroom_descrip = request.data.get("livingroom_descrip")
    kitchen_descrip = request.data.get("kitchen_descrip")
    area = request.data.get("area")
    description = request.data.get("description")
    price = request.data.get("price")
    images = request.FILES.getlist("images")

    if not (district and description and price):
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    home = Home.objects.create(
        user = user,
        district = district,
        rooms = rooms, 
        description = description,
        price = price,
        bedrooms = bedrooms,
        bedrooms_descrip = bedrooms_descrip,
        bathrooms = bathrooms,
        bathrooms_descrip = bathrooms_descrip,
        livingroom_descrip = livingroom_descrip,
        kitchen_descrip = kitchen_descrip,
        area = area

    )

    for img in images:
        Images.objects.create(home = home, image = img)

    serializer = HomeSerializer(home)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




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
    home = Home.objects.all()
    serializer = HomeSerializer(home, many = True)
    return Response(serializer.data)


@api_view(["GET"])
def HomeDetailPage(request, id):
    home = Home.objects.get(id = id)
    serializer = HomeDetailSerializer(home)
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







