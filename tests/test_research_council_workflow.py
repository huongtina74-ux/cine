import json
from types import SimpleNamespace

import pytest

from cinefactory.research_intelligence.council import collect_evidence, decide_council
from cinefactory.research_intelligence.workflow import create_round_tasks, parse_claude_opinion
from cinefactory.research_intelligence.council_learning import build_joint_experiment
from cinefactory.research_intelligence import claude_bridge

ISSUE = {"issue_id": "asmr-originality-01", "question": "Test a new ASMR original audio pattern?"}


@pytest.fixture
def fixture(tmp_path):
    observation = tmp_path / "reference.json"
    observation.write_text(json.dumps({"schema": "cine.research.observation.v1", "frames": [], "source": "ref.mp4"}), encoding="utf-8")
    metrics = tmp_path / "owner.csv"
    metrics.write_text("owned-channel snapshot", encoding="utf-8")
    registry = collect_evidence([
        {"evidence_id": "ref", "kind": "observation", "path": str(observation),
         "independent_root": "competitor-ref", "verified_by": "local_machine"},
        {"evidence_id": "owned", "kind": "owned_analytics", "path": str(metrics),
         "independent_root": "owned-channel", "verified_by": "authorized_owner"},
    ], tmp_path / "registry.json")
    return observation, registry


def owned_feedback(ledger, metrics):
    return {"schema": "cine.research.feedback.v1", "produced_source": "owned.mp4",
            "owned_video_id": "abcdefghijk", "owned_metrics": metrics,
            "owned_analytics_provenance": {
                "sha256": next(s["sha256"] for s in ledger["sources"] if s["kind"] == "owned_analytics"),
                "channel_id": "UC-owned", "period_start": "2026-10-01", "period_end": "2026-10-08"}}


def make_opinion(task, *, stance="SUPPORT", evidence=None):
    return {
        "issue_id": task["council_issue"]["issue_id"],
        "department": task["department"], "round": task["council_round"],
        "stance": stance, "evidence_ids": evidence or ["ref"], "rationale": "Original idea needs controlled testing",
        "confidence": 0.55,
        "responds_to": (["quality"] if task["department"] != "quality" else ["research"]) if task["council_round"] == "rebuttal" else [],
        "proposed_test": "Pilot an original audio mix"
    }


def test_round_tasks_have_one_question_and_shared_registry(fixture, tmp_path):
    video, ledger = fixture
    result = create_round_tasks(ISSUE, ledger, video, tmp_path / "round", niche="ASMR sleep")
    assert len(result["tasks"]) == 4
    assert all(t["council_issue"] == ISSUE for t in result["tasks"])
    assert all(t["approval_status"] == "pending_approval" for t in result["tasks"])
    assert len({t["council_registry_path"] for t in result["tasks"]}) == 1
    assert set(t["shared_evidence_ids"] for t in []) == set()


