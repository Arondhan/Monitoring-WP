"""
Упрощённая конфигурация для локального запуска без Docker
Использует SQLite для тестирования
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения для локальной разработки"""
    
    # Используем SQLite для простоты (не требует установки PostgreSQL)
    # Для PostgreSQL: postgresql+asyncpg://user:pass@localhost:5432/db
    database_url: str = "sqlite+aiosqlite:///./uptime_db.sqlite"
    
    # Celery (требуется Redis)
    # Если Redis недоступен, можно запускать задачи синхронно
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "dev-secret-key-not-for-production"
    
    # SSL Check
    ssl_warning_days: int = 14
    
    # HTTP Check
    http_timeout: int = 10
    slow_threshold_ms: int = 1500
    
    # Check intervals
    default_check_interval: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
