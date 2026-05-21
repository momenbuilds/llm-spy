from __future__ import annotations

import json
from pathlib import Path

from llmspy.storage import Storage


def run_ci(
    max_cost: float | None = None,
    fail_on_pii: bool = False,
    fail_on_injection: bool = False,
    input_file: Path | None = None,
    storage: Storage | None = None,
) -> tuple[int, list[str]]:
    if input_file:
        calls = json.loads(input_file.read_text())
    else:
        calls = (storage or Storage()).export_json()
    messages: list[str] = []
    total_cost = sum((c.get("total_cost_usd") or 0) for c in calls)
    if max_cost is not None and total_cost > max_cost:
        messages.append(f"cost ${total_cost:.4f} exceeds max ${max_cost:.4f}")
    if fail_on_pii and any(c.get("has_pii_warning") for c in calls):
        messages.append("PII warnings found")
    if fail_on_injection and any(c.get("has_injection_warning") for c in calls):
        messages.append("prompt injection warnings found")
    return (1 if messages else 0), messages or ["ci checks passed"]
