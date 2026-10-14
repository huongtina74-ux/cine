"""Verified-reference creator platform and Claude/MCP research for CineFactory v217.

Never interprets vendors' creator interviews or public model catalogs as
independent performance measurements, license clearance or run authorization.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
from .contracts import DepartmentId
from .technology_discovery_v211 import production_family

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"config/technology/creator_platforms_mcp_research_v217.json"
def load_creator_technology_research() -> dict:
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema")!="cine.technology.external_creator_mcp_research.v217":
        raise ValueError("INVALID_CREATOR_TECH_SCHEMA")
    if data.get("baseline_96_unchanged") is not True or data.get("no_auto_install") is not True or data.get("no_paid_calls") is not True or data.get("no_backend_switch") is not True:
        raise ValueError("UNSAFE_CREATOR_RESEARCH_POLICY")
    if data.get("credit_budget_usd") != 0:
        raise ValueError("CREATOR_RESEARCH_CREDIT_BUDGET_NONZERO")
    items=data["candidates"]
    if len({x["id"] for x in items})!=len(items):
        raise ValueError("DUPLICATE_CANDIDATE_ID")
    for x in items:
        if x["installed_verified"] or x["production_qualified"] or x["benchmarked_on_rtx3060"]:
            raise ValueError("RESEARCH_CANNOT_PREQUALIFY_BACKEND")
        if urlparse(x["official_source"]).scheme!="https":
            raise ValueError("UNTRUSTED_CREATOR_SOURCE")
    return data

def suggest_creator_technologies(minor_niche:str,*,department:str|None=None,
                                 limit:int=12) -> dict:
    if not minor_niche or not minor_niche.strip():
        raise ValueError("NICHE_REQUIRED")
    if department and department not in {x.value for x in DepartmentId}:
        raise ValueError("UNKNOWN_DEPARTMENT")
    if not 1<=limit<=50:
        raise ValueError("LIMIT_OUT_OF_RANGE")
    data=load_creator_technology_research()
    family=production_family(minor_niche,None)
    candidates=[]
    for row in data["candidates"]:
        if family not in row["format_families"] or department and department not in row["departments"]:
            continue
        candidates.append({
            "id":row["id"],"name":row["name"],"priority":row["priority"],
            "integration":row["integration"],"role":row["role"],
            "official_source":row["official_source"],
            "cost_mode":row["cost_mode"],"gates":row["gate"],
            "research_only":True,"credit_budget_usd":0,"execution_authorized":False,
        })
    order={"P0":0,"P1":1,"P2":2,"HOLD":3}
    candidates.sort(key=lambda x:(order.get(x["priority"],4),x["id"]))
    return {
        "schema":"cine.company.creator_technology_advisory.v217",
        "niche":minor_niche,"family":family,"department":department,
        "candidate_catalog_total":len(data["candidates"]),
        "named_studio_case_studies":len(data["case_studies"]),
        "matching":len(candidates),"items":candidates[:limit],
        "competitor_footage_inspected_by_this_process":False,
        "benchmarked":False,"spend_authorized":False,
        "production_permission":False,
    }
