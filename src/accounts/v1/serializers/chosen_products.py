from rest_framework import serializers
from gifts.models import Product
from accounts.models import ChosenProducts


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        read_only_fields = (
            "id",
            "name",
            "price",
            "currency",
            "image_url",
            "additional_image_url",
            "product_url",
            "source",
            "in_stock",
        )


class ChosenProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChosenProducts
        fields = ("id", "product", "selected_at", "quantity", "is_purchased", "note")
