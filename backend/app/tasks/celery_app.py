from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "provisioning",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.store_tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_default_retry_delay=60,
    broker_connection_retry_on_startup=True,
)
