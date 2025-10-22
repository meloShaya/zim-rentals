"""Metadata endpoints for mobile clients."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from api.v1.serializers.metadata import MetadataSerializer


class MetadataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = MetadataSerializer.from_model_choices()
        return Response(serializer.data)


