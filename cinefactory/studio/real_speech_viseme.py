from __future__ import annotations

"""Local Windows SAPI voice-to-viseme capture with strictly labeled provenance.

VisemeReached is produced by the synthesizer at generation time. It is neither
forced alignment of a separate recording nor independent observed A/V lip-sync.
"""
import hashlib
import json
import math
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field, model_validator
from cinefactory.media.ffmpeg import FFmpegToolchain


class SapiVisemeEvent(BaseModel):
    viseme: int = Field(ge=0,le=21)
    time_seconds: float = Field(ge=0)
    duration_seconds: float = Field(ge=0)
    next_viseme: int = Field(ge=0,le=21)
    emphasis: str = ""


class SpeechVisemeTrack(BaseModel):
    line_id: str
    actor_id: str
    text: str
    voice: str
    audio_path: str
    audio_sha256: str
    audio_duration_seconds: float = Field(gt=0)
    line_start_seconds: float = Field(ge=0)
    timeline_end_seconds: float = Field(gt=0)
    event_source: str
    events: list[SapiVisemeEvent] = Field(min_length=1)
    phoneme_alignment_verified: bool = False
    audio_visual_sync_verified: bool = False
    production_qualified: bool = False

    @model_validator(mode="after")
    def validate_events(self):
        if self.timeline_end_seconds <= self.line_start_seconds:
            raise ValueError("SPEECH_TIMELINE_INVALID")
        if self.timeline_end_seconds+1e-3 < self.line_start_seconds+self.audio_duration_seconds:
            raise ValueError("AUDIO_EXCEEDS_LINE_WINDOW")
        if self.event_source != "SYNTHESIZER_VISEME_REACHED":
            raise ValueError("VISEME_PROVENANCE_UNTRUSTED")
        times=[e.time_seconds for e in self.events]
        if times != sorted(times) or times[-1] > self.audio_duration_seconds + .1:
            raise ValueError("VISEME_EVENTS_OUT_OF_AUDIO")
        if not any(e.viseme != 0 for e in self.events):
            raise ValueError("VISEME_EVENTS_SILENT")
        return self


