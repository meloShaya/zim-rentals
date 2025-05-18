from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()

class Listing(models.Model):
    PROPERTY_TYPES = (
        ('single', 'Single Room'),
        ('shared', 'Shared Room'),
        ('cottage', 'Cottage'),
        ('apartment', 'Apartment'),
        ('house', 'House'),
    )
    
    CURRENCY_CHOICES = (
        ('USD', 'USD'),
        ('ZWL', 'ZWL'),
    )
    
    CITIES = (
        ('harare', 'Harare'),
        ('bulawayo', 'Bulawayo'),
        ('mutare', 'Mutare'),
        ('gweru', 'Gweru'),
        ('masvingo', 'Masvingo'),
        ('chitungwiza', 'Chitungwiza'),
    )
    
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    city = models.CharField(max_length=20, choices=CITIES)
    suburb = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    is_furnished = models.BooleanField(default=False)
    has_water = models.BooleanField(default=True)
    has_electricity = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=20, help_text="Contact phone number")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp number (optional)")
    featured_image = models.ImageField(upload_to='listings/', null=True, blank=True)
    is_direct_message = models.BooleanField(default=False, help_text="Flag for listings created for direct messaging only")
    
    @property
    def location(self):
        return f"{self.suburb}, {self.get_city_display()}"
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    def get_images(self):
        return self.images.all()[:4]  # Return up to 4 images
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Listing Image')
        verbose_name_plural = _('Listing Images')

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'listing')
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')

class ChatMessage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')

    def __str__(self):
        return f'{self.user.username} - {self.message[:50]}'

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

class RoommateProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    )
    
    LIFESTYLE_CHOICES = (
        ('early_bird', 'Early Bird'),
        ('night_owl', 'Night Owl'),
        ('social', 'Social/Outgoing'),
        ('quiet', 'Quiet/Private'),
        ('studious', 'Studious'),
        ('neat', 'Neat and Tidy'),
        ('relaxed', 'Relaxed about cleaning'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='roommate_profile')
    title = models.CharField(max_length=100, help_text="Brief title for your roommate search")
    age = models.PositiveIntegerField(help_text="Your age")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    city = models.CharField(max_length=50)
    suburb = models.CharField(max_length=50, blank=True)
    min_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Your minimum budget")
    max_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Your maximum budget")
    move_in_date = models.DateField(help_text="When are you looking to move in?")
    lifestyle = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES, blank=True)
    bio = models.TextField(help_text="Tell potential roommates about yourself")
    preferences = models.TextField(help_text="Describe what you're looking for in a roommate or housing", blank=True)
    is_smoker = models.BooleanField(default=False)
    has_pets = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Roommate Profile"

class SocialShare(models.Model):
    SOURCE_CHOICES = (
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('email', 'Email'),
        ('other', 'Other'),
    )
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='social_shares')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=1)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('Social Share')
        verbose_name_plural = _('Social Shares')
        unique_together = ('listing', 'source', 'ip_address')
    
    def __str__(self):
        return f"{self.get_source_display()} share for {self.listing.title}"
    
    @classmethod
    def record_share_visit(cls, listing, source, ip_address=None):
        """
        Record a visit from a social share, incrementing counter if same IP has visited before
        """
        share, created = cls.objects.get_or_create(
            listing=listing,
            source=source,
            ip_address=ip_address,
            defaults={'clicks': 1}
        )
        
        if not created:
            share.clicks += 1
            share.save()
        
        return share

class SavedSearch(models.Model):
    """Model for users to save search criteria and receive alerts for new matching listings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100, help_text="Name this search for your reference")
    city = models.CharField(max_length=20, choices=Listing.CITIES, blank=True, null=True)
    suburb = models.CharField(max_length=100, blank=True, null=True)
    property_type = models.CharField(max_length=20, choices=Listing.PROPERTY_TYPES, blank=True, null=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bedrooms = models.PositiveIntegerField(blank=True, null=True)
    bathrooms = models.PositiveIntegerField(blank=True, null=True)
    is_furnished = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent_at = models.DateTimeField(blank=True, null=True, help_text="When the last alert was sent")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Saved Search')
        verbose_name_plural = _('Saved Searches')
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"
    
    def get_matching_listings(self, since_datetime=None):
        """
        Get all listings that match this saved search's criteria
        If since_datetime is provided, only return listings created after that time
        """
        filters = {}
        
        # Only include active, non-direct-message listings
        filters['is_available'] = True
        filters['is_direct_message'] = False
        
        # Add all non-null criteria to the filters
        if self.city:
            filters['city'] = self.city
            
        if self.suburb:
            filters['suburb__icontains'] = self.suburb
            
        if self.property_type:
            filters['property_type'] = self.property_type
            
        if self.max_price:
            filters['price__lte'] = self.max_price
            
        if self.min_price:
            filters['price__gte'] = self.min_price
            
        if self.bedrooms is not None:
            filters['bedrooms__gte'] = self.bedrooms
            
        if self.bathrooms is not None:
            filters['bathrooms__gte'] = self.bathrooms
            
        if self.is_furnished is not None:
            filters['is_furnished'] = self.is_furnished
            
        # Only get listings created after the specified time
        if since_datetime:
            filters['created_at__gt'] = since_datetime
            
        return Listing.objects.filter(**filters).order_by('-created_at')
