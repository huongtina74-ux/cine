from __future__ import annotations

from dataclasses import dataclass
import time
from pathlib import Path

from cinefactory.domain.enums import ShotComplexity
from cinefactory.domain.models import AssetBibleSpec, ShotSpec
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.production.comfy_pipeline import ComfyShotPipeline
from cinefactory.production.contracts import DailiesReport, ShotDailiesReport, TakeRecord
from cinefactory.production.dailies import DailiesSelector
from cinefactory.production.failure_router import FailureRouter
from cinefactory.production.router import ShotRouter
from cinefactory.qc.technical import TechnicalQC
from cinefactory.qc.visual_command import CommandVisualQC
from cinefactory.qc.visual_policy import normalized_visual_review
from cinefactory.turbo.logic_gate import PreRenderLogicGate
from cinefactory.turbo.contracts import FactoryEvent, ThroughputSample
from cinefactory.turbo.incremental_editor import IncrementalTimeline
from cinefactory.turbo.comfy_dispatch import TurboComfyDispatcher


@dataclass(frozen=True)
class VideoFactoryResult:
    pilot_shot_ids: list[str]
    pilot_reports: list[ShotDailiesReport]
    dailies: DailiesReport

    @property
    def selected_paths(self) -> dict[str, str]:
        return {x.shot_id: x.selected_path for x in self.dailies.shots if x.selected_path}


