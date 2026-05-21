"""Run with: HTTPS_PROXY=http://localhost:8080 flask --app examples.flask_app_example run"""

from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()


@app.get("/ask")
def ask():
    q = request.args.get("q", "Say hello from llm-spy.")
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": q}]
    )
    return {"answer": response.choices[0].message.content}
