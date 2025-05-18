from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties.models import Property, ShareTracking

@login_required
def sharing_analytics(request):
    """View for property owners to see sharing statistics for their properties."""
    user_properties = Property.objects.filter(owner=request.user)
    
    # Collect sharing statistics for all user properties
    properties_with_stats = []
    for property in user_properties:
        stats = {
            'property': property,
            'total_shares': property.share_count,
            'whatsapp_shares': ShareTracking.objects.filter(property=property, platform='whatsapp').count(),
            'facebook_shares': ShareTracking.objects.filter(property=property, platform='facebook').count(),
            'twitter_shares': ShareTracking.objects.filter(property=property, platform='twitter').count(),
            'email_shares': ShareTracking.objects.filter(property=property, platform='email').count(),
        }
        properties_with_stats.append(stats)
    
    context = {
        'properties_with_stats': properties_with_stats,
        'total_properties': user_properties.count(),
        'total_shares': sum(prop['total_shares'] for prop in properties_with_stats),
    }
    
    return render(request, 'properties/sharing_analytics.html', context) 