from __future__ import annotations

"""Three-actor local Blender->Wan identity and semantic dialogue probe.

Diagnostic qualification only; never promotes Wan semantic QC.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import ActorPlacement, CameraIntent, EpisodeSpec, ShotPerformanceSpec
from cinefactory.studio.block_production import BlockAnimationProducer
from cinefactory.studio.dialogue_performance import DialogueLineIntent
from cinefactory.turbo.contracts import ResourceClass, WorkerSpec, WorkState
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore


def main() -> None:
    out = ROOT / "data" / "verification" / "v182_three_actor_dialogue"
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / "three_actor_verification.json"
    report: dict = {"status": "STARTED", "actor_ids": ["A", "B", "C"]}
    try:
        ctx = build_context(ROOT)
        shot = ShotPerformanceSpec(
            shot_id="S_ABC",
            scene_template_id="minecraft_classroom",
            duration_seconds=4.8,
            actors=[
                ActorPlacement(actor_id="A", rig_id="mc_a", marker="hero_a", facing_target="B"),
                ActorPlacement(actor_id="B", rig_id="mc_b", marker="hero_b", facing_target="A"),
                ActorPlacement(actor_id="C", rig_id="mc_c", marker="hero_c", facing_target="B"),
            ],
            camera=CameraIntent(purpose="fidelity_group", pattern_id="fidelity_group", targets=["A","B","C"], alternatives=4),
            creative_intent={"scene_id": "SC_DIALOGUE_ABC", "story_beat": "three friends confront a secret"},
            narrative_purpose="three-character argument and reaction coverage",
        )
        lines = [
            DialogueLineIntent(
                line_id="A1", speaker_id="A", listener_ids=["B", "C"],
                text="Who took the key?", objective="pressure friends for truth",
                action_verb="accuse", emotion="angry", start_seconds=0.35, end_seconds=1.28,
            ),
            DialogueLineIntent(
                line_id="B1", speaker_id="B", listener_ids=["A", "C"],
                text="I know what happened.", objective="reveal a clue",
                action_verb="reveal", emotion="surprised", start_seconds=1.6, end_seconds=2.5,
            ),
            DialogueLineIntent(
                line_id="C1", speaker_id="C", listener_ids=["A"],
                text="Listen to me first.", objective="stop the argument",
                action_verb="warn", emotion="confused", start_seconds=2.88, end_seconds=3.84,
            ),
        ]
        sem = ctx.dialogue_performance.compile(
            shot_id=shot.shot_id, duration_seconds=shot.duration_seconds,
            actor_ids=["A","B","C"], lines=lines,
        )
        report["semantic_qc"] = sem.qc.model_dump(mode="json")
        report["directive_count"] = len(sem.directives)
        assert sem.qc.passed and len(sem.directives) == 8
        shot = ctx.dialogue_performance.apply_to_shot(shot, sem)
        episode = EpisodeSpec(
            project_id="V182_DIALOGUE_ABC",
            episode_id="V182_DIALOGUE_ABC",
            title="v1.6.22 three actor real qualification",
            fps=24, width=320, height=180, quality_profile="preview", shots=[shot],
        )
        producer = BlockAnimationProducer(
            ROOT, blender_executable=str(ROOT / ".tools/blender-4.5.14-windows-x64/blender.exe"),
            max_repair_rounds=0,
        )
        try:
            dailies = producer.produce(
                episode, project_root=out / "blender", render_preview=True,
            )
        finally:
            producer.close()
        report["blender_dailies_passed"] = dailies.passed
        if not dailies.passed:
            report["blender_dailies"] = dailies.model_dump(mode="json")
            raise RuntimeError("THREE_ACTOR_BLENDER_DAILIES_FAILED")
        shot_report = dailies.shots[0]
        blender_path = Path(shot_report.selected_path)
        report["blender_video"] = {"path": str(blender_path), "bytes": blender_path.stat().st_size}
        sidecar = blender_path.with_suffix(blender_path.suffix + ".frame_qc.json")
        frame_qc = json.loads(sidecar.read_text(encoding="utf-8"))
        report["frame_actor_ids"] = sorted(frame_qc.get("actors", {}))
        assert set(report["frame_actor_ids"]) == {"A", "B", "C"}
        packs = {}
        for actor_id, rig_id in [("A", "mc_a"), ("B", "mc_b"), ("C", "mc_c")]:
            pack = ctx.character_factory.capture_reference_from_render(
                source_media=blender_path, actor_id=actor_id, rig_id=rig_id,
            )
            packs[actor_id] = {
                "global_character_id": pack.global_character_id,
                "reference_id": pack.reference_id,
            }
        report["reference_packs"] = packs
        compiled = EpisodeAssembler.from_root(ROOT).compile(episode, output_dir=out / "wan")
        work = ctx.cross_backend_video.build_work_item(
            compiled=compiled, shot=compiled.shots[0],
            output_path=out / "wan" / "S_ABC.wan.mp4",
            render_preview=True, switch_round=1,
            switch_of_work_id="V182_BLENDER_ABC_REFERENCE",
            reference_frame_path=blender_path,
            recurring_identity_required=True,
            semantic_performance_required=False,
            precise_camera_required=False,
        )
        reference = work.payload["video_request"]["reference"]
        report["wan_reference_actor_ids"] = sorted(reference["actor_reference_ids"])
        assert set(report["wan_reference_actor_ids"]) == {"A", "B", "C"}
        ctx.turbo_store = TurboStore(out / "turbo_abc.db")
        ctx.turbo_store.enqueue_work(work)
        worker = FactoryDaemon(
            ctx,
            WorkerSpec(
                worker_id="v182-three-actor-gpu",
                resources={ResourceClass.GPU},
                capabilities={"block.video.comfy"},
                active_model_affinity=work.model_affinity,
            ),
            poll_seconds=0.05,
        )
        try:
            assert worker.tick() is True
        finally:
            worker.close()
        done = ctx.turbo_store.get_work(work.work_id)
        report["wan_state"] = done.state.value
        if done.state is not WorkState.SUCCESS:
            report["wan_error"] = str(getattr(done, "error", "UNKNOWN_WORK_ERROR"))
            raise RuntimeError("THREE_ACTOR_WAN_EXECUTION_FAILED")
        result = dict(done.result)
        report["wan_path"] = result.get("path")
        report["wan_character_identity_qc"] = result.get("character_identity_qc")
        report["wan_actor_tracking_qc"] = result.get("actor_tracking_qc")
        report["wan_identity_qc"] = result.get("identity_qc")
        report["status"] = "QUALIFIED_IDENTITY_ONLY" if (
            result.get("character_identity_qc", {}).get("passed")
            and result.get("actor_tracking_qc", {}).get("passed")
        ) else "UNQUALIFIED_IDENTITY"
    except Exception as exc:
        report["status"] = "FAILED_OR_BLOCKED"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        manifest.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({"status": report["status"], "manifest": str(manifest)}, indent=2))


if __name__ == "__main__":
    main()
