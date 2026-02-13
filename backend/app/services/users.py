from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import UserORM


def get_user_by_email(db: Session, email: str) -> UserORM | None:
    return db.query(UserORM).filter(UserORM.email == email).first()


def create_user(db: Session, email: str, password: str) -> UserORM:
    user = UserORM(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> UserORM | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
