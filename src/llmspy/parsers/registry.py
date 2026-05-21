from __future__ import annotations

from llmspy.parsers.anthropic import AnthropicParser
from llmspy.parsers.base import ProviderParser, UnknownParser
from llmspy.parsers.cohere import CohereParser
from llmspy.parsers.gemini import GeminiParser
from llmspy.parsers.mistral import MistralParser
from llmspy.parsers.ollama import OllamaParser
from llmspy.parsers.openai import OpenAIParser
from llmspy.parsers.openai_compatible import OpenAICompatibleParser
from llmspy.parsers.together import TogetherParser
from llmspy.utils import safe_json_loads


class ParserRegistry:
    def __init__(self) -> None:
        self.parsers: list[ProviderParser] = [
            OpenAIParser(),
            AnthropicParser(),
            GeminiParser(),
            MistralParser(),
            OllamaParser(),
            CohereParser(),
            TogetherParser(),
            OpenAICompatibleParser(),
        ]
        self.unknown = UnknownParser()

    def register(self, parser: ProviderParser) -> None:
        self.parsers.insert(0, parser)

    def get_parser(self, host: str, path: str, request_body, response_body) -> ProviderParser:
        request = safe_json_loads(request_body)
        response = safe_json_loads(response_body)
        for parser in self.parsers:
            if parser.can_handle(host, path, request, response):
                return parser
        return self.unknown


registry = ParserRegistry()
