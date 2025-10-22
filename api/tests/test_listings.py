"""Tests for listing endpoints."""

import pytest
from django.urls import reverse

from listings.models import Listing


@pytest.mark.django_db
def test_landlord_can_create_listing(api_client, landlord):
    api_client.force_authenticate(user=landlord)
    url = reverse("api:v1:listings-list")
    payload = {
        "title": "Test Listing",
        "description": "Nice place",
        "price": "500.00",
        "currency": "USD",
        "city": "harare",
        "suburb": "Avondale",
        "address": "123 Street",
        "property_type": "house",
        "bedrooms": 3,
        "bathrooms": 2,
        "is_furnished": True,
        "has_water": True,
        "has_electricity": True,
        "has_wifi": False,
        "phone_number": "+263771111111",
        "whatsapp_number": "+263771111111",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert Listing.objects.filter(title="Test Listing", landlord=landlord).exists()


@pytest.mark.django_db
def test_renter_cannot_create_listing(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("api:v1:listings-list")
    payload = {
        "title": "Test Listing",
        "description": "Nice place",
        "price": "500.00",
        "currency": "USD",
        "city": "harare",
        "suburb": "Avondale",
        "address": "123 Street",
        "property_type": "house",
        "bedrooms": 3,
        "bathrooms": 2,
        "is_furnished": True,
        "has_water": True,
        "has_electricity": True,
        "has_wifi": False,
        "phone_number": "+263771111111",
        "whatsapp_number": "+263771111111",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 403
