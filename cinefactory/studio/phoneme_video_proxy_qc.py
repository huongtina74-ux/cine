from __future__ import annotations
"""Compare acoustically aligned PHONE-TIME OPENNESS PROXY to real video pixels.

The phone labels come from the known transcript's lexicon. Their alignment
times come from the audio model, not TTS viseme events. Proxy mouth-open
levels are approximate; not independently labelled mouth shapes, and never
production qualified. Fixed lag=0; no optimizing offset for high score.
"""
import math
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field
from cinefactory.studio.acoustic_forced_alignment import AcousticAlignmentReport
from cinefactory.studio.rendered_mouth_qc import (
    RenderedMouthSample,RenderedMouthQCReport,
)


class PhonemeVideoCheck(BaseModel):
    actor_id: str
    line_id: str
    observed_samples: int
    correlation_zero_lag: float | None
    proxy_dynamic_range: float
    passed: bool
    blockers: list[str] = Field(default_factory=list)


class PhonemeVideoProxyReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    independent_acoustic_phone_timings: bool = False
    phoneme_shapes_independently_validated: bool = False
    known_transcript_supplied_to_aligner: bool = True
    comparison_method: str = "PRESET_ARPABET_OPENNESS_VS_RENDERED_PIXEL_ZERO_LAG"
    checks: list[PhonemeVideoCheck] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class PhonemeVideoProxyQC:
    _VOWELS={
        "AA","AE","AH","AO","AW","AY","EH","ER","EY",
        "IH","IY","OW","OY","UH","UW",
    }
    _LIPS_CLOSED={"B","M","P"}

    def __init__(self, *,minimum_corr:float=.55,minimum_frames:int=8):
        self.minimum_corr=minimum_corr
        self.minimum_frames=minimum_frames

    def _openness(self,*,phones:AcousticAlignmentReport,
                  at_seconds:float)->float:
        active=next((
            row.phone for row in phones.phones if
            row.start_seconds<=at_seconds<row.end_seconds
        ),None)
        if active is None or active in self._LIPS_CLOSED:
            return 0.
        if active in self._VOWELS:
            return .95
        return .38

    def verify(self,*,pixel:RenderedMouthQCReport,
               projections:list[RenderedMouthSample],
               alignments:dict[str,AcousticAlignmentReport],
               audio_start_seconds:dict[str,float],
               shift_seconds:float=0.) -> PhonemeVideoProxyReport:
        if not pixel.passed:
            return PhonemeVideoProxyReport(
                status="BLOCKED",passed=False,measured=False,
                blockers=["RENDERED_VIDEO_MOUTH_PIXEL_QC_FAILED"],
            )
        checks=[]
        for c in pixel.checks:
            findings=[]
            if c.actor_id not in alignments or c.actor_id not in audio_start_seconds:
                findings.append("ACOUSTIC_SOURCE_UNAVAILABLE_FOR_ACTOR")
            source=alignments.get(c.actor_id)
            if source is not None and not source.passed:
                findings.append("ACOUSTIC_SOURCE_ALIGNMENT_NOT_PASSED")
            group=sorted([
                x for x in projections if x.actor_id==c.actor_id and
                x.line_id==c.line_id
            ],key=lambda x:x.frame_index)
            if len(group)!=len(c.observed_activity):
                findings.append("MOUTH_PIXEL_FRAME_PROJECTION_COUNT_MISMATCH")
            if len(group)<self.minimum_frames:
                findings.append("INSUFFICIENT_PHONEME_IMAGE_SAMPLES")
            pred=[]
            if source is not None and source.passed and len(group)==len(c.observed_activity):
                for frame in group:
                    time=frame.time_seconds-audio_start_seconds[c.actor_id]-shift_seconds
                    pred.append(self._openness(phones=source,at_seconds=time))
            variation=float(np.ptp(pred)) if pred else 0.
            if variation<.30:
                findings.append("ACOUSTIC_PHONE_OPENNESS_NOT_DYNAMIC")
            corr=None
            if len(pred)>=self.minimum_frames and variation>=.30 and c.observed_activity:
                obs=np.asarray(c.observed_activity,dtype=float)
                if float(np.std(obs))<1e-4 or float(np.std(pred))<.05:
                    findings.append("MOUTH_IMAGE_OR_PHONE_PROXY_STATIC")
                else:
                    cc=float(np.corrcoef(obs,pred)[0,1])
                    if math.isfinite(cc):
                        corr=cc
                        if corr<self.minimum_corr:
                            findings.append("PHONEME_VIDEO_PROXY_CORRELATION_LOW")
                    else:
                        findings.append("NONFINITE_ACOUSTIC_VIDEO_CORRELATION")
            checks.append(PhonemeVideoCheck(
                actor_id=c.actor_id,line_id=c.line_id,
                observed_samples=len(c.observed_activity),
                correlation_zero_lag=corr,proxy_dynamic_range=variation,
                passed=not findings,blockers=sorted(set(findings)),
            ))
        blockers=sorted({
            f"{item.actor_id}:{finding}"
            for item in checks for finding in item.blockers
        })
        if not checks:
            blockers.append("NO_ACOUSTIC_VIDEO_LINES")
        return PhonemeVideoProxyReport(
            status="ACOUSTIC_PHONE_IMAGE_PROXY_PASS" if not blockers else "BLOCKED",
            passed=not blockers,measured=bool(checks),
            independent_acoustic_phone_timings=any(
                a.independent_audio_acoustic_timing for a in alignments.values()
            ),
            checks=checks,blockers=blockers,
        )
