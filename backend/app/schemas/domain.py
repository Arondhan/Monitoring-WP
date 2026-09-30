from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_serializer


# ===== Domain Schemas =====

class DomainBase(BaseModel):
    """Базовая схема домена"""
    url: HttpUrl = Field(..., description="URL для мониторинга")
    name: str = Field(..., min_length=1, max_length=255, description="Отображаемое имя домена")
    check_interval_seconds: int = Field(default=60, ge=30, le=604800, description="Интервал проверки в секундах (30 сек - 7 дней)")


class DomainCreate(DomainBase):
    """Схема для создания домена"""
    pass


class DomainUpdate(BaseModel):
    """Схема для обновления домена"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    check_interval_seconds: Optional[int] = Field(None, ge=30, le=604800)
    url: Optional[HttpUrl] = None


class DomainResponse(DomainBase):
    """Схема ответа домена"""
    model_config = ConfigDict(from_attributes=True)

    id: Any
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_status: str = "PENDING"
    last_response_time_ms: Optional[int] = None
    last_checked_at: Optional[datetime] = None
    uptime_percentage_24h: int = 100
    uptime_percentage_7d: int = 100

    # WordPress-детекция (мониторинг)
    is_wordpress: bool = False
    last_post_date: Optional[datetime] = None
    last_post_title: Optional[str] = None
    last_post_checked_at: Optional[datetime] = None
    wordpress_version: Optional[str] = None

    # Вычисляемые поля (возраст поста)
    wordpress_post_age_days: Optional[int] = None
    wordpress_post_status: Optional[str] = None  # "fresh", "warning", "stale"

    @field_serializer('id')
    def serialize_id(self, value):
        return str(value)


class DomainListResponse(BaseModel):
    """Схема списка доменов"""
    items: List[DomainResponse]
    total: int


# ===== Check Schemas =====

class CheckBase(BaseModel):
    """Базовая схема проверки"""
    status: str = Field(..., description="Статус проверки: UP, DOWN, SLOW, SSL_ERROR")
    status_code: Optional[int] = Field(None, description="HTTP статус код")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Время отклика в мс")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")


class CheckCreate(CheckBase):
    """Схема для создания проверки"""
    domain_id: Any


class CheckResponse(CheckBase):
    """Схема ответа проверки"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain_id: Any
    timestamp: datetime
    ssl_expires_at: Optional[datetime] = None
    ssl_days_remaining: Optional[int] = None

    @field_serializer('domain_id')
    def serialize_domain_id(self, value):
        return str(value)


class CheckListResponse(BaseModel):
    """Схема списка проверок"""
    items: List[CheckResponse]
    total: int
    period: str


# ===== Incident Schemas =====

class IncidentBase(BaseModel):
    """Базовая схема инцидента"""
    reason: str = Field(..., description="Причина инцидента")
    severity: str = Field(default="HIGH", description="Серьезность: LOW, MEDIUM, HIGH, CRITICAL")
    error_details: Optional[str] = None


class IncidentResponse(IncidentBase):
    """Схема ответа инцидента"""
    model_config = ConfigDict(from_attributes=True)

    id: Any
    domain_id: Any
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    is_resolved: bool

    @field_serializer('id')
    def serialize_id(self, value):
        return str(value)

    @field_serializer('domain_id')
    def serialize_domain_id(self, value):
        return str(value)


class IncidentListResponse(BaseModel):
    """Схема списка инцидентов"""
    items: List[IncidentResponse]
    total: int


# ===== Dashboard/Stats Schemas =====

class DomainStats(BaseModel):
    """Статистика домена"""
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    average_response_time_ms: Optional[float] = None
    uptime_percentage: float = 0.0
    last_downtime: Optional[datetime] = None


class StatusCount(BaseModel):
    """Количество доменов по статусам"""
    up: int = 0
    down: int = 0
    slow: int = 0
    ssl_error: int = 0
    pending: int = 0


class DashboardSummary(BaseModel):
    """Сводка дашборда"""
    total_domains: int = 0
    status_counts: StatusCount = StatusCount()
    overall_uptime: float = 0.0
    active_incidents: int = 0


# ===== WordPress Schemas (мониторинг) =====

class WordPressCheckResponse(BaseModel):
    """Схема ответа проверки WordPress"""
    model_config = ConfigDict(from_attributes=True)

    domain_id: Any
    is_wordpress: bool
    last_post_date: Optional[datetime] = None
    last_post_title: Optional[str] = None
    last_post_checked_at: Optional[datetime] = None
    wordpress_version: Optional[str] = None

    @field_serializer('domain_id')
    def serialize_domain_id(self, value):
        return str(value)


class WordPressStats(BaseModel):
    """Статистика WordPress сайтов (для дашборда)"""
    total: int = 0           # Всего WordPress сайтов
    fresh: int = 0           # < 7 дней (🟢)
    warning: int = 0         # 7-30 дней (🟡)
    stale: int = 0           # > 30 дней (🔴)
    no_posts: int = 0        # WordPress без постов


class WordPressContent(BaseModel):
    """Контент WordPress страницы (Meta + Заголовки) для SEO-мониторинга"""
    meta_title: Optional[str] = None
    meta_title_length: Optional[int] = None
    meta_description: Optional[str] = None
    meta_description_length: Optional[int] = None
    h1: Optional[str] = None
    h2: List[str] = []
