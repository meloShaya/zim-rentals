"""Metadata serializers for enumerations and configuration."""

from rest_framework import serializers

from listings.models import Listing, RoommateProfile


class ChoiceFieldSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class MetadataSerializer(serializers.Serializer):
    property_types = ChoiceFieldSerializer(many=True)
    listing_cities = ChoiceFieldSerializer(many=True)
    roommate_lifestyles = ChoiceFieldSerializer(many=True)
    roommate_genders = ChoiceFieldSerializer(many=True)

    @classmethod
    def from_model_choices(cls):
        def _serialize(choices):
            return [{"value": value, "label": label} for value, label in choices]

        return cls(
            {
                "property_types": _serialize(Listing.PROPERTY_TYPES),
                "listing_cities": _serialize(Listing.CITIES),
                "roommate_lifestyles": _serialize(RoommateProfile.LIFESTYLE_CHOICES),
                "roommate_genders": _serialize(RoommateProfile.GENDER_CHOICES),
            }
        )


