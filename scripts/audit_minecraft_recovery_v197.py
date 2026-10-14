"""CineFactory Minecraft art recovery: inspect ACTUAL v197 pilot + fail-closed gate.

The visuals are an internally generated experimental clip, NOT quality-
certified or a recreation of any external competitor. Use genuine media,
metadata, source shader/node and image evidence without fabricating review.
"""
import json,subprocess,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.minecraft_art_gate_v197 import (
    MinecraftShotEvidence,evaluate_minecraft_art)
OUT=ROOT/"data/verification/v197_minecraft_art_direction"
golden=ROOT/"data/verification/v196_golden_benchmark/eevee.mp4"
pilot=OUT/"minecraft_3shot_visual_pilot_with_original_sfx.mp4"
contract=json.loads((OUT/"3shot_visual_contract.json").read_text(encoding="utf-8"))
origin=json.loads((OUT/"pilot_media_evidence.json").read_text(encoding="utf-8"))

def probe(file):
    return json.loads(subprocess.check_output([
        "ffprobe","-v","error","-count_frames","-show_streams","-of","json",str(file)
    ],text=True,timeout=30))
def get_video(streams):
    return next(s for s in streams if s.get("codec_type")=="video")
def key(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

baseprobe=probe(golden)
base=get_video(baseprobe["streams"])
basee=MinecraftShotEvidence(title="v196 original tech benchmark",
    video_path=str(golden.resolve()),resolution_x=int(base["width"]),
    resolution_y=int(base["height"]),fps=12,duration_seconds=2,
    character_count=2,camera_shot_count=1,
    natively_executed_real_media=True,benchmark_only=True)
base_result=evaluate_minecraft_art(basee)
raw=probe(pilot)
stream=get_video(raw["streams"])
audio=[s for s in raw["streams"] if s.get("codec_type")=="audio"]
if (int(stream["width"]),int(stream["height"]))!=(960,540):
    raise RuntimeError("INVALID_ACTUAL_960X540")
if int(stream["nb_read_frames"])!=48 or not audio:
    raise RuntimeError("ACTUAL_48_FRAME_AUDIO_MISSING")
if origin["video_sha256"]!=key(pilot):
    raise RuntimeError("TAMPERED_FINAL_OUTPUT")
pilot_e=MinecraftShotEvidence(title="v197 artistic exploration, NOT episode",
    video_path=str(pilot.resolve()),
    resolution_x=960,resolution_y=540,fps=24,duration_seconds=2,
    character_count=2,
    original_skin_texture_files=[], # 17 internal packed textures; no approved UV character skin files.
    unique_character_faces=2,facial_expression_cues=1,
    mouth_or_viseme_cues=0,emotion_acting_keys=0,
    animation_clips=["arm pivot", "root sway"],
    articulated_arm_or_leg_pivot=True,
    controlled_character_identity=False,
    original_world_and_props=True,
    camera_shot_count=3,camera_plan_approved=False,
    physically_readable_depth=True,
    artistic_lighting_reviewed=False,
    dialogue_required=False,dialogue_audio_present=False,
    music_required=False,music_present=False,
    audio_master_loudness_checked=False,
    license_clearance_complete=False,original_story_reviewed=False,
    independent_qa_approved=False,
    natively_executed_real_media=True,benchmark_only=False)
pilot_result=evaluate_minecraft_art(pilot_e)
assert len(pilot_result.hard_blockers)>5
record={
    "status":"MINECRAFT_QUALITY_RECOVERY_DIAGNOSED_NOT_YET_PRODUCTION",
    "v196_art_gate":base_result.model_dump(mode="json"),
    "v197_art_gate":pilot_result.model_dump(mode="json"),
    "verified_pilot_hash":key(pilot),
    "pilot_frames":48,"pilot_audio_codec":audio[0]["codec_name"],
    "pilot_three_shot_cameras":[x["camera"] for x in contract["shots"]],
    "packed_pixel_texture_previews_not_approved_uv_skins":True,
    "original_music_or_voice_acting_verified":False,
    "first_party_prototype_not_a_bigschool_or_maizen_copy":True,
    "reference_video_full_decoding_successful":False,
    "artist_quality_approved":False,
    "next_production_gates":[
        "WRITE_ORIGINAL_30_60_SECOND_STORY_WITH_3_ACTING_BEATS",
        "IMPORT_VALID_SKIN_64X64_AND_3D_LAYER_FROM_CHARACTER_ART_DEPARTMENT",
        "BUILD_SHOULDER_ELBOW_HIP_HAND_RIG_AND_NLA_ACTION_LIBRARY",
        "BUILD_ACTUAL_EYE_BROW_MOUTH_FACE_CONTROLLER_AND_REAL_VISEMES",
        "BUILD_ORIGINAL_MINECRAFT_WORLD_AND_COPYRIGHT_SAFETY_LEDGER",
        "ANIMATE_ACTING_AND_CINEMATIC_CAMERA_FROM_LOCKED_STORYBOARD",
        "ORIGINAL_DIALOGUE_PERFORMANCES_RECORD_OR_LICENCED_TTS_AND_ALIGN",
        "INDEPENDENT_VISUAL_AUDIO_REVIEW_ON_REAL_1080P24_LONGER_PILOT",
        "BENCHMARK_EEVEE_CYCLES_MINEIMATOR_CONDITIONALLY_ON_COMPETENT_SAME_ASSETS",
        "APPROVE_COST_PER_ACCEPTED_MINUTE_AFTER_RETAKES_AND_HUMAN_TOUCH",
    ],
}
(OUT/"recovery_gap_audit.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
print("Minecraft original video PASS 48 decoded frames and AAC audio, SHA",key(pilot)[:12])
print("v196 art gate",base_result.decision,"blockers",len(base_result.hard_blockers))
print("v197 art gate",pilot_result.decision,"blockers",len(pilot_result.hard_blockers))
print("rights / human independent QC not passed; no production approval")
