# Safety

PII detection is regex-based and local-only. It detects common emails, phone numbers, SSNs, credit-card-like numbers, API keys, bearer tokens, OpenAI keys, Anthropic keys, and JWT-like strings.

PromptShield is the internal prompt injection engine. It is pattern-based, local-only, and detects phrases such as “ignore previous instructions”, system prompt extraction, exfiltration, jailbreaks, and policy bypass requests.

Safety warnings do not block requests by default and are not a guarantee of safety.
