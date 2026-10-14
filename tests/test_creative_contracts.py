from pathlib import Path

import pytest

from cinefactory.core.policy import FactoryPolicy
from cinefactory.creative.contracts import CreativeContractError, CreativeValidator
from cinefactory.creative.store import CreativeStore
from cinefactory.domain.enums import ProjectState
from cinefactory.domain.models import (
    ActionBeat,
    AssetBibleSpec,
    BlockingMap,
    BlockingPosition,
    CameraMove,
    CameraSpec,
    CharacterAssetSpec,
    CharacterState,
    DirectorPlan,
    PerformancePlan,
    ProjectSpec,
    SceneAssetSpec,
    SceneDirection,
    ScriptScene,
    ScriptSpec,
    ShotSpec,
    StoryBeat,
    StorySpec,
    WorldState,
)
from cinefactory.pipeline.creative import CreativePipeline
from cinefactory.pipeline.orchestrator import PipelineOrchestrator
from cinefactory.storage.database import AuditLogRepository, Database, SqlProjectRepository

ROOT = Path(__file__).resolve().parents[1]


def make_pipeline(tmp_path):
    db = Database(f"sqlite:///{tmp_path / 'creative.db'}")
    db.create_schema()
    projects = SqlProjectRepository(db)
    audit = AuditLogRepository(db)
    policy = FactoryPolicy.from_yaml(ROOT / "config" / "factory_policy.yaml")
    orch = PipelineOrchestrator(policy, projects, audit)
    return orch, CreativePipeline(CreativeStore(tmp_path / "projects"), orch)


def fixtures():
    story = StorySpec(
        title="The House",
        premise="A daughter discovers her father sold the house to pay for her mother's care.",
        protagonist_goal="understand the truth",
        central_conflict="the father hides his sacrifice",
        ending_state="daughter understands the sacrifice",
        beats=[StoryBeat(beat_id="B1", purpose="reveal", change="understand the truth")],
    )
    script = ScriptSpec(
        title="The House",
        logline="A daughter tries to understand the truth behind the missing house deed.",
        scenes=[
            ScriptScene(
                scene_id="SC01",
                heading="INT. KITCHEN - NIGHT",
                location_id="KITCHEN",
                time_of_day="night",
                dramatic_event="daughter notices the missing deed",
                action=["She places the empty folder on the table."],
            )
        ],
    )
    bible = AssetBibleSpec(
        characters=[
            CharacterAssetSpec(
                character_id="C01",
                name="Daughter",
                identity_lock="same oval face, shoulder-length dark hair",
                appearance="woman in her thirties",
                default_costume_id="W01",
            )
        ],
        scenes=[
            SceneAssetSpec(
                location_id="KITCHEN",
                name="Family Kitchen",
                topology_lock="table center, door west, window east",
                lighting_anchors=["warm ceiling practical"],
            )
        ],
        visual_style_lock="restrained realistic family drama",
    )
    director = DirectorPlan(
        project_title="The House",
        visual_concept="restrained realism",
        scenes=[
            SceneDirection(
                scene_id="SC01",
                dramatic_event="daughter notices the missing deed",
                audience_know="the deed is missing",
                audience_feel="unease",
                blocking=BlockingMap(
                    scene_id="SC01",
                    action_axis="daughter-father",
                    allowed_camera_side="south",
                    positions=[BlockingPosition(subject_id="C01", start="door", end="table", facing="east")],
                ),
                cinematography_intent="begin observationally, then narrow attention to the reaction",
            )
        ],
    )
    state = WorldState(
        location_id="KITCHEN",
        characters={"C01": CharacterState(character_id="C01", costume_id="W01", position="table", facing="east")},
        camera_side="south",
    )
    shot = ShotSpec(
        shot_id="SC01_SH01",
        scene_id="SC01",
        narrative_purpose="show the daughter's realization",
        audience_endpoint="the audience notices her suspicion",
        duration_seconds=4.0,
        performance={"C01": PerformancePlan(objective="test her father", action_verb="probe")},
        entry_state=state,
        action_beats=[ActionBeat(actor="C01", action="looks at the empty folder")],
        camera=CameraSpec(
            narrative_purpose="capture the hidden reaction",
            shot_size="MCU",
            lens_mm=65,
            focus_target="C01 eyes",
            movement=CameraMove(kind="dolly_in", purpose="narrow attention", start_second=1.5, end_second=3.5),
        ),
        exit_state=state,
    )
    return story, script, bible, director, shot


def test_creative_vertical_slice(tmp_path):
    orch, creative = make_pipeline(tmp_path)
    record = orch.create_project(ProjectSpec(prompt="Create a restrained family drama"))
    orch.policy_check(record.spec.project_id)
    story, script, bible, director, shot = fixtures()
    creative.submit_story(record.spec.project_id, story)
    creative.submit_script(record.spec.project_id, script)
    creative.submit_asset_bible(record.spec.project_id, bible)
    creative.submit_director_plan(record.spec.project_id, director)
    creative.submit_shots(record.spec.project_id, [shot])
    final = orch.repository.get(record.spec.project_id)
    assert final.state == ProjectState.SHOTSPEC_VALIDATED


def test_director_cannot_omit_script_scene():
    _, script, _, director, _ = fixtures()
    director.scenes = []
    with pytest.raises(Exception):
        DirectorPlan.model_validate(director.model_dump())


def test_camera_move_must_fit_shot_duration():
    _, _, _, _, shot = fixtures()
    raw = shot.model_dump()
    raw["camera"]["movement"]["end_second"] = 9.0
    with pytest.raises(ValueError):
        ShotSpec.model_validate(raw)
