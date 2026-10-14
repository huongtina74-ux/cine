from __future__ import annotations

"""v1.6.23 sampled multi-actor temporal association.

Independent detections can support a stronger gate. Reference-seeded crop searches
are diagnostic evidence only: they cannot demonstrate reacquisition after occlusion.
"""
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator


class DetectionOrigin(StrEnum):
    INDEPENDENT = "INDEPENDENT"
    REFERENCE_SEEDED = "REFERENCE_SEEDED"
    HUMAN_ANNOTATED = "HUMAN_ANNOTATED"


class ActorDetection(BaseModel):
    detection_id: str
    screen_box: dict[str, float]
    appearance_scores: dict[str, float]
    origin: DetectionOrigin

    @model_validator(mode="after")
    def bounded(self):
        b = self.screen_box
        if not all(k in b for k in ("x0", "x1", "y0", "y1")):
            raise ValueError("detection must have an XYXY screen_box")
        if not (0 <= b["x0"] < b["x1"] <= 1 and 0 <= b["y0"] < b["y1"] <= 1):
            raise ValueError("detection screen_box is out of range")
        if not self.appearance_scores or any(
            not 0 <= score <= 1 for score in self.appearance_scores.values()
        ):
            raise ValueError("appearance scores must be in [0,1]")
        return self


class TemporalFrame(BaseModel):
    time_seconds: float = Field(ge=0)
    detections: list[ActorDetection] = Field(default_factory=list)
    scene_cut: bool = False


class TemporalActorTrack(BaseModel):
    actor_id: str
    matched_frames: int = 0
    missing_frames: int = 0
    minimum_score: float | None = None
    observed_boxes: list[dict[str, Any]] = Field(default_factory=list)
    reacquisitions: int = 0
    reference_window_resumptions: int = 0


class TemporalReIDReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    evidence_type: str
    frame_count: int
    identity_floor: float
    tracks: list[TemporalActorTrack] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TemporalReIDEngine:
    def __init__(
        self, *, identity_floor: float = 0.70,
        cross_identity_margin: float = 0.08,
        minimum_coverage: float = 0.80,
        maximum_consecutive_missing: int = 2,
    ) -> None:
        self.identity_floor = identity_floor
        self.cross_identity_margin = cross_identity_margin
        self.minimum_coverage = minimum_coverage
        self.maximum_consecutive_missing = maximum_consecutive_missing

    @staticmethod
    def iou(a: dict[str, float], b: dict[str, float]) -> float:
        x0, y0 = max(a["x0"], b["x0"]), max(a["y0"], b["y0"])
        x1, y1 = min(a["x1"], b["x1"]), min(a["y1"], b["y1"])
        inter = max(0., x1-x0) * max(0., y1-y0)
        area = lambda z: (z["x1"]-z["x0"]) * (z["y1"]-z["y0"])
        union = area(a) + area(b) - inter
        return inter / union if union > 0 else 0.

    def assess(self, *, actor_ids: list[str], frames: list[TemporalFrame]) -> TemporalReIDReport:
        blockers: list[str] = []
        warnings: list[str] = []
        if not actor_ids or len(set(actor_ids)) != len(actor_ids):
            blockers.append("INVALID_ACTOR_SET")
        if len(frames) < 4:
            blockers.append("TEMPORAL_EVIDENCE_TOO_SPARSE")
        for prev, current in zip(frames, frames[1:]):
            if current.time_seconds <= prev.time_seconds:
                blockers.append("NON_MONOTONIC_TIMESTAMPS")
                break
        origins = {d.origin for f in frames for d in f.detections}
        evidence_type = (
            "INDEPENDENT_DETECTIONS"
            if origins == {DetectionOrigin.INDEPENDENT} else
            "REFERENCE_SEEDED_OR_MIXED"
        )
        tracks = {aid: TemporalActorTrack(actor_id=aid) for aid in actor_ids}
        misses = {aid: 0 for aid in actor_ids}
        prior_boxes: dict[str, dict[str, float]] = {}
        prior_times: dict[str, float] = {}
        for f in frames:
            ids = [d.detection_id for d in f.detections]
            if len(set(ids)) != len(ids):
                blockers.append(f"DUPLICATE_DETECTION_ID:{f.time_seconds:.3f}")
            valid: dict[str, list[tuple[float, ActorDetection]]] = {}
            for actor in actor_ids:
                candidates: list[tuple[float, ActorDetection]] = []
                for detection in f.detections:
                    own = detection.appearance_scores.get(actor, 0.)
                    rivals = [
                        detection.appearance_scores.get(other, 0.)
                        for other in actor_ids if other != actor
                    ]
                    competing = max(rivals, default=0.)
                    if own < self.identity_floor:
                        continue
                    if own - competing < self.cross_identity_margin:
                        if competing > own:
                            code = (
                                "REFERENCE_SEEDED_CROSS_IDENTITY_CONFUSION"
                                if detection.origin != DetectionOrigin.INDEPENDENT
                                else "IDENTITY_SWAP_OR_MISMATCH"
                            )
                            blockers.append(f"{code}:{actor}:{f.time_seconds:.3f}")
                        else:
                            warnings.append(
                                f"AMBIGUOUS_IDENTITY:{actor}:{f.time_seconds:.3f}"
                            )
                        continue
                    if actor in prior_boxes and not f.scene_cut:
                        gap = f.time_seconds - prior_times[actor]
                        if gap <= 1.5:
                            prev = prior_boxes[actor]
                            now = detection.screen_box
                            cx = (prev["x0"] + prev["x1"])/2.
                            cy = (prev["y0"] + prev["y1"])/2.
                            nx = (now["x0"] + now["x1"])/2.
                            ny = (now["y0"] + now["y1"])/2.
                            if ((nx-cx)**2+(ny-cy)**2)**.5 > 0.30 + 0.15*gap:
                                warnings.append(
                                    f"TRACK_POSITION_JUMP:{actor}:{f.time_seconds:.3f}"
                                )
                                continue
                    candidates.append((own, detection))
                valid[actor] = sorted(candidates, key=lambda item: item[0], reverse=True)
            assignments: dict[str, ActorDetection] = {}
            used: set[str] = set()
            # Assign confident actors first, avoiding duplicate use of one detection.
            for actor in sorted(actor_ids, key=lambda a: valid[a][0][0] if valid[a] else -1, reverse=True):
                for score, detection in valid[actor]:
                    if detection.detection_id not in used:
                        assignments[actor] = detection
                        used.add(detection.detection_id)
                        break
            for actor in actor_ids:
                track = tracks[actor]
                chosen = assignments.get(actor)
                if chosen is None:
                    track.missing_frames += 1
                    misses[actor] += 1
                    if misses[actor] > self.maximum_consecutive_missing:
                        blockers.append(f"TRACK_OCCLUSION_LIMIT:{actor}")
                    continue
                for other, other_detection in assignments.items():
                    if other != actor and self.iou(
                        chosen.screen_box, other_detection.screen_box
                    ) >= .70:
                        blockers.append(
                            f"ACTOR_REGION_COLLISION:{actor}:{other}:{f.time_seconds:.3f}"
                        )
                if misses[actor] > 0:
                    if chosen.origin == DetectionOrigin.INDEPENDENT:
                        track.reacquisitions += 1
                    else:
                        track.reference_window_resumptions += 1
                misses[actor] = 0
                score = chosen.appearance_scores[actor]
                track.matched_frames += 1
                track.minimum_score = min(
                    track.minimum_score if track.minimum_score is not None else score,
                    score,
                )
                track.observed_boxes.append({
                    "time_seconds": f.time_seconds, "score": score,
                    "screen_box": chosen.screen_box,
                    "origin": chosen.origin.value,
                })
                prior_boxes[actor] = chosen.screen_box
                prior_times[actor] = f.time_seconds
        for actor, track in tracks.items():
            coverage = track.matched_frames / len(frames) if frames else 0.
            if coverage < self.minimum_coverage:
                blockers.append(f"ACTOR_TRACK_COVERAGE_LOW:{actor}:{coverage:.3f}")
            if not track.matched_frames:
                blockers.append(f"ACTOR_TRACK_NEVER_FOUND:{actor}")
        blockers = sorted(set(blockers))
        warnings = sorted(set(warnings))
        # A reference-seeded search can reveal drift, not prove independent re-identification.
        eligible = evidence_type == "INDEPENDENT_DETECTIONS"
        passed = bool(not blockers and frames and tracks and eligible)
        status = "FAIL" if blockers else ("PASS" if passed else "REVIEW_REQUIRED")
        if not eligible:
            warnings.append("INDEPENDENT_ACTOR_DETECTION_NOT_QUALIFIED")
        return TemporalReIDReport(
            status=status, passed=passed, measured=bool(frames),
            production_qualified=False, evidence_type=evidence_type,
            frame_count=len(frames), identity_floor=self.identity_floor,
            tracks=list(tracks.values()),
            blockers=blockers, warnings=sorted(set(warnings)),
        )

    def assess_reference_seeded_video(
        self, *, factory: Any, actor_reference_ids: dict[str,str],
        global_character_ids: dict[str,str], video_path: str | Path,
        max_samples: int = 12,
    ) -> TemporalReIDReport:
        """Bounded actual video probe; never marks independent Re-ID qualified."""
        import cv2
        from PIL import Image
        video = Path(video_path).resolve()
        expected = set(actor_reference_ids) | set(global_character_ids)
        if not expected or any(
            not actor_reference_ids.get(a) or not global_character_ids.get(a)
            for a in expected
        ):
            return TemporalReIDReport(
                status="FAIL", passed=False, measured=False,
                evidence_type="REFERENCE_SEEDED_OR_MIXED",
                frame_count=0, identity_floor=self.identity_floor,
                blockers=["TEMPORAL_REFERENCE_BINDINGS_INCOMPLETE"],
            )
        try:
            packs = {
                actor: factory.store.get_reference(
                    global_character_ids[actor], actor_reference_ids[actor]
                ) for actor in sorted(expected)
            }
        except KeyError:
            return TemporalReIDReport(
                status="FAIL", passed=False, measured=False,
                evidence_type="REFERENCE_SEEDED_OR_MIXED",
                frame_count=0, identity_floor=self.identity_floor,
                blockers=["TEMPORAL_REFERENCE_PACK_MISSING"],
            )
        video_capture = cv2.VideoCapture(str(video))
        frames: list[TemporalFrame] = []
        try:
            count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(video_capture.get(cv2.CAP_PROP_FPS))
            if count < 4 or fps <= 0:
                return self.assess(actor_ids=sorted(expected),frames=[])
            steps = min(max(4, max_samples), count)
            frame_ids = sorted({
                round(index * (count - 1) / (steps - 1))
                for index in range(steps)
            })
            boxes = {a: dict(p.screen_box) for a,p in packs.items()}
            for frame_id in frame_ids:
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
                ok, bgr = video_capture.read()
                if not ok:
                    frames.append(TemporalFrame(time_seconds=frame_id/fps))
                    continue
                rgb = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
                detections: list[ActorDetection] = []
                for actor, pack in packs.items():
                    evidence, score = factory._track_sample(
                        image=rgb, actor_id=actor, pack=pack,
                        base_box=boxes[actor],
                    )
                    if evidence is None or score is None:
                        continue
                    boxes[actor] = dict(evidence.screen_box)
                    comparisons = {
                        key: factory.evaluator.compare_actor(
                            other_pack.evidence, evidence
                        ).score or 0.0
                        for key, other_pack in packs.items()
                    }
                    detections.append(ActorDetection(
                        detection_id=f"{actor}@{frame_id}",
                        screen_box=dict(evidence.screen_box),
                        appearance_scores=comparisons,
                        origin=DetectionOrigin.REFERENCE_SEEDED,
                    ))
                frames.append(TemporalFrame(
                    time_seconds=frame_id/fps,detections=detections,
                ))
        finally:
            video_capture.release()
        return self.assess(actor_ids=sorted(expected), frames=frames)
