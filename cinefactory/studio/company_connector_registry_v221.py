"""v221: one live company capability registry for researched creative MCPs.

A capability may be known/relevant, but cannot be used until the executable,
integration, rights, safety and representative quality pilot ALL pass.
This adapter prepares per-department scene planning from ALL 27 v220 entries;
does not execute workflows, connect external MCPs or spend credits.
"""
from __future__ import annotations

from collections import Counter
import shutil

from .contracts import DepartmentId
from .creative_mcp_landscape_v220 import load_creative_software_mcp_landscape
from .technology_discovery_v211 import production_family

# A non-privileged PATH check can be useful on Windows; not finding an executable
# on PATH does NOT prove the software is absent (GUI apps often are not on PATH).
EXECUTABLE_HINTS = {
    "ue58_native": ("UnrealEditor.exe", "UnrealEditor"),
    "cinema4d_native": ("Cinema 4D.exe",),
    "unity_cli_native": ("unity.exe", "Unity.exe"),
    "silhouette_native": ("silhouette.exe",),
    "resolve_community": ("Resolve.exe",),
    "premiere_community": ("Adobe Premiere Pro.exe",),
    "aftereffects_community": ("AfterFX.exe",),
    "photoshop_community": ("Photoshop.exe",),
    "houdini_fx": ("houdini.exe",),
    "nuke_community": ("Nuke.exe",),
    "maya_community": ("maya.exe",),
    "reaper_audio": ("reaper.exe",),
    "audacity_audio": ("audacity.exe",),
    "natron_vfx": ("Natron.exe",),
    "godot_engine": ("godot.exe", "godot_console.exe"),
}
CLOUD_CLASS = frozenset((
    "OFFICIAL_REMOTE_MCP", "OFFICIAL_REMOTE_MCP_CLI",
    "OFFICIAL_PRIVATE_PREVIEW",
))
RANK = {"P0":0,"P1":1,"P2":2,"P3":3,"HOLD":4}


def _local_executable_hints() -> dict[str,dict]:
    hints = {}
    for item, executables in EXECUTABLE_HINTS.items():
        matched = next((name for name in executables if shutil.which(name)), None)
        hints[item] = {
            "executable_found_on_path": bool(matched),
            "matched_executable_name": matched,
            "not_on_path_does_not_mean_not_installed": True,
        }
    # Existing local ecosystem rather than new third-party MCP binaries.
    hints["comfy_official_local"] = {
        "executable_found_on_path": bool(shutil.which("comfy-mcp")),
        "matched_executable_name": "comfy-mcp" if shutil.which("comfy-mcp") else None,
        "not_on_path_does_not_mean_not_installed": True,
    }
    return hints


def _validate_input(niche: str, department: str|None) -> None:
    from .claude_mcp_gateway_v218 import _niche
    _niche(niche)
    if department is not None and department not in {x.value for x in DepartmentId}:
        raise ValueError("UNKNOWN_DEPARTMENT")


