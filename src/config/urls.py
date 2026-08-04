from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

if settings.DEBUG:
    import debug_toolbar
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.api.v1.router import router as account_router
from accounts.api.v1.views import LogoutView
from custom_router import EnhancedAPIRouter
from gifts.api.v1.router import router as gift_router
from gifts.api.v1.views import AnswerSubmitAPIView

router = EnhancedAPIRouter()
# api router
router.register("gifts", gift_router, basename="gift")
router.register(
    "account",
    account_router,
    basename="account",
)

# api JWT authentication
jwt_urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
]

# api Social auth
social_auth_urlpatterns = [
    re_path("api/social-auth/", include("drf_social_oauth2.urls", namespace="social")),
]


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
urlpatterns = (
    [
        path("api/", include(router.urls)),
        path("api/answers", AnswerSubmitAPIView.as_view()),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
        path("gifts/", include("gifts.urls")),
        path("admin/", admin.site.urls),
        path("accounts/", include("accounts.urls")),
    ]
    + drf_spectacular_urlpatterns
    + jwt_urlpatterns
    + social_auth_urlpatterns
)

if settings.DEBUG:
    urlpatterns += debug_toolbar_urlpatterns
