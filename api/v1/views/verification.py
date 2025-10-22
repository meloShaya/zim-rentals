"""Landlord verification endpoints."""

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1 import permissions as custom_permissions
from api.v1.serializers import verification as serializers
from accounts.models import LandlordVerification


class VerificationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return LandlordVerification.objects.select_related("user")
        return LandlordVerification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "admin_update":
            return serializers.VerificationAdminUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, custom_permissions.IsStaffOrReadOnly])
    def admin_update(self, request, pk=None):
        verification = self.get_object()
        serializer = self.get_serializer(verification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if verification.status == "approved":
            verification.user.is_verified_landlord = True
            verification.user.save(update_fields=["is_verified_landlord"])
        return Response(serializer.data, status=status.HTTP_200_OK)

