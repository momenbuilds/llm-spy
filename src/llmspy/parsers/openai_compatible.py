from __future__ import annotations

from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedRequest, ParsedResponse, TokenUsage
from llmspy.parsers.base import ProviderParser
from llmspy.utils import safe_json_loads


class OpenAICompatibleParser(ProviderParser):
    provider = "openai-compatible"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        body = request_body if isinstance(request_body, dict) else safe_json_loads(request_body)
        return (
            isinstance(body, dict) and ("messages" in body or "prompt" in body) and "model" in body
        )

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        body = safe_json_loads(exchange.request_body) or {}
        messages = body.get("messages") or (
            [{"role": "user", "content": body.get("prompt")}] if body.get("prompt") else []
        )
        system = (
            "\n".join(str(m.get("content", "")) for m in messages if m.get("role") == "system")
            or None
        )
        params = {
            k: v
            for k, v in body.items()
            if k not in {"messages", "prompt", "model", "tools", "functions"}
        }
        tools = body.get("tools") or body.get("functions") or []
        return ParsedRequest(
            provider=self.provider,
            model=body.get("model"),
            endpoint=exchange.path,
            system_prompt=system,
            messages=messages,
            parameters=params,
            tools=tools,
            raw_request=body,
        )

    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        body = safe_json_loads(exchange.response_body)
        if not isinstance(body, dict):
            return ParsedResponse(raw_response=body, response_content=str(body) if body else None)
        content = None
        finish = None
        choices = body.get("choices") or []
        if choices:
            first = choices[0]
            finish = first.get("finish_reason")
            msg = first.get("message") or {}
            content = msg.get("content") or first.get("text") or body.get("response")
        content = content or body.get("output_text") or body.get("response")
        usage = body.get("usage") or {}
        return ParsedResponse(
            response_content=content,
            finish_reason=finish,
            raw_response=body,
            usage=TokenUsage(
                prompt_tokens=usage.get("prompt_tokens") or usage.get("input_tokens"),
                completion_tokens=usage.get("completion_tokens") or usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
            ),
            error=(body.get("error") or {}).get("message")
            if isinstance(body.get("error"), dict)
            else body.get("error"),
        )
