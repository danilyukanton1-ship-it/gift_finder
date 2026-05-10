import time

from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):

        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        jti = token["jti"]
        exp = token["exp"]

        timeout = exp - int(time.time())
        cache.set(
            f"blacklist_{jti}",
            "blacklisted",
            timeout=timeout,
        )

        return Response({"message": "token blacklisted"})
