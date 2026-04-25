from rest_framework import serializers
from accounts.models import SavedSearch
from gifts.models import Option


class OptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ("id", "text", "order", "is_active", "tags")


class SavedSearchSerializer(serializers.ModelSerializer):
    options = OptionsSerializer(many=True, read_only=True)

    class Meta:
        model = SavedSearch
        fields = ("name", "description", "options")
        read_only_fields = ("id", "created_at")
