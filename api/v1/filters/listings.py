"""Listing filters for API v1."""

import django_filters.rest_framework as filters

from listings.models import Listing


class ListingFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    bedrooms_min = filters.NumberFilter(field_name="bedrooms", lookup_expr="gte")
    bedrooms_max = filters.NumberFilter(field_name="bedrooms", lookup_expr="lte")
    bathrooms_min = filters.NumberFilter(field_name="bathrooms", lookup_expr="gte")
    bathrooms_max = filters.NumberFilter(field_name="bathrooms", lookup_expr="lte")
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Listing
        fields = [
            "city",
            "suburb",
            "property_type",
            "currency",
            "is_furnished",
            "has_water",
            "has_electricity",
            "has_wifi",
            "is_available",
        ]

