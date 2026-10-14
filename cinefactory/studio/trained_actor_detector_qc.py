from __future__ import annotations
"""Independent target-frame YOLO inference + held-out Blender rig label QC.

Detector sees target pixels ONLY; evaluator reads rig target labels AFTER the
boxes have been frozen. Same-scene synthetic-training provenance means no
general detector certification. Licence must be checked before commercial use.
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from pydantic import BaseModel, Field

from cinefactory.studio.temporal_reid import TemporalReIDEngine


class TrainedDetectorEvaluation(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    general_out_of_domain_actor_detection_verified: bool = False
    target_actor_labels_used_for_inference: bool = False
    source_training_labels_from_blender: bool = True
    target_ground_truth: str = "BLENDER_RIG_LABELS_EVALUATION_ONLY"
    model_sha256: str
    video_sha256: str
    model_kind: str
    frames: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    mean_match_iou: float | None = None
    blockers: list[str] = Field(default_factory=list)
    license_notice: str = "REVIEW_ULTRALYTICS_AGPL_AND_WEIGHTS_TERMS_BEFORE_COMMERCIAL_USE"


class HeldoutActorDetectorEvaluator:
    def __init__(
        self,*,sample_count:int=10,confidence:float=.20,
        iou_floor:float=.50,precision_floor:float=.85,
        recall_floor:float=.85,
    ):
        self.sample_count=sample_count
        self.confidence=confidence
        self.iou_floor=iou_floor
        self.precision_floor=precision_floor
        self.recall_floor=recall_floor

    def evaluate(
        self,*,weights:str|Path,target_video:str|Path,
        target_annotations:str|Path,model_kind:str,
        person_only:bool=False,
    )->TrainedDetectorEvaluation:
        import ultralytics
        weights=Path(weights).resolve()
        media=Path(target_video).resolve()
        annotations=Path(target_annotations).resolve()
        if not (weights.is_file() and media.is_file() and annotations.is_file()):
            raise ValueError("MODEL_VIDEO_OR_TARGET_GROUND_TRUTH_MISSING")
        from ultralytics import YOLO
        gt=json.loads(annotations.read_text(encoding="utf-8"))
        bboxes=gt.get("actors",{})
        if len(bboxes)<2:
            raise ValueError("GROUND_TRUTH_ACTORS_INSUFFICIENT")
        # Rig-box labels only enter the evaluator and are never passed to model.
        cap=cv2.VideoCapture(str(media))
        tp=fp=fn=0
        ious=[]
        frame_total=0
        try:
            count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if count<4:
                raise ValueError("TARGET_VIDEO_TOO_SHORT")
            model=YOLO(str(weights))
            for idx in sorted({int(round(n)) for n in np.linspace(
                0,count-1,min(count,self.sample_count)
            )}):
                cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
                ok,frame=cap.read()
                if not ok:
                    raise RuntimeError("YOLO_TEST_VIDEO_DECODE_FAILED")
                h,w=frame.shape[:2]
                predictions=model.predict(
                    frame,device="cpu",verbose=False,imgsz=320,
                    conf=self.confidence,
                )[0]
                output=[]
                for cls,c,box in zip(
                    predictions.boxes.cls,predictions.boxes.conf,
                    predictions.boxes.xyxy
                ):
                    if person_only and int(cls)!=0:
                        continue
                    x0,y0,x1,y1=(float(z) for z in box)
                    if x1<=x0 or y1<=y0:
                        continue
                    output.append({
                        "x0":max(0.,x0/w),"y0":max(0.,y0/h),
                        "x1":min(1.,x1/w),"y1":min(1.,y1/h)
                    })
                # Ground truth Blender sidecar uses bottom-left coordinates.
                truth=[{
                    "x0":a["screen_box"]["x0"],
                    "x1":a["screen_box"]["x1"],
                    "y0":1-a["screen_box"]["y1"],
                    "y1":1-a["screen_box"]["y0"],
                } for a in bboxes.values()]
                pairs=[]
                for ai,x in enumerate(output):
                    for bi,y in enumerate(truth):
                        score=TemporalReIDEngine.iou(x,y)
                        if score>=self.iou_floor:
                            pairs.append((score,ai,bi))
                used_a=set()
                used_b=set()
                for score,ai,bi in sorted(pairs,reverse=True):
                    if ai in used_a or bi in used_b:continue
                    used_a.add(ai);used_b.add(bi)
                    ious.append(score)
                tp+=len(used_a)
                fp+=len(output)-len(used_a)
                fn+=len(truth)-len(used_b)
                frame_total+=1
        finally:cap.release()
        prec=tp/(tp+fp) if tp+fp else 0.
        rec=tp/(tp+fn) if tp+fn else 0.
        blockers=[]
        if frame_total<4:
            blockers.append("INSUFFICIENT_HELDOUT_FRAMES")
        if prec<self.precision_floor:
            blockers.append("TRAINED_ACTOR_PRECISION_BELOW_FLOOR")
        if rec<self.recall_floor:
            blockers.append("TRAINED_ACTOR_RECALL_BELOW_FLOOR")
        return TrainedDetectorEvaluation(
            status="HELDOUT_SAME_SCENE_DETECTOR_PASS" if not blockers else "BLOCKED",
            passed=not blockers,measured=frame_total>=4,
            model_sha256=hashlib.sha256(weights.read_bytes()).hexdigest(),
            video_sha256=hashlib.sha256(media.read_bytes()).hexdigest(),
            model_kind=model_kind,frames=frame_total,
            true_positives=tp,false_positives=fp,false_negatives=fn,
            precision=prec,recall=rec,
            mean_match_iou=float(np.mean(ious)) if ious else None,
            blockers=blockers,
        )
