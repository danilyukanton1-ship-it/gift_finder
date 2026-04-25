from rest_framework import serializers


class AnswerSubmitSerializer(serializers.Serializer):
    selected_options = serializers.ListField(child=serializers.IntegerField())
