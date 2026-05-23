"""FastAPI demo that sends a chat request through llm-spy.

Run the zero-key demo with the bundled fake OpenAI-compatible provider:

    # Terminal 1
    python examples/fake_openai_provider.py

    # Terminal 2
    llm-spy start --port 8080

    # Terminal 3
    env -u NO_PROXY -u no_proxy \
      HTTP_PROXY=http://localhost:8080 \
      uvicorn examples.fastapi_app_example:app --reload --port 8001
"""

from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI(
    api_key="llm-spy-demo-key",
    base_url="http://127.0.0.1:8000/v1",
)


@app.get("/ask")
def ask(q: str = "Say hello from llm-spy."):
    response = client.chat.completions.create(
        model="fake-openai-compatible-model",
        messages=[{"role": "user", "content": q}],
    )
    return {"answer": response.choices[0].message.content}
