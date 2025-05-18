from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm, LandlordVerificationForm
from listings.models import Favorite
from .models import LandlordVerification

# Create your views here.

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('listing')
    context = {'favorites': favorites}
    return render(request, 'accounts/favorites.html', context)

@login_required
def landlord_verification(request):
    # Redirect if user is not a landlord
    if request.user.user_type != 'landlord':
        messages.error(request, 'Only landlord accounts can apply for verification.')
        return redirect('accounts:profile')
    
    # Check if user already has a pending or approved verification
    existing_verifications = LandlordVerification.objects.filter(
        user=request.user,
        status__in=['pending', 'approved']
    ).first()
    
    if existing_verifications and existing_verifications.status == 'approved':
        messages.info(request, 'Your account is already verified!')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = LandlordVerificationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            verification = form.save()
            messages.success(request, 'Your verification request has been submitted. We will review it within 2-3 business days.')
            return redirect('accounts:profile')
    else:
        # If there's a pending request, show it
        if existing_verifications:
            messages.info(request, 'You already have a pending verification request. You can update it below.')
            form = LandlordVerificationForm(instance=existing_verifications, user=request.user)
        else:
            form = LandlordVerificationForm(user=request.user)
    
    context = {
        'form': form,
        'existing_verification': existing_verifications
    }
    return render(request, 'accounts/landlord_verification.html', context)