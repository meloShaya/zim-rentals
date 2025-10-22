"""Authentication serializers for API v1."""

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": _("Passwords do not match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ActivateAccountSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def save(self, **kwargs):
        # Placeholder for actual account activation logic (e.g., allauth integration)
        return None


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        login_value = attrs.get("login")
        password = attrs.get("password")

        user = authenticate(request=request, username=login_value, password=password)
        if not user:
            # Try email fallback
            try:
                user_obj = User.objects.get(email__iexact=login_value)
            except User.DoesNotExist:
                raise serializers.ValidationError(_("Invalid credentials."))
            user = authenticate(request=request, username=user_obj.username, password=password)

        if not user:
            raise serializers.ValidationError(_("Invalid credentials."))

        if not user.is_active:
            raise serializers.ValidationError(_("User account is disabled."))

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            RefreshToken(attrs["refresh"])
        except Exception as exc:  # pylint: disable=broad-except
            raise serializers.ValidationError(_("Invalid refresh token.")) from exc
        return attrs

