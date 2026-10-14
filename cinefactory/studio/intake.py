from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .contracts import StudioProjectSpec
from .niche_os import NicheRegistry


class GreenlightState(StrEnum):
    PROCEED_RESEARCH = "PROCEED_RESEARCH"
    GREENLIGHT = "GREENLIGHT"
    HOLD = "HOLD"


class NicheReadiness(BaseModel):
    niche_id: str
    research_ready: bool = False
    competitor_ready: bool = False
    seo_ready: bool = False
    production_ready: bool = False
    packaging_retention_ready: bool = False
    risk_ready: bool = False
    missing: list[str] = Field(default_factory=list)

    @property
    def production_greenlight_ready(self) -> bool:
        return all(
            (
                self.research_ready,
                self.competitor_ready,
                self.seo_ready,
                self.production_ready,
                self.packaging_retention_ready,
                self.risk_ready,
            )
        )


class ProjectIntake(BaseModel):
    project_id: str
    prompt: str
    platform: str
    requested_niche: str | None = None
    resolved_niche: str | None = None
    explicit_niche: bool = False
    strict_niche_gate: bool = False
    recognized_niche: bool = False
    reasons: list[str] = Field(default_factory=list)


class PortfolioGreenlight(BaseModel):
    project_id: str
    state: GreenlightState
    approved_for_research: bool
    approved_for_production: bool
    niche_id: str | None = None
    readiness: NicheReadiness | None = None
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CorporatePreflight(BaseModel):
    project_id: str
    approved: bool
    finance_ready: bool
    rights_policy_ready: bool
    risk_ready: bool
    seo_discovery_ready: bool
    competitor_research_ready: bool
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)


class NicheConfigStore:
    def __init__(self, repo_root: str | Path) -> None:
        self.root = Path(repo_root).resolve() / "config" / "niches"

    def _load(self, niche_id: str, filename: str) -> dict[str, Any]:
        path = self.root / niche_id / filename
        if not path.is_file():
            return {}
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _has_any(value: Any) -> bool:
        if isinstance(value, dict):
            return any(NicheConfigStore._has_any(v) for v in value.values())
        if isinstance(value, (list, tuple, set)):
            return any(NicheConfigStore._has_any(v) for v in value)
        if isinstance(value, str):
            return bool(value.strip())
        return value not in (None, False, 0)

    def readiness(self, niche_id: str) -> NicheReadiness:
        research = self._load(niche_id, "research.yaml")
        competitors = self._load(niche_id, "competitors.yaml")
        seo = self._load(niche_id, "seo.yaml")
        production = self._load(niche_id, "production.yaml")
        packaging = self._load(niche_id, "packaging_retention.yaml")
        risk = self._load(niche_id, "risk_analytics.yaml")

        result = NicheReadiness(
            niche_id=niche_id,
            research_ready=self._has_any(research),
            competitor_ready=self._has_any(competitors),
            seo_ready=self._has_any(seo),
            production_ready=self._has_any(production),
            packaging_retention_ready=self._has_any(packaging),
            risk_ready=self._has_any(risk.get("rights_and_policy"))
            and self._has_any(risk.get("monetization")),
        )
        checks = {
            "NICHE_RESEARCH_MISSING": result.research_ready,
            "COMPETITOR_BASELINE_MISSING": result.competitor_ready,
            "SEO_DISCOVERY_BASELINE_MISSING": result.seo_ready,
            "PRODUCTION_RECIPE_BASELINE_MISSING": result.production_ready,
            "PACKAGING_RETENTION_BASELINE_MISSING": result.packaging_retention_ready,
            "NICHE_RISK_MONETIZATION_BASELINE_MISSING": result.risk_ready,
        }
        result.missing = [code for code, ok in checks.items() if not ok]
        return result


