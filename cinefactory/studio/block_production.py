from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import BlenderAnimationJob, EpisodeSpec
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.block_animation.render_continuity import (
    RenderContinuityEvaluator,
    RenderContinuityResult,
)
from cinefactory.block_animation.rendered_frame_qc import (
    ActorAppearanceComparison,
    ActorAppearanceEvidence,
    CutAppearanceComparison,
    RenderedAppearanceEvaluator,
    RenderedFrameQCResult,
)
from cinefactory.block_animation.repair import LocalBlockRepairPlanner
from cinefactory.production.failure_router import FailureRouter
from cinefactory.studio.production_economics import (
    EconomicsAction,
    EconomicsDecision,
    ProductionEconomicsController,
)
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
    MethodSwitchStatus,
    ProductionMethodSwitchController,
)
from cinefactory.production.contracts import (
    DailiesReport,
    ShotDailiesReport,
    TakeRecord,
)
from cinefactory.turbo.blender import PersistentBlenderWorker
from cinefactory.turbo.contracts import ResourceClass, WorkerSpec, WorkItem, WorkState
from cinefactory.turbo.daemon import FactoryDaemon


class BlockAnimationProducer:
    """Render a compiled block-animation episode through one hot Blender worker."""

    def __init__(
        self,
        root: str | Path,
        *,
        blender_executable: str = "blender",
        worker: PersistentBlenderWorker | None = None,
        ctx: Any | None = None,
        max_repair_rounds: int = 2,
        economics_controller: ProductionEconomicsController | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.ctx = ctx
        self.blender_executable = blender_executable
        self.assembler = EpisodeAssembler.from_root(self.root)
        self.runtime = BlockAnimationRuntime(self.root)
        self.worker = worker or PersistentBlenderWorker(
            self.root,
            blender_executable=blender_executable,
        )
        self.max_repair_rounds = max(0, int(max_repair_rounds))
        self.repair_planner = LocalBlockRepairPlanner()
        self.economics = (
            economics_controller
            or ProductionEconomicsController()
        )
        self.method_switch = (
            getattr(ctx, "method_switch", None)
            if ctx is not None
            else None
        )
        self.shot_router = (
            getattr(ctx, "shot_router", None)
            if ctx is not None
            else None
        )
        if self.method_switch is None and ctx is not None:
            self.method_switch = (
                ProductionMethodSwitchController(ctx)
            )


    def close(self) -> None:
        self.worker.close()

    def _economics_execution_metrics(
        self,
        store: Any,
        *,
        episode: EpisodeSpec,
        compiled: Any,
        decisions: list[EconomicsDecision],
        shot_routing: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        metrics = store.execution_cost_summary(
            project_id=episode.project_id
        )
        project_budget = self.economics.project_gpu_budget(
            list(compiled.shots),
            episode_metadata=dict(episode.metadata or {}),
            global_max_repair_rounds=self.max_repair_rounds,
        )
        shot_budgets = [
            self.economics.budget_for(
                shot,
                episode_metadata=dict(episode.metadata or {}),
                global_max_repair_rounds=self.max_repair_rounds,
            ).model_dump(mode="json")
            for shot in compiled.shots
        ]
        metrics["economics"] = {
            **self.economics.kpi_report(metrics),
            "project_gpu_budget": project_budget,
            "shot_budgets": shot_budgets,
            "decisions": [
                row.model_dump(mode="json")
                for row in decisions
            ],
        }
        if shot_routing:
            metrics["shot_routing"] = dict(shot_routing)
        return metrics

    @staticmethod
    def _evidence_scores(
        result: dict[str, Any],
        continuity: RenderContinuityResult | None = None,
        appearance_comparisons: list[ActorAppearanceComparison] | None = None,
        cut_appearance: CutAppearanceComparison | None = None,
    ) -> dict[str, Any]:
        geometry = dict(result.get("geometry_qc") or {})
        identity_qc = dict(result.get("identity_qc") or {})
        performance_qc = dict(result.get("performance_qc") or {})
        rendered_frame_qc = dict(
            result.get("rendered_frame_qc") or {}
        )
        geometry_warnings = list(geometry.get("warnings") or [])
        geometry_blockers = list(geometry.get("blockers") or [])
        runtime_qc_findings = list(
            result.get("qc_findings") or []
        )
        frame_warnings = list(
            rendered_frame_qc.get("warnings") or []
        )
        frame_blockers = list(
            rendered_frame_qc.get("findings") or []
        )
        gaze_rows = list(result.get("gaze_debug") or [])
        gaze_requested = len(gaze_rows)
        gaze_applied = sum(
            1 for row in gaze_rows if bool(row.get("applied"))
        )

        camera_score = None
        if geometry:
            if not geometry.get("passed", False):
                camera_score = 0.0
            else:
                camera_score = max(
                    0.75,
                    1.0 - 0.05 * len(geometry_warnings),
                )

        performance_score = None
        if performance_qc.get("score") is not None:
            performance_score = float(performance_qc["score"])
        elif gaze_requested:
            performance_score = gaze_applied / gaze_requested

        appearance_rows = appearance_comparisons or []
        measured_identity = [
            row.score
            for row in appearance_rows
            if row.measured and row.score is not None
        ]
        identity_score = (
            sum(measured_identity) / len(measured_identity)
            if measured_identity
            else (
                float(identity_qc["score"])
                if (
                    identity_qc.get("measured", False)
                    and identity_qc.get("score") is not None
                )
                else None
            )
        )
        identity_appearance_passed = (
            all(
                row.passed
                for row in appearance_rows
                if row.measured
            )
            if any(row.measured for row in appearance_rows)
            else (
                bool(identity_qc.get("passed", False))
                if identity_qc
                else True
            )
        )

        continuity_payload: dict[str, Any] = {}
        cut_payload: dict[str, Any] = {}
        continuity_components: list[float] = []
        continuity_passed = True
        continuity_labels: list[str] = []
        if continuity is not None:
            continuity_payload = continuity.model_dump(mode="json")
            if continuity.measured:
                if continuity.score is not None:
                    continuity_components.append(
                        float(continuity.score)
                    )
                continuity_passed = (
                    continuity_passed and continuity.passed
                )
                continuity_labels.append("3D_STATE")
        if cut_appearance is not None:
            cut_payload = cut_appearance.model_dump(mode="json")
            if cut_appearance.measured:
                if cut_appearance.score is not None:
                    continuity_components.append(
                        float(cut_appearance.score)
                    )
                continuity_passed = (
                    continuity_passed and cut_appearance.passed
                )
                continuity_labels.append("FRAME_APPEARANCE")
        continuity_score = (
            sum(continuity_components)
            / len(continuity_components)
            if continuity_components
            else None
        )

        findings = [
            f"CAMERA_GEOMETRY_BLOCKER:{item}"
            for item in geometry_blockers
        ]
        findings.extend(
            f"CAMERA_GEOMETRY_WARNING:{item}"
            for item in geometry_warnings
        )
        findings.extend(
            f"RUNTIME_QC_BLOCKER:{item}"
            for item in runtime_qc_findings
        )
        findings.extend(
            f"RENDERED_FRAME_QC_BLOCKER:{item}"
            for item in frame_blockers
        )
        findings.extend(
            f"RENDERED_FRAME_WARNING:{item}"
            for item in frame_warnings
        )
        findings.extend(
            "GAZE_NOT_APPLIED:"
            + str(row.get("actor_id") or "UNKNOWN")
            + ":"
            + str(row.get("reason") or "UNKNOWN")
            for row in gaze_rows
            if not bool(row.get("applied"))
        )
        findings.extend(
            f"PERFORMANCE_QC_WARNING:{item}"
            for item in performance_qc.get("warnings", [])
        )
        findings.extend(
            f"PERFORMANCE_QC_BLOCKER:{item}"
            for item in performance_qc.get("blockers", [])
        )
        findings.extend(
            f"IDENTITY_STRUCTURE_BLOCKER:{item}"
            for item in identity_qc.get("blockers", [])
        )
        if continuity is not None:
            findings.extend(continuity.findings)
        if cut_appearance is not None:
            findings.extend(cut_appearance.findings)
        for comparison in appearance_rows:
            findings.extend(comparison.findings)

        measured_scores = [
            score
            for score in (
                identity_score,
                performance_score,
                camera_score,
                continuity_score,
            )
            if score is not None
        ]
        aggregate = (
            sum(measured_scores) / len(measured_scores)
            if measured_scores
            else 1.0
        )
        camera_passed = (
            not geometry
            or bool(geometry.get("passed", False))
        )
        performance_passed = (
            bool(performance_qc.get("passed", False))
            if performance_qc
            else (
                gaze_requested == 0
                or gaze_applied == gaze_requested
            )
        )
        identity_structure_passed = (
            not identity_qc
            or bool(identity_qc.get("passed", False))
        )
        rendered_frames_passed = (
            not rendered_frame_qc
            or bool(rendered_frame_qc.get("passed", False))
        )
        execution_conformance_passed = (
            camera_passed
            and performance_passed
            and identity_structure_passed
            and identity_appearance_passed
            and continuity_passed
            and rendered_frames_passed
        )

        identity_payload = [
            row.model_dump(mode="json")
            for row in appearance_rows
        ]
        return {
            "execution_conformance_passed": (
                execution_conformance_passed
            ),
            "identity_score": identity_score,
            "continuity_score": continuity_score,
            "performance_score": performance_score,
            "camera_score": camera_score,
            "aggregate_score": aggregate,
            "findings": findings,
            "evidence": {
                "geometry_qc": geometry,
                "identity_qc": identity_qc,
                "performance_qc": performance_qc,
                "rendered_frame_qc": rendered_frame_qc,
                "rendered_identity_comparisons": identity_payload,
                "rendered_cut_appearance": cut_payload,
                "render_state": dict(
                    result.get("render_state") or {}
                ),
                "render_continuity": continuity_payload,
                "gaze_debug": gaze_rows,
                "lighting_debug": dict(
                    result.get("lighting_debug") or {}
                ),
                "creative_intent_bound": bool(
                    result.get("creative_intent_bound", False)
                ),
                "performance_directive_count": int(
                    result.get("performance_directive_count", 0)
                ),
                "visual_qc": dict(result.get("visual_qc") or {}),
                "runtime_qc_findings": list(
                    result.get("qc_findings") or []
                ),
            },
            "score_semantics": {
                "identity_score": (
                    (
                        "RENDERED_ACTOR_APPEARANCE_CONSISTENCY_"
                        "AGAINST_FIRST_ACCEPTED_BASELINE"
                    )
                    if measured_identity
                    else (
                        str(
                            identity_qc.get(
                                "metric",
                                "BACKEND_IDENTITY_QC",
                            )
                        )
                        if identity_score is not None
                        else "NOT_MEASURED"
                    )
                ),
                "continuity_score": (
                    (
                        "ADJACENT_RENDER_STATE_CONFORMANCE"
                        if continuity_labels == ["3D_STATE"]
                        else (
                            "ADJACENT_FRAME_APPEARANCE_CONFORMANCE"
                            if continuity_labels == ["FRAME_APPEARANCE"]
                            else (
                                "ADJACENT_RENDER_STATE_AND_FRAME_APPEARANCE_CONFORMANCE"
                                if continuity_labels
                                else "NOT_MEASURED"
                            )
                        )
                    )
                    if continuity_score is not None
                    else "NOT_MEASURED"
                ),
                "performance_score": (
                    "MEASURED_3D_ACTION_GAZE_CONTACT_BALANCE_CONFORMANCE"
                    if performance_qc.get("score") is not None
                    else (
                        "GAZE_EXECUTION_CONFORMANCE"
                        if performance_score is not None
                        else "NOT_MEASURED"
                    )
                ),
                "camera_score": (
                    "GEOMETRY_FRAMING_OCCLUSION_CONFORMANCE"
                    if camera_score is not None
                    else "NOT_MEASURED"
                ),
                "aggregate_score": (
                    "MEAN_OF_MEASURED_EXECUTION_CONFORMANCE_SCORES"
                    if measured_scores
                    else "NO_SEMANTIC_SCORE_MEASURED"
                ),
            },
        }

    @staticmethod
    def _appearance_context(
        result: dict[str, Any],
        *,
        evaluator: RenderedAppearanceEvaluator,
        actor_baselines: dict[str, ActorAppearanceEvidence],
        previous_frame_qc: RenderedFrameQCResult | None,
        previous_render_state: dict[str, Any] | None,
    ) -> tuple[
        RenderedFrameQCResult | None,
        list[ActorAppearanceComparison],
        CutAppearanceComparison | None,
    ]:
        raw = result.get("rendered_frame_qc")
        if not raw:
            return None, [], None
        current = RenderedFrameQCResult.model_validate(raw)
        comparisons = [
            evaluator.compare_actor(
                actor_baselines[actor_id],
                evidence,
            )
            for actor_id, evidence in current.actors.items()
            if actor_id in actor_baselines
        ]

        cut = None
        current_state = dict(result.get("render_state") or {})
        if (
            previous_frame_qc is not None
            and previous_render_state is not None
            and current_state
        ):
            previous_scene = previous_render_state.get("scene_id")
            current_scene = current_state.get("scene_id")
            same_scene = (
                bool(previous_scene)
                and previous_scene == current_scene
            )
            previous_light = (
                previous_render_state.get("lighting") or {}
            )
            current_light = current_state.get("lighting") or {}
            previous_intent = (
                previous_light.get("light_state"),
                previous_light.get("time_of_day"),
            )
            current_intent = (
                current_light.get("light_state"),
                current_light.get("time_of_day"),
            )
            same_lighting = (
                bool(previous_light or current_light)
                and previous_intent == current_intent
            )
            cut = evaluator.compare_cut(
                previous_frame_qc.tail,
                current.head,
                same_scene=same_scene,
                same_lighting_intent=same_lighting,
            )
        return current, comparisons, cut

    def produce(
        self,
        episode: EpisodeSpec,
        *,
        project_root: str | Path,
        render_preview: bool = False,
    ) -> DailiesReport:
        project_root = Path(project_root).resolve()
        output_dir = project_root / "renders" / "block_animation"
        compiled = self.assembler.compile(
            episode,
            output_dir=output_dir,
        )
        reports: list[ShotDailiesReport] = []
        continuity_evaluator = RenderContinuityEvaluator()
        appearance_evaluator = RenderedAppearanceEvaluator()
        failure_router = FailureRouter()
        actor_baselines: dict[str, ActorAppearanceEvidence] = {}
        previous_render_state: dict[str, Any] | None = None
        previous_frame_qc: RenderedFrameQCResult | None = None

        self.worker.start()
        for original_shot in compiled.shots:
            attempts: list[TakeRecord] = []
            current_shot = original_shot
            accepted_take: TakeRecord | None = None
            accepted_frame_qc: RenderedFrameQCResult | None = None
            accepted_render_state: dict[str, Any] | None = None
            final_directives = []
            final_findings: list[str] = []

            for repair_round in range(self.max_repair_rounds + 1):
                base_output = (
                    Path(original_shot.output_path)
                    if original_shot.output_path
                    else (
                        output_dir
                        / "shots"
                        / f"{original_shot.order:04d}_{original_shot.shot_id}.mp4"
                    )
                )
                if repair_round:
                    output_path = base_output.with_name(
                        base_output.stem
                        + f".repair{repair_round:02d}"
                        + base_output.suffix
                    )
                else:
                    output_path = base_output

                job = BlenderAnimationJob(
                    project_id=compiled.project_id,
                    episode_id=compiled.episode_id,
                    shot=current_shot,
                    output_path=str(output_path),
                    render_preview=render_preview,
                )
                take_id = (
                    f"{original_shot.shot_id}_BLENDER_"
                    f"{repair_round + 1:02d}"
                )
                result: dict[str, Any] = {}
                score_bundle: dict[str, Any] = {}
                current_frame_qc = None
                current_render_state: dict[str, Any] = {}
                repair_directives = []
                semantic_pass = False

                try:
                    result = self.runtime.render_and_qc(
                        self.worker,
                        job,
                    )
                    current_render_state = dict(
                        result.get("render_state") or {}
                    )
                    continuity = None
                    if (
                        bool(
                            result.get(
                                "creative_intent_bound",
                                False,
                            )
                        )
                        and previous_render_state is not None
                        and current_render_state
                    ):
                        continuity = continuity_evaluator.compare(
                            previous_render_state,
                            current_render_state,
                        )

                    (
                        current_frame_qc,
                        appearance_comparisons,
                        cut_appearance,
                    ) = self._appearance_context(
                        result,
                        evaluator=appearance_evaluator,
                        actor_baselines=actor_baselines,
                        previous_frame_qc=previous_frame_qc,
                        previous_render_state=previous_render_state,
                    )
                    score_bundle = self._evidence_scores(
                        result,
                        continuity=continuity,
                        appearance_comparisons=(
                            appearance_comparisons
                        ),
                        cut_appearance=cut_appearance,
                    )
                    semantic_pass = bool(
                        score_bundle[
                            "execution_conformance_passed"
                        ]
                    )
                    if not semantic_pass:
                        repair_directives = (
                            failure_router.classify_all(
                                original_shot.shot_id,
                                list(score_bundle["findings"])
                                or [
                                    "SEMANTIC_EXECUTION_CONFORMANCE_FAILED"
                                ],
                            )
                        )

                    take = TakeRecord(
                        take_id=take_id,
                        shot_id=original_shot.shot_id,
                        path=result["path"],
                        technical_pass=True,
                        visual_pass=semantic_pass,
                        identity_score=score_bundle[
                            "identity_score"
                        ],
                        continuity_score=score_bundle[
                            "continuity_score"
                        ],
                        performance_score=score_bundle[
                            "performance_score"
                        ],
                        camera_score=score_bundle[
                            "camera_score"
                        ],
                        aggregate_score=score_bundle[
                            "aggregate_score"
                        ],
                        failure_code=(
                            repair_directives[0].failure_code
                            if repair_directives
                            else None
                        ),
                        findings=score_bundle["findings"],
                        evidence=score_bundle["evidence"],
                        score_semantics=score_bundle[
                            "score_semantics"
                        ],
                        repair_round=repair_round,
                    )
                except Exception as exc:
                    error_finding = (
                        f"{type(exc).__name__}:{exc}"
                    )
                    repair_directives = (
                        failure_router.classify_all(
                            original_shot.shot_id,
                            [error_finding],
                        )
                    )
                    repair = repair_directives[0]
                    rendered_file_exists = output_path.exists()
                    semantic_after_render = (
                        rendered_file_exists
                        and (
                            "render frame QC failed"
                            in str(exc)
                            or "render visual QC failed"
                            in str(exc)
                            or "render combined QC failed"
                            in str(exc)
                        )
                    )
                    take = TakeRecord(
                        take_id=take_id,
                        shot_id=original_shot.shot_id,
                        path=(
                            str(output_path)
                            if rendered_file_exists
                            else ""
                        ),
                        technical_pass=semantic_after_render,
                        visual_pass=False,
                        aggregate_score=0.0,
                        failure_code=repair.failure_code,
                        findings=[error_finding],
                        repair_round=repair_round,
                        evidence={
                            "repair_exception": error_finding,
                        },
                    )

                attempts.append(take)

                if semantic_pass:
                    accepted_take = take
                    accepted_frame_qc = current_frame_qc
                    accepted_render_state = (
                        current_render_state or None
                    )
                    final_directives = []
                    final_findings = []
                    break

                final_directives = repair_directives
                final_findings = list(take.findings)

                if repair_round >= self.max_repair_rounds:
                    break

                previous_frame_payload = (
                    previous_frame_qc.model_dump(
                        mode="json"
                    )
                    if previous_frame_qc is not None
                    else None
                )
                repair_evidence = (
                    score_bundle.get("evidence", {})
                    if score_bundle
                    else {}
                )
                repair_plan = self.repair_planner.plan(
                    current_shot,
                    repair_directives,
                    repair_round=repair_round + 1,
                    evidence=repair_evidence,
                    previous_frame_qc=previous_frame_payload,
                )
                take.evidence["repair_plan_next"] = {
                    "repair_round": repair_plan.repair_round,
                    "supported": repair_plan.supported,
                    "applied": [
                        item.model_dump(mode="json")
                        for item in repair_plan.applied
                    ],
                    "skipped": list(repair_plan.skipped),
                }
                if (
                    not repair_plan.supported
                    or repair_plan.repaired_shot is None
                ):
                    break
                current_shot = repair_plan.repaired_shot

            if accepted_take is not None:
                if accepted_render_state:
                    previous_render_state = (
                        accepted_render_state
                    )
                else:
                    previous_render_state = None
                previous_frame_qc = accepted_frame_qc
                if accepted_frame_qc is not None:
                    for actor_id, actor_evidence in (
                        accepted_frame_qc.actors.items()
                    ):
                        actor_baselines.setdefault(
                            actor_id,
                            actor_evidence,
                        )
                report = ShotDailiesReport(
                    shot_id=original_shot.shot_id,
                    passed=True,
                    selected_take_id=accepted_take.take_id,
                    selected_path=accepted_take.path,
                    selected_score=(
                        accepted_take.aggregate_score
                    ),
                    takes=attempts,
                    findings=[],
                    repair_directives=[],
                )
            else:
                # A rejected shot must not become the entry-state
                # baseline for the next cut.
                previous_render_state = None
                previous_frame_qc = None
                report = ShotDailiesReport(
                    shot_id=original_shot.shot_id,
                    passed=False,
                    takes=attempts,
                    findings=(
                        final_findings
                        or sorted(
                            {
                                finding
                                for take in attempts
                                for finding in take.findings
                            }
                        )
                        or ["NO_ACCEPTABLE_TAKE"]
                    ),
                    repair_directives=final_directives,
                )

            reports.append(report)

        failed = [
            item.shot_id
            for item in reports
            if not item.passed
        ]
        repair_directives = [
            directive
            for report in reports
            for directive in report.repair_directives
        ]
        return DailiesReport(
            passed=not failed,
            shots=reports,
            findings=[
                f"BLOCK_RENDER_FAILED:{shot_id}"
                for shot_id in failed
            ],
            repair_directives=repair_directives,
        )


    @staticmethod
    def _daemon_loop(daemon: FactoryDaemon, stop_event: threading.Event, poll: float) -> None:
        try:
            while not stop_event.is_set():
                if not daemon.tick():
                    stop_event.wait(poll)
        finally:
            daemon.close()

    @staticmethod
    def _wait_turbo_items(
        store: Any,
        work_ids: list[str],
        *,
        deadline: float,
        poll_seconds: float,
        label: str,
    ) -> list[WorkItem]:
        terminal = {
            WorkState.SUCCESS,
            WorkState.QC_REJECTED,
            WorkState.BLOCKED,
            WorkState.DEAD_LETTER,
            WorkState.CANCELLED,
        }
        while time.monotonic() < deadline:
            items = [
                store.get_work(work_id)
                for work_id in work_ids
            ]
            if all(item.state in terminal for item in items):
                return items
            time.sleep(poll_seconds)
        states = {
            work_id: store.get_work(work_id).state.value
            for work_id in work_ids
        }
        raise TimeoutError(
            f"Turbo {label} timed out with states={states}"
        )

    def _enqueue_turbo_render(
        self,
        *,
        compiled: Any,
        shot: Any,
        output_path: Path,
        render_preview: bool,
        repair_round: int,
        repair_of_work_id: str | None = None,
        repair_directives: list[Any] | None = None,
        extra_payload: dict[str, Any] | None = None,
    ) -> WorkItem:
        payload = {
            "job": BlenderAnimationJob(
                project_id=compiled.project_id,
                episode_id=compiled.episode_id,
                shot=shot,
                output_path=str(output_path),
                render_preview=render_preview,
            ).model_dump(mode="json"),
            "output_units": max(1, shot.frame_end),
            "repair_round": repair_round,
            "repair_of_work_id": repair_of_work_id,
            "repair_directives": [
                item.model_dump(mode="json")
                for item in (repair_directives or [])
            ],
        }
        if self.blender_executable:
            payload["blender_executable"] = (
                self.blender_executable
            )
        if extra_payload:
            payload.update(dict(extra_payload))
        item = WorkItem(
            project_id=compiled.project_id,
            kind=(
                "block.render"
                if repair_round == 0
                else "block.render.repair"
            ),
            handler="blender.animation.render",
            resource=ResourceClass.GPU,
            priority=max(70, 98 - int(shot.order)),
            model_affinity=f"BLENDER:{shot.render_engine}",
            payload=payload,
            # One durable work item represents one take. Deterministic
            # QC failure is repaired by a new work item instead of
            # wasting GPU time retrying the identical bad contract.
            max_attempts=1,
        )
        self.ctx.turbo_store.enqueue_work(item)
        return item

    def _enqueue_turbo_post(
        self,
        *,
        compiled: Any,
        accepted: list[dict[str, Any]],
        output_dir: Path,
    ) -> tuple[list[str], str]:
        store = self.ctx.turbo_store
        timeline_ids: list[str] = []
        assembly_shots: list[dict[str, Any]] = []

        for row in accepted:
            shot = row["shot"]
            render_work_id = str(row["work_id"])
            path = str(row["path"])
            timeline = WorkItem(
                project_id=compiled.project_id,
                kind="timeline.accept",
                handler="timeline.accept",
                resource=ResourceClass.IO,
                priority=60,
                dependencies=[render_work_id],
                payload={
                    "shot_id": shot.shot_id,
                    "path": path,
                    "order": shot.order,
                    "duration_seconds": shot.duration_seconds,
                    "edit_intent": {
                        "camera_take": (
                            shot.camera_takes[0].take_id
                            if shot.camera_takes
                            else None
                        ),
                        "selected_render_work_id": (
                            render_work_id
                        ),
                        "repair_round": int(
                            row.get("repair_round", 0)
                        ),
                    },
                },
                max_attempts=2,
            )
            store.enqueue_work(timeline)
            timeline_ids.append(timeline.work_id)
            assembly_shots.append(
                {
                    "shot_id": shot.shot_id,
                    "order": shot.order,
                    "path": path,
                }
            )

        assemble = WorkItem(
            project_id=compiled.project_id,
            kind="block.episode.assemble",
            handler="block.episode.assemble",
            resource=ResourceClass.IO,
            priority=55,
            dependencies=timeline_ids,
            payload={
                "episode_id": compiled.episode_id,
                "output_path": str(
                    output_dir
                    / f"{compiled.episode_id}.mp4"
                ),
                "shots": assembly_shots,
            },
            max_attempts=2,
        )
        store.enqueue_work(assemble)
        return timeline_ids, assemble.work_id

    def _record_turbo_repair_memory(
        self,
        *,
        shot: Any,
        directives: list[Any],
        success: bool,
        score: float,
    ) -> None:
        store = self.ctx.turbo_store
        if not hasattr(store, "record_repair"):
            return
        for directive in directives:
            store.record_repair(
                key=(
                    "block_animation:"
                    f"{directive.failure_code.value}:"
                    f"{directive.action}"
                ),
                failure_code=directive.failure_code.value,
                workflow_id="block_animation",
                shot_class=str(
                    getattr(shot, "visual_style", None)
                    or "UNKNOWN"
                ),
                strategy=directive.action,
                prompt_directive=(
                    directive.prompt_directive
                ),
                success=success,
                score=float(score),
            )

    def produce_turbo(
        self,
        episode: EpisodeSpec,
        *,
        project_root: str | Path,
        timeout_seconds: int = 1800,
        poll_seconds: float = 0.02,
        render_preview: bool = False,
    ) -> DailiesReport:
        if (
            self.ctx is None
            or not hasattr(self.ctx, "turbo_store")
        ):
            raise RuntimeError(
                "Turbo production requires an AppContext "
                "with turbo_store"
            )

        project_root = Path(project_root).resolve()
        output_dir = (
            project_root / "renders" / "block_animation"
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        compiled = self.assembler.compile(
            episode,
            output_dir=output_dir,
        )
        store = self.ctx.turbo_store
        deadline = time.monotonic() + timeout_seconds

        gpu = FactoryDaemon(
            self.ctx,
            WorkerSpec(
                worker_id=(
                    f"company-gpu-{episode.project_id}"
                ),
                resources={ResourceClass.GPU},
                capabilities={
                    "blender.animation.render",
                    "block.video.comfy",
                },
                active_model_affinity=(
                    f"BLENDER:{episode.render_engine}"
                ),
            ),
            poll_seconds=poll_seconds,
        )
        gpu_stop = threading.Event()
        gpu_thread = threading.Thread(
            target=self._daemon_loop,
            args=(gpu, gpu_stop, poll_seconds),
            daemon=True,
        )

        initial_items: list[WorkItem] = []
        initial_shots: list[Any] = []
        proactive_routes: dict[str, dict[str, Any]] = {}
        for shot in compiled.shots:
            base_path = (
                Path(shot.output_path)
                if shot.output_path
                else (
                    output_dir
                    / "shots"
                    / f"{shot.order:04d}_{shot.shot_id}.mp4"
                )
            )
            route = None
            if self.shot_router is not None:
                route = self.shot_router.route(
                    project_id=compiled.project_id,
                    episode_id=compiled.episode_id,
                    shot=shot,
                    episode_metadata=dict(
                        episode.metadata or {}
                    ),
                )
                proactive_routes[shot.shot_id] = (
                    route.model_dump(mode="json")
                )
            if (
                route is not None
                and route.executable_method
                and route.method_decision is not None
                and self.method_switch is not None
            ):
                routed_shot = (
                    self.method_switch
                    .transform_block_shot(
                        shot,
                        route.method_decision,
                    )
                )
                item = self.method_switch.build_work_item(
                    compiled=compiled,
                    shot=routed_shot,
                    decision=route.method_decision,
                    output_path=base_path,
                    render_preview=render_preview,
                    switch_round=0,
                    switch_of_work_id=(
                        "PROACTIVE_SHOT_ROUTE"
                    ),
                    blender_executable=(
                        self.blender_executable
                    ),
                )
                item.payload["proactive_route"] = (
                    route.model_dump(mode="json")
                )
                store.enqueue_work(item)
                initial_items.append(item)
                initial_shots.append(routed_shot)
                continue
            if (
                route is not None
                and route.mode.value == "BLOCKED"
                and route.strict
            ):
                raise RuntimeError(
                    "PROACTIVE_SHOT_ROUTING_BLOCKED:"
                    + shot.shot_id
                    + ":"
                    + "|".join(route.blockers)
                )
            item = self._enqueue_turbo_render(
                compiled=compiled,
                shot=shot,
                output_path=base_path,
                render_preview=render_preview,
                repair_round=0,
                extra_payload=(
                    {
                        "proactive_route": route.model_dump(
                            mode="json"
                        )
                    }
                    if route is not None
                    else None
                ),
            )
            initial_items.append(item)
            initial_shots.append(shot)

        gpu_thread.start()
        reports: list[ShotDailiesReport] = []
        accepted_rows: list[dict[str, Any]] = []
        acquisition_by_shot: dict[str, str] = {}
        continuation_id = (
            f"{compiled.project_id}:{compiled.episode_id}"
        )
        continuity_evaluator = RenderContinuityEvaluator()
        appearance_evaluator = RenderedAppearanceEvaluator()
        failure_router = FailureRouter()
        actor_baselines: dict[
            str, ActorAppearanceEvidence
        ] = {}
        previous_render_state: (
            dict[str, Any] | None
        ) = None
        previous_frame_qc: (
            RenderedFrameQCResult | None
        ) = None
        economics_decisions: list[EconomicsDecision] = []
        project_gpu_budget = self.economics.project_gpu_budget(
            list(compiled.shots),
            episode_metadata=dict(episode.metadata or {}),
            global_max_repair_rounds=self.max_repair_rounds,
        )

        try:
            self._wait_turbo_items(
                store,
                [item.work_id for item in initial_items],
                deadline=deadline,
                poll_seconds=poll_seconds,
                label="initial renders",
            )

            for (
                original_shot,
                initial_item,
                routed_initial_shot,
            ) in zip(
                compiled.shots,
                initial_items,
                initial_shots,
            ):
                current_shot = routed_initial_shot
                current_work_id = initial_item.work_id
                attempts: list[TakeRecord] = []
                accepted_take: TakeRecord | None = None
                accepted_work_id: str | None = None
                accepted_frame_qc: (
                    RenderedFrameQCResult | None
                ) = None
                accepted_render_state: (
                    dict[str, Any] | None
                ) = None
                final_directives: list[Any] = []
                final_findings: list[str] = []
                pending_repair_directives: list[Any] = []
                lineage_work_ids = [initial_item.work_id]
                shot_budget = self.economics.budget_for(
                    original_shot,
                    episode_metadata=dict(episode.metadata or {}),
                    global_max_repair_rounds=self.max_repair_rounds,
                )

                for repair_round in range(
                    self.max_repair_rounds + 1
                ):
                    item = store.get_work(
                        current_work_id
                    )
                    job_payload = (
                        item.payload.get("job") or {}
                    )
                    video_payload = (
                        item.payload.get(
                            "video_request"
                        )
                        or {}
                    )
                    output_path = Path(
                        str(
                            job_payload.get(
                                "output_path"
                            )
                            or video_payload.get(
                                "output_path"
                            )
                            or current_shot.output_path
                            or ""
                        )
                    )
                    result = dict(item.result or {})
                    path = str(
                        result.get("path")
                        or (
                            output_path
                            if str(output_path)
                            else ""
                        )
                    )
                    rendered_file_exists = (
                        bool(path)
                        and Path(path).is_file()
                    )
                    render_success = (
                        item.state is WorkState.SUCCESS
                        and rendered_file_exists
                    )
                    quality_rejected = (
                        item.state is WorkState.QC_REJECTED
                        and rendered_file_exists
                        and bool(result)
                    )
                    media_evidence_available = (
                        render_success
                        or quality_rejected
                    )

                    score_bundle: dict[str, Any] = {}
                    current_frame_qc = None
                    current_render_state: (
                        dict[str, Any]
                    ) = {}
                    repair_directives: list[Any] = []
                    passed = False

                    if media_evidence_available:
                        current_render_state = dict(
                            result.get(
                                "render_state"
                            )
                            or {}
                        )
                        continuity = None
                        if (
                            bool(
                                result.get(
                                    "creative_intent_bound",
                                    False,
                                )
                            )
                            and previous_render_state
                            is not None
                            and current_render_state
                        ):
                            continuity = (
                                continuity_evaluator.compare(
                                    previous_render_state,
                                    current_render_state,
                                )
                            )
                        (
                            current_frame_qc,
                            appearance_comparisons,
                            cut_appearance,
                        ) = self._appearance_context(
                            result,
                            evaluator=(
                                appearance_evaluator
                            ),
                            actor_baselines=(
                                actor_baselines
                            ),
                            previous_frame_qc=(
                                previous_frame_qc
                            ),
                            previous_render_state=(
                                previous_render_state
                            ),
                        )
                        score_bundle = (
                            self._evidence_scores(
                                result,
                                continuity=continuity,
                                appearance_comparisons=(
                                    appearance_comparisons
                                ),
                                cut_appearance=(
                                    cut_appearance
                                ),
                            )
                        )
                        findings = list(
                            score_bundle["findings"]
                        )
                        hard_conformance_passed = (
                            item.state is WorkState.SUCCESS
                            and bool(
                                score_bundle[
                                    "execution_conformance_passed"
                                ]
                            )
                        )
                        quality_floor_passed = True
                        if (
                            hard_conformance_passed
                            and float(
                                score_bundle.get(
                                    "aggregate_score",
                                    0.0,
                                )
                            )
                            < shot_budget.quality_floor
                        ):
                            quality_floor_passed = False
                            findings.append(
                                "QUALITY_CLASS_FLOOR_MISS:"
                                f"{shot_budget.shot_class.value}:"
                                f"score={float(score_bundle.get('aggregate_score', 0.0)):.3f}:"
                                f"required={shot_budget.quality_floor:.3f}"
                            )
                        passed = (
                            hard_conformance_passed
                            and quality_floor_passed
                        )
                        if not passed:
                            repair_directives = (
                                failure_router.classify_all(
                                    original_shot.shot_id,
                                    findings
                                    or list(
                                        result.get(
                                            "qc_findings"
                                        )
                                        or []
                                    )
                                    or [
                                        "SEMANTIC_EXECUTION_"
                                        "CONFORMANCE_FAILED"
                                    ],
                                )
                            )
                        technical_pass = True
                    else:
                        error = (
                            item.last_error
                            or (
                                "TURBO_RENDER_"
                                f"{item.state.value}"
                            )
                        )
                        findings = [error]
                        repair_directives = (
                            failure_router.classify_all(
                                original_shot.shot_id,
                                findings,
                            )
                        )
                        technical_pass = False
                        score_bundle = {
                            "identity_score": None,
                            "continuity_score": None,
                            "performance_score": None,
                            "camera_score": None,
                            "aggregate_score": 0.0,
                            "evidence": {
                                "turbo_work_id": (
                                    current_work_id
                                ),
                                "turbo_state": (
                                    item.state.value
                                ),
                                "repair_round": (
                                    repair_round
                                ),
                            },
                            "score_semantics": {
                                "identity_score": (
                                    "NOT_MEASURED"
                                ),
                                "continuity_score": (
                                    "NOT_MEASURED"
                                ),
                                "performance_score": (
                                    "NOT_MEASURED"
                                ),
                                "camera_score": (
                                    "NOT_MEASURED"
                                ),
                                "aggregate_score": (
                                    "FAILED_RENDER"
                                ),
                            },
                        }

                    take_id = (
                        f"{original_shot.shot_id}"
                        f"_BLENDER_TURBO_"
                        f"{repair_round + 1:02d}"
                    )
                    take = TakeRecord(
                        take_id=take_id,
                        shot_id=original_shot.shot_id,
                        path=path,
                        technical_pass=technical_pass,
                        visual_pass=passed,
                        identity_score=(
                            score_bundle[
                                "identity_score"
                            ]
                        ),
                        continuity_score=(
                            score_bundle[
                                "continuity_score"
                            ]
                        ),
                        performance_score=(
                            score_bundle[
                                "performance_score"
                            ]
                        ),
                        camera_score=(
                            score_bundle[
                                "camera_score"
                            ]
                        ),
                        aggregate_score=(
                            score_bundle[
                                "aggregate_score"
                            ]
                        ),
                        failure_code=(
                            repair_directives[
                                0
                            ].failure_code
                            if repair_directives
                            else None
                        ),
                        findings=findings,
                        evidence={
                            **dict(
                                score_bundle.get(
                                    "evidence"
                                )
                                or {}
                            ),
                            "turbo_work_id": (
                                current_work_id
                            ),
                            "turbo_state": (
                                item.state.value
                            ),
                            "repair_round": (
                                repair_round
                            ),
                            "economics_budget": (
                                shot_budget.model_dump(
                                    mode="json"
                                )
                            ),
                            "production_method": (
                                {
                                    "method_switch": bool(
                                        item.payload.get(
                                            "method_switch",
                                            False,
                                        )
                                    ),
                                    "method_id": item.payload.get(
                                        "method_id"
                                    ),
                                    "method_switch_round": (
                                        item.payload.get(
                                            "method_switch_round"
                                        )
                                    ),
                                    "method_switch_of_work_id": (
                                        item.payload.get(
                                            "method_switch_of_work_id"
                                        )
                                    ),
                                }
                            ),
                        },
                        score_semantics=(
                            score_bundle[
                                "score_semantics"
                            ]
                        ),
                        repair_round=repair_round,
                    )
                    attempts.append(take)

                    if pending_repair_directives:
                        self._record_turbo_repair_memory(
                            shot=current_shot,
                            directives=(
                                pending_repair_directives
                            ),
                            success=passed,
                            score=take.aggregate_score,
                        )
                        pending_repair_directives = []

                    if passed:
                        accepted_take = take
                        accepted_work_id = (
                            current_work_id
                        )
                        accepted_frame_qc = (
                            current_frame_qc
                        )
                        accepted_render_state = (
                            current_render_state
                            or None
                        )
                        final_directives = []
                        final_findings = []
                        break

                    final_directives = (
                        repair_directives
                    )
                    final_findings = list(
                        take.findings
                    )

                    previous_frame_payload = (
                        previous_frame_qc.model_dump(
                            mode="json"
                        )
                        if previous_frame_qc
                        is not None
                        else None
                    )
                    memory_hints: dict[str, dict[str, Any]] = {}
                    shot_class = str(
                        getattr(
                            current_shot,
                            "visual_style",
                            None,
                        )
                        or "UNKNOWN"
                    )
                    for directive in repair_directives:
                        memory = store.best_repair(
                            failure_code=(
                                directive.failure_code.value
                            ),
                            workflow_id="block_animation",
                            shot_class=shot_class,
                        )
                        if memory is None:
                            continue
                        memory_hints[
                            directive.failure_code.value
                        ] = {
                            "strategy": memory.strategy,
                            "success_rate": (
                                memory.success_rate
                            ),
                            "attempts": memory.attempts,
                            "average_score": (
                                memory.average_score
                            ),
                            "key": memory.key,
                        }
                    repair_plan = (
                        self.repair_planner.plan(
                            current_shot,
                            repair_directives,
                            repair_round=(
                                repair_round + 1
                            ),
                            evidence=(
                                score_bundle.get(
                                    "evidence", {}
                                )
                                if score_bundle
                                else {}
                            ),
                            previous_frame_qc=(
                                previous_frame_payload
                            ),
                            preferred_strategies=(
                                memory_hints
                            ),
                        )
                    )
                    lineage_cost = (
                        store.execution_cost_for_work_ids(
                            lineage_work_ids
                        )
                    )
                    project_cost = (
                        store.execution_cost_summary(
                            project_id=episode.project_id
                        )
                    )
                    economics_decision = (
                        self.economics.decide_after_failure(
                            shot=original_shot,
                            directives=repair_directives,
                            current_repair_round=(
                                repair_round
                            ),
                            gpu_seconds_spent=float(
                                lineage_cost.get(
                                    "gpu_seconds",
                                    0.0,
                                )
                                or 0.0
                            ),
                            gpu_wasted_seconds=float(
                                lineage_cost.get(
                                    "gpu_wasted_seconds",
                                    0.0,
                                )
                                or 0.0
                            ),
                            mean_gpu_attempt_seconds=float(
                                lineage_cost.get(
                                    "mean_gpu_attempt_seconds",
                                    0.0,
                                )
                                or 0.0
                            ),
                            project_gpu_seconds=float(
                                project_cost.get(
                                    "gpu_seconds",
                                    0.0,
                                )
                                or 0.0
                            ),
                            project_gpu_budget=(
                                project_gpu_budget
                            ),
                            global_max_repair_rounds=(
                                self.max_repair_rounds
                            ),
                            episode_metadata=dict(
                                episode.metadata or {}
                            ),
                            memory_hints=memory_hints,
                            quality_score=(
                                take.aggregate_score
                            ),
                            local_repair_supported=(
                                repair_plan.supported
                                and repair_plan.repaired_shot
                                is not None
                            ),
                        )
                    )
                    economics_decisions.append(
                        economics_decision
                    )
                    take.evidence[
                        "economics_decision"
                    ] = economics_decision.model_dump(
                        mode="json"
                    )
                    take.evidence[
                        "repair_plan_next"
                    ] = {
                        "repair_round": (
                            repair_plan.repair_round
                        ),
                        "supported": (
                            repair_plan.supported
                        ),
                        "applied": [
                            row.model_dump(
                                mode="json"
                            )
                            for row
                            in repair_plan.applied
                        ],
                        "skipped": list(
                            repair_plan.skipped
                        ),
                        "memory_hints": list(
                            repair_plan.memory_hints
                        ),
                    }
                    if (
                        economics_decision.action
                        is EconomicsAction.SWITCH_METHOD
                        and self.method_switch is not None
                    ):
                        economics_cfg = dict(
                            (
                                original_shot.creative_intent.get(
                                    "economics"
                                )
                                or {}
                            )
                        )
                        switch_budget = economics_cfg.get(
                            "method_switch_gpu_seconds"
                        )
                        if switch_budget is None:
                            switch_budget = max(
                                0.001,
                                shot_budget.max_gpu_seconds
                                * 0.50,
                            )
                        policy_raw = (
                            economics_decision
                            .recommended_method_policy
                            or "QUALITY_FIRST_ALTERNATIVE"
                        )
                        try:
                            switch_policy = MethodSwitchPolicy(
                                policy_raw
                            )
                        except ValueError:
                            switch_policy = (
                                MethodSwitchPolicy
                                .BALANCED_ALTERNATIVE
                            )
                        current_method_id = (
                            "blender.cycles.quality"
                            if str(
                                current_shot.render_engine
                            ).upper() == "CYCLES"
                            else "blender.eevee.current"
                        )
                        switch_request = MethodSwitchRequest(
                            project_id=compiled.project_id,
                            episode_id=compiled.episode_id,
                            shot_id=original_shot.shot_id,
                            current_tool_id="blender",
                            current_method_id=current_method_id,
                            policy=switch_policy,
                            min_quality=shot_budget.quality_floor,
                            max_vram_gb=float(
                                economics_cfg.get(
                                    "max_vram_gb",
                                    12.0,
                                )
                            ),
                            local_only=True,
                            commercial_safe=True,
                            max_additional_gpu_seconds=float(
                                switch_budget
                            ),
                            mean_current_attempt_seconds=float(
                                lineage_cost.get(
                                    "mean_gpu_attempt_seconds",
                                    0.0,
                                )
                                or 0.0
                            ),
                            continuity_priority=bool(
                                original_shot.actors
                                or original_shot.creative_intent.get(
                                    "continuity_priority",
                                    True,
                                )
                            ),
                            backend_switch_allowed=bool(
                                original_shot.creative_intent.get(
                                    "backend_switch_allowed",
                                    False,
                                )
                            ),
                            recurring_identity_required=bool(
                                original_shot.actors
                            ),
                            reference_frame_path=(
                                path
                                if rendered_file_exists
                                else None
                            ),
                            precise_camera_required=bool(
                                original_shot.creative_intent.get(
                                    "precise_camera_required",
                                    False,
                                )
                            ),
                            semantic_performance_required=bool(
                                original_shot.creative_intent.get(
                                    "semantic_performance_required",
                                    False,
                                )
                                or original_shot.actions
                                or original_shot.expressions
                            ),
                            visual_style=str(
                                getattr(
                                    original_shot,
                                    "visual_style",
                                    "",
                                )
                                or ""
                            ),
                            failure_codes=[
                                directive.failure_code.value
                                for directive in repair_directives
                            ],
                        )
                        method_decision = (
                            self.method_switch.deliberate(
                                switch_request
                            )
                        )
                        take.evidence[
                            "method_switch_decision"
                        ] = method_decision.model_dump(
                            mode="json"
                        )
                        if method_decision.executable:
                            switched_shot = (
                                self.method_switch
                                .transform_block_shot(
                                    current_shot,
                                    method_decision,
                                    repaired_base=(
                                        repair_plan.repaired_shot
                                    ),
                                )
                            )
                            switch_round = repair_round + 1
                            base_path = (
                                Path(
                                    original_shot.output_path
                                )
                                if original_shot.output_path
                                else (
                                    output_dir
                                    / "shots"
                                    / (
                                        f"{original_shot.order:04d}_"
                                        f"{original_shot.shot_id}.mp4"
                                    )
                                )
                            )
                            switched_path = (
                                base_path.with_name(
                                    base_path.stem
                                    + (
                                        ".method_switch"
                                        f"{switch_round:02d}"
                                    )
                                    + base_path.suffix
                                )
                            )
                            switch_item = (
                                self.method_switch
                                .build_work_item(
                                    compiled=compiled,
                                    shot=switched_shot,
                                    decision=method_decision,
                                    output_path=switched_path,
                                    render_preview=(
                                        render_preview
                                    ),
                                    switch_round=(
                                        switch_round
                                    ),
                                    switch_of_work_id=(
                                        current_work_id
                                    ),
                                    blender_executable=(
                                        self.blender_executable
                                    ),
                                )
                            )
                            store.enqueue_work(switch_item)
                            lineage_work_ids.append(
                                switch_item.work_id
                            )
                            self._wait_turbo_items(
                                store,
                                [switch_item.work_id],
                                deadline=deadline,
                                poll_seconds=poll_seconds,
                                label=(
                                    "method switch render "
                                    f"{original_shot.shot_id}"
                                ),
                            )
                            current_shot = switched_shot
                            current_work_id = (
                                switch_item.work_id
                            )
                            pending_repair_directives = []
                            continue

                        resume_shot = (
                            repair_plan.repaired_shot
                            or current_shot
                        )
                        resume_base_path = (
                            Path(original_shot.output_path)
                            if original_shot.output_path
                            else (
                                output_dir
                                / "shots"
                                / (
                                    f"{original_shot.order:04d}_"
                                    f"{original_shot.shot_id}.mp4"
                                )
                            )
                        )
                        resume_round = repair_round + 1
                        resume_output_path = (
                            resume_base_path.with_name(
                                resume_base_path.stem
                                + (
                                    ".capability_resume"
                                    f"{resume_round:02d}"
                                )
                                + resume_base_path.suffix
                            )
                        )
                        acquisition_item = (
                            self.method_switch
                            .build_acquisition_work_item(
                                method_decision,
                                resume_context={
                                    "shot": (
                                        resume_shot.model_dump(
                                            mode="json"
                                        )
                                    ),
                                    "output_path": str(
                                        resume_output_path
                                    ),
                                    "render_preview": bool(
                                        render_preview
                                    ),
                                    "switch_round": (
                                        resume_round
                                    ),
                                    "switch_of_work_id": (
                                        current_work_id
                                    ),
                                    "blender_executable": (
                                        self.blender_executable
                                    ),
                                    "continuation_id": (
                                        continuation_id
                                    ),
                                    "continuation_shot_id": (
                                        original_shot.shot_id
                                    ),
                                },
                            )
                        )
                        store.enqueue_work(acquisition_item)
                        acquisition_by_shot[
                            original_shot.shot_id
                        ] = acquisition_item.work_id
                        take.evidence[
                            "capability_acquisition_work_id"
                        ] = acquisition_item.work_id
                        economics_directive = (
                            self.economics.decision_directive(
                                economics_decision
                            )
                        )
                        final_directives = [
                            economics_directive,
                            *repair_directives,
                        ]
                        final_findings = [
                            *take.findings,
                            (
                                "ECONOMICS_DECISION:"
                                f"{economics_decision.action.value}"
                            ),
                            (
                                "METHOD_SWITCH_STATUS:"
                                f"{method_decision.status.value}"
                            ),
                            (
                                "CAPABILITY_ACQUISITION_WORK:"
                                f"{acquisition_item.work_id}"
                            ),
                            *[
                                "METHOD_SWITCH_REASON:"
                                + reason
                                for reason
                                in method_decision.reasons
                            ],
                        ]
                        if (
                            method_decision
                            .acquisition_request_path
                        ):
                            final_findings.append(
                                "CAPABILITY_ACQUISITION_REQUEST:"
                                + str(
                                    method_decision
                                    .acquisition_request_path
                                )
                            )
                        break

                    if (
                        economics_decision.action
                        is not EconomicsAction.REPAIR_LOCAL
                    ):
                        economics_directive = (
                            self.economics.decision_directive(
                                economics_decision
                            )
                        )
                        final_directives = [
                            economics_directive,
                            *repair_directives,
                        ]
                        final_findings = [
                            *take.findings,
                            (
                                "ECONOMICS_DECISION:"
                                f"{economics_decision.action.value}"
                            ),
                            *[
                                "ECONOMICS_REASON:" + reason
                                for reason
                                in economics_decision.reason_codes
                            ],
                        ]
                        break

                    if (
                        not repair_plan.supported
                        or repair_plan.repaired_shot
                        is None
                    ):
                        break

                    current_shot = (
                        repair_plan.repaired_shot
                    )
                    base_path = (
                        Path(
                            original_shot.output_path
                        )
                        if original_shot.output_path
                        else (
                            output_dir
                            / "shots"
                            / (
                                f"{original_shot.order:04d}_"
                                f"{original_shot.shot_id}.mp4"
                            )
                        )
                    )
                    next_round = repair_round + 1
                    repaired_path = (
                        base_path.with_name(
                            base_path.stem
                            + (
                                f".turbo_repair"
                                f"{next_round:02d}"
                            )
                            + base_path.suffix
                        )
                    )
                    repair_item = (
                        self._enqueue_turbo_render(
                            compiled=compiled,
                            shot=current_shot,
                            output_path=repaired_path,
                            render_preview=(
                                render_preview
                            ),
                            repair_round=(
                                next_round
                            ),
                            repair_of_work_id=(
                                current_work_id
                            ),
                            repair_directives=(
                                repair_directives
                            ),
                        )
                    )
                    lineage_work_ids.append(
                        repair_item.work_id
                    )
                    pending_repair_directives = (
                        list(repair_directives)
                    )
                    self._wait_turbo_items(
                        store,
                        [repair_item.work_id],
                        deadline=deadline,
                        poll_seconds=poll_seconds,
                        label=(
                            "repair render "
                            f"{original_shot.shot_id}"
                        ),
                    )
                    current_work_id = (
                        repair_item.work_id
                    )

                if accepted_take is not None:
                    previous_render_state = (
                        accepted_render_state
                    )
                    previous_frame_qc = (
                        accepted_frame_qc
                    )
                    if (
                        accepted_frame_qc
                        is not None
                    ):
                        for (
                            actor_id,
                            actor_evidence,
                        ) in (
                            accepted_frame_qc
                            .actors.items()
                        ):
                            actor_baselines.setdefault(
                                actor_id,
                                actor_evidence,
                            )
                    reports.append(
                        ShotDailiesReport(
                            shot_id=(
                                original_shot.shot_id
                            ),
                            passed=True,
                            selected_take_id=(
                                accepted_take.take_id
                            ),
                            selected_path=(
                                accepted_take.path
                            ),
                            selected_score=(
                                accepted_take
                                .aggregate_score
                            ),
                            takes=attempts,
                            findings=[],
                            repair_directives=[],
                        )
                    )
                    accepted_rows.append(
                        {
                            "shot": original_shot,
                            "work_id": (
                                accepted_work_id
                            ),
                            "path": (
                                accepted_take.path
                            ),
                            "repair_round": (
                                accepted_take
                                .repair_round
                            ),
                        }
                    )
                else:
                    previous_render_state = None
                    previous_frame_qc = None
                    reports.append(
                        ShotDailiesReport(
                            shot_id=(
                                original_shot.shot_id
                            ),
                            passed=False,
                            takes=attempts,
                            findings=(
                                final_findings
                                or [
                                    "NO_ACCEPTABLE_TURBO_TAKE"
                                ]
                            ),
                            repair_directives=(
                                final_directives
                            ),
                        )
                    )
        finally:
            gpu_stop.set()
            gpu_thread.join(timeout=10)
            gpu.close()

        failed = [
            report.shot_id
            for report in reports
            if not report.passed
        ]
        if failed:
            continuation_manager = getattr(
                self.ctx,
                "production_continuation",
                None,
            )
            if (
                continuation_manager is not None
                and acquisition_by_shot
            ):
                continuation_manager.create_blocked_episode(
                    compiled=compiled,
                    output_dir=output_dir,
                    accepted_rows=accepted_rows,
                    acquisition_by_shot=acquisition_by_shot,
                )
            directives = [
                directive
                for report in reports
                for directive
                in report.repair_directives
            ]
            return DailiesReport(
                passed=False,
                shots=reports,
                findings=[
                    f"BLOCK_RENDER_FAILED:{shot_id}"
                    for shot_id in failed
                ],
                repair_directives=directives,
                execution_metrics=(
                    self._economics_execution_metrics(
                        store,
                        episode=episode,
                        compiled=compiled,
                        decisions=economics_decisions,
                        shot_routing=proactive_routes,
                    )
                ),
            )

        timeline_ids, assemble_id = (
            self._enqueue_turbo_post(
                compiled=compiled,
                accepted=accepted_rows,
                output_dir=output_dir,
            )
        )
        io = FactoryDaemon(
            self.ctx,
            WorkerSpec(
                worker_id=(
                    f"company-io-{episode.project_id}"
                ),
                resources={ResourceClass.IO},
                capabilities={
                    "timeline.accept",
                    "block.episode.assemble",
                },
            ),
            poll_seconds=poll_seconds,
        )
        io_stop = threading.Event()
        io_thread = threading.Thread(
            target=self._daemon_loop,
            args=(io, io_stop, poll_seconds),
            daemon=True,
        )
        io_thread.start()
        try:
            self._wait_turbo_items(
                store,
                timeline_ids + [assemble_id],
                deadline=deadline,
                poll_seconds=poll_seconds,
                label="post/assembly",
            )
        finally:
            io_stop.set()
            io_thread.join(timeout=10)
            io.close()

        post_findings: list[str] = []
        for work_id in timeline_ids:
            item = store.get_work(work_id)
            if item.state is not WorkState.SUCCESS:
                post_findings.append(
                    item.last_error
                    or (
                        "TURBO_TIMELINE_"
                        f"{item.state.value}"
                    )
                )
        assemble = store.get_work(assemble_id)
        if assemble.state is not WorkState.SUCCESS:
            post_findings.append(
                assemble.last_error
                or (
                    "BLOCK_EPISODE_ASSEMBLY_"
                    f"{assemble.state.value}"
                )
            )

        return DailiesReport(
            passed=not post_findings,
            shots=reports,
            findings=post_findings,
            repair_directives=[],
            execution_metrics=(
                self._economics_execution_metrics(
                    store,
                    episode=episode,
                    compiled=compiled,
                    decisions=economics_decisions,
                    shot_routing=proactive_routes,
                )
            ),
        )
