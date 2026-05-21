# Security

Report security issues privately by opening a GitHub security advisory or emailing the maintainers once a public contact is available.

llm-spy stores captured LLM traffic locally in SQLite. Treat `~/.llm-spy/llm-spy.db` as sensitive because it may contain prompts, responses, headers, and safety findings. llm-spy does not intentionally store provider API keys.

Do not paste secrets into public issues. Use minimal reproduction cases with redacted data.
