from rest_framework import serializers

from gifts.models import Product


class DirectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()


class ProductSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "currency",
            "image_url",
            "additional_image_url",
            "product_url",
            "source",
            "direction",
            "rating",
            "review_count",
            "in_stock",
        )
