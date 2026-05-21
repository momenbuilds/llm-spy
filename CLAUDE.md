# CLAUDE.md - Instructions for Claude Code

## Project Context

llm-spy is a developer tool for Python developers building LLM applications.
The core design principle is: zero config, local first, works in 10 seconds.
Never compromise this in code suggestions.

## Preferred Code Style

- Type hints on public functions.
- Docstrings for public APIs when behavior is not obvious.
- Avoid raw `print()` in application code; use Rich console output or logging.
- Errors should be user-friendly, not stack traces, unless debug mode is explicit.
- Keep dependencies minimal in the core proxy.

## When Adding Features

Ask: does this require any cloud account, API key, or service signup to work?
If yes, make it optional, default off, and clearly documented.

## Running The Full Stack Locally

```bash
pip install -e ".[dev]"

# Terminal 1
python examples/fake_openai_provider.py

# Terminal 2
llm-spy start

# Terminal 3
HTTP_PROXY=http://localhost:8080 python examples/openai_compatible_example.py
llm-spy history
```

## Current Known Issues / Good Areas To Improve

- Streaming responses are not displayed token-by-token yet.
- Windows proxy setup needs deeper platform-specific documentation.
- Azure OpenAI parser is missing.
- AWS Bedrock parser is missing.
- DeepSeek parser is missing.
- Replay mode is experimental and needs hardening.
