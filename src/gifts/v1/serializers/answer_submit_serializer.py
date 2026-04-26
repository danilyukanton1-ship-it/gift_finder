from rest_framework import serializers


class AnswerItemSerializer(serializers.Serializer):
    question_order = serializers.IntegerField()
    selected_options = serializers.ListField(child=serializers.IntegerField())


class AnswerSubmitSerializer(serializers.Serializer):
    answers = AnswerItemSerializer(many=True)

    def validate_answers(self, answers):
        required_order = [1, 4, 5, 6, 7, 8, 9, 10]
        received_order = [item["question_order"] for item in answers]
        missing_order = set(required_order) - set(received_order)
        if missing_order:
            raise serializers.ValidationError(
                f"You should answer for all needed questions: {missing_order}"
            )
        return answers
