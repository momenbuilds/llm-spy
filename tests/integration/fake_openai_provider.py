from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        self.rfile.read(length)
        body = (
            b'{"id":"chatcmpl_fake","object":"chat.completion","model":"gpt-4o-mini",'
            b'"choices":[{"index":0,"message":{"role":"assistant","content":"Hello from fake OpenAI"},"finish_reason":"stop"}],'
            b'"usage":{"prompt_tokens":8,"completion_tokens":5,"total_tokens":13}}'
        )
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    HTTPServer(("127.0.0.1", 19001), FakeOpenAIHandler).serve_forever()


if __name__ == "__main__":
    main()