class RealSpeechVisemeService:
    ALLOWED_VOICES = {
        "Microsoft David Desktop",
        "Microsoft Zira Desktop",
        "Microsoft Huihui Desktop",
    }
    # Procedural mouth approximations (SAPI viseme IDs), NOT measured speech shapes.
    # 0 -> closure. Other mappings are simple jaw-open/widen proxy for block faces.
    JAW_BY_SAPI = (
        .02,.62,.70,.82,.46,.45,.72,.65,.81,.62,.85,
        .72,.40,.48,.32,.26,.25,.35,.30,.19,.53,.60,
    )
    WIDTH_BY_SAPI = (
        .05,.58,.66,.52,.44,.35,.38,.45,.48,.59,.42,
        .50,.45,.38,.32,.46,.55,.49,.34,.47,.57,.54,
    )

    def __init__(self, root: Path | str):
        self.root=Path(root).resolve()
        self.ps_script=self.root/"scripts"/"sapi_viseme_synthesize.ps1"
        self.media=FFmpegToolchain()

    @staticmethod
    def _hash(path: Path) -> str:
        h=hashlib.sha256()
        with path.open("rb") as fh:
            for data in iter(lambda:fh.read(1<<20),b""):
                h.update(data)
        return h.hexdigest()

    def synthesize(
        self, *, line_id: str, actor_id: str, text: str,
        voice: str, output_dir: Path | str, line_start_seconds: float=0.,
        timeline_end_seconds: float | None=None,
    ) -> SpeechVisemeTrack:
        if voice not in self.ALLOWED_VOICES:
            raise ValueError("SAPI_VOICE_NOT_ALLOWLISTED")
        if not text.strip() or len(text)>900 or "\x00" in text:
            raise ValueError("INVALID_SPEECH_TEXT")
        if not line_id or not actor_id or not line_id.isidentifier() or not actor_id.isidentifier():
            raise ValueError("UNSAFE_LINE_OR_ACTOR_ID")
        out=Path(output_dir).resolve()
        out.mkdir(parents=True,exist_ok=True)
        filename=f"{line_id}_{actor_id}"
        audio=out/f"{filename}.wav"
        events_path=out/f"{filename}.visemes.json"
        req_path=out/f"{filename}.request.json"
        req_path.write_text(json.dumps({
            "text":text,"voice":voice,
            "audio_path":str(audio),"events_path":str(events_path),
        }),encoding="utf-8")
        process=subprocess.run([
            "powershell.exe","-NoProfile","-ExecutionPolicy","Bypass",
            "-File",str(self.ps_script),"-RequestPath",str(req_path),
        ],capture_output=True,text=True,timeout=90,check=False)
        if process.returncode!=0:
            raise RuntimeError("LOCAL_SAPI_SYNTHESIS_FAILED:"+process.stderr[-600:])
        if not audio.is_file() or not events_path.is_file():
            raise RuntimeError("SAPI_EVIDENCE_OUTPUT_MISSING")
        obj=json.loads(events_path.read_text(encoding="utf-8-sig"))
        if obj.get("voice")!=voice or obj.get("text")!=text:
            raise RuntimeError("SAPI_EVIDENCE_IDENTITY_MISMATCH")
        digest=self._hash(audio)
        if digest!=obj.get("wav_sha256"):
            raise RuntimeError("SAPI_AUDIO_HASH_MISMATCH")
        probe=self.media.probe(audio)
        if probe.audio_codec is None or probe.duration<=0:
            raise RuntimeError("TTS_AUDIO_PROBE_FAILED")
        events=[SapiVisemeEvent.model_validate(e) for e in obj.get("viseme_events",[])]
        end=timeline_end_seconds if timeline_end_seconds is not None else (
            line_start_seconds+probe.duration+.16
        )
        return SpeechVisemeTrack(
            line_id=line_id,actor_id=actor_id,text=text,voice=voice,
            audio_path=str(audio),audio_sha256=digest,
            audio_duration_seconds=probe.duration,
            line_start_seconds=line_start_seconds,
            timeline_end_seconds=end,
            event_source=obj["event_source"],events=events,
        )

    def attach_to_shot(self, shot: object, tracks: list[SpeechVisemeTrack]) -> object:
        """Authorize real-source visemes on a typed shot; do not alter semantics."""
        available={a.actor_id for a in shot.actors}
        occupied: dict[str,float]={}
        for row in sorted(tracks,key=lambda item:item.line_start_seconds):
            if row.actor_id not in available:
                raise ValueError("SPEECH_ACTOR_NOT_IN_SHOT")
            if row.timeline_end_seconds > shot.duration_seconds + 1e-6:
                raise ValueError("SPEECH_AUDIO_EXCEEDS_SHOT")
            if row.line_start_seconds < occupied.get(row.actor_id,0.) - 1e-6:
                raise ValueError("SPEECH_OVERLAPPING_ACTOR_TURNS")
            occupied[row.actor_id]=row.timeline_end_seconds
            path=Path(row.audio_path).resolve()
            if not path.is_file() or self._hash(path)!=row.audio_sha256:
                raise ValueError("SPEECH_AUDIO_EVIDENCE_HASH_MISMATCH")
            probe=self.media.probe(path)
            if (probe.audio_codec is None
                or abs(probe.duration-row.audio_duration_seconds)>.04):
                raise ValueError("SPEECH_AUDIO_DURATION_OR_STREAM_INVALID")
            event_file=path.with_suffix(".visemes.json")
            if not event_file.is_file():
                raise ValueError("SPEECH_VISEME_EVENT_SOURCE_MISSING")
            source=json.loads(event_file.read_text(encoding="utf-8-sig"))
            source_events=[SapiVisemeEvent.model_validate(e) for e in source.get("viseme_events",[])]
            if not (source.get("wav_sha256")==row.audio_sha256
                    and source.get("voice")==row.voice
                    and source.get("text")==row.text
                    and source.get("event_source")==row.event_source
                    and source_events==row.events):
                raise ValueError("SPEECH_VISEME_EVENT_SOURCE_MISMATCH")
        return shot.model_copy(update={
            "creative_intent":{
                **dict(shot.creative_intent),
                "speech_viseme_tracks":[self.blender_cue(row) for row in tracks],
                "speech_viseme_source":"SAPI_SYNTHESIS_TIMING_NOT_INDEPENDENT_AUDIO_ALIGNMENT",
                "speech_viseme_production_qualified":False,
            },
        })

    @classmethod
    def blender_cue(cls, track: SpeechVisemeTrack) -> dict:
        # Consumer treats these approximate dimensions as animation, not QC.
        return {
            "line_id":track.line_id,"actor_id":track.actor_id,
            "audio_sha256":track.audio_sha256,
            "event_source":track.event_source,
            "line_start_seconds":track.line_start_seconds,
            "timeline_end_seconds":track.timeline_end_seconds,
            "audio_duration_seconds":track.audio_duration_seconds,
            "viseme_events":[{
                "time_seconds":event.time_seconds,
                "viseme":event.viseme,
                "jaw_open":cls.JAW_BY_SAPI[event.viseme],
                "mouth_width":cls.WIDTH_BY_SAPI[event.viseme],
            } for event in track.events],
        }
