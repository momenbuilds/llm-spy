# Dashboard

Run:

```bash
llm-spy dashboard
```

Pages: overview, calls, call detail, sessions, stats, settings, and diff. API routes include `/api/calls`, `/api/calls/{id}`, `/api/sessions`, `/api/stats`, `/api/cost/today`, `/api/export`, `/api/diff`, `/api/settings`, and replay.

The dashboard is local only. It reads SQLite and does not connect to a cloud service.
