from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from gifts.models import Question
from gifts.v1.serializers import QuestionSerializer


@extend_schema(tags=["Question"])
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.filter(is_active=True).order_by("order")
    serializer_class = QuestionSerializer
    pagination_class = ()
