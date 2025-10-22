"""API v1 custom permissions."""

from rest_framework import permissions


class IsLandlord(permissions.BasePermission):
    """Allow access only to users marked as landlords."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.user_type == "landlord")


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Restrict write access to object owners."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        if hasattr(obj, "landlord_id"):
            return obj.landlord_id == user.id
        if hasattr(obj, "user_id"):
            return obj.user_id == user.id
        if hasattr(obj, "listing") and hasattr(obj.listing, "landlord_id"):
            return obj.listing.landlord_id == user.id
        return False


class IsChatParticipant(permissions.BasePermission):
    """Allow access to chat messages only for participants."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.user_id == request.user.id or obj.listing.landlord_id == request.user.id


class IsStaffOrReadOnly(permissions.BasePermission):
    """Allow write access to staff users only."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsRequestUser(permissions.BasePermission):
    """Ensure the object belongs to the requesting user."""

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, "user_id") and obj.user_id == request.user.id

