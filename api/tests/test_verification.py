"""Tests for landlord verification endpoints."""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.models import LandlordVerification


@pytest.mark.django_db
def test_landlord_can_submit_verification(api_client, landlord):
    api_client.force_authenticate(user=landlord)
    url = reverse("api:v1:verifications-list")
    file_data = SimpleUploadedFile("doc.pdf", b"test", content_type="application/pdf")
    payload = {
        "document": file_data,
        "document_type": "id",
        "notes": "Please verify",
    }

    response = api_client.post(url, payload)
    assert response.status_code == 201
    assert LandlordVerification.objects.filter(user=landlord).exists()


@pytest.mark.django_db
def test_staff_can_update_verification_status(api_client, landlord):
    staff = landlord.__class__.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="pass12345",
        user_type="landlord",
        is_staff=True,
    )
    verification = LandlordVerification.objects.create(
        user=landlord,
        document_type="id",
        document=SimpleUploadedFile("doc.pdf", b"test", content_type="application/pdf"),
        notes="Verify",
    )
    api_client.force_authenticate(user=staff)
    url = reverse("api:v1:verifications-admin-update", kwargs={"pk": verification.pk})

    response = api_client.patch(url, {"status": "approved"}, format="json")
    assert response.status_code == 200
    verification.refresh_from_db()
    assert verification.status == "approved"
    landlord.refresh_from_db()
    assert landlord.is_verified_landlord is True
