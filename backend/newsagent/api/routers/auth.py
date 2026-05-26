import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response
from fastapi.requests import Request
from pydantic import BaseModel

from newsagent.api.auth import create_token, verify_token
from newsagent.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth")

COOKIE_NAME = "newsagent_token"


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"


@router.post("/login")
async def login(req: LoginRequest, response: Response) -> LoginResponse:
    if not settings.admin_password:
        raise HTTPException(status_code=503, detail="Auth not configured")
    if req.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_token()
    max_age = settings.jwt_expiry_hours * 3600

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=max_age,
        expires=int((datetime.now(UTC) + timedelta(hours=settings.jwt_expiry_hours)).timestamp()),
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )

    return LoginResponse(token=token)


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"ok": True}


class VerifyResponse(BaseModel):
    valid: bool


@router.get("/verify")
async def verify(request: Request) -> VerifyResponse:
    token = request.cookies.get(COOKIE_NAME, "")
    auth_header = request.headers.get("Authorization", "")
    if not token and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
    return VerifyResponse(valid=verify_token(token) is not None)
