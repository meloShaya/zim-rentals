"""Messaging serializers."""

from rest_framework import serializers

from listings.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "listing",
            "message",
            "user",
            "sender",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "listing", "is_read", "read_at", "created_at", "sender"]

    def get_sender(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["message"]

