"""v209 enterprise production gates: fail-closed, real-signed, still source-honest."""
from __future__ import annotations
import base64
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import pytest
from typer.testing import CliRunner
from typer import Exit

from cinefactory.cli import app,_require_required_company_handlers
from cinefactory.domain.models import DialogueLine,ScriptScene,ScriptSpec
from cinefactory.studio.script_continuity_v209 import inspect_script_continuity
from cinefactory.studio.film_release_gate_v209 import review_original_master
from cinefactory.studio.operational_readiness_v209 import (
    audit_company_readiness,required_handler_gaps,
)
from cinefactory.studio.company import CompanyOrchestrator,CompanyStage
from cinefactory.studio.company_runner import StageHandlerRegistry,StageHandlerResult
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.contracts import StudioProjectSpec


def scene(name,event,action=("Somebody acts",),entry=None,exit=None):
    return ScriptScene(scene_id=name,heading=name,location_id="loc_1",
                       time_of_day="DAY",dramatic_event=event,
                       action=list(action),entry_state_summary=entry,
                       exit_state_summary=exit)


def script(scenes):
    return ScriptSpec(title="An original story",logline="Someone seeks a friend",
                      scenes=scenes)


def test_structural_story_check_is_no_longer_fake_semantic_pass():
    report,contract=inspect_script_continuity(script([
        scene("s1","The friend leaves"),
        scene("s2","The protagonist searches for their missing friend"),
    ]))
    assert report["passed"] is True
    assert report["status"]=="STRUCTURAL_CHECK_PASSED_SEMANTIC_REVIEW_PENDING"
    assert report["independent_narrative_quality_qualified"] is False
    assert report["causal_motivation_qualified"] is False
    assert contract["independently_approved"] is False
    assert len(contract["scene_transitions"])==1
    assert contract["scene_transitions"][0]["causality_proven"] is False


def test_actual_declared_state_contradiction_blocks():
    report,contract=inspect_script_continuity(script([
        scene("s1","The gate closes",exit="STATE_ID=door_closed"),
        scene("s2","The gate is open",entry="STATE_ID=door_open"),
    ]))
    assert report["passed"] is False
    assert report["status"]=="BLOCKED_MECHANICAL_CONTRADICTIONS"
    assert "CONTRADICTORY_DECLARED_WORLD_STATE" in [
        x["code"] for x in report["findings"]
    ]
    assert contract["scene_transitions"][0]["structured_state_compatible"] is False


def test_scene_without_performable_content_blocks():
    report,_=inspect_script_continuity(script([
        scene("s1","Something mysteriously changes",action=()),
    ]))
    assert not report["passed"]
    assert "SCENE_WITHOUT_OBSERVABLE_ACTION_OR_DIALOGUE" in {
        f["code"] for f in report["findings"]
    }


def test_matching_structured_state_is_checked_not_inferred():
    report,contract=inspect_script_continuity(script([
        scene("s1","A promise is made",exit="STATE_ID=promise_made"),
        scene("s2","The friend responds",entry="STATE_ID=promise_made"),
    ]))
    assert report["passed"]
    assert contract["scene_transitions"][0]["structured_state_compatible"] is True
    assert contract["scene_transitions"][0]["physical_screen_direction_proven"] is False


def test_new_generic_studio_project_uses_professional_governance(tmp_path):
    bp=CompanyOrchestrator(build_studio_kernel(tmp_path)).build_blueprint(
        StudioProjectSpec(prompt="An original cinematic friendship tale",
                          duration_seconds=60),
    )
    assert bp.strict_stage_receipts
    assert {"PROJECT_INTAKE","CORPORATE_PREFLIGHT","PORTFOLIO_GREENLIGHT"} <= {
        x.stage_id for x in bp.stages
    }
    assert not bp.executable
    assert "UNCLASSIFIED_NICHE_REQUIRES_OWNER_GREENLIGHT" in bp.blockers


def test_explicit_legacy_blueprint_opt_out_remains_available(tmp_path):
    bp=CompanyOrchestrator(build_studio_kernel(tmp_path)).build_blueprint(
        StudioProjectSpec(prompt="An original family story",
                          duration_seconds=60),
        professional_governance=False,
    )
    assert bp.strict_stage_receipts is False


