from functools import lru_cache

import jwt
from django.conf import settings
from django.core.cache import cache
from datetime import datetime


class JWTBlacklistService:

    def __init__(self, cache_client=None):
        self._cache = cache_client or cache

    def _get_jti_from_token(self, token):
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("jti")
        except jwt.PyJWTError:
            return None

    def add_token_to_blacklist(self, access_token):
        jti = self._get_jti_from_token(access_token)
        if not jti:
            return False

        exp = self._get_jti_from_token(access_token)
        if exp:
            ttl = exp - datetime.now().timestamp()
        else:
            ttl = 300

        if ttl > 0:
            self._cache.set(f"blacklist_{jti}", "blacklisted", timeout=int(ttl))
            return True
        return False

    def is_token_blacklisted(self, access_token):
        jti = self._get_jti_from_token(access_token)
        if not jti:
            return False
        return self._cache.get(f"blacklist_{jti}") is not None


@lru_cache
def get_blacklist_service():
    return JWTBlacklistService()
