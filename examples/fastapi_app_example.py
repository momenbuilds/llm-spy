"""Run with: HTTPS_PROXY=http://localhost:8080 uvicorn examples.fastapi_app_example:app"""

from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI()


@app.get("/ask")
def ask(q: str = "Say hello from llm-spy."):
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": q}]
    )
    return {"answer": response.choices[0].message.content}
