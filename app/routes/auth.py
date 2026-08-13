""" Routes relatives à la gestion utilisateur """

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.core.security import verify_password, create_access_token, hash_password, generate_reset_token, hash_reset_token
from app.deps.auth import get_current_user, require_admin
from app.enums import UserRole
from app.models.user import User

from app.schemas.auth import (
    UserCreate,
    UserRead,
    PasswordResetConfirm,
    PasswordResetRequest,
    )

from app.utils.auth import invalid_credentials, authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])

RESET_TOKEN_TTL_MINUTES = 30


@router.post("/register",status_code=201, response_model=UserRead)
def register(
    payload: UserCreate,
    session: Session = Depends(get_session),
):

    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )
    session.add(new_user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    session.refresh(new_user)
    return new_user


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


@router.post("/password-reset/request")
def request_password_reset(
    payload: PasswordResetRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()

    response = {
        "detail": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."
    }

    if not user:
        return response  # même réponse : on ne révèle jamais si l'email existe
    
    raw_token = generate_reset_token()
    user.reset_token_hash = hash_reset_token(raw_token)
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)

    session.add(user)
    session.commit()

    # TODO Phase 2 : envoyer raw_token par email au lieu de le retourner.
    if settings.debug:
        response["debug_token"] = raw_token

    return response

@router.post("/password-reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirm,
    session: Session = Depends(get_session),
):
    token_hash = hash_reset_token(payload.token)

    user = session.exec(
        select(User).where(User.reset_token_hash == token_hash)
    ).first()

    if (
        not user
        or not user.reset_token_expires_at
        or user.reset_token_expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    user.password_hash = hash_password(payload.new_password)
    user.reset_token_hash = None
    user.reset_token_expires_at = None

    session.add(user)
    session.commit()

    return {"detail": "Mot de passe mis à jour avec succès."}