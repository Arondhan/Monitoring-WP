"""
Uptime Checker - FastAPI Application
Главный файл приложения
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import settings
from app.db.session import init_db, close_db
from app.api.domains import router as domains_router, dashboard_router, wordpress_router
from app.api.docs import router as docs_router
from app.api.settings import router as settings_router


# Настройка логгирования
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting up Uptime Checker API...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Uptime Checker API...")
    await close_db()
    logger.info("Database connections closed")


# Создание FastAPI приложения
app = FastAPI(
    title="Uptime Checker API",
    description="""
## Uptime Checker API

API для мониторинга доступности и производительности веб-сайтов.

### Основные возможности:

* **Управление доменами** - Добавление, удаление и редактирование доменов для мониторинга
* **Проверка доступности** - Автоматическая проверка HTTP/HTTPS эндпоинтов
* **SSL мониторинг** - Проверка срока действия SSL сертификатов
* **История проверок** - Хранение и анализ результатов проверок
* **Инциденты** - Отслеживание простоев и проблем
* **Статистика** - Расчет uptime и времени отклика

### Статусы доменов:

* **UP** - Сайт доступен, время отклика в норме
* **SLOW** - Сайт доступен, но время отклика превышено
* **DOWN** - Сайт недоступен или возвращает ошибки
* **SSL_ERROR** - Проблема с SSL сертификатом
* **PENDING** - Домен добавлен, проверка еще не выполнена
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация роутеров (wordpress_router должен быть перед domains_router)
app.include_router(wordpress_router)  # WordPress endpoints (должен быть первым)
app.include_router(domains_router)
app.include_router(dashboard_router)
app.include_router(settings_router)  # Settings endpoints
app.include_router(docs_router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "name": "Uptime Checker API",
        "version": "1.0.0",
        "description": "Система мониторинга доступности веб-сайтов",
        "docs": "/docs",
        "redoc": "/redoc",
        "project_docs": "/project-docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "database": "connected",
    }


@app.get("/api/status")
async def api_status():
    """Статус API и настройки"""
    return {
        "settings": {
            "http_timeout": settings.http_timeout,
            "slow_threshold_ms": settings.slow_threshold_ms,
            "ssl_warning_days": settings.ssl_warning_days,
            "default_check_interval": settings.default_check_interval,
        }
    }


# Обработка исключений
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error("Internal server error", exc_info=exc)
    return {"detail": "Internal server error"}
