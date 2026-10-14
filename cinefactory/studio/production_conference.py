from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .contracts import CapabilityKind, MediaProductSpec, StudioProjectSpec
from .planning import (
    PlanningMode,
    ProductionStrategy,
    SceneToolPlanner,
)
from .script_intelligence import ScriptSourcePack


class ConferenceLane(StrEnum):
    QUALITY_FIRST = "QUALITY_FIRST"
    BALANCED = "BALANCED"
    FAST_LEAN = "FAST_LEAN"


class ConferenceRole(StrEnum):
    RESEARCH = "RESEARCH"
    WRITER = "WRITER"
    DIRECTOR = "DIRECTOR"
    TECHNICAL_DIRECTOR = "TECHNICAL_DIRECTOR"
    EDITOR = "EDITOR"
    AUDIO = "AUDIO"
    COMPUTE_FINANCE = "COMPUTE_FINANCE"


class ConferencePolicy(BaseModel):
    optimization_weights: dict[str, float]
    render_scale: float = Field(ge=0.5, le=1.0)
    candidate_multiplier: float = Field(ge=0.5, le=2.0)
    repair_budget: int = Field(ge=0, le=5)
    qc_target: float = Field(ge=0.0, le=1.0)
    continuity_priority: float = Field(ge=0.0, le=1.0)
    compute_budget_index: float = Field(ge=0.0, le=1.0)
    backend_mix_policy: str
    asset_reuse_priority: float = Field(ge=0.0, le=1.0)


class ConferenceProposal(BaseModel):
    proposal_id: str
    lane: ConferenceLane
    policy: ConferencePolicy
    intent: str
    assumptions: list[str] = Field(default_factory=list)


class DepartmentVote(BaseModel):
    role: ConferenceRole
    proposal_id: str
    score: float = Field(ge=0.0, le=1.0)
    veto: bool = False
    reasons: list[str] = Field(default_factory=list)


class ProductionConferenceDecision(BaseModel):
    project_id: str
    proposals: list[ConferenceProposal] = Field(default_factory=list)
    votes: list[DepartmentVote] = Field(default_factory=list)
    selected_proposal_id: str | None = None
    selected_lane: ConferenceLane | None = None
    selected_policy: ConferencePolicy | None = None
    proposal_scores: dict[str, float] = Field(default_factory=dict)
    executable: bool = False
    blockers: list[str] = Field(default_factory=list)
    decision_reasons: list[str] = Field(default_factory=list)


