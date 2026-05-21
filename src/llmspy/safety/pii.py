from __future__ import annotations

import re

from llmspy.models import SafetyFinding
from llmspy.utils import mask_secret

PATTERNS = {
    "email": (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "low"),
    "phone": (re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "medium"),
    "ssn": (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "high"),
    "credit_card": (re.compile(r"\b(?:\d[ -]*?){13,19}\b"), "high"),
    "openai_key": (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "critical"),
    "anthropic_key": (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"), "critical"),
    "bearer_token": (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b", re.I), "critical"),
    "jwt": (re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"), "critical"),
    "generic_secret": (
        re.compile(r"\b(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9._~+/=-]{16,}", re.I),
        "high",
    ),
}


def scan_text(text: str | None, location: str = "body") -> list[SafetyFinding]:
    if not text:
        return []
    findings: list[SafetyFinding] = []
    for name, (pattern, severity) in PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append(
                SafetyFinding(
                    type=name,
                    preview=mask_secret(match.group(0)),
                    location=location,
                    severity=severity,
                )
            )
    return findings
