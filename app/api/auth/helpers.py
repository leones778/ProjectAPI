import base64
import hashlib
import os
from datetime import datetime, timedelta

from app.core.config import Config


def hash_password(raw_password: str) -> str:
    salt = os.urandom(Config.SALT_SIZE)
    key = hashlib.pbkdf2_hmac("sha256", raw_password.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode()


def check_password(raw_password: str, hashed_password: str) -> bool:
    decoded = base64.b64decode(hashed_password.encode())
    salt, key = decoded[: Config.SALT_SIZE], decoded[Config.SALT_SIZE :]
    new_key = hashlib.pbkdf2_hmac("sha256", raw_password.encode(), salt, 100000)
    return key == new_key


def calc_expiration_at():
    return datetime.utcnow() + timedelta(seconds=Config.USER_SESSION_EXPIRY)


def calc_refresh_at(created_at: datetime):
    return created_at + timedelta(seconds=Config.USER_SESSION_REFRESH)


def set_session_cookie(response, session):
    response.set_cookie(
        "X-Session-ID",
        session.session_id,
        httponly=True,
        samesite="Strict",
        expires=session.expiration_at,
    )
