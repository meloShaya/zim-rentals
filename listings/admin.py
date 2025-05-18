from django.contrib import admin
from .models import Listing, ListingImage, Favorite, ChatMessage, RoommateProfile, SocialShare, SavedSearch

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'property_type', 'price', 'city', 'is_available', 'created_at')
    list_filter = ('property_type', 'city', 'is_available', 'is_furnished')
    search_fields = ('title', 'description', 'suburb', 'address')
    date_hierarchy = 'created_at'
    inlines = [ListingImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('landlord', 'title', 'description', 'property_type')
        }),
        ('Location', {
            'fields': ('city', 'suburb', 'address', 'latitude', 'longitude')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Features', {
            'fields': ('bedrooms', 'bathrooms', 'is_furnished', 'has_water', 'has_electricity', 'has_wifi')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
    )

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('listing__title',)
    date_hierarchy = 'created_at'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'listing__title')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'message', 'created_at', 'is_read', 'read_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username', 'listing__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(SocialShare)
class SocialShareAdmin(admin.ModelAdmin):
    list_display = ('listing', 'source', 'clicks', 'created_at', 'ip_address')
    list_filter = ('source', 'created_at')
    search_fields = ('listing__title', 'ip_address')
    date_hierarchy = 'created_at'

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'city', 'property_type', 'min_price', 'max_price', 'is_active', 'created_at', 'last_sent_at')
    list_filter = ('is_active', 'city', 'property_type', 'created_at')
    search_fields = ('name', 'user__username', 'user__email', 'suburb')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'last_sent_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Search Criteria', {
            'fields': ('city', 'suburb', 'property_type', 'min_price', 'max_price', 'bedrooms', 'bathrooms', 'is_furnished')
        }),
        ('Status', {
            'fields': ('created_at', 'last_sent_at')
        }),
    )
