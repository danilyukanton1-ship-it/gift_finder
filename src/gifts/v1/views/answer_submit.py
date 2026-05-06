from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from gifts.services import GiftSearchService, serialize_products_by_direction
from gifts.v1.serializers import AnswerSubmitSerializer
from rest_framework import status


@extend_schema(tags=["Answer of a user"])
class AnswerSubmitAPIView(APIView):
    @extend_schema(responses={200: AnswerSubmitSerializer})
    def post(self, request, *args, **kwargs):
        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        option_ids = []
        for answer in serializer.validated_data["answers"]:
            option_ids.extend(answer["selected_options"])

        engine = GiftSearchService(option_ids)
        if not engine.has_required_answer():
            return Response(
                {"error": "You must answer all required questions"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = engine.get_result()

        serialized = serialize_products_by_direction(result)

        return Response(serialized)
