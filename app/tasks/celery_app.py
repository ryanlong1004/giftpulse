"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "giftpulse",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.monitor"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.celery_task_track_started,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_time_limit - 10,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "poll-twilio-logs": {
        "task": "app.tasks.monitor.poll_twilio_logs",
        "schedule": settings.poll_interval_seconds,
        "options": {"queue": "default"},
    },
}

celery_app.conf.task_routes = {
    "app.tasks.monitor.*": {"queue": "default"},
}
