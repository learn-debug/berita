import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from newsagent.api.auth import create_token, verify_token
from newsagent.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth")


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"


@router.post("/login")
async def login(req: LoginRequest) -> LoginResponse:
    if not settings.admin_password:
        raise HTTPException(status_code=503, detail="Auth not configured")
    if req.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    return LoginResponse(token=create_token())


class VerifyResponse(BaseModel):
    valid: bool


@router.get("/verify")
async def verify(token: str = "") -> VerifyResponse:
    return VerifyResponse(valid=verify_token(token) is not None)
