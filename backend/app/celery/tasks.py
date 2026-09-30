"""
Celery задачи для проверки доменов
"""
import time
import ssl
import socket
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse
import asyncio

import httpx
import structlog
from celery import Task
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery import celery_app
from app.core.config import settings
from app.db.session import async_session_maker
from app.models.domain import Domain, Check, Incident


logger = structlog.get_logger(__name__)


# ===== Helper функции =====

def parse_url(url: str) -> Tuple[str, str, int]:
    """Парсинг URL для получения схемы, хоста и порта"""
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    host = parsed.hostname or url
    port = parsed.port or (443 if scheme == "https" else 80)
    return scheme, host, port


def check_ssl_certificate(host: str, port: int = 443, timeout: int = 5) -> Dict[str, Any]:
    """
    Проверка SSL сертификата
    
    Returns:
        Dict с информацией о сертификате:
        - valid: bool
        - expires_at: datetime
        - days_remaining: int
        - error: str (если есть ошибка)
    """
    result = {
        "valid": False,
        "expires_at": None,
        "days_remaining": None,
        "error": None,
        "issuer": None,
        "subject": None,
    }
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
                # Получаем дату истечения
                expires_at = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                days_remaining = (expires_at - now).days
                
                result.update({
                    "valid": True,
                    "expires_at": expires_at,
                    "days_remaining": days_remaining,
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                })
                
    except ssl.SSLCertVerificationError as e:
        result["error"] = f"SSL verification failed: {str(e)}"
    except ssl.SSLError as e:
        result["error"] = f"SSL error: {str(e)}"
    except socket.timeout:
        result["error"] = "Connection timeout"
    except socket.gaierror:
        result["error"] = "DNS resolution failed"
    except Exception as e:
        result["error"] = f"SSL check failed: {str(e)}"
    
    return result


async def check_http_endpoint(
    url: str,
    timeout: int = 10,
    follow_redirects: bool = True,
    content_match: Optional[str] = None,
) -> Dict[str, Any]:
    """
    HTTP проверка эндпоинта
    
    Returns:
        Dict с результатами проверки:
        - status_code: int
        - response_time_ms: int
        - success: bool
        - error: str (если есть ошибка)
        - content_matched: bool (если была проверка контента)
    """
    result = {
        "status_code": None,
        "response_time_ms": None,
        "success": False,
        "error": None,
        "content_matched": None,
        "headers": {},
    }
    
    start_time = time.perf_counter()
    
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=follow_redirects,
            verify=True,
        ) as client:
            response = await client.get(url)
            
            elapsed = time.perf_counter() - start_time
            response_time_ms = int(elapsed * 1000)
            
            result.update({
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "success": response.status_code in (200, 201, 202, 203, 204, 301, 302, 303, 307, 308),
                "headers": dict(response.headers),
            })
            
            # Проверка контента (если задана)
            if content_match:
                result["content_matched"] = content_match in response.text
            
    except httpx.TimeoutException as e:
        result["error"] = f"Request timeout after {timeout}s"
    except httpx.ConnectError as e:
        result["error"] = f"Connection failed: {str(e)}"
    except httpx.SSLCertVerificationError as e:
        result["error"] = f"SSL verification failed: {str(e)}"
    except httpx.RequestError as e:
        result["error"] = f"Request error: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
    
    return result


