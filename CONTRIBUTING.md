# Contributing to llm-spy

Thanks for helping make local-first AI debugging better.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m ruff format .
```

## Add a Provider Parser

1. Add `src/llmspy/parsers/<provider>.py`.
2. Subclass `ProviderParser`.
3. Implement `can_handle`, `parse_request`, and `parse_response`.
4. Register it in `src/llmspy/parsers/registry.py`.
5. Add parser tests under `tests/`.
6. Add pricing data in `src/llmspy/pricing.py` when public pricing is known.
7. Update `docs/providers.md`.

Parsers must never crash the proxy. Store raw data and return a clear parser error when something unexpected appears.

## Docs

Keep docs honest. If a feature is best-effort or experimental, say so. Do not add fake provider support claims, fake users, fake metrics, or fake screenshots.

## Pull Requests

Use small focused PRs, include tests, run formatting, and explain user-visible behavior. Commit messages should be concise imperative phrases such as `Add Gemini parser tests`.
