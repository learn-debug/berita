import hashlib
import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _is_bcrypt(hashed: str) -> bool:
    return hashed.startswith("$2b$") or hashed.startswith("$2a$") or hashed.startswith("$2y$")


def _verify_sha256(password: str, hashed: str) -> bool:
    try:
        salt, h = hashed.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    except (ValueError, AttributeError):
        return False


def verify_password(password: str, hashed: str) -> bool:
    if _is_bcrypt(hashed):
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except (ValueError, AttributeError):
            return False
    return _verify_sha256(password, hashed)
