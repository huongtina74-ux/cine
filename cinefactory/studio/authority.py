from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field, model_validator


class DecisionDomain(StrEnum):
    PORTFOLIO = "PORTFOLIO"
    BUDGET = "BUDGET"
    RIGHTS = "RIGHTS"
    STORY = "STORY"
    SCRIPT = "SCRIPT"
    DIRECTION = "DIRECTION"
    CAMERA = "CAMERA"
    PRODUCTION_DESIGN = "PRODUCTION_DESIGN"
    PERFORMANCE = "PERFORMANCE"
    TOOL_ROUTING = "TOOL_ROUTING"
    EDITORIAL = "EDITORIAL"
    AUDIO = "AUDIO"
    COLOR = "COLOR"
    QC_RELEASE = "QC_RELEASE"
    SEO_DISCOVERY = "SEO_DISCOVERY"
    PACKAGING = "PACKAGING"
    PUBLISH = "PUBLISH"


class AuthorityRule(BaseModel):
    domain: DecisionDomain
    accountable: str
    responsible: list[str] = Field(default_factory=list)
    consulted: list[str] = Field(default_factory=list)
    informed: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_accountability(self) -> "AuthorityRule":
        if self.accountable in self.consulted:
            raise ValueError("accountable owner cannot also be merely consulted")
        return self


DEFAULT_AUTHORITY: dict[DecisionDomain, AuthorityRule] = {
    DecisionDomain.PORTFOLIO: AuthorityRule(domain=DecisionDomain.PORTFOLIO, accountable="EXECUTIVE_STRATEGY", responsible=["STUDIO_MANAGEMENT"], consulted=["FINANCE_INVESTMENT", "INTELLIGENCE"]),
    DecisionDomain.BUDGET: AuthorityRule(domain=DecisionDomain.BUDGET, accountable="FINANCE_INVESTMENT", responsible=["STUDIO_MANAGEMENT"], consulted=["EXECUTIVE_STRATEGY"]),
    DecisionDomain.RIGHTS: AuthorityRule(domain=DecisionDomain.RIGHTS, accountable="RIGHTS", responsible=["BUSINESS_AFFAIRS_LEGAL"], consulted=["PRODUCTION", "PACKAGING"]),
    DecisionDomain.STORY: AuthorityRule(domain=DecisionDomain.STORY, accountable="DIRECTION", responsible=["WRITERS_ROOM"], consulted=["SCRIPT_LOGIC", "EDITORIAL"]),
    DecisionDomain.SCRIPT: AuthorityRule(domain=DecisionDomain.SCRIPT, accountable="WRITERS_ROOM", responsible=["WRITERS_ROOM"], consulted=["DIRECTION", "SCRIPT_LOGIC"]),
    DecisionDomain.DIRECTION: AuthorityRule(domain=DecisionDomain.DIRECTION, accountable="DIRECTION", responsible=["DIRECTION"], consulted=["CINEMATOGRAPHY", "EDITORIAL", "PERFORMANCE"]),
    DecisionDomain.CAMERA: AuthorityRule(domain=DecisionDomain.CAMERA, accountable="CINEMATOGRAPHY", responsible=["CINEMATOGRAPHY"], consulted=["DIRECTION", "EDITORIAL"]),
    DecisionDomain.PRODUCTION_DESIGN: AuthorityRule(domain=DecisionDomain.PRODUCTION_DESIGN, accountable="PRODUCTION_DESIGN", responsible=["ASSETS"], consulted=["DIRECTION", "CINEMATOGRAPHY"]),
    DecisionDomain.PERFORMANCE: AuthorityRule(domain=DecisionDomain.PERFORMANCE, accountable="DIRECTION", responsible=["PERFORMANCE"], consulted=["EDITORIAL", "AUDIO"]),
    DecisionDomain.TOOL_ROUTING: AuthorityRule(domain=DecisionDomain.TOOL_ROUTING, accountable="TECHNICAL_DIRECTION", responsible=["PRODUCTION"], consulted=["DIRECTION", "OPERATIONS", "RND"]),
    DecisionDomain.EDITORIAL: AuthorityRule(domain=DecisionDomain.EDITORIAL, accountable="EDITORIAL", responsible=["EDITORIAL"], consulted=["DIRECTION", "AUDIO"]),
    DecisionDomain.AUDIO: AuthorityRule(domain=DecisionDomain.AUDIO, accountable="AUDIO", responsible=["AUDIO"], consulted=["DIRECTION", "EDITORIAL"]),
    DecisionDomain.COLOR: AuthorityRule(domain=DecisionDomain.COLOR, accountable="COLOR", responsible=["COLOR"], consulted=["CINEMATOGRAPHY", "DIRECTION"]),
    DecisionDomain.QC_RELEASE: AuthorityRule(domain=DecisionDomain.QC_RELEASE, accountable="QC", responsible=["QC"], consulted=["RIGHTS", "PACKAGING", "STUDIO_MANAGEMENT"]),
    DecisionDomain.SEO_DISCOVERY: AuthorityRule(domain=DecisionDomain.SEO_DISCOVERY, accountable="YOUTUBE_GROWTH_SEO", responsible=["INTELLIGENCE"], consulted=["PACKAGING", "ANALYTICS"]),
    DecisionDomain.PACKAGING: AuthorityRule(domain=DecisionDomain.PACKAGING, accountable="PACKAGING", responsible=["PACKAGING"], consulted=["YOUTUBE_GROWTH_SEO", "CREATIVE_STRATEGY"]),
    DecisionDomain.PUBLISH: AuthorityRule(domain=DecisionDomain.PUBLISH, accountable="STUDIO_MANAGEMENT", responsible=["PACKAGING"], consulted=["QC", "RIGHTS", "YOUTUBE_GROWTH_SEO"]),
}


class AuthorityMatrix:
    def __init__(self, rules: dict[DecisionDomain, AuthorityRule] | None = None) -> None:
        self._rules = dict(rules or DEFAULT_AUTHORITY)

    def get(self, domain: DecisionDomain) -> AuthorityRule:
        return self._rules[domain]

    def can_decide(self, domain: DecisionDomain, actor: str) -> bool:
        return self._rules[domain].accountable == actor

    def validate(self) -> list[str]:
        missing = [d.value for d in DecisionDomain if d not in self._rules]
        return [f"AUTHORITY_MISSING:{x}" for x in missing]
