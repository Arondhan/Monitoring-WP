"""
API endpoints для управления доменами
"""
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.domain import Domain, Check, Incident
from app.schemas.domain import (
    DomainCreate,
    DomainUpdate,
    DomainResponse,
    DomainListResponse,
    CheckResponse,
    CheckListResponse,
    IncidentResponse,
    IncidentListResponse,
    DashboardSummary,
    StatusCount,
    WordPressCheckResponse,
    WordPressStats,
    WordPressContent,
)
from app.celery.tasks import check_domain_task, check_wordpress_post_task

# Основной роутер
router = APIRouter(prefix="/api/domains", tags=["domains"])

# WordPress роутер (должен быть зарегистрирован ПЕРЕД роутами с {domain_id})
wordpress_router = APIRouter(prefix="/api/domains", tags=["domains"])


def calculate_wordpress_age(post_date: datetime) -> tuple[Optional[int], Optional[str]]:
    """
    Вычисление возраста последнего поста WordPress.

    Returns:
        (age_days, status): возраст в днях и статус
        - "fresh": < 7 дней (🟢)
        - "warning": 7-30 дней (🟡)
        - "stale": > 30 дней (🔴)
    """
    if not post_date:
        return None, None

    now = datetime.now(timezone.utc)
    if post_date.tzinfo is None:
        post_date = post_date.replace(tzinfo=timezone.utc)

    age_days = (now - post_date).days

    if age_days < 0:
        return 0, "fresh"
    elif age_days < 7:
        return age_days, "fresh"
    elif age_days < 30:
        return age_days, "warning"
    else:
        return age_days, "stale"


# ===== WordPress Stats Endpoint (должен быть ПЕРЕД {domain_id}) =====

@wordpress_router.get("/wordpress/stats", response_model=WordPressStats)
async def get_wordpress_stats(db: AsyncSession = Depends(get_db)):
    """
    Получить статистику WordPress сайтов.

    Возвращает количество WordPress сайтов по статусам:
    - total: Всего WordPress сайтов
    - fresh: < 7 дней (🟢)
    - warning: 7-30 дней (🟡)
    - stale: > 30 дней (🔴)
    - no_posts: WordPress без постов
    """
    result = await db.execute(select(Domain))
    domains = result.scalars().all()

    stats = WordPressStats()

    for domain in domains:
        if domain.is_wordpress:
            stats.total += 1

            if not domain.last_post_date:
                stats.no_posts += 1
            else:
                _, post_status = calculate_wordpress_age(domain.last_post_date)
                if post_status == "fresh":
                    stats.fresh += 1
                elif post_status == "warning":
                    stats.warning += 1
                elif post_status == "stale":
                    stats.stale += 1

    return stats


# ===== Domain Endpoints =====


