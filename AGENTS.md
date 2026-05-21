# AGENTS.md - llm-spy for AI Coding Agents

This file tells AI coding agents (Claude Code, Codex, Cursor, Windsurf, etc.) how to work with this codebase effectively.

## What This Project Does

llm-spy is a local HTTP/HTTPS proxy that intercepts LLM API calls and displays them in a terminal UI with token counts, cost estimates, and safety warnings.
No cloud, no SDK changes: just set `HTTP_PROXY` or `HTTPS_PROXY` and run.

## Architecture in 60 Seconds

```text
User app -> HTTP_PROXY / HTTPS_PROXY -> llm-spy proxy -> real LLM API
                                      |
                                      v
parsers/         detect provider, extract prompt/response
safety/          PII scan, prompt injection scan
pricing.py       token and cost calculation
storage.py       SQLite persistence
display.py       Rich terminal output
dashboard/       FastAPI local web UI
```

## How To Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## How To Run The App Locally

```bash
# Terminal 1: start fake provider, no API key needed
python examples/fake_openai_provider.py

# Terminal 2: start proxy on :8080
llm-spy start

# Terminal 3: send a request through the proxy
HTTP_PROXY=http://localhost:8080 python examples/openai_compatible_example.py
llm-spy history
llm-spy dashboard
```

## Where To Add A New Provider Parser

1. Create `src/llmspy/parsers/your_provider.py`.
2. Implement the parser interface from `src/llmspy/parsers/base.py`.
3. Register it in `src/llmspy/parsers/registry.py`.
4. Add tests in `tests/`.
5. Add verified pricing in `src/llmspy/pricing.py` if public pricing is available.
6. Update `docs/providers.md` and the README provider table.

See `src/llmspy/parsers/openai.py` as the reference implementation.

## Key Files

| File | Purpose |
| --- | --- |
| `src/llmspy/proxy.py` | Core proxy interceptor |
| `src/llmspy/parsers/` | Provider-specific request/response parsers |
| `src/llmspy/safety/` | PII and prompt injection detectors |
| `src/llmspy/storage.py` | SQLite read/write |
| `src/llmspy/display.py` | Rich terminal output |
| `src/llmspy/dashboard/` | FastAPI local web UI |
| `src/llmspy/cli.py` | Typer CLI commands |
| `src/llmspy/pricing.py` | Token and cost tables |

## Common Tasks For AI Agents

**Add Bedrock parser:**
Use `parsers/anthropic.py` and `parsers/openai_compatible.py` for shape references. Bedrock uses endpoint patterns such as `/model/{model-id}/invoke` and AWS SigV4 auth, so never store credentials.

**Add DeepSeek parser:**
DeepSeek uses an OpenAI-compatible format. Use the generic OpenAI-compatible parser as a reference and specialize host detection for `api.deepseek.com`.

**Fix a bug in cost calculation:**
See `pricing.py` for bundled pricing and cache fallback behavior. Token calculation uses provider usage fields when present and falls back to a text-length estimate.

**Add a CLI command:**
See `cli.py`. Commands use Typer and should keep empty-database behavior friendly.

## Do Not

- Add telemetry or analytics.
- Store API keys anywhere in the codebase or database.
- Add cloud dependencies to the core proxy.
- Break the zero-config local install path.
- Claim HTTPS body inspection works without mitmproxy CA trust.

## Testing Philosophy

- Unit tests for parsers give them raw request/response bodies and assert normalized fields.
- Integration tests should prefer `examples/fake_openai_provider.py`.
- No real API calls in tests.
