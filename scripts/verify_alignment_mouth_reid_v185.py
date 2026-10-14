from __future__ import annotations

"""Proof runner for v1.6.25: *measured* PCM word checks and actual rendered mouth
pixels, plus controlled three-seed detector stress and deliberately bad seed.
"""
import json
import hashlib
import subprocess
import sys
import numpy as np
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cinefactory.studio.audio_constrained_alignment import (
    AudioConstrainedWordVerifier,SynthesizerWordEvent,
)
from cinefactory.studio.rendered_mouth_qc import (
    RenderedMouthProjectionQC,RenderedMouthSample,
)
from cinefactory.studio.independent_actor_detection import (
    IndependentColorActorDetector,ColorSignature,
)
from cinefactory.studio.multi_seed_identity_qc import MultiSeedIdentityLab
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate


def main()->None:
    base=ROOT/"data"/"verification"/"v185_alignment_reid"
    source=base/"v185_render_evidence.json"
    output=base/"v185_qualification_evidence.json"
    record={"version":"v1.6.25","status":"STARTED","production_qualified":False}
    try:
        previous=json.loads(source.read_text(encoding="utf-8"))
        if previous.get("status")!="REAL_SPEECH_RENDER_AND_CONTROLLED_DETECTOR_PASS_PRODUCTION_BLOCKED":
            raise RuntimeError("V185_AUDIO_BLENDER_SOURCE_NOT_VERIFIED")
        verifier=AudioConstrainedWordVerifier()
        words={}
        word_models=[]
        for row in previous["speech"]:
            audio=Path(row["audio_path"])
            proof_path=audio.with_suffix(".visemes.json")
            proof=json.loads(proof_path.read_text(encoding="utf-8-sig"))
            if proof.get("wav_sha256")!=row["audio_sha256"]:
                raise RuntimeError("SYNTHESIS_EVENT_HASH_MISMATCH")
            events=[SynthesizerWordEvent.model_validate(w) for w in proof.get("word_events",[])]
            word_report=verifier.verify(
                audio_path=audio,
                audio_sha256=row["audio_sha256"],
                transcript=row["text"],
                word_events=events,
            )
            word_models.append(word_report)
            words[row["actor_id"]]=word_report.model_dump(mode="json")
        record["audio_constrained_word_evidence"]=words
        video=Path(previous["blender"]["path"])
        sidecar=video.with_suffix(video.suffix+".geometry_qc.json")
        side=json.loads(sidecar.read_text(encoding="utf-8"))
        samples=[RenderedMouthSample.model_validate(x) for x in side.get("mouth_projection",[])]
        rendered=RenderedMouthProjectionQC().evaluate(
            video_path=video,samples=samples,
        )
        record["real_blender_projected_mouth_pixel_qc"]=rendered.model_dump(mode="json")
        # The released diagnostic MP4 is remuxed H264 with AAC. Verify pixels
        # again on that actual deliverable, rather than trusting the raw render.
        actual_mux=RenderedMouthProjectionQC().evaluate(
            video_path=previous["speech_video"]["path"],samples=samples,
        )
        record["final_mux_mouth_pixel_qc"]=actual_mux.model_dump(mode="json")
        mux_path=Path(previous["speech_video"]["path"])
        decoded=subprocess.run([
            "ffmpeg","-nostdin","-v","error","-i",str(mux_path),
            "-map","0:a:0","-ac","1","-ar","16000",
            "-f","f32le","-acodec","pcm_f32le","pipe:1",
        ],capture_output=True,timeout=35,check=False)
        if decoded.returncode or not decoded.stdout:
            raise RuntimeError("FINAL_MUX_AUDIO_DECODING_FAILED")
        pcm=np.frombuffer(decoded.stdout,dtype="<f4")
        speaker_audio={}
        for row in previous["speech"]:
            first=int(row["line_start_seconds"]*16000)
            last=int((row["line_start_seconds"]+row["audio_duration_seconds"])*16000)
            segment=pcm[first:last]
            if not len(segment):
                raise RuntimeError("FINAL_MUX_SPEECH_WINDOW_EMPTY")
            signal=float(np.sqrt(np.mean(segment.astype(np.float64)**2)))
            speaker_audio[row["actor_id"]]={
                "window_start_seconds":row["line_start_seconds"],
                "audio_rms":signal,"audio_samples":len(segment),
                "passed":signal>=.008,
            }
        record["final_mux_actor_audio_window_qc"]=speaker_audio
        record["real_rendered_mouth_projected_count"]=len(samples)
        signatures=[
            ColorSignature(actor_id="A",rgb=(230,40,45),tolerance=28),
            ColorSignature(actor_id="B",rgb=(40,80,230),tolerance=28),
        ]
        lab=MultiSeedIdentityLab(IndependentColorActorDetector(signatures))
        positive=lab.evaluate(seeds=[1,7,16])
        impostor=lab.evaluate(seeds=[1,7,16],corrupted_seeds={7})
        record["controlled_multiseed_benchmark"]=positive.model_dump(mode="json")
        record["controlled_impostor_negative"]=impostor.model_dump(mode="json")
        assert positive.passed and not positive.production_qualified
        assert not impostor.passed
        # Stronger v185 signal evidence may not satisfy v183's broader
        # *production* gates; explicitly preserve the BLOCKED decision.
        gate=PerformanceQualificationGate.assess(
            temporal=None,sync=None,v185_required=True,
            audio_word_reports=word_models,mouth_pixels=rendered,
            multi_seed=positive,
        )
        record["global_production_gate"]=gate.model_dump(mode="json")
        assert not gate.passed
        assert len(words)==2
        record["status"]="DIAGNOSTICS_COMPLETED_PRODUCTION_BLOCKED"
        print(json.dumps({
            "status":record["status"],
            "word_alignment":{k:v["status"] for k,v in words.items()},
            "real_rendered_mouth":rendered.status,
            "real_rendered_mouth_blockers":rendered.blockers,
            "final_mux_mouth":actual_mux.status,
            "final_mux_mouth_blockers":actual_mux.blockers,
            "final_mux_voice_rms":{
                actor:round(item["audio_rms"],5)
                for actor,item in speaker_audio.items()
            },
            "projected_sample_count":len(samples),
            "multi_seed_positive":positive.status,
            "worst_precision":positive.worst_precision,
            "worst_recall":positive.worst_recall,
            "impostor_control":impostor.status,
            "production":gate.status,
            "artifact":str(output),
        },indent=2))
    except Exception as exc:
        record["status"]="FAILED"
        record["error"]=f"{type(exc).__name__}: {exc}"
        raise
    finally:
        output.write_text(json.dumps(record,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
