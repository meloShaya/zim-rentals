from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import ListingViewSet, ListingImageViewSet, FavoriteViewSet, ChatMessageViewSet

# Create the main router
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'listing-images', ListingImageViewSet, basename='listing-image')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

# Create nested routers for listing-related resources
listings_router = routers.NestedSimpleRouter(router, r'listings', lookup='listing')
listings_router.register(r'messages', ChatMessageViewSet, basename='listing-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(listings_router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 