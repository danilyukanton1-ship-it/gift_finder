import json
import logging
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class JWTBlacklistMiddleware(MiddlewareMixin):
    """middleware to check if refresh token is blacklisted"""

    def process_request(self, request):

        if request.path == "/api/token/refresh/" and request.method == "POST":
            try:
                body = json.loads(request.body)
                refresh = body.get("refresh")

                if refresh:
                    token = RefreshToken(refresh)
                    jti = token["jti"]

                    if cache.get(f"blacklist:{jti}"):
                        return JsonResponse(
                            {
                                "error": "Refresh token is blacklisted, please log in again"
                            },
                            status=401,
                        )
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            except (TokenError, InvalidToken):
                return JsonResponse({"error": "Invalid token"}, status=401)
            except ConnectionError:
                return JsonResponse({"error": "Connection error"})
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        return None
