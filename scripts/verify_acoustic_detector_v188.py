from __future__ import annotations
"""Real two-pass phoneme alignment, final-MP4 proxy lip-sync and YOLO benchmark.

Only downstream diagnostics are qualified. Production remains fail-closed:
lexicon-conditioned phones, no human mouth labels, controlled same-scene
Blender domain, and Ultralytics licensing pending for business deployment.
"""
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
OUT=ROOT/"data"/"verification"/"v188_acoustic_detector"

from cinefactory.studio.acoustic_forced_alignment import PocketSphinxAcousticAligner
from cinefactory.studio.phoneme_video_proxy_qc import PhonemeVideoProxyQC
from cinefactory.studio.rendered_mouth_qc import RenderedMouthSample,RenderedMouthProjectionQC
from cinefactory.studio.trained_actor_detector_qc import HeldoutActorDetectorEvaluator
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate
from cinefactory.studio.independent_speech_asr import IndependentASRReport


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mux_audio_window(media:Path,start:float,duration:float,output:Path)->None:
    proc=subprocess.run([
        "ffmpeg","-nostdin","-v","error","-y",
        "-i",str(media),"-ss",str(start),"-t",str(duration),
        "-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",str(output),
    ],capture_output=True,timeout=40,check=False)
    if proc.returncode or not output.is_file():
        raise RuntimeError("FINAL_MUX_WINDOW_EXTRACTION_FAILED")


