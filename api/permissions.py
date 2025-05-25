from rest_framework import permissions
from listings.models import ChatMessage

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'landlord'):
            return obj.landlord == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'listing'):
            # For objects related to listings
            return obj.listing.landlord == request.user
        return False

class IsChatMessageParticipant(permissions.BasePermission):
    """
    Permission to only allow participants of a chat to view messages.
    """
    def has_permission(self, request, view):
        # Allow all authenticated requests initially
        # Further filtering will be done in the view
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, ChatMessage):
            # User is a participant if they are the sender or the receiver
            # For the chat model in this app, the user is always the sender
            # The listing owner is the implicit recipient
            return obj.user == request.user or obj.listing.landlord == request.user
        return False

class IsLandlordUser(permissions.BasePermission):
    """
    Custom permission to only allow users with user_type 'landlord' to perform an action.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and if their user_type is 'landlord'.
        return request.user and request.user.is_authenticated and request.user.user_type == 'landlord' 