from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from gifts.services import (
    get_tags_from_options,
    find_products_and_group_by_direction,
    serialize_products_by_direction,
)
from gifts.v1.serializers import AnswerSubmitSerializer


@extend_schema(tags=["Answer of a user"])
class AnswerSubmitAPIView(APIView):
    @extend_schema(responses={200: AnswerSubmitSerializer})
    def post(self, request, *args, **kwargs):
        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        option_ids = serializer.validated_data["selected_options"]

        tags_by_question = get_tags_from_options(option_ids)
        products_by_direction = find_products_and_group_by_direction(tags_by_question)
        result = serialize_products_by_direction(products_by_direction)
        return Response(result)
