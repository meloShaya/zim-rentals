from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, ListingImage, Favorite, ChatMessage, RoommateProfile, SocialShare, SavedSearch
from .forms import ListingForm, RoommateProfileForm, SavedSearchForm, ContactForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from django.template.loader import render_to_string
from django.core.mail import send_mail

def listing_list(request):
    # Get all available non-direct message listings
    all_listings = Listing.objects.filter(is_available=True, is_direct_message=False).order_by('-created_at')
    
    # Get filter parameters
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    property_type = request.GET.get('property_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    # Apply filters if provided
    if query:
        all_listings = all_listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(suburb__icontains=query) |
            Q(address__icontains=query)
        )
    
    if city:
        all_listings = all_listings.filter(city=city)
    
    if property_type:
        all_listings = all_listings.filter(property_type=property_type)
    
    if min_price:
        all_listings = all_listings.filter(price__gte=min_price)
    
    if max_price:
        all_listings = all_listings.filter(price__lte=max_price)
    
    # Pagination
    paginator = Paginator(all_listings, 6)  # Show 6 listings per page
    page = request.GET.get('page')
    
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        listings = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        listings = paginator.page(paginator.num_pages)
    
    # Check if this is an AJAX load more request
    if request.GET.get('format') == 'json' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        listing_list_html = render_to_string('listings/listing_cards.html', {'listings': listings})
        return JsonResponse({
            'html': listing_list_html,
            'has_next': listings.has_next(),
            'next_page': listings.next_page_number() if listings.has_next() else None
        })
    
    # Add cities and property types for the filter dropdown
    context = {
        'listings': listings,
        'query': query,
        'city': city,
        'property_type': property_type,
        'min_price': min_price,
        'max_price': max_price,
        'cities': Listing.CITIES,
        'property_types': Listing.PROPERTY_TYPES,
        'total_listings': all_listings.count(),
    }
    
    return render(request, 'listings/listing_list.html', context)

def search(request):
    # Redirect to listing_list with search parameters
    return redirect('listings:listing_list')

