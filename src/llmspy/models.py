from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    estimated_tokens: bool = False


class CostBreakdown(BaseModel):
    input_cost_usd: float | None = None
    output_cost_usd: float | None = None
    total_cost_usd: float | None = None
    pricing_known: bool = True


class SafetyFinding(BaseModel):
    type: str
    preview: str
    location: str = "unknown"
    severity: str = "medium"


class SafetyFlags(BaseModel):
    has_pii_warning: bool = False
    pii_findings: list[SafetyFinding] = Field(default_factory=list)
    has_injection_warning: bool = False
    injection_findings: list[SafetyFinding] = Field(default_factory=list)


class ProviderInfo(BaseModel):
    provider: str = "unknown"
    model: str | None = None
    endpoint: str | None = None


class CapturedHTTPExchange(BaseModel):
    method: str
    host: str
    path: str
    request_headers: dict[str, str] = Field(default_factory=dict)
    request_body: str | None = None
    response_status: int | None = None
    response_headers: dict[str, str] = Field(default_factory=dict)
    response_body: str | None = None
    latency_ms: int | None = None
    error: str | None = None


class ParsedRequest(BaseModel):
    provider: str = "unknown"
    model: str | None = None
    endpoint: str | None = None
    system_prompt: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    tools: list[dict[str, Any]] = Field(default_factory=list)
    raw_request: Any = None


class ParsedResponse(BaseModel):
    response_content: str | None = None
    finish_reason: str | None = None
    raw_response: Any = None
    usage: TokenUsage = Field(default_factory=TokenUsage)
    error: str | None = None


class ParsedCall(BaseModel):
    id: str = Field(default_factory=lambda: new_id("call"))
    session_id: str | None = None
    parent_call_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: str = "unknown"
    model: str | None = None
    endpoint: str | None = None
    method: str | None = None
    status_code: int | None = None
    system_prompt: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    tools: list[dict[str, Any]] = Field(default_factory=list)
    raw_request: Any = None
    response_content: str | None = None
    finish_reason: str | None = None
    raw_response: Any = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    estimated_tokens: bool = False
    input_cost_usd: float | None = None
    output_cost_usd: float | None = None
    total_cost_usd: float | None = None
    latency_ms: int | None = None
    has_pii_warning: bool = False
    pii_findings: list[dict[str, Any]] = Field(default_factory=list)
    has_injection_warning: bool = False
    injection_findings: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class Session(BaseModel):
    id: str = Field(default_factory=lambda: new_id("session"))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BudgetSettings(BaseModel):
    daily: float | None = None


class ReplayOptions(BaseModel):
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class DiffResult(BaseModel):
    call_a: str
    call_b: str
    differences: dict[str, Any]


class PricingEntry(BaseModel):
    provider: str
    model: str
    input_cost_per_1k: float
    output_cost_per_1k: float


class ConfigEntry(BaseModel):
    key: str
    value: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
