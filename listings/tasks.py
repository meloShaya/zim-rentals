import logging
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Count
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import timedelta

from .models import SavedSearch, Listing, ChatMessage

logger = logging.getLogger(__name__)

@shared_task
def check_new_listings_for_saved_searches():
    """
    Task to check for new listings that match saved searches
    and send notifications to users
    """
    logger.info("Running check_new_listings_for_saved_searches task")
    
    # Get active saved searches
    saved_searches = SavedSearch.objects.filter(is_active=True)
    
    if not saved_searches.exists():
        logger.info("No active saved searches found")
        return
    
    # Check each saved search for new matching listings
    for saved_search in saved_searches:
        # Skip if we've sent an alert in the last 24 hours
        last_sent = saved_search.last_sent_at
        if last_sent and timezone.now() < last_sent + timedelta(hours=settings.PRICE_ALERTS_FREQUENCY):
            continue
        
        # If never sent or sent more than 24 hours ago
        since_datetime = saved_search.last_sent_at or saved_search.created_at
        
        # Get matching listings created since last alert
        new_listings = saved_search.get_matching_listings(since_datetime=since_datetime)
        
        # If there are new listings, send alert
        if new_listings.exists():
            send_price_alert(saved_search.id, new_listings)
            
            # Update last_sent_at timestamp
            saved_search.last_sent_at = timezone.now()
            saved_search.save(update_fields=['last_sent_at'])
            
            logger.info(f"Sent alert for saved search {saved_search.id} with {new_listings.count()} new listings")

@shared_task
def send_price_alert(saved_search_id, listing_ids=None):
    """
    Send email and in-app notification for new listings matching a saved search
    """
    try:
        saved_search = SavedSearch.objects.get(id=saved_search_id)
        user = saved_search.user
        
        # Get the new listings if IDs were provided, otherwise use all matching listings
        if listing_ids:
            new_listings = Listing.objects.filter(id__in=listing_ids)
        else:
            new_listings = saved_search.get_matching_listings(since_datetime=saved_search.last_sent_at)
        
        if not new_listings.exists():
            return
        
        # Send email notification
        send_email_alert(user, saved_search, new_listings)
        
        # Send in-app notification via chat message
        send_chat_notification(user, saved_search, new_listings)
        
        # Update last sent timestamp
        saved_search.last_sent_at = timezone.now()
        saved_search.save(update_fields=['last_sent_at'])
        
        logger.info(f"Alert sent for saved search {saved_search.id} ({len(new_listings)} listings)")
        
    except SavedSearch.DoesNotExist:
        logger.error(f"SavedSearch with ID {saved_search_id} not found")
    except Exception as e:
        logger.error(f"Error sending price alert: {str(e)}")

def send_email_alert(user, saved_search, new_listings):
    """Send email alert about new listings"""
    if not user.email:
        return
    
    subject = f"New listings matching your saved search: {saved_search.name}"
    
    context = {
        'user': user,
        'saved_search': saved_search,
        'listings': new_listings,
        'listings_count': new_listings.count(),
    }
    
    html_message = render_to_string('listings/email/price_alert.html', context)
    plain_message = render_to_string('listings/email/price_alert_plain.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )

def send_chat_notification(user, saved_search, new_listings):
    """
    Send a system message via the chat system to notify the user about new listings
    Creates a special direct message listing for system notifications if needed
    """
    try:
        # Get or create a system notification listing for this user
        system_listing, created = Listing.objects.get_or_create(
            title="System Notifications",
            landlord_id=1,  # System user ID (admin)
            is_direct_message=True,
            is_available=True,
            defaults={
                'description': "System notifications and alerts",
                'price': 0,
                'city': 'harare',  # Default city
                'suburb': 'System',
                'address': 'System',
                'property_type': 'single',
                'bedrooms': 1,
                'bathrooms': 1,
                'phone_number': '000-000-0000'
            }
        )
        
        # Create message with links to the new listings
        message_text = f"🔔 Alert for your saved search '{saved_search.name}': {new_listings.count()} new listing(s) match your criteria!\n\n"
        
        # Add listing info to the message
        for listing in new_listings:
            message_text += f"• {listing.title} - ${listing.price} in {listing.suburb}, {listing.get_city_display()}\n"
        
        # Add link to view all listings
        message_text += f"\nView all your saved searches: /listings/saved-searches/"
        
        # Create the message
        message = ChatMessage.objects.create(
            listing=system_listing,
            user_id=1,  # System user ID (admin)
            message=message_text,
        )
        
        # Send WebSocket notification if user is online
        channel_layer = get_channel_layer()
        
        # Try to notify through WebSocket
        try:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user.id}',
                {
                    'type': 'notification_message',
                    'message': {
                        'type': 'price_alert',
                        'title': f"New listings for '{saved_search.name}'",
                        'body': f"Found {new_listings.count()} new listings matching your criteria",
                        'url': f"/listings/saved-searches/{saved_search.id}/",
                        'chat_message_id': message.id
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error creating chat notification: {str(e)}")

@shared_task
def cleanup_old_saved_searches():
    """Remove saved searches that haven't been used in a long time (90 days)"""
    cutoff_date = timezone.now() - timedelta(days=90)
    old_searches = SavedSearch.objects.filter(
        last_sent_at__lt=cutoff_date
    )
    count = old_searches.count()
    old_searches.delete()
    logger.info(f"Deleted {count} old saved searches not used in the last 90 days") 