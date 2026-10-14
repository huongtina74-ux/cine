from __future__ import annotations

from dataclasses import dataclass, field
from cinefactory.domain.enums import RightsStatus


@dataclass
class RightsDecision:
    passed: bool
    findings: list[str]=field(default_factory=list)


class RightsGate:
    def __init__(self, assets, model_registry=None): self.assets=assets; self.models=model_registry
    def project_assets(self,project_id:str)->RightsDecision:
        findings=[]
        for a in self.assets.list_project(project_id):
            if a.rights_status is not RightsStatus.GREEN:
                findings.append(f'{a.asset_id}:{a.rights_status}')
            if a.rights.commercial_use is False:
                findings.append(f'{a.asset_id}:COMMERCIAL_USE_DENIED')
            if a.rights.expires_at is not None:
                from datetime import datetime, timezone
                if a.rights.expires_at <= datetime.now(timezone.utc): findings.append(f'{a.asset_id}:RIGHTS_EXPIRED')
        return RightsDecision(not findings,findings)
