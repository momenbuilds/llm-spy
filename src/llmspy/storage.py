from __future__ import annotations

import csv
import sqlite3
from collections.abc import Iterable
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

from llmspy.config import db_path
from llmspy.models import ParsedCall, PricingEntry, Session
from llmspy.utils import safe_json_dumps, safe_json_loads

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  ended_at DATETIME,
  label TEXT,
  metadata JSON
);
CREATE TABLE IF NOT EXISTS calls (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  parent_call_id TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  provider TEXT,
  model TEXT,
  endpoint TEXT,
  method TEXT,
  status_code INTEGER,
  system_prompt TEXT,
  messages JSON,
  parameters JSON,
  tools JSON,
  raw_request TEXT,
  response_content TEXT,
  finish_reason TEXT,
  raw_response TEXT,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  total_tokens INTEGER,
  estimated_tokens BOOLEAN DEFAULT FALSE,
  input_cost_usd REAL,
  output_cost_usd REAL,
  total_cost_usd REAL,
  latency_ms INTEGER,
  has_pii_warning BOOLEAN DEFAULT FALSE,
  pii_findings JSON,
  has_injection_warning BOOLEAN DEFAULT FALSE,
  injection_findings JSON,
  error TEXT
);
CREATE TABLE IF NOT EXISTS pricing_cache (
  provider TEXT,
  model TEXT,
  input_cost_per_1k REAL,
  output_cost_per_1k REAL,
  updated_at DATETIME,
  PRIMARY KEY(provider, model)
);
CREATE TABLE IF NOT EXISTS budgets (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at DATETIME
);
CREATE TABLE IF NOT EXISTS config (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at DATETIME
);
"""

CALL_COLUMNS = [
    "id",
    "session_id",
    "parent_call_id",
    "timestamp",
    "provider",
    "model",
    "endpoint",
    "method",
    "status_code",
    "system_prompt",
    "messages",
    "parameters",
    "tools",
    "raw_request",
    "response_content",
    "finish_reason",
    "raw_response",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "estimated_tokens",
    "input_cost_usd",
    "output_cost_usd",
    "total_cost_usd",
    "latency_ms",
    "has_pii_warning",
    "pii_findings",
    "has_injection_warning",
    "injection_findings",
    "error",
]


class Storage:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        self._load_env_defaults()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def create_session(
        self, label: str | None = None, metadata: dict[str, Any] | None = None
    ) -> Session:
        session = Session(label=label, metadata=metadata or {})
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO sessions (id, started_at, label, metadata) VALUES (?, ?, ?, ?)",
                (
                    session.id,
                    session.started_at.isoformat(),
                    label,
                    safe_json_dumps(session.metadata),
                ),
            )
        return session

    def end_session(self, session_id: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE sessions SET ended_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), session_id),
            )

    def insert_call(self, call: ParsedCall) -> ParsedCall:
        data = call.model_dump()
        data["timestamp"] = call.timestamp.isoformat()
        for key in [
            "messages",
            "parameters",
            "tools",
            "raw_request",
            "raw_response",
            "pii_findings",
            "injection_findings",
        ]:
            data[key] = safe_json_dumps(data.get(key))
        placeholders = ",".join("?" for _ in CALL_COLUMNS)
        with self.connect() as conn:
            conn.execute(
                f"INSERT INTO calls ({','.join(CALL_COLUMNS)}) VALUES ({placeholders})",
                [data.get(col) for col in CALL_COLUMNS],
            )
        return call

    def _row_to_call(self, row: sqlite3.Row) -> ParsedCall:
        data = dict(row)
        for key in [
            "messages",
            "parameters",
            "tools",
            "raw_request",
            "raw_response",
            "pii_findings",
            "injection_findings",
        ]:
            data[key] = safe_json_loads(data.get(key)) or (
                [] if key in {"messages", "tools", "pii_findings", "injection_findings"} else {}
            )
        data["estimated_tokens"] = bool(data.get("estimated_tokens"))
        data["has_pii_warning"] = bool(data.get("has_pii_warning"))
        data["has_injection_warning"] = bool(data.get("has_injection_warning"))
        return ParsedCall(**data)

    def get_call(self, call_id: str) -> ParsedCall | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM calls WHERE id = ?", (call_id,)).fetchone()
        return self._row_to_call(row) if row else None

    def list_calls(
        self,
        limit: int = 20,
        provider: str | None = None,
        model: str | None = None,
        since: datetime | None = None,
        errors_only: bool = False,
        search: str | None = None,
        session: str | None = None,
    ) -> list[ParsedCall]:
        where, args = self._filters(provider, model, since, errors_only, search, session)
        sql = f"SELECT * FROM calls {where} ORDER BY timestamp DESC LIMIT ?"
        with self.connect() as conn:
            rows = conn.execute(sql, [*args, limit]).fetchall()
        return [self._row_to_call(row) for row in rows]

    def search_calls(self, text: str, limit: int = 50) -> list[ParsedCall]:
        return self.list_calls(limit=limit, search=text)

    def list_sessions(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM sessions ORDER BY started_at DESC").fetchall()
        return [dict(row) for row in rows]

    def clear_calls(self) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM calls")
            conn.execute("DELETE FROM sessions")

    def export_json(self, calls: Iterable[ParsedCall] | None = None) -> list[dict[str, Any]]:
        calls = list(calls) if calls is not None else self.list_calls(limit=100000)
        return [call.model_dump(mode="json") for call in calls]

    def export_csv(self, calls: Iterable[ParsedCall] | None = None) -> str:
        calls = list(calls) if calls is not None else self.list_calls(limit=100000)
        fields = [
            "timestamp",
            "provider",
            "model",
            "endpoint",
            "latency_ms",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "total_cost_usd",
            "has_pii_warning",
            "has_injection_warning",
            "error",
        ]
        out = StringIO()
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        for call in calls:
            row = call.model_dump()
            writer.writerow({field: row.get(field) for field in fields})
        return out.getvalue()

    def export_promptfoo(self, calls: Iterable[ParsedCall] | None = None) -> str:
        calls = list(calls) if calls is not None else self.list_calls(limit=100000)
        lines = ["# Best-effort promptfoo export generated by llm-spy", "prompts:"]
        for call in calls:
            prompt = call.system_prompt or "\n".join(
                str(m.get("content", "")) for m in call.messages
            )
            lines.append(f"  - {safe_json_dumps(prompt)}")
        lines.extend(["providers:", "  - openai:chat:gpt-4o-mini", "tests:"])
        for call in calls:
            lines.append(f"  - vars: {{ captured_call_id: {call.id} }}")
        return "\n".join(lines) + "\n"

    def cost_summary(self, **filters: Any) -> dict[str, Any]:
        calls = self.list_calls(limit=100000, **{k: v for k, v in filters.items() if v is not None})
        return {
            "total_cost_usd": sum(c.total_cost_usd or 0 for c in calls),
            "input_cost_usd": sum(c.input_cost_usd or 0 for c in calls),
            "output_cost_usd": sum(c.output_cost_usd or 0 for c in calls),
            "total_tokens": sum(c.total_tokens or 0 for c in calls),
            "calls": len(calls),
            "unknown_pricing_calls": sum(1 for c in calls if c.total_cost_usd is None),
        }

    def daily_cost(self) -> float:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.cost_summary(since=today)["total_cost_usd"]

    def provider_stats(self) -> list[dict[str, Any]]:
        return self._group_stats("provider")

    def model_stats(self) -> list[dict[str, Any]]:
        return self._group_stats("model")

    def latency_stats(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT AVG(latency_ms) avg_latency, MAX(latency_ms) max_latency FROM calls"
            ).fetchone()
        return dict(row)

    def save_budget(self, key: str, value: str) -> None:
        self._upsert("budgets", key, value)

    def load_budget(self, key: str = "daily") -> str | None:
        return self._get("budgets", key)

    def save_config(self, key: str, value: str) -> None:
        self._upsert("config", key, value)

    def load_config(self, key: str) -> str | None:
        return self._get("config", key)

    def list_config(self) -> dict[str, str]:
        with self.connect() as conn:
            rows = conn.execute("SELECT key, value FROM config ORDER BY key").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def diff_calls(self, call_a: str, call_b: str) -> dict[str, Any]:
        a, b = self.get_call(call_a), self.get_call(call_b)
        if not a or not b:
            raise KeyError("one or both call ids were not found")
        fields = [
            "system_prompt",
            "messages",
            "parameters",
            "tools",
            "model",
            "provider",
            "endpoint",
            "response_content",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "total_cost_usd",
            "latency_ms",
            "error",
            "injection_findings",
            "pii_findings",
        ]
        return {
            field: {"a": getattr(a, field), "b": getattr(b, field)}
            for field in fields
            if getattr(a, field) != getattr(b, field)
        }

    def update_pricing_cache(self, entries: list[PricingEntry]) -> None:
        with self.connect() as conn:
            for entry in entries:
                conn.execute(
                    """INSERT OR REPLACE INTO pricing_cache
                    (provider, model, input_cost_per_1k, output_cost_per_1k, updated_at)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        entry.provider,
                        entry.model,
                        entry.input_cost_per_1k,
                        entry.output_cost_per_1k,
                        datetime.utcnow().isoformat(),
                    ),
                )

    def get_pricing(self, provider: str, model: str) -> PricingEntry | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM pricing_cache WHERE provider = ? AND model = ?",
                (provider, model),
            ).fetchone()
        return PricingEntry(**dict(row)) if row else None

    def _filters(self, provider, model, since, errors_only, search, session):
        clauses, args = [], []
        if provider:
            clauses.append("provider = ?")
            args.append(provider)
        if model:
            clauses.append("model = ?")
            args.append(model)
        if since:
            clauses.append("timestamp >= ?")
            args.append(since.isoformat())
        if errors_only:
            clauses.append("error IS NOT NULL")
        if session:
            clauses.append("session_id = ?")
            args.append(session)
        if search:
            like = f"%{search}%"
            clauses.append(
                "(messages LIKE ? OR response_content LIKE ? OR model LIKE ? OR provider LIKE ? OR endpoint LIKE ? OR error LIKE ?)"
            )
            args.extend([like] * 6)
        return ("WHERE " + " AND ".join(clauses) if clauses else ""), args

    def _group_stats(self, column: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT {column} name, COUNT(*) calls, SUM(total_cost_usd) cost, SUM(total_tokens) tokens FROM calls GROUP BY {column} ORDER BY calls DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def _upsert(self, table: str, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                f"INSERT OR REPLACE INTO {table} (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.utcnow().isoformat()),
            )

    def _get(self, table: str, key: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(f"SELECT value FROM {table} WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def _load_env_defaults(self) -> None:
        import os

        if os.getenv("LLM_SPY_DAILY_BUDGET") and not self.load_budget("daily"):
            self.save_budget("daily", os.environ["LLM_SPY_DAILY_BUDGET"])
