from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets

from accounts.api.v1.serializers import CartSerializer
from accounts.models import Cart
from base.pagination import CustomPagination


@extend_schema(tags=["Cart"])
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
