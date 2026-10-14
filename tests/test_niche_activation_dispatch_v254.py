"""Regression: user-approved niche instantly dispatches scoped public research."""
import importlib.util
import json
import sys
from pathlib import Path
import pytest
from cinefactory.studio.two_track_research_v201 import DualResearchStore

SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"run_two_track_research_v201.py"

def load_script():
    spec=importlib.util.spec_from_file_location("daily_activation_v254_test", SCRIPT)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_explicit_niche_approval_starts_research_without_waiting_for_schedule(tmp_path,monkeypatch,capsys):
    mod=load_script()
    monkeypatch.setattr(mod,"ROOT",tmp_path)
    invoked=[]
    def scan(**kwargs):
        invoked.append(kwargs)
        return {"status":"APPROVED_DEEP_KEYWORD_RESEARCH_RECORDED",
                "full_metadata_checks":12}
    def generate(_root):
        return {"branch_1_global_new_niche_scan":{
                    "status":"NO_EMPIRICAL_WINNING_NICHE_CONFIRMED",
                    "verified_born_0_30d_channels_in_ledger":0,
                    "candidate_fingerprint_proposals":[]},
                "branch_2_approved_niche_studies":{
                    "status":"APPROVED_NICHE_SOURCE_RESEARCH_PENDING_CREATIVE_VERIFICATION",
                    "approved_format_count":1},
                "report_path":"test.json",
                "data_sources":{"public_video_snapshots":12}}
    monkeypatch.setattr(mod,"search_approved_formats",scan)
    monkeypatch.setattr(mod,"generate_two_track_daily",generate)
    monkeypatch.setattr(mod,"write_owner_briefs",lambda *args:{
       "branch_1_markdown":"b1.md","branch_2_markdown":"b2.md","approved_niche_agent_packets":[]})
    monkeypatch.setattr(sys,"argv",["daily","--approve-niche","minecraft","minecraft_animation",
                                   "--confirmation","DUYET minecraft minecraft_animation"])
    mod.main()
    approvals=DualResearchStore(tmp_path/"data/research/youtube_breakout/cinefactory_breakout.sqlite3").approvals()
    assert [(a["niche_id"],a["format_id"],a["state"]) for a in approvals]==[
           ("minecraft","minecraft_animation","APPROVED")]
    assert len(invoked)==1
    assert invoked[0]["per_niche_keywords"]==4
    assert invoked[0]["per_query"]==20
    assert invoked[0]["max_total_metadata"]==48
    assert "NICHE_DEEP_RESEARCH_USER_APPROVED" in capsys.readouterr().out

def test_without_user_confirmation_fails_closed_no_scanning(tmp_path,monkeypatch):
    mod=load_script()
    monkeypatch.setattr(mod,"ROOT",tmp_path)
    hits=[]
    monkeypatch.setattr(mod,"search_approved_formats",lambda **k:hits.append(k))
    monkeypatch.setattr(sys,"argv",["daily","--approve-niche","minecraft","minecraft_gameplay"])
    with pytest.raises(PermissionError,match="CONFIRM"):
        mod.main()
    assert hits==[]
    assert DualResearchStore(tmp_path/"data/research/youtube_breakout/cinefactory_breakout.sqlite3").approvals()==[]

def test_discovered_candidate_rivals_are_not_automatically_verified(tmp_path):
    from cinefactory.studio.approved_niche_keyword_scan_v201 import search_approved_formats
    from cinefactory.studio.daily_youtube_breakout_v199 import PublicVideo
    store=DualResearchStore(tmp_path/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",
                  note="Explicit",at="2026-10-11T00:00:00+00:00")
    class Stub:
        def search(self,phrase,*,limit):
            return [{"id":"BARbfz8ik8k"}]
        def video(self,video_id,*,lane):
            return PublicVideo.parse({
                "id":video_id,"title":"JJ vs Mikey - Minecraft Animation Movie",
                "upload_date":"20261005","duration":1324,
                "view_count":1500000,"channel_id":"UC"+"x"*22,
                "channel":"Rival Studio","was_live":False},lane)
    from datetime import datetime,timezone
    r=search_approved_formats(root=tmp_path,client=Stub(),
                              as_of=datetime(2026,10,11,tzinfo=timezone.utc),
                              per_niche_keywords=1,max_total_metadata=4)
    assert len(r["candidate_competitor_channels"])==1
    candidate=r["candidate_competitor_channels"][0]
    assert candidate["channel_name"]=="Rival Studio"
    assert candidate["candidate_video_ids"]==["BARbfz8ik8k"]
    assert candidate["verified_same_format_competitor"] is False
    assert candidate["needs_full_av_and_channel_origin_review"] is True

def test_legacy_one_format_per_niche_schema_migrates_without_losing_approvals(tmp_path):
    import sqlite3
    path=tmp_path/"old.sqlite3"
    with sqlite3.connect(path) as conn:
        conn.execute("""CREATE TABLE research_niche_approvals(
          niche_id TEXT PRIMARY KEY,format_id TEXT NOT NULL,
          state TEXT NOT NULL,approved_by TEXT NOT NULL,
          approval_note TEXT NOT NULL, approved_at TEXT NOT NULL)""")
        conn.execute("""INSERT INTO research_niche_approvals
          VALUES(?,?,?,?,?,?)""",("minecraft","minecraft_gameplay","APPROVED",
          "USER_EXPLICIT_APPROVAL","Legacy choice","2026-10-10T00:00:00+00:00"))
    store=DualResearchStore(path)
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",
                  note="Second format",at="2026-10-11T00:00:00+00:00")
    vals={(a["niche_id"],a["format_id"]) for a in store.approvals()}
    assert vals=={("minecraft","minecraft_gameplay"),("minecraft","minecraft_animation")}
    assert sqlite3.connect(path).execute("pragma integrity_check").fetchone()[0]=="ok"
    # Opening again must be idempotent.
    assert len(DualResearchStore(path).approvals())==2
