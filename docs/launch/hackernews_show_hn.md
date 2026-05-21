Show HN: llm-spy, a local-first proxy for inspecting LLM API calls

I built llm-spy because I wanted the “Charles Proxy for AI apps” experience: run a local proxy, route your app through it, and see prompts, responses, latency, token usage, cost estimates, and safety warnings without adding SDK instrumentation or creating a cloud account.

There is a no-API-key demo using a fake OpenAI-compatible provider, so you can try the flow without spending credits.

It is early but functional, with SQLite history and a local dashboard. I’d love feedback on where the first 10 minutes are confusing.
