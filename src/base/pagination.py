from rest_framework.pagination import PageNumberPagination
from math import ceil

from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 40

    def get_paginated_response(self, data):
        context = {
            "page_size": self.page_size,
            "pages": (
                ceil(self.page.paginator.count / self.get_page_size(self.request))
                if self.get_page_size(self.request)
                else 1
            ),
            "current_page": self.page.number,
            "results": data,
        }
        return Response(context)
