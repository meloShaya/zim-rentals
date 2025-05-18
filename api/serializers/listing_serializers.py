from rest_framework import serializers
from listings.models import Listing, ListingImage, Favorite, ChatMessage, SocialShare
from .user_serializers import UserSerializer

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'listing', 'image', 'created_at']
        read_only_fields = ['created_at']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'listing', 'created_at']
        read_only_fields = ['created_at']

class SocialShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialShare
        fields = ['id', 'listing', 'source', 'created_at']
        read_only_fields = ['created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'listing', 'user', 'sender_details', 'message', 
                  'is_read', 'read_at', 'created_at']
        read_only_fields = ['created_at', 'read_at', 'user', 'listing']
        extra_kwargs = {
            'listing': {'required': False},
            'user': {'required': False}
        }

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    landlord_details = UserSerializer(source='landlord', read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'currency', 'landlord', 'landlord_details',
            'address', 'city', 'suburb', 'latitude', 'longitude',
            'property_type', 'bedrooms', 'bathrooms', 'is_furnished', 'has_water',
            'has_electricity', 'has_wifi', 'is_available',
            'created_at', 'updated_at', 'images', 'phone_number', 'whatsapp_number'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ListingDetailSerializer(ListingSerializer):
    favorites_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta(ListingSerializer.Meta):
        fields = ListingSerializer.Meta.fields + ['favorites_count', 'shares_count', 'is_favorited']
    
    def get_favorites_count(self, obj):
        return Favorite.objects.filter(listing=obj).count()
    
    def get_shares_count(self, obj):
        return SocialShare.objects.filter(listing=obj).count()
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(listing=obj, user=request.user).exists()
        return False 