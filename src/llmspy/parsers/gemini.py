from __future__ import annotations

from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedRequest, ParsedResponse, TokenUsage
from llmspy.parsers.base import ProviderParser
from llmspy.utils import safe_json_loads


class GeminiParser(ProviderParser):
    provider = "gemini"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return "generativelanguage.googleapis.com" in host or ":generateContent" in path

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        body = safe_json_loads(exchange.request_body) or {}
        model = (
            exchange.path.split("/models/")[-1].split(":")[0]
            if "/models/" in exchange.path
            else body.get("model")
        )
        messages = []
        for content in body.get("contents", []):
            text = " ".join(
                part.get("text", "") for part in content.get("parts", []) if isinstance(part, dict)
            )
            messages.append({"role": content.get("role", "user"), "content": text})
        system = body.get("systemInstruction", {})
        system_text = (
            " ".join(p.get("text", "") for p in system.get("parts", []) if isinstance(p, dict))
            if isinstance(system, dict)
            else None
        )
        return ParsedRequest(
            provider=self.provider,
            model=model,
            endpoint=exchange.path,
            system_prompt=system_text,
            messages=messages,
            parameters={
                k: v for k, v in body.items() if k not in {"contents", "systemInstruction"}
            },
            raw_request=body,
        )

    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        body = safe_json_loads(exchange.response_body)
        text = []
        if isinstance(body, dict):
            for cand in body.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    if "text" in part:
                        text.append(part["text"])
            usage = body.get("usageMetadata") or {}
            return ParsedResponse(
                response_content="\n".join(text) or None,
                finish_reason=(body.get("candidates") or [{}])[0].get("finishReason")
                if body.get("candidates")
                else None,
                raw_response=body,
                usage=TokenUsage(
                    prompt_tokens=usage.get("promptTokenCount"),
                    completion_tokens=usage.get("candidatesTokenCount"),
                    total_tokens=usage.get("totalTokenCount"),
                ),
            )
        return ParsedResponse(raw_response=body, response_content=str(body) if body else None)
