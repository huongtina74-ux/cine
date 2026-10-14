"""CineFactory v205 end-to-end contracts with synthetic evidence and mock provider.

Fixtures are not YouTube facts, owner consent or accepted professional movies.
"""
from __future__ import annotations
import base64
import hashlib
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from cinefactory.studio.contracts import DepartmentId,MediaFormat
from cinefactory.studio.departments import DEFAULT_DEPARTMENTS,default_department_registry
from cinefactory.studio.department_charters_v205 import specialist_operational_readiness
from cinefactory.studio.company import stage_blueprint
from cinefactory.studio.company_handlers import FilmCompanyHandlers
from cinefactory.studio.contract_integrity import audit_company_wiring
from cinefactory.studio.specialist_media_lanes_v205 import LANES
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.research_studio_handoff_v205 import (
    create_studio_work_order,verify_studio_work_order,validate_breakout_evidence,
)
from cinefactory.studio.longform_acceptance_v205 import (
    independent_film_acceptance,
)
from cinefactory.studio.distribution_learning_v205 import (
    build_release_intent,upload_private_with_approval,ingest_owned_analytics,
)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def keypair(tmp_path, name):
    private=Ed25519PrivateKey.generate()
    keypath=tmp_path/f"{name}.pem"
    keypath.write_bytes(private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    return private,keypath

def signed(pri,payload):
    return base64.b64encode(pri.sign(canonical(payload))).decode()

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj),encoding="utf8")
    return path

def test_all_26_departments_have_distinct_charters_but_not_fake_qualifications():
    assert len(DEFAULT_DEPARTMENTS)==len(DepartmentId)==26
    assert len(default_department_registry().list())==26
    assert all(d.mission and d.skills and d.reads and d.writes and d.qc_gates
               for d in DEFAULT_DEPARTMENTS.values())
    status=specialist_operational_readiness(set(),set())
    assert len(status)==11
    assert all(v["status"]=="CHARTER_ONLY" for v in status.values())

@pytest.mark.parametrize("niche",sorted(LANES))
def test_each_nonanimation_has_specialist_producer_wiring_and_real_handler(niche,tmp_path):
    stages=stage_blueprint(MediaFormat.DOCUMENTARY,False,
                           professional_governance=True,professional_niche=niche)
    assert len(stages)==10
    assert audit_company_wiring(stages).valid
    assert not {"ASSET_BUILD","PREVIS","DIRECTION","PERFORMANCE"} & {s.stage_id for s in stages}
    handlers=FilmCompanyHandlers(build_studio_kernel(tmp_path)).registry(niche=niche)
    assert all(handlers.get(s.stage_id) is not None for s in stages)

@pytest.mark.parametrize("niche",sorted(LANES))
def test_unapproved_media_studio_has_no_validated_research_source(niche,tmp_path):
    from cinefactory.studio.company import CompanyOrchestrator
    from cinefactory.studio.contracts import StudioProjectSpec
    kernel=build_studio_kernel(tmp_path)
    bp=CompanyOrchestrator(kernel).build_blueprint(StudioProjectSpec(
        prompt="Create an original longform episode",niche=niche,
        duration_seconds=540),professional_governance=True)
    assert bp.strict_stage_receipts
    assert not bp.portfolio_greenlight.approved_for_production
    assert "NICHE_PRODUCTION_NOT_GREENLIT" in bp.blockers
    assert bp.stages[0].stage_id=="NICHE_PROJECT_INTAKE"

def source_evidence(now):
    cid="UC"+"a"*22
    vids=[{
        "video_id":"VIDEO000001"+str(i),"channel_id":cid,
        "published_at":(now-timedelta(days=i+1)).isoformat(),
        "duration_seconds":540,"views":1_400_000,
        "evidence_status":"VERIFIED_OFFICIAL_API",
    } for i in (1,2)]
    return {
        "schema":"cine.research.source_bundle.v205",
        "source_tier":"OFFICIAL_API_ARCHIVED_AND_HUMAN_REVIEWED",
        "source_digest_sha256":"a"*64,"reviewer_evidence_id":"review-001",
        "niche":"minecraft","breakout_channel":{
            "channel_id":cid,"created_at":(now-timedelta(days=10)).isoformat(),
            "videos":vids},
        "evergreen_witnesses":[{
            "video_id":"MATURE_VIDEO_001",
            "channel_id":"UC"+"b"*22,
            "published_at":(now-timedelta(days=7)).isoformat(),
            "recent_views":250_000,
            "evidence_status":"VERIFIED_OFFICIAL_API"}],
    }

