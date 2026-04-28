from rest_framework import serializers
from gifts.models import Product
from accounts.models import Cart


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


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ("id", "product", "selected_at", "quantity", "is_purchased", "note")
