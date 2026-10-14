from __future__ import annotations

import ipaddress
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Any


FORBIDDEN_PROVIDER_RE = re.compile(
    r"(?i)(openai|gpt[-_ ]?image|kling|veo|runway|replicate|fal(?:\.ai)?|elevenlabs|hailuo|"
    r"seedance|dreamina|jimeng|runninghub|dashscope|volcengine|ark|minimax.*api|gemini.*api)"
)
URL_RE = re.compile(r"https?://[^\s\"']+")


@dataclass(frozen=True)
class WorkflowSafetyReport:
    passed: bool
    findings: list[str] = field(default_factory=list)


def _iter_values(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _iter_values(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _iter_values(v, f"{path}[{i}]")
    else:
        yield path, value


def _public_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if not host:
        return False
    if host == "localhost":
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local)


class WorkflowSafetyValidator:
    """Static guard against obvious metered/cloud nodes in production workflows.

    This is defense-in-depth, not a sandbox. Production should also run ComfyUI with
    `--disable-api-nodes`, pinned custom nodes and restricted egress.
    """

    def review(self, workflow: dict) -> WorkflowSafetyReport:
        findings: list[str] = []
        for path, value in _iter_values(workflow):
            if not isinstance(value, str):
                continue
            # class_type/node names and service/model labels are useful signals.
            if (path.endswith(".class_type") or path.endswith(".type") or "provider" in path.lower()) and FORBIDDEN_PROVIDER_RE.search(value):
                findings.append(f"FORBIDDEN_PROVIDER_NODE:{path}:{value}")
            for url in URL_RE.findall(value):
                if _public_url(url):
                    findings.append(f"PUBLIC_NETWORK_URL:{path}:{url}")
        return WorkflowSafetyReport(passed=not findings, findings=sorted(set(findings)))

    def require_safe(self, workflow: dict) -> None:
        report = self.review(workflow)
        if not report.passed:
            raise ValueError("Unsafe production workflow: " + "; ".join(report.findings))
