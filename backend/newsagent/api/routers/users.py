import logging

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException
from pydantic import BaseModel

from newsagent.api.auth import verify_api_key_or_jwt, verify_token
from newsagent.api.auth_utils import hash_password
from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users")


class CreateUserRequest(BaseModel):
    email: str
    password: str
    name: str = ""
    role: str = "editor"


class UpdateUserRequest(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    is_active: bool | None = None


async def _require_owner(
    _auth: None = Depends(verify_api_key_or_jwt),
    authorization: str = Header(""),
    newsagent_token: str | None = Cookie(None),
) -> None:
    token = authorization.removeprefix("Bearer ").strip()
    if not token and newsagent_token:
        token = newsagent_token
    if token:
        payload = verify_token(token)
        if payload and payload.get("role") == "owner":
            return
    raise HTTPException(status_code=403, detail="Hanya owner yang dapat mengakses")


@router.get("")
async def list_users(_auth: None = Depends(_require_owner)) -> list[dict]:
    engine = await get_engine()
    rows = await engine.fetch(
        "SELECT id, email, name, role, is_active, created_at FROM users ORDER BY created_at ASC"
    )
    return [dict(r) for r in rows]


@router.post("")
async def create_user(body: CreateUserRequest, _auth: None = Depends(_require_owner)) -> dict:
    if body.role != "editor":
        raise HTTPException(status_code=422, detail="Hanya role 'editor' yang dapat dibuat")

    engine = await get_engine()
    existing = await engine.fetchval("SELECT id FROM users WHERE email = $1", body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email sudah terdaftar")

    pw_hash = hash_password(body.password)
    insert_sql = (
        "INSERT INTO users (email, password_hash, name, role) VALUES ($1, $2, $3, $4) "
        "RETURNING id, email, name, role, is_active, created_at"
    )
    row = await engine.fetchrow(
        insert_sql,
        body.email,
        pw_hash,
        body.name or body.email.split("@")[0],
        body.role,
    )
    return dict(row)


@router.patch("/{user_id}")
async def update_user(user_id: str, body: UpdateUserRequest, _auth: None = Depends(_require_owner)) -> dict:
    engine = await get_engine()
    user = await engine.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates: list[str] = []
    params: list = []
    idx = 1

    if body.email is not None:
        updates.append(f"email = ${idx}")
        params.append(body.email)
        idx += 1
    if body.password is not None:
        updates.append(f"password_hash = ${idx}")
        params.append(hash_password(body.password))
        idx += 1
    if body.name is not None:
        updates.append(f"name = ${idx}")
        params.append(body.name)
        idx += 1
    if body.is_active is not None:
        updates.append(f"is_active = ${idx}")
        params.append(body.is_active)
        idx += 1

    if not updates:
        raise HTTPException(status_code=422, detail="No fields to update")

    params.append(user_id)
    set_clause = ", ".join(updates)
    update_sql = (
        f"UPDATE users SET {set_clause}, updated_at = NOW() WHERE id = ${idx} "
        "RETURNING id, email, name, role, is_active, created_at"
    )
    row = await engine.fetchrow(
        update_sql,
        *params,
    )
    return dict(row) if row else {}


@router.delete("/{user_id}")
async def delete_user(user_id: str, _auth: None = Depends(_require_owner)) -> dict:
    engine = await get_engine()
    user = await engine.fetchrow("SELECT role FROM users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user["role"] == "owner":
        raise HTTPException(status_code=422, detail="Cannot delete owner account")

    await engine.execute("DELETE FROM users WHERE id = $1", user_id)
    return {"ok": True}
