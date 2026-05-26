import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response
from fastapi.requests import Request
from pydantic import BaseModel

from newsagent.api.auth import create_token, verify_token
from newsagent.api.auth_utils import _is_bcrypt, hash_password, verify_password
from newsagent.core.config import settings
from newsagent.memory.engine import get_engine
from newsagent.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth")

COOKIE_NAME = "newsagent_token"
_login_limiter = RateLimiter(max_calls=10, window=60.0)


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    email: str
    role: str
    name: str
    token: str
    token_type: str = "Bearer"


@router.post("/login")
async def login(req: LoginRequest, response: Response) -> LoginResponse:
    if not await _login_limiter.acquire():
        raise HTTPException(status_code=429, detail="Terlalu banyak percobaan login. Coba lagi nanti.")

    engine = await get_engine()

    user = await engine.fetchrow(
        "SELECT id, email, name, role, password_hash FROM users WHERE email = $1 AND is_active = true",
        req.email,
    )

    if user and verify_password(req.password, user["password_hash"]):
        if user and not _is_bcrypt(user["password_hash"]):
            pw_hash = hash_password(req.password)
            await engine.execute("UPDATE users SET password_hash = $1 WHERE id = $2", pw_hash, user["id"])
        token = create_token(email=user["email"], role=user["role"], name=user["name"])
    elif req.email == settings.admin_email and req.password == settings.admin_password:
        token = create_token(email=req.email, role="owner", name="Admin")
    else:
        raise HTTPException(status_code=401, detail="Email atau password salah")

    max_age = settings.jwt_expiry_hours * 3600

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=max_age,
        expires=int((datetime.now(UTC) + timedelta(hours=settings.jwt_expiry_hours)).timestamp()),
        httponly=True,
        samesite="lax",
        secure=settings.secure_cookie,
        path="/",
    )

    return LoginResponse(
        email=user["email"] if user else req.email,
        role=user["role"] if user else "owner",
        name=user["name"] if user else "Admin",
        token=token,
    )


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"ok": True}


class VerifyResponse(BaseModel):
    valid: bool
    email: str = ""
    role: str = ""
    name: str = ""


@router.get("/verify")
async def verify(request: Request) -> VerifyResponse:
    token = request.cookies.get(COOKIE_NAME, "")
    auth_header = request.headers.get("Authorization", "")
    if not token and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
    payload = verify_token(token)
    if payload:
        return VerifyResponse(
            valid=True,
            email=payload.get("sub", ""),
            role=payload.get("role", "editor"),
            name=payload.get("name", ""),
        )
    return VerifyResponse(valid=False)
