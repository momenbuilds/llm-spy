"""Tiny OpenAI-compatible fake provider for the llm-spy zero-key demo.

Run in terminal 1:
    python examples/fake_openai_provider.py
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class FakeOpenAIProvider(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        request = json.loads(self.rfile.read(length) or b"{}")
        user_text = " ".join(
            str(message.get("content", ""))
            for message in request.get("messages", [])
            if message.get("role") == "user"
        )
        body = {
            "id": "chatcmpl_llm_spy_demo",
            "object": "chat.completion",
            "model": request.get("model", "fake-openai-compatible-model"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Fake provider saw: {user_text or 'an empty prompt'}",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 9, "total_tokens": 21},
        }
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    host, port = "127.0.0.1", 8000
    print(f"Fake OpenAI-compatible provider listening on http://{host}:{port}/v1")
    try:
        HTTPServer((host, port), FakeOpenAIProvider).serve_forever()
    except KeyboardInterrupt:
        print("\nFake provider stopped.")


if __name__ == "__main__":
    main()
