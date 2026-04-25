from rest_framework.routers import DefaultRouter

from accounts.v1.views import (
    SearchHistoryViewSet,
    ChosenProductsViewSet,
    SavedSearchViewSet,
)

router = DefaultRouter()

router.register("search-history", SearchHistoryViewSet, basename="search-history")
router.register("chosen-products", ChosenProductsViewSet, basename="chosen-products")
router.register("saved-search", SavedSearchViewSet, basename="saved-search")
