from __future__ import annotations

from dataclasses import dataclass, field

from cinefactory.discovery.models import ResearchBrief
from cinefactory.domain.models import ScriptSpec


@dataclass
class FactualityDecision:
    passed: bool
    findings: list[str] = field(default_factory=list)


class FactualityGate:
    """Conservative source gate for claims explicitly attached to screenplay scenes."""

    def research(self, brief: ResearchBrief) -> FactualityDecision:
        findings: list[str] = []
        for claim in brief.claims:
            if claim.high_risk and (not claim.verified or not claim.source_url):
                findings.append(f"UNVERIFIED_HIGH_RISK_CLAIM:{claim.claim_id}")
        return FactualityDecision(not findings, findings)

    def script(self, script: ScriptSpec, brief: ResearchBrief) -> FactualityDecision:
        available = {c.claim_id: c for c in brief.claims}
        findings: list[str] = []
        for scene in script.scenes:
            for claim_id in scene.claim_ids:
                claim = available.get(claim_id)
                if claim is None:
                    findings.append(f"UNKNOWN_CLAIM:{scene.scene_id}:{claim_id}")
                elif not claim.verified:
                    findings.append(f"UNVERIFIED_CLAIM:{scene.scene_id}:{claim_id}")
        return FactualityDecision(not findings, findings)