class ProductionConferenceRoom:
    """Evidence-backed pre-production decision board.

    The room does not rewrite creative content. It selects an execution policy
    after research/script analysis and before expensive production begins.
    """

    ROLE_WEIGHTS = {
        ConferenceRole.RESEARCH: 1.00,
        ConferenceRole.WRITER: 1.00,
        ConferenceRole.DIRECTOR: 1.15,
        ConferenceRole.TECHNICAL_DIRECTOR: 1.30,
        ConferenceRole.EDITOR: 0.95,
        ConferenceRole.AUDIO: 0.90,
        ConferenceRole.COMPUTE_FINANCE: 1.10,
    }

    @staticmethod
    def proposals(project_id: str) -> list[ConferenceProposal]:
        return [
            ConferenceProposal(
                proposal_id=f"{project_id}:QUALITY",
                lane=ConferenceLane.QUALITY_FIRST,
                intent=(
                    "protect acting, continuity and finish quality even when "
                    "production requires more candidates and repair passes"
                ),
                policy=ConferencePolicy(
                    optimization_weights={
                        "quality": 0.58,
                        "speed": 0.10,
                        "determinism": 0.22,
                        "availability": 0.10,
                    },
                    render_scale=1.0,
                    candidate_multiplier=1.5,
                    repair_budget=3,
                    qc_target=0.86,
                    continuity_priority=0.96,
                    compute_budget_index=0.90,
                    backend_mix_policy="continuity_first",
                    asset_reuse_priority=0.92,
                ),
            ),
            ConferenceProposal(
                proposal_id=f"{project_id}:BALANCED",
                lane=ConferenceLane.BALANCED,
                intent=(
                    "balance production quality, throughput, determinism and "
                    "currently executable tools"
                ),
                policy=ConferencePolicy(
                    optimization_weights={
                        "quality": 0.46,
                        "speed": 0.22,
                        "determinism": 0.20,
                        "availability": 0.12,
                    },
                    render_scale=1.0,
                    candidate_multiplier=1.0,
                    repair_budget=2,
                    qc_target=0.80,
                    continuity_priority=0.88,
                    compute_budget_index=0.66,
                    backend_mix_policy="selective_scene_mix",
                    asset_reuse_priority=0.84,
                ),
            ),
            ConferenceProposal(
                proposal_id=f"{project_id}:FAST",
                lane=ConferenceLane.FAST_LEAN,
                intent=(
                    "maximize safe throughput and reuse while preserving hard "
                    "authenticity, script-lock and QC constraints"
                ),
                policy=ConferencePolicy(
                    optimization_weights={
                        "quality": 0.32,
                        "speed": 0.38,
                        "determinism": 0.16,
                        "availability": 0.14,
                    },
                    render_scale=0.75,
                    candidate_multiplier=0.5,
                    repair_budget=1,
                    qc_target=0.74,
                    continuity_priority=0.76,
                    compute_budget_index=0.42,
                    backend_mix_policy="minimal_backend_switching",
                    asset_reuse_priority=0.95,
                ),
            ),
        ]

    @staticmethod
    def _prompt_preferences(prompt: str) -> tuple[float, float, float]:
        text = prompt.lower()
        quality_terms = (
            "professional", "cinematic", "high quality", "highest quality",
            "4k", "đẹp", "chuyên nghiệp", "điện ảnh", "chất lượng cao",
        )
        speed_terms = (
            "fast", "quick", "rapid", "nhanh", "tốc độ", "liên tục",
        )
        lean_terms = (
            "cheap", "free", "zero api", "low cost", "rẻ", "miễn phí",
            "không tốn api", "tiết kiệm",
        )
        q = min(1.0, sum(term in text for term in quality_terms) / 2.0)
        s = min(1.0, sum(term in text for term in speed_terms) / 2.0)
        l = min(1.0, sum(term in text for term in lean_terms) / 2.0)
        return q, s, l

    @staticmethod
    def _runtime_readiness(
        kernel: Any,
        kinds: list[CapabilityKind],
        strategy: ProductionStrategy,
    ) -> tuple[float, list[str]]:
        unique = list(dict.fromkeys(kinds))
        if not unique:
            return 1.0, []

        # With a full StudioKernel, reuse the exact same executable-routing
        # gates that Technical Direction will later use. This prevents the
        # conference from treating a declared capability as production-ready.
        if all(
            hasattr(kernel, name)
            for name in (
                "tool_adapters",
                "execution_mastery",
                "production_qualification",
            )
        ):
            planner = SceneToolPlanner(kernel)
            ready = 0
            missing: list[str] = []
            for kind in unique:
                assignment = planner.assign(
                    kind,
                    strategy,
                    authenticity_sensitive=(
                        kind is CapabilityKind.GAME_RUNTIME
                    ),
                )
                if assignment.execution_ready:
                    ready += 1
                else:
                    missing.append(kind.value)
            return ready / len(unique), missing

        # Lightweight fallback for isolated rubric tests.
        ready = 0
        missing = []
        for kind in unique:
            offers = kernel.capabilities.list(kind)
            acceptable = [
                item
                for item in offers
                if item.executable and item.commercial_safe is True
            ]
            if acceptable:
                ready += 1
            else:
                missing.append(kind.value)
        return ready / len(unique), missing

    @staticmethod
    def _profile(pack: ScriptSourcePack | None) -> dict[str, Any]:
        if pack is None or pack.production_profile is None:
            return {}
        return pack.production_profile.model_dump(mode="json")

    def _vote(
        self,
        *,
        role: ConferenceRole,
        proposal: ConferenceProposal,
        project: StudioProjectSpec,
        product: MediaProductSpec,
        strategy: ProductionStrategy,
        script_pack: ScriptSourcePack | None,
        readiness: float,
        hard_missing: list[str],
    ) -> DepartmentVote:
        lane = proposal.lane
        profile = self._profile(script_pack)
        performance = float(profile.get("performance_load", 0.0) or 0.0)
        continuity = float(profile.get("continuity_load", 0.0) or 0.0)
        dialogue = float(profile.get("dialogue_density", 0.0) or 0.0)
        research = float(strategy.research_confidence_score)
        quality_pref, speed_pref, lean_pref = self._prompt_preferences(
            project.prompt
        )
        score = 0.72
        reasons: list[str] = []
        veto = False

        lane_quality = {
            ConferenceLane.QUALITY_FIRST: 1.0,
            ConferenceLane.BALANCED: 0.78,
            ConferenceLane.FAST_LEAN: 0.56,
        }[lane]
        lane_speed = {
            ConferenceLane.QUALITY_FIRST: 0.48,
            ConferenceLane.BALANCED: 0.78,
            ConferenceLane.FAST_LEAN: 1.0,
        }[lane]
        lane_lean = {
            ConferenceLane.QUALITY_FIRST: 0.42,
            ConferenceLane.BALANCED: 0.72,
            ConferenceLane.FAST_LEAN: 1.0,
        }[lane]

        if role is ConferenceRole.RESEARCH:
            score = 0.58 + 0.24 * research
            if lane is ConferenceLane.QUALITY_FIRST and research < 0.35:
                score -= 0.08
                reasons.append("weak research does not justify expensive research-driven embellishment")
            if lane is ConferenceLane.BALANCED:
                score += 0.06
                reasons.append("balanced policy limits overreaction to uncertain patterns")

        elif role is ConferenceRole.WRITER:
            score = 0.62 + 0.22 * lane_quality
            if strategy.script_locked:
                if lane is ConferenceLane.FAST_LEAN:
                    score -= 0.08
                reasons.append("locked script must be preserved regardless of throughput pressure")
            if performance >= 0.65:
                score += 0.12 * lane_quality
                reasons.append("script has high performance load")

        elif role is ConferenceRole.DIRECTOR:
            score = 0.50 + 0.30 * lane_quality
            score += 0.16 * max(performance, continuity) * lane_quality
            if lane is ConferenceLane.FAST_LEAN and continuity >= 0.65:
                score -= 0.10
                reasons.append("high continuity load makes aggressive speed optimization risky")
            if lane is ConferenceLane.QUALITY_FIRST and max(performance, continuity) >= 0.65:
                reasons.append("quality lane protects acting and continuity")

        elif role is ConferenceRole.TECHNICAL_DIRECTOR:
            score = 0.46 + 0.34 * readiness
            score += 0.12 * lane_speed if readiness < 1.0 else 0.08 * lane_quality
            if hard_missing:
                score -= 0.10
                reasons.append("some primary capabilities lack an executable commercial-safe provider")
            if (
                strategy.planning_mode is PlanningMode.AUTHENTIC_GAMEPLAY
                and CapabilityKind.GAME_RUNTIME.value in hard_missing
            ):
                veto = True
                score = 0.0
                reasons.append("authentic gameplay cannot be substituted by another renderer")

        elif role is ConferenceRole.EDITOR:
            score = 0.58 + 0.16 * lane_speed + 0.12 * lane_quality
            if strategy.retention_principles:
                score += 0.05
            if lane is ConferenceLane.FAST_LEAN and continuity >= 0.70:
                score -= 0.08
                reasons.append("editing speed may not override setup/payoff continuity")

        elif role is ConferenceRole.AUDIO:
            score = 0.62 + 0.15 * lane_quality
            if dialogue >= 0.35:
                score += 0.14 * lane_quality
                reasons.append("dialogue density increases intelligibility and timing requirements")
            if (
                CapabilityKind.SPEECH in strategy.script_required_capabilities
                and readiness < 1.0
            ):
                score -= 0.05

        elif role is ConferenceRole.COMPUTE_FINANCE:
            score = 0.50 + 0.20 * lane_speed + 0.20 * lane_lean
            score += 0.08 * readiness
            score += 0.10 * speed_pref * lane_speed
            score += 0.10 * lean_pref * lane_lean
            score += 0.10 * quality_pref * lane_quality
            if lane is ConferenceLane.QUALITY_FIRST and (speed_pref + lean_pref) >= 1.0:
                score -= 0.10
                reasons.append("user prompt explicitly values throughput/cost")

        score += 0.08 * quality_pref * lane_quality
        score += 0.06 * speed_pref * lane_speed
        score += 0.06 * lean_pref * lane_lean
        return DepartmentVote(
            role=role,
            proposal_id=proposal.proposal_id,
            score=round(max(0.0, min(1.0, score)), 4),
            veto=veto,
            reasons=reasons,
        )

    @staticmethod
    def _objective_alignment_bonus(
        lane: ConferenceLane,
        *,
        quality_pref: float,
        speed_pref: float,
        lean_pref: float,
    ) -> float:
        if lane is ConferenceLane.QUALITY_FIRST:
            return (
                0.07 * quality_pref
                - 0.03 * speed_pref
                - 0.03 * lean_pref
            )
        if lane is ConferenceLane.FAST_LEAN:
            return (
                0.06 * speed_pref
                + 0.06 * lean_pref
                - 0.03 * quality_pref
            )
        # Balanced gets a smaller bonus only when the prompt genuinely asks
        # for competing objectives rather than expressing a single clear one.
        conflicting = min(
            quality_pref,
            max(speed_pref, lean_pref),
        )
        return 0.04 * conflicting

    def deliberate(
        self,
        *,
        kernel: Any,
        project: StudioProjectSpec,
        product: MediaProductSpec,
        strategy: ProductionStrategy,
        script_pack: ScriptSourcePack | None = None,
    ) -> ProductionConferenceDecision:
        proposals = self.proposals(project.studio_project_id)
        hard_kinds = list(strategy.primary_capabilities)
        readiness, hard_missing = self._runtime_readiness(
            kernel,
            hard_kinds,
            strategy,
        )
        votes: list[DepartmentVote] = []
        scores: dict[str, float] = {}
        vetoed: set[str] = set()
        (
            quality_pref,
            speed_pref,
            lean_pref,
        ) = self._prompt_preferences(project.prompt)

        for proposal in proposals:
            proposal_votes = [
                self._vote(
                    role=role,
                    proposal=proposal,
                    project=project,
                    product=product,
                    strategy=strategy,
                    script_pack=script_pack,
                    readiness=readiness,
                    hard_missing=hard_missing,
                )
                for role in ConferenceRole
            ]
            votes.extend(proposal_votes)
            if any(item.veto for item in proposal_votes):
                vetoed.add(proposal.proposal_id)
            weighted_total = sum(
                item.score * self.ROLE_WEIGHTS[item.role]
                for item in proposal_votes
            )
            weight_total = sum(
                self.ROLE_WEIGHTS[item.role]
                for item in proposal_votes
            )
            raw_score = weighted_total / weight_total
            raw_score += self._objective_alignment_bonus(
                proposal.lane,
                quality_pref=quality_pref,
                speed_pref=speed_pref,
                lean_pref=lean_pref,
            )
            scores[proposal.proposal_id] = round(
                max(0.0, min(1.0, raw_score)),
                4,
            )

        viable = [
            item
            for item in proposals
            if item.proposal_id not in vetoed
        ]
        blockers: list[str] = []
        if not viable:
            blockers.append(
                "PRODUCTION_CONFERENCE_NO_VIABLE_PROPOSAL"
            )
            if hard_missing:
                blockers.append(
                    "MISSING_PRIMARY_CAPABILITIES:"
                    + ",".join(sorted(hard_missing))
                )
            return ProductionConferenceDecision(
                project_id=project.studio_project_id,
                proposals=proposals,
                votes=votes,
                proposal_scores=scores,
                executable=False,
                blockers=blockers,
                decision_reasons=[
                    "all proposals were vetoed by hard production constraints"
                ],
            )

        selected = max(
            viable,
            key=lambda item: (
                scores[item.proposal_id],
                {
                    ConferenceLane.BALANCED: 2,
                    ConferenceLane.QUALITY_FIRST: 1,
                    ConferenceLane.FAST_LEAN: 0,
                }[item.lane],
            ),
        )
        reasons = [
            f"runtime_readiness={readiness:.3f}",
            f"research_confidence={strategy.research_confidence_score:.3f}",
            f"selected_lane={selected.lane.value}",
            (
                "conference_score="
                f"{scores[selected.proposal_id]:.4f}"
            ),
            (
                "user_objective_preferences="
                f"quality:{quality_pref:.2f},"
                f"speed:{speed_pref:.2f},"
                f"lean:{lean_pref:.2f}"
            ),
        ]
        profile = self._profile(script_pack)
        if profile:
            reasons.append(
                "script_performance_load="
                f"{float(profile.get('performance_load', 0.0) or 0.0):.3f}"
            )
            reasons.append(
                "script_continuity_load="
                f"{float(profile.get('continuity_load', 0.0) or 0.0):.3f}"
            )
        return ProductionConferenceDecision(
            project_id=project.studio_project_id,
            proposals=proposals,
            votes=votes,
            selected_proposal_id=selected.proposal_id,
            selected_lane=selected.lane,
            selected_policy=selected.policy,
            proposal_scores=scores,
            executable=True,
            blockers=[],
            decision_reasons=reasons,
        )

    @staticmethod
    def apply(
        strategy: ProductionStrategy,
        decision: ProductionConferenceDecision,
    ) -> ProductionStrategy:
        if not decision.executable or decision.selected_policy is None:
            return strategy
        policy = decision.selected_policy
        rules = list(strategy.production_rules)
        rules.extend(
            [
                (
                    "production conference lane="
                    + str(decision.selected_lane.value)
                ),
                (
                    "backend mix policy="
                    + policy.backend_mix_policy
                ),
                (
                    "conference QC target="
                    + f"{policy.qc_target:.2f}"
                ),
            ]
        )
        return strategy.model_copy(
            update={
                "optimization_weights": dict(
                    policy.optimization_weights
                ),
                "conference_lane": decision.selected_lane.value,
                "conference_policy": policy.model_dump(mode="json"),
                "conference_score": decision.proposal_scores.get(
                    decision.selected_proposal_id or "",
                    0.0,
                ),
                "production_rules": list(dict.fromkeys(rules)),
            },
            deep=True,
        )
