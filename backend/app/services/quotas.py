from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.store import StoreORM


def get_store_count(db: Session, user_id) -> int:
    return db.query(func.count(StoreORM.id)).filter(StoreORM.user_id == user_id).scalar() or 0


def check_quota(db: Session, user_id, quota_limit: int) -> bool:
    return get_store_count(db, user_id) < quota_limit