def company_connector_inventory(*, local_probe: bool=False) -> dict:
    catalog=load_creative_software_mcp_landscape()
    hints=_local_executable_hints() if local_probe else {}
    comfy=None
    if local_probe:
        from .local_ai_connector_v219 import comfyui_local_status
        comfy=comfyui_local_status()
    rows=[]
    for source in catalog["items"]:
        item=dict(source)
        hint=hints.get(item["id"])
        item["host_executable_hint"]=hint or {
            "executable_found_on_path": False,
            "not_checked_this_call": True,
        }
        item["integration_activation"]="NOT_CONNECTED_TO_CLAUDE_CODE"
        item["production_execution"]="DENIED_NO_QUALIFIED_CONNECTOR"
        item["budget_approval"]="REQUIRED_FOR_CLOUD_OR_MODEL_CREDITS"
        item["quality_and_rights_gate"]="NOT_MEASURED_OR_SIGNED"
        item["auditable_external_commands_allowed"]=False
        if item["id"]=="comfy_official_local" and comfy is not None:
            item["underlying_local_comfyui"]={
                "connection":comfy["connection"],
                "version":comfy.get("comfy_version"),
                "local_get_bridge_available":comfy["connection"]=="RESPONDING",
                "official_comfy_mcp_connected":False,
            }
        if item["connection_class"] in CLOUD_CLASS:
            item["authentication"]="EXPLICIT_EXTERNAL_ACCOUNT_CONNECTION_REQUIRED"
            item["cloud_generation"]="DISABLED"
        rows.append(item)
    return {
        "schema":"cine.company.connector_inventory.v221",
        "catalog_source":catalog["schema"],"connector_count":len(rows),
        "baseline_96_unchanged":True,
        "all_connectors_in_company_plan":True,
        "local_probe_performed":local_probe,
        "runtime_checks_do_not_constitute_install_validation":True,
        "records":rows,
        "external_connectors_enabled":0,"paid_provider_jobs_authorized":0,
        "production_backend_changes":0,
        "existing_company_execution_unchanged":True,
    }


def company_scene_connector_plan(niche: str, *, department: str|None=None,
                                 limit: int=12, local_probe: bool=False) -> dict:
    _validate_input(niche,department)
    if type(limit) is not int or not 1<=limit<=27:
        raise ValueError("LIMIT_OUT_OF_RANGE")
    family=production_family(niche,None)
    inv=company_connector_inventory(local_probe=local_probe)
    rows=sorted(
        (x for x in inv["records"]
         if family in x["format_families"] and
           (department is None or department in x["departments"])),
        key=lambda x:(RANK.get(x["priority"],9),x["id"]),
    )
    return {
        "schema":"cine.company.scene_connector_plan.v221",
        "niche":niche,"media_family":family,
        "department":department,"connected_company_catalog_count":27,
        "matching_count":len(rows),"options":[{
            "id":x["id"],"name":x["name"],"priority":x["priority"],
            "role":x["function"],"integration_class":x["connection_class"],
            "host_executable_hint":x["host_executable_hint"],
            "source_url":x["source_url"],
            "risks":x["requirements_and_cautions"],
            "underlying_local_comfyui":x.get("underlying_local_comfyui"),
            "execution_status":x["production_execution"],
            "mcp_status":x["integration_activation"],
            "license":x["quality_and_rights_gate"],
        } for x in rows[:limit]],
        "decision":"STAGE_PILOT_REQUIRES_EXPLICIT_APPROVAL",
        "policy":[
            "Observe real authorized source video+sound before inferring production method",
            "Check installed app, official/community MCP provenance and rights",
            "Isolated adapter build and stdout/input secrets audit",
            "Approved cloud credits or FREE local-only budget",
            "Produce comparable original scene pilots on actual available GPU",
            "Character/camera/audio/story QC acceptance before speed optimization",
            "Written owner consent before changing working pipeline",
        ],
        "live_checks_done":local_probe,
        "all_unapproved_backend_execution_denied":True,
    }


def company_department_connector_index(niche: str, *, top_k:int=6) -> dict:
    _validate_input(niche,None)
    if type(top_k) is not int or not 1<=top_k<=12:
        raise ValueError("TOP_K_OUT_OF_RANGE")
    family=production_family(niche,None)
    catalog=load_creative_software_mcp_landscape()
    sorted_rows=sorted(catalog["items"],
                       key=lambda x:(RANK.get(x["priority"],9),x["id"]))
    mapping={
        dept.value:[x["id"] for x in sorted_rows
                    if dept.value in x["departments"]
                    and family in x["format_families"]][:top_k]
        for dept in DepartmentId
    }
    return {
        "schema":"cine.company.department_connector_index.v221",
        "niche":niche,"family":family,
        "department_count":len(mapping),
        "catalog_total":len(sorted_rows),
        "department_candidate_ids":mapping,
        "executors_changed":False,
        "all_candidates_require_validation":True,
    }
