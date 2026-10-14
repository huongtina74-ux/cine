from __future__ import annotations

"""SAPI word timing versus actual PCM, without claiming forced alignment.

The audio constrains word presence and duration, not linguistic correctness:
the timeline still originates from the TTS that generated the audio.
"""
import hashlib
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field, model_validator


class SynthesizerWordEvent(BaseModel):
    text: str = Field(min_length=1)
    time_seconds: float = Field(ge=0)
    character_position: int = Field(ge=0)
    character_count: int = Field(ge=1)


class WordAudioEvidence(BaseModel):
    text: str
    start_seconds: float
    end_seconds: float
    peak_rms: float
    voice_coverage: float
    passed: bool
    findings: list[str] = Field(default_factory=list)


class AudioConstrainedWordReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    audio_sha256: str
    words: list[WordAudioEvidence] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    source_timing: str = "SYNTHESIZER_SPEAK_PROGRESS"
    forced_alignment_verified: bool = False
    phoneme_alignment_verified: bool = False
    production_qualified: bool = False


class AudioConstrainedWordVerifier:
    """Small local, deterministic PCM consistency evaluator."""

    def __init__(
        self, *, minimum_peak_rms: float=.006,
        minimum_voice_coverage: float=.12,
        frame_seconds: float=.025,
    ) -> None:
        self.minimum_peak_rms=minimum_peak_rms
        self.minimum_voice_coverage=minimum_voice_coverage
        self.frame_seconds=frame_seconds

    @staticmethod
    def _canonical_words(text: str) -> list[str]:
        return re.findall(r"[^\W_]+(?:['’-][^\W_]+)*",text.casefold(),flags=re.UNICODE)

    @staticmethod
    def decode_wav(path: Path) -> tuple[np.ndarray,int]:
        # FFmpeg normalizes supported WAV subtypes to a known local stream format.
        run=subprocess.run([
            "ffmpeg","-nostdin","-v","error","-i",str(path),
            "-map","0:a:0","-vn","-ac","1","-ar","16000",
            "-acodec","pcm_f32le","-f","f32le","pipe:1",
        ],capture_output=True,timeout=40,check=False)
        if run.returncode or not run.stdout:
            raise RuntimeError("WORD_ALIGNMENT_AUDIO_DECODE_FAILED")
        return np.frombuffer(run.stdout,dtype="<f4").astype(np.float64),16000

    def verify(
        self, *, audio_path: str | Path, audio_sha256: str,
        transcript: str, word_events: list[SynthesizerWordEvent],
    ) -> AudioConstrainedWordReport:
        path=Path(audio_path).resolve()
        if not path.is_file():
            raise ValueError("WORD_ALIGNMENT_AUDIO_MISSING")
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=audio_sha256:
            raise ValueError("WORD_ALIGNMENT_AUDIO_HASH_MISMATCH")
        if not word_events:
            return AudioConstrainedWordReport(
                status="BLOCKED",passed=False,measured=False,
                audio_sha256=actual,
                blockers=["SYNTHESIZER_WORD_EVENTS_MISSING"],
            )
        expected=self._canonical_words(transcript)
        annotated=self._canonical_words(" ".join(w.text for w in word_events))
        blockers=[]
        if expected!=annotated:
            blockers.append("SYNTHESIZER_WORD_TEXT_MISMATCH")
        if [w.time_seconds for w in word_events]!=sorted(w.time_seconds for w in word_events):
            blockers.append("SYNTHESIZER_WORD_TIMES_NONMONOTONIC")
        if len({w.character_position for w in word_events})!=len(word_events):
            blockers.append("SYNTHESIZER_WORD_POSITIONS_DUPLICATED")
        for event in word_events:
            snippet=transcript[
                event.character_position:
                event.character_position+event.character_count
            ]
            if self._canonical_words(snippet)!=self._canonical_words(event.text):
                blockers.append("SYNTHESIZER_CHARACTER_SPAN_MISMATCH")
                break
        audio,rate=self.decode_wav(path)
        duration=len(audio)/rate
        rows=[]
        for i,word in enumerate(word_events):
            start=word.time_seconds
            end=(word_events[i+1].time_seconds if i+1<len(word_events)
                 else duration)
            # A conservative timeline window is wider than one analysis frame.
            if not 0 <= start < end <= duration + .045:
                blockers.append(f"WORD_TIME_OUTSIDE_AUDIO:{i}")
                rows.append(WordAudioEvidence(
                    text=word.text,start_seconds=start,end_seconds=end,
                    peak_rms=0,voice_coverage=0,passed=False,
                    findings=["WORD_TIME_OUTSIDE_AUDIO"],
                ))
                continue
            points=[]
            step=max(1,round(rate*self.frame_seconds))
            for offset in range(max(0,int(start*rate)),min(len(audio),int(end*rate)),step):
                block=audio[offset:min(len(audio),offset+step)]
                if block.size:
                    points.append(float(np.sqrt(np.mean(block*block))))
            peak=max(points,default=0.)
            voiced=sum(value >= self.minimum_peak_rms for value in points)
            coverage=voiced/len(points) if points else 0.
            findings=[]
            if peak<self.minimum_peak_rms:
                findings.append("WORD_AUDIO_SIGNAL_MISSING")
            if coverage<self.minimum_voice_coverage:
                findings.append("WORD_AUDIO_ACTIVITY_LOW")
            rows.append(WordAudioEvidence(
                text=word.text,start_seconds=start,end_seconds=end,
                peak_rms=peak,voice_coverage=coverage,
                passed=not findings,findings=findings,
            ))
            if findings:
                blockers.extend(f"WORD_{i}:{finding}" for finding in findings)
        return AudioConstrainedWordReport(
            status="SYNTH_WORD_PCM_CONSISTENT" if not blockers else "BLOCKED",
            passed=not blockers,measured=bool(rows),audio_sha256=actual,
            words=rows,blockers=sorted(set(blockers)),
        )
