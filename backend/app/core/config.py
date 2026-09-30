from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Настройки приложения"""

    # Database
    database_url: str = "sqlite+aiosqlite:///./uptime_db.sqlite"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "your-secret-key-change-in-production"

    # SSL Check
    ssl_warning_days: int = 14

    # HTTP Check
    http_timeout: int = 10
    slow_threshold_ms: int = 1500

    # Check intervals
    default_check_interval: int = 60

    # Notification settings (for future use)
    enable_email_notifications: bool = False
    enable_slack_notifications: bool = False
    enable_telegram_notifications: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Получить кэшированные настройки"""
    return Settings()


settings = get_settings()
