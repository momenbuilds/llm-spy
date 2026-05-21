# I built llm-spy: a local proxy for seeing what your LLM app actually sends

I made this because I wanted a quick local way to inspect prompts, responses, token usage, latency, and cost estimates without wiring an observability SDK into every toy app.

llm-spy runs as an HTTP/HTTPS proxy. You run your app with `HTTP_PROXY` or `HTTPS_PROXY`, and it prints LLM calls in the terminal, stores them in SQLite, and serves a local dashboard.

It is not a hosted LangSmith/Langfuse replacement. The point is fast local debugging: no account, no telemetry, no cloud sync.

There is also a fake OpenAI-compatible demo so you can try it without an API key or real API credits.

I’d especially love feedback on first-run UX and provider parsing edge cases.
