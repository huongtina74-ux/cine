from __future__ import annotations

"""Full-frame color-signature detector for controlled block-animation scenes.

Locates actors without prior/seeded screen boxes. It is an intentionally narrow
baseline (flat-color controlled renders), not a semantic or general-purpose
detector. Benchmark provenance and coverage decide if it can be trusted.
"""
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from pydantic import BaseModel, Field, model_validator

from cinefactory.studio.temporal_reid import (
    ActorDetection, DetectionOrigin, TemporalFrame, TemporalReIDEngine,
)


class ColorSignature(BaseModel):
    actor_id: str
    rgb: tuple[int,int,int]
    tolerance: int = Field(default=24,ge=1,le=110)
    minimum_area_fraction: float = Field(default=.006,gt=0,lt=.4)

    @model_validator(mode="after")
    def valid(self):
        if any(x<0 or x>255 for x in self.rgb):
            raise ValueError("RGB_OUT_OF_RANGE")
        return self


class ActorGroundTruth(BaseModel):
    actor_id: str
    time_seconds: float = Field(ge=0)
    screen_box: dict[str,float]
    visible: bool = True


class DetectionBenchmarkReport(BaseModel):
    status: str
    passed: bool
    production_qualified: bool = False
    sample_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    matched_iou_mean: float | None = None
    blockers: list[str] = Field(default_factory=list)
    scenario: str = "CONTROLLED_FLAT_COLOR"
    limitation: str = "COLOR_SIGNATURE_BASELINE_ONLY"


class IndependentColorActorDetector:
    def __init__(self, signatures: list[ColorSignature]):
        if not signatures or len({s.actor_id for s in signatures})!=len(signatures):
            raise ValueError("UNIQUE_COLOR_SIGNATURE_REQUIRED")
        colors=np.asarray([s.rgb for s in signatures],dtype=float)
        for i in range(len(colors)):
            for j in range(i+1,len(colors)):
                sep=float(np.linalg.norm(colors[i]-colors[j]))
                if sep<=max(signatures[i].tolerance,signatures[j].tolerance)*1.8:
                    raise ValueError("COLOR_SIGNATURES_NOT_SEPARABLE")
        self.signatures=signatures

    def detect(self, rgb: np.ndarray) -> list[ActorDetection]:
        if rgb.ndim!=3 or rgb.shape[2]!=3 or rgb.dtype!=np.uint8:
            raise ValueError("RGB_U8_IMAGE_REQUIRED")
        h,w=rgb.shape[:2]
        result: list[ActorDetection]=[]
        arr=rgb.astype(np.int16)
        for sig in self.signatures:
            ref=np.asarray(sig.rgb,dtype=np.int16)
            # RGB distance is actor-specific, not a location proposal from crop.
            dist=np.linalg.norm(arr-ref,axis=2)
            binary=np.asarray(dist<=sig.tolerance,dtype=np.uint8)
            n, labels, stats, _=cv2.connectedComponentsWithStats(
                binary,connectivity=8,
            )
            candidates=[]
            for label in range(1,n):
                x,y,bw,bh,area=(int(x) for x in stats[label])
                if area/(w*h)<sig.minimum_area_fraction:
                    continue
                box={"x0":x/w,"y0":y/h,"x1":(x+bw)/w,"y1":(y+bh)/h}
                candidates.append((area,box))
            for rank,(area,box) in enumerate(
                sorted(candidates,key=lambda item:item[0],reverse=True)
            ):
                score=float(np.clip(.82+.16*area/(h*w*.12),0.,.99))
                scores={
                    s.actor_id:score if s.actor_id==sig.actor_id else .05
                    for s in self.signatures
                }
                result.append(ActorDetection(
                    detection_id=f"{sig.actor_id}_color_{rank}",
                    screen_box=box,appearance_scores=scores,
                    origin=DetectionOrigin.INDEPENDENT,
                ))
        return result

    def benchmark(
        self, *, frames: list[tuple[float,np.ndarray]],
        ground_truth: list[ActorGroundTruth],
        iou_floor: float=.50,precision_floor: float=.95,
        recall_floor: float=.95,
    ) -> DetectionBenchmarkReport:
        truth_by_time: dict[float,list[ActorGroundTruth]]={}
        for row in ground_truth:
            truth_by_time.setdefault(round(row.time_seconds,6),[]).append(row)
        tp=fp=fn=0
        ious: list[float]=[]
        blockers=[]
        if len(frames)<4:
            blockers.append("BENCHMARK_TOO_FEW_FRAMES")
        if not ground_truth:
            blockers.append("GROUND_TRUTH_MISSING")
        for time,frame in frames:
            found=self.detect(frame)
            gt=truth_by_time.get(round(time,6),[])
            if not gt:
                blockers.append(f"GROUND_TRUTH_FRAME_UNLABELED:{time}")
            used: set[int]=set()
            for target in gt:
                if not target.visible:
                    continue
                options=[
                    (TemporalReIDEngine.iou(d.screen_box,target.screen_box),i)
                    for i,d in enumerate(found)
                    if i not in used and
                    max(d.appearance_scores,key=d.appearance_scores.get)==target.actor_id
                ]
                best=max(options,default=(0.,-1))
                if best[0]>=iou_floor:
                    tp+=1
                    used.add(best[1])
                    ious.append(best[0])
                else:
                    fn+=1
            fp+=len(found)-len(used)
        prec=tp/(tp+fp) if tp+fp else 0.
        rec=tp/(tp+fn) if tp+fn else 0.
        if prec<precision_floor:
            blockers.append("DETECTOR_PRECISION_BELOW_FLOOR")
        if rec<recall_floor:
            blockers.append("DETECTOR_RECALL_BELOW_FLOOR")
        passed=not blockers
        return DetectionBenchmarkReport(
            status="CONTROLLED_BENCHMARK_PASS" if passed else "FAIL",
            passed=passed,sample_count=len(frames),
            true_positives=tp,false_positives=fp,false_negatives=fn,
            precision=prec,recall=rec,
            matched_iou_mean=sum(ious)/len(ious) if ious else None,
            blockers=sorted(set(blockers)),
        )

    def video_frames(
        self, *, video_path: Path | str, sample_count: int=12,
    ) -> list[tuple[float,np.ndarray]]:
        cap=cv2.VideoCapture(str(Path(video_path).resolve()))
        try:
            n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps=float(cap.get(cv2.CAP_PROP_FPS))
            if n<1 or fps<=0:
                raise ValueError("VIDEO_DECODE_OR_FPS_INVALID")
            count=min(n,max(4,sample_count))
            indices=sorted({
                round(i*(n-1)/(count-1)) for i in range(count)
            })
            frames=[]
            for i in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES,i)
                ok,bgr=cap.read()
                if not ok:
                    raise RuntimeError("INDEPENDENT_FRAME_DECODE_FAILED")
                frames.append((
                    i/fps,cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                ))
            return frames
        finally:
            cap.release()


class IndependentActorDetectionLab:
    """Explicit signature-scoped detector factory for controlled scenes."""

    def build(self, signatures: list[ColorSignature]) -> IndependentColorActorDetector:
        return IndependentColorActorDetector(signatures)

    def multiseed(self, signatures: list[ColorSignature]):
        from cinefactory.studio.multi_seed_identity_qc import MultiSeedIdentityLab
        return MultiSeedIdentityLab(self.build(signatures))
