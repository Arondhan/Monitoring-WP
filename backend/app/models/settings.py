"""
Модели для настроек приложения и прокси серверов.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.session import Base, is_sqlite


class ProxyProtocol(str, PyEnum):
    """Протоколы прокси."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class UsageType(str, PyEnum):
    """Типы использования прокси."""
    SECURITY = "security"      # Для проверки безопасности доменов
    GENERAL = "general"        # Общее использование


class ProxyServer(Base):
    """
    Модель прокси сервера.

    Используется для проверки безопасности доменов (обнаружение эксплойтов).
    """

    __tablename__ = "proxy_servers"

    if is_sqlite:
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Идентификация
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Подключение
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)  # В продакшене лучше шифровать
    protocol = Column(String(20), default="http")  # http, https, socks5

    # Статус
    is_active = Column(Boolean, default=True, index=True)
    is_working = Column(Boolean, nullable=True)  # True/False/None (не проверен)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)

    # Назначение
    usage_type = Column(String(50), default="security", index=True)

    # Метаданные
    country = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_proxy_servers_active", "is_active"),
        Index("ix_proxy_servers_usage", "usage_type"),
    )

    def __repr__(self):
        return f"<ProxyServer(id={self.id}, name={self.name}, host={self.host}:{self.port})>"

    @property
    def connection_url(self) -> str:
        """Получить URL подключения к прокси."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"


class AppSetting(Base):
    """
    Модель настроек приложения.
    
    Хранит различные настройки в формате ключ-значение.
    """

    __tablename__ = "app_settings"

    if is_sqlite:
        id = Column(Integer, primary_key=True, autoincrement=True)
    else:
        id = Column(Integer, primary_key=True, autoincrement=True)

    # Ключ настройки (уникальный)
    key = Column(String(255), nullable=False, unique=True, index=True)
    
    # Значение (текст, числа, JSON)
    value = Column(Text, nullable=True)
    
    # Тип значения для правильной десериализации
    value_type = Column(String(50), default="string")  # string, int, float, bool, json
    
    # Описание настройки
    description = Column(Text, nullable=True)
    
    # Метаданные
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_app_settings_key", "key", unique=True),
    )

    def __repr__(self):
        return f"<AppSetting(key={self.key}, value={self.value})>"
