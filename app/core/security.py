from datetime import datetime, timedelta, timezone

import hashlib
import secrets
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.core.config import settings

# ======================
# Password hashing
# ======================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ======================
# JWT configuration
# ======================

SECRET_KEY = settings.secret_key
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set")

ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    

def generate_token() -> str:
    """Token en clair (256 bits), à envoyer par email — jamais stocké tel quel.
    Réutilisé pour le reset de mot de passe et la vérification d'email."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash rapide (SHA-256) pour stocker/chercher un token en base."""
    return hashlib.sha256(token.encode()).hexdigest()