from sqlmodel import Session, select
from app.core.database import engine
from app.core.security import hash_password
from app.models.user import User
from app.enums import UserRole
from app.core.config import settings


if __name__ == "__main__":

    if not settings.admin_email or not settings.admin_password:
        raise SystemExit(
            "ADMIN_EMAIL et ADMIN_PASSWORD doivent être définis dans .env pour lancer ce script."
        )

    with Session(engine) as session:

        # Vérifier que l'admin n'est pas déjà en db
        admin_already_exist = session.exec(
            select(User).where(
                User.email == settings.admin_email
            )
        ).first()

        if admin_already_exist:
            print("Admin déjà généré avec cet email")

        else:
            admin = User(
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                role=UserRole.ADMIN,
                is_active=True,
                email_verified=True,
            )
            session.add(admin)
            session.commit()
            print("Admin créé avec succès !")
