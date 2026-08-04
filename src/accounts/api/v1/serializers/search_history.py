from rest_framework import serializers

from accounts.models import SearchHistory
from gifts.models import Option


class TagsQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class QuestionOptionSerializer(serializers.ModelSerializer):
    tags = TagsQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Option
        fields = ("id", "text", "order", "is_active", "tags")


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ("id", "options", "created_at")
        read_only_fields = ("created_at",)
