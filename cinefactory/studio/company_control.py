from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def canonical_hash(payload: Any) -> str:
    if isinstance(payload, BaseModel):
        data = payload.model_dump(mode="json", exclude_none=False)
    else:
        data = payload
    encoded = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


class FormatDNA(BaseModel):
    """Versioned channel/format contract. New rules require a new version."""

    model_config = ConfigDict(frozen=True)

    format_id: str
    version: str = "1"
    source_project_id: str
    media_format: str
    platform: str
    domain: str
    niche: str | None = None
    target_duration_seconds: int | None = Field(default=None, gt=0)
    script_rules: dict[str, Any] = Field(default_factory=dict)
    retention_rules: dict[str, Any] = Field(default_factory=dict)
    shot_rules: dict[str, Any] = Field(default_factory=dict)
    visual_rules: dict[str, Any] = Field(default_factory=dict)
    camera_rules: dict[str, Any] = Field(default_factory=dict)
    editing_rules: dict[str, Any] = Field(default_factory=dict)
    audio_rules: dict[str, Any] = Field(default_factory=dict)
    production_rules: dict[str, Any] = Field(default_factory=dict)
    qc_thresholds: dict[str, float] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)

    @property
    def content_hash(self) -> str:
        return canonical_hash(self)


class FormatDNACompiler:
    """Builds a conservative format contract from already-approved project data."""

    @staticmethod
    def _slug(value: str) -> str:
        return "".join(
            ch.lower() if ch.isalnum() else "."
            for ch in value.strip()
        ).strip(".").replace("..", ".")

    def compile(self, *, project, project_dna, product) -> FormatDNA:
        base = project.niche or project.domain or product.format.value
        format_id = self._slug(
            f"{project.platform}.{base}.{product.format.value}"
        )
        return FormatDNA(
            format_id=format_id,
            source_project_id=project.studio_project_id,
            media_format=product.format.value,
            platform=project.platform,
            domain=project.domain,
            niche=project.niche,
            target_duration_seconds=project.duration_seconds,
            script_rules={
                "story_required": product.story_required,
                "evidence_required": product.evidence_required,
            },
            retention_rules={
                "source": "PROJECT_DNA",
                "rules": list(
                    project_dna.editing.pacing_principles
                ),
            },
            shot_rules={
                "motivated_shots_only": True,
                "preserve_screen_direction": True,
            },
            visual_rules={
                "style_principles": list(
                    project_dna.visual.style_principles
                ),
                "asset_consistency_rules": list(
                    project_dna.visual.asset_consistency_rules
                ),
            },
            camera_rules={
                "grammar": list(project_dna.camera.grammar),
                "movement_policy": list(
                    project_dna.camera.movement_policy
                ),
                "continuity_rules": list(
                    project_dna.camera.continuity_rules
                ),
            },
            editing_rules={
                "pacing_principles": list(
                    project_dna.editing.pacing_principles
                ),
                "transition_policy": list(
                    project_dna.editing.transition_policy
                ),
            },
            audio_rules={
                "music_role": project_dna.audio.music_role,
                "ambience_policy": list(
                    project_dna.audio.ambience_policy
                ),
                "mix_priorities": list(
                    project_dna.audio.mix_priorities
                ),
            },
            production_rules={
                "actual_gameplay_required": (
                    product.actual_gameplay_required
                ),
                "brand_compliance_required": (
                    product.brand_compliance_required
                ),
                "silent_tool_substitution_allowed": False,
            },
        )


class ProductionSheetState(StrEnum):
    DRAFT = "DRAFT"
    LOCKED = "LOCKED"
    SUPERSEDED = "SUPERSEDED"


class ProductionSheetShot(BaseModel):
    shot_id: str
    scene_id: str
    duration_seconds: float = Field(gt=0)
    narrative_purpose: str
    camera: dict[str, Any] = Field(default_factory=dict)
    action_beats: list[dict[str, Any]] = Field(default_factory=list)
    edit_intent: str | None = None


