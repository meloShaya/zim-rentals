"""Tests for authentication endpoints."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_creates_user(api_client):
    url = reverse("api:v1:auth-users-list")
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "pass12345",
        "password_confirm": "pass12345",
        "user_type": "renter",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert response.data["username"] == "newuser"


@pytest.mark.django_db
def test_login_returns_tokens(api_client, user):
    url = reverse("api:v1:auth-sessions-login")
    payload = {"login": user.username, "password": "pass12345"}

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
