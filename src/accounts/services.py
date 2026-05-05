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

        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return False

            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            ttl = (exp_datetime - datetime.now()).total_seconds()

            if ttl > 0:

                self._cache.set(f"blacklist_{jti}", 'blacklisted', timeout=int(ttl))
                return True
            else:
                return False
        except jwt.PyJWTError:
            return False

    def is_token_blacklisted(self, access_token):
        jti = self._get_jti_from_token(access_token)
        if not jti:
            return False
        return self._cache.get(f"blacklist_{jti}") is not None

@lru_cache
def get_blacklist_service():
    return JWTBlacklistService()