class VideoFactory:
    """Pilot-first, multi-take, QC-driven local video production.

    The factory never falls back to a metered provider. A failed take is routed to the
    owning layer, and only render-local/retryable failures are retried automatically.
    """

    def __init__(
        self,
        ctx,
        *,
        visual_qc: CommandVisualQC | None = None,
        min_visual_score: float = 0.72,
        early_accept_score: float = 0.88,
        max_repair_rounds: int = 2,
        turbo_dispatch: bool = False,
        turbo_timeout_seconds: int = 1800,
        diagnostic_slate: bool = False,
    ) -> None:
        self.ctx = ctx
        self.media = FFmpegToolchain()
        self.technical = TechnicalQC(self.media)
        self.visual_qc = visual_qc
        self.diagnostic_slate = diagnostic_slate
        self.selector = DailiesSelector(0.0 if diagnostic_slate else min_visual_score)
        self.router = ShotRouter()
        self.failures = FailureRouter()
        self.early_accept_score = early_accept_score
        self.max_repair_rounds = max_repair_rounds
        self.comfy = ComfyShotPipeline(ctx.workflows)
        self.logic_gate = PreRenderLogicGate()
        self.repair_memory = getattr(ctx, "repair_memory", None)
        self.turbo_store = getattr(ctx, "turbo_store", None)
        self.turbo_dispatch = turbo_dispatch
        self.turbo_timeout_seconds = turbo_timeout_seconds
        self.turbo_comfy = TurboComfyDispatcher(ctx) if turbo_dispatch else None

    def _emit(self, event_type: str, project_id: str, entity_id: str | None = None, **payload) -> None:
        if self.turbo_store is not None:
            self.turbo_store.publish_event(FactoryEvent(event_type=event_type, project_id=project_id, entity_id=entity_id, payload=payload))


    def _reference_paths(self, shot: ShotSpec, bible: AssetBibleSpec) -> list[str]:
        ids: list[str] = []
        char_ids = set(shot.performance) | set(shot.entry_state.characters)
        for item in bible.characters:
            if item.character_id in char_ids:
                ids.extend(item.reference_asset_ids)
        for item in bible.scenes:
            if item.location_id == shot.entry_state.location_id:
                ids.extend(item.reference_asset_ids)
        prop_ids = set(shot.entry_state.props)
        for state in shot.entry_state.characters.values():
            prop_ids.update(state.held_props)
        for item in bible.props:
            if item.prop_id in prop_ids:
                ids.extend(item.reference_asset_ids)
        paths: list[str] = []
        for asset_id in ids:
            try:
                rec = self.ctx.assets.get(asset_id)
            except KeyError:
                continue
            if rec.source and rec.source not in paths:
                paths.append(rec.source)
        return paths

    @staticmethod
    def choose_pilot(shots: list[ShotSpec], count: int = 2) -> list[ShotSpec]:
        if not shots:
            return []
        rank = {ShotComplexity.GREEN: 0, ShotComplexity.YELLOW: 1, ShotComplexity.RED: 2, ShotComplexity.HERO: 3}
        picked: list[ShotSpec] = [shots[0]]
        for shot in sorted(shots[1:], key=lambda x: rank[x.complexity], reverse=True):
            if len(picked) >= max(1, count):
                break
            if shot.shot_id not in {x.shot_id for x in picked}:
                picked.append(shot)
        return picked

    def _visual_review(self, path: Path, shot: ShotSpec) -> tuple[bool, dict, list[str]]:
        if self.visual_qc is None:
            if self.diagnostic_slate:
                return True, {"identity": 0.0, "continuity": 0.0, "performance": 0.0, "camera": 0.0}, ["DIAGNOSTIC_SLATE_NOT_VISUALLY_REVIEWED"]
            return False, {"identity": 0.0, "continuity": 0.0, "performance": 0.0, "camera": 0.0}, ["VISUAL_QC_MISSING_FAIL_CLOSED"]
        r = self.visual_qc.review(path, {"kind": "video_take", "shot": shot.model_dump(mode="json")})
        return normalized_visual_review(r, min_score=self.selector.min_score)

    def _render_take(
        self,
        *,
        project_root: Path,
        shot: ShotSpec,
        bible: AssetBibleSpec,
        keyframe_path: str,
        mode: str,
        workflow_id: str | None,
        workflow_version: str,
        workflow_lanes: dict[str, tuple[str | None, str]] | None = None,
        render_width: int,
        render_height: int,
        candidate_index: int,
        repair_round: int,
        repair_hint: str | None,
    ) -> TakeRecord:
        if mode != "slate" and self.visual_qc is None:
            raise RuntimeError("VISUAL_QC_MISSING_FAIL_CLOSED: generated video cannot be produced unreviewed")
        if mode == "slate" and not self.diagnostic_slate:
            raise RuntimeError("SLATE_ONLY_DIAGNOSTIC: slate takes cannot qualify as premium footage")
        take_id = f"{shot.shot_id}_T{candidate_index:02d}_R{repair_round:02d}"
        out_dir = project_root / "renders" / "takes" / shot.shot_id / take_id
        out_dir.mkdir(parents=True, exist_ok=True)
        seed = None
        try:
            if mode == "slate":
                path = self.media.make_slate(
                    f"{take_id} | {shot.camera.shot_size} | {shot.camera.movement.kind}",
                    out_dir / f"{take_id}.mp4", duration=shot.duration_seconds,
                    size=f"{render_width}x{render_height}",
                )
            elif mode == "comfyui":
                if not workflow_id:
                    raise RuntimeError("video workflow id required for ComfyUI production")
                manifest = self.ctx.workflows.get(workflow_id, workflow_version)
                if not manifest.model_revision:
                    raise RuntimeError(f"Workflow {workflow_id}@{workflow_version} must pin model_revision before production")
                self.ctx.models.require_approved(manifest.model_id, manifest.model_revision)
                built = self.comfy.payload(
                    shot, bible, workflow_id=workflow_id, workflow_version=workflow_version,
                    width=render_width, height=render_height, input_image=keyframe_path,
                    reference_images=self._reference_paths(shot, bible), repair_hint=repair_hint,
                )
                seed = built.seed
                if self.turbo_comfy is not None:
                    model_affinity=f"{manifest.model_id}@{manifest.model_revision}"
                    result = self.turbo_comfy.execute(
                        project_id=project_root.name, workflow=built.workflow, output_dir=str(out_dir),
                        model_affinity=model_affinity, timeout_seconds=self.turbo_timeout_seconds,
                        priority=80 if shot.complexity is ShotComplexity.HERO else 50,
                        provenance={
                            "seed": built.seed,
                            "workflow_id": workflow_id,
                            "workflow_version": workflow_version,
                            "model_id": manifest.model_id,
                            "model_revision": manifest.model_revision,
                        },
                    )
                else:
                    executor = self.ctx.executors.get("local.comfyui")
                    result = executor.execute({
                        "workflow": built.workflow,
                        "output_dir": str(out_dir),
                        "seed": built.seed,
                        "workflow_id": workflow_id,
                        "workflow_version": workflow_version,
                        "model_id": manifest.model_id,
                        "model_revision": manifest.model_revision,
                    })
                if not result.ok:
                    return TakeRecord(take_id=take_id, shot_id=shot.shot_id, path="", seed=seed, technical_pass=False, visual_pass=False, aggregate_score=0.0, findings=[result.error or "RENDER_FAILED"], repair_round=repair_round)
                videos = [Path(x) for x in result.artifacts if Path(x).suffix.lower() in {".mp4", ".mov", ".webm", ".mkv", ".avi"}]
                if not videos:
                    return TakeRecord(take_id=take_id, shot_id=shot.shot_id, path="", seed=seed, technical_pass=False, visual_pass=False, aggregate_score=0.0, findings=["OUTPUT_MISSING"], repair_round=repair_round)
                path = videos[0]
            else:
                raise ValueError("production mode must be slate or comfyui")

            technical = self.technical.video(path)
            if not technical.passed:
                directive = self.failures.classify(shot.shot_id, technical.findings)
                return TakeRecord(
                    take_id=take_id, shot_id=shot.shot_id, path=str(path), seed=seed,
                    technical_pass=False, visual_pass=False, aggregate_score=0.0,
                    failure_code=directive.failure_code, findings=technical.findings, repair_round=repair_round,
                )
            visual_pass, scores, findings = self._visual_review(path, shot)
            values = [x for x in scores.values() if x is not None]
            aggregate = sum(values) / len(values) if values else (1.0 if visual_pass else 0.0)
            failure_code = None
            if not visual_pass:
                failure_code = self.failures.classify(shot.shot_id, findings).failure_code
            return TakeRecord(
                take_id=take_id, shot_id=shot.shot_id, path=str(path), seed=seed,
                technical_pass=True, visual_pass=visual_pass,
                identity_score=scores["identity"], continuity_score=scores["continuity"],
                performance_score=scores["performance"], camera_score=scores["camera"],
                aggregate_score=aggregate, failure_code=failure_code, findings=findings,
                repair_round=repair_round,
            )
        except Exception as exc:
            directive = self.failures.classify(shot.shot_id, [str(exc)])
            return TakeRecord(
                take_id=take_id, shot_id=shot.shot_id, path="", seed=seed,
                technical_pass=False, visual_pass=False, aggregate_score=0.0,
                failure_code=directive.failure_code, findings=[str(exc)], repair_round=repair_round,
            )

    def _workflow_for_shot(self, shot: ShotSpec, default_id: str | None, default_version: str, workflow_lanes: dict[str, tuple[str | None, str]] | None) -> tuple[str | None, str, str]:
        if shot.complexity is ShotComplexity.GREEN:
            lane = "fast"
        elif shot.complexity is ShotComplexity.HERO:
            lane = "master"
        else:
            lane = "standard"
        if workflow_lanes and lane in workflow_lanes:
            wid,ver=workflow_lanes[lane]
            return wid or default_id, ver or default_version, lane
        return default_id, default_version, lane

    def produce_shot(
        self,
        *,
        project_root: Path,
        shot: ShotSpec,
        bible: AssetBibleSpec,
        keyframe_path: str,
        mode: str,
        workflow_id: str | None,
        workflow_version: str,
        render_width: int,
        render_height: int,
        force_candidates: int | None = None,
    ) -> ShotDailiesReport:
        route = self.router.route(shot)
        target = max(1, force_candidates if force_candidates is not None else route.candidates)
        takes: list[TakeRecord] = []
        repair_hint: str | None = None
        repair_round = 0
        pending_repair: tuple[str, str, str | None] | None = None

        for candidate_index in range(1, target + 1):
            started_take = time.monotonic()
            take = self._render_take(
                project_root=project_root, shot=shot, bible=bible, keyframe_path=keyframe_path,
                mode=mode, workflow_id=workflow_id, workflow_version=workflow_version,
                render_width=render_width, render_height=render_height,
                candidate_index=candidate_index, repair_round=repair_round, repair_hint=repair_hint,
            )
            takes.append(take)
            if self.turbo_store is not None:
                elapsed=max(0.0001,time.monotonic()-started_take)
                self.turbo_store.add_throughput(ThroughputSample(worker_id="inline-video",kind="video_take",model_affinity=workflow_id,duration_seconds=elapsed,output_units=max(0.01,shot.duration_seconds)))
            if pending_repair and self.repair_memory is not None:
                code,strategy,prompt = pending_repair
                success = bool(take.technical_pass and take.visual_pass)
                self.repair_memory.record(
                    failure_code=code, workflow_id=workflow_id, shot_class=shot.complexity.value,
                    strategy=strategy, prompt_directive=prompt, success=success, score=take.aggregate_score,
                )
                pending_repair = None

            interim = self.selector.select_shot(shot.shot_id, takes)
            if interim.passed and interim.selected_score >= self.early_accept_score:
                return interim

            if take.failure_code:
                directive = self.failures.classify(shot.shot_id, take.findings)
                remembered = self.repair_memory.suggest(directive.failure_code.value, workflow_id, shot.complexity.value) if self.repair_memory is not None else None
                chosen_strategy = remembered.strategy if remembered else directive.action
                chosen_prompt = remembered.prompt_directive if remembered and remembered.prompt_directive else directive.prompt_directive
                if directive.retryable and repair_round < self.max_repair_rounds:
                    repair_round += 1
                    repair_hint = chosen_prompt
                    pending_repair = (directive.failure_code.value, chosen_strategy, chosen_prompt)
                elif not directive.retryable:
                    break

        return self.selector.select_shot(shot.shot_id, takes)

    def run(
        self,
        *,
        project_root: Path,
        shots: list[ShotSpec],
        bible: AssetBibleSpec,
        keyframes: dict[str, str],
        mode: str,
        workflow_id: str | None,
        workflow_version: str,
        render_width: int,
        render_height: int,
        pilot_count: int = 2,
        workflow_lanes: dict[str, tuple[str | None, str]] | None = None,
    ) -> VideoFactoryResult:
        logic = self.logic_gate.validate(shots, auto_fill_missing=True)
        if not logic.passed:
            reports = [ShotDailiesReport(shot_id=s.shot_id, passed=False, findings=[f"PRE_RENDER_LOGIC:{x}" for x in logic.findings]) for s in shots]
            return VideoFactoryResult(pilot_shot_ids=[], pilot_reports=[], dailies=DailiesReport(passed=False, shots=reports, findings=[f"PRE_RENDER_LOGIC:{x}" for x in logic.findings]))
        shots = logic.shots
        pilots = self.choose_pilot(shots, pilot_count)
        pilot_reports: list[ShotDailiesReport] = []
        reports_by_id: dict[str, ShotDailiesReport] = {}
        order_by_id = {shot.shot_id: i for i, shot in enumerate(shots)}
        timeline = IncrementalTimeline(project_root / "post" / "incremental_timeline.json")
        project_id = project_root.name
        self._emit("PRODUCTION_STARTED", project_id, shot_count=len(shots), pilot_count=len(pilots))

        for shot in pilots:
            shot_workflow_id, shot_workflow_version, lane = self._workflow_for_shot(shot, workflow_id, workflow_version, workflow_lanes)
            self._emit("SHOT_RENDER_QUEUED", project_id, shot.shot_id, lane=lane, workflow_id=shot_workflow_id, pilot=True)
            report = self.produce_shot(
                project_root=project_root, shot=shot, bible=bible, keyframe_path=keyframes[shot.shot_id],
                mode=mode, workflow_id=shot_workflow_id, workflow_version=shot_workflow_version,
                render_width=render_width, render_height=render_height,
            )
            pilot_reports.append(report); reports_by_id[shot.shot_id] = report
            if report.passed and report.selected_path:
                timeline.accept_shot(shot_id=shot.shot_id, path=report.selected_path, order=order_by_id[shot.shot_id], duration_seconds=shot.duration_seconds, edit_intent=shot.edit_intent)
                self._emit("SHOT_ACCEPTED", project_id, shot.shot_id, path=report.selected_path, pilot=True, score=report.selected_score)
            else:
                self._emit("SHOT_FAILED", project_id, shot.shot_id, pilot=True, findings=report.findings)
        if any(not x.passed for x in pilot_reports):
            failed = [x.shot_id for x in pilot_reports if not x.passed]
            return VideoFactoryResult(
                pilot_shot_ids=[x.shot_id for x in pilots], pilot_reports=pilot_reports,
                dailies=DailiesReport(passed=False, shots=pilot_reports, findings=[f"PILOT_FAILED:{x}" for x in failed]),
            )

        self._emit("PILOT_PASSED", project_id, accepted=[x.shot_id for x in pilot_reports if x.passed])
        pilot_ids = {x.shot_id for x in pilots}
        remaining = [x for x in shots if x.shot_id not in pilot_ids]
        # Render order is allowed to differ from editorial order. Group by lane/workflow so a
        # single GPU keeps the same hot model loaded for as long as possible.
        lane_rank={"fast":0,"standard":1,"master":2}
        remaining.sort(key=lambda x: (lane_rank[self._workflow_for_shot(x,workflow_id,workflow_version,workflow_lanes)[2]], str(self._workflow_for_shot(x,workflow_id,workflow_version,workflow_lanes)[0] or ""), order_by_id[x.shot_id]))
        self._emit("BATCH_RENDER_ORDER", project_id, order=[x.shot_id for x in remaining])
        for shot in remaining:
            shot_workflow_id, shot_workflow_version, lane = self._workflow_for_shot(shot, workflow_id, workflow_version, workflow_lanes)
            self._emit("SHOT_RENDER_QUEUED", project_id, shot.shot_id, lane=lane, workflow_id=shot_workflow_id, pilot=False)
            report = self.produce_shot(
                project_root=project_root, shot=shot, bible=bible, keyframe_path=keyframes[shot.shot_id],
                mode=mode, workflow_id=shot_workflow_id, workflow_version=shot_workflow_version,
                render_width=render_width, render_height=render_height,
            )
            reports_by_id[shot.shot_id] = report
            if report.passed and report.selected_path:
                timeline.accept_shot(shot_id=shot.shot_id, path=report.selected_path, order=order_by_id[shot.shot_id], duration_seconds=shot.duration_seconds, edit_intent=shot.edit_intent)
                self._emit("SHOT_ACCEPTED", project_id, shot.shot_id, path=report.selected_path, pilot=False, score=report.selected_score)
            else:
                self._emit("SHOT_FAILED", project_id, shot.shot_id, pilot=False, findings=report.findings)

        ordered = [reports_by_id[x.shot_id] for x in shots]
        failed = [x.shot_id for x in ordered if not x.passed]
        self._emit("PRODUCTION_FINISHED", project_id, accepted=len(ordered)-len(failed), failed=failed)
        return VideoFactoryResult(
            pilot_shot_ids=[x.shot_id for x in pilots], pilot_reports=pilot_reports,
            dailies=DailiesReport(passed=not failed, shots=ordered, findings=[f"NO_ACCEPTED_TAKE:{x}" for x in failed]),
        )
