"""Listing endpoints for API v1."""

from django.db.models import Count
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters.listings import ListingFilter
from api.v1.permissions import IsLandlord, IsOwnerOrReadOnly
from api.v1.serializers import listings as serializers
from listings.models import Listing, ListingImage, Favorite, SavedSearch


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(is_direct_message=False).select_related("landlord").prefetch_related("images")
    serializer_class = serializers.ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = ListingFilter
    search_fields = ["title", "description", "city", "suburb", "address"]
    ordering_fields = ["created_at", "price", "bedrooms", "bathrooms"]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return serializers.ListingCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsLandlord()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        listing = self.get_object()
        Favorite.objects.get_or_create(user=request.user, listing=listing)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        listing = self.get_object()
        Favorite.objects.filter(user=request.user, listing=listing).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        listings = Listing.objects.filter(landlord=request.user)
        page = self.paginate_queryset(listings)
        serializer = self.get_serializer(page or listings, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request, pk=None):
        listing = self.get_object()
        data = {
            "favorites": listing.favorited_by.count(),
            "images": listing.images.count(),
            "shares": listing.social_shares.count(),
        }
        return Response(data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def popular(self, request):
        listings = (
            Listing.objects.filter(is_available=True, is_direct_message=False)
            .annotate(favorite_count=Count("favorited_by"))
            .order_by("-favorite_count", "-created_at")[:10]
        )
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)


class ListingImageViewSet(viewsets.ModelViewSet):
    queryset = ListingImage.objects.all()
    serializer_class = serializers.ListingImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return ListingImage.objects.filter(listing__landlord=self.request.user)

    def perform_create(self, serializer):
        listing_id = self.kwargs.get("listing_pk") or self.request.data.get("listing")
        listing = Listing.objects.filter(id=listing_id, landlord=self.request.user).first()
        serializer.save(listing=listing)


class FavoriteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related("listing", "listing__landlord").prefetch_related("listing__images")


class ListingFavoriteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        listing_id = self.kwargs.get("listing_pk")
        return Favorite.objects.filter(listing_id=listing_id).select_related("listing", "user")


