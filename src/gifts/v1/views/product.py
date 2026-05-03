from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ReadOnlyModelViewSet
from base.pagination import CustomPagination
from gifts.models import Product
from gifts.v1.serializers import ProductSerializer


@extend_schema(tags=["Product"])
class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