def determine_status(
    http_result: Dict[str, Any],
    ssl_result: Optional[Dict[str, Any]] = None,
    slow_threshold_ms: int = 1500,
    ssl_warning_days: int = 14,
) -> Tuple[str, Optional[str]]:
    """
    Определение статуса проверки
    
    Returns:
        Tuple[status, error_message]
    """
    # Проверка SSL
    if ssl_result and ssl_result.get("error"):
        return "SSL_ERROR", ssl_result["error"]
    
    if ssl_result and ssl_result.get("days_remaining") is not None:
        if ssl_result["days_remaining"] < 0:
            return "SSL_ERROR", f"SSL certificate expired {abs(ssl_result['days_remaining'])} days ago"
        if ssl_result["days_remaining"] < ssl_warning_days:
            return "SSL_WARNING", f"SSL certificate expires in {ssl_result['days_remaining']} days"
    
    # Проверка HTTP
    if http_result.get("error"):
        error = http_result["error"]
        if "timeout" in error.lower():
            return "DOWN", "Timeout - site did not respond"
        elif "connection" in error.lower() or "dns" in error.lower():
            return "DOWN", "Connection failed - site unreachable"
        elif "ssl" in error.lower():
            return "SSL_ERROR", error
        else:
            return "DOWN", error
    
    status_code = http_result.get("status_code")
    response_time = http_result.get("response_time_ms", 0)
    
    if status_code is None:
        return "DOWN", "No status code received"
    
    if status_code >= 500:
        return "DOWN", f"Server error: {status_code}"
    
    if status_code >= 400:
        return "DOWN", f"Client error: {status_code}"
    
    # Проверка времени отклика
    if response_time >= slow_threshold_ms:
        return "SLOW", f"Slow response: {response_time}ms"
    
    # Проверка контента
    if http_result.get("content_matched") is False:
        return "DOWN", "Content check failed - expected content not found"
    
    return "UP", None


# ===== Celery Tasks =====

@celery_app.task(bind=True, max_retries=3)
def check_domain_task(self, domain_id: str) -> Dict[str, Any]:
    """
    Основная задача проверки домена
    
    Args:
        domain_id: UUID домена в виде строки
    
    Returns:
        Dict с результатами проверки
    """
    from uuid import UUID
    
    domain_uuid = UUID(domain_id)
    
    # Запускаем асинхронную проверку
    result = asyncio.run(_perform_check(domain_uuid))
    
    return result


async def _perform_check(domain_uuid) -> Dict[str, Any]:
    """Асинхронное выполнение проверки"""
    
    async with async_session_maker() as session:
        # Получаем домен
        result = await session.execute(
            select(Domain).where(Domain.id == domain_uuid)
        )
        domain = result.scalar_one_or_none()
        
        if not domain:
            logger.warning(f"Domain {domain_uuid} not found")
            return {"error": "Domain not found"}
        
        logger.info(f"Checking domain: {domain.url}")
        
        # Парсим URL
        scheme, host, port = parse_url(domain.url)
        
        # Выполняем проверки параллельно
        http_result = await check_http_endpoint(
            url=domain.url,
            timeout=settings.http_timeout,
            content_match=None,  # Можно добавить проверку контента
        )
        
        # SSL проверка только для HTTPS
        ssl_result = None
        if scheme == "https":
            ssl_result = check_ssl_certificate(host, port, timeout=5)
        
        # Определяем статус
        status, error_message = determine_status(
            http_result,
            ssl_result,
            settings.slow_threshold_ms,
            settings.ssl_warning_days,
        )
        
        # Создаем запись проверки
        check = Check(
            domain_id=domain.id,
            timestamp=datetime.now(timezone.utc),
            status_code=http_result.get("status_code"),
            response_time_ms=http_result.get("response_time_ms"),
            status=status,
            error_message=error_message,
            ssl_expires_at=ssl_result.get("expires_at") if ssl_result else None,
            ssl_days_remaining=ssl_result.get("days_remaining") if ssl_result else None,
        )
        
        session.add(check)
        
        # Обновляем кэшированные данные домена
        domain.last_status = status
        domain.last_response_time_ms = http_result.get("response_time_ms")
        domain.last_checked_at = datetime.now(timezone.utc)
        
        # Обрабатываем инциденты
        await _handle_incidents(session, domain, status, error_message)
        
        # Отправляем уведомления при изменении статуса
        await _check_status_change(session, domain, status)
        
        await session.commit()
        
        logger.info(
            f"Check completed for {domain.url}: {status}",
            response_time=http_result.get("response_time_ms"),
        )
        
        return {
            "domain_id": str(domain.id),
            "status": status,
            "response_time_ms": http_result.get("response_time_ms"),
            "status_code": http_result.get("status_code"),
            "error_message": error_message,
        }


