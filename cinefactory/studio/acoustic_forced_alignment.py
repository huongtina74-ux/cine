from __future__ import annotations
"""v1.6.28 real acoustic forced alignment (PocketSphinx HMM).

Acoustic phone *timings* are estimated from real decoded audio by a local
trained model, conditioned on the provided words/lexicon. The phone labels
are from CMUDict, not an independently recognized transcript or proof of
correct pronunciation. Never claim visual phoneme sync or production release.
"""
import hashlib
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field


class AcousticPhone(BaseModel):
    word_index: int
    word: str
    phone: str
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(ge=0)


class AcousticWord(BaseModel):
    word: str
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(ge=0)
    phones: list[AcousticPhone] = Field(default_factory=list)


class AcousticAlignmentReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    alignment_method: str = "POCKETSPHINX_EN_US_HMM_TWO_PASS_LEXICON_CONDITIONED"
    independent_audio_acoustic_timing: bool = False
    transcript_conditioned: bool = True
    phone_labels_from_lexicon: bool = True
    independent_phoneme_recognition_verified: bool = False
    visual_phoneme_sync_verified: bool = False
    audio_sha256: str | None = None
    audio_seconds: float = 0.
    phones: list[AcousticPhone] = Field(default_factory=list)
    words: list[AcousticWord] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class PocketSphinxAcousticAligner:
    def __init__(self,root: str|Path,*,speech_rms_floor:float=.007,
                 frame_rate:int=100):
        self.root=Path(root).resolve()
        self.speech_rms_floor=speech_rms_floor
        self.frame_rate=frame_rate

    def _load_engine(self):
        site=self.root/".tools"/"pocketsphinx_lib"
        if not (site/"pocketsphinx").is_dir():
            raise RuntimeError("POCKETSPHINX_LOCAL_MODEL_NOT_INSTALLED")
        if str(site) not in sys.path:
            sys.path.insert(0,str(site))
        from pocketsphinx import Decoder
        return Decoder

    @staticmethod
    def normalize(transcript: str) -> list[str]:
        return re.findall(r"[a-z]+(?:'[a-z]+)?",transcript.lower())

    @staticmethod
    def _pcm(path:Path)->bytes:
        proc=subprocess.run([
            "ffmpeg","-nostdin","-v","error",
            "-i",str(path),"-map","0:a:0","-vn",
            "-ac","1","-ar","16000","-acodec","pcm_s16le",
            "-f","s16le","pipe:1",
        ],capture_output=True,timeout=45,check=False)
        if proc.returncode or not proc.stdout:
            raise RuntimeError("ACOUSTIC_PCM_DECODE_FAILED")
        return proc.stdout

    def align(self,*,audio_path:str|Path,audio_sha256:str,
              transcript:str)->AcousticAlignmentReport:
        path=Path(audio_path).resolve()
        if not path.is_file():
            raise ValueError("ACOUSTIC_ALIGNMENT_AUDIO_MISSING")
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=audio_sha256:
            raise ValueError("ACOUSTIC_ALIGNMENT_SHA256_MISMATCH")
        pcm=self._pcm(path)
        duration=len(pcm)/32000.
        signal=np.frombuffer(pcm,dtype="<i2").astype(np.float64)/32768.
        rms=float(np.sqrt(np.mean(signal*signal)))
        words=self.normalize(transcript)
        problems=[]
        if not words:
            problems.append("ACOUSTIC_ALIGNMENT_TRANSCRIPT_EMPTY")
        if rms<self.speech_rms_floor:
            problems.append("ACOUSTIC_ALIGNMENT_AUDIO_SILENT")
        if duration<.2:
            problems.append("ACOUSTIC_ALIGNMENT_AUDIO_TOO_SHORT")
        if problems:
            return AcousticAlignmentReport(
                status="BLOCKED",passed=False,measured=False,
                audio_sha256=actual,audio_seconds=duration,
                blockers=problems,
            )
        Decoder=self._load_engine()
        decoder=Decoder(lm=None,loglevel="ERROR")
        unknown=[word for word in words if decoder.lookup_word(word) is None]
        if unknown:
            return AcousticAlignmentReport(
                status="BLOCKED",passed=False,measured=False,
                audio_sha256=actual,audio_seconds=duration,
                blockers=["ALIGNMENT_DICTIONARY_WORD_UNKNOWN:"+word for word in unknown],
            )
        try:
            decoder.set_align_text(" ".join(words))
            decoder.start_utt()
            decoder.process_raw(pcm,full_utt=True)
            decoder.end_utt()
            decoder.set_alignment()
            decoder.start_utt()
            decoder.process_raw(pcm,full_utt=True)
            decoder.end_utt()
            hierarchy=decoder.get_alignment()
            if hierarchy is None:
                raise RuntimeError("POCKETSPHINX_NO_SUBWORD_ALIGNMENT")
            aligned_words=[]
            phonemes=[]
            for w in hierarchy:
                word_label=str(w.name).lower().split("(")[0]
                if word_label in ("<sil>","<s>","</s>"):
                    continue
                index=len(aligned_words)
                local=[]
                for phone in w:
                    start=float(phone.start)/self.frame_rate
                    end=float(phone.start+phone.duration)/self.frame_rate
                    item=AcousticPhone(
                        word_index=index,word=word_label,
                        phone=str(phone.name).upper(),
                        start_seconds=start,end_seconds=end,
                    )
                    local.append(item)
                    phonemes.append(item)
                aligned_words.append(AcousticWord(
                    word=word_label,start_seconds=float(w.start)/self.frame_rate,
                    end_seconds=float(w.start+w.duration)/self.frame_rate,
                    phones=local,
                ))
        except (RuntimeError,ValueError) as exc:
            return AcousticAlignmentReport(
                status="BLOCKED",passed=False,measured=False,
                audio_sha256=actual,audio_seconds=duration,
                blockers=["ACOUSTIC_MODEL_ALIGNMENT_FAILED:"+type(exc).__name__],
            )
        if [w.word for w in aligned_words]!=words:
            problems.append("FORCED_ALIGNMENT_WORD_SEQUENCE_INVALID")
        if not phonemes:
            problems.append("PHONEME_EVIDENCE_MISSING")
        for w in aligned_words:
            if not w.phones:
                problems.append("WORD_WITHOUT_PHONES:"+w.word)
            if not 0<=w.start_seconds<w.end_seconds<=duration+.08:
                problems.append("WORD_TIME_OUT_OF_AUDIO:"+w.word)
            if w.phones and (abs(w.phones[0].start_seconds-w.start_seconds)>.03
                             or abs(w.phones[-1].end_seconds-w.end_seconds)>.03):
                problems.append("SUBWORD_TIMING_NOT_CONTIGUOUS:"+w.word)
        previous=0.
        for p in phonemes:
            if not previous-.03<=p.start_seconds<p.end_seconds<=duration+.08:
                problems.append("PHONE_TIME_OUT_OF_RANGE_OR_ORDER")
                break
            previous=p.end_seconds
        # Check gross audio energy in the union of speech words. The forced
        # decoder by itself can align totally unrelated or silent audio.
        if aligned_words:
            hits=0
            for w in aligned_words:
                a=min(len(signal),int(w.start_seconds*16000))
                b=min(len(signal),int(w.end_seconds*16000))
                energy=float(np.sqrt(np.mean(signal[a:b]**2))) if b>a else 0.
                hits+=int(energy>=self.speech_rms_floor)
            if hits!=len(aligned_words):
                problems.append("FORCED_WORD_AUDIO_ENERGY_MISSING")
        return AcousticAlignmentReport(
            status="ACOUSTIC_FORCED_PHONE_TIMING_PASS" if not problems else "BLOCKED",
            passed=not problems,measured=bool(phonemes),
            independent_audio_acoustic_timing=bool(phonemes),
            audio_sha256=actual,audio_seconds=duration,
            words=aligned_words,phones=phonemes,
            blockers=sorted(set(problems)),
        )
