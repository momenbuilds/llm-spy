from __future__ import annotations

from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedRequest, ParsedResponse, TokenUsage
from llmspy.parsers.base import ProviderParser
from llmspy.utils import safe_json_loads


class AnthropicParser(ProviderParser):
    provider = "anthropic"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return "api.anthropic.com" in host or path.startswith("/v1/messages")

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        body = safe_json_loads(exchange.request_body) or {}
        system = body.get("system")
        if isinstance(system, list):
            system = "\n".join(str(x.get("text", x)) for x in system)
        return ParsedRequest(
            provider=self.provider,
            model=body.get("model"),
            endpoint=exchange.path,
            system_prompt=system,
            messages=body.get("messages") or [],
            parameters={
                k: v for k, v in body.items() if k not in {"system", "messages", "model", "tools"}
            },
            tools=body.get("tools") or [],
            raw_request=body,
        )

    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        body = safe_json_loads(exchange.response_body)
        if not isinstance(body, dict):
            return ParsedResponse(raw_response=body, response_content=str(body) if body else None)
        text = []
        for block in body.get("content", []):
            if block.get("type") == "text":
                text.append(block.get("text", ""))
        usage = body.get("usage") or {}
        return ParsedResponse(
            response_content="\n".join(text) or None,
            finish_reason=body.get("stop_reason"),
            raw_response=body,
            usage=TokenUsage(
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
                total_tokens=(usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)
                if usage
                else None,
            ),
            error=(body.get("error") or {}).get("message")
            if isinstance(body.get("error"), dict)
            else None,
        )
