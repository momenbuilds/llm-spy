# Providers

Supported parser modules live in `src/llmspy/parsers/`.

OpenAI, Anthropic, Gemini, Mistral, Ollama, Together, OpenAI-compatible APIs, and unknown providers are handled with concrete parser tests. Cohere support is best-effort for common chat/message shapes. Unknown providers are stored as raw calls instead of crashing.

To add a provider, implement `ProviderParser`, register it, add tests, add docs, and include pricing when public pricing is known.
