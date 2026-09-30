"""
Сервис для управления прокси серверами.
"""
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import httpx

from app.models.settings import ProxyServer
from app.schemas.settings import ProxyServerCreate, ProxyServerUpdate, ProxyServerTestResponse

logger = structlog.get_logger(__name__)


class ProxyService:
    """Сервис для управления прокси серверами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ProxyServerCreate) -> ProxyServer:
        """Создание прокси сервера."""
        proxy = ProxyServer(
            name=data.name,
            description=data.description,
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password,
            protocol=data.protocol,
            usage_type=data.usage_type,
            country=data.country,
        )
        self.db.add(proxy)
        await self.db.commit()
        await self.db.refresh(proxy)
        logger.info(f"Created proxy server: {proxy.id}")
        return proxy

    async def get(self, proxy_id) -> Optional[ProxyServer]:
        """Получение прокси сервера по ID."""
        result = await self.db.execute(
            select(ProxyServer).where(ProxyServer.id == proxy_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        active_only: bool = False,
        usage_type: Optional[str] = None
    ) -> List[ProxyServer]:
        """Получение всех прокси серверов."""
        query = select(ProxyServer).order_by(ProxyServer.created_at.desc())
        
        if active_only:
            query = query.where(ProxyServer.is_active == True)
        if usage_type:
            query = query.where(ProxyServer.usage_type == usage_type)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        proxy_id,
        data: ProxyServerUpdate
    ) -> Optional[ProxyServer]:
        """Обновление прокси сервера."""
        proxy = await self.get(proxy_id)
        if not proxy:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proxy, field, value)

        await self.db.commit()
        await self.db.refresh(proxy)
        logger.info(f"Updated proxy server: {proxy.id}")
        return proxy

    async def delete(self, proxy_id) -> bool:
        """Удаление прокси сервера."""
        proxy = await self.get(proxy_id)
        if not proxy:
            return False

        await self.db.delete(proxy)
        await self.db.commit()
        logger.info(f"Deleted proxy server: {proxy_id}")
        return True

    async def test_proxy(
        self,
        proxy_id,
        test_url: str = "https://www.google.com",
        timeout: int = 10
    ) -> ProxyServerTestResponse:
        """
        Тестирование прокси сервера.
        
        Проверяет:
        - Подключение к прокси
        - Доступ к тестовому URL
        - Время отклика
        """
        proxy = await self.get(proxy_id)
        if not proxy:
            return ProxyServerTestResponse(
                success=False,
                is_working=False,
                error="Proxy not found",
                test_url=test_url,
                tested_at=datetime.now(timezone.utc)
            )

        try:
            # Формируем URL прокси
            proxies = {
                "http://": proxy.connection_url,
                "https://": proxy.connection_url,
            }

            async with httpx.AsyncClient(
                proxies=proxies,
                timeout=timeout
            ) as client:
                start_time = datetime.now()
                response = await client.get(test_url)
                end_time = datetime.now()
                
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                is_working = response.status_code == 200
                
                # Обновляем статус прокси
                proxy.is_working = is_working
                proxy.last_checked_at = datetime.now(timezone.utc)
                await self.db.commit()
                
                logger.info(
                    f"Proxy test {'successful' if is_working else 'failed'}",
                    proxy_id=proxy_id,
                    response_time_ms=response_time_ms
                )
                
                return ProxyServerTestResponse(
                    success=True,
                    is_working=is_working,
                    response_time_ms=response_time_ms,
                    test_url=test_url,
                    tested_at=datetime.now(timezone.utc)
                )

        except httpx.TimeoutException:
            logger.warning(f"Proxy test timeout: {proxy_id}")
            await self._mark_proxy_failed(proxy_id)
            return ProxyServerTestResponse(
                success=True,
                is_working=False,
                error="Connection timeout",
                test_url=test_url,
                tested_at=datetime.now(timezone.utc)
            )
            
        except httpx.ProxyError as e:
            logger.warning(f"Proxy connection error: {proxy_id}, {e}")
            await self._mark_proxy_failed(proxy_id)
            return ProxyServerTestResponse(
                success=True,
                is_working=False,
                error=f"Proxy connection error: {str(e)}",
                test_url=test_url,
                tested_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Proxy test failed: {proxy_id}, {type(e).__name__}: {e}")
            await self._mark_proxy_failed(proxy_id)
            return ProxyServerTestResponse(
                success=True,
                is_working=False,
                error=f"{type(e).__name__}: {str(e)}",
                test_url=test_url,
                tested_at=datetime.now(timezone.utc)
            )

    async def _mark_proxy_failed(self, proxy_id):
        """Отметить прокси как нерабочий."""
        proxy = await self.get(proxy_id)
        if proxy:
            proxy.is_working = False
            proxy.last_checked_at = datetime.now(timezone.utc)
            await self.db.commit()

    async def get_active_proxy_for_usage(
        self,
        usage_type: str
    ) -> Optional[ProxyServer]:
        """
        Получить активный рабочий прокси для указанного типа использования.
        
        Если есть несколько, возвращает первый рабочий.
        """
        query = select(ProxyServer).where(
            ProxyServer.is_active == True,
            ProxyServer.usage_type == usage_type,
            ProxyServer.is_working == True
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_proxy_connection_url(self, proxy_id) -> Optional[str]:
        """Получить URL подключения для прокси."""
        proxy = await self.get(proxy_id)
        if proxy:
            return proxy.connection_url
        return None
