"""Roommate feature viewsets."""

from django.db.models import Prefetch
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters.roommate import RoommateProfileFilter
from api.v1.serializers import roommate as serializers
from listings.models import RoommateProfile, RoommateConnection


class RoommateProfileViewSet(viewsets.ModelViewSet):
    queryset = (
        RoommateProfile.objects.filter(is_active=True)
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "connection_requests",
                queryset=RoommateConnection.objects.filter(status="pending"),
            )
        )
    )
    serializer_class = serializers.RoommateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = RoommateProfileFilter
    search_fields = ["title", "city", "suburb", "bio"]
    ordering_fields = ["created_at", "min_budget", "max_budget", "move_in_date"]

    def get_queryset(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return RoommateProfile.objects.filter(user=self.request.user)
        if self.action == "mine":
            return RoommateProfile.objects.filter(user=self.request.user)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return serializers.RoommateProfileCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="me")
    def mine(self, request):
        profile = self.get_queryset().first()
        if not profile:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class RoommateConnectionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.RoommateConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        roommate_profile_id = self.kwargs.get("roommate_pk")
        return RoommateConnection.objects.filter(roommate_profile_id=roommate_profile_id).select_related(
            "requester", "roommate_profile", "roommate_profile__user"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.RoommateConnectionCreateSerializer
        if self.action in {"update", "partial_update"}:
            return serializers.RoommateConnectionUpdateSerializer
        if self.action in {"list", "retrieve"}:
            return serializers.RoommateConnectionSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        roommate_profile_id = self.kwargs.get("roommate_pk")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        connection = RoommateConnection.objects.create(
            roommate_profile_id=roommate_profile_id,
            requester=request.user,
            **serializer.validated_data,
        )

        read_serializer = serializers.RoommateConnectionSerializer(connection)
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        if instance.requester != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.status = "cancelled"
        instance.save(update_fields=["status", "updated_at"])

    def update(self, request, *args, **kwargs):  # pylint: disable=arguments-differ
        instance = self.get_object()
        if instance.roommate_profile.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