def test_mocked_claude_to_evidence_validated_council_learning(fixture, tmp_path, monkeypatch):
    video, ledger = fixture
    batch = create_round_tasks(ISSUE, ledger, video, tmp_path / "tasks", niche="ASMR sleep", approved=True)
    tasks = batch["tasks"]
    # Read-only mocked Claude Code subprocess: no paid inference or service call.
    monkeypatch.setattr(claude_bridge.shutil, "which", lambda _: "claude")
    def runner(argv, **kwargs):
        task_data = json.loads(next(x for x in argv if isinstance(x, str) and x.startswith("You are CineFactory")).split("Your authorized task: ", 1)[1].split("\nEvidence:", 1)[0])
        payload = make_opinion(task_data, evidence=["owned"] if task_data["department"] == "quality" else ["ref"])
        return SimpleNamespace(returncode=0, stdout=json.dumps({"result": json.dumps(payload)}), stderr="")
    monkeypatch.setattr(claude_bridge.subprocess, "run", runner)
    opinions = []
    for task in tasks:
        task_file = tmp_path / "tasks" / "tasks" / f"{task['department']}_initial.json"
        result = claude_bridge.run_approved_task(str(task_file), str(tmp_path / f"{task['department']}.claude.json"))
        opinions.append(parse_claude_opinion(task, result, ledger, tmp_path / f"{task['department']}.opinion.json"))
    opening = decide_council(ISSUE, ledger, opinions)
    assert opening["state"] == "NEEDS_CROSS_EXAM"
    next_round = create_round_tasks(ISSUE, ledger, video, tmp_path / "rebuttal", niche="ASMR sleep",
                                    round="rebuttal", previous_opinions=opinions, approved=True)
    for task in next_round["tasks"]:
        file = tmp_path / "rebuttal" / "tasks" / f"{task['department']}_rebuttal.json"
        result = claude_bridge.run_approved_task(str(file), str(tmp_path / f"{task['department']}.rebuttal.claude.json"))
        opinions.append(parse_claude_opinion(task, result, ledger, tmp_path / f"{task['department']}.rebuttal.opinion.json"))
    decision = decide_council(ISSUE, ledger, opinions)
    assert decision["state"] == "SUPPORTED_FOR_TEST"
    feedback = owned_feedback(ledger, {"ctr": 0.05, "views": 150})
    qc = {"schema": "cine.research.production_qc.v1", "source": "owned.mp4", "passed": True}
    experiment = build_joint_experiment(decision, feedback, qc, ledger, tmp_path / "experiment.json")
    assert experiment["release_approved"] is False
    assert experiment["learned_policy_applied"] is False


def test_rebuttal_round_passes_peer_positions(fixture, tmp_path):
    video, ledger = fixture
    initial = create_round_tasks(ISSUE, ledger, video, tmp_path / "initial", niche="ASMR")
    positions = [make_opinion(t, stance="UNKNOWN" if t["department"] == "quality" else "SUPPORT") for t in initial["tasks"]]
    followup = create_round_tasks(ISSUE, ledger, video, tmp_path / "rebuttal", niche="ASMR",
                                  round="rebuttal", previous_opinions=positions)
    assert len(followup["tasks"]) == len(initial["tasks"])
    assert all(task["council_round"] == "rebuttal" for task in followup["tasks"])
    assert all(task["peer_positions"] for task in followup["tasks"])


def test_import_rejects_incorrect_agent_identity(fixture, tmp_path):
    video, ledger = fixture
    task = create_round_tasks(ISSUE, ledger, video, tmp_path / "run", niche="ASMR", approved=True)["tasks"][0]
    payload = make_opinion(task)
    payload["issue_id"] = "other-question"
    result = {"schema": "cine.research.claude_result.v1", "task_id": task["task_id"], "exit_code": 0,
              "stdout": json.dumps({"result": json.dumps(payload)})}
    with pytest.raises(ValueError, match="canonical"):
        parse_claude_opinion(task, result, ledger, tmp_path / "ignored.json")


def test_cannot_learn_from_conflict_or_failed_qc(fixture, tmp_path):
    video, ledger = fixture
    batch = create_round_tasks(ISSUE, ledger, video, tmp_path / "tasks", niche="ASMR")
    opinions = [make_opinion(t, stance="OPPOSE" if t["department"] == "quality" else "SUPPORT") for t in batch["tasks"]]
    decision = decide_council(ISSUE, ledger, opinions)
    feedback = owned_feedback(ledger, {"views": 100})
    qc = {"schema": "cine.research.production_qc.v1", "source": "owned.mp4", "passed": True}
    with pytest.raises(PermissionError):
        build_joint_experiment(decision, feedback, qc, ledger, tmp_path / "should_not.json")
    opinions[-1] = make_opinion(batch["tasks"][-1], evidence=["owned"])
    rebuttal = create_round_tasks(ISSUE, ledger, video, tmp_path / "followup", niche="ASMR", round="rebuttal", previous_opinions=opinions)
    opinions += [make_opinion(task, evidence=["owned"] if task["department"] == "quality" else ["ref"]) for task in rebuttal["tasks"]]
    decision = decide_council(ISSUE, ledger, opinions)
    assert decision["state"] == "SUPPORTED_FOR_TEST"
    with pytest.raises(ValueError, match="QC"):
        build_joint_experiment(decision, feedback, {**qc, "passed": False}, ledger, tmp_path / "still_no.json")


