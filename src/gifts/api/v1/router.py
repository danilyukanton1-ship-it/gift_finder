from rest_framework.routers import DefaultRouter

from gifts.api.v1.views import ProductViewSet, QuestionViewSet

router = DefaultRouter()

router.register("questions", QuestionViewSet, basename="questions")
router.register("products", ProductViewSet, basename="products")
