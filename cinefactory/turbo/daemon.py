from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from cinefactory.turbo.blender import BlenderHeadlessWorker, BlenderPrevisJob, PersistentBlenderWorker
from cinefactory.block_animation.contracts import BlenderAnimationJob
from cinefactory.block_animation.runtime import BlockAnimationRuntime, RenderQualityRejected
from cinefactory.turbo.contracts import (
    ExecutionCostSample,
    FactoryEvent,
    ResourceClass,
    ThroughputSample,
    WorkerSpec,
    WorkItem,
    WorkState,
)
from cinefactory.turbo.incremental_editor import IncrementalTimeline
from cinefactory.turbo.metrics import gpu_snapshot
from cinefactory.turbo.scheduler import ModelAffinityScheduler
from cinefactory.turbo.store import TurboStore


Handler=Callable[[WorkItem],dict|None]


class WorkDeferred(RuntimeError):
    def __init__(
        self,
        reason: str,
        *,
        delay_seconds: int,
        result: dict | None = None,
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.delay_seconds = max(1, int(delay_seconds))
        self.result = dict(result or {})


class FactoryDaemon:
    """Always-on event/work daemon.

    The daemon never owns FilmSpec or creative truth. It executes durable work items,
    publishes completion events and records throughput. OpenClaw can supervise it through
    the thin API without polling ComfyUI or touching the database directly.
    """
    def __init__(self,ctx,worker:WorkerSpec,*,poll_seconds:float=0.25)->None:
        self.ctx=ctx; self.worker=worker; self.poll_seconds=poll_seconds
        self.store:TurboStore=ctx.turbo_store; self.scheduler=ModelAffinityScheduler(self.store)
        self.handlers:dict[str,Handler]={}
        self._persistent_blender:PersistentBlenderWorker|None=None
        self._block_runtime=BlockAnimationRuntime(ctx.root)
        self.register("job.execute",self._execute_job)
        self.register("comfy.execute",self._comfy_execute)
        self.register("timeline.accept",self._timeline_accept)
        self.register("blender.previs",self._blender_previs)
        self.register("blender.animation.render",self._blender_animation_render)
        self.register("block.episode.assemble",self._block_episode_assemble)
        self.register("rnd.capability.acquire",self._rnd_capability_acquire)
        self.register("lab.comfyui.execute",self._lab_comfyui_execute)
        self.register("block.video.comfy",self._block_video_comfy)
        self.register("noop",lambda item:{"ok":True})

    def register(self,name:str,handler:Handler)->None: self.handlers[name]=handler

    def _execute_job(self,item:WorkItem)->dict:
        job_id=str(item.payload["job_id"]); job=self.ctx.job_service.execute_now(job_id,worker_id=self.worker.worker_id)
        if job.state.value!="SUCCESS": raise RuntimeError(f"job {job_id} ended {job.state.value}: {job.error_detail}")
        return {"job_id":job_id,"artifacts":job.output_artifact_ids}

    def _comfy_execute(self,item:WorkItem)->dict:
        executor=self.ctx.executors.get("local.comfyui")
        result=executor.execute(dict(item.payload))
        if not result.ok:
            raise RuntimeError(result.error or "ComfyUI render failed")
        return {"ok":True,"artifacts":result.artifacts,"metadata":result.metadata}

    def _timeline_accept(self,item:WorkItem)->dict:
        path=self.ctx.root/"data"/"projects"/item.project_id/"post"/"incremental_timeline.json"
        tl=IncrementalTimeline(path)
        data=tl.accept_shot(shot_id=str(item.payload['shot_id']),path=str(item.payload['path']),order=int(item.payload['order']),duration_seconds=item.payload.get('duration_seconds'),edit_intent=item.payload.get('edit_intent'))
        return {"timeline":str(path),"revision":data['revision']}

    def _blender_previs(self,item:WorkItem)->dict:
        worker=BlenderHeadlessWorker(self.ctx.root,item.payload.get("blender_executable","blender"))
        job=BlenderPrevisJob.model_validate(item.payload["job"]); return {"path":worker.execute(job)}


    def _blender_animation_render(self,item:WorkItem)->dict:
        if self._persistent_blender is None:self._persistent_blender=PersistentBlenderWorker(self.ctx.root,item.payload.get("blender_executable","blender"))
        return self._block_runtime.render_and_qc(self._persistent_blender,BlenderAnimationJob.model_validate(item.payload["job"]))

    def _block_episode_assemble(self,item:WorkItem)->dict:
        return self._block_runtime.assemble_episode(item.payload)

    def _rnd_capability_acquire(self,item:WorkItem)->dict:
        worker=getattr(self.ctx,"capability_acquisition",None)
        if worker is None:
            raise RuntimeError("CAPABILITY_ACQUISITION_WORKER_NOT_CONFIGURED")
        outcome=worker.process(item)
        result=outcome.model_dump(mode="json")
        if outcome.deferred:
            raise WorkDeferred(
                outcome.reason or "CAPABILITY_ACQUISITION_DEFERRED",
                delay_seconds=outcome.defer_seconds or 300,
                result=result,
            )
        return result

    def _lab_comfyui_execute(self,item:WorkItem)->dict:
        controller=getattr(self.ctx,"candidate_promotion",None)
        if controller is None:
            raise RuntimeError("CANDIDATE_PROMOTION_CONTROLLER_NOT_CONFIGURED")
        return controller.execute_comfyui_lab_work_item(item)

    def _block_video_comfy(self,item:WorkItem)->dict:
        service=getattr(self.ctx,"cross_backend_video",None)
        if service is None:
            raise RuntimeError("CROSS_BACKEND_VIDEO_SERVICE_NOT_CONFIGURED")
        result=service.execute_work_item(item)
        if not bool(result.get("qc_passed",False)):
            raise RenderQualityRejected(
                list(result.get("qc_findings") or ["CROSS_BACKEND_VIDEO_QC_FAILED"]),
                result=result,
            )
        return result

    def close(self)->None:
        if self._persistent_blender is not None:self._persistent_blender.close(); self._persistent_blender=None

    def _record_execution_cost(
        self,
        item: WorkItem,
        *,
        state: WorkState,
        elapsed: float,
        accepted: bool,
    ) -> None:
        self.store.add_execution_cost(
            ExecutionCostSample(
                work_id=item.work_id,
                project_id=item.project_id,
                worker_id=self.worker.worker_id,
                kind=item.kind,
                resource=item.resource,
                state=state,
                duration_seconds=max(0.0001, elapsed),
                output_units=float(
                    item.payload.get("output_units", 1.0) or 1.0
                ),
                accepted=accepted,
                repair_round=int(
                    item.payload.get("repair_round", 0) or 0
                ),
            )
        )

    def tick(self)->bool:
        self.worker.last_heartbeat = datetime.now(timezone.utc)
        self.worker.metadata["gpu"] = gpu_snapshot()
        self.worker.metadata["ready_depth"] = self.store.ready_work_count(
            self.worker
        )
        self.store.upsert_worker(self.worker)
        item = self.scheduler.claim(self.worker)
        if item is None:
            return False

        started = time.monotonic()
        self.store.mark_running(item.work_id)
        handler = self.handlers.get(item.handler)
        if handler is None:
            state = self.store.finish_work(
                item.work_id,
                False,
                f"Unknown handler {item.handler}",
            )
            self._record_execution_cost(
                item,
                state=state,
                elapsed=time.monotonic() - started,
                accepted=False,
            )
            return True

        try:
            result = handler(item) or {}
            state = self.store.finish_work(
                item.work_id,
                True,
                result=result,
            )
            continuation = dict(
                item.payload.get("continuation") or {}
            )
            continuation_result = None
            if (
                continuation
                and result.get("path")
                and getattr(
                    self.ctx,
                    "production_continuation",
                    None,
                )
                is not None
            ):
                try:
                    continuation_result = (
                        self.ctx.production_continuation
                        .accept_requeued_render(
                            continuation_id=str(
                                continuation[
                                    "continuation_id"
                                ]
                            ),
                            shot_id=str(
                                continuation["shot_id"]
                            ),
                            render_work_id=item.work_id,
                            path=str(result["path"]),
                            method_id=item.payload.get(
                                "method_id"
                            ),
                        )
                    )
                except Exception as exc:
                    self.store.publish_event(
                        FactoryEvent(
                            event_type=(
                                "PRODUCTION_CONTINUATION_FAILED"
                            ),
                            project_id=item.project_id,
                            entity_id=item.work_id,
                            priority=90,
                            payload={
                                "kind": item.kind,
                                "error": (
                                    f"{type(exc).__name__}:{exc}"
                                ),
                                "continuation": continuation,
                            },
                        )
                    )
            if continuation_result is not None:
                result["continuation"] = (
                    continuation_result.model_dump(
                        mode="json"
                    )
                )
            if item.model_affinity:
                self.worker.active_model_affinity = (
                    item.model_affinity
                )
            self.store.publish_event(
                FactoryEvent(
                    event_type="WORK_SUCCEEDED",
                    project_id=item.project_id,
                    entity_id=item.work_id,
                    payload={
                        "kind": item.kind,
                        "result": result,
                    },
                )
            )
            elapsed = max(
                0.0001,
                time.monotonic() - started,
            )
            units = float(
                item.payload.get("output_units", 1.0) or 1.0
            )
            self.store.add_throughput(
                ThroughputSample(
                    worker_id=self.worker.worker_id,
                    kind=item.kind,
                    model_affinity=item.model_affinity,
                    duration_seconds=elapsed,
                    output_units=units,
                )
            )
            self._record_execution_cost(
                item,
                state=state,
                elapsed=elapsed,
                accepted=True,
            )
        except WorkDeferred as exc:
            state = self.store.defer_work(
                item.work_id,
                delay_seconds=exc.delay_seconds,
                reason=exc.reason,
                result=exc.result,
            )
            self.store.publish_event(
                FactoryEvent(
                    event_type="WORK_DEFERRED",
                    project_id=item.project_id,
                    entity_id=item.work_id,
                    priority=55,
                    payload={
                        "kind": item.kind,
                        "state": state.value,
                        "reason": exc.reason,
                        "delay_seconds": exc.delay_seconds,
                        "result": exc.result,
                    },
                )
            )
        except RenderQualityRejected as exc:
            state = self.store.reject_work(
                item.work_id,
                str(exc),
                result=exc.result,
            )
            elapsed = max(
                0.0001,
                time.monotonic() - started,
            )
            self._record_execution_cost(
                item,
                state=state,
                elapsed=elapsed,
                accepted=False,
            )
            self.store.publish_event(
                FactoryEvent(
                    event_type="WORK_QC_REJECTED",
                    project_id=item.project_id,
                    entity_id=item.work_id,
                    priority=75,
                    payload={
                        "kind": item.kind,
                        "state": state.value,
                        "error": str(exc),
                        "findings": list(exc.findings),
                        "elapsed_seconds": elapsed,
                        "repair_round": int(
                            item.payload.get(
                                "repair_round",
                                0,
                            )
                            or 0
                        ),
                    },
                )
            )
        except Exception as exc:
            state = self.store.finish_work(
                item.work_id,
                False,
                str(exc),
            )
            elapsed = max(
                0.0001,
                time.monotonic() - started,
            )
            self._record_execution_cost(
                item,
                state=state,
                elapsed=elapsed,
                accepted=False,
            )
            self.store.publish_event(
                FactoryEvent(
                    event_type="WORK_FAILED",
                    project_id=item.project_id,
                    entity_id=item.work_id,
                    priority=90,
                    payload={
                        "kind": item.kind,
                        "state": state.value,
                        "error": str(exc),
                        "elapsed_seconds": elapsed,
                    },
                )
            )
        self.store.upsert_worker(self.worker)
        return True

    def run_forever(self)->None:
        try:
            while True:
                if not self.tick(): time.sleep(self.poll_seconds)
        finally:
            self.close()
