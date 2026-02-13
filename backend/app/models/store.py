from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class StoreORM(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(63), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    namespace: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    helm_release_name: Mapped[str] = mapped_column(String(63), nullable=False)
    admin_username: Mapped[Optional[str]] = mapped_column(String(255))
    admin_password: Mapped[Optional[str]] = mapped_column(String(255))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    ready_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    user: Mapped["UserORM"] = relationship("UserORM", back_populates="stores")

    __table_args__ = (
        Index("idx_stores_user_id", "user_id"),
        Index("idx_status", "status"),
    )
