"""Celery configuration for background tasks."""
from celery import Celery
from celery.signals import worker_ready

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "smart_agri",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.weather_tasks",
        "app.tasks.market_tasks",
        "app.tasks.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Handle worker ready signal."""
    print("Celery worker is ready!")


# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "fetch-weather-data": {
        "task": "app.tasks.weather_tasks.fetch_weather_for_all_locations",
        "schedule": 3600.0,  # Every hour
    },
    "update-market-prices": {
        "task": "app.tasks.market_tasks.update_market_prices",
        "schedule": 86400.0,  # Every day
    },
}
