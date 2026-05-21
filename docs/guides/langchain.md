# LangChain Guide

LangChain can be inspected when the underlying provider client honors `HTTPS_PROXY`.

```bash
llm-spy start
HTTPS_PROXY=http://localhost:8080 python chain.py
```

If a custom transport bypasses environment proxies, configure the provider client explicitly or use SDK mode where available.
