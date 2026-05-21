# Flask Guide

Run llm-spy, then run Flask with proxy variables:

```bash
llm-spy start
HTTPS_PROXY=http://localhost:8080 HTTP_PROXY=http://localhost:8080 flask --app app run
```

Any LLM calls made by your Flask app through standard HTTP clients should be captured.
