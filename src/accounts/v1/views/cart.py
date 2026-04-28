from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions

from accounts.models import Cart
from accounts.v1.serializers import CartSerializer


@extend_schema(tags=["Cart"])
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
