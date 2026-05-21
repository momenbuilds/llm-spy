from __future__ import annotations

import json

from llmspy.storage import Storage
from llmspy.utils import parse_since


def export_data(
    storage: Storage,
    fmt: str,
    provider: str | None = None,
    model: str | None = None,
    since: str | None = None,
    session: str | None = None,
) -> str:
    calls = storage.list_calls(
        limit=100000,
        provider=provider,
        model=model,
        since=parse_since(since),
        session=session,
    )
    if fmt == "json":
        return json.dumps(storage.export_json(calls), indent=2)
    if fmt == "csv":
        return storage.export_csv(calls)
    if fmt == "promptfoo":
        return storage.export_promptfoo(calls)
    raise ValueError("format must be json, csv, or promptfoo")
