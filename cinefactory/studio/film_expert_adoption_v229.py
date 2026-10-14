"""v229 read-only adoption review for the user's Agent Leap / cinema encyclopedia.

Distinguishes a written expert compilation, verified official documentation,
candidate DCC adapters, locally tested implementations and genuinely qualified
production workflows. This module does NOT claim that any agent or MCP installed.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"config/technology/agentic_film_studio_adoption_v229.json"
ALLOWED_STATUS=frozenset({
    "SOURCE_RESEARCHED_NOT_CONNECTED",
    "NOT_VERIFIED_NOT_CONNECTED",
    "SOURCE_RESEARCHED_NO_END_TO_END_USD_INTERCHANGE_TEST",
    "OFFICIAL_AVAILABLE_NOT_CONNECTED_TO_COMPANY",
    "RESEARCH_IN_CATALOG_NOT_EXECUTION_VERIFIED",
    "RESEARCH_ONLY_NOT_INSTALLED_OR_BENCHMARKED",
    "DOCUMENTED_NOT_INSTALLED_OR_BENCHMARKED",
    "VENDOR_FEATURES_VERIFIED_RUNTIME_NOT_AVAILABLE",
    "NOT_PRODUCTION_AVAILABLE_OR_BENCHMARKED",
    "EARLY_ACCESS_AVAILABILITY_AND_LOCAL_VRAM_UNVERIFIED",
    "APP_AND_API_DISCONTINUATION_VERIFIED_CAUSE_UNPROVEN",
    "3D_EXTENSION_RATIFIED_4D_STANDARD_CLAIM_UNSUPPORTED",
    "SOURCE_RESEARCHED_NOT_ALL_END_TO_END_VERIFIED",
    "NO_BENCHMARK_NO_FINANCIAL_ASSERTION",
    "PARTIAL_CODE_EXISTS_NOT_END_TO_END_VERIFIED",
})

def load_film_expert_intake()->dict:
    obj=json.loads(SRC.read_text(encoding="utf8"))
    if obj.get("schema")!="cine.company.agentic_film_studio_user_study.v229":
        raise ValueError("USER_FILM_STUDY_SCHEMA_MISMATCH")
    sources=(ROOT/obj["user_source"],ROOT/obj["other_study"])
    if any(not p.is_file() for p in sources):
        raise ValueError("FILM_STUDY_SOURCE_MISSING")
    steps=obj.get("stages",[])
    if len(steps)!=8 or len({x["stage"] for x in steps})!=8:
        raise ValueError("FILM_STUDIO_OPERATIONAL_CHAIN_INCOMPLETE")
    ts=obj.get("technologies",[])
    if len(ts)<12 or len({x["id"] for x in ts})!=len(ts):
        raise ValueError("EXPERT_TECHNOLOGY_CATALOG_INCOMPLETE")
    from .contracts import DepartmentId
    departments={d.value for d in DepartmentId}
    if any(t["status"] not in ALLOWED_STATUS
           or t["priority"] not in ("P0","P1","P2","HOLD","REFERENCE")
           or not set(t["maps_to"]).issubset(departments)
           or not t["next_gate"] for t in ts):
        raise ValueError("FILM_TECHNOLOGY_UNSAFE_OR_INCOMPLETE")
    if any(x["owner"] not in departments or not x["gate"] for x in steps):
        raise ValueError("STUDIO_STAGE_OWNER_OR_GATE_MISSING")
    conditions=obj["owner_constraints"]
    if not all(conditions.get(x) is True for x in (
        "free_local_first","no_paid_api_calls","no_install_just_by_research",
        "no_unverified_model_claims","no_assumed_connected_mcp",
        "requires_complete_competitor_av_before_source_based_methods",
    )):
        raise ValueError("FILM_RESEARCH_GUARDS_DISABLED")
    if obj["actual_integration_status"]!="RESEARCH_INDEX_AND_QUALIFICATION_GATES_ONLY_NO_NEW_SOFTWARE_CONNECTED":
        raise ValueError("CANNOT_MISREPORT_RESEARCH_AS_CONNECTED_SOFTWARE")
    return obj

def film_expert_adoption_audit(department:str|None=None)->dict:
    data=load_film_expert_intake()
    from .contracts import DepartmentId
    if department is not None and department not in {d.value for d in DepartmentId}:
        raise ValueError("UNKNOWN_FILM_STUDIO_DEPARTMENT")
    tech=[{k:v for k,v in t.items()} for t in data["technologies"]
          if department is None or department in t["maps_to"]]
    stages=[dict(s) for s in data["stages"]
            if department is None or s["owner"]==department]
    counts=dict(Counter(t["priority"] for t in tech))
    return {
        "schema":"cine.company.agentic_film_adoption_audit.v229",
        "department":department,
        "source_user_study_exists":True,
        "source_user_study":data["user_source"],
        "source_expert_encyclopedia":data["other_study"],
        "technology_records":len(tech),
        "priority_counts":counts,
        "company_pipeline_stages":stages,
        "technology_statuses":tech,
        "research_only":True,
        "new_software_installed_by_this_adoption":False,
        "new_mcp_providers_connected_by_this_adoption":False,
        "paid_credits_spent_by_this_adoption":0,
        "full_production_studio_autonomy_proven":False,
        "licensing_security_gpu_12gb_production_tests_still_required":True,
        "first_implementation_target":data["next_first_build"],
    }
