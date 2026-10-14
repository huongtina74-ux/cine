from pathlib import Path

import pytest
from pydantic import ValidationError

from cinefactory.studio.company_control import (
    CostClass,
    CostEntry,
    CostLedgerStore,
    DebtSeverity,
    EpisodeProductionSheet,
    FormatDNA,
    GateCheck,
    GateEngine,
    GateVerdict,
    OperationalRunbook,
    ProductionSheetCompiler,
    ProductionSheetShot,
    RunbookAction,
    RunbookRule,
    ScaleGate,
    ScaleLevel,
    ScaleMetric,
    SpendGate,
    SpendGatePolicy,
    SpendGateRequest,
    TechnicalDebtItem,
    TechnicalDebtRegistry,
)
from cinefactory.studio.learning import ControlledExperiment


def _format() -> FormatDNA:
    return FormatDNA(
        format_id="youtube.test.animation",
        source_project_id="P1",
        media_format="ANIMATION",
        platform="youtube",
        domain="test",
        target_duration_seconds=600,
        visual_rules={"identity": "locked"},
    )


def test_format_dna_is_immutable_and_hash_stable():
    dna = _format()
    assert dna.content_hash == _format().content_hash
    with pytest.raises(ValidationError):
        dna.version = "2"


def test_gate_engine_enforces_independent_reviewer():
    decision = GateEngine().evaluate(
        gate_id="G1",
        producer="PRODUCTION",
        reviewer="PRODUCTION",
        checks=[GateCheck(check_id="A", passed=True)],
    )
    assert decision.verdict is GateVerdict.BLOCK
    assert "PRODUCER_REVIEWER_SEPARATION_REQUIRED" in decision.notes


def test_gate_engine_reworks_then_escalates():
    check = GateCheck(check_id="QUALITY", passed=False)
    engine = GateEngine()
    assert engine.evaluate(
        gate_id="G2",
        producer="PRODUCTION",
        reviewer="QC",
        checks=[check],
        repair_count=0,
        max_repair_rounds=2,
    ).verdict is GateVerdict.REWORK
    assert engine.evaluate(
        gate_id="G2",
        producer="PRODUCTION",
        reviewer="QC",
        checks=[check],
        repair_count=2,
        max_repair_rounds=2,
    ).verdict is GateVerdict.ESCALATE


def test_hard_gate_blocks_without_repair():
    decision = GateEngine().evaluate(
        gate_id="LICENSE",
        producer="TECHNICAL_DIRECTION",
        reviewer="RIGHTS",
        checks=[
            GateCheck(
                check_id="COMMERCIAL_LICENSE",
                passed=False,
                hard_block=True,
            )
        ],
    )
    assert decision.verdict is GateVerdict.BLOCK


def test_spend_gate_blocks_cloud_and_paid_over_budget():
    decision = SpendGate.evaluate(
        SpendGateRequest(
            project_id="P1",
            all_local=False,
            estimated_paid_usd=1.0,
            pilot_count=4,
        ),
        SpendGatePolicy(
            local_only=True,
            max_paid_usd=0.0,
            max_pilot_count=3,
        ),
    )
    assert decision.approved is False
    assert "NON_LOCAL_EXECUTION_NOT_ALLOWED" in decision.reasons
    assert "PAID_BUDGET_EXCEEDED" in decision.reasons
    assert "PILOT_COUNT_EXCEEDS_POLICY" in decision.reasons


def test_cost_ledger_separates_measured_cost(tmp_path: Path):
    store = CostLedgerStore(tmp_path)
    store.append(
        CostEntry(
            project_id="P1",
            cost_class=CostClass.GPU,
            units=12.5,
            unit_name="gpu_seconds",
            estimated_usd=0.02,
            measured=True,
        )
    )
    store.append(
        CostEntry(
            project_id="P1",
            cost_class=CostClass.API,
            units=1,
            unit_name="request",
            estimated_usd=0.50,
            measured=False,
        )
    )
    ledger = store.load("P1")
    assert ledger.total_usd == 0.52
    assert ledger.measured_total_usd == 0.02