def test_research_to_studio_owner_signed_work_order_and_tamper_gate(tmp_path):
    now=datetime.now(timezone.utc)
    root=tmp_path/"Company Youtube"
    root.mkdir()
    bridge=write(root/"imported_bridge.json",{"source":"TEST_FIXTURE_ONLY"})
    pod=write(tmp_path/"pod.json",{
        "schema":"cine.niche.pod.v1","niche":"minecraft",
        "state":"CONFIGURED_NOT_SCHEDULED",
        "approval_id":"OWNER_RESEARCH_APPROVAL_FIXTURE",
        "bridge_source":str(bridge),"bridge_sha256":digest(bridge),
    })
    ev=write(tmp_path/"evidence.json",source_evidence(now))
    private,public=keypair(tmp_path,"trusted_owner")
    payload={
        "pod_sha256":digest(pod),"evidence_sha256":digest(ev),
        "bridge_sha256":digest(bridge),"niche":"minecraft",
        "decision":"APPROVE_ORIGINAL_PILOT_PRODUCTION",
        "project_id":"TEST_PROJECT_1","output_mode":"LOCAL_NO_METERED_API",
        "issued_at":now.isoformat(),
    }
    approval=write(tmp_path/"authorization.json",{
        "schema":"cine.owner.production_authorization.v205",
        "niche":"minecraft","payload":payload,
        "signature_b64":signed(private,payload),
    })
    out=tmp_path/"approved_workorder.json"
    packet=create_studio_work_order(pod,ev,approval,public,out,now=now)
    assert packet["production_permission"] is True
    assert verify_studio_work_order(out,trusted_public_key=public)["pilot_only"]
    wrong_pri,wrong_pub=keypair(tmp_path,"untrusted")
    with pytest.raises(Exception):
        verify_studio_work_order(out,trusted_public_key=wrong_pub)
    evidence=json.loads(ev.read_text(encoding="utf8"))
    evidence["breakout_channel"]["videos"][0]["views"]=34
    write(ev,evidence)
    with pytest.raises(ValueError,match="UPSTREAM_SOURCE_CHANGED"):
        verify_studio_work_order(out,trusted_public_key=public)

def test_source_proof_rejects_one_breakout_even_if_declared_verified():
    now=datetime.now(timezone.utc)
    proof=source_evidence(now)
    proof["breakout_channel"]["videos"][0]["views"]=900_000
    with pytest.raises(ValueError,match="TWO_BREAKOUTS"):
        validate_breakout_evidence(proof,at=now)

def test_independent_film_review_requires_six_distinct_valid_signatures(tmp_path):
    digest_value="1"*64
    tech={"technical_pass":True,
          "sha256":digest_value,
          "schema":"cine.film.longform_technical_evidence.v205"}
    assert independent_film_acceptance(tech,{},{} )["release_permission"] is False
    gates=("story","acting_identity","camera_edit","sound","rights","originality")
    reviews,trust={},{}
    for i,g in enumerate(gates):
        pri,pub=keypair(tmp_path,f"reviewer{i}")
        payload={"schema":"cine.film.signed_review.v205",
                 "gate":g,"decision":"ACCEPT","master_sha256":digest_value}
        reviews[g]={"reviewer_id":f"reviewer{i}","payload":payload,
                    "signature_b64":signed(pri,payload)}
        trust[f"reviewer{i}"]=str(pub)
    accepted=independent_film_acceptance(tech,reviews,trust)
    assert accepted["release_permission"] is True
    reviews["rights"]["payload"]["master_sha256"]="WRONG"
    assert independent_film_acceptance(tech,reviews,trust)["release_permission"] is False

