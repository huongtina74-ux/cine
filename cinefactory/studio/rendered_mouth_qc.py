from __future__ import annotations

"""Post-render Blender mouth projection to actual pixel-change QC.

Input boxes are projected rig geometry (not trusted face landmarks). Sampling
rendered pixels provides an independent image signal, but does not establish
accurate mouth shapes/phonemes or rule out occlusion at arbitrary angles.
"""
import hashlib
from pathlib import Path

import cv2
import numpy as np
from pydantic import BaseModel, Field, model_validator


class RenderedMouthSample(BaseModel):
    line_id: str
    actor_id: str
    frame_index: int = Field(ge=1)
    time_seconds: float = Field(ge=0)
    mouth_box: dict[str,float] | None
    projected_width_px: float = Field(ge=0)
    projected_height_px: float = Field(ge=0)
    expected_jaw: float = Field(ge=0,le=1)
    coordinate_system: str = "NORMALIZED_TOP_LEFT"
    provenance: str = "BLENDER_RIG_MOUTH_PROJECTION"
    visibility_verified: bool = False

    @model_validator(mode="after")
    def valid_roi(self):
        if self.coordinate_system!="NORMALIZED_TOP_LEFT" or self.provenance!="BLENDER_RIG_MOUTH_PROJECTION":
            raise ValueError("UNTRUSTED_MOUTH_REGION_PROVENANCE")
        if self.mouth_box is not None:
            b=self.mouth_box
            if not all(k in b for k in ("x0","x1","y0","y1")):
                raise ValueError("MOUTH_BBOX_KEYS_MISSING")
            if not (0<=b["x0"]<b["x1"]<=1 and 0<=b["y0"]<b["y1"]<=1):
                raise ValueError("MOUTH_BBOX_INVALID")
        return self


