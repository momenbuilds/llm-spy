from __future__ import annotations

from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedRequest
from llmspy.parsers.openai_compatible import OpenAICompatibleParser
from llmspy.utils import safe_json_loads


class OpenAIParser(OpenAICompatibleParser):
    provider = "openai"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return "api.openai.com" in host or path.startswith("/v1/responses")

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        body = safe_json_loads(exchange.request_body) or {}
        if exchange.path.startswith("/v1/responses"):
            messages = []
            input_value = body.get("input")
            if isinstance(input_value, str):
                messages.append({"role": "user", "content": input_value})
            elif isinstance(input_value, list):
                for item in input_value:
                    if isinstance(item, dict):
                        messages.append(
                            {
                                "role": item.get("role", "user"),
                                "content": item.get("content") or item.get("text") or "",
                            }
                        )
            return ParsedRequest(
                provider=self.provider,
                model=body.get("model"),
                endpoint=exchange.path,
                system_prompt=body.get("instructions"),
                messages=messages,
                parameters={
                    k: v
                    for k, v in body.items()
                    if k not in {"model", "instructions", "input", "tools"}
                },
                tools=body.get("tools") or [],
                raw_request=body,
            )
        return super().parse_request(exchange)

    def parse_response(self, exchange):
        parsed = super().parse_response(exchange)
        body = parsed.raw_response
        if isinstance(body, dict) and not parsed.response_content and "output" in body:
            chunks = []
            for item in body.get("output", []):
                for content in item.get("content", []):
                    if isinstance(content, dict) and "text" in content:
                        chunks.append(content["text"])
            parsed.response_content = "\n".join(chunks) or None
        return parsed