def test_private_upload_and_owner_metric_provenance_mock_only(tmp_path):
    film=tmp_path/"original.mp4"
    film.write_bytes(b"fixture_not_real_film")
    h=digest(film)
    qc={"release_permission":True,"master_sha256":h}
    channel="UC"+"k"*22
    metadata={"title":"Original fixture only","description":"Fixture not an upload",
              "visibility":"private","made_for_kids":False}
    intent=build_release_intent(film,channel,metadata,qc)
    assert intent["state"]=="AWAITING_OWNER_AUTHENTICATION"
    pub,owner_key=keypair(tmp_path,"upload_owner")
    payload={"master_sha256":h,"channel_id":channel,
             "metadata_sha256":intent["metadata_sha256"],
             "scope":"UPLOAD_PRIVATE_ONLY","decision":"APPROVED",
             "issued_at":datetime.now(timezone.utc).isoformat()}
    event={"schema":"cine.owner.youtube_private_upload.v205",
           "payload":payload,"signature_b64":signed(pub,payload)}
    class FakeOwnedTransport:
        def __init__(self):self.uploaded=0
        def upload_private(self,path,meta):
            self.uploaded+=1
            return "VIDEO_FIXTURE"
        def fetch_video(self,video_id):
            return {"id":video_id,"channel_id":channel,"privacy_status":"private"}
    transport=FakeOwnedTransport()
    with pytest.raises(Exception):
        upload_private_with_approval(intent,dict(event,signature_b64="bogus"),
                                     transport,trusted_owner_public_key=owner_key)
    assert transport.uploaded==0
    receipt=upload_private_with_approval(
        intent,event,transport,trusted_owner_public_key=owner_key,
        idempotency_reservation=tmp_path/"immutable_upload_attempt.json")
    assert receipt["state"]=="UPLOADED_PRIVATE_VERIFIED"
    durable=tmp_path/"immutable_upload_attempt.verified_receipt.json"
    assert durable.is_file()
    assert json.loads(durable.read_text(encoding="utf8"))["video_id"]=="VIDEO_FIXTURE"
    assert transport.uploaded==1
    with pytest.raises(FileExistsError):
        upload_private_with_approval(
            intent,event,transport,trusted_owner_public_key=owner_key,
            idempotency_reservation=tmp_path/"immutable_upload_attempt.json")
    assert transport.uploaded==1
    values={"video_id":"VIDEO_FIXTURE","window_start":"2026-10-01",
            "window_end":"2026-10-09","views":120,"watch_minutes":850}
    provenance={"provider":"YOUTUBE_ANALYTICS_API",
                "authenticated_provider_readback":True,
                "channel_id":channel,"video_id":"VIDEO_FIXTURE"}
    obs=ingest_owned_analytics(receipt,values,provenance)
    assert obs["metrics"]["views"]==120 and obs["learning_promoted"] is False
    provenance["channel_id"]="UCwrong"
    with pytest.raises(PermissionError,match="PROVENANCE"):
        ingest_owned_analytics(receipt,values,provenance)

