import os
from typing import Generator

from sqlmodel import create_engine, Session

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=settings.debug,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session