"""Run with: HTTPS_PROXY=http://localhost:8080 python examples/openai_example.py"""

from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello from llm-spy."}],
)
print(response.choices[0].message.content)