class ProjectIntakeEngine:
    ALIASES = {
        "minecraft": ("minecraft", "gaming.minecraft"),
        "roblox_animation": ("roblox", "gaming.roblox"),
        "long_slices_game": ("long slice", "long slices", "animal long slide", "animation.animal_long_slide"),
        "asmr_sleep_hands_objects": ("asmr", "hand sounds", "hands objects"),
        "audio_storytelling_seniors": ("audio storytelling", "storytelling seniors", "story for seniors"),
        "fishing_silent": ("fishing silent", "silent fishing"),
        "rain_sleep_white_noise": ("rain sleep", "white noise", "sleep rain"),
    }

    def __init__(self, repo_root: str | Path, niches: NicheRegistry | None = None) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.niches = niches or NicheRegistry()
        self.config = NicheConfigStore(self.repo_root)

    def resolve_niche(self, project: StudioProjectSpec) -> str | None:
        known = {item.niche_id for item in self.niches.list()}
        if project.niche:
            normalized = project.niche.strip().lower().replace(" ", "_")
            if normalized in known:
                return normalized
            for niche_id, aliases in self.ALIASES.items():
                if project.niche.lower() in aliases:
                    return niche_id
            return project.niche

        haystack = f"{project.domain} {project.prompt}".lower()
        for niche_id, aliases in self.ALIASES.items():
            if any(alias in haystack for alias in aliases):
                return niche_id
        return None

    def intake(self, project: StudioProjectSpec) -> ProjectIntake:
        resolved = self.resolve_niche(project)
        known = {item.niche_id for item in self.niches.list()}
        explicit = bool(project.niche)
        recognized = bool(resolved and resolved in known)
        reasons: list[str] = []
        if explicit:
            reasons.append("EXPLICIT_NICHE_REQUEST")
        elif recognized:
            reasons.append("NICHE_INFERRED_FROM_PROJECT_CONTEXT")
        else:
            reasons.append("GENERAL_OR_UNREGISTERED_NICHE")

        return ProjectIntake(
            project_id=project.studio_project_id,
            prompt=project.prompt,
            platform=project.platform,
            requested_niche=project.niche,
            resolved_niche=resolved,
            explicit_niche=explicit,
            strict_niche_gate=explicit,
            recognized_niche=recognized,
            reasons=reasons,
        )

    def portfolio_greenlight(self, project: StudioProjectSpec) -> PortfolioGreenlight:
        intake = self.intake(project)
        if intake.explicit_niche and not intake.recognized_niche:
            return PortfolioGreenlight(
                project_id=project.studio_project_id,
                state=GreenlightState.HOLD,
                approved_for_research=False,
                approved_for_production=False,
                niche_id=intake.resolved_niche,
                blockers=["UNKNOWN_EXPLICIT_NICHE"],
            )

        if not intake.recognized_niche:
            return PortfolioGreenlight(
                project_id=project.studio_project_id,
                state=GreenlightState.GREENLIGHT,
                approved_for_research=True,
                approved_for_production=True,
                warnings=["GENERAL_PROJECT_USES_SHARED_COMPANY_RULES"],
            )

        readiness = self.config.readiness(intake.resolved_niche or "")
        strict = intake.strict_niche_gate
        if strict and not readiness.production_greenlight_ready:
            return PortfolioGreenlight(
                project_id=project.studio_project_id,
                state=GreenlightState.PROCEED_RESEARCH,
                approved_for_research=True,
                approved_for_production=False,
                niche_id=intake.resolved_niche,
                readiness=readiness,
                blockers=list(readiness.missing),
                warnings=["NICHE_RESEARCH_MUST_BE_COMPLETED_BEFORE_EXPENSIVE_PRODUCTION"],
            )

        return PortfolioGreenlight(
            project_id=project.studio_project_id,
            state=GreenlightState.GREENLIGHT,
            approved_for_research=True,
            approved_for_production=True,
            niche_id=intake.resolved_niche,
            readiness=readiness,
            warnings=(
                ["NICHE_INFERRED_ADVISORY_MODE"]
                if not strict and not readiness.production_greenlight_ready
                else []
            ),
        )

    def corporate_preflight(
        self,
        project: StudioProjectSpec,
        *,
        competitor_profiles: list[dict[str, Any]] | None = None,
        research_pack: dict[str, Any] | None = None,
    ) -> CorporatePreflight:
        intake = self.intake(project)
        greenlight = self.portfolio_greenlight(project)
        competitor_profiles = competitor_profiles or []
        research_pack = research_pack or {}

        finance_ready = True  # zero-metered API policy and spend gates remain authoritative downstream
        rights_policy_ready = True  # final asset/tool rights are still fail-closed downstream
        risk_ready = True
        seo_ready = True
        competitor_ready = True
        blockers: list[str] = []
        warnings: list[str] = []

        if intake.recognized_niche and intake.resolved_niche:
            readiness = self.config.readiness(intake.resolved_niche)
            competitor_ready = readiness.competitor_ready or bool(competitor_profiles)
            seo_ready = readiness.seo_ready
            risk_ready = readiness.risk_ready
            if intake.strict_niche_gate:
                if not competitor_ready:
                    blockers.append("COMPETITOR_RESEARCH_REQUIRED")
                if not seo_ready:
                    blockers.append("SEO_DISCOVERY_REQUIRED")
                if not risk_ready:
                    blockers.append("NICHE_RISK_MONETIZATION_REQUIRED")
                if not greenlight.approved_for_production:
                    blockers.extend(
                        code for code in greenlight.blockers if code not in blockers
                    )
            elif not readiness.production_greenlight_ready:
                warnings.append("INFERRED_NICHE_BASELINE_INCOMPLETE_ADVISORY_ONLY")

        if project.platform.lower() == "youtube" and not intake.recognized_niche:
            warnings.append("NO_NICHE_SPECIFIC_YOUTUBE_BASELINE")

        promoted_patterns = int(research_pack.get("promoted_pattern_count") or 0)
        return CorporatePreflight(
            project_id=project.studio_project_id,
            approved=not blockers,
            finance_ready=finance_ready,
            rights_policy_ready=rights_policy_ready,
            risk_ready=risk_ready,
            seo_discovery_ready=seo_ready,
            competitor_research_ready=competitor_ready,
            blockers=list(dict.fromkeys(blockers)),
            warnings=list(dict.fromkeys(warnings)),
            evidence={
                "resolved_niche": intake.resolved_niche,
                "strict_niche_gate": intake.strict_niche_gate,
                "competitor_profile_count": len(competitor_profiles),
                "promoted_pattern_count": promoted_patterns,
                "zero_metered_api_policy": True,
                "downstream_rights_gate_required": True,
            },
        )
