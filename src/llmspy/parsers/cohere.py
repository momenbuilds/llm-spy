from __future__ import annotations

from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedRequest, ParsedResponse, TokenUsage
from llmspy.parsers.base import ProviderParser
from llmspy.utils import safe_json_loads


class CohereParser(ProviderParser):
    provider = "cohere"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return "api.cohere.ai" in host

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        body = safe_json_loads(exchange.request_body) or {}
        messages = body.get("messages") or (
            [{"role": "user", "content": body.get("message")}] if body.get("message") else []
        )
        return ParsedRequest(
            provider=self.provider,
            model=body.get("model"),
            endpoint=exchange.path,
            messages=messages,
            raw_request=body,
        )

    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        body = safe_json_loads(exchange.response_body)
        text = body.get("text") if isinstance(body, dict) else None
        usage = (body.get("meta") or {}).get("billed_units", {}) if isinstance(body, dict) else {}
        return ParsedResponse(
            response_content=text,
            raw_response=body,
            usage=TokenUsage(
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
            ),
        )
