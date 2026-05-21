"""OpenAI-compatible demo client.

Zero-key demo:
    HTTP_PROXY=http://localhost:8080 python examples/openai_compatible_example.py
"""

import os

import httpx

base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "http://127.0.0.1:8000/v1")
api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY", "local")
response = httpx.post(
    f"{base_url}/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello from the llm-spy zero-key demo"}],
        "temperature": 0,
    },
    timeout=10,
)
response.raise_for_status()
print(response.json()["choices"][0]["message"]["content"])
