from rest_framework.routers import DefaultRouter

from accounts.v1.views import (
    SearchHistoryViewSet,
    CartViewSet,
    SavedSearchViewSet,
    UserViewSet,
)

router = DefaultRouter()

router.register("search-history", SearchHistoryViewSet, basename="search-history")
router.register("cart", CartViewSet, basename="cart")
router.register("saved-search", SavedSearchViewSet, basename="saved-search")
router.register("user", UserViewSet, basename="user")
