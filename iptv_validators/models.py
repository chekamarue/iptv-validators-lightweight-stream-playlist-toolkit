from enum import StrEnum

from pydantic import BaseModel, Field


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEAD = "dead"
    TIMEOUT = "timeout"
    HTTP_ERROR = "http_error"
    INVALID = "invalid"
    NOT_MEDIA = "not_media"
    AUTH_REQUIRED = "auth_required"
    RATE_LIMITED = "rate_limited"
    NETWORK_ERROR = "network_error"


class ProbeResult(BaseModel):
    url: str
    status_code: int | None = None
    final_url: str | None = None
    content_type: str | None = None
    ttfb_ms: float | None = None
    total_time_ms: float | None = None
    response_size: int | None = None
    error_category: HealthStatus | None = None
    health_status: HealthStatus


class M3UEntry(BaseModel):
    channel_name: str | None = None
    stream_url: str
    tvg_id: str | None = None
    tvg_name: str | None = None
    tvg_logo: str | None = None
    group_title: str | None = None
    extra_attributes: dict[str, str] = Field(default_factory=dict)


class AuditSummary(BaseModel):
    total: int
    healthy: int
    dead: int
    timeout: int
    http_error: int
    invalid: int
    not_media: int
    auth_required: int
    rate_limited: int
    network_error: int
    p50_ttfb_ms: float | None = None
    p95_ttfb_ms: float | None = None
    avg_ttfb_ms: float | None = None
    min_ttfb_ms: float | None = None
    max_ttfb_ms: float | None = None


class AuditReport(BaseModel):
    summary: AuditSummary
    results: list[ProbeResult]
