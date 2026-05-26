import logging
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Cookie, Header, HTTPException
from fastapi.websockets import WebSocket

from newsagent.core.config import settings

logger = logging.getLogger(__name__)

COOKIE_NAME = "newsagent_token"


def _secret() -> str:
    return settings.jwt_secret


def _algorithm() -> str:
    return settings.jwt_algorithm


def create_token(email: str = "admin", role: str = "editor", name: str = "") -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": email,
        "role": role,
        "name": name,
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_expiry_hours),
        "iss": "newsagent",
        "aud": "newsagent-api",
    }
    return jwt.encode(payload, _secret(), algorithm=_algorithm())


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            _secret(),
            algorithms=[_algorithm()],
            issuer="newsagent",
            audience="newsagent-api",
        )
    except jwt.ExpiredSignatureError:
        logger.warning("[auth] token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("[auth] invalid token: %s", e)
        return None


async def verify_api_key_or_jwt(
    authorization: str = Header(""),
    newsagent_token: str | None = Cookie(None),
) -> None:
    token = authorization.removeprefix("Bearer ").strip()
    if settings.api_key and secrets.compare_digest(token, settings.api_key):
        return
    if token and verify_token(token):
        return
    if newsagent_token and verify_token(newsagent_token):
        return
    raise HTTPException(status_code=401, detail="Unauthorized")


async def verify_ws_token(websocket: WebSocket) -> bool:
    token = websocket.query_params.get("token", "")
    if not token:
        return False
    if settings.api_key and secrets.compare_digest(token, settings.api_key):
        return True
    return verify_token(token) is not None
