from __future__ import annotations

from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedRequest, ParsedResponse, TokenUsage
from llmspy.parsers.base import ProviderParser
from llmspy.utils import safe_json_loads


class OllamaParser(ProviderParser):
    provider = "ollama"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return (
            "localhost" in host
            and path.startswith("/api/")
            or path.startswith("/api/chat")
            or path.startswith("/api/generate")
        )

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        body = safe_json_loads(exchange.request_body) or {}
        messages = body.get("messages") or (
            [{"role": "user", "content": body.get("prompt")}] if body.get("prompt") else []
        )
        return ParsedRequest(
            provider=self.provider,
            model=body.get("model"),
            endpoint=exchange.path,
            messages=messages,
            parameters={k: v for k, v in body.items() if k not in {"model", "messages", "prompt"}},
            raw_request=body,
        )

    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        body = safe_json_loads(exchange.response_body)
        content = None
        if isinstance(body, dict):
            content = body.get("response") or (body.get("message") or {}).get("content")
            return ParsedResponse(
                response_content=content,
                raw_response=body,
                usage=TokenUsage(
                    prompt_tokens=body.get("prompt_eval_count"),
                    completion_tokens=body.get("eval_count"),
                    total_tokens=(body.get("prompt_eval_count") or 0)
                    + (body.get("eval_count") or 0)
                    if body.get("eval_count")
                    else None,
                ),
            )
        return ParsedResponse(raw_response=body, response_content=str(body) if body else None)