def test_technical_debt_blockers_are_visible():
    registry = TechnicalDebtRegistry(
        items=[
            TechnicalDebtItem(
                debt_id="D1",
                title="runtime unverified",
                severity=DebtSeverity.CRITICAL,
                owner="TECHNICAL_DIRECTION",
                blocks_production=True,
            )
        ]
    )
    assert [item.debt_id for item in registry.production_blockers()] == ["D1"]


def test_runbook_returns_exact_incident_rule():
    runbook = OperationalRunbook(
        rules=[
            RunbookRule(
                incident_code="CUDA_OOM",
                actions=[
                    RunbookAction(
                        action_id="CLEAR_CACHE",
                        instruction="clear cache once",
                    )
                ],
            )
        ]
    )
    assert runbook.rule_for("CUDA_OOM").actions[0].action_id == "CLEAR_CACHE"
    assert runbook.rule_for("UNKNOWN") is None


def test_scale_gate_requires_all_business_dimensions():
    gate = ScaleGate()
    partial = gate.evaluate(
        level=ScaleLevel.CHANNEL,
        metrics=[
            ScaleMetric(metric_id="QUALITY", passed=True),
            ScaleMetric(metric_id="FINANCE", passed=True),
        ],
    )
    assert partial.approved is False
    assert any(
        item.startswith("MISSING_SCALE_DIMENSION:")
        for item in partial.blockers
    )

    complete = gate.evaluate(
        level=ScaleLevel.CHANNEL,
        metrics=[
            ScaleMetric(metric_id=name, passed=True)
            for name in sorted(gate.REQUIRED_DIMENSIONS)
        ],
    )
    assert complete.approved is True


def test_causal_experiment_allows_exactly_one_changed_variable():
    exp = ControlledExperiment(
        control={"model": "wan", "steps": 20},
        variant={"model": "wan", "steps": 24},
    )
    assert exp.changed_variables == ["steps"]

    with pytest.raises(ValidationError):
        ControlledExperiment(
            control={"model": "wan", "steps": 20},
            variant={"model": "ltx", "steps": 24},
        )


def test_production_sheet_lock_detects_tampering():
    sheet = EpisodeProductionSheet(
        project_id="P1",
        format_id="youtube.test.animation",
        format_version="1",
        format_hash="format-hash",
        source_artifact_hashes={"script": "abc"},
        shots=[
            ProductionSheetShot(
                shot_id="SHOT_1",
                scene_id="SCENE_1",
                duration_seconds=3.0,
                narrative_purpose="establish conflict",
            )
        ],
    ).lock()
    passed, findings = sheet.verify_lock()
    assert passed is True
    assert findings == []

    tampered = sheet.model_copy(
        update={
            "shots": [
                ProductionSheetShot(
                    shot_id="SHOT_1",
                    scene_id="SCENE_1",
                    duration_seconds=5.0,
                    narrative_purpose="establish conflict",
                )
            ]
        }
    )
    passed, findings = tampered.verify_lock()
    assert passed is False
    assert "PRODUCTION_SHEET_HASH_MISMATCH" in findings


def test_production_sheet_detects_upstream_source_drift():
    sheet = EpisodeProductionSheet(
        project_id="P1",
        format_id="youtube.test.animation",
        format_version="1",
        format_hash="format-hash",
        source_artifact_hashes={
            "script": "not-the-current-hash",
        },
        shots=[
            ProductionSheetShot(
                shot_id="SHOT_1",
                scene_id="SCENE_1",
                duration_seconds=3.0,
                narrative_purpose="establish conflict",
            )
        ],
    ).lock()
    passed, findings = ProductionSheetCompiler().verify_sources(
        sheet,
        {"script": {"title": "changed"}},
    )
    assert passed is False
    assert "PRODUCTION_SHEET_SOURCE_DRIFT:script" in findings
