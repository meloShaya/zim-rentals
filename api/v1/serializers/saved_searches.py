"""Saved search serializers."""

from rest_framework import serializers

from listings.models import SavedSearch


class SavedSearchCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        exclude = ["user", "created_at", "last_sent_at"]

