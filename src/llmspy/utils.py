from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any


def safe_json_loads(value: str | bytes | None) -> Any:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    try:
        return json.loads(value)
    except Exception:
        return value


def safe_json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def truncate(value: str | None, limit: int = 900) -> str:
    if not value:
        return ""
    if len(value) <= limit:
        return value
    return value[: limit - 24] + "\n... [truncated]"


def parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    now = datetime.utcnow()
    unit = value[-1].lower()
    amount = int(value[:-1]) if value[:-1].isdigit() else 0
    if unit == "h":
        return now - timedelta(hours=amount)
    if unit == "d":
        return now - timedelta(days=amount)
    if unit == "w":
        return now - timedelta(weeks=amount)
    raise ValueError("since must look like 1h, 24h, 7d, or 2w")


def estimate_tokens(*texts: str | None) -> int:
    joined = " ".join(t for t in texts if t)
    return max(1, len(joined) // 4) if joined else 0


def mask_secret(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"
