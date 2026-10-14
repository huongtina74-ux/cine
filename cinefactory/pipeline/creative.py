from __future__ import annotations

from cinefactory.core.continuity import ContinuityValidator
from cinefactory.creative.contracts import CONTRACTS, CreativeValidator
from cinefactory.creative.store import CreativeStore
from cinefactory.domain.enums import CreativeStage, ProjectState
from cinefactory.domain.models import AssetBibleSpec, DirectorPlan, ScriptSpec, ShotSpec, ShotSpecBatch, StorySpec
from cinefactory.pipeline.orchestrator import PipelineOrchestrator


class CreativePipeline:
    """Submits versioned creative decisions and advances project gates only after validation."""

    def __init__(self, store: CreativeStore, orchestrator: PipelineOrchestrator) -> None:
        self.store = store
        self.orchestrator = orchestrator
        self.validator = CreativeValidator()
        self.continuity = ContinuityValidator()

    def submit_story(self, project_id: str, story: StorySpec):
        c = CONTRACTS[CreativeStage.STORY]
        artifact = self.store.put(project_id, c.stage, c.owner, story)
        record = self.orchestrator.repository.get(project_id)
        if record.state is ProjectState.POLICY_CHECKED:
            self.orchestrator.transition(project_id, ProjectState.STORY_READY)
        return artifact

    def submit_script(self, project_id: str, script: ScriptSpec):
        story, story_meta = self.store.get_latest(project_id, CreativeStage.STORY, StorySpec)
        issues = self.validator.validate_story_script(story, script)
        self.validator.require_clean(issues, "SCRIPT")
        c = CONTRACTS[CreativeStage.SCRIPT]
        artifact = self.store.put(project_id, c.stage, c.owner, script, [story_meta.content_hash])
        record = self.orchestrator.repository.get(project_id)
        if record.state is ProjectState.STORY_READY:
            self.orchestrator.transition(project_id, ProjectState.SCRIPT_READY)
        return artifact


    def submit_asset_bible(self, project_id: str, bible: AssetBibleSpec):
        script, script_meta = self.store.get_latest(project_id, CreativeStage.SCRIPT, ScriptSpec)
        script_locations = {s.location_id for s in script.scenes}
        bible_locations = {s.location_id for s in bible.scenes}
        missing = script_locations - bible_locations
        if missing:
            self.validator.require_clean(["ASSET_BIBLE_MISSING_LOCATIONS:" + ",".join(sorted(missing))], "ASSET_BIBLE")
        c = CONTRACTS[CreativeStage.ASSET_BIBLE]
        artifact = self.store.put(project_id, c.stage, c.owner, bible, [script_meta.content_hash])
        record = self.orchestrator.repository.get(project_id)
        if record.state is ProjectState.SCRIPT_READY:
            self.orchestrator.transition(project_id, ProjectState.ASSET_BIBLE_READY)
        return artifact

    def submit_director_plan(self, project_id: str, director: DirectorPlan):
        script, script_meta = self.store.get_latest(project_id, CreativeStage.SCRIPT, ScriptSpec)
        _, asset_meta = self.store.get_latest(project_id, CreativeStage.ASSET_BIBLE, AssetBibleSpec)
        issues = self.validator.validate_script_director(script, director)
        self.validator.require_clean(issues, "DIRECTOR_PLAN")
        c = CONTRACTS[CreativeStage.DIRECTOR_PLAN]
        artifact = self.store.put(project_id, c.stage, c.owner, director, [script_meta.content_hash, asset_meta.content_hash])
        record = self.orchestrator.repository.get(project_id)
        # Asset Bible is a deliberate gate. v0.2 can advance only if caller explicitly marked it ready.
        if record.state is ProjectState.ASSET_BIBLE_READY:
            self.orchestrator.transition(project_id, ProjectState.DIRECTOR_PLAN_READY)
        return artifact

    def submit_shots(self, project_id: str, shots: list[ShotSpec]):
        director, director_meta = self.store.get_latest(project_id, CreativeStage.DIRECTOR_PLAN, DirectorPlan)
        issues = self.validator.validate_shots(director, shots)
        for previous, current in zip(shots, shots[1:]):
            if previous.scene_id == current.scene_id:
                continuity = self.continuity.validate_adjacent(previous, current)
                issues.extend(f"CONTINUITY:{current.shot_id}:{i.field}" for i in continuity)
        self.validator.require_clean(issues, "SHOT_SPEC")
        c = CONTRACTS[CreativeStage.SHOT_SPEC]
        batch = ShotSpecBatch(shots=shots)
        artifact = self.store.put(project_id, c.stage, c.owner, batch, [director_meta.content_hash])
        record = self.orchestrator.repository.get(project_id)
        if record.state is ProjectState.DIRECTOR_PLAN_READY:
            self.orchestrator.transition(project_id, ProjectState.SHOTSPEC_VALIDATED)
        return artifact
