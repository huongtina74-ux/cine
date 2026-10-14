"""v220: cited Claude Code software/MCP landscape, read-only planning.

A provider's official MCP, a community DCC bridge and a vendor's basic API
are different integration classes. These records do not install providers.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlsplit
from .contracts import DepartmentId
from .technology_discovery_v211 import production_family

CATALOG=Path(__file__).resolve().parents[2] / "config/technology/creative_software_mcp_landscape_v220.json"
_ALLOWED={"OFFICIAL_NATIVE_EXPERIMENTAL","OFFICIAL_NATIVE",
          "COMMUNITY_MCP","COMMUNITY_MCP_MACOS_VERIFIED",
          "NO_OFFICIAL_MCP_AS_OF_2026_06","OFFICIAL_REMOTE_MCP",
          "OFFICIAL_REMOTE_MCP_CLI","OFFICIAL_PRIVATE_PREVIEW",
          "OFFICIAL_COMMUNITY_OPENSOURCE_BETA"}
def load_creative_software_mcp_landscape() -> dict:
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema")!="cine.company.creative_software_mcp_landscape.v220":
        raise ValueError("INVALID_MCP_RESEARCH_SCHEMA")
    if not all(data.get(x) is True for x in
               ("registry_96_unchanged","no_auto_install","no_auto_execute","no_spend")):
        raise ValueError("MCP_RESEARCH_SAFETY_POLICY_BROKEN")
    items=data["items"]
    if len(items)!=27 or len({x["id"] for x in items})!=len(items):
        raise ValueError("INVALID_MCP_RESEARCH_ITEMS")
    valid_departments={x.value for x in DepartmentId}
    for r in items:
        source=urlsplit(r["source_url"])
        if (source.scheme!="https" or not source.hostname
            or r["connection_class"] not in _ALLOWED
            or not r["departments"]
            or not set(r["departments"]).issubset(valid_departments)
            or any(r.get(x) for x in (
                "installed_and_connected_to_cinefactory","benchmarked",
                "production_approved"))):
            raise ValueError("MCP_RECORD_NOT_IN_SAFE_RESEARCH_STATE")
    return data

def plan_creative_mcp_for_niche(minor_niche: str, *,
                               department: str|None=None, limit:int=15) -> dict:
    if not isinstance(minor_niche,str) or not minor_niche.strip():
        raise ValueError("NICHE_REQUIRED")
    from .claude_mcp_gateway_v218 import _niche
    _niche(minor_niche)
    if department is not None and department not in {x.value for x in DepartmentId}:
        raise ValueError("UNKNOWN_DEPARTMENT")
    if type(limit) is not int or not 1<=limit<=27:
        raise ValueError("INVALID_RESULT_LIMIT")
    data=load_creative_software_mcp_landscape()
    family=production_family(minor_niche,None)
    rank={"P0":0,"P1":1,"P2":2,"P3":3,"HOLD":4}
    match=sorted(
        (r for r in data["items"] if family in r["format_families"]
          and (department is None or department in r["departments"])),
        key=lambda x:(rank.get(x["priority"],9),x["id"])
    )
    return {
        "schema":"cine.company.creative_mcp_niche_advisory.v220",
        "niche":minor_niche,"media_family":family,"department":department,
        "verified_source_catalog_total":len(data["items"]),
        "matching_options":len(match),
        "options":[{
            "id":r["id"],"name":r["name"],"priority":r["priority"],
            "connection_class":r["connection_class"],
            "integration_role":r["function"],
            "source_url":r["source_url"],
            "limitations":r["requirements_and_cautions"],
            "installed_in_company":False,
            "production_permission":False,"credit_spend_permission":False,
            "next_gate":"INSTALLATION_LICENSE_SAFETY_RUNTIME_BENCHMARK_OWNER_APPROVAL",
        } for r in match[:limit]],
        "note":"Research only: official vs community, experimental/preview and commercial plans differ.",
        "auto_install":False,"auto_execute":False,"credits_spent":0,
        "production_permission":False,
    }
