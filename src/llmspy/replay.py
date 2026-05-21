from __future__ import annotations

import os

import httpx

from llmspy.models import CapturedHTTPExchange, ReplayOptions
from llmspy.proxy import normalize_exchange
from llmspy.storage import Storage
from llmspy.utils import safe_json_dumps

API_KEYS = {
    "openai": ("OPENAI_API_KEY", "https://api.openai.com"),
    "anthropic": ("ANTHROPIC_API_KEY", "https://api.anthropic.com"),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com"),
    "mistral": ("MISTRAL_API_KEY", "https://api.mistral.ai"),
    "cohere": ("COHERE_API_KEY", "https://api.cohere.ai"),
    "together": ("TOGETHER_API_KEY", "https://api.together.xyz"),
}


def replay_call(storage: Storage, call_id: str, options: ReplayOptions) -> tuple[bool, str]:
    call = storage.get_call(call_id)
    if not call:
        return False, f"call not found: {call_id}"
    if call.provider not in API_KEYS:
        return False, f"replay is not implemented for provider {call.provider}"
    env_name, base_url = API_KEYS[call.provider]
    api_key = os.getenv(env_name)
    if not api_key:
        return (
            False,
            f"missing {env_name}; llm-spy never stores API keys, so set it in the environment",
        )
    body = call.raw_request if isinstance(call.raw_request, dict) else {}
    if options.model:
        body["model"] = options.model
    if options.temperature is not None:
        body["temperature"] = options.temperature
    if options.max_tokens is not None:
        body["max_tokens"] = options.max_tokens
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if call.provider == "anthropic":
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
    url = base_url + (call.endpoint or "")
    response = httpx.post(url, json=body, headers=headers, timeout=120)
    exchange = CapturedHTTPExchange(
        method="POST",
        host=httpx.URL(url).host or "",
        path=call.endpoint or "",
        request_body=safe_json_dumps(body),
        response_status=response.status_code,
        response_body=response.text,
        latency_ms=int(response.elapsed.total_seconds() * 1000),
    )
    replayed = normalize_exchange(exchange, call.session_id, storage)
    replayed.parent_call_id = call.id
    storage.insert_call(replayed)
    return True, f"replayed as {replayed.id}"
