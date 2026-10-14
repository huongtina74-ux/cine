from __future__ import annotations

"""v1.6.23 *envelope-level* measured audio/video mouth-motion verification.

This does not perform speech recognition, phoneme/viseme classification, speaker
diarization, or certify real lip-sync. Requires audio encoded in the actual
video and an approved actor-bound on-screen mouth ROI.
"""
import math
import subprocess
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field, model_validator

from cinefactory.media.ffmpeg import FFmpegToolchain


class MouthRegion(BaseModel):
    actor_id: str
    box: dict[str, float]
    provenance: Literal["trusted_rig_projection", "human_approved"] = "human_approved"

    @model_validator(mode="after")
    def valid(self):
        b = self.box
        if not all(k in b for k in ("x0", "x1", "y0", "y1")):
            raise ValueError("mouth region missing screen coordinates")
        if not (0 <= b["x0"] < b["x1"] <= 1 and 0 <= b["y0"] < b["y1"] <= 1):
            raise ValueError("mouth region outside normalized image")
        return self


class SpeakerWindow(BaseModel):
    line_id: str
    actor_id: str
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)

    @model_validator(mode="after")
    def timing(self):
        if self.end_seconds <= self.start_seconds:
            raise ValueError("speaker window end before start")
        return self


class EnvelopeAlignmentCheck(BaseModel):
    line_id: str
    actor_id: str
    passed: bool = False
    measured: bool = False
    best_offset_seconds: float | None = None
    envelope_correlation: float | None = None
    audio_rms_peak: float | None = None
    mouth_motion_range: float | None = None
    sample_count: int = 0
    findings: list[str] = Field(default_factory=list)


class AudioVisualSyncReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    audio_lipsync_measured: bool = False  # phoneme/viseme lip-sync remains unmeasured
    measurement_kind: str = "AUDIO_ENVELOPE_VS_MOUTH_DARK_PIXEL_ACTIVITY"
    phoneme_alignment_verified: bool = False
    source_media_path: str | None = None
    source_media_sha256: str | None = None
    checks: list[EnvelopeAlignmentCheck] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class AudioVisualSyncVerifier:
    @staticmethod
    def windows_from_dialogue(compilation: object) -> list[SpeakerWindow]:
        """Use locked, valid semantic speaker turns; never infer attribution."""
        from cinefactory.studio.dialogue_performance import DialogueRole
        qc = getattr(compilation, "qc", None)
        if qc is None or not qc.passed:
            raise ValueError("DIALOGUE_SEMANTIC_QC_NOT_PASSED")
        turns = [
            SpeakerWindow(
                line_id=directive.line_id,
                actor_id=directive.actor_id,
                start_seconds=directive.start_seconds,
                end_seconds=directive.end_seconds,
            )
            for directive in compilation.directives
            if directive.role is DialogueRole.SPEAKER
        ]
        if not turns:
            raise ValueError("NO_SPEAKER_DIRECTIVES")
        return turns

    def __init__(
        self, *, sample_fps: int = 20, max_offset_seconds: float = 0.12,
        minimum_correlation: float = 0.55, maximum_duration_seconds: float = 30.0,
    ) -> None:
        self.sample_fps = sample_fps
        self.max_offset_seconds = max_offset_seconds
        self.minimum_correlation = minimum_correlation
        self.maximum_duration_seconds = maximum_duration_seconds
        self.media = FFmpegToolchain()

    @staticmethod
    def _failure(reason: str, path: Path) -> AudioVisualSyncReport:
        return AudioVisualSyncReport(
            status="BLOCKED",passed=False,measured=False,
            source_media_path=str(path),
            blockers=[reason],
        )

    @staticmethod
    def _decode_audio(path: Path) -> np.ndarray:
        process = subprocess.run([
            "ffmpeg","-nostdin","-v","error","-i",str(path),
            "-map","0:a:0","-vn","-ac","1","-ar","8000",
            "-f","s16le","-acodec","pcm_s16le","pipe:1",
        ], capture_output=True, timeout=35, check=False)
        if process.returncode != 0:
            raise RuntimeError("AUDIO_DECODE_FAILED")
        return np.frombuffer(process.stdout, dtype="<i2").astype(np.float32)/32768.

    @staticmethod
    def _mouth_dark_fraction(frame: np.ndarray, region: MouthRegion) -> float:
        import cv2
        height, width = frame.shape[:2]
        box = region.box
        x0 = round(box["x0"]*width)
        x1 = round(box["x1"]*width)
        y0 = round(box["y0"]*height)
        y1 = round(box["y1"]*height)
        patch = frame[y0:y1,x0:x1]
        if patch.size == 0:
            return float("nan")
        grey = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        return float(np.mean(grey < 85))

    def _video_activity(
        self, path: Path, regions: dict[str,MouthRegion],
    ) -> tuple[np.ndarray,dict[str,np.ndarray]]:
        import cv2
        cap = cv2.VideoCapture(str(path))
        try:
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            if fps <= 0:
                raise RuntimeError("VIDEO_FPS_INVALID")
            times: list[float] = []
            signals: dict[str,list[float]] = {a:[] for a in regions}
            count = 0
            next_sample = 0.
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                second = count / fps
                count += 1
                if second + 1e-6 < next_sample:
                    continue
                times.append(second)
                for actor, region in regions.items():
                    signals[actor].append(self._mouth_dark_fraction(frame,region))
                next_sample += 1. / self.sample_fps
            return np.asarray(times,dtype=float),{
                key: np.asarray(value,dtype=float)
                for key,value in signals.items()
            }
        finally:
            cap.release()

    @staticmethod
    def _energy_at(audio: np.ndarray, times: np.ndarray) -> np.ndarray:
        rate = 8000
        radius = round(.030 * rate)
        values = np.zeros(len(times),dtype=float)
        for index, second in enumerate(times):
            center = round(float(second)*rate)
            start = max(0, center-radius)
            end = min(len(audio), center+radius)
            if end > start:
                block = audio[start:end]
                values[index] = float(np.sqrt(np.mean(block*block)))
        return values

    def verify(
        self, *, media_path: str | Path,
        turns: list[SpeakerWindow],
        mouth_regions: list[MouthRegion],
    ) -> AudioVisualSyncReport:
        import hashlib
        path = Path(media_path).resolve()
        if not path.is_file():
            return self._failure("MEDIA_MISSING",path)
        regions = {r.actor_id:r for r in mouth_regions}
        if len(regions) != len(mouth_regions):
            return self._failure("DUPLICATE_MOUTH_REGION_ACTOR",path)
        if not turns:
            return self._failure("SPEAKER_WINDOWS_MISSING",path)
        if len(set(w.line_id for w in turns)) != len(turns):
            return self._failure("DUPLICATE_LINE_ID",path)
        if any(w.actor_id not in regions for w in turns):
            return self._failure("MOUTH_REGION_MISSING_FOR_SPEAKER",path)
        ordered = sorted(turns,key=lambda w:w.start_seconds)
        if any(a.end_seconds > b.start_seconds + 1e-9 for a,b in zip(ordered,ordered[1:])):
            return self._failure("OVERLAPPING_SPEAKER_WINDOWS_MIX_UNATTRIBUTABLE",path)
        try:
            probe = self.media.probe(path)
        except (RuntimeError,ValueError,OSError):
            return self._failure("MEDIA_PROBE_FAILED",path)
        if probe.audio_codec is None:
            return self._failure("ACTUAL_AUDIO_TRACK_REQUIRED",path)
        if probe.width is None or probe.height is None or not probe.fps:
            return self._failure("ACTUAL_VIDEO_TRACK_REQUIRED",path)
        if not .3 < probe.duration <= self.maximum_duration_seconds:
            return self._failure("MEDIA_DURATION_OUTSIDE_LIMITS",path)
        if any(w.end_seconds > probe.duration + 1e-6 for w in turns):
            return self._failure("SPEAKER_WINDOW_OUTSIDE_MEDIA",path)
        try:
            times, signals = self._video_activity(path,regions)
            audio = self._decode_audio(path)
        except (RuntimeError,OSError,subprocess.TimeoutExpired):
            return self._failure("MEDIA_DECODING_FAILED",path)
        if len(times) < 6 or len(audio) < 8000*.2:
            return self._failure("AUDIO_VIDEO_SAMPLES_INSUFFICIENT",path)
        checks: list[EnvelopeAlignmentCheck] = []
        max_lag = .35
        for window in turns:
            mask = (times >= window.start_seconds) & (times < window.end_seconds)
            t = times[mask]
            mouth = signals[window.actor_id][mask]
            findings: list[str] = []
            if len(t) < 10 or np.any(~np.isfinite(mouth)):
                findings.append("MOUTH_SAMPLES_INSUFFICIENT")
            mouth_range = float(np.ptp(mouth)) if len(mouth) else 0.
            audio_base = self._energy_at(audio,t)
            audio_peak = float(np.max(audio_base)) if len(audio_base) else 0.
            if mouth_range < .15:
                findings.append("MOUTH_VISUAL_ACTIVITY_INSUFFICIENT")
            if audio_peak < .012:
                findings.append("AUDIO_SPEECH_ENVELOPE_INSUFFICIENT")
            best_score = -1.
            best_offset = None
            if not findings and np.std(mouth) > .015:
                step = 1./self.sample_fps
                for lag in np.arange(-max_lag,max_lag+step/2,step):
                    shifted = t + lag
                    available = (shifted >= 0) & (shifted <= probe.duration)
                    if available.sum() < 10:
                        continue
                    voice = self._energy_at(audio,shifted[available])
                    moving = mouth[available]
                    if np.std(voice) < .006:
                        continue
                    corr = float(np.corrcoef(moving,voice)[0,1])
                    if np.isfinite(corr) and corr > best_score:
                        best_score = corr
                        best_offset = float(lag)
                if best_offset is None or best_score < self.minimum_correlation:
                    findings.append("AUDIO_MOUTH_ENVELOPE_CORRELATION_LOW")
                elif abs(best_offset) > self.max_offset_seconds+1e-6:
                    findings.append("AUDIO_MOUTH_OFFSET_TOO_LARGE")
            checks.append(EnvelopeAlignmentCheck(
                line_id=window.line_id,actor_id=window.actor_id,
                passed=not findings,measured=not (
                    "MOUTH_SAMPLES_INSUFFICIENT" in findings
                    or "AUDIO_SPEECH_ENVELOPE_INSUFFICIENT" in findings
                ),
                best_offset_seconds=best_offset,
                envelope_correlation=best_score if best_score>=0 else None,
                audio_rms_peak=audio_peak,
                mouth_motion_range=mouth_range,
                sample_count=len(t),findings=findings,
            ))
        blockers = sorted({
            f"{row.line_id}:{issue}" for row in checks for issue in row.findings
        })
        h=hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda:stream.read(1<<20),b""):
                h.update(chunk)
        return AudioVisualSyncReport(
            status="ENVELOPE_ONLY_PASS" if not blockers else "BLOCKED",
            passed=not blockers, measured=any(c.measured for c in checks),
            production_qualified=False,
            audio_lipsync_measured=False,
            phoneme_alignment_verified=False,
            source_media_path=str(path),
            source_media_sha256=h.hexdigest(),
            checks=checks,blockers=blockers,
        )


