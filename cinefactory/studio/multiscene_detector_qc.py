from __future__ import annotations
"""Validation-calibrated YOLO held-out PNG evaluation (never train on TEST).

Image-only inference first; pixel-mask-derived ground truth labels loaded
AFTER YOLO returns boxes. Holdout has disjoint scene seeds/palettes; still
belongs to the same procedural Blender generator, NOT human video domain.
"""
import hashlib
from pathlib import Path

import cv2
import numpy as np
from pydantic import BaseModel, Field


class SplitDetectionResult(BaseModel):
    split: str
    images: int
    total_ground_truth: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float
    mean_match_iou: float | None
    confidence: float


class MultiSceneDetectorReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    generalized_real_video_detection_qualified: bool = False
    trained_scene_family: str = "PROCEDURAL_BLENDER_VOXEL_BLOCK_RIG"
    target_ground_truth_source: str = "HELDOUT_PIXEL_RENDERED_ACTOR_MASKS"
    inference_used_target_boxes: bool = False
    model_sha256: str
    dataset_manifest_sha256: str
    validation_sweep: list[SplitDetectionResult] = Field(default_factory=list)
    chosen_confidence: float
    selection_rule: str = "VALIDATION_ONLY_MAX_F1_WITH_PRECISION_FLOOR_0_80"
    heldout_test: SplitDetectionResult
    original_cinefactory_video: dict | None = None
    blockers: list[str] = Field(default_factory=list)


