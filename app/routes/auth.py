from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select


from app.core.database import get_session
from app.deps.auth import get_current_user, require_admin
from app.models.user import User

from app.schemas.auth import UserRead
from app.core.security import verify_password, create_access_token
from app.utils.auth import invalid_credentials, authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):

    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        invalid_credentials()

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user