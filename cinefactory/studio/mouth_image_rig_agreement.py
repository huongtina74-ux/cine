from __future__ import annotations

"""Cross-check image-discovered mouth motion against 3D rig projection only
*after* image localization. Image search is independent of the mouth mesh,
but agreement is a calibrated ground-truth proxy, not human annotations.
"""
from pydantic import BaseModel, Field
from cinefactory.studio.face_mouth_observability import ImageMouthObservabilityReport
from cinefactory.studio.rendered_mouth_qc import RenderedMouthSample


class ImageRigMouthMatch(BaseModel):
    actor_id: str
    line_id: str
    iou: float = 0.
    passed: bool
    blockers: list[str] = Field(default_factory=list)


class MouthCrossCheckReport(BaseModel):
    status: str
    passed: bool
    production_qualified: bool = False
    independent_landmark_ground_truth: bool = False
    matches: list[ImageRigMouthMatch] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class MouthRigCrossCheck:
    def __init__(self, *, minimum_iou: float=.32):
        self.minimum_iou=minimum_iou

    @staticmethod
    def _iou(a:dict,b:dict)->float:
        area=lambda r:max(0.,r["x1"]-r["x0"])*max(0.,r["y1"]-r["y0"])
        inter=max(0.,min(a["x1"],b["x1"])-max(a["x0"],b["x0"])) * max(
            0.,min(a["y1"],b["y1"])-max(a["y0"],b["y0"]))
        union=area(a)+area(b)-inter
        return float(inter/union) if union>0 else 0.

    def compare(self,*,observed: ImageMouthObservabilityReport,
                projected: list[RenderedMouthSample])->MouthCrossCheckReport:
        if not observed.passed:
            return MouthCrossCheckReport(status="BLOCKED",passed=False,
                                         blockers=["IMAGE_MOUTH_OBSERVATION_NOT_PASSED"])
        matches=[]
        for candidate in observed.candidates:
            compatible=[
                x.mouth_box for x in projected if
                x.line_id==candidate.line_id and x.actor_id==candidate.actor_id
                and x.mouth_box is not None
            ]
            failures=[]
            if len(compatible)<4 or candidate.screen_box_top_left is None:
                failures.append("MOUTH_RIG_IMAGE_PAIR_MISSING")
                overlap=0.
            else:
                reference={
                    "x0":min(b["x0"] for b in compatible),
                    "y0":min(b["y0"] for b in compatible),
                    "x1":max(b["x1"] for b in compatible),
                    "y1":max(b["y1"] for b in compatible),
                }
                overlap=self._iou(reference,candidate.screen_box_top_left)
                if overlap<self.minimum_iou:
                    failures.append("MOUTH_IMAGE_RIG_LOCATION_DISAGREEMENT")
            matches.append(ImageRigMouthMatch(
                actor_id=candidate.actor_id,line_id=candidate.line_id,
                iou=overlap,passed=not failures,blockers=failures,
            ))
        findings=sorted({
            f"{m.line_id}:{f}" for m in matches for f in m.blockers
        })
        if not matches:
            findings.append("MOUTH_IMAGE_RIG_MATCHES_MISSING")
        return MouthCrossCheckReport(
            status="RIG_CONSTRAINED_IMAGE_LOCALIZATION_PASS" if not findings else "BLOCKED",
            passed=bool(matches) and not findings,matches=matches,blockers=findings,
        )
