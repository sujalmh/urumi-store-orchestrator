from sqlalchemy.orm import Session

from app.models.store import StoreORM


def get_store_by_id(db: Session, store_id) -> StoreORM | None:
    return db.query(StoreORM).filter(StoreORM.id == store_id).first()


def get_store_owned(db: Session, store_id, user_id) -> StoreORM | None:
    return (
        db.query(StoreORM)
        .filter(StoreORM.id == store_id, StoreORM.user_id == user_id)
        .first()
    )
