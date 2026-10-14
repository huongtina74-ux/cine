from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from cinefactory.domain.models import (
    DialogueLine,
    ScriptScene,
    ScriptSpec,
)
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_handlers import (
    FilmCompanyHandlers,
    FilmHandlerConfig,
)
from cinefactory.studio.company_runner import StageExecutionContext
from cinefactory.studio.contracts import (
    MediaFormat,
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)
from cinefactory.studio.control_plane import StudioControlPlane
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.script_intelligence import (
    ScriptInputCompiler,
    ScriptSourceMode,
)


def _structured_script() -> ScriptSpec:
    return ScriptSpec(
        title="Locked User Script",
        logline="A courier must choose between speed and honesty.",
        scenes=[
            ScriptScene(
                scene_id="S01",
                heading="INT. WAREHOUSE - DAY",
                location_id="LOC01",
                time_of_day="DAY",
                dramatic_event="The courier finds the wrong package.",
                action=["A sealed package sits under the wrong label."],
                dialogue=[
                    DialogueLine(
                        speaker="MIA",
                        text="This is not the package I was assigned.",
                    )
                ],
                exit_state_summary="Mia decides to investigate.",
            ),
            ScriptScene(
                scene_id="S02",
                heading="EXT. LOADING BAY - DAY",
                location_id="LOC02",
                time_of_day="DAY",
                dramatic_event="Mia returns the package despite the delay.",
                action=["Mia hands the package back to dispatch."],
                dialogue=[],
                exit_state_summary="The package is corrected.",
            ),
        ],
    )


def test_structured_user_script_compiles_without_rewrite(tmp_path: Path):
    script = _structured_script()
    item = PlanningInputRef(
        input_id="PIN_SCRIPT_JSON",
        kind=PlanningInputKind.SCRIPT,
        content=script.model_dump_json(),
        metadata={"revision_policy": "LOCK"},
    )

    pack = ScriptInputCompiler(tmp_path).compile([item])

    assert pack.mode is ScriptSourceMode.LOCKED_SCRIPT
    assert pack.primary_input_id == "PIN_SCRIPT_JSON"
    assert pack.compiled_script == script.model_dump(mode="json")
    assert pack.compiled_story is not None
    assert pack.primary_content_sha256
    assert pack.revision_policy.value == "LOCK"


def test_plain_screenplay_preserves_scene_dialogue_and_action(tmp_path: Path):
    screenplay = """Courier Test

INT. WAREHOUSE - DAY

MIA
This is not my package.

She checks the label twice.

EXT. LOADING BAY - DAY

DISPATCHER
You will miss the deadline.

Mia returns the package anyway.
"""
    item = PlanningInputRef(
        kind=PlanningInputKind.SCRIPT,
        title="Courier Test",
        content=screenplay,
    )

    pack = ScriptInputCompiler(tmp_path).compile([item])
    script = ScriptSpec.model_validate(pack.compiled_script)

    assert len(script.scenes) == 2
    assert script.scenes[0].dialogue[0].speaker == "MIA"
    assert (
        script.scenes[0].dialogue[0].text
        == "This is not my package."
    )
    assert "She checks the label twice." in script.scenes[0].action
    assert script.scenes[0].dramatic_event
    assert script.scenes[0].dramatic_event.strip()
    assert script.scenes[1].dialogue[0].speaker == "DISPATCHER"
    assert "Mia returns the package anyway." in script.scenes[1].action


def test_outline_compiles_to_story_for_writer_expansion(tmp_path: Path):
    outline = """- A child discovers a hidden door.
- The door leads to a dangerous test.
- The child chooses to help a rival.
- Both escape and return home changed.
"""
    item = PlanningInputRef(
        input_id="PIN_OUTLINE",
        kind=PlanningInputKind.SCRIPT_OUTLINE,
        title="Hidden Door",
        content=outline,
    )

    pack = ScriptInputCompiler(tmp_path).compile([item])

    assert pack.mode is ScriptSourceMode.OUTLINE
    assert pack.compiled_script is None
    assert pack.compiled_story is not None
    assert len(pack.compiled_story["beats"]) == 4
    assert (
        pack.compiled_story["beats"][0]["change"]
        == "A child discovers a hidden door."
    )


