"""Notification serializers."""

from rest_framework import serializers

from listings.models import ChatMessage


class NotificationSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    landlord_name = serializers.CharField(source="listing.landlord.get_full_name", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "listing_title",
            "landlord_name",
            "message",
            "is_read",
            "created_at",
        ]


class MarkNotificationReadSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

