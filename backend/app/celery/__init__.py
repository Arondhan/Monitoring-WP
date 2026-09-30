from celery import Celery
from celery.schedules import crontab
from app.core.config import settings


# Создание Celery приложения
celery_app = Celery(
    "uptime_checker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.celery.tasks"],
)

# Конфигурация Celery
celery_app.conf.update(
    # Сериализация
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Настройки задач
    task_track_started=True,
    task_time_limit=300,  # 5 минут максимум на задачу
    task_soft_time_limit=240,  # 4 минуты мягкий лимит
    
    # Retry настройки
    task_autoretry_for=(Exception,),
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_max_retries=3,
    
    # Prefetch multiplier
    worker_prefetch_multiplier=1,
    
    # Beat schedule - расписание периодических задач
    beat_schedule={
        "calculate-uptime-stats": {
            "task": "app.celery.tasks.calculate_uptime_stats",
            "schedule": 300.0,  # Каждые 5 минут пересчитываем статистику
        },
        "cleanup-old-checks": {
            "task": "app.celery.tasks.cleanup_old_checks",
            "schedule": crontab(minute=0, hour=3),  # Каждый день в 3:00
        },
    },
)
