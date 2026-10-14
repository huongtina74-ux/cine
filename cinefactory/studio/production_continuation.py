from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkItem,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ContinuationShotState(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    WAITING_CAPABILITY = "WAITING_CAPABILITY"
    REQUEUED = "REQUEUED"
    FAILED = "FAILED"


class ContinuationShot(BaseModel):
    shot_id: str
    order: int
    duration_seconds: float = Field(gt=0)
    edit_intent: dict[str, Any] = Field(default_factory=dict)
    state: ContinuationShotState = ContinuationShotState.PENDING
    render_work_id: str | None = None
    acquisition_work_id: str | None = None
    path: str | None = None
    method_id: str | None = None


class EpisodeContinuation(BaseModel):
    continuation_id: str
    project_id: str
    episode_id: str
    output_path: str
    shots: list[ContinuationShot] = Field(default_factory=list)
    post_enqueued: bool = False
    timeline_work_ids: list[str] = Field(default_factory=list)
    assembly_work_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @property
    def all_accepted(self) -> bool:
        return bool(self.shots) and all(
            item.state is ContinuationShotState.ACCEPTED
            and item.path
            and item.render_work_id
            for item in self.shots
        )


class ContinuationResumeResult(BaseModel):
    continuation_id: str
    shot_id: str
    accepted: bool
    all_accepted: bool
    post_enqueued: bool
    timeline_work_ids: list[str] = Field(default_factory=list)
    assembly_work_id: str | None = None


class ProductionContinuationStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _key(value: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value)[:32]
        digest = hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()[:10]
        return f"{safe or 'continuation'}-{digest}"

    def path(self, continuation_id: str) -> Path:
        return self.root / f"{self._key(continuation_id)}.json"

    def save(
        self,
        record: EpisodeContinuation,
    ) -> EpisodeContinuation:
        record.updated_at = utcnow()
        self.path(record.continuation_id).write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return record

    def get(self, continuation_id: str) -> EpisodeContinuation:
        path = self.path(continuation_id)
        if not path.exists():
            raise KeyError(continuation_id)
        return EpisodeContinuation.model_validate_json(
            path.read_text(encoding="utf-8")
        )


class ProductionContinuationManager:
    """Durable post-acquisition episode continuation.

    It only resumes deterministic post-production after every shot in the
    episode has an accepted render work item. It never treats a queued/rejected
    acquisition render as accepted media.
    """

    def __init__(
        self,
        root: str | Path,
        turbo_store,
        *,
        store: ProductionContinuationStore | None = None,
    ) -> None:
        self.root = Path(root)
        self.turbo_store = turbo_store
        self.store = store or ProductionContinuationStore(
            self.root
            / "data"
            / "studio"
            / "production_continuation"
        )

    @staticmethod
    def continuation_id(
        project_id: str,
        episode_id: str,
    ) -> str:
        return f"{project_id}:{episode_id}"

    @staticmethod
    def _timeline_work_id(
        continuation_id: str,
        shot_id: str,
    ) -> str:
        digest = hashlib.sha256(
            f"{continuation_id}:timeline:{shot_id}".encode("utf-8")
        ).hexdigest()[:14]
        return f"WORK_CONT_TL_{digest}"

    @staticmethod
    def _assembly_work_id(
        continuation_id: str,
    ) -> str:
        digest = hashlib.sha256(
            f"{continuation_id}:assembly".encode("utf-8")
        ).hexdigest()[:14]
        return f"WORK_CONT_ASM_{digest}"

    @staticmethod
    def _shot_edit_intent(shot: Any) -> dict[str, Any]:
        return {
            "camera_take": (
                shot.camera_takes[0].take_id
                if getattr(shot, "camera_takes", None)
                else None
            ),
            "continuation_recovery": True,
        }

    def create_blocked_episode(
        self,
        *,
        compiled: Any,
        output_dir: str | Path,
        accepted_rows: list[dict[str, Any]],
        acquisition_by_shot: dict[str, str],
    ) -> EpisodeContinuation:
        continuation_id = self.continuation_id(
            compiled.project_id,
            compiled.episode_id,
        )
        accepted_by_shot = {
            str(row["shot"].shot_id): row
            for row in accepted_rows
        }
        shots: list[ContinuationShot] = []
        for shot in sorted(
            compiled.shots,
            key=lambda item: int(item.order),
        ):
            accepted = accepted_by_shot.get(shot.shot_id)
            acquisition_work_id = acquisition_by_shot.get(
                shot.shot_id
            )
            if accepted is not None:
                state = ContinuationShotState.ACCEPTED
                render_work_id = str(accepted["work_id"])
                path = str(accepted["path"])
            elif acquisition_work_id:
                state = (
                    ContinuationShotState.WAITING_CAPABILITY
                )
                render_work_id = None
                path = None
            else:
                state = ContinuationShotState.FAILED
                render_work_id = None
                path = None
            shots.append(
                ContinuationShot(
                    shot_id=shot.shot_id,
                    order=int(shot.order),
                    duration_seconds=float(
                        shot.duration_seconds
                    ),
                    edit_intent=self._shot_edit_intent(shot),
                    state=state,
                    render_work_id=render_work_id,
                    acquisition_work_id=acquisition_work_id,
                    path=path,
                )
            )

        record = EpisodeContinuation(
            continuation_id=continuation_id,
            project_id=compiled.project_id,
            episode_id=compiled.episode_id,
            output_path=str(
                Path(output_dir)
                / f"{compiled.episode_id}.mp4"
            ),
            shots=shots,
        )
        return self.store.save(record)

    def mark_requeued(
        self,
        *,
        continuation_id: str,
        shot_id: str,
        render_work_id: str,
        method_id: str | None,
    ) -> EpisodeContinuation:
        record = self.store.get(continuation_id)
        shot = next(
            item
            for item in record.shots
            if item.shot_id == shot_id
        )
        shot.state = ContinuationShotState.REQUEUED
        shot.render_work_id = render_work_id
        shot.method_id = method_id
        return self.store.save(record)

    def _enqueue_post(
        self,
        record: EpisodeContinuation,
    ) -> EpisodeContinuation:
        if record.post_enqueued:
            return record
        if not record.all_accepted:
            return record

        timeline_ids: list[str] = []
        assembly_shots: list[dict[str, Any]] = []
        for shot in sorted(
            record.shots,
            key=lambda item: item.order,
        ):
            assert shot.render_work_id
            assert shot.path
            timeline_id = self._timeline_work_id(
                record.continuation_id,
                shot.shot_id,
            )
            timeline = WorkItem(
                work_id=timeline_id,
                project_id=record.project_id,
                kind="timeline.accept",
                handler="timeline.accept",
                resource=ResourceClass.IO,
                priority=60,
                dependencies=[shot.render_work_id],
                payload={
                    "shot_id": shot.shot_id,
                    "path": shot.path,
                    "order": shot.order,
                    "duration_seconds": shot.duration_seconds,
                    "edit_intent": {
                        **dict(shot.edit_intent),
                        "selected_render_work_id": (
                            shot.render_work_id
                        ),
                        "recovered_after_acquisition": True,
                        "method_id": shot.method_id,
                    },
                },
                max_attempts=2,
            )
            self.turbo_store.enqueue_work(timeline)
            timeline_ids.append(timeline_id)
            assembly_shots.append(
                {
                    "shot_id": shot.shot_id,
                    "order": shot.order,
                    "path": shot.path,
                }
            )

        assembly_id = self._assembly_work_id(
            record.continuation_id
        )
        assembly = WorkItem(
            work_id=assembly_id,
            project_id=record.project_id,
            kind="block.episode.assemble",
            handler="block.episode.assemble",
            resource=ResourceClass.IO,
            priority=55,
            dependencies=timeline_ids,
            payload={
                "episode_id": record.episode_id,
                "output_path": record.output_path,
                "shots": assembly_shots,
                "continuation_recovery": True,
            },
            max_attempts=2,
        )
        self.turbo_store.enqueue_work(assembly)
        record.timeline_work_ids = timeline_ids
        record.assembly_work_id = assembly_id
        record.post_enqueued = True
        return self.store.save(record)

    def accept_requeued_render(
        self,
        *,
        continuation_id: str,
        shot_id: str,
        render_work_id: str,
        path: str,
        method_id: str | None,
    ) -> ContinuationResumeResult:
        record = self.store.get(continuation_id)
        shot = next(
            item
            for item in record.shots
            if item.shot_id == shot_id
        )
        shot.state = ContinuationShotState.ACCEPTED
        shot.render_work_id = render_work_id
        shot.path = path
        shot.method_id = method_id
        self.store.save(record)
        record = self._enqueue_post(record)
        return ContinuationResumeResult(
            continuation_id=continuation_id,
            shot_id=shot_id,
            accepted=True,
            all_accepted=record.all_accepted,
            post_enqueued=record.post_enqueued,
            timeline_work_ids=list(
                record.timeline_work_ids
            ),
            assembly_work_id=record.assembly_work_id,
        )
