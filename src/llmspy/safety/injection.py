from __future__ import annotations

from llmspy.models import SafetyFinding
from llmspy.safety.promptshield import scan as promptshield_scan


def scan_text(text: str | None, location: str = "prompt") -> list[SafetyFinding]:
    return promptshield_scan(text, location)
