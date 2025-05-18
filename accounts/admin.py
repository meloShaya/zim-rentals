from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LandlordVerification
from django.utils.translation import gettext_lazy as _
from allauth.account.models import EmailAddress

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified_landlord', 'email_verified', 'is_staff')
    list_filter = ('is_staff', 'user_type', 'is_verified_landlord', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_picture')}),
        (_('User Type'), {'fields': ('user_type', 'is_verified_landlord')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def email_verified(self, obj):
        """Check if user has a verified email address."""
        return EmailAddress.objects.filter(user=obj, verified=True).exists()
    
    email_verified.boolean = True
    email_verified.short_description = 'Email verified'

@admin.register(LandlordVerification)
class LandlordVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'document_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'notes', 'admin_notes')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('User Information'), {'fields': ('user',)}),
        (_('Verification Details'), {'fields': ('document', 'document_type', 'notes')}),
        (_('Review'), {'fields': ('status', 'admin_notes')}),
        (_('Dates'), {'fields': ('created_at', 'updated_at')}),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle status changes"""
        if change and 'status' in form.changed_data:
            # If status changed to approved, update the user's verification status
            if obj.status == 'approved':
                obj.user.is_verified_landlord = True
                obj.user.save()
            # If status changed to rejected or pending, ensure user is not verified
            elif obj.status in ['rejected', 'pending'] and obj.user.is_verified_landlord:
                obj.user.is_verified_landlord = False
                obj.user.save()
        super().save_model(request, obj, form, change)
