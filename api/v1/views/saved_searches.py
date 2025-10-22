"""Saved search endpoints."""

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers import listings as listing_serializers
from api.v1.serializers import saved_searches as serializers
from listings.models import SavedSearch


class SavedSearchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = listing_serializers.SavedSearchSerializer

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return serializers.SavedSearchCreateUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle(self, request, pk=None):
        saved_search = self.get_object()
        saved_search.is_active = not saved_search.is_active
        saved_search.save(update_fields=["is_active"])
        return Response({"is_active": saved_search.is_active})

    @action(detail=True, methods=["get"], url_path="matches")
    def matches(self, request, pk=None):
        saved_search = self.get_object()
        listings = saved_search.get_matching_listings()
        serializer = listing_serializers.ListingSerializer(listings, many=True, context={"request": request})
        return Response(serializer.data)


class SavedSearchAlertViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = listing_serializers.ListingSerializer

    def get_queryset(self):
        saved_search = SavedSearch.objects.filter(id=self.kwargs.get("search_pk"), user=self.request.user).first()
        if not saved_search:
            return SavedSearch.objects.none()
        return saved_search.get_matching_listings()

