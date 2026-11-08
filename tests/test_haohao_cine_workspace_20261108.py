from pathlib import Path
import pytest
from tools.haohao import workspace as ws

def test_workspace_root_inside_cine_and_not_downloads_root():
    assert (ws.CINE_ROOT/"tools/haohao/workspace.py").is_file()
    assert ws.CINE_ROOT.name.lower()!="downloads"
    assert ws.RUNS_ROOT == ws.CINE_ROOT/"data/haohao/runs"
    assert ws.RUNS_ROOT != Path.home()/"Downloads"
    assert ws.APP_USER_DATA != ws.RUNS_ROOT
    assert ws.LEGACY_ROOT == ws.CINE_ROOT/"data/haohao/legacy_runs"

def test_allocate_and_reject_duplicate(tmp_path,monkeypatch):
    monkeypatch.setattr(ws,"RUNS_ROOT",tmp_path/"cine"/"data"/"haohao"/"runs")
    run=ws.allocate_run("BL-0001","pilot_S001_001")
    assert run.is_dir()
    assert run.is_relative_to(ws.RUNS_ROOT)
    assert run.name=="pilot_S001_001"
    with pytest.raises(FileExistsError):
        ws.allocate_run("BL-0001","pilot_S001_001")

@pytest.mark.parametrize("episode,run_id",[
    ("../secrets","pilot_123"),("BL-0001","../../Downloads"),
    ("BL-1","pilot_123"),("BL-0001","a/b"),("BL-0001","!bad")
])
def test_refuse_bad_run_identifiers(tmp_path,monkeypatch,episode,run_id):
    monkeypatch.setattr(ws,"RUNS_ROOT",tmp_path/"runs")
    with pytest.raises(ValueError):
        ws.allocate_run(episode,run_id)

def test_artifact_categories_are_scoped(tmp_path,monkeypatch):
    monkeypatch.setattr(ws,"RUNS_ROOT",tmp_path/"runs")
    run=ws.allocate_run("BL-0001","pilot_S001_001")
    dest=ws.artifact_destination(run,"S001_source_image.png","screenshots")
    assert dest.parent == run/"screenshots"
    dest.write_bytes(b"test-evidence")
    with pytest.raises(FileExistsError):
        ws.artifact_destination(run,"S001_source_image.png","screenshots")

@pytest.mark.parametrize("filename,category",[
    ("../token.txt","screenshots"),("secret.png","../../Downloads"),
    (".","prompts"),("foo","private"),("C:\\temp\\oops.png","videos"),
])
def test_artifact_refuses_path_traversal(tmp_path,monkeypatch,filename,category):
    monkeypatch.setattr(ws,"RUNS_ROOT",tmp_path/"runs")
    run=ws.allocate_run("BL-0001","pilot_S001_001")
    with pytest.raises(ValueError):
        ws.artifact_destination(run,filename,category)

def test_artifact_refuses_outside_directory(tmp_path,monkeypatch):
    monkeypatch.setattr(ws,"RUNS_ROOT",tmp_path/"runs")
    with pytest.raises(ValueError):
        ws.artifact_destination(tmp_path/"other","test.png","screenshots")
