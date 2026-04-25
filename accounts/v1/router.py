from rest_framework.routers import DefaultRouter

from accounts.v1.views.search_history import SearchHistoryViewSet

router = DefaultRouter()

router.register("search-history", SearchHistoryViewSet, basename="search-history")