class EpisodeProductionSheet(BaseModel):
    project_id: str
    format_id: str
    format_version: str
    format_hash: str
    source_artifact_hashes: dict[str, str]
    shots: list[ProductionSheetShot] = Field(min_length=1)
    production_constraints: dict[str, Any] = Field(default_factory=dict)
    state: ProductionSheetState = ProductionSheetState.DRAFT
    sheet_hash: str | None = None
    locked_at: datetime | None = None

    def _lock_payload(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude={"sheet_hash", "locked_at", "state"},
            exclude_none=False,
        )

    def expected_hash(self) -> str:
        return canonical_hash(self._lock_payload())

    def lock(self) -> "EpisodeProductionSheet":
        if self.state is ProductionSheetState.SUPERSEDED:
            raise ValueError("SUPERSEDED_PRODUCTION_SHEET_CANNOT_LOCK")
        return self.model_copy(
            update={
                "state": ProductionSheetState.LOCKED,
                "sheet_hash": self.expected_hash(),
                "locked_at": utcnow(),
            }
        )

    def verify_lock(self) -> tuple[bool, list[str]]:
        findings: list[str] = []
        if self.state is not ProductionSheetState.LOCKED:
            findings.append("PRODUCTION_SHEET_NOT_LOCKED")
        if not self.sheet_hash:
            findings.append("PRODUCTION_SHEET_HASH_MISSING")
        elif self.sheet_hash != self.expected_hash():
            findings.append("PRODUCTION_SHEET_HASH_MISMATCH")
        return not findings, findings


