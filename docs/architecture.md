# Architecture

llm-spy is a local proxy plus a normalization pipeline.

```mermaid
flowchart LR
  A[User app] --> B[HTTP_PROXY / HTTPS_PROXY]
  B --> C[Proxy capture]
  C --> D[Provider detection]
  D --> E[Parser]
  E --> F[Safety scanners]
  F --> G[Pricing/token calculator]
  G --> H[SQLite]
  G --> I[Rich terminal]
  H --> J[FastAPI dashboard]
```

The parser registry keeps providers isolated. Storage is SQLite at `~/.llm-spy/llm-spy.db` by default. The dashboard reads the same local database and does not require login.

Privacy model: llm-spy does not send captured data anywhere. Exports are explicit user actions.