class RenderedMouthCheck(BaseModel):
    line_id: str
    actor_id: str
    measured: bool
    passed: bool
    sample_count: int
    valid_projected_samples: int
    mean_width_pixels: float = 0.
    mean_height_pixels: float = 0.
    pixel_activity_range: float | None = None
    pixel_signal_kind: str = "DARK_PIXEL_FRACTION"
    jaw_pixel_correlation: float | None = None
    observed_activity: list[float] = Field(default_factory=list)
    expected_jaw: list[float] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class RenderedMouthQCReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    image_mouth_motion_measured: bool = False
    phoneme_shapes_verified: bool = False
    video_path: str
    video_sha256: str | None = None
    checks: list[RenderedMouthCheck] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class RenderedMouthProjectionQC:
    def __init__(
        self, *, minimum_width_pixels: float=3.0,
        minimum_height_pixels: float=2.0,
        minimum_activity_range: float=.04,
        minimum_correlation: float=.35,
    ) -> None:
        self.minimum_width_pixels=minimum_width_pixels
        self.minimum_height_pixels=minimum_height_pixels
        self.minimum_activity_range=minimum_activity_range
        self.minimum_correlation=minimum_correlation

    def evaluate(
        self, *, video_path: str | Path,
        samples: list[RenderedMouthSample],
    ) -> RenderedMouthQCReport:
        path=Path(video_path).resolve()
        if not path.is_file():
            return RenderedMouthQCReport(
                status="BLOCKED",passed=False,measured=False,
                video_path=str(path),blockers=["MOUTH_VIDEO_MISSING"],
            )
        groups:dict[tuple[str,str],list[RenderedMouthSample]]={}
        for sample in samples:
            groups.setdefault((sample.line_id,sample.actor_id),[]).append(sample)
        capture=cv2.VideoCapture(str(path))
        checks:list[RenderedMouthCheck]=[]
        try:
            fps=float(capture.get(cv2.CAP_PROP_FPS))
            frame_count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            width=int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height=int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if fps<=0 or frame_count<1 or width<1 or height<1:
                return RenderedMouthQCReport(
                    status="BLOCKED",passed=False,measured=False,
                    video_path=str(path),blockers=["MOUTH_VIDEO_DECODE_INVALID"],
                )
            for (line,actor),group in sorted(groups.items()):
                errors=[]
                ordered=sorted(group,key=lambda s:s.frame_index)
                ids=[s.frame_index for s in ordered]
                if len(set(ids))!=len(ids):
                    errors.append("MOUTH_FRAME_SAMPLES_DUPLICATE")
                projected=[
                    item for item in ordered
                    if item.mouth_box and
                       item.projected_width_px>=self.minimum_width_pixels and
                       item.projected_height_px>=self.minimum_height_pixels
                ]
                if len(projected)<4:
                    errors.append("MOUTH_PROJECTED_REGION_TOO_SMALL_OR_HIDDEN")
                if any(item.frame_index>frame_count for item in ordered):
                    errors.append("MOUTH_FRAME_OUT_OF_VIDEO")
                # Fixed actor-specific union ROI, so opening/closing the mouth
                # changes the amount of darkness, not the crop's denominator.
                if projected:
                    boxes=[s.mouth_box for s in projected]
                    x0=max(0,int(np.floor(min(b["x0"] for b in boxes)*width))-2)
                    y0=max(0,int(np.floor(min(b["y0"] for b in boxes)*height))-2)
                    x1=min(width,int(np.ceil(max(b["x1"] for b in boxes)*width))+2)
                    y1=min(height,int(np.ceil(max(b["y1"] for b in boxes)*height))+2)
                else:
                    x0=y0=x1=y1=0
                if x1-x0<3 or y1-y0<2:
                    errors.append("MOUTH_FIXED_ROI_TOO_SMALL")
                predicted=[]
                activity=[]
                luma_inverse=[]
                signal_kind="DARK_PIXEL_FRACTION"
                if not errors:
                    for item in ordered:
                        if item.frame_index>frame_count:
                            continue
                        capture.set(cv2.CAP_PROP_POS_FRAMES,item.frame_index-1)
                        ok,frame=capture.read()
                        if not ok:
                            errors.append("MOUTH_FRAME_READ_FAILED")
                            break
                        roi=frame[y0:y1,x0:x1]
                        if not roi.size:
                            errors.append("MOUTH_ROI_EMPTY")
                            break
                        grey=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
                        activity.append(float(np.mean(grey<90)))
                        luma_inverse.append(1.0-float(np.mean(grey))/255.0)
                        predicted.append(item.expected_jaw)
                # Predeclared saturation fallback: selected solely from
                # pixel dynamic range, never based on correlation with cue.
                if (len(activity)>=4 and
                    float(np.ptp(activity))<self.minimum_activity_range and
                    float(np.ptp(luma_inverse))>=self.minimum_activity_range):
                    activity=luma_inverse
                    signal_kind="INVERSE_MEAN_LUMA_SATURATION_FALLBACK"
                corr=None
                signal_range=None
                if len(activity)>=4:
                    signal_range=float(np.ptp(activity))
                    if signal_range<self.minimum_activity_range:
                        errors.append("MOUTH_PIXEL_ACTIVITY_INSUFFICIENT")
                    if np.std(predicted)<.10:
                        errors.append("EXPECTED_VISEMES_NOT_DYNAMIC")
                    if not errors:
                        corr=float(np.corrcoef(predicted,activity)[0,1])
                        if not np.isfinite(corr) or corr<self.minimum_correlation:
                            errors.append("RENDERED_MOUTH_VISEME_CORRELATION_LOW")
                else:
                    errors.append("MOUTH_PIXEL_SAMPLES_INSUFFICIENT")
                checks.append(RenderedMouthCheck(
                    line_id=line,actor_id=actor,
                    measured=len(activity)>=4,
                    passed=not errors,
                    sample_count=len(ordered),
                    valid_projected_samples=len(projected),
                    mean_width_pixels=sum(s.projected_width_px for s in ordered)/len(ordered),
                    mean_height_pixels=sum(s.projected_height_px for s in ordered)/len(ordered),
                    pixel_activity_range=signal_range,
                    pixel_signal_kind=signal_kind,
                    jaw_pixel_correlation=corr,
                    observed_activity=activity,expected_jaw=predicted,
                    blockers=sorted(set(errors)),
                ))
        finally:
            capture.release()
        blockers=sorted(set(
            [f"{item.line_id}:{code}" for item in checks for code in item.blockers]
        ))
        if not checks:
            blockers.append("NO_MOUTH_PROJECTION_SAMPLES")
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        return RenderedMouthQCReport(
            status="PIXEL_CONFORMANCE_ONLY_PASS" if not blockers else "BLOCKED",
            passed=not blockers,measured=any(c.measured for c in checks),
            image_mouth_motion_measured=any(c.measured for c in checks),
            video_path=str(path),video_sha256=digest,
            checks=checks,blockers=blockers,
        )