class ListingDetailView(DetailView):
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The GOOGLE_MAPS_API_KEY is now provided by our context processor
        # No need to add it again here
        
        # Check if user is authenticated for favorites
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                listing=self.object
            ).exists()
        
        # Track UTM parameters from social sharing
        utm_source = self.request.GET.get('utm_source')
        utm_medium = self.request.GET.get('utm_medium')
        utm_campaign = self.request.GET.get('utm_campaign')
        
        # If this is a social share visit, log it
        if utm_source and utm_medium == 'social' and utm_campaign == 'listing_share':
            self.track_social_share(utm_source)
        
        return context
    
    def track_social_share(self, source):
        """Track social media shares using the SocialShare model"""
        listing = self.object
        
        # Get client IP address
        ip_address = self.get_client_ip()
        
        # Record the share visit
        SocialShare.record_share_visit(
            listing=listing,
            source=source,
            ip_address=ip_address
        )
        
        # Also log it
        logger = logging.getLogger('listing_shares')
        logger.info(f"Listing #{listing.id} ({listing.title}) was visited from a {source} share from IP {ip_address}")
    
    def get_client_ip(self):
        """Get the client's IP address from the request"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

@login_required
def listing_create(request):
    # Check if the user is a landlord
    if request.user.user_type != 'landlord':
        messages.error(request, 'Only landlord accounts can create listings.')
        return redirect('listings:listing_list')
        
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.landlord = request.user
            listing.save()
            messages.success(request, 'Listing created successfully!')
            return redirect('listings:listing_detail', pk=listing.pk)
    else:
        form = ListingForm()
    return render(request, 'listings/listing_form.html', {'form': form})

@login_required
def listing_update(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.landlord:
        messages.error(request, 'You do not have permission to edit this listing.')
        return redirect('listings:listing_detail', pk=listing.pk)
    
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listings:listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/listing_form.html', {'form': form})

@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.landlord:
        messages.error(request, 'You do not have permission to delete this listing.')
        return redirect('listings:listing_detail', pk=listing.pk)
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted successfully!')
        return redirect('listings:listing_list')
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})

@login_required
def toggle_favorite(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
    
    if not created:
        favorite.delete()
        messages.success(request, 'Listing removed from favorites.')
    else:
        messages.success(request, 'Listing added to favorites.')
    
    return redirect('listings:listing_detail', pk=listing.pk)

@login_required
def chat(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    chat_messages = ChatMessage.objects.filter(listing=listing).order_by('created_at')
    
    # Mark messages from other users as read
    ChatMessage.objects.filter(
        listing=listing,
        is_read=False
    ).exclude(user=request.user).update(is_read=True, read_at=timezone.now())
    
    # Check if redirected from roommate finder
    from_roommate = 'from_roommate' in request.GET
    
    context = {
        'listing': listing,
        'chat_messages': chat_messages,
        'from_roommate': from_roommate,
    }
    return render(request, 'listings/chat.html', context)

@login_required
def landlord_messages(request):
    # For landlords: Get all listings owned by the landlord 
    # For regular users: Get all direct message listings where they've sent/received messages
    if hasattr(request.user, 'listings'):
        listings = Listing.objects.filter(
            Q(landlord=request.user) | 
            Q(is_direct_message=True, chat_messages__user=request.user)
        ).distinct()
    else:
        listings = Listing.objects.filter(
            is_direct_message=True, 
            chat_messages__user=request.user
        ).distinct()
    
    # Get all messages for these listings
    all_messages = ChatMessage.objects.filter(
        listing__in=listings
    ).select_related('user', 'listing').order_by('-created_at')
    
    # Group messages by listing
    messages_by_listing = {}
    
    # Process messages and only include listings that have messages
    for message in all_messages:
        listing_id = message.listing.id
        if listing_id not in messages_by_listing:
            messages_by_listing[listing_id] = {
                'listing': message.listing,
                'messages': [],
                'unread_count': 0
            }
        
        messages_by_listing[listing_id]['messages'].append(message)
        if not message.is_read and message.user != request.user:
            messages_by_listing[listing_id]['unread_count'] += 1
    
    # Sort listings with messages by latest message
    for listing_data in messages_by_listing.values():
        listing_data['messages'].sort(key=lambda x: x.created_at, reverse=True)
    
    context = {
        'messages_by_listing': messages_by_listing.values(),
    }
    return render(request, 'listings/landlord_messages.html', context)

@login_required
def mark_messages_read(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if listing.landlord != request.user:
        return HttpResponseForbidden()
    
    # Mark all unread messages as read for this listing
    ChatMessage.objects.filter(
        listing=listing,
        is_read=False
    ).exclude(user=request.user).update(is_read=True, read_at=timezone.now())
    
    return redirect('listings:landlord_messages')

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    listing = message.listing
    
    # Check if user has permission to delete this message
    if message.user != request.user and listing.landlord != request.user:
        messages.error(request, "You don't have permission to delete this message.")
        return redirect('listings:chat', pk=listing.id)
    
    # If it's a POST request, delete the message
    if request.method == 'POST':
        message.delete()
        messages.success(request, "Message deleted successfully.")
        
        # Redirect back to the chat
        return redirect('listings:chat', pk=listing.id)
    
    # If it's a GET request, show confirmation page
    return render(request, 'listings/delete_message_confirm.html', {
        'message': message,
        'listing': listing
    })

@login_required
def delete_chat(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    
    # Only allow the landlord or a user who has participated in the chat to delete it
    user_messages = ChatMessage.objects.filter(listing=listing, user=request.user).exists()
    if listing.landlord != request.user and not user_messages:
        messages.error(request, "You don't have permission to delete this chat.")
        return redirect('listings:listing_detail', pk=listing.id)
    
    # If it's a POST request, delete all messages in the chat
    if request.method == 'POST':
        # If user is landlord, delete all messages
        if listing.landlord == request.user:
            ChatMessage.objects.filter(listing=listing).delete()
        # If user is not landlord, only delete their messages
        else:
            ChatMessage.objects.filter(listing=listing, user=request.user).delete()
        
        messages.success(request, "Chat deleted successfully.")
        
        # Redirect based on user type
        if listing.landlord == request.user:
            return redirect('listings:landlord_messages')
        else:
            return redirect('listings:listing_detail', pk=listing.id)
    
    # If it's a GET request, show confirmation page
    return render(request, 'listings/delete_chat_confirm.html', {
        'listing': listing
    })

# Roommate Finder Views
@login_required
def roommate_list(request):
    """View to list all active roommate profiles"""
    roommate_profiles = RoommateProfile.objects.filter(is_active=True).order_by('-created_at')
    
    # Get search parameters
    city = request.GET.get('city', '')
    min_budget = request.GET.get('min_budget', '')
    max_budget = request.GET.get('max_budget', '')
    gender = request.GET.get('gender', '')
    lifestyle = request.GET.get('lifestyle', '')
    
    # Apply filters if provided
    if city:
        roommate_profiles = roommate_profiles.filter(city__icontains=city)
    if min_budget:
        roommate_profiles = roommate_profiles.filter(max_budget__gte=min_budget)
    if max_budget:
        roommate_profiles = roommate_profiles.filter(min_budget__lte=max_budget)
    if gender:
        roommate_profiles = roommate_profiles.filter(gender=gender)
    if lifestyle:
        roommate_profiles = roommate_profiles.filter(lifestyle=lifestyle)
    
    context = {
        'roommate_profiles': roommate_profiles,
        'city': city,
        'min_budget': min_budget,
        'max_budget': max_budget,
        'gender': gender,
        'lifestyle': lifestyle,
        'gender_choices': RoommateProfile.GENDER_CHOICES,
        'lifestyle_choices': RoommateProfile.LIFESTYLE_CHOICES,
    }
    return render(request, 'listings/roommate_list.html', context)

@login_required
def roommate_detail(request, pk):
    """View to show details of a specific roommate profile"""
    roommate_profile = get_object_or_404(RoommateProfile, pk=pk, is_active=True)
    context = {
        'profile': roommate_profile,
    }
    return render(request, 'listings/roommate_detail.html', context)

@login_required
def roommate_create(request):
    """View to create a new roommate profile"""
    # Check if user already has a profile
    try:
        profile = RoommateProfile.objects.get(user=request.user)
        messages.warning(request, 'You already have a roommate profile. You can update it instead.')
        return redirect('listings:roommate_update', pk=profile.pk)
    except RoommateProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = RoommateProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Your roommate profile has been created!')
            return redirect('listings:roommate_detail', pk=profile.pk)
    else:
        form = RoommateProfileForm()
    
    context = {
        'form': form,
        'is_create': True,
    }
    return render(request, 'listings/roommate_form.html', context)

@login_required
def roommate_update(request, pk):
    """View to update an existing roommate profile"""
    profile = get_object_or_404(RoommateProfile, pk=pk)
    
    # Check if user owns this profile
    if profile.user != request.user:
        messages.error(request, "You don't have permission to edit this profile.")
        return redirect('listings:roommate_list')
    
    if request.method == 'POST':
        form = RoommateProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your roommate profile has been updated!')
            return redirect('listings:roommate_detail', pk=profile.pk)
    else:
        form = RoommateProfileForm(instance=profile)
    
    context = {
        'form': form,
        'is_create': False,
        'profile': profile,
    }
    return render(request, 'listings/roommate_form.html', context)

@login_required
def roommate_delete(request, pk):
    """View to delete a roommate profile"""
    profile = get_object_or_404(RoommateProfile, pk=pk)
    
    # Check if user owns this profile
    if profile.user != request.user:
        messages.error(request, "You don't have permission to delete this profile.")
        return redirect('listings:roommate_list')
    
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Your roommate profile has been deleted.')
        return redirect('listings:roommate_list')
    
    context = {
        'profile': profile,
    }
    return render(request, 'listings/roommate_confirm_delete.html', context)

@login_required
def roommate_chat(request, pk):
    """Start a direct chat with a roommate"""
    roommate_profile = get_object_or_404(RoommateProfile, pk=pk, is_active=True)
    
    # Prevent users from messaging themselves
    if request.user == roommate_profile.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('listings:roommate_detail', pk=roommate_profile.pk)
    
    # Create a pseudo listing for direct messaging if the user doesn't have any listings
    try:
        # First check if there's an existing direct message listing for this roommate
        direct_listing = Listing.objects.filter(
            title__startswith=f"Direct message with {roommate_profile.user.username}",
            landlord=roommate_profile.user,
            is_direct_message=True
        ).first()
        
        # If no direct message listing exists, create one
        if not direct_listing:
            direct_listing = Listing.objects.create(
                title=f"Direct message with {roommate_profile.user.username}",
                description=f"Direct messaging for roommate inquiry",
                price=0,  # Set to 0 as it's not a real listing
                city="harare",  # Default city
                suburb="Roommate Finder",
                address="Roommate Finder",
                property_type="single",  # Default type
                bedrooms=1,
                bathrooms=1,
                landlord=roommate_profile.user,
                is_available=True,
                is_direct_message=True,  # Use this flag to identify direct message listings
                phone_number="000-000-0000"  # Dummy phone number
            )
        
        # Redirect to the chat for this listing with a flag indicating it's from roommate finder
        chat_url = reverse('listings:chat', kwargs={'pk': direct_listing.pk})
        return redirect(f"{chat_url}?from_roommate=1")
    except Exception as e:
        messages.error(request, f"Error starting chat: {str(e)}")
        return redirect('listings:roommate_detail', pk=roommate_profile.pk)

# SavedSearch Views
@login_required
def saved_search_list(request):
    """View to list a user's saved searches"""
    searches = SavedSearch.objects.filter(user=request.user).order_by('-created_at')
    
    # For each search, get a sample of matching listings
    for search in searches:
        search.sample_listings = search.get_matching_listings()[:3]
        search.total_matches = search.get_matching_listings().count()
    
    return render(request, 'listings/saved_searches.html', {
        'searches': searches
    })

