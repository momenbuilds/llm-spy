from __future__ import annotations

import re

from llmspy.models import SafetyFinding

PATTERNS = {
    "ignore_previous_instructions": r"ignore (all )?(previous|above|prior) instructions",
    "reveal_system_prompt": r"(reveal|show|print|repeat).{0,30}(system prompt|developer message)",
    "hidden_instructions": r"hidden instructions|secret instructions",
    "exfiltrate": r"exfiltrate|send secrets|leak (the )?(secret|token|key)",
    "override_safety": r"override safety|bypass (policy|safety|guardrails)",
    "jailbreak": r"jailbreak|roleplay as unrestricted|do anything now",
    "confidential_disclosure": r"disclose confidential|reveal confidential",
    "disregard_above": r"disregard (the )?(above|previous)",
}


def scan(text: str | None, location: str = "prompt") -> list[SafetyFinding]:
    if not text:
        return []
    findings: list[SafetyFinding] = []
    for name, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text, re.I):
            findings.append(
                SafetyFinding(
                    type=name, preview=match.group(0)[:120], location=location, severity="high"
                )
            )
    return findings
