from fastapi import APIRouter, Depends, Query
from sqlmodel import select, Session

from app.core.database import get_session
from app.models.product import Product
from app.schemas.product import PublicClothingRead
from app.utils.product import visible_product_statement

router = APIRouter(prefix="/clothes", tags=["Public Clothes"])


# Liste de tous les vêtements
@router.get("", response_model=list[PublicClothingRead])
def list_public_clothes(
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    statement = (
        visible_product_statement()
        .order_by(Clothing.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    clothes = session.exec(statement).all()
    return clothes