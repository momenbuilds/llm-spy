# CI Mode

Use `llm-spy ci` to fail builds based on local captured data or exported JSON.

```yaml
jobs:
  llm-spy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install llm-spy
      - run: llm-spy ci --input calls.json --max-cost 5 --fail-on-pii --fail-on-injection
```

Gates: maximum cost, PII warnings, and prompt injection warnings.
