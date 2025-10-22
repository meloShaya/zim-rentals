"""Root URLs for API application."""

from django.urls import include, path

from api.v1.routers import get_urlpatterns as get_v1_urlpatterns


app_name = "api"

urlpatterns = [
    path("v1/", include((get_v1_urlpatterns(), "v1"), namespace="v1")),
]

