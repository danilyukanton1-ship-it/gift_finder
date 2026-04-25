from rest_framework import serializers

from gifts.models import Question, Option


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ("id", "text", "order", "is_active")


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "description", "order", "options")
