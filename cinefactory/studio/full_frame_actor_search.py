from __future__ import annotations
"""Full-frame visual-reference actor search on real rendered MP4 frames.

An *approved annotated reference crop* from first shot supplies appearance
templates, not target screen position. Search of subsequent shot uses entire
image. Ground truth from the second Blender shot is evaluation ONLY.
Constrained camera/style/rig domain: not a general actor detector or real-Wan
multi-seed certification.
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from pydantic import BaseModel, Field

from cinefactory.studio.temporal_reid import (
    ActorDetection, DetectionOrigin, TemporalFrame, TemporalReIDEngine,
    TemporalReIDReport,
)


class FullFrameTemplate(BaseModel):
    actor_id: str
    origin: str = "FIRST_SHOT_RIG_ANNOTATED_REFERENCE"
    template_gray: np.ndarray | None = Field(default=None,exclude=True)
    source_video_sha256: str
    template_image_sha256: str
    width: int = Field(ge=16)
    height: int = Field(ge=16)

    model_config={"arbitrary_types_allowed":True}


class FullFrameDetectionRow(BaseModel):
    actor_id: str
    time_seconds: float
    screen_box: dict[str,float] | None = None
    template_score: float
    secondary_score: float
    secondary_margin: float
    matched: bool = False
    blockers: list[str] = Field(default_factory=list)


class TargetShotSearchReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    source_reference_kind: str = "RIG_APPROVED_FIRST_SHOT_TEMPLATE"
    target_location_source: str = "WHOLE_FRAME_CV_TEMPLATE_MATCH"
    target_rig_annotations_used_for_detection: bool = False
    unknown_camera_generalization_verified: bool = False
    source_template_video_sha256: str
    target_video_sha256: str
    frames: int
    observations: list[FullFrameDetectionRow] = Field(default_factory=list)
    tracking: TemporalReIDReport | None = None
    blockers: list[str] = Field(default_factory=list)


class RigAnnotatedEvaluationReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    annotation_source: str = "TARGET_BLENDER_RIG_FRAME_QC_FOR_EVALUATION_ONLY"
    annotated_video_sha256: str
    compared_count: int
    mean_iou: float | None = None
    minimum_iou: float | None = None
    blockers: list[str] = Field(default_factory=list)


class FullFrameReferenceActorScanner:
    def __init__(
        self, *, score_floor:float=.85,
        minimum_secondary_margin:float=.04,
        minimum_frame_coverage:float=.90,
        sample_count:int=12,
    ):
        self.score_floor=score_floor
        self.minimum_secondary_margin=minimum_secondary_margin
        self.minimum_frame_coverage=minimum_frame_coverage
        self.sample_count=sample_count

    @staticmethod
    def _sha(path:Path)->str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _frame(path:Path,frame_index:int)->np.ndarray:
        capture=cv2.VideoCapture(str(path))
        try:
            if not capture.isOpened():
                raise ValueError("REFERENCE_VIDEO_NOT_READABLE")
            capture.set(cv2.CAP_PROP_POS_FRAMES,frame_index)
            ok,frame=capture.read()
            if not ok:
                raise ValueError("REFERENCE_VIDEO_FRAME_UNREADABLE")
            return frame
        finally:
            capture.release()

    def reference_templates(self,*,source_video:str|Path) -> dict[str,np.ndarray]:
        # The only access to rig annotation in this class is the *reference*
        # template creation, never target scan or localization.
        source=Path(source_video).resolve()
        if not source.is_file():
            raise ValueError("REFERENCE_VIDEO_MISSING")
        file=Path(str(source)+".frame_qc.json")
        if not file.is_file():
            raise ValueError("REFERENCE_FRAME_ANNOTATIONS_MISSING")
        info=json.loads(file.read_text(encoding="utf-8"))
        cap=cv2.VideoCapture(str(source))
        try:
            fps=float(cap.get(cv2.CAP_PROP_FPS))
            mid=float(info["mid"]["time_seconds"])
            if fps<=0:
                raise ValueError("REFERENCE_FPS_INVALID")
        finally:
            cap.release()
        frame=self._frame(source,round(mid*fps))
        h,w=frame.shape[:2]
        templates={}
        for actor,entry in info["actors"].items():
            box=entry["screen_box"] # Blender NDC bottom-left coordinates.
            x0=int(box["x0"]*w);x1=int(np.ceil(box["x1"]*w))
            y0=int((1-box["y1"])*h)
            y1=int(np.ceil((1-box["y0"])*h))
            part=frame[y0:y1,x0:x1]
            if part.shape[0]<16 or part.shape[1]<16:
                raise ValueError("REFERENCE_TEMPLATE_TOO_SMALL")
            templates[actor]=cv2.cvtColor(part,cv2.COLOR_BGR2GRAY)
        if len(templates)<2:
            raise ValueError("REFERENCE_ACTOR_VARIETY_INSUFFICIENT")
        return templates

    def _locate(self,frame_gray:np.ndarray,template:np.ndarray,
                actor:str,time_seconds:float) -> FullFrameDetectionRow:
        h,w=frame_gray.shape[:2]
        th,tw=template.shape[:2]
        if h<th or w<tw:
            return FullFrameDetectionRow(actor_id=actor,time_seconds=time_seconds,
                 template_score=0.,secondary_score=0.,secondary_margin=0.,
                 blockers=["TEMPLATE_LARGER_THAN_TARGET_FRAME"])
        matrix=cv2.matchTemplate(frame_gray,template,cv2.TM_CCOEFF_NORMED)
        if not np.isfinite(matrix).all():
            return FullFrameDetectionRow(actor_id=actor,time_seconds=time_seconds,
                 template_score=0.,secondary_score=0.,secondary_margin=0.,
                 blockers=["TEMPLATE_MATCH_NON_FINITE"])
        _,score,_,where=cv2.minMaxLoc(matrix)
        # Second peak after suppressing neighborhood of the first location.
        # A pasted impostor matching the actor reference must veto success.
        x,y=where
        alternate=matrix.copy()
        suppress_x=max(2,round(tw*.55))
        suppress_y=max(2,round(th*.55))
        alternate[max(0,y-suppress_y):min(matrix.shape[0],y+suppress_y+1),
                  max(0,x-suppress_x):min(matrix.shape[1],x+suppress_x+1)]=-1
        _,second,_,_=cv2.minMaxLoc(alternate)
        margin=float(score-second)
        blockers=[]
        if score<self.score_floor:
            blockers.append("REFERENCE_APPEARANCE_MATCH_BELOW_THRESHOLD")
        if second>=self.score_floor and margin<self.minimum_secondary_margin:
            blockers.append("TWO_SIMILAR_SCREEN_ACTOR_CANDIDATES")
        return FullFrameDetectionRow(
            actor_id=actor,time_seconds=time_seconds,
            screen_box={
                "x0":x/w,"y0":y/h,"x1":(x+tw)/w,"y1":(y+th)/h,
            } if not blockers else None,
            template_score=float(score),secondary_score=float(second),
            secondary_margin=margin,matched=not blockers,blockers=blockers,
        )

    @staticmethod
    def evaluate_rig_ground_truth(
        report: TargetShotSearchReport,
        target_video:str|Path,
        *,minimum_iou:float=.70,
    )->RigAnnotatedEvaluationReport:
        """Target rig labels are used AFTER detection, never fed to scanner."""
        target=Path(target_video).resolve()
        if not target.is_file():
            raise ValueError("TARGET_EVALUATION_VIDEO_MISSING")
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        if digest!=report.target_video_sha256:
            raise ValueError("TARGET_EVALUATION_HASH_MISMATCH")
        side=Path(str(target)+".frame_qc.json")
        if not side.is_file():
            return RigAnnotatedEvaluationReport(
                status="BLOCKED",passed=False,measured=False,
                annotated_video_sha256=digest,compared_count=0,
                blockers=["TARGET_RIG_EVALUATION_ANNOTATIONS_MISSING"],
            )
        rows=json.loads(side.read_text(encoding="utf-8"))["actors"]
        errors=[]
        ious=[]
        for match in report.observations:
            if not match.matched or match.actor_id not in rows or not match.screen_box:
                errors.append(f"{match.actor_id}:ACTOR_NOT_FOUND_OR_UNLABELED")
                continue
            source=rows[match.actor_id]["screen_box"]
            expected={
                "x0":source["x0"],"x1":source["x1"],
                "y0":1-source["y1"],"y1":1-source["y0"],
            }
            iou=TemporalReIDEngine.iou(expected,match.screen_box)
            ious.append(iou)
            if iou<minimum_iou:
                errors.append(f"{match.actor_id}:TARGET_RIG_IOU_BELOW_FLOOR")
        if not report.observations:
            errors.append("SEARCH_OBSERVATIONS_MISSING")
        errors=sorted(set(errors))
        return RigAnnotatedEvaluationReport(
            status="RIG_LABEL_EVALUATION_PASS" if not errors else "BLOCKED",
            passed=not errors,measured=bool(ious),
            annotated_video_sha256=digest,
            compared_count=len(ious),mean_iou=float(np.mean(ious)) if ious else None,
            minimum_iou=min(ious) if ious else None,blockers=errors,
        )

    def scan(self,*,source_video:str|Path,target_video:str|Path,
             output_sample_count:int|None=None)->TargetShotSearchReport:
        source=Path(source_video).resolve()
        target=Path(target_video).resolve()
        if not source.is_file() or not target.is_file():
            raise ValueError("REFERENCE_OR_TARGET_MEDIA_MISSING")
        src_digest=self._sha(source)
        target_digest=self._sha(target)
        if source==target or src_digest==target_digest:
            raise ValueError("IDENTICAL_SOURCE_AND_TARGET_NOT_CROSS_SHOT")
        templates=self.reference_templates(source_video=source)
        capture=cv2.VideoCapture(str(target))
        rows=[]
        timelines=[]
        try:
            count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps=float(capture.get(cv2.CAP_PROP_FPS))
            if count<4 or fps<=0:
                raise ValueError("TARGET_VIDEO_FRAMES_INVALID")
            n=min(count,max(4,output_sample_count or self.sample_count))
            indices=sorted(set(int(round(t)) for t in np.linspace(0,count-1,n)))
            for idx in indices:
                capture.set(cv2.CAP_PROP_POS_FRAMES,idx)
                ok,frame=capture.read()
                if not ok:
                    raise RuntimeError("FULL_FRAME_TARGET_DECODE_FAILED")
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                detections=[]
                for actor,template in sorted(templates.items()):
                    found=self._locate(gray,template,actor,idx/fps)
                    rows.append(found)
                    if found.matched:
                        detections.append(ActorDetection(
                            detection_id=f"{actor}@{idx}",
                            screen_box=found.screen_box,
                            appearance_scores={
                                name:(max(.0,min(1.,found.template_score))
                                      if name==actor else 0.0)
                                for name in templates
                            },
                            origin=DetectionOrigin.INDEPENDENT,
                        ))
                timelines.append(TemporalFrame(
                    time_seconds=idx/fps,detections=detections,
                    scene_cut=False,
                ))
        finally:
            capture.release()
        temporal=TemporalReIDEngine(
            identity_floor=max(.70,self.score_floor),
            minimum_coverage=self.minimum_frame_coverage,
        ).assess(actor_ids=sorted(templates),frames=timelines)
        errors=sorted(set(
            [f"{s.actor_id}:{x}" for s in rows for x in s.blockers]
            + [f"TRACK:{x}" for x in temporal.blockers]
        ))
        # No sidecar of target shot has been read for detection.
        return TargetShotSearchReport(
            status="CONTROLLED_REAL_RENDER_FULL_FRAME_MATCH_PASS" if not errors else "BLOCKED",
            passed=not errors,measured=bool(rows),
            source_template_video_sha256=src_digest,
            target_video_sha256=target_digest,
            frames=len(timelines),observations=rows,tracking=temporal,
            blockers=errors,
        )
