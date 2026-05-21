"""Run with: HTTPS_PROXY=http://localhost:8080 python examples/anthropic_example.py"""

from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    model="claude-3-5-haiku-latest",
    max_tokens=64,
    messages=[{"role": "user", "content": "Say hello from llm-spy."}],
)
print(message.content[0].text)
