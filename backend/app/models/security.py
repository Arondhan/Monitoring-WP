"""
Модели для проверки безопасности доменов.
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base, is_sqlite


class DomainSecurityCheck(Base):
    """
    Результат проверки безопасности домена.
    """

    __tablename__ = "domain_security_checks"

    if is_sqlite:
        id = Column(Integer, primary_key=True, autoincrement=True)
        domain_id = Column(String(36), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    else:
        id = Column(Integer, primary_key=True, autoincrement=True)
        domain_id = Column(PG_UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)

    # Временные метки
    checked_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Статус проверки
    is_safe = Column(Boolean, default=True)
    threat_level = Column(String(20), default="none")  # none, low, medium, high, critical

    # Детектированные проблемы
    has_malicious_links = Column(Boolean, default=False)
    malicious_links_count = Column(Integer, default=0)
    malicious_links_details = Column(Text, nullable=True)  # JSON список ссылок

    has_unexpected_redirects = Column(Boolean, default=False)
    redirect_chain = Column(Text, nullable=True)  # JSON цепочка редиректов

    has_suspicious_iframes = Column(Boolean, default=False)
    suspicious_iframes_count = Column(Integer, default=0)
    suspicious_iframes_details = Column(Text, nullable=True)  # JSON список iframe

    has_hidden_content = Column(Boolean, default=False)
    hidden_content_details = Column(Text, nullable=True)

    # Контент для сравнения
    html_hash = Column(String(64), nullable=True)  # SHA256 хэш HTML
    links_hash = Column(String(64), nullable=True)  # SHA256 хэш списка ссылок

    # Ошибки проверки
    error_message = Column(Text, nullable=True)
    proxy_used = Column(Boolean, default=False)

    # Связи
    domain = relationship("Domain", back_populates="security_checks")

    __table_args__ = (
        Index("ix_domain_security_checks_domain_time", "domain_id", "checked_at"),
        Index("ix_domain_security_checks_safe", "is_safe"),
        Index("ix_domain_security_checks_threat", "threat_level"),
    )

    def __repr__(self):
        return f"<DomainSecurityCheck(domain_id={self.domain_id}, safe={self.is_safe})>"


class DomainBaseline(Base):
    """
    Базовая сигнатура домена (чистое состояние).
    Используется для сравнения при проверках.
    """

    __tablename__ = "domain_baselines"

    if is_sqlite:
        id = Column(Integer, primary_key=True, autoincrement=True)
        domain_id = Column(String(36), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, unique=True)
    else:
        id = Column(Integer, primary_key=True, autoincrement=True)
        domain_id = Column(PG_UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Базовые сигнатуры
    html_hash = Column(String(64), nullable=True)
    links_hash = Column(String(64), nullable=True)
    known_links = Column(Text, nullable=True)  # JSON список известных ссылок
    known_scripts = Column(Text, nullable=True)  # JSON список известных скриптов

    # Метаданные
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Связи
    domain = relationship("Domain", backref="baseline")

    __table_args__ = (
        Index("ix_domain_baselines_domain", "domain_id"),
        Index("ix_domain_baselines_active", "is_active"),
    )

    def __repr__(self):
        return f"<DomainBaseline(domain_id={self.domain_id})>"
