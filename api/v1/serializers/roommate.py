"""Roommate feature serializers."""

from rest_framework import serializers

from listings.models import RoommateProfile, RoommateConnection


class RoommateProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = RoommateProfile
        fields = [
            "id",
            "user",
            "title",
            "age",
            "gender",
            "city",
            "suburb",
            "min_budget",
            "max_budget",
            "move_in_date",
            "lifestyle",
            "bio",
            "preferences",
            "is_smoker",
            "has_pets",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
        }


class RoommateProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommateProfile
        exclude = ["user", "created_at", "updated_at"]


class RoommateConnectionSerializer(serializers.ModelSerializer):
    roommate_profile = RoommateProfileSerializer(read_only=True)

    class Meta:
        model = RoommateConnection
        fields = [
            "id",
            "requester",
            "roommate_profile",
            "message",
            "status",
            "created_at",
            "updated_at",
            "responded_at",
        ]
        read_only_fields = [
            "id",
            "requester",
            "roommate_profile",
            "status",
            "created_at",
            "updated_at",
            "responded_at",
        ]


class RoommateConnectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommateConnection
        fields = ["message"]


class RoommateConnectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommateConnection
        fields = ["status"]