def test_missing_required_handlers_block_before_any_render(capsys):
    stages=[
        CompanyStage(stage_id="PROJECT_INTAKE",owner="STUDIO_MANAGEMENT",
                     artifacts_in=["project_brief"],artifacts_out=["project_intake"]),
        CompanyStage(stage_id="VOICE_PREP",owner="AUDIO",
                     artifacts_in=["project_intake"],artifacts_out=["voice_tracks"]),
    ]
    register=StageHandlerRegistry()
    register.register("PROJECT_INTAKE",lambda x:StageHandlerResult(ok=True))
    assert required_handler_gaps(stages,register)==["VOICE_PREP"]
    bp=SimpleNamespace(strict_stage_receipts=True,
                       stages=stages,project=SimpleNamespace(studio_project_id="TEST"))
    with pytest.raises(Exit) as err:
        _require_required_company_handlers(bp,register)
    assert err.value.exit_code==2
    assert "VOICE_PREP" in capsys.readouterr().out


def _generate_signed_reviews(tmp_path,media,project_dir):
    master_sig={}
    key_map={}
    for gate in ("story","acting_identity","camera_edit","sound","rights","originality"):
        key=Ed25519PrivateKey.generate()
        pub=tmp_path/(gate+".pub.pem")
        pub.write_bytes(key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo))
        reviewer_id="independent_"+gate
        key_map[reviewer_id]=str(pub)
        payload={
            "schema":"cine.film.signed_review.v205",
            "gate":gate,"decision":"ACCEPT",
            "master_sha256":media["sha256"],
        }
        encoded=json.dumps(payload,sort_keys=True,separators=(",",":"),
                           ensure_ascii=False).encode("utf8")
        master_sig[gate]={
            "reviewer_id":reviewer_id,"payload":payload,
            "signature_b64":base64.b64encode(key.sign(encoded)).decode("ascii"),
        }
    key_file=tmp_path/"externally_trusted_reviewer_keys.json"
    key_file.write_text(json.dumps(key_map),encoding="utf8")
    review_file=project_dir/"inputs"/"independent_film_reviews.json"
    review_file.write_text(json.dumps(master_sig),encoding="utf8")
    return key_file,review_file,master_sig


def test_film_release_requires_real_master_and_independent_reviewers(tmp_path,monkeypatch):
    project=tmp_path/"project"
    inputs=project/"inputs"
    inputs.mkdir(parents=True)
    master=tmp_path/"original_master.mp4"
    master.write_bytes(b"test fixture for cryptographic path only")
    media={"sha256":hashlib.sha256(master.read_bytes()).hexdigest(),
           "technical_pass":True,"technical_findings":[],
           "schema":"cine.film.longform_technical_evidence.v205"}
    import cinefactory.studio.film_release_gate_v209 as gate
    monkeypatch.setattr(gate,"probe_film",lambda *a,**k:media)
    no_review=review_original_master(project,master,duration_target=60)
    assert not no_review["release_permission"]
    assert no_review["status"]=="WAITING_SIGNED_INDEPENDENT_FILM_REVIEWS"
    key_file,review_file,reviews=_generate_signed_reviews(tmp_path,media,project)
    denied=review_original_master(project,master,duration_target=60)
    assert denied["status"]=="EXTERNAL_REVIEWER_TRUST_ROOT_REQUIRED"
    accepted=review_original_master(
        project,master,duration_target=60,trusted_key_map_file=key_file,
    )
    assert accepted["release_permission"]
    assert accepted["reviewer_count"]==6
    assert accepted["master_sha256"]==media["sha256"]
    assert accepted["scope"]=="ORIGINAL_PILOT"
    # Signing this hash does not authorize a different movie.
    reviews["story"]["payload"]["master_sha256"]="f"*64
    review_file.write_text(json.dumps(reviews),encoding="utf8")
    tampered=review_original_master(
        project,master,duration_target=60,trusted_key_map_file=key_file,
    )
    assert tampered["release_permission"] is False
    assert tampered["status"]=="PENDING_AUTHENTICATED_REVIEW"


def test_project_owned_trust_keys_are_rejected(tmp_path,monkeypatch):
    project=tmp_path/"project"
    (project/"inputs").mkdir(parents=True)
    master=tmp_path/"movie.mp4"
    master.write_bytes(b"movie test")
    media={"sha256":hashlib.sha256(master.read_bytes()).hexdigest(),
           "technical_pass":True,"technical_findings":[],
           "schema":"cine.film.longform_technical_evidence.v205"}
    import cinefactory.studio.film_release_gate_v209 as gate
    monkeypatch.setattr(gate,"probe_film",lambda *a,**k:media)
    trust,_,_=_generate_signed_reviews(project,media,project)
    denied=review_original_master(
        project,master,duration_target=60,trusted_key_map_file=trust,
    )
    assert not denied["release_permission"]
    assert denied["status"]=="FILM_REVIEW_PROVENANCE_REJECTED"