def test_asmr_local_owned_media_can_be_encoded_but_not_film_approved(tmp_path,monkeypatch):
    """Two generated 1s DIAGNOSTIC clips: verify executable FFmpeg lane only."""
    import shutil,subprocess
    from cinefactory.studio.company import CompanyOrchestrator
    from cinefactory.studio.contracts import StudioProjectSpec
    from cinefactory.studio.company_runner import StageExecutionContext
    from cinefactory.studio.specialist_media_handlers_v205 import (
        niche_rights_and_sources,niche_media_assembly,
        niche_sound_quality,niche_film_qc,
    )
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("Local FFmpeg/FFprobe not installed")
    project_root=tmp_path/"project"
    inputs=project_root/"inputs"
    inputs.mkdir(parents=True)
    clips=[]
    for i,col in enumerate(("blue","red")):
        clip=inputs/f"diagnostic_{i}.mp4"
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error",
            "-f","lavfi","-i",f"color=c={col}:s=640x360:r=24:d=1",
            "-f","lavfi","-i","sine=frequency=440:duration=1",
            "-c:v","libx264","-pix_fmt","yuv420p",
            "-c:a","aac","-shortest","-y",str(clip)],
            capture_output=True,check=True,timeout=60)
        rights=inputs/f"diagnostic_{i}_rights.txt"
        rights.write_text("TEST FIXTURE GENERATED BY OUR TEST CODE; NOT A REAL ART LICENSE")
        clips.append({"file":clip.name,"sha256":digest(clip),
                      "rights_evidence":rights.name,"rights_sha256":digest(rights),
                      "license_scope":"OWNED_ORIGINAL"})
    manifest=write(inputs/"media_manifest.json",{
        "schema":"cine.owner_media.v205",
        "niche":"asmr_sleep_hands_objects","clips":clips,
    })
    kernel=build_studio_kernel(tmp_path)
    blueprint=CompanyOrchestrator(kernel).build_blueprint(StudioProjectSpec(
        prompt="ASMR original hands/object video",
        niche="asmr_sleep_hands_objects",duration_seconds=540),
        professional_governance=True)
    # Fixture overrides a simulated research greenlight; NO such evidence exists
    # in the actual production system and this test MUST NOT promote it.
    greenlight=blueprint.portfolio_greenlight.model_copy(
        update={"approved_for_production":True})
    blueprint=blueprint.model_copy(update={"portfolio_greenlight":greenlight})
    pri,pub=keypair(tmp_path,"rights")
    monkeypatch.setenv("CINEFACTORY_RIGHTS_TRUST_PUBKEY",str(pub))
    payload={"manifest_sha256":digest(manifest),
             "niche":"asmr_sleep_hands_objects",
             "project_id":blueprint.project.studio_project_id,
             "decision":"CLEAR_ORIGINAL_LOCAL_PRODUCTION","scope":"PROJECT_ONLY"}
    write(inputs/"rights_authorization.json",{
        "schema":"cine.rights.signed_clearance.v205",
        "payload":payload,"signature_b64":signed(pri,payload)})
    def stage(name):
        entry=next(v for v in blueprint.stages if v.stage_id==name)
        return StageExecutionContext(blueprint=blueprint,stage=entry,
                                     kernel=kernel,project_root=project_root)
    assert niche_rights_and_sources(stage("NICHE_RIGHTS_AND_SOURCES")).ok
    assembled=niche_media_assembly(stage("NICHE_MEDIA_ASSEMBLY"))
    assert assembled.ok,assembled.error
    movie=project_root/"master"/"niche_original_assembly.mp4"
    assert movie.is_file() and movie.stat().st_size>10000
    assert niche_sound_quality(stage("NICHE_SOUND_QUALITY")).ok
    qc=niche_film_qc(stage("NICHE_FILM_QC"))
    assert qc.ok is False
    assert qc.error=="SIX_SIGNED_INDEPENDENT_FILM_REVIEWS_REQUIRED"
    assert not (project_root/"master"/"release.mp4").exists()

def test_signed_approved_work_order_unlocks_original_pilot_only(tmp_path,monkeypatch):
    from cinefactory.studio.company import CompanyOrchestrator
    from cinefactory.studio.contracts import StudioProjectSpec
    now=datetime.now(timezone.utc)
    project_id="PILOT_SOURCE_001"
    project_root=tmp_path/"data"/"projects"/project_id
    inputs=project_root/"inputs"
    inputs.mkdir(parents=True)
    bridge=write(tmp_path/"company_import.json",{"fixture_only":True})
    proof=source_evidence(now)
    proof["niche"]="asmr_sleep_hands_objects"
    pod=write(tmp_path/"approved_pod.json",{
        "schema":"cine.niche.pod.v1","niche":proof["niche"],
        "state":"CONFIGURED_NOT_SCHEDULED",
        "approval_id":"TEST_ONLY_SOURCE_APPROVAL",
        "bridge_source":str(bridge),"bridge_sha256":digest(bridge)})
    evidence=write(tmp_path/"signed_pilot_evidence.json",proof)
    pri,pub=keypair(tmp_path,"pilot_authority")
    signed_payload={
        "pod_sha256":digest(pod),"evidence_sha256":digest(evidence),
        "bridge_sha256":digest(bridge),"niche":proof["niche"],
        "decision":"APPROVE_ORIGINAL_PILOT_PRODUCTION",
        "project_id":project_id,"output_mode":"LOCAL_NO_METERED_API",
        "issued_at":now.isoformat(),
    }
    approval=write(tmp_path/"authorization.json",{
        "schema":"cine.owner.production_authorization.v205",
        "niche":proof["niche"],"payload":signed_payload,
        "signature_b64":signed(pri,signed_payload),
    })
    create_studio_work_order(
        pod,evidence,approval,pub,
        inputs/"approved_studio_work_order.json",now=now)
    monkeypatch.setenv("CINEFACTORY_OWNER_TRUST_PUBKEY",str(pub))
    kernel=build_studio_kernel(tmp_path)
    project=StudioProjectSpec(prompt="ASMR locally approved ORIGINAL PILOT",
                              niche=proof["niche"],
                              studio_project_id=project_id,
                              duration_seconds=60)
    blueprint=CompanyOrchestrator(kernel).build_blueprint(
        project,professional_governance=True)
    assert blueprint.pilot_only is True
    assert blueprint.approved_pilot_work_order_sha256
    assert blueprint.portfolio_greenlight.approved_for_production is True
    assert "NICHE_PRODUCTION_NOT_GREENLIT" not in blueprint.blockers
    assert blueprint.stages[0].stage_id=="NICHE_PROJECT_INTAKE"
    with pytest.raises(PermissionError,match="SIGNED_PILOT_ONLY"):
        CompanyOrchestrator(kernel).build_blueprint(
            project.model_copy(update={"duration_seconds":540}),
            professional_governance=True,
        )
    wrong_pub=keypair(tmp_path,"wrong_owner")[1]
    monkeypatch.setenv("CINEFACTORY_OWNER_TRUST_PUBKEY",str(wrong_pub))
    with pytest.raises(Exception):
        CompanyOrchestrator(kernel).build_blueprint(
            project,professional_governance=True)

