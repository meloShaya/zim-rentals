"""Shared pytest fixtures for API tests."""

import pytest
from rest_framework.test import APIClient

from accounts.models import CustomUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="pass12345",
        user_type="renter",
    )


@pytest.fixture
def landlord(db):
    return CustomUser.objects.create_user(
        username="landlord",
        email="landlord@example.com",
        password="pass12345",
        user_type="landlord",
    )

