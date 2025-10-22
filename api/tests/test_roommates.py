"""Tests for roommate API endpoints."""

import pytest
from django.urls import reverse

from listings.models import RoommateProfile


@pytest.mark.django_db
def test_user_can_create_roommate_profile(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("api:v1:roommates-list")
    payload = {
        "title": "Looking for roommate",
        "age": 25,
        "gender": "M",
        "city": "Harare",
        "suburb": "Avondale",
        "min_budget": "300.00",
        "max_budget": "600.00",
        "move_in_date": "2025-06-01",
        "lifestyle": "quiet",
        "bio": "Easy going",
        "preferences": "Non-smoker",
        "is_smoker": False,
        "has_pets": False,
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert RoommateProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_roommate_connections(api_client, user, landlord):
    profile = RoommateProfile.objects.create(
        user=landlord,
        title="Spare room",
        age=30,
        gender="M",
        city="Harare",
        suburb="Borrowdale",
        min_budget="400.00",
        max_budget="800.00",
        move_in_date="2025-06-01",
        lifestyle="social",
        bio="Friendly",
    )
    api_client.force_authenticate(user=user)
    url = reverse("api:v1:roommate-connections-list", kwargs={"roommate_pk": profile.pk})
    payload = {"message": "Interested"}

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    connection_id = response.data["id"]

    # Landlord accepts
    api_client.force_authenticate(user=landlord)
    url_detail = reverse(
        "api:v1:roommate-connections-detail",
        kwargs={"roommate_pk": profile.pk, "pk": connection_id},
    )
    response = api_client.patch(url_detail, {"status": "accepted"}, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "accepted"