def test_orchestrator_selects_native_media_lane_from_explicit_niche_even_if_planner_says_narrative(tmp_path):
    from cinefactory.studio.company import CompanyOrchestrator
    from cinefactory.studio.contracts import StudioProjectSpec
    engine=CompanyOrchestrator(build_studio_kernel(tmp_path))
    bp=engine.build_blueprint(StudioProjectSpec(
        prompt="Create an original ASMR hands sleep sound video",
        niche="asmr_sleep_hands_objects",
        duration_seconds=540,
    ),professional_governance=True)
    ids=[s.stage_id for s in bp.stages]
    assert ids[0]=="NICHE_PROJECT_INTAKE"
    assert len(ids)==10
    assert "NICHE_SOUND_QUALITY" in ids
    assert "STORYBOARD_EDITORIAL" not in ids
    assert "ASSET_BUILD" not in ids
    assert bp.portfolio_greenlight.approved_for_production is False


def test_metadata_change_after_signed_private_approval_is_rejected(tmp_path):
    master=tmp_path/"master.mp4"
    master.write_bytes(b"test_fixture_not_an_accepted_real_video")
    h=digest(master)
    channel="UC"+"q"*22
    metadata={"title":"Original","description":"No ads",
              "visibility":"private","made_for_kids":False}
    qc={"release_permission":True,"master_sha256":h}
    intent=build_release_intent(master,channel,metadata,qc)
    private,pub=keypair(tmp_path,"owner_for_metadata")
    payload={"master_sha256":h,"channel_id":channel,
             "metadata_sha256":intent["metadata_sha256"],
             "scope":"UPLOAD_PRIVATE_ONLY","decision":"APPROVED",
             "issued_at":datetime.now(timezone.utc).isoformat()}
    signature=signed(private,payload)
    event={"schema":"cine.owner.youtube_private_upload.v205",
           "payload":payload,"signature_b64":signature}
    attempts=[]
    class FakeTransport:
        owned_channel_id=channel
        def upload_private(self,*args,**kwargs):
            attempts.append(1)
            raise RuntimeError("Should never upload")
    intent["metadata"]["title"]="Changed without fresh signed owner consent"
    with pytest.raises(PermissionError,match="APPROVAL_SCOPE"):
        upload_private_with_approval(
            intent,event,FakeTransport(),trusted_owner_public_key=pub,
            idempotency_reservation=tmp_path/"no_upload_must_happen.json")
    assert not attempts
    assert not (tmp_path/"no_upload_must_happen.json").exists()


def test_verified_breakouts_must_be_distinct_qualifying_videos():
    now=datetime.now(timezone.utc)
    evidence=source_evidence(now)
    first=evidence["breakout_channel"]["videos"][0]
    second=evidence["breakout_channel"]["videos"][1]
    second["video_id"]=first["video_id"]
    third=dict(second)
    third["video_id"]="DISTINCT_UNDER_THRESHOLD"
    third["views"]=500
    evidence["breakout_channel"]["videos"].append(third)
    with pytest.raises(ValueError,match="TWO_BREAKOUTS"):
        validate_breakout_evidence(evidence,at=now)
    fresh=source_evidence(now)
    fresh["evergreen_witnesses"][0]["published_at"]=(now-timedelta(days=130)).isoformat()
    with pytest.raises(ValueError,match="RECENT_ESTABLISHED"):
        validate_breakout_evidence(fresh,at=now)


