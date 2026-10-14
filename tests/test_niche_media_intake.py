from pathlib import Path
import hashlib,json,subprocess
import pytest
from cinefactory.research_intelligence.niche_media_intake import process_niche_media

VID="ABCdef12345"

def setup(tmp_path):
    folder=tmp_path/"stage";folder.mkdir()
    watch=folder/"workorders.json"
    watch.write_text(json.dumps({"schema":"cine.niche.work_orders.v1",
               "lane_tasks":[{"video_id":VID},{"video_id":VID,"lane":"fresh"}]}),encoding="utf-8")
    movie=folder/"owned.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-f","lavfi","-i","testsrc2=size=640x360:duration=3:rate=12",
       "-c:v","mpeg4","-q:v","6",str(movie)],check=True,timeout=30)
    manifest=folder/"media.json"
    def write(sha,per="OWNED"):
        manifest.write_text(json.dumps({"schema":"cine.niche.authorized_media_manifest.v1",
        "cases":[{"video_id":VID,"media_path":str(movie),"sha256":sha,
                  "authorization":per,"permission_reference":"test-original-owned-video"}]}),encoding="utf-8")
    write(hashlib.sha256(movie.read_bytes()).hexdigest())
    return watch,manifest,movie,write

def test_review_pipeline_processes_only_explicitly_owned_video(tmp_path):
    watch,manifest,movie,_=setup(tmp_path)
    out=process_niche_media(watch,manifest,tmp_path/"result",max_scan_seconds=5)
    assert out["mechanically_analyzed_video_count"]==1
    assert out["matching_authorized_media"]==1
    assert out["source_rights_authenticated"] is False
    assert out["production_permission"] is False
    mechanics=json.loads(Path(out["video_analysis"][0]["mechanics_file"]).read_text(encoding="utf-8"))
    assert mechanics["segment_count"]>0
    assert not mechanics["script_or_character_understood"]
    assert out["video_analysis"][0]["frames_observed"]>0
    study=json.loads(Path(out["video_analysis"][0]["frame_study_file"]).read_text(encoding="utf-8"))
    assert study["observed_full_video_story"] is False
    assert out["video_analysis"][0]["department_task_count"]>=5

def test_hash_mismatch_fails_before_analysis(tmp_path):
    w,m,_,write=setup(tmp_path)
    write("0"*64)
    with pytest.raises(ValueError,match="differs"):
        process_niche_media(w,m,tmp_path/"bad")
    assert not (tmp_path/"bad").exists()

def test_unlicensed_attachment_rejected(tmp_path):
    w,m,f,write=setup(tmp_path)
    write(hashlib.sha256(f.read_bytes()).hexdigest(),"UNKNOWN")
    with pytest.raises(PermissionError):
        process_niche_media(w,m,tmp_path/"bad")

def test_nonexistent_watch_video_is_never_processed(tmp_path):
    w,m,f,write=setup(tmp_path)
    data=json.loads(w.read_text(encoding="utf-8"))
    data["lane_tasks"]=[{"video_id":"OTHER123456"}]
    w.write_text(json.dumps(data),encoding="utf-8")
    r=process_niche_media(w,m,tmp_path/"empty")
    assert r["state"]=="NO_MATCHING_AUTHORIZED_MEDIA"
    assert r["mechanically_analyzed_video_count"]==0


def test_oversized_input_blocked_before_costly_full_hash(tmp_path,monkeypatch):
    from cinefactory.research_intelligence import niche_media_intake as module
    w,m,f,write=setup(tmp_path)
    monkeypatch.setattr(module,"MAX_MEDIA_BYTES",100)
    with pytest.raises(ValueError,match="exceeds bounded"):
        process_niche_media(w,m,tmp_path/"huge")
    assert not (tmp_path/"huge").exists()


def test_file_replacement_during_media_analysis_is_rejected(tmp_path,monkeypatch):
    from cinefactory.research_intelligence import niche_media_intake as module
    w,m,f,write=setup(tmp_path)
    recorded_hash=hashlib.sha256(f.read_bytes()).hexdigest()
    def altered_source(path,*args,**kw):
        f.write_bytes(f.read_bytes()+b"modified while processing")
        return {"source_sha256":recorded_hash,"timeline_sha256":"valid-test-only"}
    monkeypatch.setattr(module,"prepare_media_mechanics",altered_source)
    with pytest.raises(RuntimeError,match="MEDIA_SOURCE_CHANGED_DURING_ANALYSIS"):
        process_niche_media(w,m,tmp_path/"changed")
    assert not (tmp_path/"changed"/"media_intake.json").exists()
