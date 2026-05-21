I’m launching llm-spy, a local-first developer tool for inspecting LLM API calls.

The goal is simple: help developers see what their AI apps are actually sending and receiving without setting up a full observability stack.

It works through standard proxy environment variables, keeps data in local SQLite, and includes terminal output, a dashboard, cost estimates, and local safety warnings.

It is early, intentionally local-first, and built for the first debugging loop before you need heavier production observability.
