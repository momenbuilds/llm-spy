from __future__ import annotations

import time

from llmspy.models import CapturedHTTPExchange
from llmspy.proxy import normalize_exchange
from llmspy.storage import Storage
from llmspy.utils import safe_json_dumps


class SpyOpenAIClient:
    def __init__(self, client, storage: Storage | None = None, session_id: str | None = None):
        self.client = client
        self.storage = storage or Storage()
        self.session_id = session_id

    def chat_completions_create(self, **kwargs):
        started = time.perf_counter()
        response = self.client.chat.completions.create(**kwargs)
        body = response.model_dump() if hasattr(response, "model_dump") else response
        exchange = CapturedHTTPExchange(
            method="POST",
            host="api.openai.com",
            path="/v1/chat/completions",
            request_body=safe_json_dumps(kwargs),
            response_status=200,
            response_body=safe_json_dumps(body),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
        call = normalize_exchange(exchange, self.session_id, self.storage)
        self.storage.insert_call(call)
        return response


def spy_openai(
    client, storage: Storage | None = None, session_id: str | None = None
) -> SpyOpenAIClient:
    return SpyOpenAIClient(client, storage, session_id)