def test_unqualified_duration_rejected_without_media_probe(tmp_path):
    project=tmp_path/"project";project.mkdir()
    master=tmp_path/"fake.mp4";master.write_bytes(b"fake")
    x=review_original_master(project,master,duration_target=300)
    assert x["status"]=="BLOCKED_UNSUPPORTED_RELEASE_DURATION"


def test_stale_turbo_worker_is_not_a_live_worker(tmp_path):
    db=tmp_path/"data"/"turbo.db"
    db.parent.mkdir(parents=True)
    with sqlite3.connect(db) as c:
        c.execute("create table workers(worker_id text,healthy int,last_heartbeat text)")
        c.execute("create table work_items(state text)")
        c.execute("insert into workers values(?,?,?)",(
            "zombie",1,"2026-10-01T01:00:00+00:00"))
        c.execute("insert into work_items values('SUCCESS')")
    now=datetime(2026,10,10,8,tzinfo=timezone.utc)
    audit=audit_company_readiness(tmp_path,now=now)
    assert audit["department_counts"]=={"declared":26,"specified":26}
    assert audit["workers"]["stored_workers"]==1
    assert audit["workers"]["active_fresh_workers"]==0
    assert audit["workers"]["stale_reported_healthy"]==1
    assert audit["film"]["accepted_verified_longform_count"]==0
    assert audit["production_ready"] is False
    assert len(audit["niches"])==7
    assert all(x["wiring_pass"] for x in audit["niches"].values())


def test_readiness_cli_reports_not_qualified_without_fake_green():
    result=CliRunner().invoke(app,["company-readiness"])
    assert result.exit_code==0,result.output[-1200:]
    report=json.loads(result.output)
    assert report["verdict"]=="NOT_PRODUCTION_QUALIFIED"
    assert report["department_counts"]["specified"]==26
    assert report["film"]["accepted_verified_longform_count"]==0
    assert report["production_ready"] is False


def test_readiness_correctly_decodes_powershell_utf16_logs_and_keeps_partial_research(tmp_path):
    logfile=tmp_path/"data"/"research"/"youtube_breakout"/"logs"/"scheduled_cinefactory_20261010_080000.log"
    logfile.parent.mkdir(parents=True)
    scout={"status":"RESEARCH_PARTIAL","full_video_decoded":False}
    branch={"branch1_status":"NO_EMPIRICAL_WINNING_NICHE_CONFIRMED",
            "branch2_status":"NO_USER_APPROVED_NICHES"}
    logfile.write_text(
        "CINEFACTORY_REAL_DAILY_SCOUT_RESULT "+json.dumps(scout)+"\n"
        +"CINEFACTORY_TWO_BRANCH_DAILY_REPORT "+json.dumps(branch)+"\n",
        encoding="utf-16",
    )
    audit=audit_company_readiness(tmp_path,now=datetime(2026,10,10,8,tzinfo=timezone.utc))
    research=audit["research"]
    assert research["daily_scout_state"]=="RESEARCH_PARTIAL"
    assert research["new_niche_branch_status"]=="NO_EMPIRICAL_WINNING_NICHE_CONFIRMED"
    assert audit["production_ready"] is False


def test_active_worker_requires_fresh_heartbeat_not_historical_bool(tmp_path):
    db=tmp_path/"data"/"turbo.db";db.parent.mkdir(parents=True)
    with sqlite3.connect(db) as conn:
        conn.execute("create table workers(worker_id text,healthy int,last_heartbeat text)")
        conn.execute("create table work_items(state text)")
        conn.execute("insert into workers values(?,?,?)",(
            "qualifying_running_worker",1,"2026-10-10T07:55:00+00:00"))
        conn.execute("insert into work_items values(?)",("RUNNING",))
    now=datetime(2026,10,10,8,tzinfo=timezone.utc)
    audit=audit_company_readiness(tmp_path,now=now)
    assert audit["workers"]["active_fresh_workers"]==1
    assert audit["workers"]["open_work_items"]==1
    # Worker heartbeat alone never validates story, media, research, and rights.
    assert audit["production_ready"] is False
