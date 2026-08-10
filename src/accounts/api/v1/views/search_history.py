from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets

from accounts.api.v1.serializers import SearchHistorySerializer
from accounts.models import SearchHistory
from base.pagination import CustomPagination


@extend_schema(tags=["Search History"])
class SearchHistoryViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "delete")
    serializer_class = SearchHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)
