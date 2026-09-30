"""
Pydantic схемы для настроек и прокси.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_serializer


# ===== Proxy Server Schemas =====

class ProxyServerBase(BaseModel):
    """Базовая схема прокси сервера."""
    name: str = Field(..., min_length=1, max_length=255, description="Название прокси")
    description: Optional[str] = Field(None, max_length=1000, description="Описание")
    host: str = Field(..., min_length=1, max_length=255, description="Хост прокси")
    port: int = Field(..., ge=1, le=65535, description="Порт прокси")
    username: Optional[str] = Field(None, max_length=255, description="Логин (опционально)")
    password: Optional[str] = Field(None, max_length=255, description="Пароль (опционально)")
    protocol: str = Field(default="http", description="Протокол: http, https, socks5")
    usage_type: str = Field(default="security", description="Тип использования")
    country: Optional[str] = Field(None, max_length=50, description="Страна")


class ProxyServerCreate(ProxyServerBase):
    """Схема для создания прокси сервера."""
    pass


class ProxyServerUpdate(BaseModel):
    """Схема для обновления прокси сервера."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)
    protocol: Optional[str] = None
    usage_type: Optional[str] = None
    country: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ProxyServerResponse(ProxyServerBase):
    """Схема ответа прокси сервера."""
    model_config = ConfigDict(from_attributes=True)

    id: Any
    is_active: bool = True
    is_working: Optional[bool] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    connection_url: str  # URL для подключения

    @field_serializer('id')
    def serialize_id(self, value):
        return str(value)


class ProxyServerListResponse(BaseModel):
    """Схема списка прокси серверов."""
    items: List[ProxyServerResponse]
    total: int
    active_count: int
    working_count: int


class ProxyServerTestRequest(BaseModel):
    """Схема для теста прокси."""
    test_url: str = Field(default="https://www.google.com", description="URL для теста")
    timeout: int = Field(default=10, ge=1, le=60, description="Таймаут в секундах")


class ProxyServerTestResponse(BaseModel):
    """Схема результата теста прокси."""
    success: bool
    is_working: bool
    response_time_ms: Optional[int] = None
    error: Optional[str] = None
    test_url: str
    tested_at: datetime


# ===== App Setting Schemas =====

class AppSettingBase(BaseModel):
    """Базовая схема настройки."""
    key: str = Field(..., min_length=1, max_length=255, description="Ключ настройки")
    value: Optional[str] = Field(None, description="Значение настройки")
    value_type: str = Field(default="string", description="Тип значения")
    description: Optional[str] = Field(None, max_length=1000, description="Описание")


class AppSettingCreate(AppSettingBase):
    """Схема для создания настройки."""
    pass


class AppSettingUpdate(BaseModel):
    """Схема для обновления настройки."""
    value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)


class AppSettingResponse(AppSettingBase):
    """Схема ответа настройки."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: Optional[datetime] = None

    @field_serializer('id')
    def serialize_id(self, value):
        return str(value)


class AppSettingListResponse(BaseModel):
    """Схема списка настроек."""
    items: List[AppSettingResponse]
    total: int


# ===== Settings Group Schemas =====

class SecuritySettings(BaseModel):
    """Настройки безопасности."""
    proxy_enabled: bool = False
    default_proxy_id: Optional[str] = None
    check_interval_seconds: int = 300  # 5 минут
    detect_malicious_links: bool = True
    detect_redirects: bool = True
    detect_iframes: bool = True


class SettingsDashboardResponse(BaseModel):
    """Сводка настроек дашборда."""
    total_proxies: int = 0
    active_proxies: int = 0
    working_proxies: int = 0
    security_settings: SecuritySettings
