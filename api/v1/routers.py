"""Implementation of versioned routers for API v1."""

from django.urls import include, path
from rest_framework_nested import routers

from api.v1.views import (
    authentication,
    listings,
    messaging,
    roommate,
    saved_searches,
    notifications,
    verification,
    users,
    metadata,
)


def get_urlpatterns() -> list:
    """Return urlpatterns for API v1."""

    router = routers.DefaultRouter()

    router.register("auth/users", authentication.RegisterViewSet, basename="auth-users")
    router.register("auth/sessions", authentication.SessionViewSet, basename="auth-sessions")
    router.register("users", users.UserViewSet, basename="users")
    router.register("listings", listings.ListingViewSet, basename="listings")
    router.register("favorites", listings.FavoriteViewSet, basename="favorites")
    router.register("roommates", roommate.RoommateProfileViewSet, basename="roommates")
    router.register("saved-searches", saved_searches.SavedSearchViewSet, basename="saved-searches")
    router.register("notifications", notifications.NotificationViewSet, basename="notifications")
    router.register("verifications", verification.VerificationViewSet, basename="verifications")

    listings_router = routers.NestedSimpleRouter(router, "listings", lookup="listing")
    listings_router.register("images", listings.ListingImageViewSet, basename="listing-images")
    listings_router.register("messages", messaging.ListingMessageViewSet, basename="listing-messages")
    listings_router.register("favorites", listings.ListingFavoriteViewSet, basename="listing-favorites")

    roommates_router = routers.NestedSimpleRouter(router, "roommates", lookup="roommate")
    roommates_router.register("connections", roommate.RoommateConnectionViewSet, basename="roommate-connections")

    saved_search_router = routers.NestedSimpleRouter(router, "saved-searches", lookup="search")
    saved_search_router.register("alerts", saved_searches.SavedSearchAlertViewSet, basename="search-alerts")

    urlpatterns = [
        path("", include(router.urls)),
        path("", include(listings_router.urls)),
        path("", include(roommates_router.urls)),
        path("", include(saved_search_router.urls)),
        path("metadata/", metadata.MetadataView.as_view(), name="metadata"),
    ]

    return urlpatterns

