from __future__ import annotations

import httpx


def main() -> None:
    response = httpx.post(
        "http://127.0.0.1:19001/v1/chat/completions",
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello through llm-spy audit"}],
            "temperature": 0,
        },
        timeout=10,
    )
    response.raise_for_status()
    print(response.json()["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
