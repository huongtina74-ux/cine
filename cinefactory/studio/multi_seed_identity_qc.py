from __future__ import annotations

"""Bounded multi-seed identity stress bench with auditable per-seed veto.

Synthetic frame generation is deterministic per seed; the benchmarks are NOT
evidence of generalizable re-identification in rendered or real footage.
"""
from hashlib import sha256
from pathlib import Path

import cv2
import numpy as np
from pydantic import BaseModel, Field

from cinefactory.studio.independent_actor_detection import (
    ActorGroundTruth, DetectionBenchmarkReport,
    IndependentColorActorDetector,
)
from cinefactory.studio.temporal_reid import (
    TemporalFrame, TemporalReIDEngine, TemporalReIDReport,
)


class SeedScenarioReport(BaseModel):
    seed: int
    frame_count: int
    frame_fingerprints: list[str]
    detection: DetectionBenchmarkReport
    identity: TemporalReIDReport
    passed: bool
    blockers: list[str] = Field(default_factory=list)


class MultiSeedIdentityReport(BaseModel):
    status: str
    passed: bool
    production_qualified: bool = False
    seed_count: int
    scenarios: list[SeedScenarioReport]
    worst_precision: float | None = None
    worst_recall: float | None = None
    blockers: list[str] = Field(default_factory=list)


class MultiSeedIdentityLab:
    def __init__(
        self, detector: IndependentColorActorDetector,
        *, minimum_seeds: int=3,
    ) -> None:
        self.detector=detector
        self.minimum_seeds=minimum_seeds

    @staticmethod
    def synthetic_frames(
        seed: int, *, corrupt: bool=False,
        frame_count: int=12,
    ) -> tuple[list[tuple[float,np.ndarray]],list[ActorGroundTruth]]:
        rng=np.random.default_rng(seed)
        samples=[]
        annotations=[]
        width,height=320,180
        shift=int(rng.integers(-6,7))
        # Use fixed large color patches and vary position & lighting/noise
        # while retaining exact ground-truth boxes per seed/frame.
        for frame_index in range(frame_count):
            time=frame_index/12
            frame=np.full((height,width,3),(207,204,201),dtype=np.uint8)
            jitter=rng.integers(-6,7,size=(height,width,1),dtype=np.int16)
            frame=np.uint8(np.clip(frame.astype(np.int16)+jitter,0,255))
            left=30+shift+9*frame_index
            right=246+shift-9*frame_index
            visible_b=frame_index not in (5,6)
            color_a=(230,40,45)
            color_b=(40,80,230)
            cv2.rectangle(frame,(left,49),(left+37,120),color_a,-1)
            if visible_b:
                cv2.rectangle(frame,(right,49),(right+37,120),color_b,-1)
            if corrupt:
                # An impostor with identical color must be counted as FP.
                cv2.rectangle(frame,(140,128),(190,171),color_a,-1)
            for actor,x,visible in (("A",left,True),("B",right,visible_b)):
                annotations.append(ActorGroundTruth(
                    actor_id=actor,time_seconds=time,visible=visible,
                    screen_box={
                        "x0":x/width,"y0":49/height,
                        "x1":(x+38)/width,"y1":121/height,
                    },
                ))
            samples.append((time,frame))
        return samples,annotations

    def evaluate(
        self, *, seeds: list[int], corrupted_seeds: set[int] | None=None,
    ) -> MultiSeedIdentityReport:
        blockers=[]
        if len(seeds)<self.minimum_seeds or len(set(seeds))!=len(seeds):
            blockers.append("MULTISEED_SEED_SET_INSUFFICIENT_OR_DUPLICATE")
        corrupt=corrupted_seeds or set()
        reports=[]
        for seed in seeds:
            frames,annotations=self.synthetic_frames(
                seed,corrupt=seed in corrupt
            )
            detect=self.detector.benchmark(
                frames=frames,ground_truth=annotations,
            )
            temporal=TemporalReIDEngine().assess(
                actor_ids=["A","B"],
                frames=[TemporalFrame(
                    time_seconds=second,
                    detections=self.detector.detect(img),
                ) for second,img in frames],
            )
            findings=[]
            if not detect.passed:
                findings.append("SEED_DETECTOR_BENCHMARK_FAILED")
            if not temporal.passed:
                findings.append("SEED_TEMPORAL_ASSOCIATION_FAILED")
            fingerprint=[
                sha256(frame.tobytes()).hexdigest() for _,frame in frames
            ]
            reports.append(SeedScenarioReport(
                seed=seed,frame_count=len(frames),
                frame_fingerprints=fingerprint,
                detection=detect,identity=temporal,
                passed=not findings,blockers=findings,
            ))
            blockers.extend(f"SEED_{seed}:{finding}" for finding in findings)
        return MultiSeedIdentityReport(
            status="CONTROLLED_MULTI_SEED_PASS" if not blockers else "BLOCKED",
            passed=not blockers,
            seed_count=len(seeds),scenarios=reports,
            worst_precision=min((x.detection.precision for x in reports),default=None),
            worst_recall=min((x.detection.recall for x in reports),default=None),
            blockers=sorted(set(blockers)),
        )