class MultiSceneDetectorEvaluator:
    VALIDATION_THRESHOLDS=(.10,.20,.30,.40,.50)

    def __init__(self,*,iou_floor:float=.50,precision_floor:float=.80,
                 recall_floor:float=.80):
        self.iou_floor=iou_floor
        self.precision_floor=precision_floor
        self.recall_floor=recall_floor

    @staticmethod
    def _iou(a:dict,b:dict)->float:
        w=max(0.,min(a["x1"],b["x1"])-max(a["x0"],b["x0"]))
        h=max(0.,min(a["y1"],b["y1"])-max(a["y0"],b["y0"]))
        area=lambda r:max(0.,r["x1"]-r["x0"])*max(0.,r["y1"]-r["y0"])
        den=area(a)+area(b)-w*h
        return float(w*h/den) if den>0 else 0.

    def evaluate_split(self,*,model,dataset_dir:Path,split:str,
                       thresholds:tuple[float,...])->list[SplitDetectionResult]:
        if split not in ("val","test"):
            raise ValueError("NON_HELDOUT_SPLIT_EVALUATION_FORBIDDEN")
        images=sorted((dataset_dir/"images"/split).glob("*.png"))
        if len(images)<3:
            raise ValueError("DATASET_EVALUATION_SAMPLE_COUNT_LOW")
        counters={c:{"tp":0,"fp":0,"fn":0,"iou":[]} for c in thresholds}
        total_truth=0
        for img in images:
            pixels=cv2.imread(str(img),cv2.IMREAD_COLOR)
            if pixels is None:
                raise RuntimeError("HELDOUT_IMAGE_UNREADABLE")
            h,w=pixels.shape[:2]
            # Inference gets only RGB. Heldout label file is loaded AFTER.
            raw=model.predict(pixels,device="cpu",verbose=False,
                              imgsz=384,conf=min(thresholds))[0]
            guesses=[]
            for cls,score,rect in zip(raw.boxes.cls,raw.boxes.conf,raw.boxes.xyxy):
                if int(cls)!=0:continue
                x0,y0,x1,y1=(float(x) for x in rect)
                guesses.append((float(score),{
                    "x0":x0/w,"y0":y0/h,"x1":x1/w,"y1":y1/h,
                }))
            label_path=dataset_dir/"labels"/split/(img.stem+".txt")
            lines=label_path.read_text(encoding="utf-8").strip().splitlines()
            truth=[]
            for line in lines:
                cls,cx,cy,bw,bh=(float(x) for x in line.split())
                if cls!=0 or min(bw,bh)<=0:raise ValueError("BAD_HELDOUT_LABEL")
                truth.append({
                    "x0":cx-bw/2,"y0":cy-bh/2,"x1":cx+bw/2,"y1":cy+bh/2,
                })
            total_truth+=len(truth)
            for threshold in thresholds:
                predicted=[b for score,b in guesses if score>=threshold]
                matches=[]
                for i,proposed in enumerate(predicted):
                    for j,actual in enumerate(truth):
                        v=self._iou(proposed,actual)
                        if v>=self.iou_floor:matches.append((v,i,j))
                matched_pred=set()
                matched_true=set()
                for value,pi,ti in sorted(matches,reverse=True):
                    if pi in matched_pred or ti in matched_true:continue
                    matched_pred.add(pi);matched_true.add(ti)
                    counters[threshold]["iou"].append(value)
                counters[threshold]["tp"]+=len(matched_pred)
                counters[threshold]["fp"]+=len(predicted)-len(matched_pred)
                counters[threshold]["fn"]+=len(truth)-len(matched_true)
        output=[]
        for threshold in thresholds:
            x=counters[threshold]
            precision=x["tp"]/(x["tp"]+x["fp"]) if x["tp"]+x["fp"] else 0.
            recall=x["tp"]/(x["tp"]+x["fn"]) if x["tp"]+x["fn"] else 0.
            f1=2*precision*recall/(precision+recall) if precision+recall else 0.
            output.append(SplitDetectionResult(
                split=split,images=len(images),total_ground_truth=total_truth,
                true_positives=x["tp"],false_positives=x["fp"],
                false_negatives=x["fn"],precision=precision,recall=recall,
                f1=f1,mean_match_iou=float(np.mean(x["iou"])) if x["iou"] else None,
                confidence=threshold,
            ))
        return output

    def evaluate(self,*,checkpoint:str|Path,dataset_dir:str|Path,
                 dataset_manifest_sha256:str)->MultiSceneDetectorReport:
        from ultralytics import YOLO
        model_file=Path(checkpoint).resolve()
        dataset=Path(dataset_dir).resolve()
        if not model_file.is_file():
            raise ValueError("DETECTOR_CHECKPOINT_MISSING")
        model=YOLO(str(model_file))
        sweep=self.evaluate_split(model=model,dataset_dir=dataset,split="val",
                                  thresholds=self.VALIDATION_THRESHOLDS)
        viable=[x for x in sweep if x.precision>=self.precision_floor]
        if viable:
            # Deterministic max F1, then precision, then higher threshold.
            chosen=max(viable,key=lambda x:(x.f1,x.precision,x.confidence))
            calibration_ok=True
        else:
            chosen=max(sweep,key=lambda x:(x.f1,x.precision,x.confidence))
            calibration_ok=False
        # Test labels are read exactly once under a VALIDATION-CHOSEN threshold.
        test=self.evaluate_split(model=model,dataset_dir=dataset,split="test",
                                 thresholds=(chosen.confidence,))[0]
        blockers=[]
        if not calibration_ok:
            blockers.append("VALIDATION_PRECISION_NEVER_REACHED_FLOOR")
        if test.precision<self.precision_floor:
            blockers.append("UNSEEN_SCENE_TEST_PRECISION_BELOW_FLOOR")
        if test.recall<self.recall_floor:
            blockers.append("UNSEEN_SCENE_TEST_RECALL_BELOW_FLOOR")
        return MultiSceneDetectorReport(
            status="HELDOUT_PROCEDURAL_SCENE_QC_PASS" if not blockers else "BLOCKED",
            passed=not blockers,measured=True,
            model_sha256=hashlib.sha256(model_file.read_bytes()).hexdigest(),
            dataset_manifest_sha256=dataset_manifest_sha256,
            validation_sweep=sweep,chosen_confidence=chosen.confidence,
            heldout_test=test,blockers=blockers,
        )
