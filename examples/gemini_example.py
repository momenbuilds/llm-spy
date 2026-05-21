"""Run with: HTTPS_PROXY=http://localhost:8080 python examples/gemini_example.py"""

import os

import httpx

key = os.environ["GEMINI_API_KEY"]
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
response = httpx.post(url, json={"contents": [{"parts": [{"text": "Say hello from llm-spy."}]}]})
print(response.text)