def test_reference_script_is_quarantined_and_only_patterns_escape(
    tmp_path: Path,
):
    secret = "UNIQUE COMPETITOR DIALOGUE MUST NEVER ESCAPE"
    reference = f"""INT. ROOM - NIGHT

VILLAIN
{secret}

The hero turns away.
"""
    item = PlanningInputRef(
        input_id="PIN_REF_SCRIPT",
        kind=PlanningInputKind.REFERENCE_SCRIPT,
        content=reference,
    )

    pack = ScriptInputCompiler(tmp_path).compile([item])
    serialized = pack.model_dump_json()

    assert secret not in serialized
    assert pack.reference_script_analyses
    assert pack.reference_script_patterns
    assert (
        pack.reference_script_analyses[0].raw_expression_allowed
        is False
    )
    quarantine = (
        tmp_path
        / "data"
        / "studio"
        / "script_intelligence"
        / "quarantine"
    )
    assert list(quarantine.rglob("reference_script.txt"))


def test_company_writing_uses_user_script_instead_of_prompt_scaffold(
    tmp_path: Path,
):
    studio = build_studio_kernel(tmp_path)
    runtime = SimpleNamespace(root=tmp_path, studio=studio)
    script = _structured_script()
    project = StudioProjectSpec(
        prompt="Make a completely different generic movie prompt",
        domain="animation",
        planning_inputs=[
            PlanningInputRef(
                input_id="PIN_LOCKED",
                kind=PlanningInputKind.SCRIPT,
                content=script.model_dump_json(),
            )
        ],
    )
    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    registry = FilmCompanyHandlers(
        runtime,
        config=FilmHandlerConfig(
            production_mode="slate",
            allow_diagnostic_slate=True,
        ),
    ).registry()

    for stage_id in (
        "INTELLIGENCE",
        "CREATIVE_STRATEGY",
        "PLANNING",
        "WRITING",
    ):
        stage = next(
            item
            for item in blueprint.stages
            if item.stage_id == stage_id
        )
        result = registry.get(stage_id)(
            StageExecutionContext(
                blueprint=blueprint,
                stage=stage,
                kernel=runtime,
                project_root=tmp_path / "project",
            )
        )
        assert result.ok is True, result.error

    written = studio.blackboard.get(
        project.studio_project_id,
        "script",
    )["payload"]
    source_pack = studio.blackboard.get(
        project.studio_project_id,
        "script_source_pack",
    )["payload"]
    strategy = studio.blackboard.get(
        project.studio_project_id,
        "production_strategy",
    )["payload"]

    assert written == script.model_dump(mode="json")
    assert source_pack["mode"] == "LOCKED_SCRIPT"
    assert strategy["script_source_mode"] == "LOCKED_SCRIPT"
    assert strategy["script_locked"] is True
    assert (
        written["title"]
        != "Make a completely different generic movie prompt"
    )


def test_reference_script_patterns_enter_planning_without_expression(
    tmp_path: Path,
):
    secret = "EXACT REFERENCE SCRIPT WORDING"
    compiler = ScriptInputCompiler(tmp_path)
    pack = compiler.compile(
        [
            PlanningInputRef(
                kind=PlanningInputKind.REFERENCE_SCRIPT,
                content=(
                    "INT. LAB - DAY\n\nSCIENTIST\n"
                    + secret
                    + "\n\nEXT. STREET - NIGHT\n\nThe chase begins."
                ),
            )
        ]
    )

    serialized = json.dumps(
        pack.model_dump(mode="json"),
        ensure_ascii=False,
    )
    assert secret not in serialized
    assert any(
        "scene" in pattern.lower()
        or "dialogue" in pattern.lower()
        or "action" in pattern.lower()
        for pattern in pack.reference_script_patterns
    )


