from rest_framework.viewsets import ModelViewSet

from gifts.models import Question
from gifts.v1.serializers import QuestionSerializer


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.filter(is_active=True).order_by("order")
    serializer_class = QuestionSerializer
