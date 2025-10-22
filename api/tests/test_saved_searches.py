"""Tests for saved search endpoints."""

import pytest
from django.urls import reverse

from listings.models import SavedSearch


@pytest.mark.django_db
def test_create_saved_search(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("api:v1:saved-searches-list")
    payload = {
        "name": "Harare Houses",
        "city": "harare",
        "property_type": "house",
        "min_price": "300.00",
        "max_price": "800.00",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert SavedSearch.objects.filter(user=user, name="Harare Houses").exists()


@pytest.mark.django_db
def test_toggle_saved_search(api_client, user):
    saved_search = SavedSearch.objects.create(user=user, name="Search", city="harare")
    api_client.force_authenticate(user=user)
    url = reverse("api:v1:saved-searches-toggle", kwargs={"pk": saved_search.pk})

    response = api_client.post(url, format="json")
    assert response.status_code == 200
    saved_search.refresh_from_db()
    assert saved_search.is_active is False