def test_owned_script_signal_can_drive_format_classification():
    project = StudioProjectSpec(
        prompt="Make a video from my script",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT,
                content=(
                    "ROBLOX ANIMATION\n\n"
                    "INT. SCHOOL - DAY\n"
                    "A block character enters the classroom."
                ),
            )
        ],
    )

    plan = StudioControlPlane().plan(project)

    assert plan.product.format is MediaFormat.ANIMATION
    assert plan.product.actual_gameplay_required is False
    assert (
        plan.product.constraints.get("domain")
        == "gaming.roblox"
    )


def test_reference_script_does_not_drive_project_format():
    project = StudioProjectSpec(
        prompt="Make an original story video",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.REFERENCE_SCRIPT,
                content=(
                    "ROBLOX GAMEPLAY WALKTHROUGH SPEEDRUN\n"
                    "Exact reference structure should not classify the project."
                ),
            )
        ],
    )

    plan = StudioControlPlane().plan(project)

    assert plan.product.format is MediaFormat.NARRATIVE
    assert plan.product.actual_gameplay_required is False


def test_company_blueprint_quarantines_reference_script_before_persistence(
    tmp_path: Path,
):
    studio = build_studio_kernel(tmp_path)
    secret = "REFERENCE SECRET DIALOGUE MUST NOT ENTER BLUEPRINT"
    project = StudioProjectSpec(
        prompt="Create an original animation story",
        planning_inputs=[
            PlanningInputRef(
                input_id="PIN_USER",
                kind=PlanningInputKind.SCRIPT,
                content=_structured_script().model_dump_json(),
            ),
            PlanningInputRef(
                input_id="PIN_REFERENCE",
                kind=PlanningInputKind.REFERENCE_SCRIPT,
                title="Secret Reference Title",
                content=(
                    "INT. SECRET ROOM - NIGHT\n\n"
                    "VILLAIN\n"
                    + secret
                    + "\n\nThe door closes."
                ),
            ),
        ],
    )

    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    serialized = blueprint.model_dump_json()

    assert secret not in serialized
    assert "Secret Reference Title" not in serialized
    assert blueprint.script_source_pack is not None
    assert blueprint.script_source_pack.reference_script_patterns
    assert (
        blueprint.script_source_pack.raw_reference_expression_allowed
        is False
    )

    reference_input = next(
        item
        for item in blueprint.project.planning_inputs
        if item.input_id == "PIN_REFERENCE"
    )
    assert reference_input.content is None
    assert reference_input.uri is None
    assert reference_input.title is None
    assert reference_input.metadata["quarantined"] is True
    assert reference_input.metadata["content_sha256"]

    user_script = next(
        item
        for item in blueprint.project.planning_inputs
        if item.input_id == "PIN_USER"
    )
    assert user_script.content is not None
    assert "Locked User Script" in user_script.content


def test_user_script_and_reference_script_can_coexist_without_reference_leak(
    tmp_path: Path,
):
    studio = build_studio_kernel(tmp_path)
    runtime = SimpleNamespace(root=tmp_path, studio=studio)
    script = _structured_script()
    secret = "DO NOT BORROW THIS REFERENCE LINE"
    project = StudioProjectSpec(
        prompt="Use my script and only learn abstract structure from reference",
        planning_inputs=[
            PlanningInputRef(
                input_id="PIN_PRIMARY_SCRIPT",
                kind=PlanningInputKind.SCRIPT,
                content=script.model_dump_json(),
                metadata={"revision_policy": "LOCK"},
            ),
            PlanningInputRef(
                input_id="PIN_REF",
                kind=PlanningInputKind.REFERENCE_SCRIPT,
                content=(
                    "INT. LAB - DAY\n\nSCIENTIST\n"
                    + secret
                    + "\n\nEXT. STREET - NIGHT\n\nA chase begins."
                ),
            ),
        ],
    )
    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    registry = FilmCompanyHandlers(
        runtime,
        config=FilmHandlerConfig(
            production_mode="slate",
            allow_diagnostic_slate=True,
        ),
    ).registry()

    for stage_id in (
        "INTELLIGENCE",
        "CREATIVE_STRATEGY",
        "PLANNING",
        "WRITING",
    ):
        stage = next(
            item
            for item in blueprint.stages
            if item.stage_id == stage_id
        )
        result = registry.get(stage_id)(
            StageExecutionContext(
                blueprint=blueprint,
                stage=stage,
                kernel=runtime,
                project_root=tmp_path / "project",
            )
        )
        assert result.ok is True, result.error

    written = studio.blackboard.get(
        project.studio_project_id,
        "script",
    )["payload"]
    strategy = studio.blackboard.get(
        project.studio_project_id,
        "production_strategy",
    )["payload"]
    patterns = studio.blackboard.get(
        project.studio_project_id,
        "reference_pattern_map",
    )["payload"]

    serialized = json.dumps(
        {
            "script": written,
            "strategy": strategy,
            "patterns": patterns,
        },
        ensure_ascii=False,
    )
    assert written == script.model_dump(mode="json")
    assert secret not in serialized
    assert strategy["script_source_mode"] == "LOCKED_SCRIPT"
    assert strategy["script_locked"] is True
    assert any(
        item["source_kind"] == "REFERENCE_SCRIPT"
        for item in patterns["patterns"]
    )


