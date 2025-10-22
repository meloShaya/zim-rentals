"""Listing related serializers."""

from rest_framework import serializers

from listings.models import Listing, ListingImage, Favorite, SavedSearch


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ["id", "image", "created_at"]
        read_only_fields = ["id", "created_at"]


class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    landlord_name = serializers.CharField(source="landlord.get_full_name", read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "price",
            "currency",
            "city",
            "suburb",
            "address",
            "latitude",
            "longitude",
            "property_type",
            "bedrooms",
            "bathrooms",
            "is_furnished",
            "has_water",
            "has_electricity",
            "has_wifi",
            "is_available",
            "created_at",
            "updated_at",
            "phone_number",
            "whatsapp_number",
            "featured_image",
            "landlord",
            "landlord_name",
            "images",
            "is_direct_message",
            "is_favorited",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "landlord",
            "is_direct_message",
            "is_favorited",
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()


class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        exclude = ["landlord", "created_at", "updated_at", "is_direct_message"]


class FavoriteSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "listing", "created_at"]
        read_only_fields = ["id", "created_at", "listing"]


class SavedSearchSerializer(serializers.ModelSerializer):
    match_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SavedSearch
        fields = [
            "id",
            "name",
            "city",
            "suburb",
            "property_type",
            "max_price",
            "min_price",
            "bedrooms",
            "bathrooms",
            "is_furnished",
            "is_active",
            "created_at",
            "last_sent_at",
            "match_count",
        ]
        read_only_fields = ["id", "created_at", "last_sent_at", "match_count"]


