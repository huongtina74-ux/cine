from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.rendered_frame_qc import (
    RenderedFrameQCResult,
)
from cinefactory.studio.character_factory import CharacterBackendId
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
)
from cinefactory.turbo.contracts import ResourceClass, WorkerSpec, WorkState
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore


def _frame_qc(path: Path) -> RenderedFrameQCResult:
    sidecar = path.with_suffix(path.suffix + ".frame_qc.json")
    return RenderedFrameQCResult.model_validate_json(
        sidecar.read_text(encoding="utf-8")
    )


def main() -> None:
    out = (
        ROOT
        / "data"
        / "verification"
        / "v181_character_factory"
    )
    out.mkdir(parents=True, exist_ok=True)
    db = out / "turbo_v181.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)

    blender_before = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    blender_after = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S02.cycles.golden.mp4"
    )
    assert blender_before.is_file()
    assert blender_after.is_file()

    pack = ctx.character_factory.capture_reference_from_render(
        source_media=blender_before,
        actor_id="A",
        rig_id="mc_a",
    )
    record = ctx.character_factory.record_for_rig("mc_a")
    assert record.global_character_id == "CHAR_MC_A"
    assert pack.global_character_id == record.global_character_id
    assert Path(pack.crop_path).is_file()

    ns = runpy.run_path(
        str(ROOT / "tests" / "test_block_auto_repair_v173.py")
    )
    episode = ns["_episode"]().model_copy(
        deep=True,
        update={
            "project_id": "V181_CHARACTER_FACTORY",
            "episode_id": "V181_CHARACTER_FACTORY",
        },
    )
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=out / "renders",
    )
    shot = compiled.shots[0]

    request = MethodSwitchRequest(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot_id=shot.shot_id,
        current_tool_id="blender",
        current_method_id="blender.cycles.quality",
        policy=MethodSwitchPolicy.BALANCED_ALTERNATIVE,
        min_quality=0.70,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=240.0,
        mean_current_attempt_seconds=20.0,
        continuity_priority=True,
        backend_switch_allowed=True,
        recurring_identity_required=True,
        reference_frame_path=str(blender_before),
        precise_camera_required=False,
        semantic_performance_required=False,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
        required_tags={"reference_conditioning"},
    )
    decision = ctx.method_switch.deliberate(request)
    assert decision.executable is True
    assert decision.selected_method_id == (
        "comfyui.wan21.fun.inpaint.1.3b"
    )

    work = ctx.method_switch.build_work_item(
        compiled=compiled,
        shot=shot,
        decision=decision,
        output_path=out / "renders" / "S01.wan.character.mp4",
        render_preview=True,
        switch_round=1,
        switch_of_work_id="V181_BLENDER_REFERENCE",
    )
    video_request = work.payload["video_request"]
    assert video_request["reference"]["global_character_ids"] == {
        "A": "CHAR_MC_A"
    }
    assert video_request["reference"]["actor_reference_ids"]["A"]
    assert video_request["reference"]["actor_screen_boxes"]["A"]["area"] > 0
    assert "global character CHAR_MC_A" in video_request["prompt"]

    ctx.turbo_store.enqueue_work(work)
    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v181-character-gpu",
            resources={ResourceClass.GPU},
            capabilities={"block.video.comfy"},
            active_model_affinity=work.model_affinity,
        ),
        poll_seconds=0.05,
    )
    try:
        assert gpu.tick() is True
    finally:
        gpu.close()

    done = ctx.turbo_store.get_work(work.work_id)
    assert done.state is WorkState.SUCCESS
    result = dict(done.result)
    assert result["qc_passed"] is True
    assert result["identity_qc"]["metric"] == (
        "PER_ACTOR_REFERENCE_APPEARANCE"
    )
    assert result["identity_qc"]["measured"] is True
    assert result["identity_qc"]["passed"] is True
    assert result["character_identity_qc"]["passed"] is True

    actor_rows = result["identity_qc"]["actors"]
    actor_a = next(
        row for row in actor_rows if row["actor_id"] == "A"
    )
    assert actor_a["global_character_id"] == "CHAR_MC_A"
    assert actor_a["score"] >= ctx.character_factory.identity_floor

    before_qc = _frame_qc(blender_before)
    after_qc = _frame_qc(blender_after)
    wan_qc = RenderedFrameQCResult.model_validate(
        result["rendered_frame_qc"]
    )
    assert "A" in before_qc.actors
    assert "A" in wan_qc.actors
    assert "A" in after_qc.actors

    mapping = {"A": "CHAR_MC_A"}
    b_to_w = ctx.character_factory.evaluate_transition(
        previous_backend=CharacterBackendId.BLENDER_BLOCK,
        current_backend=CharacterBackendId.WAN21,
        actor_to_global=mapping,
        previous_actors=before_qc.actors,
        current_actors=wan_qc.actors,
    )
    w_to_b = ctx.character_factory.evaluate_transition(
        previous_backend=CharacterBackendId.WAN21,
        current_backend=CharacterBackendId.BLENDER_BLOCK,
        actor_to_global=mapping,
        previous_actors=wan_qc.actors,
        current_actors=after_qc.actors,
    )
    assert b_to_w.passed is True
    assert w_to_b.passed is True

    payload = {
        "character": record.model_dump(mode="json"),
        "reference_pack": pack.model_dump(mode="json"),
        "wan_request_identity": {
            "global_character_ids": (
                video_request["reference"]["global_character_ids"]
            ),
            "actor_reference_ids": (
                video_request["reference"]["actor_reference_ids"]
            ),
            "actor_screen_boxes": (
                video_request["reference"]["actor_screen_boxes"]
            ),
        },
        "wan_render": {
            "work_id": work.work_id,
            "state": done.state.value,
            "path": result["path"],
            "bytes": Path(result["path"]).stat().st_size,
            "identity_qc": result["identity_qc"],
            "character_identity_qc": result["character_identity_qc"],
        },
        "cross_backend_transitions": {
            "blender_to_wan": b_to_w.model_dump(mode="json"),
            "wan_to_blender": w_to_b.model_dump(mode="json"),
        },
    }
    target = out / "character_factory_verification.json"
    target.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
