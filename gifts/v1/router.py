from rest_framework.routers import DefaultRouter

from gifts.v1.views.question import QuestionViewSet

router = DefaultRouter()

router.register("questions", QuestionViewSet)
