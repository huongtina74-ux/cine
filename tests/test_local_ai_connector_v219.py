"""v219 verifies actual local ComfyAI read tools and zero paid/executable MCP."""
import json
from typer.testing import CliRunner
import pytest

from cinefactory.cli import app
from cinefactory.studio.claude_mcp_gateway_v218 import build_server
from cinefactory.studio import local_ai_connector_v219 as api

def test_12_integrations_are_explicit_with_nonautomatic_enablement():
    r=api.claude_external_connector_plan()
    assert r["schema"]=="cine.company.claude_external_connector_plan.v219"
    assert len(r["external_connectors"])==12
    assert all(item["auto_enabled"] is False for item in r["external_connectors"])
    assert not r["production_approved"]
    assert not r["paid_credits_authorized"]
    names={x["id"] for x in r["external_connectors"]}
    assert "comfy_local_api" in names
    assert "blender_desktop_extension" in names
    assert "blender_lab_official" in names
    assert "openart_mcp" in names
    assert "higgsfield_mcp" in names
    assert "piclumen" in names

def test_readonly_fixed_loopback_endpoint_and_fake_api_responses(monkeypatch):
    recorded=[]
    def fake_get(path):
        recorded.append(path)
        if path=="/system_stats":
            return {"system":{"comfyui_version":"0.38.0","python_version":"3.12",
                     "pytorch_version":"2.14","argv":["--disable-api-nodes"]},
                    "devices":[{"type":"cuda","name":"RTX 3060","vram_total":12_884_000_000,
                                 "vram_free":6_000_000_000}]}
        if path=="/object_info":
            return {"CheckpointLoaderSimple":{}, "ImageScale":{}, "RemoteSecretNode":{}}
        if path=="/queue":
            return {"queue_pending":[1,2],"queue_running":[3]}
        raise ValueError("UNSUPPORTED")
    monkeypatch.setattr(api,"_get_local_json",fake_get)
    status=api.comfyui_local_status()
    assert status["connection"]=="RESPONDING"
    assert status["devices"][0]["name"]=="RTX 3060"
    assert status["api_nodes_disabled"]
    assert status["allows_generation"] is False
    nodes=api.comfyui_local_capabilities("Checkpoint")
    assert nodes["node_types"]==["CheckpointLoaderSimple"]
    assert nodes["credits_spent"]==0
    queue=api.comfyui_local_queue()
    assert (queue["running_count"],queue["pending_count"])==(1,2)
    assert recorded==["/system_stats","/object_info","/queue"]

def test_api_disallows_arbitrary_endpoint_or_untrusted_node_search():
    with pytest.raises(ValueError,match="UNSUPPORTED_READONLY_ENDPOINT"):
        api._get_local_json("http://evil.example/api")
    with pytest.raises(ValueError,match="INVALID_NODE_SEARCH"):
        api.comfyui_local_capabilities("../../PROMPT")
    with pytest.raises(ValueError,match="INVALID_RESULT_LIMIT"):
        api.comfyui_local_capabilities("Checkpoint",limit=200)

def test_graceful_local_service_downtime(monkeypatch):
    def unavailable(_):
        raise RuntimeError("COMFY_LOCAL_PROBE_FAILED")
    monkeypatch.setattr(api,"_get_local_json",unavailable)
    assert api.comfyui_local_status()["connection"]=="UNAVAILABLE"
    assert api.comfyui_local_capabilities("Image")["connection"]=="UNAVAILABLE"
    assert api.comfyui_local_queue()["connection"]=="UNAVAILABLE"

def test_readonly_mcp_api_includes_actual_ai_probes_but_no_generators():
    tools=build_server()._tool_manager._tools
    assert {"comfyui_local_status","comfyui_local_capabilities",
            "comfyui_local_queue","claude_external_connector_plan"} <= set(tools)
    assert not set(tools) & {
        "generate_image","run_workflow","submit_prompt","partner_generate",
        "install_models","execute_python","change_scene","approve_spend"
    }

def test_cli_reports_connector_ledger_without_triggering_paid_work():
    response=CliRunner().invoke(app,["ai-connector-status"])
    assert response.exit_code==0,str(response.exception)
    data=json.loads(response.output)
    assert data["production_approved"] is False
    assert len(data["external_connectors"])==12
    assert "local_comfyui" not in data

def test_catalog_guards_break_on_hidden_activation(monkeypatch):
    sample=api.load_connector_catalog()
    sample["connectors"][0]["auto_enabled"]=True
    real=api.json.loads
    # Force a doctored manifest read rather than touching original repo data.
    orig=api.MANIFEST
    class FakePath:
        def read_text(self,**kwargs):
            return json.dumps(sample)
    monkeypatch.setattr(api,"MANIFEST",FakePath())
    with pytest.raises(ValueError,match="UNAPPROVED_EXTERNAL_CONNECTOR_ENABLEMENT"):
        api.load_connector_catalog()
