import time
from typing import Optional, Dict, Any
import httpx
from jose import jwt
from fastapi import Header, HTTPException, status

from app.settings import get_settings
from app.schemas.auth import CurrentUser

_JWKS_CACHE: Dict[str, Any] = {}
_JWKS_EXP: float = 0


async def _get_jwks(url: str) -> dict:
    global _JWKS_CACHE, _JWKS_EXP
    now = time.time()
    if _JWKS_CACHE and now < _JWKS_EXP:
        return _JWKS_CACHE
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(url)
        r.raise_for_status()
        _JWKS_CACHE = r.json()
        _JWKS_EXP = now + 300
        return _JWKS_CACHE


def _authz_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> CurrentUser:
    settings = get_settings()
    token = _authz_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token"
        )

    if not settings.supabase_jwks_url:
        raise HTTPException(status_code=500, detail="Server missing SUPABASE_JWKS_URL")

    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Bad token header: {e}")

    jwks = await _get_jwks(settings.supabase_jwks_url)
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Signing key not found")
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            options={"verify_aud": False},
            issuer=settings.supabase_issuer if settings.supabase_issuer else None,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing 'sub'")

    return CurrentUser(user_id=sub, email=payload.get("email"))
