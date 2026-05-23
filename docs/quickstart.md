# Quickstart

llm-spy shows the LLM API calls your app makes by sitting between your app and the provider as a local HTTP/HTTPS proxy. It prints calls in your terminal, stores them in SQLite, and serves a local dashboard.

## Try It Without An API Key

Terminal 1:

```bash
python examples/fake_openai_provider.py
```

Terminal 2:

```bash
llm-spy start --port 8080
```

Terminal 3:

```bash
HTTP_PROXY=http://localhost:8080 python examples/openai_compatible_example.py
```

Then inspect the captured call:

```bash
llm-spy history
llm-spy dashboard
```

## Install

```bash
pip install llm-spy
```

For local development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Real Provider Usage

Start the proxy:

```bash
llm-spy start
```

Run your app through it:

```bash
HTTPS_PROXY=http://localhost:8080 HTTP_PROXY=http://localhost:8080 python app.py
```

OpenAI-compatible FastAPI example without an API key:

```bash
python examples/fake_openai_provider.py
llm-spy start --port 8080
env -u NO_PROXY -u no_proxy HTTP_PROXY=http://localhost:8080 \
  uvicorn examples.fastapi_app_example:app --reload --port 8001
```

Then call `http://127.0.0.1:8001/ask` and inspect `llm-spy history` or
`llm-spy dashboard`. See [FastAPI Guide](guides/fastapi.md) for the full
walkthrough.

OpenAI example:

```bash
OPENAI_API_KEY=*** HTTPS_PROXY=http://localhost:8080 python examples/openai_example.py
```

Anthropic example:

```bash
ANTHROPIC_API_KEY=... HTTPS_PROXY=http://localhost:8080 python examples/anthropic_example.py
```

## HTTPS Setup

HTTP traffic works immediately. HTTPS body inspection requires trusting mitmproxy's local CA certificate.

1. Start `llm-spy start`.
2. Open `http://mitm.it` through the proxy.
3. Install/trust the certificate for your OS/client.
4. Re-run your app with `HTTPS_PROXY=http://localhost:8080`.

## If It Does Not Capture

Run:

```bash
llm-spy doctor
```

Common fixes:

- Make sure `HTTP_PROXY` or `HTTPS_PROXY` is set in the same shell that launches your app.
- Clear `NO_PROXY` for local demos: `env -u NO_PROXY -u no_proxy HTTP_PROXY=http://localhost:8080 python ...`.
- Trust the mitmproxy CA for HTTPS traffic.
- Use `llm-spy start --port 18080` if port 8080 is busy.
- Check `~/.llm-spy/llm-spy.db` or set `LLM_SPY_DB_PATH` if you use a custom DB.

## Export

```bash
llm-spy export --format json --output calls.json
llm-spy export --format csv --output calls.csv
```
