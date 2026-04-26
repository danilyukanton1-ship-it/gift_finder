from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
import debug_toolbar
from gifts.v1.router import router as GiftRouter
from accounts.v1.router import router as AccountRouter
from config import settings
from custom_router import EnhancedAPIRouter
from gifts.v1.views import AnswerSubmitAPIView

router = EnhancedAPIRouter()

router.register("gifts", GiftRouter, basename="gift")
router.register(
    "account",
    AccountRouter,
    basename="account",
)


# drf-spectacular urls
drf_spectacular_urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# debug toolbar urls
debug_toolbar_urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
]

# main project urls
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/answers", AnswerSubmitAPIView.as_view()),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("gifts/", include("gifts.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
] + drf_spectacular_urlpatterns

if settings.DEBUG:
    urlpatterns += debug_toolbar_urlpatterns
