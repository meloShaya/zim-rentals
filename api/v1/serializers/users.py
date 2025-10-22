"""User serializers for API v1."""

from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "profile_picture",
            "bio",
            "is_verified_landlord",
        ]
        read_only_fields = ["id", "is_verified_landlord"]


class UserDetailSerializer(UserSerializer):
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["date_joined"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "bio"]


class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_picture"]

