from fastapi import HTTPException, status
from sqlmodel import select

from app.models.user import User
from app.core.security import verify_password


def invalid_credentials():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def authenticate_user(session, email, password):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user