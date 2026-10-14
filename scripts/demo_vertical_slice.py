from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.domain.models import AssetBibleSpec, DirectorPlan, ProjectSpec, RenderJob, ScriptSpec, ShotSpec, StorySpec, model_hash

EXAMPLE = ROOT / "examples" / "golden_family_drama"


def read(path: str, cls):
    return cls.model_validate_json((EXAMPLE / path).read_text(encoding="utf-8"))


def main() -> None:
    ctx = build_context(ROOT)
    project = ctx.orchestrator.create_project(
        ProjectSpec(
            prompt="Create a restrained family drama about a daughter discovering her father's sacrifice.",
            profile="cinematic_story",
            language="en",
            duration_seconds=600,
        )
    )
    pid = project.spec.project_id
    ctx.orchestrator.policy_check(pid)
    ctx.creative.submit_story(pid, read("story.json", StorySpec))
    ctx.creative.submit_script(pid, read("script.json", ScriptSpec))
    ctx.creative.submit_asset_bible(pid, read("assets.json", AssetBibleSpec))
    ctx.creative.submit_director_plan(pid, read("director.json", DirectorPlan))
    raw_shots = json.loads((EXAMPLE / "shots.json").read_text(encoding="utf-8"))
    shots = [ShotSpec.model_validate(x) for x in raw_shots]
    shot_artifact = ctx.creative.submit_shots(pid, shots)

    pilot_job = RenderJob(
        project_id=pid,
        shot_id=shots[0].shot_id,
        job_type="PILOT_RENDER",
        executor_id="local.mock",
        workflow_id="mock.local",
        workflow_version="1",
        dependency_hash=model_hash(shots[0]),
        payload={"shot_id": shots[0].shot_id, "shot_spec_hash": model_hash(shots[0])},
    )
    pilot_job, created = ctx.job_service.enqueue(pilot_job)
    pilot_job = ctx.job_service.execute_now(pilot_job.job_id)

    result = {
        "project_id": pid,
        "project_state": ctx.projects.get(pid).state.value,
        "shot_spec_artifact": shot_artifact.model_dump(mode="json"),
        "pilot_job_created": created,
        "pilot_job_state": pilot_job.state.value,
        "audit_events": [e.event_type for e in ctx.audit.list_for_project(pid)],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