def test_script_production_profile_drives_duration_and_voice_requirements(
    tmp_path: Path,
):
    studio = build_studio_kernel(tmp_path)
    script = _structured_script()
    project = StudioProjectSpec(
        prompt="Create from my Roblox animation script",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT,
                content=script.model_dump_json(),
                metadata={"revision_policy": "LOCK"},
            )
        ],
    )

    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    profile = blueprint.script_source_pack.production_profile

    assert profile is not None
    assert profile.scene_count == 2
    assert profile.dialogue_line_count == 1
    assert profile.dialogue_present is True
    assert profile.estimated_duration_seconds > 0
    assert (
        blueprint.project.duration_seconds
        == int(round(profile.estimated_duration_seconds))
    )

    runtime = SimpleNamespace(root=tmp_path, studio=studio)
    registry = FilmCompanyHandlers(
        runtime,
        config=FilmHandlerConfig(
            production_mode="slate",
            allow_diagnostic_slate=True,
        ),
    ).registry()
    for stage_id in (
        "INTELLIGENCE",
        "CREATIVE_STRATEGY",
        "PLANNING",
        "WRITING",
    ):
        stage = next(
            item for item in blueprint.stages
            if item.stage_id == stage_id
        )
        result = registry.get(stage_id)(
            StageExecutionContext(
                blueprint=blueprint,
                stage=stage,
                kernel=runtime,
                project_root=tmp_path / "project",
            )
        )
        assert result.ok is True, result.error

    strategy = studio.blackboard.get(
        project.studio_project_id,
        "production_strategy",
    )["payload"]
    assert strategy["script_production_profile"]["scene_count"] == 2
    assert "SPEECH" in strategy["script_required_capabilities"]
    assert "LIPSYNC" in strategy["script_required_capabilities"]


def test_explicit_duration_overrides_script_estimate(tmp_path: Path):
    studio = build_studio_kernel(tmp_path)
    project = StudioProjectSpec(
        prompt="Create from my script",
        duration_seconds=600,
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT,
                content=_structured_script().model_dump_json(),
            )
        ],
    )

    blueprint = CompanyOrchestrator(studio).build_blueprint(project)

    assert blueprint.script_source_pack.production_profile is not None
    assert blueprint.project.duration_seconds == 600


def test_outline_profile_is_advisory_until_full_script_exists(
    tmp_path: Path,
):
    studio = build_studio_kernel(tmp_path)
    project = StudioProjectSpec(
        prompt="Expand my animation outline",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT_OUTLINE,
                content=(
                    "- The hero discovers the problem.\n"
                    "- A rival blocks the path.\n"
                    "- They cooperate.\n"
                    "- They resolve the conflict."
                ),
            )
        ],
    )

    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    profile = blueprint.script_source_pack.production_profile

    assert profile is not None
    assert profile.duration_estimate_basis == "outline_heuristic_only"
    assert profile.scene_count == 4
    assert profile.dialogue_present is False
    assert blueprint.project.duration_seconds == int(
        round(profile.estimated_duration_seconds)
    )
