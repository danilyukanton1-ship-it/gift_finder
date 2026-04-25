from django_rest.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from gifts.models import Product
from gifts.v1.serializers import ProductSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
