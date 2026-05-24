import logging

from fastapi import Header, HTTPException

from newsagent.core.config import settings

logger = logging.getLogger(__name__)


async def verify_api_key(authorization: str = Header("")) -> None:
    if not settings.api_key:
        return
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
