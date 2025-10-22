"""Notification endpoints."""

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers import notifications as serializers
from listings.models import ChatMessage


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        return (
            ChatMessage.objects.filter(listing__is_direct_message=True)
            .exclude(user=self.request.user)
            .select_related("listing", "listing__landlord")
            .order_by("-created_at")
        )

    @action(detail=False, methods=["post"], url_path="mark-read")
    def mark_read(self, request):
        serializer = serializers.MarkNotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = ChatMessage.objects.filter(
            id__in=serializer.validated_data["ids"], listing__is_direct_message=True
        ).exclude(user=request.user).update(is_read=True)
        return Response({"updated": updated})