class PerformanceProductionDecision(BaseModel):
    passed: bool
    status: str
    blockers: list[str] = Field(default_factory=list)


class PerformanceQualificationGate:
    """Fail closed: diagnostic metrics never silently qualify production."""

    @staticmethod
    def assess(
        *, temporal: object | None,
        sync: AudioVisualSyncReport | None,
        identity_required: bool = True,
        lipsync_required: bool = True,
        v185_required: bool = False,
        audio_word_reports: list[object] | None = None,
        mouth_pixels: object | None = None,
        multi_seed: object | None = None,
        v186_required: bool = False,
        speaker_source: object | None = None,
        image_mouth: object | None = None,
        real_multishot: object | None = None,
        mouth_rig_agreement: object | None = None,
        v187_required: bool = False,
        independent_asr_reports: list[object] | None = None,
        final_mux_asr_reports: list[object] | None = None,
        full_frame_actor: object | None = None,
        full_frame_annotated_benchmark: object | None = None,
        v188_required: bool = False,
        phoneme_audio: dict[str,object] | None = None,
        phoneme_video_proxy: object | None = None,
        trained_actor_detector: object | None = None,
        v189_required: bool = False,
        blender_mask_dataset: object | None = None,
        diverse_scene_detector: object | None = None,
        independent_human_detector_review: object | None = None,
        v190_required: bool = False,
        actual_rig_dataset: object | None = None,
        real_rig_domain: object | None = None,
        human_approved_dataset: object | None = None,
    ) -> PerformanceProductionDecision:
        blockers: list[str] = []
        if identity_required:
            if temporal is None or not bool(getattr(temporal,"measured",False)):
                blockers.append("TEMPORAL_ACTOR_EVIDENCE_MISSING")
            elif not bool(getattr(temporal,"passed",False)):
                blockers.append("TEMPORAL_REID_QC_FAILED")
            if temporal is None or not bool(getattr(temporal,"production_qualified",False)):
                blockers.append("TEMPORAL_REID_PRODUCTION_NOT_QUALIFIED")
        if lipsync_required:
            if sync is None or not sync.measured:
                blockers.append("AUDIO_VIDEO_LIPSYNC_EVIDENCE_MISSING")
            elif not sync.passed:
                blockers.append("AUDIO_VIDEO_ENVELOPE_QC_FAILED")
            if sync is None or not (
                sync.production_qualified
                and sync.audio_lipsync_measured
                and sync.phoneme_alignment_verified
            ):
                blockers.append("PHONEME_VISEME_LIPSYNC_NOT_QUALIFIED")
        if v185_required:
            word_reports=audio_word_reports or []
            if not word_reports or any(
                not bool(getattr(item,"passed",False)) for item in word_reports
            ):
                blockers.append("REAL_AUDIO_WORD_CONSISTENCY_FAILED_OR_MISSING")
            if not word_reports or any(
                not bool(getattr(item,"production_qualified",False))
                for item in word_reports
            ):
                blockers.append("INDEPENDENT_FORCED_ALIGNMENT_UNQUALIFIED")
            if mouth_pixels is None or not bool(getattr(mouth_pixels,"passed",False)):
                blockers.append("RENDERED_MOUTH_PIXEL_QC_FAILED_OR_MISSING")
            if mouth_pixels is None or not bool(getattr(mouth_pixels,"production_qualified",False)):
                blockers.append("RENDERED_PHONEME_SHAPES_UNQUALIFIED")
            if multi_seed is None or not bool(getattr(multi_seed,"passed",False)):
                blockers.append("MULTISEED_IDENTITY_BENCHMARK_FAILED_OR_MISSING")
            if multi_seed is None or not bool(getattr(multi_seed,"production_qualified",False)):
                blockers.append("MULTISEED_REAL_VIDEO_IDENTITY_UNQUALIFIED")
        if v186_required:
            if speaker_source is None or not bool(getattr(speaker_source,"passed",False)):
                blockers.append("KNOWN_SOURCE_SPEAKER_ATTRIBUTION_FAILED")
            if speaker_source is None or not (
                getattr(speaker_source,"production_qualified",False)
                and getattr(speaker_source,"independent_diarization_verified",False)
            ):
                blockers.append("INDEPENDENT_DIARIZATION_NOT_QUALIFIED")
            if image_mouth is None or not bool(getattr(image_mouth,"passed",False)):
                blockers.append("IMAGE_ONLY_FACE_MOUTH_OBSERVABILITY_FAILED")
            if image_mouth is None or not (
                getattr(image_mouth,"production_qualified",False)
                and getattr(image_mouth,"independent_face_landmarks_verified",False)
            ):
                blockers.append("FACE_LANDMARK_OBSERVABILITY_NOT_QUALIFIED")
            if mouth_rig_agreement is None or not bool(getattr(mouth_rig_agreement,"passed",False)):
                blockers.append("IMAGE_RIG_MOUTH_LOCALIZATION_DISAGREES_OR_MISSING")
            if mouth_rig_agreement is None or not bool(getattr(mouth_rig_agreement,"production_qualified",False)):
                blockers.append("HUMAN_GROUNDED_MOUTH_LANDMARKS_UNQUALIFIED")
            if real_multishot is None or not bool(getattr(real_multishot,"passed",False)):
                blockers.append("REAL_TWO_SHOT_APPEARANCE_IDENTITY_FAILED")
            if real_multishot is None or not bool(getattr(real_multishot,"production_qualified",False)):
                blockers.append("REAL_MULTISHOT_UNCONSTRAINED_REID_NOT_QUALIFIED")
        if v187_required:
            if full_frame_actor is None or not bool(getattr(full_frame_actor,"passed",False)):
                blockers.append("FULL_FRAME_REFERENCE_ACTOR_TRACKING_FAILED")
            if full_frame_actor is None or not bool(
                getattr(full_frame_actor,"production_qualified",False)
            ):
                blockers.append("UNCONSTRAINED_ACTOR_DETECTOR_NOT_QUALIFIED")
            if full_frame_annotated_benchmark is None or not bool(
                getattr(full_frame_annotated_benchmark,"passed",False)
            ):
                blockers.append("REAL_VIDEO_FRAME_BENCHMARK_FAILED")
            if full_frame_annotated_benchmark is None or not bool(
                getattr(full_frame_annotated_benchmark,"production_qualified",False)
            ):
                blockers.append("INDEPENDENT_HUMAN_VIDEO_GROUND_TRUTH_NOT_QUALIFIED")
            independent=independent_asr_reports or []
            if not independent or any(not bool(getattr(x,"passed",False)) for x in independent):
                blockers.append("INDEPENDENT_SPEECH_RECOGNITION_FAILED_OR_LOW_CONFIDENCE")
            final_speech=final_mux_asr_reports or []
            if not final_speech or any(not bool(getattr(x,"passed",False)) for x in final_speech):
                blockers.append("FINAL_MUX_INDEPENDENT_SPEECH_RECOGNITION_FAILED")
            if not independent or any(not (
                getattr(x,"phoneme_alignment_verified",False)
                and getattr(x,"production_qualified",False)
            ) for x in independent):
                blockers.append("INDEPENDENT_FORCED_PHONEME_ALIGNMENT_NOT_QUALIFIED")
        if v188_required:
            source_asr=independent_asr_reports or []
            final_asr=final_mux_asr_reports or []
            if not source_asr or any(not bool(getattr(r,"passed",False)) for r in source_asr):
                blockers.append("ACOUSTIC_ALIGNMENT_SOURCE_ASR_INDEPENDENCE_NOT_VERIFIED")
            if not final_asr or any(not bool(getattr(r,"passed",False)) for r in final_asr):
                blockers.append("ACOUSTIC_ALIGNMENT_FINAL_ASR_INDEPENDENCE_NOT_VERIFIED")
            acoustic=phoneme_audio or {}
            if not acoustic or any(not bool(getattr(x,"passed",False))
                                   for x in acoustic.values()):
                blockers.append("REAL_AUDIO_ACOUSTIC_PHONE_ALIGNMENT_FAILED")
            if not acoustic or any(not bool(getattr(x,"independent_audio_acoustic_timing",False))
                                   for x in acoustic.values()):
                blockers.append("INDEPENDENT_AUDIO_PHONE_TIMINGS_MISSING")
            if not acoustic or any(not (
                    getattr(x,"production_qualified",False)
                    and getattr(x,"independent_phoneme_recognition_verified",False)
                ) for x in acoustic.values()):
                blockers.append("LEXICON_CONDITIONED_PHONEME_GROUND_TRUTH_UNQUALIFIED")
            if phoneme_video_proxy is None or not bool(getattr(phoneme_video_proxy,"passed",False)):
                blockers.append("ACOUSTIC_PHONE_PIXEL_MOUTH_PROXY_FAILED")
            if phoneme_video_proxy is None or not (
                getattr(phoneme_video_proxy,"production_qualified",False)
                and getattr(phoneme_video_proxy,"phoneme_shapes_independently_validated",False)
            ):
                blockers.append("PHONEME_TO_MOUTH_SHAPES_NOT_HUMAN_VALIDATED")
            if trained_actor_detector is None or not bool(
                getattr(trained_actor_detector,"passed",False)
            ):
                blockers.append("TRAINED_HELDOUT_ACTOR_DETECTOR_FAILED")
            if trained_actor_detector is None or not (
                getattr(trained_actor_detector,"production_qualified",False)
                and getattr(trained_actor_detector,"general_out_of_domain_actor_detection_verified",False)
            ):
                blockers.append("CROSS_DOMAIN_ACTOR_DETECTION_NOT_QUALIFIED")
        if v189_required:
            if blender_mask_dataset is None or not bool(getattr(blender_mask_dataset,"passed",False)):
                blockers.append("BLENDER_PIXEL_MASK_DATASET_QC_FAILED")
            if diverse_scene_detector is None or not bool(getattr(diverse_scene_detector,"passed",False)):
                blockers.append("DIVERSE_SCENE_HELDOUT_DETECTOR_QC_FAILED")
            if diverse_scene_detector is None or not (
                getattr(diverse_scene_detector,"production_qualified",False)
                and getattr(diverse_scene_detector,"generalized_real_video_detection_qualified",False)
            ):
                blockers.append("REAL_UNSEEN_STYLE_DETECTOR_GENERALIZATION_UNQUALIFIED")
            if independent_human_detector_review is None or not (
                getattr(independent_human_detector_review,"approved",False)
                and getattr(independent_human_detector_review,"production_qualified",False)
            ):
                blockers.append("INDEPENDENT_HUMAN_ACTOR_LABEL_REVIEW_MISSING")
        if v190_required:
            if actual_rig_dataset is None or not bool(
                getattr(actual_rig_dataset,"passed",False)
            ):
                blockers.append("ACTUAL_CINEFACTORY_WORKER_RIG_DATASET_FAILED")
            if real_rig_domain is None or not bool(
                getattr(real_rig_domain,"passed",False)
            ):
                blockers.append("REAL_RIG_EXTERNAL_VIDEO_GENERALIZATION_FAILED")
            if real_rig_domain is None or not (
                getattr(real_rig_domain,"production_qualified",False)
                and getattr(real_rig_domain,"generalization_to_multiple_independent_projects_verified",False)
            ):
                blockers.append("MULTIPROJECT_REAL_RIG_GENERALIZATION_UNQUALIFIED")
            if human_approved_dataset is None or not (
                getattr(human_approved_dataset,"approved",False)
                and getattr(human_approved_dataset,"production_qualified",False)
            ):
                blockers.append("HUMAN_APPROVED_ACTOR_MASKS_MISSING")
            if real_rig_domain is None or not getattr(
                real_rig_domain,"license_approved_for_commercial_distribution",False
            ):
                blockers.append("DETECTOR_COMMERCIAL_LICENSE_NOT_APPROVED")
        return PerformanceProductionDecision(
            passed=not blockers,
            status="QUALIFIED" if not blockers else "BLOCKED",
            blockers=sorted(set(blockers)),
        )
