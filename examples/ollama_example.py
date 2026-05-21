"""Run with: HTTP_PROXY=http://localhost:8080 python examples/ollama_example.py"""

import httpx

response = httpx.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3.2", "prompt": "Say hello from llm-spy.", "stream": False},
)
print(response.json().get("response"))
