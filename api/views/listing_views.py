from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from listings.models import Listing, ListingImage, Favorite, ChatMessage
from api.serializers.listing_serializers import (
    ListingSerializer, ListingDetailSerializer, ListingImageSerializer,
    FavoriteSerializer, ChatMessageSerializer
)
from api.permissions import IsOwnerOrReadOnly, IsChatMessageParticipant

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'suburb', 'property_type', 'bedrooms', 'price', 'status']
    search_fields = ['title', 'description', 'city', 'suburb']
    ordering_fields = ['price', 'created_at', 'bedrooms']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ListingDetailSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        listing = self.get_object()
        user = request.user
        
        favorite, created = Favorite.objects.get_or_create(user=user, listing=listing)
        
        if created:
            return Response({'status': 'listing favorited'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'listing already favorited'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        listing = self.get_object()
        user = request.user
        
        try:
            favorite = Favorite.objects.get(user=user, listing=listing)
            favorite.delete()
            return Response({'status': 'listing unfavorited'}, status=status.HTTP_200_OK)
        except Favorite.DoesNotExist:
            return Response({'status': 'listing not favorited'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def favorites(self, request):
        user = request.user
        favorites = Listing.objects.filter(favorited_by__user=user)
        page = self.paginate_queryset(favorites)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

class ListingImageViewSet(viewsets.ModelViewSet):
    queryset = ListingImage.objects.all()
    serializer_class = ListingImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return ListingImage.objects.filter(listing__landlord=self.request.user)

    def perform_create(self, serializer):
        # Ensure the user only uploads images to their own listings
        listing_id = self.request.data.get('listing')
        try:
            listing = Listing.objects.get(id=listing_id, landlord=self.request.user)
            serializer.save(listing=listing)
        except Listing.DoesNotExist:
            return Response(
                {'error': 'You can only upload images to your own listings'}, 
                status=status.HTTP_403_FORBIDDEN
            )

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatMessageParticipant]

    def get_queryset(self):
        # Return messages where the user is either sender or the listing owner
        listing_id = self.kwargs.get('listing_id')
        
        return ChatMessage.objects.filter(
            listing__id=listing_id
        ).order_by('created_at')

    def perform_create(self, serializer):
        listing_id = self.kwargs.get('listing_id')
        try:
            # Use filter().first() instead of get() to avoid the DoesNotExist exception
            listing = Listing.objects.filter(id=listing_id).first()
            if listing is None:
                raise Listing.DoesNotExist(f"Listing with ID {listing_id} not found")
            serializer.save(user=self.request.user, listing=listing)
        except Exception as e:
            # Add more context to the error
            raise Exception(f"Error creating message: {str(e)}. Listing ID: {listing_id}, User: {self.request.user.username}")
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None, listing_id=None):
        message = self.get_object()
        
        # Only recipient can mark a message as read
        if message.user == request.user:
            return Response(
                {'error': 'You cannot mark your own messages as read'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        if not message.is_read:
            message.mark_as_read()
            return Response({'status': 'message marked as read'}, status=status.HTTP_200_OK)
            
        return Response({'status': 'message already read'}, status=status.HTTP_200_OK) 