@router.get("", response_model=DomainListResponse)
async def get_domains(
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    wordpress_only: bool = Query(False, description="Только WordPress сайты"),
    wordpress_status: Optional[str] = Query(None, description="Фильтр по возрасту поста (fresh/warning/stale)"),
):
    """
    Получить список всех доменов с фильтрацией и сортировкой

    - **status**: Фильтр по статусу (UP, DOWN, SLOW, SSL_ERROR, PENDING)
    - **sort_by**: Поле для сортировки (name, status, last_response_time_ms, created_at)
    - **sort_order**: Порядок сортировки (asc, desc)
    - **wordpress_only**: Только WordPress сайты
    - **wordpress_status**: Фильтр по возрасту поста (fresh/warning/stale)
    """
    query = select(Domain)

    if status_filter:
        query = query.where(Domain.last_status == status_filter.upper())

    if wordpress_only:
        query = query.where(Domain.is_wordpress == 1)

    sort_columns = {
        "name": Domain.name,
        "status": Domain.last_status,
        "last_response_time_ms": Domain.last_response_time_ms,
        "created_at": Domain.created_at,
        "uptime_percentage_24h": Domain.uptime_percentage_24h,
    }

    sort_column = sort_columns.get(sort_by, Domain.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    domains = result.scalars().all()

    count_query = select(func.count(Domain.id))
    if status_filter:
        count_query = count_query.where(Domain.last_status == status_filter.upper())
    if wordpress_only:
        count_query = count_query.where(Domain.is_wordpress == 1)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Вычисляем возраст поста для каждого домена
    domains_with_age = []
    for domain in domains:
        domain_dict = DomainResponse.model_validate(domain)
        if domain.is_wordpress and domain.last_post_date:
            age_days, post_status = calculate_wordpress_age(domain.last_post_date)
            domain_dict.wordpress_post_age_days = age_days
            domain_dict.wordpress_post_status = post_status
        domains_with_age.append(domain_dict)

    return DomainListResponse(
        items=domains_with_age,
        total=total,
    )


@router.post("", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain_data: DomainCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Добавить новый домен для мониторинга

    - **url**: URL сайта для мониторинга
    - **name**: Отображаемое имя домена
    - **check_interval_seconds**: Интервал проверки в секундах (30-3600)
    """
    existing = await db.execute(
        select(Domain).where(Domain.url == str(domain_data.url))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain with this URL already exists",
        )

    domain = Domain(
        url=str(domain_data.url),
        name=domain_data.name,
        check_interval_seconds=domain_data.check_interval_seconds,
        last_status="PENDING",
    )

    db.add(domain)
    await db.commit()
    await db.refresh(domain)

    # Запускаем HTTP-проверку и проверку WordPress параллельно
    check_domain_task.delay(str(domain.id))
    check_wordpress_post_task.delay(str(domain.id))

    return DomainResponse.model_validate(domain)


@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Получить детальную информацию о домене"""
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id)
    )
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    return DomainResponse.model_validate(domain)


@router.put("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: UUID,
    domain_data: DomainUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновить информацию о домене"""
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id)
    )
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    update_data = domain_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(domain, field, value)

    await db.commit()
    await db.refresh(domain)

    return DomainResponse.model_validate(domain)


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Удалить домен из мониторинга"""
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id)
    )
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    await db.delete(domain)
    await db.commit()

    return None


