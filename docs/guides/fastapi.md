# FastAPI Guide

This guide shows a minimal FastAPI app that sends an OpenAI-compatible chat
request through `llm-spy`. It uses the bundled fake provider, so you can copy and
paste the commands without an API key.

## 1. Start the fake provider

```bash
python examples/fake_openai_provider.py
```

The fake provider listens on `http://127.0.0.1:8000/v1` and returns a
chat-completions response in the same shape as OpenAI-compatible APIs.

## 2. Start llm-spy

In a second terminal:

```bash
llm-spy start --port 8080
```

## 3. Run the FastAPI example through the proxy

In a third terminal:

```bash
env -u NO_PROXY -u no_proxy \
  HTTP_PROXY=http://localhost:8080 \
  uvicorn examples.fastapi_app_example:app --reload --port 8001
```

The example client points at the fake provider and uses `HTTP_PROXY` so llm-spy
can capture the request before it reaches the provider.

## 4. Trigger an LLM request

```bash
curl "http://127.0.0.1:8001/ask?q=Explain%20llm-spy%20in%20one%20sentence"
```

## 5. Inspect captured calls

```bash
llm-spy history
llm-spy dashboard
```

`history` prints recent captured calls in the terminal. `dashboard` opens the
local web UI so you can inspect prompts, responses, token counts, and safety
signals.

## Using a real provider

For a real OpenAI-compatible provider, keep `llm-spy start` running and launch
your app with `HTTPS_PROXY=http://localhost:8080 HTTP_PROXY=http://localhost:8080`.
Set the provider's API key and base URL in your app as usual. HTTPS body
inspection also requires trusting the mitmproxy CA certificate; see
[HTTPS Setup](../quickstart.md#https-setup).
