from rest_framework import serializers
from .models import Home, FavoriteCart, FavoriteItems, Images, Profile
from django.utils.timesince import timesince
from django.utils import timezone



class ProfileSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(read_only = True)

    class Meta:
        model = Profile
        fields = [ "id", 'users', 'role', 'name_user', 'phone_number', 'city']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data["users"] = request.user
        return super().create(validated_data)



class PostHomeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Images
        fields = ["id", "image"]

class HomeSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    is_old = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = ["id", "district", "rooms", "price", "first_image", "created_at", "is_old"]

    def get_first_image(self, obj):
        image = obj.images.first()
        if image:
            return image.image.url
        return None
    
    def get_created_at(self, obj):
        time = timesince(obj.created_at)

        first_part = time.split(",")[0]
        return first_part + " ago"

    def get_is_old(self, obj):
        delta =timezone.now() - obj.created_at
        return delta.days > 2


class HomeDetailSerializer(serializers.ModelSerializer):
    images = PostHomeSerializer(many = True, read_only = True)
    user = serializers.CharField(source = 'user.username', read_only = True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields =["id", "district", "rooms", "city", "description", "bedrooms", "bedrooms_descrip", "bathrooms", "bathrooms_descrip", "livingroom_descrip", "kitchen_descrip", "area", "created_at", "images", "price", "user"]


    def get_created_at(self, obj):
        time = timesince(obj.created_at)

        first_part = time.split(",")[0]
        return first_part + " ago"





class FavoriteCartItemSerializer(serializers.ModelSerializer):
    homes = HomeSerializer(read_only = True)
    class Meta:
        model = FavoriteItems
        fields = ["id", "homes", "quantity"]



class FavoritCartSerializer(serializers.ModelSerializer):
    items = FavoriteCartItemSerializer(read_only = True, many = True)
    class Meta:
        model = FavoriteCart
        fields = ["id", "fav_code", "items",]

class HomeImageGallary(serializers.ModelSerializer):
    images = PostHomeSerializer(many = True, read_only = True)

    class Meta:
        model = Home
        fields = ["id", "district", "images"]







