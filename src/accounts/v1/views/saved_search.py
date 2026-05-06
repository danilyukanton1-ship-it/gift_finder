from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import SavedSearch
from accounts.v1.serializers import SavedSearchSerializer
from base.pagination import CustomPagination


@extend_schema(tags=["Saved Search"])
class SavedSearchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedSearchSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)
