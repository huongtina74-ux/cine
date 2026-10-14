from __future__ import annotations

import pytest
from pydantic import ValidationError

from cinefactory.studio.contracts import DepartmentId, StudioProjectSpec
from cinefactory.studio.direction import (
    CameraCoverageShot,
    ContinuityValidator,
    DirectorCut,
    DramaticState,
    SceneDramaticSpec,
)
from cinefactory.studio.intelligence import (
    CompetitorVideoProfile,
    NichePlaybookCompiler,
    ObservationType,
    PatternMiner,
    VideoObservation,
)
from cinefactory.studio.project_dna import ProjectDNACompiler
from cinefactory.studio.qc_department import QCDepartment, QCLayer, StudioQCFinding
from cinefactory.studio.tooling import ToolDoctor, ToolSkillRegistry
from cinefactory.studio.control_plane import StudioControlPlane


def test_pattern_miner_requires_cross_video_support():
    profiles = []
    for idx in range(3):
        profiles.append(
            CompetitorVideoProfile(
                video_id=f"V{idx}",
                source_locator=f"https://example/{idx}",
                observations=[
                    VideoObservation(
                        observation_id=f"O{idx}",
                        kind=ObservationType.EDITING,
                        description="cut when information state changes",
                        confidence=0.9,
                    )
                ],
            )
        )
    patterns = PatternMiner().mine(profiles, min_support=2)
    assert len(patterns) == 1
    assert patterns[0].support_count == 3
def test_expression_sensitive_competitor_observation_never_becomes_pattern():
    profiles = [
        CompetitorVideoProfile(
            video_id="V1",
            source_locator="x",
            observations=[
                VideoObservation(
                    observation_id="O1",
                    kind=ObservationType.PACKAGING,
                    description="copy exact thumbnail expression",
                    expression_sensitive=True,
                )
            ],
        ),
        CompetitorVideoProfile(
            video_id="V2",
            source_locator="y",
            observations=[
                VideoObservation(
                    observation_id="O2",
                    kind=ObservationType.PACKAGING,
                    description="copy exact thumbnail expression",
                    expression_sensitive=True,
                )
            ],
        ),
    ]
    assert PatternMiner().mine(profiles) == []


def test_playbook_has_copy_prohibitions():
    playbook = NichePlaybookCompiler().compile("gaming.minecraft", [])
    assert "storyline" in playbook.production_grammar.copy_prohibitions
    assert "branding" in playbook.production_grammar.copy_prohibitions


def test_project_dna_compiler_locks_purposeful_camera():
    project = StudioProjectSpec(prompt="Create a cinematic story")
    plan = StudioControlPlane().plan(project)
    dna = ProjectDNACompiler().compile(project, plan.product)
    assert "no shot without purpose" in dna.camera.grammar
    assert any("persistent entity" in x for x in dna.visual.asset_consistency_rules)
def test_camera_move_requires_purpose():
    with pytest.raises(ValidationError):
        CameraCoverageShot(
            shot_id="S1",
            segment_id="SEG_001",
            purpose="reveal threat",
            scale="CU",
            movement="dolly_in",
        )


def test_continuity_validator_detects_prop_jump():
    cut = DirectorCut(
        project_id="P1",
        segments=[
            SceneDramaticSpec(
                segment_id="SEG_001",
                purpose="setup",
                exit_state=DramaticState(held_props={"HERO": ["SWORD"]}),
            ),
            SceneDramaticSpec(
                segment_id="SEG_002",
                purpose="continuation",
                entry_state=DramaticState(held_props={"HERO": []}),
            ),
        ],
    )
    findings = ContinuityValidator().validate(cut)
    assert findings == ["SEG_002:HERO:HELD_PROP_DISCONTINUITY"]


def test_qc_routes_camera_failure_to_cinematography():
    finding = StudioQCFinding(
        code="CAM_001",
        layer=QCLayer.CAMERA,
        message="subject occluded",
        segment_id="SEG_002",
    )
    assignment = QCDepartment().assign(finding)
    assert assignment.owner is DepartmentId.CINEMATOGRAPHY
    assert assignment.scope == "segment:SEG_002"
def test_tool_doctor_detects_portable_blender(tmp_path):
    exe = tmp_path / ".tools" / "blender-test" / "blender.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"fake")
    env = ToolDoctor(tmp_path).inspect("blender")
    assert env.installed is True
    assert "headless" in env.capabilities


def test_tool_skills_separate_craft_from_implementation():
    skills = ToolSkillRegistry().list("premiere")
    assert len(skills) == 1
    assert skills[0].craft_skill == "editorial"
    assert "UXP API" in skills[0].automation_interfaces


def test_documentary_plan_stays_blocked_until_evidence_is_ready():
    plan = StudioControlPlane().plan(
        StudioProjectSpec(prompt="Documentary about history", duration_seconds=300)
    )
    assert plan.product.evidence_required is True
    assert any("EVIDENCE_MAP_REQUIRED" in item for item in plan.blockers)


def test_actual_gameplay_cannot_silently_use_blender():
    plan = StudioControlPlane().plan(
        StudioProjectSpec(prompt="Minecraft gameplay survival 100 days")
    )
    assert plan.product.actual_gameplay_required is True
    game_routes = [
        route for segment in plan.segments
        for route in segment.routes
        if route.requirement.kind.value == "GAME_RUNTIME"
    ]
    assert game_routes and all(not route.executable for route in game_routes)