async def _handle_incidents(
    session: AsyncSession,
    domain: Domain,
    status: str,
    error_message: Optional[str],
):
    """Обработка инцидентов - создание и закрытие"""
    
    # Если домен DOWN или SSL_ERROR - создаем инцидент
    if status in ("DOWN", "SSL_ERROR"):
        # Проверяем есть ли активный инцидент
        result = await session.execute(
            select(Incident)
            .where(Incident.domain_id == domain.id)
            .where(Incident.is_resolved == 0)
            .order_by(Incident.start_time.desc())
            .limit(1)
        )
        existing_incident = result.scalar_one_or_none()
        
        if not existing_incident:
            # Создаем новый инцидент
            reason = "SSL_ERROR" if status == "SSL_ERROR" else (error_message or "UNKNOWN_ERROR")[:100]
            severity = "CRITICAL" if status == "SSL_ERROR" else "HIGH"
            
            incident = Incident(
                domain_id=domain.id,
                start_time=datetime.now(timezone.utc),
                reason=reason,
                severity=severity,
                error_details=error_message,
                is_resolved=0,
            )
            session.add(incident)
            logger.info(f"Created incident for domain {domain.url}")
    
    # Если домен UP и был активный инцидент - закрываем его
    elif status == "UP":
        result = await session.execute(
            select(Incident)
            .where(Incident.domain_id == domain.id)
            .where(Incident.is_resolved == 0)
            .order_by(Incident.start_time.asc())
            .limit(1)
        )
        active_incident = result.scalar_one_or_none()
        
        if active_incident:
            active_incident.is_resolved = 1
            active_incident.end_time = datetime.now(timezone.utc)
            duration = active_incident.end_time - active_incident.start_time
            active_incident.duration_seconds = int(duration.total_seconds())
            logger.info(
                f"Resolved incident for domain {domain.url}",
                duration=active_incident.duration_seconds,
            )


async def _check_status_change(
    session: AsyncSession,
    domain: Domain,
    new_status: str,
):
    """Проверка изменения статуса и отправка уведомлений"""
    # Здесь будет логика уведомлений
    # Пока просто логируем
    if new_status == "DOWN":
        logger.warning(f"ALERT: Domain {domain.url} is DOWN!")
    elif new_status == "UP" and domain.last_status == "DOWN":
        logger.info(f"RECOVERY: Domain {domain.url} is back UP!")


@celery_app.task
def schedule_domain_checks():
    """
    Планировщик проверок доменов
    Проверяет какие домены нужно проверить и создает задачи
    """
    import asyncio
    from asyncio import new_event_loop, set_event_loop

    # Создаем новый event loop для этой задачи
    loop = new_event_loop()
    set_event_loop(loop)

    try:
        loop.run_until_complete(_schedule())
    finally:
        loop.close()


async def _schedule():
    """Асинхронное планирование"""
    async with async_session_maker() as session:
        result = await session.execute(select(Domain))
        domains = result.scalars().all()

        now = datetime.now(timezone.utc)

        for domain in domains:
            # Проверяем нужно ли проверять домен
            should_check = False

            if domain.last_checked_at is None:
                should_check = True
            else:
                time_since_check = now - domain.last_checked_at
                if time_since_check.total_seconds() >= domain.check_interval_seconds:
                    should_check = True

            if should_check:
                # Запускаем задачу проверки
                check_domain_task.delay(str(domain.id))