def test_analytics_oauth_channel_identity_checked_via_google_owned_channel(monkeypatch):
    from unittest.mock import MagicMock
    from googleapiclient import discovery
    import cinefactory.studio.youtube_oauth_transport_v205 as api
    verified_id="UC"+"c"*22
    youtube=MagicMock()
    youtube.channels.return_value.list.return_value.execute.return_value={
        "items":[{"id":verified_id}],
    }
    metrics=MagicMock()
    calls=[]
    def build(provider,*args,**kwargs):
        calls.append(provider)
        return youtube if provider=="youtube" else metrics
    monkeypatch.setattr(discovery,"build",build)
    monkeypatch.setattr(api,"_credentials",lambda *_: object())
    instance=api.GoogleYouTubeOwnedAnalyticsTransport(
        "dummy-not-real-token.json",verified_channel_id=verified_id)
    assert instance.owned_channel_id==verified_id
    assert calls==["youtube","youtubeAnalytics"]
    with pytest.raises(PermissionError,match="ANALYTICS_OAUTH_NOT_OWNED_CHANNEL"):
        api.GoogleYouTubeOwnedAnalyticsTransport(
            "dummy-not-real-token.json",verified_channel_id="UC"+"d"*22)

def test_company_plan_cli_uses_exact_explicit_project_id_for_native_lane():
    from typer.testing import CliRunner
    from cinefactory.cli import app
    result=CliRunner().invoke(app,[
        "company-plan","--project-id","V205_ROUTE_INSPECTION_001",
        "--prompt","Original rain ambience with own source footage",
        "--niche","rain_sleep_white_noise","--duration","540",
    ])
    assert result.exit_code==0,result.output[-900:]
    bp=json.loads(result.output)
    assert bp["project"]["studio_project_id"]=="V205_ROUTE_INSPECTION_001"
    assert bp["project"]["niche"]=="rain_sleep_white_noise"
    assert bp["strict_stage_receipts"] is True
    assert bp["stages"][0]["stage_id"]=="NICHE_PROJECT_INTAKE"
    assert bp["stages"][-2]["stage_id"]=="PUBLISHING"
    assert bp["executable"] is False
    assert "NICHE_PRODUCTION_NOT_GREENLIT" in bp["blockers"]


def test_work_order_wrong_project_target_fails_without_creating_file(tmp_path):
    now=datetime.now(timezone.utc)
    bridge=write(tmp_path/"bridge.json",{"fixture":True})
    pod=write(tmp_path/"pod.json",{
        "schema":"cine.niche.pod.v1","niche":"minecraft",
        "state":"CONFIGURED_NOT_SCHEDULED","approval_id":"test-approval",
        "bridge_source":str(bridge),"bridge_sha256":digest(bridge),
    })
    evidence=write(tmp_path/"evidence.json",source_evidence(now))
    pri,key=keypair(tmp_path,"owner")
    payload={
        "pod_sha256":digest(pod),"evidence_sha256":digest(evidence),
        "bridge_sha256":digest(bridge),"niche":"minecraft",
        "decision":"APPROVE_ORIGINAL_PILOT_PRODUCTION",
        "project_id":"ORIGINAL_PROJECT_ONLY","output_mode":"LOCAL_NO_METERED_API",
        "issued_at":now.isoformat(),
    }
    event=write(tmp_path/"event.json",{
        "schema":"cine.owner.production_authorization.v205",
        "niche":"minecraft","payload":payload,"signature_b64":signed(pri,payload),
    })
    dest=tmp_path/"WRONG_TARGET"/"approved_studio_work_order.json"
    with pytest.raises(PermissionError,match="SIGNED_PROJECT_ID_DOES_NOT_MATCH"):
        create_studio_work_order(
            pod,evidence,event,key,dest,expected_project_id="WRONG_TARGET",now=now)
    assert not dest.exists()
