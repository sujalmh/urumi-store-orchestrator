from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLogORM


def log_audit(
    db: Session,
    user_id,
    action: str,
    resource_type: str | None = None,
    resource_id=None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
):
    entry = AuditLogORM(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
