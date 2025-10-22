"""Authentication endpoints for API v1."""

from django.contrib.auth import get_user_model, login, logout
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.serializers import authentication as serializers


User = get_user_model()


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Handle user registration flows."""

    queryset = User.objects.all()
    serializer_class = serializers.RegisterSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def activate(self, request):
        serializer = serializers.ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionViewSet(viewsets.ViewSet):
    """Session and token management endpoints."""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        serializer = serializers.LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        serializer = serializers.LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def refresh(self, request):
        serializer = serializers.RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = RefreshToken(serializer.validated_data["refresh"])
        data = {
            "access": str(refresh_token.access_token),
            "refresh": str(refresh_token),
        }
        return Response(data, status=status.HTTP_200_OK)

