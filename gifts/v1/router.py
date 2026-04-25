from rest_framework.routers import DefaultRouter
from django.urls import path
from gifts.v1.views import QuestionViewSet, ProductViewSet

router = DefaultRouter()

router.register("questions", QuestionViewSet, basename="questions")
router.register("products", ProductViewSet, basename="products")
