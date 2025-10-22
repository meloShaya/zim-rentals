"""Landlord verification serializers."""

from rest_framework import serializers

from accounts.models import LandlordVerification


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandlordVerification
        fields = [
            "id",
            "document",
            "document_type",
            "notes",
            "status",
            "admin_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "admin_notes", "created_at", "updated_at"]


class VerificationAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandlordVerification
        fields = ["status", "admin_notes"]

