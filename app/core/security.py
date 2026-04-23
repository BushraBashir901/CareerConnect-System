import bcrypt
import hashlib
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# HASH PASSWORD
def hash_password(password: str) -> str:
    sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(sha256_hash.encode("utf-8"), salt).decode("utf-8")


# 🔍 VERIFY PASSWORD
def verify_password(plain_password: str, hashed_password: str) -> bool:
    sha256_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return bcrypt.checkpw(
        sha256_hash.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# 🔑 JWT
def create_jwt(user_id: int, role: str, expires_minutes: int = 60):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None