class ProductionSheetCompiler:
    REQUIRED_SOURCE_ARTIFACTS = (
        "script",
        "director_cut",
        "performance_plan",
        "asset_manifest",
        "shot_book",
        "previs_report",
    )

    def compile(
        self,
        *,
        project_id: str,
        format_dna: FormatDNA,
        shots: list[Any],
        source_artifacts: dict[str, Any],
        production_constraints: dict[str, Any] | None = None,
    ) -> EpisodeProductionSheet:
        missing = [
            name
            for name in self.REQUIRED_SOURCE_ARTIFACTS
            if name not in source_artifacts
        ]
        if missing:
            raise ValueError(
                "PRODUCTION_SHEET_SOURCE_MISSING:" + ",".join(missing)
            )
        refs = {
            name: canonical_hash(source_artifacts[name])
            for name in self.REQUIRED_SOURCE_ARTIFACTS
        }
        rows = [
            ProductionSheetShot(
                shot_id=str(shot.shot_id),
                scene_id=str(shot.scene_id),
                duration_seconds=float(shot.duration_seconds),
                narrative_purpose=str(shot.narrative_purpose),
                camera=shot.camera.model_dump(mode="json"),
                action_beats=[
                    item.model_dump(mode="json")
                    for item in shot.action_beats
                ],
                edit_intent=shot.edit_intent,
            )
            for shot in shots
        ]
        return EpisodeProductionSheet(
            project_id=project_id,
            format_id=format_dna.format_id,
            format_version=format_dna.version,
            format_hash=format_dna.content_hash,
            source_artifact_hashes=refs,
            shots=rows,
            production_constraints=dict(production_constraints or {}),
        ).lock()

    def verify_sources(
        self,
        sheet: EpisodeProductionSheet,
        source_artifacts: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        findings: list[str] = []
        for name, expected_hash in sheet.source_artifact_hashes.items():
            if name not in source_artifacts:
                findings.append(
                    f"PRODUCTION_SHEET_SOURCE_MISSING:{name}"
                )
                continue
            if canonical_hash(source_artifacts[name]) != expected_hash:
                findings.append(
                    f"PRODUCTION_SHEET_SOURCE_DRIFT:{name}"
                )
        return not findings, findings


class GateVerdict(StrEnum):
    PASS = "PASS"
    PASS_WITH_NOTE = "PASS_WITH_NOTE"
    REWORK = "REWORK"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class GateCheck(BaseModel):
    check_id: str
    passed: bool
    required: bool = True
    hard_block: bool = False
    evidence: list[str] = Field(default_factory=list)
    note: str | None = None


class GateDecision(BaseModel):
    gate_id: str
    producer: str
    reviewer: str
    verdict: GateVerdict
    checks: list[GateCheck] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    repair_count: int = Field(default=0, ge=0)


class GateEngine:
    """Common fail-closed gate with reviewer/producer separation."""

    def evaluate(
        self,
        *,
        gate_id: str,
        producer: str,
        reviewer: str,
        checks: list[GateCheck],
        repair_count: int = 0,
        max_repair_rounds: int = 2,
    ) -> GateDecision:
        if producer == reviewer:
            return GateDecision(
                gate_id=gate_id,
                producer=producer,
                reviewer=reviewer,
                verdict=GateVerdict.BLOCK,
                checks=checks,
                notes=["PRODUCER_REVIEWER_SEPARATION_REQUIRED"],
                repair_count=repair_count,
            )
        required_failures = [
            item for item in checks if item.required and not item.passed
        ]
        if any(item.hard_block for item in required_failures):
            verdict = GateVerdict.BLOCK
        elif required_failures:
            verdict = (
                GateVerdict.REWORK
                if repair_count < max_repair_rounds
                else GateVerdict.ESCALATE
            )
        elif any(item.note for item in checks):
            verdict = GateVerdict.PASS_WITH_NOTE
        else:
            verdict = GateVerdict.PASS
        return GateDecision(
            gate_id=gate_id,
            producer=producer,
            reviewer=reviewer,
            verdict=verdict,
            checks=checks,
            notes=[
                item.note
                for item in checks
                if item.note
            ],
            repair_count=repair_count,
        )


class HumanApprovalState(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AUTO_APPROVED = "AUTO_APPROVED"


class HumanApprovalGate(BaseModel):
    gate_id: str
    project_id: str
    purpose: str
    required: bool = True
    state: HumanApprovalState = HumanApprovalState.PENDING
    approver: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    note: str | None = None

    @property
    def executable(self) -> bool:
        if not self.required:
            return True
        return self.state in {
            HumanApprovalState.APPROVED,
            HumanApprovalState.AUTO_APPROVED,
        }


class SpendGatePolicy(BaseModel):
    local_only: bool = True
    max_paid_usd: float = Field(default=0.0, ge=0.0)
    max_pilot_count: int | None = Field(default=None, ge=1)


class SpendGateRequest(BaseModel):
    project_id: str
    all_local: bool
    estimated_paid_usd: float = Field(default=0.0, ge=0.0)
    pilot_count: int = Field(default=1, ge=1)


class SpendGateDecision(BaseModel):
    approved: bool
    reasons: list[str] = Field(default_factory=list)


class SpendGate:
    @staticmethod
    def evaluate(
        request: SpendGateRequest,
        policy: SpendGatePolicy,
    ) -> SpendGateDecision:
        reasons: list[str] = []
        if policy.local_only and not request.all_local:
            reasons.append("NON_LOCAL_EXECUTION_NOT_ALLOWED")
        if request.estimated_paid_usd > policy.max_paid_usd:
            reasons.append("PAID_BUDGET_EXCEEDED")
        if (
            policy.max_pilot_count is not None
            and request.pilot_count > policy.max_pilot_count
        ):
            reasons.append("PILOT_COUNT_EXCEEDS_POLICY")
        return SpendGateDecision(
            approved=not reasons,
            reasons=reasons,
        )
class CostClass(StrEnum):
    GPU = "GPU"
    CPU = "CPU"
    API = "API"
    HUMAN = "HUMAN"
    STORAGE = "STORAGE"


class CostEntry(BaseModel):
    entry_id: str = Field(
        default_factory=lambda: f"COST_{uuid4().hex[:12]}"
    )
    project_id: str
    cost_class: CostClass
    stage_id: str | None = None
    scene_id: str | None = None
    shot_id: str | None = None
    units: float = Field(ge=0.0)
    unit_name: str
    estimated_usd: float = Field(default=0.0, ge=0.0)
    measured: bool = False
    evidence: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class CostLedger(BaseModel):
    project_id: str
    entries: list[CostEntry] = Field(default_factory=list)

    @property
    def total_usd(self) -> float:
        return round(sum(item.estimated_usd for item in self.entries), 6)

    @property
    def measured_total_usd(self) -> float:
        return round(
            sum(
                item.estimated_usd
                for item in self.entries
                if item.measured
            ),
            6,
        )


class CostLedgerStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, project_id: str) -> Path:
        return self.root / f"{project_id}.json"

    def load(self, project_id: str) -> CostLedger:
        path = self._path(project_id)
        if not path.exists():
            return CostLedger(project_id=project_id)
        return CostLedger.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def append(self, entry: CostEntry) -> CostLedger:
        ledger = self.load(entry.project_id)
        ledger.entries.append(entry)
        self._path(entry.project_id).write_text(
            ledger.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return ledger


class DebtSeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TechnicalDebtItem(BaseModel):
    debt_id: str
    title: str
    severity: DebtSeverity
    owner: str
    status: str = "OPEN"
    evidence: list[str] = Field(default_factory=list)
    blocks_production: bool = False
    remediation: str | None = None


class TechnicalDebtRegistry(BaseModel):
    items: list[TechnicalDebtItem] = Field(default_factory=list)

    def production_blockers(self) -> list[TechnicalDebtItem]:
        return [
            item
            for item in self.items
            if item.status == "OPEN" and item.blocks_production
        ]


class RunbookAction(BaseModel):
    action_id: str
    instruction: str
    max_attempts: int = Field(default=1, ge=0, le=10)
    requires_approval: bool = False


class RunbookRule(BaseModel):
    incident_code: str
    actions: list[RunbookAction] = Field(min_length=1)
    fallback: str = "BLOCK_AND_ESCALATE"


class OperationalRunbook(BaseModel):
    version: str = "1"
    rules: list[RunbookRule] = Field(default_factory=list)

    def rule_for(self, incident_code: str) -> RunbookRule | None:
        return next(
            (
                item
                for item in self.rules
                if item.incident_code == incident_code
            ),
            None,
        )


class ScaleLevel(StrEnum):
    VIDEO = "VIDEO"
    CHANNEL = "CHANNEL"
    NICHE = "NICHE"
    PORTFOLIO = "PORTFOLIO"


class ScaleMetric(BaseModel):
    metric_id: str
    passed: bool
    evidence: list[str] = Field(default_factory=list)
    required: bool = True


class ScaleGateDecision(BaseModel):
    level: ScaleLevel
    approved: bool
    blockers: list[str] = Field(default_factory=list)


class ScaleGate:
    REQUIRED_DIMENSIONS = {
        "QUALITY",
        "FINANCE",
        "OPERATIONS",
        "PLATFORM",
        "AUDIENCE",
    }

    def evaluate(
        self,
        *,
        level: ScaleLevel,
        metrics: list[ScaleMetric],
    ) -> ScaleGateDecision:
        by_id = {item.metric_id: item for item in metrics}
        blockers = [
            f"MISSING_SCALE_DIMENSION:{name}"
            for name in sorted(self.REQUIRED_DIMENSIONS - set(by_id))
        ]
        blockers.extend(
            item.metric_id
            for item in metrics
            if item.required and not item.passed
        )
        return ScaleGateDecision(
            level=level,
            approved=not blockers,
            blockers=blockers,
        )
