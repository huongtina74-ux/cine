from __future__ import annotations

"""Locate moving mouth-like pixels in a controlled frontal actor crop.

No Blender mouth mesh, no viseme cue, and no projected mouth bbox is read.
The *actor* crop remains supplied by rig/shot annotation, so this is not
generic face-landmark detection nor occlusion-independent actor detection.
"""
import hashlib
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from pydantic import BaseModel, Field, model_validator


class ActorFaceSearch(BaseModel):
    actor_id: str
    line_id: str
    actor_box_top_left: dict[str,float]
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    origin: Literal["RIG_ACTOR_BOX","HUMAN_APPROVED_ACTOR_BOX"] = "RIG_ACTOR_BOX"

    @model_validator(mode="after")
    def valid(self):
        b=self.actor_box_top_left
        if not all(k in b for k in ("x0","x1","y0","y1")):
            raise ValueError("ACTOR_BOX_MISSING_COORDS")
        if not (0<=b["x0"]<b["x1"]<=1 and 0<=b["y0"]<b["y1"]<=1):
            raise ValueError("ACTOR_BOX_INVALID")
        if self.end_seconds<=self.start_seconds:
            raise ValueError("FACE_SEARCH_WINDOW_INVALID")
        return self


class MouthImageCandidate(BaseModel):
    actor_id: str
    line_id: str
    detected: bool
    pixel_box: dict[str,int] | None = None
    screen_box_top_left: dict[str,float] | None = None
    motion_pixel_count: int = 0
    image_variance_peak: float | None = None
    observations: int = 0
    blockers: list[str] = Field(default_factory=list)
    detector_provenance: str = "FACE_PATCH_TEMPORAL_VARIANCE"


class ImageMouthObservabilityReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    independent_face_landmarks_verified: bool = False
    media_path: str
    source_sha256: str | None = None
    candidates: list[MouthImageCandidate] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class FacePatchMotionMouthDetector:
    def __init__(
        self, *, minimum_sample_count: int=8,
        variance_threshold: float=4.5,
        minimum_motion_pixels: int=9,
    ) -> None:
        self.minimum_sample_count=minimum_sample_count
        self.variance_threshold=variance_threshold
        self.minimum_motion_pixels=minimum_motion_pixels

    def evaluate(
        self, *, media_path: str|Path, searches: list[ActorFaceSearch],
    ) -> ImageMouthObservabilityReport:
        media=Path(media_path).resolve()
        if not media.is_file():
            return ImageMouthObservabilityReport(
                status="BLOCKED",passed=False,measured=False,
                media_path=str(media),blockers=["VIDEO_FILE_MISSING"],
            )
        cap=cv2.VideoCapture(str(media))
        candidates=[]
        try:
            fps=float(cap.get(cv2.CAP_PROP_FPS))
            total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if not searches or fps<=0 or total<8 or width<=0 or height<=0:
                return ImageMouthObservabilityReport(
                    status="BLOCKED",passed=False,measured=False,
                    media_path=str(media),blockers=["FRAME_SEARCH_UNAVAILABLE"],
                )
            for req in searches:
                b=req.actor_box_top_left
                # Fixed face search space: central ~55% of actor width and
                # upper 55% of total actor height; no mouth bbox supplied.
                ax0,ax1=b["x0"]*width,b["x1"]*width
                ay0,ay1=b["y0"]*height,b["y1"]*height
                x0=max(0,int(ax0+.225*(ax1-ax0)))
                x1=min(width,int(ax1-.225*(ax1-ax0)))
                y0=max(0,int(ay0+.04*(ay1-ay0)))
                y1=min(height,int(ay0+.55*(ay1-ay0)))
                errors=[]
                if x1-x0<12 or y1-y0<14:
                    errors.append("FACE_CROP_BELOW_PIXEL_FLOOR")
                start_frame=max(0,round(req.start_seconds*fps))
                stop_frame=min(total-1,round(req.end_seconds*fps))
                chosen=np.unique(np.linspace(
                    start_frame,stop_frame,num=min(25,max(1,stop_frame-start_frame+1))
                ).astype(int))
                images=[]
                if not errors:
                    for i in chosen:
                        cap.set(cv2.CAP_PROP_POS_FRAMES,int(i))
                        ok,frame=cap.read()
                        if not ok:
                            errors.append("FACE_FRAME_DECODE_FAILED")
                            break
                        frame_grey=cv2.cvtColor(frame[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY)
                        images.append(frame_grey.astype(np.float32))
                motion_pixels=0
                maximum=None
                detected_box=None
                if len(images)>=self.minimum_sample_count and not errors:
                    variance=np.std(np.stack(images),axis=0)
                    maximum=float(np.max(variance))
                    # Remove isolated pixel noise; detect connected temporal
                    # motion components in the central actor FACE region.
                    binary=np.uint8(variance>=self.variance_threshold)
                    binary=cv2.morphologyEx(binary,cv2.MORPH_OPEN,
                                            np.ones((2,2),dtype=np.uint8))
                    n,labels,stats,_=cv2.connectedComponentsWithStats(binary,8)
                    components=[]
                    for k in range(1,n):
                        x,y,bw,bh,area=(int(t) for t in stats[k])
                        if area>=self.minimum_motion_pixels:
                            components.append((area,x,y,bw,bh))
                    if components:
                        area,x,y,bw,bh=max(components)
                        motion_pixels=area
                        detected_box={
                            "x0":x0+x,"y0":y0+y,
                            "x1":x0+x+bw,"y1":y0+y+bh,
                        }
                    else:
                        errors.append("NO_STABLE_MOVING_FACE_COMPONENT")
                elif not errors:
                    errors.append("FACE_TEMPORAL_SAMPLES_INSUFFICIENT")
                candidates.append(MouthImageCandidate(
                    actor_id=req.actor_id,line_id=req.line_id,
                    detected=not errors and detected_box is not None,
                    pixel_box=detected_box,
                    screen_box_top_left={
                        "x0":detected_box["x0"]/width,"y0":detected_box["y0"]/height,
                        "x1":detected_box["x1"]/width,"y1":detected_box["y1"]/height,
                    } if detected_box else None,
                    motion_pixel_count=motion_pixels,
                    image_variance_peak=maximum,observations=len(images),
                    blockers=errors,
                ))
        finally:
            cap.release()
        blockers=sorted({
            f"{x.line_id}:{reason}" for x in candidates for reason in x.blockers
        })
        return ImageMouthObservabilityReport(
            status="IMAGE_FACE_PATCH_MOTION_PASS" if candidates and not blockers else "BLOCKED",
            passed=bool(candidates) and not blockers,
            measured=any(x.observations>=self.minimum_sample_count for x in candidates),
            media_path=str(media),
            source_sha256=hashlib.sha256(media.read_bytes()).hexdigest(),
            candidates=candidates,blockers=blockers,
        )
