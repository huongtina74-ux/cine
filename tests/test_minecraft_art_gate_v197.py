from pathlib import Path
from cinefactory.studio.minecraft_art_gate_v197 import MinecraftShotEvidence,evaluate_minecraft_art

def test_v196_visual_baseline_is_not_publishable_even_if_render_passes():
    e=MinecraftShotEvidence(title="v196",resolution_x=480,resolution_y=270,
        fps=12,duration_seconds=2.,character_count=2,camera_shot_count=1,
        original_skin_texture_files=[],unique_character_faces=0,
        facial_expression_cues=0,emotion_acting_keys=0,animation_clips=[],
        benchmark_only=True,natively_executed_real_media=True,
        video_path="data/verification/v196_golden_benchmark/eevee.mp4")
    verdict=evaluate_minecraft_art(e)
    assert verdict.decision=="BLOCKED_MINECRAFT_ART_PRODUCTION"
    assert "PRODUCTION_PIXEL_SKIN_TEXTURES_MISSING" in verdict.hard_blockers
    assert "NONEXPRESSIVE_GENERIC_FACES" in verdict.hard_blockers
    assert "LIMB_RIG_WITH_SHOULDER_ELBOW_HIP_PIVOT_MISSING" in verdict.hard_blockers
    assert "AUDIO_POST_QC_MISSING" in verdict.hard_blockers
    assert not verdict.video_is_publishable

def test_untested_materials_never_pass_by_better_resolution_alone():
    e=MinecraftShotEvidence(title="upscale",resolution_x=3840,resolution_y=2160,
        fps=60,duration_seconds=600,character_count=2,camera_shot_count=3)
    result=evaluate_minecraft_art(e)
    assert "PRODUCTION_PIXEL_SKIN_TEXTURES_MISSING" in result.hard_blockers
    assert "NONEXPRESSIVE_GENERIC_FACES" in result.hard_blockers

def test_unauthorized_dialogue_and_music_are_strict_blockers():
    e=MinecraftShotEvidence(title="music",resolution_x=1920,resolution_y=1080,
        fps=24,duration_seconds=40,character_count=2,camera_shot_count=3,
        dialogue_required=True,music_required=True)
    result=evaluate_minecraft_art(e)
    assert "SCRIPTED_DIALOGUE_AUDIO_MISSING" in result.hard_blockers
    assert "SCRIPTED_MUSIC_MISSING" in result.hard_blockers
    assert "LIPSYNC_OR_DIALOGUE_MOUTH_MISSING" in result.hard_blockers

def test_even_perfect_spec_still_requires_separate_publication_authorization():
    e=MinecraftShotEvidence(title="fixture",resolution_x=1920,resolution_y=1080,
        fps=24,duration_seconds=50,character_count=2,
        original_skin_texture_files=["own_A.png","own_B.png"],unique_character_faces=2,
        facial_expression_cues=10,mouth_or_viseme_cues=12,emotion_acting_keys=20,
        animation_clips=["react","walk"],articulated_arm_or_leg_pivot=True,
        controlled_character_identity=True,original_world_and_props=True,
        camera_shot_count=3,camera_plan_approved=True,physically_readable_depth=True,
        artistic_lighting_reviewed=True,dialogue_required=True,
        dialogue_audio_present=True,audio_master_loudness_checked=True,
        license_clearance_complete=True,original_story_reviewed=True,
        independent_qa_approved=True,natively_executed_real_media=True,
        video_path="example.mp4")
    result=evaluate_minecraft_art(e)
    assert result.decision=="READY_FOR_SEPARATE_PUBLICATION_AUTHORIZATION"
    assert not result.hard_blockers
    assert not result.video_is_publishable

def test_real_v197_visual_pilot_has_mp4_audio_and_verified_sha():
    import json,hashlib
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    out=root/"data/verification/v197_minecraft_art_direction"
    record=json.loads((out/"pilot_media_evidence.json").read_text())
    file=Path(record["video_path"])
    assert file.is_file()
    assert hashlib.sha256(file.read_bytes()).hexdigest()==record["video_sha256"]
    assert record["fps"]==24 and record["frames"]==48
    assert record["resolution"]==[960,540]
    assert record["real_video_and_audio"]
    assert not record["production_qualified"]
    assert not record["competitor_video_decoded_and_analyzed"]

def test_art_gap_remains_blocked_despite_nicer_pixels():
    import json
    from pathlib import Path
    out=Path(__file__).resolve().parents[1]/"data/verification/v197_minecraft_art_direction"
    d=json.loads((out/"recovery_gap_audit.json").read_text())
    assert d["status"]=="MINECRAFT_QUALITY_RECOVERY_DIAGNOSED_NOT_YET_PRODUCTION"
    assert d["v196_art_gate"]["decision"]=="BLOCKED_MINECRAFT_ART_PRODUCTION"
    assert d["v197_art_gate"]["decision"]=="BLOCKED_MINECRAFT_ART_PRODUCTION"
    assert "PRODUCTION_PIXEL_SKIN_TEXTURES_MISSING" in d["v197_art_gate"]["hard_blockers"]
    assert "INDEPENDENT_HUMAN_VIDEO_QC_MISSING" in d["v197_art_gate"]["hard_blockers"]

def test_three_real_camera_shots_and_unapproved_acting():
    import json
    from pathlib import Path
    out=Path(__file__).resolve().parents[1]/"data/verification/v197_minecraft_art_direction"
    plan=json.loads((out/"3shot_visual_contract.json").read_text())
    assert [x["start_frame"] for x in plan["shots"]]==[1,17,33]
    assert plan["frames_expected"]==48
    assert len({x["camera"] for x in plan["shots"]})==3
    assert plan["independent_human_review"] is False
    assert not plan["professional_animated_series_approved"]
