# Replay

Replay is implemented but still experimental. It rebuilds a captured provider request and sends it again. API keys are read only from environment variables and are never stored.

```bash
OPENAI_API_KEY=... llm-spy replay CALL_ID --model gpt-4o-mini
```

Limitations: replay is explicit, provider-specific, can spend real provider credits, and works only when the original raw request has enough information.
