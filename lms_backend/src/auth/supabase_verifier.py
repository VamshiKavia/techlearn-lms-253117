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


async def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """Verify a Supabase JWT using JWKS and validate standard claims."""
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

        payload = jwt.decode(
            token,
            public_key,
            options={"verify_aud": False},  # we check aud manually
            algorithms=None,  # derive from token header
        )

        # Validate issuer
        iss = payload.get("iss")
        expected_iss_prefix = settings.SUPABASE_URL.rstrip("/")
        if not iss or not iss.startswith(expected_iss_prefix):
            raise JWTError("Invalid issuer")

        # Validate audience contains 'authenticated' or the project ref
        aud = payload.get("aud")
        if isinstance(aud, str):
            aud_ok = aud == "authenticated" or aud == "supabase"
        elif isinstance(aud, list):
            aud_ok = "authenticated" in aud or "supabase" in aud
        else:
            aud_ok = False
        if not aud_ok:
            raise JWTError("Invalid audience")

        # exp and iat validated by jose decode by default; if not, validate manually
        # Return payload
        return payload
    except Exception as e:
        # Normalize to JWTError
        if isinstance(e, JWTError):
            raise
        raise JWTError(str(e))
