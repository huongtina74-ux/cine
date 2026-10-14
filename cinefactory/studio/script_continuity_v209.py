"""v209: Evidence-bounded script continuity, not an invented story quality score.

Structured STATE_ID assertions are machine-checkable. Natural language scenes
cannot be certified as emotionally or causally coherent from field presence.
Independent Script Review / filmed-dailies review remain release prerequisites.
"""
from __future__ import annotations

import re
from typing import Any

from cinefactory.domain.models import ScriptSpec

_STATE_ID = re.compile(r"\bSTATE_ID\s*[:=]\s*([A-Za-z0-9_.-]{2,64})\b")


def _state_id(text: str | None) -> str | None:
    if not text:
        return None
    m = _STATE_ID.search(text)
    return m.group(1) if m else None


def inspect_script_continuity(script: ScriptSpec) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify only provable scene facts; reject real structured contradictions."""
    script = ScriptSpec.model_validate(script)
    findings: list[dict[str, str]] = []
    verified_handoffs: list[dict[str, Any]] = []
    scene_ids = [s.scene_id for s in script.scenes]
    for scene in script.scenes:
        if (not scene.dramatic_event.strip()
                or (not any(a.strip() for a in scene.action)
                    and not any(line.text.strip() for line in scene.dialogue))):
            findings.append({
                "code": "SCENE_WITHOUT_OBSERVABLE_ACTION_OR_DIALOGUE",
                "severity": "BLOCKER",
                "scene_id": scene.scene_id,
                "reason": "Dramatic claim alone is not a filmed action/line.",
            })
        if not scene.location_id.strip() or not scene.time_of_day.strip():
            findings.append({
                "code": "SCENE_LOCATION_TIME_UNSPECIFIED",
                "severity": "BLOCKER",
                "scene_id": scene.scene_id,
                "reason": "Required scene staging coordinates are missing.",
            })
    for before, after in zip(script.scenes, script.scenes[1:]):
        previous_state = _state_id(before.exit_state_summary)
        next_state = _state_id(after.entry_state_summary)
        if previous_state and next_state and previous_state != next_state:
            findings.append({
                "code": "CONTRADICTORY_DECLARED_WORLD_STATE",
                "severity": "BLOCKER",
                "scene_id": after.scene_id,
                "reason": (f"Previous exit state {previous_state!r} differs from "
                           f"following entry {next_state!r}."),
            })
        verified_handoffs.append({
            "from": before.scene_id,
            "to": after.scene_id,
            "exit_state_id": previous_state,
            "entry_state_id": next_state,
            "structured_state_compatible": (
                previous_state == next_state if previous_state and next_state else None
            ),
            "causality_proven": False,
            "physical_screen_direction_proven": False,
            "performance_identity_proven": False,
        })
    blockers = [x for x in findings if x["severity"] == "BLOCKER"]
    return ({
        "schema": "cine.script.continuity_report.v209",
        "passed": not blockers,
        "status": ("BLOCKED_MECHANICAL_CONTRADICTIONS" if blockers
                   else "STRUCTURAL_CHECK_PASSED_SEMANTIC_REVIEW_PENDING"),
        "scene_count": len(script.scenes),
        "findings": findings,
        "structured_handoffs_checked": len(verified_handoffs),
        "independent_narrative_quality_qualified": False,
        "causal_motivation_qualified": False,
        "acting_and_camera_continuity_qualified": False,
        "requires_independent_script_and_dailies_reviews": True,
    }, {
        "schema": "cine.script.continuity_contract.v209",
        "ordered_scene_ids": scene_ids,
        "scene_transitions": verified_handoffs,
        "must_verify_emotions_and_stakes": True,
        "must_verify_spatial_and_visual_continuity": True,
        "independently_approved": False,
    })
