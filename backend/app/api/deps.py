from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.db.session import get_db
from app.models.user import UserORM
from app.services.stores import get_store_by_id, get_store_owned
from app.services.rate_limit import check_rate_limit


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserORM:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


def get_store_for_user(
    store_id: uuid.UUID,
    current_user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = get_store_owned(db, store_id, current_user.id)
    if store:
        return store
    existing = get_store_by_id(db, store_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def rate_limit_dependency(endpoint: str, limit: int, window_seconds: int):
    def _dependency(
        current_user: UserORM = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        allowed, retry_after = check_rate_limit(db, current_user.id, endpoint, limit, window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later",
                headers={"Retry-After": str(retry_after)},
            )

    return _dependency
