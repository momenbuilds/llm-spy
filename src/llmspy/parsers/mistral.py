from __future__ import annotations

from typing import Any

from llmspy.parsers.openai_compatible import OpenAICompatibleParser


class MistralParser(OpenAICompatibleParser):
    provider = "mistral"

    def can_handle(self, host: str, path: str, request_body: Any, response_body: Any) -> bool:
        return "api.mistral.ai" in host
