"""
Сервис для управления настройками приложения.
"""
import json
from typing import Optional, List, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.settings import AppSetting

logger = structlog.get_logger(__name__)


class AppSettingService:
    """Сервис для управления настройками приложения."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, key: str) -> Optional[AppSetting]:
        """Получение настройки по ключу."""
        result = await self.db.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        return result.scalar_one_or_none()

    async def get_value(self, key: str, default: Any = None) -> Any:
        """
        Получение значения настройки.

        Автоматически конвертирует значение в нужный тип.
        """
        setting = await self.get(key)
        if not setting:
            return default

        return self._deserialize_value(setting.value, setting.value_type, default)

    async def set_value(
        self,
        key: str,
        value: Any,
        value_type: str = "string",
        description: Optional[str] = None
    ) -> AppSetting:
        """
        Установка значения настройки.

        Поддерживаемые типы: string, int, float, bool, json
        """
        setting = await self.get(key)

        if not setting:
            setting = AppSetting(
                key=key,
                value=self._serialize_value(value, value_type),
                value_type=value_type,
                description=description,
            )
            self.db.add(setting)
            logger.info(f"Created setting: {key}")
        else:
            setting.value = self._serialize_value(value, value_type)
            setting.value_type = value_type
            if description:
                setting.description = description
            logger.info(f"Updated setting: {key}")

        await self.db.commit()
        await self.db.refresh(setting)
        return setting

    async def get_all(self) -> List[AppSetting]:
        """Получение всех настроек."""
        result = await self.db.execute(
            select(AppSetting).order_by(AppSetting.key)
        )
        return list(result.scalars().all())

    async def delete(self, key: str) -> bool:
        """Удаление настройки."""
        setting = await self.get(key)
        if not setting:
            return False

        await self.db.delete(setting)
        await self.db.commit()
        logger.info(f"Deleted setting: {key}")
        return True

    def _serialize_value(self, value: Any, value_type: str) -> str:
        """Сериализация значения в строку."""
        if value is None:
            return ""

        if value_type == "json":
            return json.dumps(value)
        elif value_type == "bool":
            return "true" if value else "false"
        else:
            return str(value)

    def _deserialize_value(self, value: str, value_type: str, default: Any = None) -> Any:
        """Десериализация строки в нужное значение."""
        if not value:
            return default

        try:
            if value_type == "int":
                return int(value)
            elif value_type == "float":
                return float(value)
            elif value_type == "bool":
                return value.lower() in ("true", "1", "yes")
            elif value_type == "json":
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            logger.warning(f"Failed to deserialize setting value: {value}, type: {value_type}")
            return default

    # ===== Convenience методы для конкретных настроек =====

    async def get_security_settings(self) -> dict:
        """Получение настроек безопасности."""
        return {
            "proxy_enabled": await self.get_value("security.proxy_enabled", False),
            "default_proxy_id": await self.get_value("security.default_proxy_id", None),
            "check_interval_seconds": await self.get_value("security.check_interval_seconds", 300),
            "detect_malicious_links": await self.get_value("security.detect_malicious_links", True),
            "detect_redirects": await self.get_value("security.detect_redirects", True),
            "detect_iframes": await self.get_value("security.detect_iframes", True),
        }

    async def set_security_settings(self, settings: dict):
        """Установка настроек безопасности."""
        for key, value in settings.items():
            await self.set_value(f"security.{key}", value, value_type=type(value).__name__)
