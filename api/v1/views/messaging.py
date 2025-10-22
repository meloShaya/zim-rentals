"""Messaging endpoints for API v1."""

from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsChatParticipant
from api.v1.serializers import messaging as serializers
from listings.models import ChatMessage, Listing


class ListingMessageViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]

    def get_queryset(self):
        listing_id = self.kwargs.get("listing_pk")
        return (
            ChatMessage.objects.filter(listing_id=listing_id)
            .select_related("user", "listing", "listing__landlord")
            .order_by("created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.ChatMessageCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        listing = Listing.objects.filter(id=self.kwargs.get("listing_pk")).first()
        serializer.save(user=self.request.user, listing=listing)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, listing_pk=None, pk=None):  # pylint: disable=unused-argument
        message = self.get_object()
        if message.user_id == request.user.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save(update_fields=["is_read", "read_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            ChatMessage.objects.filter(listing__is_direct_message=True)
            .filter(listing__landlord=user) | ChatMessage.objects.filter(user=user, listing__is_direct_message=True)
        ).select_related("listing", "listing__landlord", "user").order_by("-created_at")

