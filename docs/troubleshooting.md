# Troubleshooting

HTTPS certificate issues: visit `http://mitm.it` through the proxy and trust the mitmproxy CA. llm-spy can inspect HTTPS request/response bodies only after the client trusts that CA. Without trust, HTTPS body inspection fails at the TLS layer.

Proxy not capturing: ensure both `HTTPS_PROXY` and `HTTP_PROXY` point to `http://localhost:8080`. For local HTTP demos, also clear `NO_PROXY` if your shell or HTTP client bypasses localhost.

SDK ignores proxy: some clients override transports. Use SDK mode experimentally or configure the client transport.

Windows/macOS/Linux: proxy environment variable syntax and certificate trust stores differ by platform. When in doubt, start with the no-API-key fake provider demo because it uses plain local HTTP and avoids certificate setup.

Ollama: local calls should be routed through `HTTP_PROXY` if you want capture, or use OpenAI-compatible endpoints where available.

Port conflicts: run `llm-spy doctor` or choose another proxy port with `llm-spy start --port 18080`.

Empty history: make a provider call after the proxy starts.

Dashboard cannot connect: check `LLM_SPY_DB_PATH` and file permissions.
