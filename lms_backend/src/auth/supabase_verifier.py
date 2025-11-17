import time
from typing import Any, Dict, Optional
import httpx
from jose import jwt, JWTError

from src.core.config import settings


class JWKSCache:
    """Simple in-memory JWKS cache with TTL."""

    def __init__(self, ttl_seconds: int = 600):
        self.ttl = ttl_seconds
        self._cached: Optional[Dict[str, Any]] = None
        self._expires_at: float = 0.0

    async def get_jwks(self) -> Dict[str, Any]:
        now = time.time()
        if self._cached and now < self._expires_at:
            return self._cached
        url = settings.SUPABASE_JWKS_URL or f"{settings.SUPABASE_URL}/auth/v1/jwks"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            self._cached = data
            self._expires_at = now + self.ttl
            return data


_jwks_cache = JWKSCache()


# PUBLIC_INTERFACE
async def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """Verify a Supabase JWT using JWKS and validate standard claims.

    Behavior:
    - Fetches and caches JWKS for 10 minutes
    - Verifies signature using token header 'kid'
    - Validates 'iss' starts with configured SUPABASE_URL
    - Accepts audiences: 'authenticated' or 'supabase'
    - Allows small clock skew for iat/exp implicitly via jose defaults
    """
    try:
        jwks = await _jwks_cache.get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        keys = jwks.get("keys", [])
        public_key = None
        for key in keys:
            if key.get("kid") == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        if public_key is None:
            raise JWTError("No matching JWK for kid")

        # Decode and validate standard claims except audience (checked manually)
        payload = jwt.decode(
            token,
            public_key,
            options={"verify_aud": False},
            algorithms=None,
        )

        # Issuer should match the Supabase project URL
        iss = payload.get("iss")
        expected_iss_prefix = (settings.SUPABASE_URL or "").rstrip("/")
        if not iss or not iss.startswith(expected_iss_prefix):
            raise JWTError("Invalid issuer")

        # Audience: accept 'authenticated' or 'supabase'
        aud = payload.get("aud")
        if isinstance(aud, str):
            aud_ok = aud in ("authenticated", "supabase")
        elif isinstance(aud, list):
            aud_ok = any(a in ("authenticated", "supabase") for a in aud)
        else:
            aud_ok = False
        if not aud_ok:
            raise JWTError("Invalid audience")

        return payload
    except Exception as e:
        if isinstance(e, JWTError):
            raise
        raise JWTError(str(e))
