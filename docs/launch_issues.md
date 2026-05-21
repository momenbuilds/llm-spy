# Launch Issues

Each issue should include title, labels, description, expected files to modify, and acceptance criteria.

1. Title: Add Bedrock provider parser. Labels: provider, good first issue. Files: `src/llmspy/parsers/`, `tests/`, `docs/providers.md`. Acceptance: Bedrock request/response fixtures parse without crashing.
2. Title: Add Azure OpenAI provider parser. Labels: provider. Files: parsers, tests, docs. Acceptance: Azure endpoint/model deployment names are normalized.
3. Title: Add DeepSeek provider parser. Labels: provider. Files: parsers, tests, pricing. Acceptance: OpenAI-compatible DeepSeek calls parse and price when known.
4. Title: Add Groq provider parser. Labels: provider. Files: parsers, tests, pricing. Acceptance: Groq chat calls parse.
5. Title: Add better streaming support. Labels: proxy. Files: `proxy.py`, tests, docs. Acceptance: streaming chunks are reconstructed reliably.
6. Title: Add terminal color themes. Labels: terminal. Files: `display.py`. Acceptance: selectable themes.
7. Title: Add Windows proxy setup guide. Labels: docs. Files: `docs/troubleshooting.md`. Acceptance: PowerShell and certificate steps.
8. Title: Add VS Code extension. Labels: extension. Files: new extension folder. Acceptance: reads local dashboard/API.
9. Title: Add promptfoo export improvements. Labels: export. Files: `export.py`, docs. Acceptance: richer assertions.
10. Title: Add latency benchmark mode. Labels: cli. Files: CLI and storage. Acceptance: summary by provider/model.
11. Title: Add LangChain docs. Labels: docs. Files: `docs/guides/langchain.md`. Acceptance: runnable example.
12. Title: Add LlamaIndex docs. Labels: docs. Files: docs. Acceptance: proxy setup documented.
13. Title: Add LiteLLM docs. Labels: docs. Files: docs. Acceptance: proxy setup documented.
14. Title: Add more model pricing data. Labels: pricing. Files: `pricing.py`. Acceptance: sources linked in PR.
15. Title: Add Flask quickstart improvements. Labels: docs. Files: `docs/guides/flask.md`. Acceptance: complete sample.
16. Title: Add FastAPI quickstart improvements. Labels: docs. Files: `docs/guides/fastapi.md`. Acceptance: complete sample.
17. Title: Add Anthropic parser tests. Labels: tests. Files: `tests/test_anthropic_parser.py`. Acceptance: tools and errors covered.
18. Title: Add architecture diagram improvements. Labels: docs. Files: README, architecture docs. Acceptance: clearer proxy/cert flow.
19. Title: Add comparison table improvements. Labels: docs. Files: comparison docs. Acceptance: balanced and sourced.
20. Title: Add .env support improvements. Labels: config. Files: `config.py`, docs. Acceptance: all env vars covered by tests.
