from __future__ import annotations

"""v1.6.26 real-source verification and adversarial negative controls."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import cv2

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cinefactory.studio.source_speaker_attribution import (
    SourceConditionedSpeakerVerifier,ActorVoiceStem,
)
from cinefactory.studio.face_mouth_observability import (
    FacePatchMotionMouthDetector,ActorFaceSearch,
)
from cinefactory.studio.multishot_render_identity import (
    TwoShotImageIdentityVerifier,
)
from cinefactory.studio.mouth_image_rig_agreement import MouthRigCrossCheck
from cinefactory.studio.rendered_mouth_qc import RenderedMouthSample
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate


def must_rendermanifest(path:Path)->dict:
    row=json.loads(path.read_text(encoding="utf-8"))
    assert row["status"]=="REAL_SPEECH_RENDER_AND_CONTROLLED_DETECTOR_PASS_PRODUCTION_BLOCKED"
    for key in ("blender","speech_video"):
        media=Path(row[key]["path"])
        assert media.is_file()
        assert hashlib.sha256(media.read_bytes()).hexdigest()==row[key]["sha256"]
    return row


def actor_windows(manifest:dict)->list[ActorVoiceStem]:
    return [ActorVoiceStem(
        actor_id=row["actor_id"],line_id=row["line_id"],
        source_wav=row["audio_path"],source_sha256=row["audio_sha256"],
        start_seconds=row["line_start_seconds"],
        end_seconds=row["line_start_seconds"]+row["audio_duration_seconds"],
    ) for row in manifest["speech"]]


def face_search(manifest:dict)->list[ActorFaceSearch]:
    video=Path(manifest["blender"]["path"])
    frame_qc=json.loads(Path(str(video)+".frame_qc.json").read_text(encoding="utf-8"))
    searches=[]
    for row in manifest["speech"]:
        box=frame_qc["actors"][row["actor_id"]]["screen_box"]
        searches.append(ActorFaceSearch(
            actor_id=row["actor_id"],line_id=row["line_id"],
            actor_box_top_left={
                "x0":box["x0"],"x1":box["x1"],
                "y0":1-box["y1"],"y1":1-box["y0"],
            },
            start_seconds=row["line_start_seconds"],
            end_seconds=row["line_start_seconds"]+row["audio_duration_seconds"],
        ))
    return searches


def swapped_stem_video(manifest:dict,out:Path)->Path:
    stems=manifest["speech"]
    assert len(stems)==2
    a,b=stems
    # Video remains unchanged; audio stems are intentionally assigned to the
    # *wrong* actor windows to test attribution false acceptance.
    media=manifest["speech_video"]["path"]
    dest=out/"NEGATIVE_swapped_voices.mp4"
    filter_graph=(
        f"[1:a]adelay={round(b['line_start_seconds']*1000)}:all=1[second];"
        f"[2:a]adelay={round(a['line_start_seconds']*1000)}:all=1[first];"
        "[first][second]amix=inputs=2:duration=longest:normalize=0,apad[out]"
    )
    subprocess.run([
        "ffmpeg","-nostdin","-v","error","-y",
        "-i",str(media),"-i",a["audio_path"],"-i",b["audio_path"],
        "-filter_complex",filter_graph,"-map","0:v:0","-map","[out]",
        "-c:v","copy","-c:a","aac",
        "-t",str(manifest["speech_video"]["duration_seconds"]),
        str(dest),
    ],check=True,timeout=90)
    return dest


def frozen_video(manifest:dict,out:Path)->Path:
    source=Path(manifest["speech_video"]["path"])
    capture=cv2.VideoCapture(str(source))
    ok,frame=capture.read()
    fps=float(capture.get(cv2.CAP_PROP_FPS))
    count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    assert ok and fps>0 and count>5
    destination=out/"NEGATIVE_frozen_mouth.mp4"
    writer=cv2.VideoWriter(str(destination),cv2.VideoWriter_fourcc(*"mp4v"),
                           fps,(frame.shape[1],frame.shape[0]))
    assert writer.isOpened()
    for _ in range(count):
        writer.write(frame)
    writer.release()
    return destination


def main()->None:
    out=ROOT/"data"/"verification"/"v186_real_speaker_face_multishot"
    out.mkdir(parents=True,exist_ok=True)
    first=must_rendermanifest(
        ROOT/"data"/"verification"/"v185_alignment_reid"/"v185_render_evidence.json"
    )
    second=must_rendermanifest(
        ROOT/"data"/"verification"/"v186_multishot_second"/"v186_render_evidence.json"
    )
    evidence={"milestone":"v1.6.26","status":"STARTED","production_qualified":False}
    dest=out/"v186_qualification_evidence.json"
    try:
        stems=actor_windows(first)
        speaker=SourceConditionedSpeakerVerifier()
        good_speaker=speaker.verify(media_path=first["speech_video"]["path"],stems=stems)
        swap_path=swapped_stem_video(first,out)
        bad_speaker=speaker.verify(media_path=swap_path,stems=stems)
        assert good_speaker.passed,good_speaker.blockers
        assert not bad_speaker.passed,"SPEAKER_SWAP_NEGATIVE_ACCEPTED"
        evidence["known_stem_final_mux_attribution"]=good_speaker.model_dump(mode="json")
        evidence["speaker_swap_negative"]=bad_speaker.model_dump(mode="json")

        searches=face_search(first)
        mouth=FacePatchMotionMouthDetector()
        good_mouth=mouth.evaluate(
            media_path=first["speech_video"]["path"],searches=searches,
        )
        frozen_path=frozen_video(first,out)
        bad_mouth=mouth.evaluate(media_path=frozen_path,searches=searches)
        assert good_mouth.passed,good_mouth.blockers
        assert not bad_mouth.passed,"FROZEN_FACE_NEGATIVE_ACCEPTED"
        evidence["face_patch_image_mouth_observability"]=good_mouth.model_dump(mode="json")
        evidence["frozen_face_negative"]=bad_mouth.model_dump(mode="json")
        rig_sidecar=json.loads(Path(
            first["blender"]["path"]+".geometry_qc.json"
        ).read_text(encoding="utf-8"))
        projections=[
            RenderedMouthSample.model_validate(row)
            for row in rig_sidecar["mouth_projection"]
        ]
        agreement=MouthRigCrossCheck().compare(
            observed=good_mouth,projected=projections,
        )
        evidence["image_discovered_vs_rig_mouth_crosscheck"]=agreement.model_dump(mode="json")
        assert agreement.passed,agreement.blockers
        assert not agreement.production_qualified

        verifier=TwoShotImageIdentityVerifier()
        positive=verifier.compare(
            first_video=first["blender"]["path"],
            second_video=second["blender"]["path"],
        )
        other_sidecar=Path(second["blender"]["path"]+".frame_qc.json")
        second_actors=json.loads(other_sidecar.read_text(encoding="utf-8"))["actors"]
        assert set(second_actors)=={"A","B"}
        impostor=verifier.compare(
            first_video=first["blender"]["path"],
            second_video=second["blender"]["path"],
            second_override={"A":second_actors["B"],"B":second_actors["A"]},
        )
        assert positive.passed,positive.blockers
        assert not impostor.passed,"ACTOR_LABEL_SWAP_NEGATIVE_ACCEPTED"
        evidence["real_blender_two_shot_identity"]=positive.model_dump(mode="json")
        evidence["relabel_negative"]=impostor.model_dump(mode="json")
        evidence["second_render"]=second["blender"]

        gate=PerformanceQualificationGate.assess(
            temporal=None,sync=None,v186_required=True,
            speaker_source=good_speaker,image_mouth=good_mouth,
            real_multishot=positive,mouth_rig_agreement=agreement,
        )
        evidence["global_production_gate"]=gate.model_dump(mode="json")
        assert not gate.passed,"V186_UNSAFE_PRODUCTION_RELEASE"
        # Never confer a production release based on known-source or
        # annotated-actor diagnostic evidence.
        evidence["production_blockers"]=[
            "INDEPENDENT_SPEAKER_DIARIZATION_NOT_VERIFIED",
            "FACE_LANDMARKS_AND_MOUTH_VISIBILITY_UNQUALIFIED",
            "MULTISHOT_RENDER_ACTOR_BOXES_NOT_INDEPENDENT",
            "WAN_MULTISEED_IDENTITY_UNVERIFIED",
            "PHONEME_LEVEL_AUDIO_VISUAL_SYNC_UNVERIFIED",
        ]
        evidence["status"]="REAL_DIAGNOSTICS_AND_NEGATIVE_CONTROLS_PASS_PRODUCTION_BLOCKED"
        print(json.dumps({
            "status":evidence["status"],
            "speaker_scores":[round(c.score,4) for c in good_speaker.checks],
            "speaker_swap_blocked":not bad_speaker.passed,
            "mouth_boxes":[x.pixel_box for x in good_mouth.candidates],
            "frozen_mouth_blocked":not bad_mouth.passed,
            "image_mouth_iou":[round(x.iou,3) for x in agreement.matches],
            "multishot_identity":[round(x.correct_score,4) for x in positive.matches],
            "actor_relabel_blocked":not impostor.passed,
            "production_qualified":False,"evidence":str(dest),
        },indent=2))
    except Exception as exc:
        evidence["status"]="FAILED"
        evidence["error"]=f"{type(exc).__name__}: {exc}"
        raise
    finally:
        dest.write_text(json.dumps(evidence,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
