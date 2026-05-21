from __future__ import annotations

from typing import Any

from llmspy.parsers.openai_compatible import OpenAICompatibleParser


class TogetherParser(OpenAICompatibleParser):
    provider = "together"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return "api.together.xyz" in host
