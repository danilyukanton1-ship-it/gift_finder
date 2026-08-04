from django.contrib.auth import get_user_model
from rest_framework import serializers

user = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = [
            "username",
            "first_name",
            "last_name",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "email",
            "created_at",
            "is_active",
        ]
