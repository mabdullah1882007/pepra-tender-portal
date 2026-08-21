from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "tender_portal",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Karachi",
    enable_utc=True,
    beat_schedule={
        "fetch-tenders-every-hour": {
            "task": "app.tasks.fetch_tenders.schedule_fetch",
            "schedule": 3600.0,
        },
    },
)
