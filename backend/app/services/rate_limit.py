from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.rate_limit import RateLimitORM


def _window_start(now: datetime, window_seconds: int) -> datetime:
    epoch = int(now.timestamp())
    window_epoch = epoch - (epoch % window_seconds)
    return datetime.fromtimestamp(window_epoch, tz=timezone.utc)


def check_rate_limit(
    db: Session,
    user_id,
    endpoint: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    now = datetime.now(timezone.utc)
    window_start = _window_start(now, window_seconds)

    record = (
        db.query(RateLimitORM)
        .filter(
            RateLimitORM.user_id == user_id,
            RateLimitORM.endpoint == endpoint,
            RateLimitORM.window_start == window_start,
        )
        .first()
    )

    if not record:
        record = RateLimitORM(
            user_id=user_id,
            endpoint=endpoint,
            window_start=window_start,
            request_count=1,
        )
        db.add(record)
        db.commit()
        return True, window_seconds

    if record.request_count >= limit:
        retry_after = int((window_start + timedelta(seconds=window_seconds) - now).total_seconds())
        return False, max(retry_after, 1)

    record.request_count += 1
    db.commit()
    return True, window_seconds
