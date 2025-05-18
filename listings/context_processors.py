from .models import ChatMessage, Listing
from django.conf import settings

def unread_messages(request):
    if request.user.is_authenticated:
        # Get all listings owned by the user
        listings = Listing.objects.filter(landlord=request.user)
        # Count unread messages
        unread_count = ChatMessage.objects.filter(
            listing__in=listings,
            is_read=False
        ).exclude(user=request.user).count()
    else:
        unread_count = 0
    
    return {
        'unread_messages_count': unread_count
    }

def google_maps_api_key(request):
    """
    Adds the Google Maps API key to the template context.
    """
    return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY} 