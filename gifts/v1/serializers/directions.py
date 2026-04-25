from rest_framework import serializers
from gifts.models import Direction


class DirectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Direction
        fields = ("id", "name", "description", "order", "image_url")
