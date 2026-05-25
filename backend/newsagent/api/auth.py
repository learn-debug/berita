import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Cookie, Header, HTTPException
from fastapi.websockets import WebSocket

from newsagent.core.config import settings

logger = logging.getLogger(__name__)


def _secret() -> str:
    return settings.jwt_secret


def _algorithm() -> str:
    return settings.jwt_algorithm


def create_token() -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "admin",
        "iat": now,
        "exp": now + timedelta(hours=settings.jwt_expiry_hours),
    }
    return jwt.encode(payload, _secret(), algorithm=_algorithm())


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=[_algorithm()])
    except jwt.ExpiredSignatureError:
        logger.warning("[auth] token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("[auth] invalid token: %s", e)
        return None


async def verify_api_key_or_jwt(
    authorization: str = Header(""),
    x_token: str | None = Cookie(None),
) -> None:
    if not settings.api_key and not settings.admin_password:
        return

    token = authorization.removeprefix("Bearer ").strip()
    if token == settings.api_key:
        return
    if token and verify_token(token):
        return

    if x_token and verify_token(x_token):
        return

    raise HTTPException(status_code=401, detail="Unauthorized")


async def verify_ws_token(websocket: WebSocket) -> bool:
    token = websocket.query_params.get("token", "")
    if not token:
        return False
    if token == settings.api_key:
        return True
    return verify_token(token) is not None
