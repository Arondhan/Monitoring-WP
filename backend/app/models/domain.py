import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    DateTime,
    ForeignKey,
    Text,
    Index,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base, is_sqlite


# Функция для генерации UUID строки
def generate_uuid():
    return str(uuid.uuid4())


class Domain(Base):
    """Модель домена для мониторинга"""

    __tablename__ = "domains"

    # Для SQLite используем String, для PostgreSQL - UUID
    if is_sqlite:
        id = Column(String(36), primary_key=True, default=generate_uuid)
    else:
        id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    url = Column(String(2048), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    check_interval_seconds = Column(Integer, default=60, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Кэшированные данные для быстрого отображения
    last_status = Column(String(50), default="PENDING")  # UP, DOWN, SLOW, SSL_ERROR, PENDING
    last_response_time_ms = Column(Integer, nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    uptime_percentage_24h = Column(Integer, default=100)  # В процентах (0-100)
    uptime_percentage_7d = Column(Integer, default=100)

    # WordPress-детекция (мониторинг)
    is_wordpress = Column(Integer, default=0)  # 0 = false, 1 = true (для совместимости с SQLite)
    last_post_date = Column(DateTime(timezone=True), nullable=True)
    last_post_title = Column(String(500), nullable=True)
    last_post_checked_at = Column(DateTime(timezone=True), nullable=True)
    wordpress_version = Column(String(50), nullable=True)

    # Связи
    checks = relationship("Check", back_populates="domain", cascade="all, delete-orphan", lazy="select")
    incidents = relationship("Incident", back_populates="domain", cascade="all, delete-orphan", lazy="select")

    __table_args__ = (
        Index("ix_domains_last_status", "last_status"),
        Index("ix_domains_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Domain(id={self.id}, url={self.url}, status={self.last_status})>"


class Check(Base):
    """Модель результата проверки домена"""

    __tablename__ = "checks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Для SQLite используем String, для PostgreSQL - UUID
    if is_sqlite:
        domain_id = Column(String(36), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    else:
        domain_id = Column(PG_UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Результаты проверки
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False)  # UP, DOWN, SLOW, SSL_ERROR
    error_message = Column(Text, nullable=True)

    # Дополнительная информация
    ssl_expires_at = Column(DateTime(timezone=True), nullable=True)
    ssl_days_remaining = Column(Integer, nullable=True)
    content_match = Column(String(255), nullable=True)  # Ключевое слово для проверки контента

    # Связи
    domain = relationship("Domain", back_populates="checks")

    __table_args__ = (
        Index("ix_checks_domain_timestamp", "domain_id", "timestamp"),
        Index("ix_checks_status", "status"),
    )

    def __repr__(self):
        return f"<Check(id={self.id}, domain_id={self.domain_id}, status={self.status}, response_time={self.response_time_ms}ms)>"


class Incident(Base):
    """Модель инцидента (простой домена)"""

    __tablename__ = "incidents"

    # Для SQLite используем String, для PostgreSQL - UUID
    if is_sqlite:
        id = Column(String(36), primary_key=True, default=generate_uuid)
        domain_id = Column(String(36), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    else:
        id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        domain_id = Column(PG_UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)

    # Временные метки
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)

    # Информация об инциденте
    reason = Column(String(100), nullable=False)  # TIMEOUT, 503_ERROR, SSL_ERROR, CONNECTION_ERROR
    severity = Column(String(20), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    error_details = Column(Text, nullable=True)

    # Длительность в секундах (вычисляется при закрытии инцидента)
    duration_seconds = Column(Integer, nullable=True)

    # Статус
    is_resolved = Column(Integer, default=0)  # 0 = active, 1 = resolved

    # Связи
    domain = relationship("Domain", back_populates="incidents")

    __table_args__ = (
        Index("ix_incidents_domain_status", "domain_id", "is_resolved"),
        Index("ix_incidents_start_time", "start_time"),
    )

    def __repr__(self):
        return f"<Incident(id={self.id}, domain_id={self.domain_id}, reason={self.reason}, resolved={self.is_resolved})>"
