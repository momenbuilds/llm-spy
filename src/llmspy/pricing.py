from __future__ import annotations

import os

import httpx

from llmspy.config import DEFAULT_PRICING_URL
from llmspy.models import ParsedCall, PricingEntry
from llmspy.storage import Storage
from llmspy.utils import estimate_tokens

BUNDLED_PRICING: dict[tuple[str, str], tuple[float, float]] = {
    ("openai", "gpt-4o"): (0.005, 0.015),
    ("openai", "gpt-4o-mini"): (0.00015, 0.0006),
    ("openai", "gpt-4.1"): (0.002, 0.008),
    ("openai", "gpt-4.1-mini"): (0.0004, 0.0016),
    ("openai", "gpt-4.1-nano"): (0.0001, 0.0004),
    ("openai", "o3"): (0.01, 0.04),
    ("openai", "o4-mini"): (0.0011, 0.0044),
    ("anthropic", "claude-3-5-sonnet"): (0.003, 0.015),
    ("anthropic", "claude-3-5-haiku"): (0.0008, 0.004),
    ("anthropic", "claude-3-7-sonnet"): (0.003, 0.015),
    ("anthropic", "claude-sonnet-4"): (0.003, 0.015),
    ("anthropic", "claude-opus-4"): (0.015, 0.075),
    ("gemini", "gemini-1.5-pro"): (0.00125, 0.005),
    ("gemini", "gemini-1.5-flash"): (0.000075, 0.0003),
    ("gemini", "gemini-2.0-flash"): (0.0001, 0.0004),
    ("gemini", "gemini-2.5-pro"): (0.00125, 0.01),
    ("mistral", "mistral-large-latest"): (0.002, 0.006),
    ("mistral", "mistral-small-latest"): (0.0002, 0.0006),
    ("ollama", "*"): (0.0, 0.0),
}


def lookup_pricing(
    provider: str, model: str | None, storage: Storage | None = None
) -> PricingEntry | None:
    if not model:
        return None
    if storage:
        cached = storage.get_pricing(provider, model)
        if cached:
            return cached
    if provider == "ollama":
        return PricingEntry(
            provider=provider, model=model, input_cost_per_1k=0, output_cost_per_1k=0
        )
    for (p, m), costs in BUNDLED_PRICING.items():
        if p == provider and (m == model or m in model):
            return PricingEntry(
                provider=provider,
                model=model,
                input_cost_per_1k=costs[0],
                output_cost_per_1k=costs[1],
            )
    if provider == "openai-compatible":
        for (p, m), costs in BUNDLED_PRICING.items():
            if p == "openai" and (m == model or m in model):
                return PricingEntry(
                    provider=provider,
                    model=model,
                    input_cost_per_1k=costs[0],
                    output_cost_per_1k=costs[1],
                )
    return None


def apply_pricing(call: ParsedCall, storage: Storage | None = None) -> ParsedCall:
    if call.prompt_tokens is None or call.completion_tokens is None:
        input_text = (
            (call.system_prompt or "")
            + " "
            + " ".join(str(m.get("content", "")) for m in call.messages)
        )
        output_text = call.response_content or ""
        call.prompt_tokens = (
            call.prompt_tokens if call.prompt_tokens is not None else estimate_tokens(input_text)
        )
        call.completion_tokens = (
            call.completion_tokens
            if call.completion_tokens is not None
            else estimate_tokens(output_text)
        )
        call.total_tokens = call.total_tokens or call.prompt_tokens + call.completion_tokens
        call.estimated_tokens = True
    pricing = lookup_pricing(call.provider, call.model, storage)
    if not pricing:
        usage = call.raw_response.get("usage", {}) if isinstance(call.raw_response, dict) else {}
        if isinstance(usage, dict) and usage.get("cost") is not None:
            call.total_cost_usd = round(float(usage["cost"]), 8)
            cost_details = usage.get("cost_details") or {}
            if isinstance(cost_details, dict):
                call.input_cost_usd = _optional_float(
                    cost_details.get("upstream_inference_prompt_cost")
                )
                call.output_cost_usd = _optional_float(
                    cost_details.get("upstream_inference_completions_cost")
                )
            return call
        call.input_cost_usd = None
        call.output_cost_usd = None
        call.total_cost_usd = None
        return call
    call.input_cost_usd = round((call.prompt_tokens or 0) / 1000 * pricing.input_cost_per_1k, 8)
    call.output_cost_usd = round(
        (call.completion_tokens or 0) / 1000 * pricing.output_cost_per_1k, 8
    )
    call.total_cost_usd = round(call.input_cost_usd + call.output_cost_usd, 8)
    return call


def _optional_float(value) -> float | None:
    return round(float(value), 8) if value is not None else None


def update_pricing(storage: Storage, url: str | None = None) -> tuple[bool, str]:
    url = url or os.getenv("LLM_SPY_PRICING_URL", DEFAULT_PRICING_URL)
    try:
        data = httpx.get(url, timeout=10).json()
        entries = [
            PricingEntry(**item)
            for item in data.get("pricing", data if isinstance(data, list) else [])
        ]
        storage.update_pricing_cache(entries)
        return True, f"updated {len(entries)} pricing entries"
    except Exception as exc:
        return False, f"pricing update failed; using bundled pricing ({exc})"
