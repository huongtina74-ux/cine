from __future__ import annotations

"""Source-conditioned speaker attribution on a final audio mix.

NOT blind speaker diarization: source WAV stems are supplied by production.
Measures audio content in the actual mux and rejects stem swaps, silence,
large shifts and ambiguous voice signatures.
"""
import hashlib
import subprocess
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field, model_validator


class ActorVoiceStem(BaseModel):
    actor_id: str
    line_id: str
    source_wav: str
    source_sha256: str
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)

    @model_validator(mode="after")
    def valid(self):
        if self.end_seconds <= self.start_seconds:
            raise ValueError("SPEAKER_STEM_WINDOW_INVALID")
        if len(self.source_sha256)!=64:
            raise ValueError("SPEAKER_STEM_SHA_INVALID")
        return self


class SpeakerStemCheck(BaseModel):
    actor_id: str
    line_id: str
    score: float | None = None
    strongest_competitor: float | None = None
    margin: float | None = None
    offset_seconds: float | None = None
    passed: bool
    blockers: list[str] = Field(default_factory=list)


class SourceSpeakerReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    method: str = "SOURCE_CONDITIONED_PCM_ENVELOPE_MATCH"
    independent_diarization_verified: bool = False
    media_path: str
    media_sha256: str | None = None
    checks: list[SpeakerStemCheck] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class SourceConditionedSpeakerVerifier:
    def __init__(
        self, *, frame_seconds: float=.020, max_shift_seconds: float=.100,
        minimum_score: float=.66, minimum_margin: float=.15,
    ):
        self.frame_seconds=frame_seconds
        self.max_shift_seconds=max_shift_seconds
        self.minimum_score=minimum_score
        self.minimum_margin=minimum_margin

    @staticmethod
    def pcm(path: Path) -> np.ndarray:
        cmd=[
            "ffmpeg","-nostdin","-v","error","-i",str(path),
            "-map","0:a:0","-vn","-ac","1","-ar","16000",
            "-f","f32le","-acodec","pcm_f32le","pipe:1",
        ]
        run=subprocess.run(cmd,capture_output=True,timeout=35,check=False)
        if run.returncode or not run.stdout:
            raise RuntimeError("SOURCE_SPEAKER_AUDIO_DECODING_FAILED")
        return np.frombuffer(run.stdout,dtype="<f4").astype(np.float64)

    def envelope(self, pcm: np.ndarray) -> np.ndarray:
        size=int(round(16000*self.frame_seconds))
        count=len(pcm)//size
        if count<8:
            return np.array([],dtype=float)
        shaped=pcm[:count*size].reshape(count,size)
        return np.sqrt(np.mean(shaped*shaped,axis=1))

    @staticmethod
    def _corr(a: np.ndarray,b: np.ndarray)->float:
        if len(a)<8 or len(a)!=len(b) or np.std(a)<.002 or np.std(b)<.002:
            return -1.
        corr=float(np.corrcoef(a,b)[0,1])
        return corr if np.isfinite(corr) else -1.

    def _score(self, mix: np.ndarray, source: np.ndarray,
               scheduled_start: float, scheduled_end: float
              ) -> tuple[float,float]:
        # Works on the *same* time base; comparison is to the actual
        # unmodified source segment and bounded shifts in final media.
        size=self.frame_seconds
        n=min(len(source),max(8,int((scheduled_end-scheduled_start)/size)))
        source=source[:n]
        if len(source)<8:
            return -1.,0.
        best=(-1.,0.)
        max_lag=round(self.max_shift_seconds/size)
        for lag in range(-max_lag,max_lag+1):
            idx=round(scheduled_start/size)+lag
            if idx<0 or idx+len(source)>len(mix):
                continue
            val=self._corr(source,mix[idx:idx+len(source)])
            if val>best[0]:
                best=(val,lag*size)
        return best

    def verify(
        self, *, media_path: str|Path,
        stems: list[ActorVoiceStem],
    ) -> SourceSpeakerReport:
        path=Path(media_path).resolve()
        if not path.is_file():
            return SourceSpeakerReport(
                status="BLOCKED",passed=False,measured=False,
                media_path=str(path),blockers=["FINAL_MEDIA_MISSING"],
            )
        if not stems or len({s.line_id for s in stems})!=len(stems):
            return SourceSpeakerReport(
                status="BLOCKED",passed=False,measured=False,
                media_path=str(path),blockers=["SPEAKER_LINE_SET_INVALID"],
            )
        ordered=sorted(stems,key=lambda item:item.start_seconds)
        if any(a.end_seconds>b.start_seconds+1e-6 for a,b in zip(ordered,ordered[1:])):
            return SourceSpeakerReport(
                status="BLOCKED",passed=False,measured=False,
                media_path=str(path),blockers=["OVERLAPPING_SPEAKERS_UNATTRIBUTABLE"],
            )
        try:
            mixed=self.envelope(self.pcm(path))
        except (RuntimeError,subprocess.TimeoutExpired):
            return SourceSpeakerReport(
                status="BLOCKED",passed=False,measured=False,
                media_path=str(path),blockers=["FINAL_AUDIO_DECODE_FAILED"],
            )
        source={}
        for row in stems:
            wav=Path(row.source_wav).resolve()
            if not wav.is_file() or hashlib.sha256(wav.read_bytes()).hexdigest()!=row.source_sha256:
                return SourceSpeakerReport(
                    status="BLOCKED",passed=False,measured=False,
                    media_path=str(path),blockers=["SOURCE_STEM_HASH_MISMATCH"],
                )
            source[row.line_id]=self.envelope(self.pcm(wav))
        checks=[]
        for row in ordered:
            primary,lag=self._score(mixed,source[row.line_id],
                                    row.start_seconds,row.end_seconds)
            rivals=[]
            for other in ordered:
                if other.line_id!=row.line_id:
                    competitor,_=self._score(mixed,source[other.line_id],
                                             row.start_seconds,row.end_seconds)
                    rivals.append(competitor)
            competitor=max(rivals,default=-1.)
            margin=primary-competitor
            errors=[]
            if primary<self.minimum_score:
                errors.append("EXPECTED_SPEAKER_STEM_NOT_CONFIRMED")
            if rivals and margin<self.minimum_margin:
                errors.append("SPEAKER_SIGNATURE_AMBIGUOUS_OR_SWAPPED")
            if abs(lag)>self.max_shift_seconds+1e-6:
                errors.append("SPEAKER_AUDIO_OFFSET_EXCESSIVE")
            checks.append(SpeakerStemCheck(
                actor_id=row.actor_id,line_id=row.line_id,
                score=primary,strongest_competitor=competitor,
                margin=margin,offset_seconds=lag,
                passed=not errors,blockers=errors,
            ))
        blockers=sorted({
            f"{c.line_id}:{b}" for c in checks for b in c.blockers
        })
        return SourceSpeakerReport(
            status="SOURCE_STEM_MATCH_ONLY_PASS" if not blockers else "BLOCKED",
            passed=not blockers,measured=bool(checks),
            media_path=str(path),
            media_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            checks=checks,blockers=blockers,
        )
