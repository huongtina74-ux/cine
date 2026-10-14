from __future__ import annotations
"""Independent *dictation* ASR text check for actual WAV, not forced alignment.

Windows SpeechRecognitionEngine is distinct from SAPI synthesizer's
VisemeReached/SpeakProgress. Short utterances can score poorly; confidence
gates must reject low-confidence outputs even if the transcript is correct.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class IndependentASRWord(BaseModel):
    text: str
    lexical_form: str
    confidence: float = Field(ge=0,le=1)


class IndependentASRReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    source: str = "WINDOWS_SYSTEM_SPEECH_RECOGNITION_DICTATION"
    transcript_supplied_to_recognizer: bool = False
    independent_text_recognition_verified: bool = False
    independently_forced_aligned: bool = False
    phoneme_alignment_verified: bool = False
    recognized_transcript: str = ""
    expected_transcript: str
    confidence: float = 0.0
    confidence_floor: float
    words: list[IndependentASRWord] = Field(default_factory=list)
    audio_sha256: str | None = None
    blockers: list[str] = Field(default_factory=list)


class OfflineIndependentASR:
    def __init__(self,root: str|Path,*,confidence_floor:float=.55) -> None:
        self.root=Path(root).resolve()
        self.confidence_floor=confidence_floor
        if not 0<=confidence_floor<=1:
            raise ValueError("ASR_CONFIDENCE_FLOOR_INVALID")

    @staticmethod
    def normalize(text:str)->list[str]:
        return re.findall(r"[^\W_]+(?:['’-][^\W_]+)*",text.casefold(),flags=re.UNICODE)

    def assess(self,*,source_wav:str|Path,source_sha256:str,
               expected_transcript:str,output_json:str|Path)->IndependentASRReport:
        source=Path(source_wav).resolve()
        if not source.is_file():
            raise ValueError("INDEPENDENT_ASR_WAV_MISSING")
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if digest!=source_sha256:
            raise ValueError("INDEPENDENT_ASR_SOURCE_WAV_TAMPERED")
        report_path=Path(output_json).resolve()
        report_path.parent.mkdir(parents=True,exist_ok=True)
        script=self.root/"scripts"/"windows_asr_independent.ps1"
        if not script.is_file():
            raise RuntimeError("WINDOWS_ASR_SCRIPT_MISSING")
        job=subprocess.run([
            "powershell.exe","-NoProfile","-NonInteractive",
            "-ExecutionPolicy","Bypass","-File",str(script),
            "-InputWav",str(source),"-OutputJson",str(report_path),
        ],capture_output=True,text=True,check=False,timeout=45)
        if job.returncode or not report_path.is_file():
            return IndependentASRReport(
                status="BLOCKED",passed=False,measured=False,
                expected_transcript=expected_transcript,
                confidence_floor=self.confidence_floor,audio_sha256=digest,
                blockers=["INDEPENDENT_ASR_RUNTIME_UNAVAILABLE"],
            )
        response=json.loads(report_path.read_text(encoding="utf-8-sig"))
        if response.get("source_sha256")!=digest:
            raise ValueError("INDEPENDENT_ASR_OUTPUT_SOURCE_HASH_MISMATCH")
        if response.get("source")!="WINDOWS_SYSTEM_SPEECH_RECOGNITION_DICTATION":
            raise ValueError("INDEPENDENT_ASR_EVIDENCE_PROVENANCE_INVALID")
        if response.get("transcript_supplied_to_recognizer") is not False:
            raise ValueError("TRANSCRIPT_CONDITIONED_ASR_NOT_INDEPENDENT")
        recognized=str(response.get("transcript",""))
        confidence=float(response.get("confidence",0.))
        if not 0<=confidence<=1:
            raise ValueError("ASR_CONFIDENCE_OUTSIDE_RANGE")
        words=[IndependentASRWord.model_validate(row) for row in response.get("words",[])]
        problems=[]
        if not response.get("recognized"):
            problems.append("INDEPENDENT_RECOGNITION_EMPTY")
        if self.normalize(recognized)!=self.normalize(expected_transcript):
            problems.append("INDEPENDENT_RECOGNIZED_TEXT_MISMATCH")
        if confidence<self.confidence_floor:
            problems.append("INDEPENDENT_RECOGNITION_LOW_CONFIDENCE")
        if not words:
            problems.append("INDEPENDENT_RECOGNITION_WORDS_MISSING")
        # DictationGrammar output has no word time offsets.
        if response.get("time_aligned_words_available") is not False:
            raise ValueError("UNSUPPORTED_ASR_WORD_TIMING_CLAIM")
        if response.get("forced_phoneme_alignment_verified") is not False:
            raise ValueError("UNSUPPORTED_PHONEME_ALIGNMENT_CLAIM")
        return IndependentASRReport(
            status="INDEPENDENT_DICTATION_TEXT_PASS" if not problems else "BLOCKED",
            passed=not problems,measured=bool(response.get("recognized")),
            independent_text_recognition_verified=not problems,
            expected_transcript=expected_transcript,
            recognized_transcript=recognized,confidence=confidence,
            confidence_floor=self.confidence_floor,
            words=words,audio_sha256=digest,blockers=problems,
        )
