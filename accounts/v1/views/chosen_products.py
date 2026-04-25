from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions

from accounts.models import ChosenProducts
from accounts.v1.serializers import ChosenProductsSerializer


@extend_schema(tags=["Cart"])
class ChosenProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ChosenProductsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return ChosenProducts.objects.filter(user=self.request.user)