def test_case_manifest_is_single_current_answer_and_history_retained(fixture, tmp_path):
    from pathlib import Path
    from cinefactory.research_intelligence.case_controller import consolidate_case
    video, ledger = fixture
    batch = create_round_tasks(ISSUE, ledger, video, tmp_path / "tasks", niche="ASMR")
    opening = [make_opinion(t, evidence=["owned"] if t["department"] == "quality" else ["ref"]) for t in batch["tasks"]]
    first = consolidate_case(ISSUE, ledger, opening, tmp_path / "case")
    assert first["decision_state"] == "NEEDS_CROSS_EXAM"
    first_file = Path(first["authoritative_decision"])
    assert first_file.exists()
    followup = create_round_tasks(ISSUE, ledger, video, tmp_path / "rebuttal", niche="ASMR",
                                  round="rebuttal", previous_opinions=opening)
    second = [make_opinion(t, evidence=["owned"] if t["department"] == "quality" else ["ref"]) for t in followup["tasks"]]
    feedback = owned_feedback(ledger, {"views": 1000})
    qc = {"schema": "cine.research.production_qc.v1", "source": "owned.mp4", "passed": True}
    updated = consolidate_case(ISSUE, ledger, opening + second, tmp_path / "case", feedback=feedback, technical_qc=qc)
    assert updated["decision_state"] == "SUPPORTED_FOR_TEST"
    assert updated["revision"] != first["revision"]
    assert Path(updated["experiment"]).exists()
    assert first_file.exists()
    assert updated["releases_permitted"] is False
    assert json.loads((tmp_path / "case" / "case.json").read_text(encoding="utf-8"))["revision"] == updated["revision"]


def test_identical_evidence_cannot_claim_two_independent_roots(tmp_path):
    from cinefactory.research_intelligence.council import collect_evidence
    source = tmp_path / "same.json"
    source.write_text("data", encoding="utf-8")
    with pytest.raises(ValueError, match="Identical"):
        collect_evidence([
            {"evidence_id": "x1", "kind": "observation", "path": str(source), "independent_root": "one", "verified_by": "local_machine"},
            {"evidence_id": "x2", "kind": "observation", "path": str(source), "independent_root": "two", "verified_by": "local_machine"},
        ], tmp_path / "ledger.json")


def test_council_learning_rejects_unlinked_analytics(fixture, tmp_path):
    video, registry = fixture
    opening = create_round_tasks(ISSUE, registry, video, tmp_path / "initial", niche="ASMR")["tasks"]
    prior = [make_opinion(t, evidence=["owned"] if t["department"] == "quality" else ["ref"]) for t in opening]
    followup = create_round_tasks(ISSUE, registry, video, tmp_path / "rebuttal", niche="ASMR",
                                  round="rebuttal", previous_opinions=prior)["tasks"]
    final = [make_opinion(t, evidence=["owned"] if t["department"] == "quality" else ["ref"]) for t in followup]
    decision = decide_council(ISSUE, registry, prior + final)
    qc = {"schema": "cine.research.production_qc.v1", "source": "owned.mp4", "passed": True}
    wrong = owned_feedback(registry, {"ctr": 0.07})
    wrong["owned_analytics_provenance"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="frozen source"):
        build_joint_experiment(decision, wrong, qc, registry, tmp_path / "bad.json")
    assert not (tmp_path / "bad.json").exists()
