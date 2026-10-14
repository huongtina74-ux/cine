"""v216: evidence-tiered October 2026 Agentic Creative research advisory.

The user-provided study and independent source checks are separate evidence
channels. No MCP is installed and no model/repo is promoted into production.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from .technology_discovery_v211 import production_family

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"config/technology/agentic_research_verified_v216.json"
SOURCE=ROOT/"config/technology/agent_leap_user_study_20261010.md"

def load_agentic_research() -> dict:
    metadata=json.loads(CATALOG.read_text(encoding="utf-8"))
    if metadata.get("schema")!="cine.technology.agentic_research_20261010.v216":
        raise ValueError("UNSUPPORTED_AGENTIC_RESEARCH")
    if not metadata.get("registry_96_preserved") or any(
        metadata.get(k) for k in ("auto_install","auto_authorize_paid_api","auto_switch_backend")
    ):
        raise ValueError("AGENTIC_RESEARCH_SAFETY_GATES_REMOVED")
    rows=metadata.get("candidates",[])
    if not isinstance(rows,list) or len({r["id"] for r in rows})!=len(rows):
        raise ValueError("INVALID_AGENTIC_RESEARCH_CANDIDATES")
    for r in rows:
        url=urlparse(r["url"])
        if url.scheme!="https" or not url.netloc or any(r.get(k) for k in (
            "installed","benchmarked","commercially_cleared"
        )):
            raise ValueError("AGENTIC_RESEARCH_CANNOT_PROMOTE_CANDIDATES")
    for claim in metadata.get("claims",[]):
        if claim.get("state") not in {
            "OFFICIALLY_CONFIRMED", "OFFICIALLY_CONFIRMED_EARLY_ACCESS_NOT_LOCAL",
            "OFFICIALLY_CONFIRMED_PAID_SAAS", "MISSTATED_AS_AVAILABLE",
            "PARTIALLY_VERIFIED_SPECIFIC_FEATURES_UNCHECKED",
            "OFFICIAL_FEATURE_CONFIRMED_NOT_BENCHMARKED",
            "OFFICIAL_NUKE17_RELEASE_CONFIRMED_SPECIFIC_CLAIMS_UNCHECKED",
            "OVERSTATED_4D_STANDARD","UNSUPPORTED_QUANTIFIED_SAVINGS",
            "NOT_GROUNDED_FOR_BLENDER",
        }:
            raise ValueError("UNREVIEWED_AGENTIC_CLAIM_STATE")
    original=SOURCE.read_text(encoding="utf-8")
    source_refs=sorted(set(
        "https://github.com/"+x
        for x in re.findall(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)",original)
    ))
    return {
        **metadata,
        "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_github_links":source_refs,
        "source_github_reference_count":len(source_refs),
        "candidate_count":len(rows),
        "claim_count":len(metadata["claims"]),
    }

# This is scope matching for R&D discovery only, not permission to execute.
GROUPS={
    "FILM_3D":("blender","houdini","maya","nuke","comfy","wan2gp","ai4animation","usd","dramaclaw"),
    "SLIDE_3D":("blender","comfy","usd","wan2gp","ai4animation"),
    "MACHINIMA":("blender","comfy","ai4animation","wan2gp"),
    "GAME_CAPTURE":("comfy","impeccable"),
    "REAL_ASMR":("comfy","wan2gp"),
    "FIELD_CAPTURE":("comfy","spirula"),
    "VOICE_STORY":("dramaclaw","comfy","wan2gp"),
    "AMBIENCE":("comfy","wan2gp"),
    "ANIMATION_2D":("comfy","graphite","dramaclaw"),
    "EXPLAINER":("comfy","graphite","impeccable","dramaclaw"),
}
ROLES={
    "EDITORIAL":("comfy","nuke","wan2gp","dramaclaw","graphite"),
    "RND":(), "TECHNICAL_DIRECTION":(),
    "GENERATIVE_MEDIA":("comfy","wan2gp"),
    "ASSETS":("blender","maya","usd","spirula"),
    "VFX":("nuke","houdini","comfy"),
    "PRODUCTION":("blender","comfy","maya","houdini"),
    "PACKAGING":("graphite","figma","impeccable"),
    "PRODUCTION_DESIGN":("blender","figma","graphite"),
    "STUDIO_MANAGEMENT":("dcc","figma"),
}

def advise_agentic_tools(minor_niche: str, *, department: str|None=None,
                         limit: int=10) -> dict:
    from .contracts import DepartmentId
    if not isinstance(minor_niche,str) or not minor_niche.strip():
        raise ValueError("NICHE_REQUIRED")
    if department is not None and department not in {x.value for x in DepartmentId}:
        raise ValueError("UNKNOWN_DEPARTMENT")
    if not 1<=limit<=25:
        raise ValueError("LIMIT_OUT_OF_RANGE")
    data=load_agentic_research()
    family=production_family(minor_niche,None)
    tokens=GROUPS.get(family,())
    dept_tokens=ROLES.get(department,()) if department else ()
    eligible=[]
    for row in data["candidates"]:
        name=(row["id"]+" "+row["name"]).casefold()
        matching=[t for t in tokens if t in name]
        role_match=[t for t in dept_tokens if t in name]
        if department in {"RND","TECHNICAL_DIRECTION"}:
            role_match=matching
        if not matching or (department is not None and not role_match):
            continue
        score=2*len(matching)+len(role_match)
        if row["priority"]=="HOLD":
            score=-1
        eligible.append((score,row))
    eligible.sort(key=lambda z:(-z[0],z[1]["id"]))
    return {
        "schema":"cine.company.agentic_technology_advice.v216",
        "minor_niche":minor_niche,"media_family":family,
        "department":department,"baseline_inventory_unchanged":96,
        "candidate_catalog_count":data["candidate_count"],
        "matching_count":len(eligible),
        "candidates":[{
            "id":row["id"],"name":row["name"],"priority":row["priority"],
            "url":row["url"],"source_state":row["status"],
            "risk_notes":row["gates"],"production_qualified":False,
            "mcp_permission_to_execute":False,
            "next_action":"STATIC_REPO_LICENSE_SECURITY_REVIEW_THEN_ISOLATED_BENCHMARK",
        } for _,row in eligible[:limit]],
        "production_permission":False,"auto_install":False,
        "model_credit_spent":0,
    }
