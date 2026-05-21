from __future__ import annotations

from rich.console import Console
from rich.table import Table

from llmspy.storage import Storage


def render_diff(storage: Storage, call_a: str, call_b: str) -> dict:
    return storage.diff_calls(call_a, call_b)


def print_diff(diff: dict) -> None:
    console = Console()
    table = Table(title="llm-spy diff")
    table.add_column("Field")
    table.add_column("Call A")
    table.add_column("Call B")
    for field, values in diff.items():
        table.add_row(field, str(values["a"])[:1000], str(values["b"])[:1000])
    console.print(table)