def silence_fixture(out:Path)->Path:
    dest=out/"NEGATIVE_SILENCE.wav"
    with wave.open(str(dest),"wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(bytes(16000*2))
    return dest


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    evidence={"milestone":"v1.6.28","status":"STARTED","production_qualified":False}
    result=OUT/"v188_qualification_evidence.json"
    try:
        first=json.loads((ROOT/"data"/"verification"/"v185_alignment_reid"/"v185_render_evidence.json").read_text(encoding="utf-8"))
        second=json.loads((ROOT/"data"/"verification"/"v186_multishot_second"/"v186_render_evidence.json").read_text(encoding="utf-8"))
        original=Path(first["blender"]["path"])
        heldout=Path(second["blender"]["path"])
        final=Path(first["speech_video"]["path"])
        for path,expected in [
            (original,first["blender"]["sha256"]),
            (heldout,second["blender"]["sha256"]),
            (final,first["speech_video"]["sha256"]),
        ]:
            if not path.is_file() or sha(path)!=expected:
                raise RuntimeError("VIDEO_SOURCE_SHA_MISMATCH")
        side=json.loads(Path(str(original)+".geometry_qc.json").read_text(encoding="utf-8"))
        projected=[
            RenderedMouthSample.model_validate(row)
            for row in side["mouth_projection"]
        ]
        video_pixels=RenderedMouthProjectionQC().evaluate(video_path=final,samples=projected)
        assert video_pixels.passed,video_pixels.blockers

        aligner=PocketSphinxAcousticAligner(ROOT)
        source_alignments={}
        final_alignments={}
        starts={}
        timing_differences={}
        for speech in first["speech"]:
            aid=speech["actor_id"]
            starts[aid]=float(speech["line_start_seconds"])
            wav=Path(speech["audio_path"])
            result1=aligner.align(
                audio_path=wav,audio_sha256=speech["audio_sha256"],
                transcript=speech["text"],
            )
            window=OUT/(aid+"_FINAL_MUX_AUDIO.wav")
            mux_audio_window(final,starts[aid],speech["audio_duration_seconds"],window)
            result2=aligner.align(
                audio_path=window,audio_sha256=sha(window),
                transcript=speech["text"],
            )
            source_alignments[aid]=result1
            final_alignments[aid]=result2
            if not result1.passed or not result2.passed:
                raise RuntimeError(f"POCKETSPHINX_REAL_SPEECH_ALIGNMENT_FAILED:{aid}")
            events=json.loads(wav.with_suffix(".visemes.json").read_text(encoding="utf-8-sig"))
            tts=[x["time_seconds"] for x in events["word_events"]]
            phones=[x.start_seconds for x in result2.words]
            assert len(tts)==len(phones)
            timing_differences[aid]=[round(a-b,4) for a,b in zip(phones,tts)]
        evidence["source_acoustic_word_phone_alignment"]={
            k:v.model_dump(mode="json") for k,v in source_alignments.items()
        }
        evidence["final_mux_acoustic_word_phone_alignment"]={
            k:v.model_dump(mode="json") for k,v in final_alignments.items()
        }
        evidence["independent_acoustic_vs_tts_word_onset_deltas_seconds"]=timing_differences
        pixel_proxy=PhonemeVideoProxyQC()
        agreement=pixel_proxy.verify(
            pixel=video_pixels,projections=projected,
            alignments=final_alignments,audio_start_seconds=starts,
        )
        mismatch=pixel_proxy.verify(
            pixel=video_pixels,projections=projected,
            alignments=final_alignments,audio_start_seconds=starts,
            shift_seconds=.35,
        )
        evidence["real_mp4_phone_to_pixel_envelope"]=agreement.model_dump(mode="json")
        evidence["misaligned_350ms_negative"]=mismatch.model_dump(mode="json")
        assert agreement.passed,agreement.blockers
        assert not mismatch.passed,"ACOUSTIC_VIDEO_SHIFT_NEGATIVE_FALSE_ACCEPTED"
        assert not agreement.phoneme_shapes_independently_validated

        silent=silence_fixture(OUT)
        silence=aligner.align(
            audio_path=silent,audio_sha256=sha(silent),transcript="hello",
        )
        evidence["silent_audio_negative"]=silence.model_dump(mode="json")
        assert not silence.passed
        unknown=aligner.align(
            audio_path=Path(first["speech"][0]["audio_path"]),
            audio_sha256=first["speech"][0]["audio_sha256"],
            transcript="zzzzzunlikelywordhere",
        )
        evidence["unknown_dictionary_negative"]=unknown.model_dump(mode="json")
        assert not unknown.passed
        # IMPORTANT false-accept negative: forced HMM can align an unrelated
        # dictionary word to speech. It cannot verify transcription by itself.
        wrong_lexical=aligner.align(
            audio_path=Path(first["speech"][0]["audio_path"]),
            audio_sha256=first["speech"][0]["audio_sha256"],
            transcript="go",
        )
        evidence["wrong_but_dictionary_valid_transcript_control"]={
            "wrong_text":"go","actual_spoken_text":"Hello!",
            "forced_decoder_status":wrong_lexical.status,
            "forced_decoder_accepted_wrong_text":wrong_lexical.passed,
            "significance":"ALIGNED_WORDS_ARE_CONDITIONED_ON_INPUT_NOT_CONTENT_VERIFIED",
        }
        if not wrong_lexical.passed:
            raise RuntimeError("EXPECTED_MISALIGNMENT_NEGATIVE_NOT_REPRODUCED")
        asr_evidence=json.loads(
            (ROOT/"data"/"verification"/"v187_unseeded_video_asr"/"v187_qualification_evidence.json"
            ).read_text(encoding="utf-8")
        )
        source_asr=[
            IndependentASRReport.model_validate(value)
            for value in asr_evidence["independent_speech_recognition"].values()
        ]
        final_asr=[
            IndependentASRReport.model_validate(value)
            for value in asr_evidence["final_mux_independent_speech_recognition"].values()
        ]
        evidence["independent_content_recognition_checks"]={
            "source_passed":[x.passed for x in source_asr],
            "final_mux_passed":[x.passed for x in final_asr],
            "asr_source_evidence_sha256":sha(
                ROOT/"data"/"verification"/"v187_unseeded_video_asr"/"v187_qualification_evidence.json"
            ),
        }

        trained_manifest=json.loads(
            (OUT/"training_manifest_v188.json").read_text(encoding="utf-8")
        )
        learned=Path(trained_manifest["model_path"])
        assert learned.is_file() and sha(learned)==trained_manifest["model_sha256"]
        baseline=ROOT/".tools"/"models"/"yolo11n_coco.pt"
        benchmark=HeldoutActorDetectorEvaluator(sample_count=12,confidence=.20)
        rig=Path(str(heldout)+".frame_qc.json")
        pretrain=benchmark.evaluate(
            weights=baseline,target_video=heldout,target_annotations=rig,
            model_kind="COCO_PRETRAINED_PERSON_ONLY",
            person_only=True,
        )
        in_domain=benchmark.evaluate(
            weights=learned,target_video=heldout,target_annotations=rig,
            model_kind="BLENDER_FIRST_SHOT_FINETUNED_BLOCK_ACTOR",
        )
        evidence["coco_zero_shot_block_actor_benchmark"]=pretrain.model_dump(mode="json")
        evidence["domain_adapter_heldout_second_render_benchmark"]=in_domain.model_dump(mode="json")
        evidence["training_manifest"]=trained_manifest

        gate=PerformanceQualificationGate.assess(
            temporal=None,sync=None,v188_required=True,
            phoneme_audio=final_alignments,
            phoneme_video_proxy=agreement,
            trained_actor_detector=in_domain,
            independent_asr_reports=source_asr,
            final_mux_asr_reports=final_asr,
        )
        assert not gate.passed
        evidence["global_production_gate"]=gate.model_dump(mode="json")
        evidence["status"]=(
            "REAL_ACOUSTIC_ALIGNMENT_PASS_DETECTOR_DOMAIN_BENCHMARK_"
            + ("PASS" if in_domain.passed else "BLOCKED")
            +"_PRODUCTION_BLOCKED"
        )
        print(json.dumps({
            "status":evidence["status"],
            "source_phone_counts":{k:len(v.phones) for k,v in source_alignments.items()},
            "final_mux_phone_counts":{k:len(v.phones) for k,v in final_alignments.items()},
            "acoustic_vs_tts_word_onset_delta":timing_differences,
            "actual_video_phone_pixel_correlations":{
                q.actor_id:round(q.correlation_zero_lag,4) if q.correlation_zero_lag is not None else None
                for q in agreement.checks
            },
            "negative_shift_350ms_blocked":not mismatch.passed,
            "forced_decoder_can_accept_wrong_known_word":wrong_lexical.passed,
            "independent_asr_blocked_low_confidence":{
                "source":[not x.passed for x in source_asr],
                "final":[not x.passed for x in final_asr],
            },
            "coco_person_recall":pretrain.recall,
            "trained_heldout_precision":in_domain.precision,
            "trained_heldout_recall":in_domain.recall,
            "trained_heldout_qc":in_domain.status,
            "release":gate.status,
            "evidence":str(result),
        },indent=2))
    except Exception as exc:
        evidence["status"]="FAILED"
        evidence["error"]=f"{type(exc).__name__}: {exc}"
        raise
    finally:
        result.write_text(json.dumps(evidence,indent=2),encoding="utf-8")


if __name__=="__main__":main()
