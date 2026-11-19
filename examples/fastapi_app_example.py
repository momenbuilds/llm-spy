"""FastAPI example for inspecting a local OpenAI-compatible call with llm-spy.

Start the fake provider and llm-spy proxy as shown in docs/guides/fastapi.md.
Run the app with HTTP_PROXY set and NO_PROXY cleared for localhost.
No provider account or API key is required.
"""

import os

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "http://127.0.0.1:8000/v1")
API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY", "local")


@app.get("/ask")
def ask(q: str = "Say hello from llm-spy.") -> dict[str, str]:
    """Send one request through the configured local HTTP proxy."""
    try:
        with httpx.Client(timeout=10.0, trust_env=True) as client:
            response = client.post(
                f"{BASE_URL.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "fake-openai-compatible-model",
                    "messages": [{"role": "user", "content": q}],
                    "temperature": 0,
                },
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Upstream provider request failed") from exc
    return {"answer": answer or ""}
