from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('landlord', 'Landlord'),
        ('renter', 'Renter'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='renter')
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified_landlord = models.BooleanField(default=False, help_text=_("Indicates if the landlord has been verified"))
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class LandlordVerification(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verifications')
    document = models.FileField(upload_to='verification_documents/', help_text=_("Upload ID or proof of property ownership"))
    document_type = models.CharField(max_length=50, choices=(
        ('id', 'Identification Document'),
        ('deed', 'Title Deed'),
        ('other', 'Other Proof of Ownership'),
    ))
    notes = models.TextField(blank=True, help_text=_("Additional information about your verification request"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text=_("Admin notes on verification review"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Verification for {self.user.username} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # If verification is approved, update the user's verification status
        if self.status == 'approved':
            self.user.is_verified_landlord = True
            self.user.save()
        super().save(*args, **kwargs)