@celery_app.task
def calculate_uptime_stats():
    """
    Пересчет статистики uptime для всех доменов
    Выполняется периодически
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Создаем синхронный движок для Celery задач
    from app.core.config import settings
    from app.models.domain import Domain, Check
    from datetime import timedelta
    
    # Преобразуем asyncpg URL в psycopg2 URL для синхронного подключения
    db_url = settings.database_url.replace(
        "postgresql+asyncpg://", 
        "postgresql://"
    )
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    
    try:
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        # Получаем все домены
        domains = session.query(Domain).all()
        
        for domain in domains:
            # Считаем uptime за 24 часа
            checks_24h = session.query(Check).filter(
                Check.domain_id == domain.id,
                Check.timestamp >= day_ago
            ).all()
            
            if checks_24h:
                up_count_24h = sum(1 for c in checks_24h if c.status == "UP")
                domain.uptime_percentage_24h = int((up_count_24h / len(checks_24h)) * 100)
            
            # Считаем uptime за 7 дней
            checks_7d = session.query(Check).filter(
                Check.domain_id == domain.id,
                Check.timestamp >= week_ago
            ).all()
            
            if checks_7d:
                up_count_7d = sum(1 for c in checks_7d if c.status == "UP")
                domain.uptime_percentage_7d = int((up_count_7d / len(checks_7d)) * 100)
        
        session.commit()
        logger.info("Uptime stats calculated successfully")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error calculating uptime stats: {e}")
        raise
    finally:
        session.close()
        engine.dispose()


@celery_app.task
def cleanup_old_checks(days_to_keep: int = 30):
    """
    Очистка старых записей проверок
    """
    from asyncio import new_event_loop, set_event_loop

    # Создаем новый event loop для этой задачи
    loop = new_event_loop()
    set_event_loop(loop)

    try:
        loop.run_until_complete(_cleanup())
    finally:
        loop.close()


async def _cleanup():
    """Асинхронная очистка"""
    async with async_session_maker() as session:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        result = await session.execute(
            select(Check.id)
            .where(Check.timestamp < cutoff_date)
        )
        old_check_ids = result.scalars().all()

    if old_check_ids:
        await session.execute(
            Check.__table__.delete()
            .where(Check.id.in_(old_check_ids))
        )
        await session.commit()
        logger.info(f"Deleted {len(old_check_ids)} old checks")


# ===== WordPress Monitoring Tasks =====

@celery_app.task(bind=True)
def check_wordpress_post_task(self, domain_id: str) -> Dict[str, Any]:
    """
    Задача мониторинга WordPress-сайта: определяет WP, получает дату последнего поста.

    Используется Uptime Checker для отображения "возраста поста" и SEO-инфо.
    Не путать с автопостером (постинг статей) — это только мониторинг.

    Args:
        domain_id: UUID домена в виде строки

    Returns:
        Dict с результатами проверки
    """
    from uuid import UUID
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.services.wordpress import get_wordpress_content

    domain_uuid = UUID(domain_id)

    logger.info(f"Checking WordPress: {domain_id}")

    db_url = settings.database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://"
    )

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()

    try:
        domain = session.query(Domain).filter(Domain.id == domain_uuid).first()

        if not domain:
            logger.warning(f"Domain {domain_uuid} not found")
            return {"error": "Domain not found"}

        logger.info(f"Checking WordPress: {domain.url}")

        wp_result = asyncio.run(get_wordpress_content(domain.url))

        is_wp = 1 if (wp_result.get('h1') or wp_result.get('meta_title')) else 0
        domain.is_wordpress = is_wp
        domain.last_post_title = wp_result.get('h1') or wp_result.get('meta_title')
        domain.last_post_checked_at = datetime.now(timezone.utc)
        domain.wordpress_version = None

        session.commit()

        logger.info(
            f"WordPress check completed for {domain.url}",
            is_wordpress=bool(domain.is_wordpress),
            h1=wp_result.get('h1'),
        )

        return {
            "domain_id": str(domain.id),
            "is_wordpress": bool(is_wp),
            "last_post_date": domain.last_post_date.isoformat() if domain.last_post_date else None,
            "last_post_title": domain.last_post_title,
            "wordpress_version": domain.wordpress_version,
            "checked_at": domain.last_post_checked_at.isoformat() if domain.last_post_checked_at else None,
        }

    except Exception as e:
        session.rollback()
        logger.error(f"Error checking WordPress: {e}")
        raise
    finally:
        session.close()
        engine.dispose()
