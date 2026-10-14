"""v219 local media/AI integration probe for Claude Code.

Live ComfyUI introspection over a FIXED localhost URL only. No prompt submit,
arbitrary HTTP target, model install, arbitrary Python, premium partner calls
or server operations are exposed by this adapter. Blender/paid MCP discovery
stays in source-verified connector manifest, not implied live execution.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config/technology/claude_external_connector_catalog_v219.json"
COMFY_LOCAL_BASE = "http://127.0.0.1:8188"
MAX_RESPONSE_BYTES = 12_000_000
NODE_QUERY_PATTERN = re.compile(r"^[a-zA-Z0-9_ .:-]{1,64}$")

def _get_local_json(path: str) -> object:
    # Caller cannot choose URLs/headers/path. Strict fixed whitelist.
    if path not in ("/system_stats", "/object_info", "/queue"):
        raise ValueError("UNSUPPORTED_READONLY_ENDPOINT")
    request=urllib.request.Request(
        COMFY_LOCAL_BASE + path,
        headers={"Accept":"application/json"},
        method="GET",
    )
    # Ignore machine proxy environment: this adapter must never leave loopback.
    local_only_opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with local_only_opener.open(request,timeout=2.5) as resp:
            if resp.status != 200:
                raise RuntimeError("COMFY_NON_200")
            payload=resp.read(MAX_RESPONSE_BYTES+1)
            if len(payload)>MAX_RESPONSE_BYTES:
                raise ValueError("COMFY_REPLY_TOO_LARGE")
        return json.loads(payload)
    except (OSError,ValueError,RuntimeError,TimeoutError) as ex:
        raise RuntimeError("COMFY_LOCAL_PROBE_FAILED") from ex

def comfyui_local_status() -> dict:
    try:
        report=_get_local_json("/system_stats")
        if not isinstance(report,dict):
            raise RuntimeError("BAD_STATUS_SHAPE")
        sys=report.get("system",{})
        devices=report.get("devices",[])
        gpu=[{
            "name":str(x.get("name",""))[:160],
            "type":str(x.get("type",""))[:24],
            "vram_total_bytes":int(x.get("vram_total",0)),
            "vram_free_bytes":int(x.get("vram_free",0)),
        } for x in devices if isinstance(x,dict)]
        argv=sys.get("argv",[])
        args=[str(x) for x in argv] if isinstance(argv,list) else []
        return {
            "schema":"cine.company.comfy_local_status.v219",
            "endpoint":"127.0.0.1:8188", "connection":"RESPONDING",
            "comfy_version":str(sys.get("comfyui_version","UNKNOWN"))[:64],
            "python_version":str(sys.get("python_version","UNKNOWN"))[:140],
            "pytorch_version":str(sys.get("pytorch_version","UNKNOWN"))[:64],
            "devices":gpu,
            "custom_nodes_disabled":"--disable-all-custom-nodes" in args,
            "api_nodes_disabled":"--disable-api-nodes" in args,
            "observed_commandline_flags":{
                "disable_custom_nodes":"--disable-all-custom-nodes" in args,
                "disable_api_nodes":"--disable-api-nodes" in args,
            },
            "no_credits_spent":True,"allows_generation":False,
            "mcp_gateway_rights":"READ_ONLY_GET_WHITELIST",
            "production_qualified":False,
        }
    except Exception as exc:
        return {
            "schema":"cine.company.comfy_local_status.v219",
            "endpoint":"127.0.0.1:8188", "connection":"UNAVAILABLE",
            "reason":"LIVE_LOCAL_PROBE_FAILED",
            "no_credits_spent":True,"allows_generation":False,
            "production_qualified":False,
        }

def comfyui_local_capabilities(query:str="Checkpoint",limit:int=15) -> dict:
    if not isinstance(query,str) or not NODE_QUERY_PATTERN.fullmatch(query.strip()):
        raise ValueError("INVALID_NODE_SEARCH")
    if type(limit) is not int or not 1<=limit<=30:
        raise ValueError("INVALID_RESULT_LIMIT")
    q=query.casefold().strip()
    try:
        data=_get_local_json("/object_info")
        if not isinstance(data,dict):
            raise RuntimeError("INVALID_NODE_INFO")
        # Only names, NOT raw node structures, Python code, paths, prompt
        # bodies, secret fields or model download URLs.
        matches=sorted(
            str(name)[:100] for name in data
            if q in str(name).casefold()
        )
        return {
            "schema":"cine.company.comfy_local_capabilities.v219",
            "connection":"RESPONDING","matching_node_count":len(matches),
            "node_types":matches[:limit],
            "object_info_has_nodes":len(data)>0,
            "partner_api_nodes_verified_safe":False,
            "models_downloaded_or_licensed_verified":False,
            "job_submitted":False,"credits_spent":0,
        }
    except RuntimeError:
        return {
            "schema":"cine.company.comfy_local_capabilities.v219",
            "connection":"UNAVAILABLE","matching_node_count":0,
            "node_types":[],"job_submitted":False,"credits_spent":0,
        }

def comfyui_local_queue() -> dict:
    try:
        q=_get_local_json("/queue")
        if not isinstance(q,dict):
            raise RuntimeError("INVALID_QUEUE")
        return {
            "schema":"cine.company.comfy_local_queue.v219",
            "connection":"RESPONDING",
            "running_count":len(q.get("queue_running",[])),
            "pending_count":len(q.get("queue_pending",[])),
            "workflow_details_hidden":True,"job_submitted":False,
            "credits_spent":0,
        }
    except RuntimeError:
        return {
            "schema":"cine.company.comfy_local_queue.v219",
            "connection":"UNAVAILABLE",
            "workflow_details_hidden":True,"job_submitted":False,
            "credits_spent":0,
        }

def load_connector_catalog() -> dict:
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema")!="cine.company.claude_connector_catalog.v219":
        raise ValueError("INVALID_CONNECTOR_CATALOG")
    if any(data.get(k) is not True for k in
           ("research_only","no_paid_auto_calls","no_third_party_auto_installs")):
        raise ValueError("UNSAFE_CONNECTOR_CATALOG")
    rows=data.get("connectors",[])
    if len({x["id"] for x in rows})!=len(rows):
        raise ValueError("DUPLICATE_CONNECTOR_ID")
    for item in rows:
        if item.get("auto_enabled") is not False:
            raise ValueError("UNAPPROVED_EXTERNAL_CONNECTOR_ENABLEMENT")
    return data

def claude_external_connector_plan() -> dict:
    rows=load_connector_catalog()["connectors"]
    return {
        "schema":"cine.company.claude_external_connector_plan.v219",
        "external_connectors": [{
            "id":r["id"],"name":r["name"],
            "integration_status":r["integration_status"],
            "recommended_stage":r["recommended_stage"],
            "capabilities":r["capabilities"],
            "rights_risk":r["rights_risk"],
            "activation_requirements":r["activation_requirements"],
            "auto_enabled":False,
        } for r in rows],
        "source_of_truth":"config/technology/claude_external_connector_catalog_v219.json",
        "production_approved":False,
        "paid_credits_authorized":False,
        "mcp_project_registration_does_not_imply_server_approved":True,
    }
