from __future__ import annotations
"""v1.6.27 actual rendered-video full-frame actor tracking and independently
decoded Windows English dictation. Negative visual/auditory trials fail closed.
No auto release; no invented phoneme timestamps or human ground truth.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cinefactory.studio.full_frame_actor_search import (
    FullFrameReferenceActorScanner,
)
from cinefactory.studio.independent_speech_asr import OfflineIndependentASR
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate


def source_manifest(folder:str,file:str)->dict:
    path=ROOT/"data"/"verification"/folder/file
    obj=json.loads(path.read_text(encoding="utf-8"))
    if obj["status"]!="REAL_SPEECH_RENDER_AND_CONTROLLED_DETECTOR_PASS_PRODUCTION_BLOCKED":
        raise RuntimeError("REQUIRED_RENDER_MANIFEST_NOT_PASS")
    for key in ["blender","speech_video"]:
        target=Path(obj[key]["path"])
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=obj[key]["sha256"]:
            raise RuntimeError("RENDER_SOURCE_HASH_MISMATCH")
    return obj


def create_impostor_clip(
    source:Path,target:Path,dest:Path,detector:FullFrameReferenceActorScanner,
)->None:
    template=detector.reference_templates(source_video=source)["A"]
    cap=cv2.VideoCapture(str(target))
    fps=cap.get(cv2.CAP_PROP_FPS)
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    assert fps>0 and height>template.shape[0]+10 and width>template.shape[1]+20
    writer=cv2.VideoWriter(str(dest),cv2.VideoWriter_fourcc(*"mp4v"),fps,(width,height))
    assert writer.isOpened()
    x0,y0=12,height-template.shape[0]-9
    written=0
    try:
        while True:
            ok,frame=cap.read()
            if not ok:
                break
            # A second matching "A" appears far from the original actor.
            frame[y0:y0+template.shape[0],x0:x0+template.shape[1]] = cv2.cvtColor(
                template,cv2.COLOR_GRAY2BGR
            )
            writer.write(frame)
            written+=1
    finally:
        writer.release()
        cap.release()
    if written<12:
        raise RuntimeError("IMPOSTOR_VIDEO_TOO_FEW_FRAMES")


def final_audio_segment(media: Path, *,start:float,length:float,dest:Path)->str:
    job=subprocess.run([
        "ffmpeg","-nostdin","-v","error","-y",
        "-i",str(media),"-ss",str(start),"-t",str(length),
        "-vn","-ar","16000","-ac","1","-c:a","pcm_s16le",str(dest),
    ],capture_output=True,text=True,timeout=45,check=False)
    if job.returncode or not dest.is_file():
        raise RuntimeError("FINAL_AUDIO_ASR_SEGMENT_EXTRACTION_FAILED")
    return hashlib.sha256(dest.read_bytes()).hexdigest()


def main():
    out=ROOT/"data"/"verification"/"v187_unseeded_video_asr"
    out.mkdir(parents=True,exist_ok=True)
    dest=out/"v187_qualification_evidence.json"
    evidence={"milestone":"v1.6.27","status":"STARTED","production_qualified":False}
    try:
        first=source_manifest("v185_alignment_reid","v185_render_evidence.json")
        second=source_manifest("v186_multishot_second","v186_render_evidence.json")
        a=Path(first["blender"]["path"])
        b=Path(second["blender"]["path"])
        scanner=FullFrameReferenceActorScanner()
        scan=scanner.scan(source_video=a,target_video=b)
        bench=scanner.evaluate_rig_ground_truth(scan,b)
        evidence["full_frame_target_scan"]=scan.model_dump(mode="json")
        evidence["rig_label_evaluation_ONLY"]=bench.model_dump(mode="json")
        assert scan.passed,scan.blockers
        assert bench.passed,bench.blockers
        # Verify the target's .frame_qc.json/.geometry_qc.json is unnecessary
        # for inference by using an unannotated media-only byte-copy.
        unannotated=out/"target_without_sidecars.mp4"
        shutil.copyfile(b,unannotated)
        unseeded=scanner.scan(source_video=a,target_video=unannotated)
        assert unseeded.passed and unseeded.frames>=10
        evidence["no_target_sidecar_scan"]={
            "passed":unseeded.passed,"target_sidecar_available":False,
            "source_sha256":scan.source_template_video_sha256,
            "target_sha256":unseeded.target_video_sha256,
            "frame_count":unseeded.frames,
            "used_target_rig_boxes":unseeded.target_rig_annotations_used_for_detection,
        }
        impostor=out/"NEGATIVE_second_actor_lookalike.mp4"
        create_impostor_clip(a,b,impostor,scanner)
        fake=scanner.scan(source_video=a,target_video=impostor)
        evidence["lookalike_negative"]=fake.model_dump(mode="json")
        assert not fake.passed,"DUPLICATED_REFERENCE_ACTOR_FALSE_ACCEPTED"
        assert any("TWO_SIMILAR_SCREEN_ACTOR_CANDIDATES" in x for x in fake.blockers)

        asr_service=OfflineIndependentASR(ROOT,confidence_floor=.55)
        reports={}
        for utterance in first["speech"]:
            result=asr_service.assess(
                source_wav=utterance["audio_path"],
                source_sha256=utterance["audio_sha256"],
                expected_transcript=utterance["text"],
                output_json=out/(utterance["actor_id"]+".dictation.json"),
            )
            reports[utterance["actor_id"]]=result
        evidence["independent_speech_recognition"]={
            actor:report.model_dump(mode="json") for actor,report in reports.items()
        }
        final_reports={}
        swapped_reports={}
        swapped_media=ROOT/"data"/"verification"/"v186_real_speaker_face_multishot"/"NEGATIVE_swapped_voices.mp4"
        if not swapped_media.is_file():
            raise RuntimeError("SWAPPED_VOICE_NEGATIVE_MEDIA_MISSING")
        for utterance in first["speech"]:
            key=utterance["actor_id"]
            start=float(utterance["line_start_seconds"])
            length=float(utterance["audio_duration_seconds"])
            dest_wav=out/(key+".final_mp4_audio.wav")
            digest=final_audio_segment(
                Path(first["speech_video"]["path"]),
                start=start,length=length,dest=dest_wav,
            )
            final_reports[key]=asr_service.assess(
                source_wav=dest_wav,source_sha256=digest,
                expected_transcript=utterance["text"],
                output_json=out/(key+".final_mp4.dictation.json"),
            )
            swapped_wav=out/(key+".swapped_mp4_audio.wav")
            swapped_hash=final_audio_segment(
                swapped_media,start=start,length=length,dest=swapped_wav,
            )
            swapped_reports[key]=asr_service.assess(
                source_wav=swapped_wav,source_sha256=swapped_hash,
                expected_transcript=utterance["text"],
                output_json=out/(key+".swapped_mp4.dictation.json"),
            )
        evidence["final_mux_independent_speech_recognition"]={
            actor:report.model_dump(mode="json") for actor,report in final_reports.items()
        }
        evidence["voice_swapped_final_mux_asr_negative"]={
            actor:report.model_dump(mode="json") for actor,report in swapped_reports.items()
        }
        assert not any(report.passed for report in swapped_reports.values()),(
            "SWAPPED_SPEECH_TEXT_ASR_FALSE_ACCEPTED"
        )
        # The confidence of shorter words is data-dependent; do not assume
        # results for either actor. It MUST block anything below threshold.
        assert len(reports)==2
        assert all(not report.phoneme_alignment_verified for report in reports.values())
        assert all(report.passed or "INDEPENDENT_RECOGNITION_LOW_CONFIDENCE" in report.blockers
                   or "INDEPENDENT_RECOGNIZED_TEXT_MISMATCH" in report.blockers
                   or "INDEPENDENT_RECOGNITION_EMPTY" in report.blockers
                   for report in reports.values())

        incorrect=asr_service.assess(
            source_wav=first["speech"][0]["audio_path"],
            source_sha256=first["speech"][0]["audio_sha256"],
            expected_transcript="This is a completely different statement",
            output_json=out/"NEGATIVE_wrong_text.dictation.json",
        )
        assert not incorrect.passed
        assert "INDEPENDENT_RECOGNIZED_TEXT_MISMATCH" in incorrect.blockers
        evidence["wrong_text_negative"]=incorrect.model_dump(mode="json")

        gate=PerformanceQualificationGate.assess(
            temporal=None,sync=None,v187_required=True,
            full_frame_actor=scan,full_frame_annotated_benchmark=bench,
            independent_asr_reports=list(reports.values()),
            final_mux_asr_reports=list(final_reports.values()),
        )
        evidence["production_gate"]=gate.model_dump(mode="json")
        assert not gate.passed
        evidence["unqualified_requirements"]=[
            "NO_BLIND_ACTOR_DETECTOR: FIRST-SHOT ANNOTATED REFERENCE STILL NEEDED",
            "TARGET_EVALUATION_LABELS_ARE_FROM_RIG_NOT_HUMAN",
            "NO_REAL-WAN_MULTISEED_IDENTITY_GROUND_TRUTH",
            "SAPI_RECOGNITION_CONFIDENCE_LOW_FOR_SHORT_SPEECH",
            "NO_INDEPENDENT_FORCED_PHONEME_OR_VISEME_ALIGNMENT",
            "NO_MULTI-CAMERA_OCCLUSION_OR_CONTINUOUS_4K_QC",
        ]
        evidence["status"]="CONTROLLED_REAL_VIDEO_SEARCH_PASS_AUDIO_ASR_QUALIFICATION_PARTIAL_PRODUCTION_BLOCKED"
        print(json.dumps({
            "status":evidence["status"],
            "full_frame_detection":scan.status,
            "target_frame_count":scan.frames,
            "frame_gt_iou_mean":bench.mean_iou,
            "frame_gt_iou_min":bench.minimum_iou,
            "search_without_target_sidecar":unseeded.passed,
            "lookalike_negative_rejected":not fake.passed,
            "recognition":{
                key:{"text":r.recognized_transcript,
                     "confidence":round(r.confidence,4),"status":r.status}
                for key,r in reports.items()
            },
            "wrong_text_rejected":not incorrect.passed,
            "final_video_asr":{
                key:{"text":r.recognized_transcript,
                     "confidence":round(r.confidence,4),"status":r.status}
                for key,r in final_reports.items()
            },
            "voice_swapped_asr_rejected":{
                key:not r.passed for key,r in swapped_reports.items()
            },
            "production_gate":gate.status,
            "evidence":str(dest),
        },indent=2))
    except Exception as exc:
        evidence["status"]="FAILED"
        evidence["error"]=f"{type(exc).__name__}:{exc}"
        raise
    finally:
        dest.write_text(json.dumps(evidence,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
