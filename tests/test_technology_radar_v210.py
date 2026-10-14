"""v210: entire CineFactory technology survey is bounded and non-deployable."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.technology_radar_v210 import (
    load_technology_radar,summarize_technology_radar,RESTRICTED,MUST_HAVE
)

def test_radar_has_all_requested_media_families_and_critical_minimax_comfy():
    r=load_technology_radar()
    assert r["entry_count"]>=80
    assert r["entry_count"]==len(r["items"])
    assert MUST_HAVE <= {v["id"] for v in r["items"]}
    families={v["category"] for v in r["items"]}
    assert {"orchestration","image","video","3d","animation_motion",
            "audio","editorial","saas","research"} <= families
    assert r["model_installations_performed"]==0
    assert r["paid_api_credits_used"]==0

def test_minimax_model_not_equated_to_freevideo_or_comfyui():
    items={x["id"]:x for x in load_technology_radar()["items"]}
    assert items["minimax_h3"]["category"]=="video"
    assert items["freevideo"]["id"]!="minimax_h3"
    assert items["comfyui"]["category"]=="orchestration"
    assert items["minimax_h3"]["commercial_gate"]=="TERRITORY_RESTRICTED_OUTPUT"
    assert items["freevideo"]["commercial_gate"]=="TERRITORY_RESTRICTED_OUTPUT"
    assert "NO_H3_WEIGHTS" in items["minimax_h3"]["local_runtime"]
    assert items["qwen_turbo"]["commercial_gate"]=="NONCOMMERCIAL_WEIGHT"
    assert items["flux_klein4b"]["commercial_gate"]=="APACHE_2_4B_WEIGHTS"
    assert items["blender"]["local_runtime"]!="NOT_VERIFIED"

def test_no_candidate_is_auto_authorized_for_production():
    radar=load_technology_radar()
    assert not any(x["deploy_approved"] for x in radar["items"])
    assert radar["allowed_to_auto_install"] is False
    assert radar["production_changes_performed"] is False
    out=summarize_technology_radar(radar)
    assert out["cleared_for_automatic_production"]==0
    assert out["new_models_benchmarked_on_user_gpu"]==0
    assert out["can_prove_all_repos_on_internet_checked"] is False

def test_all_urls_have_research_provenance_and_priority():
    radar=load_technology_radar()
    assert all(x["official_or_project_url"].startswith("https://")
               for x in radar["items"])
    assert all(x["priority"] in {"P0","P1","RND","HOLD"}
               for x in radar["items"])
    assert all(x["evidence_state"] in {
        "PUBLIC_SOURCE_REVIEWED_2026_10_10",
        "CATALOG_LEAD_REQUIRES_SOURCE_RECHECK",
    } for x in radar["items"])

@pytest.mark.parametrize("key,new_value,needle",[
    ("minimax_h3","APACHE_2_4B_WEIGHTS","RESTRICTED_MODEL_LICENSE_GATE"),
    ("freevideo","APACHE_2_4B_WEIGHTS","RESTRICTED_MODEL_LICENSE_GATE"),
    ("hunyuan3d21","APACHE_2_4B_WEIGHTS","RESTRICTED_MODEL_LICENSE_GATE"),
    ("qwen_turbo","APACHE_2_4B_WEIGHTS","RESTRICTED_MODEL_LICENSE_GATE"),
    ("anigen","APACHE_2_4B_WEIGHTS","RESTRICTED_MODEL_LICENSE_GATE"),
])
def test_known_legal_restrictions_cannot_be_silently_erased(
        tmp_path,key,new_value,needle):
    r=load_technology_radar()
    for x in r["items"]:
        if x["id"]==key:x["commercial_gate"]=new_value
    f=tmp_path/"radar.json"
    f.write_text(json.dumps(r),encoding="utf8")
    with pytest.raises(ValueError,match=needle):
        load_technology_radar(f)

def test_fake_preapproved_model_is_rejected(tmp_path):
    r=load_technology_radar()
    r["items"][0]["deploy_approved"]=True
    f=tmp_path/"radar.json"
    f.write_text(json.dumps(r),encoding="utf8")
    with pytest.raises(ValueError,match="UNSUPPORTED_AUTOMATIC_MODEL_DEPLOYMENT"):
        load_technology_radar(f)

def test_bad_counts_and_duplicate_ids_are_rejected(tmp_path):
    r=load_technology_radar()
    r["items"][1]["id"]=r["items"][0]["id"]
    f=tmp_path/"radar.json"
    f.write_text(json.dumps(r),encoding="utf8")
    with pytest.raises(ValueError,match="TECHNOLOGY_ID_DUPLICATE"):
        load_technology_radar(f)

def test_readonly_cli_reports_counts_and_relevant_category():
    base=CliRunner().invoke(app,["technology-radar"])
    assert base.exit_code==0,base.output[-900:]
    all_=json.loads(base.output)
    assert all_["registry_total"]>=80
    assert "entries" not in all_
    one=CliRunner().invoke(app,["technology-radar","--category","video","--priority","HOLD","--show-items"])
    assert one.exit_code==0,one.output[-900:]
    v=json.loads(one.output)
    ids={x["id"] for x in v["entries"]}
    assert {"minimax_h3","freevideo"} <= ids
    assert "flux_klein4b" not in ids
    assert all(x["deploy_approved"] is False for x in v["entries"])
