from pathlib import Path
import subprocess
import pytest

from cinefactory.research_intelligence.shot_timeline import inspect_shot_timeline


@pytest.fixture()
def movie(tmp_path):
    p=tmp_path/"owned_test.mp4"
    command=["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-f","lavfi","-i","color=c=red:s=640x360:r=12:d=2",
       "-f","lavfi","-i","color=c=blue:s=640x360:r=12:d=2",
       "-f","lavfi","-i","color=c=green:s=640x360:r=12:d=2",
       "-filter_complex","[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
       "-map","[v]","-c:v","mpeg4","-q:v","3",str(p)]
    subprocess.run(command,check=True,timeout=40)
    return p


def test_visual_shot_boundaries_from_real_decodable_video(movie,tmp_path):
    rec=inspect_shot_timeline(movie,tmp_path/"shot.json",permission="OWNED",
                              max_scan_seconds=10,fps=6,scene_threshold=.2)
    assert rec["full_duration_analyzed"]
    assert rec["coverage_ratio"]==1
    assert rec["segment_count"]>=2
    assert rec["segments"][0]["camera_type"]=="UNKNOWN"
    assert not rec["semantic_video_analysis_completed"]
    assert not rec["audio_content_analyzed"]
    assert rec["permission_authenticated"] is False


def test_partial_window_does_not_claim_whole_video(movie,tmp_path):
    rec=inspect_shot_timeline(movie,tmp_path/"part.json",permission="OWNED",
                              max_scan_seconds=5)
    assert rec["report_state"]=="VISUAL_BOUNDARIES_ONLY_PARTIAL"
    assert 0<rec["coverage_ratio"]<1


def test_no_source_rights_is_rejected_before_video_read(movie,tmp_path):
    with pytest.raises(PermissionError):
        inspect_shot_timeline(movie,tmp_path/"out.json",permission="UNKNOWN")
    assert not (tmp_path/"out.json").exists()


def test_input_source_is_hash_anchored_and_immutable(movie,tmp_path):
    p=tmp_path/"report.json"
    result=inspect_shot_timeline(movie,p,permission="OWNED")
    assert len(result["source_sha256"])==64
    with pytest.raises(FileExistsError):
        inspect_shot_timeline(movie,p,permission="OWNED")


def test_wrong_scan_budget_and_type_rejected(movie,tmp_path):
    with pytest.raises(ValueError):
        inspect_shot_timeline(movie,tmp_path/"bad.json",permission="OWNED",fps=0)
    with pytest.raises(ValueError):
        inspect_shot_timeline(movie,tmp_path/"bad.json",permission="OWNED",scene_threshold=float("nan"))
