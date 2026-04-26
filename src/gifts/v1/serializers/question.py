from rest_framework import serializers

from gifts.models import Question, Option


class TagsQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class QuestionOptionSerializer(serializers.ModelSerializer):
    tags = TagsQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Option
        fields = ("id", "text", "order", "is_active", "tags")


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "text",
            "description",
            "order",
            "priority",
            "options",
            "question_type",
            "is_active",
        )
