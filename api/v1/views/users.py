"""User profile endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.serializers import users as serializers


User = get_user_model()


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all().select_related("roommate_profile")
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(id=self.request.user.id)
        return self.queryset

    def get_serializer_class(self):
        if self.action in {"retrieve", "me"}:
            return serializers.UserDetailSerializer
        if self.action == "update_profile":
            return serializers.UserProfileUpdateSerializer
        if self.action == "update_avatar":
            return serializers.UserAvatarUpdateSerializer
        return serializers.UserSerializer

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="profile")
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="avatar")
    def update_avatar(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

