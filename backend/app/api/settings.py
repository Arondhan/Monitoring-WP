"""
API endpoints для настроек и прокси серверов.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.settings import (
    ProxyServerCreate,
    ProxyServerUpdate,
    ProxyServerResponse,
    ProxyServerListResponse,
    ProxyServerTestRequest,
    ProxyServerTestResponse,
    AppSettingResponse,
    AppSettingListResponse,
    SecuritySettings,
    SettingsDashboardResponse,
)
from app.services.proxy_service import ProxyService
from app.services.app_setting_service import AppSettingService

router = APIRouter(prefix="/api/settings", tags=["Settings"])


# ===== Proxy Server Endpoints =====

@router.get("/proxies", response_model=ProxyServerListResponse)
async def get_proxies(
    active_only: bool = Query(False, description="Только активные"),
    usage_type: Optional[str] = Query(None, description="Тип использования"),
    db: AsyncSession = Depends(get_db),
):
    """Получение списка прокси серверов."""
    service = ProxyService(db)
    proxies = await service.get_all(active_only=active_only, usage_type=usage_type)

    active_count = sum(1 for p in proxies if p.is_active)
    working_count = sum(1 for p in proxies if p.is_working is True)

    return ProxyServerListResponse(
        items=[ProxyServerResponse.model_validate(p) for p in proxies],
        total=len(proxies),
        active_count=active_count,
        working_count=working_count
    )


@router.post("/proxies", response_model=ProxyServerResponse)
async def create_proxy(
    data: ProxyServerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создание прокси сервера."""
    service = ProxyService(db)
    proxy = await service.create(data)
    return ProxyServerResponse.model_validate(proxy)


@router.get("/proxies/{proxy_id}", response_model=ProxyServerResponse)
async def get_proxy(
    proxy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Получение прокси сервера по ID."""
    service = ProxyService(db)
    proxy = await service.get(proxy_id)

    if not proxy:
        raise HTTPException(status_code=404, detail="Прокси не найден")

    return ProxyServerResponse.model_validate(proxy)


@router.put("/proxies/{proxy_id}", response_model=ProxyServerResponse)
async def update_proxy(
    proxy_id: str,
    data: ProxyServerUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновление прокси сервера."""
    service = ProxyService(db)
    proxy = await service.update(proxy_id, data)

    if not proxy:
        raise HTTPException(status_code=404, detail="Прокси не найден")

    return ProxyServerResponse.model_validate(proxy)


@router.delete("/proxies/{proxy_id}")
async def delete_proxy(
    proxy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Удаление прокси сервера."""
    service = ProxyService(db)
    success = await service.delete(proxy_id)

    if not success:
        raise HTTPException(status_code=404, detail="Прокси не найден")

    return {"success": True, "message": "Прокси удален"}


@router.post("/proxies/{proxy_id}/test", response_model=ProxyServerTestResponse)
async def test_proxy(
    proxy_id: str,
    request: ProxyServerTestRequest,
    db: AsyncSession = Depends(get_db),
):
    """Тестирование прокси сервера."""
    service = ProxyService(db)
    result = await service.test_proxy(
        proxy_id,
        test_url=request.test_url,
        timeout=request.timeout
    )
    return result


# ===== App Settings Endpoints =====

@router.get("/app", response_model=AppSettingListResponse)
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
):
    """Получение всех настроек."""
    service = AppSettingService(db)
    settings_list = await service.get_all()

    return AppSettingListResponse(
        items=[AppSettingResponse.model_validate(s) for s in settings_list],
        total=len(settings_list)
    )


@router.get("/app/{key}", response_model=AppSettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Получение настройки по ключу."""
    service = AppSettingService(db)
    setting = await service.get(key)

    if not setting:
        raise HTTPException(status_code=404, detail="Настройка не найдена")

    return AppSettingResponse.model_validate(setting)


@router.put("/app/{key}", response_model=AppSettingResponse)
async def update_setting(
    key: str,
    value: str,
    value_type: str = "string",
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Обновление/создание настройки."""
    service = AppSettingService(db)
    setting = await service.set_value(
        key, value, value_type=value_type, description=description
    )
    return AppSettingResponse.model_validate(setting)


@router.delete("/app/{key}")
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Удаление настройки."""
    service = AppSettingService(db)
    success = await service.delete(key)

    if not success:
        raise HTTPException(status_code=404, detail="Настройка не найдена")

    return {"success": True, "message": "Настройка удалена"}


# ===== Settings Group Endpoints =====

@router.get("/security", response_model=SecuritySettings)
async def get_security_settings(
    db: AsyncSession = Depends(get_db),
):
    """Получение настроек безопасности."""
    service = AppSettingService(db)
    settings_dict = await service.get_security_settings()
    return SecuritySettings(**settings_dict)


@router.put("/security")
async def update_security_settings(
    settings: SecuritySettings,
    db: AsyncSession = Depends(get_db),
):
    """Обновление настроек безопасности."""
    service = AppSettingService(db)
    await service.set_security_settings(settings.model_dump())
    return {"success": True, "message": "Настройки безопасности обновлены"}


# ===== Dashboard =====

@router.get("/dashboard", response_model=SettingsDashboardResponse)
async def get_settings_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """Сводка настроек дашборда."""
    from app.models.settings import ProxyServer
    from sqlalchemy import select, func

    service = AppSettingService(db)
    proxy_service = ProxyService(db)

    result = await db.execute(select(func.count(ProxyServer.id)))
    total_proxies = result.scalar() or 0

    result = await db.execute(
        select(func.count(ProxyServer.id)).where(ProxyServer.is_active == True)
    )
    active_proxies = result.scalar() or 0

    result = await db.execute(
        select(func.count(ProxyServer.id)).where(ProxyServer.is_working == True)
    )
    working_proxies = result.scalar() or 0

    security_settings = await service.get_security_settings()

    return SettingsDashboardResponse(
        total_proxies=total_proxies,
        active_proxies=active_proxies,
        working_proxies=working_proxies,
        security_settings=SecuritySettings(**security_settings),
    )
