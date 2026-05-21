from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from llmspy.models import CapturedHTTPExchange, ParsedCall, ParsedRequest, ParsedResponse
from llmspy.utils import safe_json_loads


class ProviderParser(ABC):
    provider = "unknown"

    @abstractmethod
    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        raise NotImplementedError

    def normalize(self, exchange: CapturedHTTPExchange) -> ParsedCall:
        try:
            req = self.parse_request(exchange)
            res = self.parse_response(exchange)
            return ParsedCall(
                provider=req.provider,
                model=req.model,
                endpoint=req.endpoint or exchange.path,
                method=exchange.method,
                status_code=exchange.response_status,
                system_prompt=req.system_prompt,
                messages=req.messages,
                parameters=req.parameters,
                tools=req.tools,
                raw_request=req.raw_request,
                response_content=res.response_content,
                finish_reason=res.finish_reason,
                raw_response=res.raw_response,
                prompt_tokens=res.usage.prompt_tokens,
                completion_tokens=res.usage.completion_tokens,
                total_tokens=res.usage.total_tokens,
                estimated_tokens=res.usage.estimated_tokens,
                latency_ms=exchange.latency_ms,
                error=res.error or exchange.error,
            )
        except Exception as exc:
            return ParsedCall(
                provider=self.provider,
                endpoint=exchange.path,
                method=exchange.method,
                status_code=exchange.response_status,
                raw_request=safe_json_loads(exchange.request_body),
                raw_response=safe_json_loads(exchange.response_body),
                latency_ms=exchange.latency_ms,
                error=f"parser error: {exc}",
            )


class UnknownParser(ProviderParser):
    provider = "unknown"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return True

    def parse_request(self, exchange: CapturedHTTPExchange) -> ParsedRequest:
        return ParsedRequest(
            provider="unknown",
            endpoint=exchange.path,
            raw_request=safe_json_loads(exchange.request_body),
        )

    def parse_response(self, exchange: CapturedHTTPExchange) -> ParsedResponse:
        body = safe_json_loads(exchange.response_body)
        return ParsedResponse(
            raw_response=body, response_content=body if isinstance(body, str) else None
        )
