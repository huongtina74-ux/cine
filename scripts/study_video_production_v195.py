from __future__ import annotations
"""CineFactory v1.6.35 — owned video and public reference observation evidence.

--live-public-youtube-metadata is explicit opt-in, no video/audio download.
Source clips are CineFactory-created local render files; raw footage remains
untouched and stays in the repository. No commercial media is copied.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.video_production_intelligence_v195 import (
    VideoProductionIntelligence,VideoReferenceInput,
)

SOURCE_VIDEOS=[
    ("minecraft","v195_owned_voxel_v185",
     "data/verification/v185_alignment_reid/two_actors_speech_audible.mp4"),
    ("minecraft","v195_owned_voxel_v186",
     "data/verification/v186_multishot_second/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4"),
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--live-public-youtube-metadata",action="store_true")
    ap.add_argument("--youtube-video-id",default="n3PT62-WX20")
    opts=ap.parse_args()
    target=ROOT/"data"/"verification"/"v195_video_production_intelligence"
    target.mkdir(parents=True,exist_ok=True)
    engine=VideoProductionIntelligence(ROOT)
    all_records=[]
    for niche,vid,rel in SOURCE_VIDEOS:
        record=engine.study(VideoReferenceInput(
            niche_id=niche,project_id="OWNED_VIDEO_FORMAT_RESEARCH_V195",
            source_video_id=vid,local_file=str(ROOT/rel),
            first_party_or_authorized_media=True,
            source_is_original_or_licensed=True,max_duration_seconds=300,
        ))
        path=target/(vid+"_decoded_evidence.json")
        path.write_text(record.model_dump_json(indent=2),encoding="utf-8")
        signals=record.observations
        assert signals.decoded_media_observed and signals.source_sha256
        assert signals.audio_stream_analyzed
        all_records.append(record)
        print("ACTUAL_FIRST_PARTY_VIDEO",vid,"frames",signals.video_frame_count,
              "cuts",signals.scene_cuts,"camera",signals.camera_motion_proxy,
              "silence_ratio",signals.measured_silence_ratio,
              "reference_sha",signals.source_sha256[:16],flush=True)
    # BigSchool is a public reference URL user used previously. We do not
    # download media without an explicitly authorized media reference.
    metadata_result=None
    public_problem=None
    if opts.live_public_youtube_metadata:
        try:
            metadata_result=engine.study(VideoReferenceInput(
                niche_id="minecraft",
                project_id="PUBLIC_BIGSCHOOL_METADATA_RESEARCH_V195",
                youtube_video_id=opts.youtube_video_id,
                max_duration_seconds=2400,
            ))
            (target/"bigschool_public_metadata_only_evidence.json").write_text(
                metadata_result.model_dump_json(indent=2),encoding="utf-8")
            s=metadata_result.observations
            assert s.metadata_only and not s.decoded_media_observed
            assert s.scene_cuts is None and s.camera_motion_proxy is None
            print("ACTUAL_PUBLIC_YOUTUBE_METADATA",s.video_id,
                  "channel",s.source_channel_public_metadata,
                  "duration",s.video_duration_seconds,
                  "views",s.views_public_metadata,
                  "DECODED_FRAMES",s.decoded_media_observed,flush=True)
        except Exception as exc:
            public_problem=type(exc).__name__+":"+str(exc)[:250]
            print("PUBLIC_YOUTUBE_METADATA_NOT_AVAILABLE",public_problem,flush=True)
    summary={
        "status":"ACTUAL_OWNED_MEDIA_ANALYSIS_PASS",
        "local_owned_media_count":len(all_records),
        "local_decoded_video_frame_counts":[x.observations.video_frame_count for x in all_records],
        "local_cameras":[x.observations.camera_motion_proxy for x in all_records],
        "local_cut_counts":[x.observations.scene_cuts for x in all_records],
        "public_metadata_only_study_done":metadata_result is not None,
        "public_metadata_error":public_problem,
        "public_video_frames_decoded":False,
        "public_video_downloaded":False,
        "transcript_or_asr_available_for_bigschool":False,
        "competitor_production_method_proven":False,
        "production_tools_benchmarked_cross_engine":False,
        "source_limited_to_owned_render_and_public_metadata":True,
        "no_paid_API_used":True,
        "production_release_authorized":False,
    }
    (target/"study_summary_v195.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

if __name__=="__main__":main()