@router.post("/{domain_id}/check", response_model=dict)
async def trigger_domain_check(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Запустить немедленную проверку домена

    Задача выполняется асинхронно через Celery.
    Результат будет доступен через GET /api/domains/{domain_id} после завершения.
    """
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id)
    )
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    check_domain_task.delay(str(domain.id))

    return {
        "message": "Check initiated",
        "domain_id": str(domain.id),
        "status": "pending",
    }


@router.post("/{domain_id}/wordpress/check", response_model=WordPressCheckResponse)
async def check_domain_wordpress(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Запустить проверку WordPress-сайта: определить WP, получить дату последнего поста.

    Задача выполняется асинхронно через Celery.
    """
    result = await db.execute(
        select(Domain).where(Domain.id == domain_id)
    )
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    check_wordpress_post_task.delay(str(domain.id))

    return WordPressCheckResponse(
        domain_id=domain.id,
        is_wordpress=bool(domain.is_wordpress),
        last_post_date=domain.last_post_date,
        last_post_title=domain.last_post_title,
        last_post_checked_at=domain.last_post_checked_at,
        wordpress_version=domain.wordpress_version,
    )


@router.get("/{domain_id}/content", response_model=WordPressContent)
async def get_domain_content(domain_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Получить контент главной страницы WordPress (заголовки, мета-информация).
    Используется для SEO-мониторинга в Uptime Checker.

    Returns:
    - meta_title: Meta Title из <title> или Yoast SEO
    - meta_description: Meta Description
    - h1: Главный заголовок страницы
    - h2: Список подзаголовков H2
    """
    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    if not domain.is_wordpress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a WordPress site",
        )

    from app.services.wordpress import get_wordpress_content
    content = await get_wordpress_content(domain.url)

    return WordPressContent(
        meta_title=content.get('meta_title'),
        meta_title_length=content.get('meta_title_length'),
        meta_description=content.get('meta_description'),
        meta_description_length=content.get('meta_description_length'),
        h1=content.get('h1'),
        h2=content.get('h2', []),
    )


@router.get("/{domain_id}/checks", response_model=CheckListResponse)
async def get_domain_checks(
    domain_id: UUID,
    period: str = Query("24h", description="Период: 1h, 24h, 7d, 30d"),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить историю проверок домена за определенный период

    - **period**: Период времени (1h, 6h, 24h, 7d, 30d)
    - **limit**: Максимальное количество записей
    """
    now = datetime.now(timezone.utc)
    period_map = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(days=1),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }

    delta = period_map.get(period, timedelta(days=1))
    start_time = now - delta

    result = await db.execute(
        select(Check)
        .where(Check.domain_id == domain_id)
        .where(Check.timestamp >= start_time)
        .order_by(Check.timestamp)
        .limit(limit)
    )
    checks = result.scalars().all()

    domain_result = await db.execute(
        select(Domain.id).where(Domain.id == domain_id)
    )
    if not domain_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    return CheckListResponse(
        items=[CheckResponse.model_validate(c) for c in checks],
        total=len(checks),
        period=period,
    )


@router.get("/{domain_id}/incidents", response_model=IncidentListResponse)
async def get_domain_incidents(
    domain_id: UUID,
    include_resolved: bool = Query(True, description="Включать завершенные инциденты"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список инцидентов для домена

    - **include_resolved**: Включать ли завершенные инциденты
    """
    domain_result = await db.execute(
        select(Domain.id).where(Domain.id == domain_id)
    )
    if not domain_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    query = select(Incident).where(Incident.domain_id == domain_id)

    if not include_resolved:
        query = query.where(Incident.is_resolved == 0)

    query = query.order_by(desc(Incident.start_time)).limit(limit)

    result = await db.execute(query)
    incidents = result.scalars().all()

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(i) for i in incidents],
        total=len(incidents),
    )


@router.get("/{domain_id}/stats", response_model=dict)
async def get_domain_stats(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Получить статистику по домену"""
    domain_result = await db.execute(
        select(Domain).where(Domain.id == domain_id)
    )
    domain = domain_result.scalar_one_or_none()

    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)

    checks_24h_result = await db.execute(
        select(
            func.count(Check.id),
            func.avg(Check.response_time_ms),
        )
        .where(Check.domain_id == domain_id)
        .where(Check.timestamp >= day_ago)
    )
    total_24h, avg_response_24h = checks_24h_result.one()

    last_check_result = await db.execute(
        select(Check)
        .where(Check.domain_id == domain_id)
        .order_by(desc(Check.timestamp))
        .limit(1)
    )
    last_check = last_check_result.scalar_one_or_none()

    return {
        "domain_id": str(domain.id),
        "total_checks_24h": total_24h or 0,
        "uptime_percentage_24h": domain.uptime_percentage_24h,
        "uptime_percentage_7d": domain.uptime_percentage_7d,
        "average_response_time_ms": round(avg_response_24h, 2) if avg_response_24h else None,
        "last_status": domain.last_status,
        "last_response_time_ms": domain.last_response_time_ms,
        "last_checked_at": domain.last_checked_at,
    }


# ===== Dashboard Endpoints =====

dashboard_router = APIRouter(prefix="/api", tags=["dashboard"])


@dashboard_router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Получить сводку дашборда"""
    total_result = await db.execute(select(func.count(Domain.id)))
    total_domains = total_result.scalar() or 0

    status_result = await db.execute(
        select(
            Domain.last_status,
            func.count(Domain.id),
        )
        .group_by(Domain.last_status)
    )
    status_rows = status_result.all()

    status_counts = StatusCount()
    for row in status_rows:
        status_lower = (row[0] or "").lower()
        if status_lower == "up":
            status_counts.up = row[1]
        elif status_lower == "down":
            status_counts.down = row[1]
        elif status_lower == "slow":
            status_counts.slow = row[1]
        elif status_lower == "ssl_error":
            status_counts.ssl_error = row[1]
        elif status_lower == "pending":
            status_counts.pending = row[1]

    uptime_result = await db.execute(
        select(func.avg(Domain.uptime_percentage_24h))
    )
    avg_uptime = uptime_result.scalar() or 0.0

    incidents_result = await db.execute(
        select(func.count(Incident.id))
        .where(Incident.is_resolved == 0)
    )
    active_incidents = incidents_result.scalar() or 0

    return DashboardSummary(
        total_domains=total_domains,
        status_counts=status_counts,
        overall_uptime=round(avg_uptime, 2),
        active_incidents=active_incidents,
    )
