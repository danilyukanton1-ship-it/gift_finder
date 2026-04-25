from http.client import responses

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status
from accounts.v1.serializers import UserSerializer
from rest_framework import viewsets, permissions

user = get_user_model()


@extend_schema(tags=["User"])
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return user.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        return Response(
            {"error": "Listing is not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