@login_required
def saved_search_create(request):
    """View to create a new saved search"""
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.user = request.user
            saved_search.save()
            
            # Get a count of matches to show the user
            match_count = saved_search.get_matching_listings().count()
            
            messages.success(
                request, 
                f'Search alert created successfully! We found {match_count} current listings matching your criteria.'
            )
            return redirect('listings:saved_search_list')
    else:
        # Pre-fill from GET parameters if coming from search page
        initial_data = {}
        if request.GET.get('city'):
            initial_data['city'] = request.GET.get('city')
        if request.GET.get('property_type'):
            initial_data['property_type'] = request.GET.get('property_type')
        if request.GET.get('min_price'):
            initial_data['min_price'] = request.GET.get('min_price')
        if request.GET.get('max_price'):
            initial_data['max_price'] = request.GET.get('max_price')
            
        form = SavedSearchForm(initial=initial_data)
    
    return render(request, 'listings/saved_search_form.html', {
        'form': form,
        'is_create': True,
    })

@login_required
def saved_search_update(request, pk):
    """View to update an existing saved search"""
    saved_search = get_object_or_404(SavedSearch, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = SavedSearchForm(request.POST, instance=saved_search)
        if form.is_valid():
            form.save()
            messages.success(request, 'Search alert updated successfully!')
            return redirect('listings:saved_search_list')
    else:
        form = SavedSearchForm(instance=saved_search)
    
    return render(request, 'listings/saved_search_form.html', {
        'form': form,
        'saved_search': saved_search,
        'is_create': False,
    })

@login_required
def saved_search_delete(request, pk):
    """View to delete a saved search"""
    saved_search = get_object_or_404(SavedSearch, id=pk, user=request.user)
    
    if request.method == 'POST':
        saved_search.delete()
        messages.success(request, 'Search alert deleted successfully!')
        return redirect('listings:saved_search_list')
    
    return render(request, 'listings/saved_search_confirm_delete.html', {
        'saved_search': saved_search
    })

@login_required
def saved_search_results(request, pk):
    """View to show all current listings matching a saved search"""
    saved_search = get_object_or_404(SavedSearch, id=pk, user=request.user)
    matching_listings = saved_search.get_matching_listings()
    
    return render(request, 'listings/saved_search_results.html', {
        'saved_search': saved_search,
        'listings': matching_listings,
        'count': matching_listings.count()
    })

@login_required
def toggle_saved_search_active(request, pk):
    """View to toggle the is_active flag for a saved search"""
    saved_search = get_object_or_404(SavedSearch, id=pk, user=request.user)
    
    saved_search.is_active = not saved_search.is_active
    saved_search.save()
    
    status = "activated" if saved_search.is_active else "paused"
    messages.success(request, f'Search alert "{saved_search.name}" {status}!')
    
    return redirect('listings:saved_search_list')

def contact_us_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']

            email_subject = f'New Contact Form Submission: {subject}'
            email_message = (
                f"You have a new message from your website's contact form.\n\n"
                f"Name: {name}\n"
                f"Email: {from_email}\n\n"
                f"Subject: {subject}\n\n"
                f"Message:\n{message_body}\n"
            )
            
            try:
                send_mail(
                    email_subject,
                    email_message,
                    from_email, # This will be the 'from' address seen by the recipient
                    [settings.CONTACT_EMAIL_RECIPIENT], # List of recipients
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('listings:contact_us')  # Redirect to a clean form page
            except Exception as e:
                # Log the exception for debugging
                logger = logging.getLogger(__name__) # Get a logger instance
                logger.error(f"Error sending contact email: {e}", exc_info=True)
                messages.error(request, f'Sorry, there was an error sending your message. Please try again or contact us directly.')

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

   
    contact_details = {
        'email': getattr(settings, 'DEFAULT_CONTACT_EMAIL', 'support@example.com'),
        'phone1': getattr(settings, 'DEFAULT_CONTACT_PHONE1', '+263 77X XXX XXX'),
        'phone2': getattr(settings, 'DEFAULT_CONTACT_PHONE2', '+263 71X XXX XXX'),
        'address': getattr(settings, 'DEFAULT_CONTACT_ADDRESS', '123 Main Street, Harare, Zimbabwe')
    }

    return render(request, 'listings/contact_us.html', {
        'form': form,
        'contact_details': contact_details
    })
