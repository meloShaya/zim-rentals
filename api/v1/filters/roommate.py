"""Roommate profile filters."""

import django_filters.rest_framework as filters

from listings.models import RoommateProfile


class RoommateProfileFilter(filters.FilterSet):
    min_budget = filters.NumberFilter(field_name="max_budget", lookup_expr="gte")
    max_budget = filters.NumberFilter(field_name="min_budget", lookup_expr="lte")
    city = filters.CharFilter(lookup_expr="icontains")
    lifestyle = filters.CharFilter(lookup_expr="exact")
    gender = filters.CharFilter(lookup_expr="exact")
    move_in_before = filters.DateFilter(field_name="move_in_date", lookup_expr="lte")
    move_in_after = filters.DateFilter(field_name="move_in_date", lookup_expr="gte")

    class Meta:
        model = RoommateProfile
        fields = [
            "city",
            "suburb",
            "gender",
            "lifestyle",
            "is_smoker",
            "has_pets",
        ]

