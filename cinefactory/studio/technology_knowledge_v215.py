"""CineFactory v215: source-preserving, non-executable studio technology library.

All user supplied research rows, skills, workflows, standards, hardware, proprietary
systems and tool references are indexed. They are NOT automatically verified.
Queries suggest technologies for further benchmarking; never authorize use.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from .contracts import DepartmentId
from .technology_radar_v210 import load_technology_radar
from .technology_discovery_v211 import production_family

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "config/technology/cinematography_studio_user_inventory_202510.txt"
FULL_SOURCE = ROOT / "config/technology/cinematography_studio_user_encyclopedia_202510.md"
RND_SOURCE = ROOT / "config/technology/professional_studio_research_v214.json"
SECTION = re.compile(r"^(\d{1,2})\.\s+(.+)$")
WORKFLOW = re.compile(r"^Workflow\s+(\d+):\s*(.+)$")
KINDS = {
    1: "DCC_SOFTWARE", 2: "PLUGIN_SPECIALIST", 3: "RENDER_ENGINE",
    4: "AI_REPOSITORY_MODEL", 5: "AI_VIDEO_VFX", 6: "SAAS_CLOUD",
    7: "REFERENCE_ASSET_WEBSITE", 8: "STUDIO_CRAFT_SKILL",
    9: "MCP_SERVER_IDEA_UNVERIFIED", 10: "AGENT_AND_FRAMEWORK",
    11: "WORKFLOW_REFERENCE", 12: "HARDWARE_STORAGE",
    13: "OPEN_STANDARD_FORMAT", 14: "SECURITY_POLICY",
    15: "DESIGN_2D_MOTION", 16: "AUDIO_SOUND",
    17: "PROPRIETARY_INHOUSE_REFERENCE_ONLY", 18: "PIPELINE_FRAMEWORK",
}
# Tag recognition is routing vocabulary, not evidence of installed capabilities.
TAGS = {
    "modeling": ("model", "mesh", "sculpt", "zbrush", "topolog", "retopo", "3d gen", "geometry", "3d asset", "3d character"),
    "animation": ("animat", "rig", "skeleton", "mocap", "capture", "motion", "blendshape", "facial", "expression", "choreog"),
    "render": ("render", "lookdev", "lighting", "shader", "pbr", "material", "udim", "ray trac", "color", "aces", "exr"),
    "vfx": ("vfx", "composit", "roto", "track", "depth", "mask", "inpaint", "segmen", "simulation", "fluid", "smoke", "crowd"),
    "image": ("image", "photo", "texture", "illustrat", "graphic", "draw", "art", "paint", "concept", "frame"),
    "video": ("video", "cinema", "film", "editor", "shot", "timeline", "footage", "nle", "cut", "camera"),
    "sound": ("audio", "sound", "voice", "tts", "speech", "music", "mix", "foley", "dubbing", "whisper", "noise"),
    "automation": ("autom", "pipeline", "python", "agent", "api", "mcp", "workflow", "orchestr", "batch", "asset management", "version"),
    "review": ("review", "qc", "dailies", "approval", "tracking", "security", "management", "backup", "provenance"),
}
DEPT_TAGS = {
    "INTELLIGENCE": ("automation", "review"), "EVIDENCE": ("review", "video"),
    "STUDIO_MANAGEMENT": ("automation", "review"), "PLANNING": ("automation", "review"),
    "CREATIVE_STRATEGY": ("image", "video"), "RND": tuple(TAGS),
    "RD_KNOWLEDGE": tuple(TAGS), "RIGHTS": ("review",),
    "OPERATIONS": ("automation", "review"), "QC": ("review", "video", "sound"),
    "ANALYTICS": ("review", "automation"), "PACKAGING": ("image", "video"),
    "WRITERS_ROOM": ("video", "sound"), "SCRIPT_LOGIC": ("video", "review"),
    "PERFORMANCE": ("animation", "sound"), "PRODUCTION_DESIGN": ("modeling", "image"),
    "ASSETS": ("modeling", "image", "render"), "DIRECTION": ("video", "animation"),
    "CINEMATOGRAPHY": ("video", "render"), "PRODUCTION": ("video", "animation", "modeling"),
    "GENERATIVE_MEDIA": ("video", "image"), "VFX": ("vfx", "render"),
    "AUDIO": ("sound",), "EDITORIAL": ("video", "sound", "review"),
    "COLOR": ("render", "image"), "TECHNICAL_DIRECTION": tuple(TAGS),
}
FORMAT_TAGS = {
    "FILM_3D": ("modeling", "animation", "render", "vfx", "sound", "video", "automation"),
    "MACHINIMA": ("animation", "video", "sound", "automation"),
    "SLIDE_3D": ("modeling", "animation", "render", "video", "automation"),
    "GAME_CAPTURE": ("video", "sound", "review", "automation"),
    "LIVE_CAPTURE": ("video", "sound", "review", "automation"),
    "FIELD_CAPTURE": ("video", "sound", "vfx", "review"),
    "REAL_ASMR": ("sound", "video", "review"),
    "AMBIENCE": ("sound", "video", "automation"),
    "VOICE_STORY": ("sound", "video", "automation"),
    "EXPLAINER": ("image", "video", "sound", "automation"),
    "MUSICAL_3D": ("modeling", "animation", "sound", "video"),
    "ANIMATION_2D": ("animation", "image", "video", "sound"),
}


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKD", value).casefold())


def _tags(value: str) -> list[str]:
    clean = unicodedata.normalize("NFKD", value).casefold()
    return sorted(k for k, phrases in TAGS.items() if any(t in clean for t in phrases))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _user_records() -> tuple[list[dict], list[dict], dict]:
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    section = None
    heading = None
    group = None
    rows: list[dict] = []
    flows: list[dict] = []
    current_flow = None
    for number, line in enumerate(lines, 1):
        line = line.strip()
        head = SECTION.fullmatch(line)
        if head:
            if current_flow:
                flows.append(current_flow)
                current_flow = None
            section = int(head.group(1))
            heading = head.group(2)
            group = None
            if section not in KINDS:
                raise ValueError("UNEXPECTED_SOURCE_SECTION")
            continue
        if section == 11:
            wm = WORKFLOW.match(line)
            if wm:
                if current_flow:
                    flows.append(current_flow)
                current_flow = {
                    "id": f"STUDY_WORKFLOW_{int(wm.group(1)):02d}",
                    "name": wm.group(2), "source_line": number,
                    "steps": [], "kind": "WORKFLOW_REFERENCE",
                    "automation_status": "ILLUSTRATIVE_NOT_EXECUTABLE",
                    "production_permission": False,
                }
            elif line and current_flow:
                current_flow["steps"].append(line)
            continue
        if not line or not section:
            continue
        if "\t" not in line:
            group = line
            continue
        parts = [p.strip() for p in line.split("\t") if p.strip()]
        if len(parts) < 2 or parts[0] in {
            "#", "Tool", "Công cụ", "Repo", "Platform", "Studio", "Hạng mục",
            "Phần mềm", "Tên", "Nhóm Kỹ Năng", "MCP Server", "Engine",
            "Frameworks", "Website", "Tính năng", "Loại", "Chuẩn / Định dạng",
            "Agent", "Nguồn", "Nhóm", "Chỉ tiêu",
        }:
            continue
        if len(parts) >= 3 and section in (1, 3) and parts[0].isdigit():
            name = parts[1]
            description = " | ".join(parts[2:])
        elif section == 17 and len(parts) >= 3:
            name = parts[0] + " — " + parts[1]
            description = " | ".join(parts[2:])
        else:
            name = parts[0]
            description = " | ".join(parts[1:])
        if name in {"Phần mềm", "Công cụ", "Chức năng", "Nhóm Kỹ Năng", "Nhóm", "Tên", "Loại", "Vai trò", "MCP Server", "Agent", "Website", "Hệ thống", "Studio", "Tính năng", "Engine", "Dịch vụ", "Repo / Tool", "Repo / Model", "Repo", "Tool / Repo", "Hạng mục", "Chuẩn / Định dạng", "Platform", "Framework", "Nhóm Kỹ Năng"}:
            continue
        rows.append({
            "source_id": f"STUDY_{number:04d}", "name": name,
            "description_from_user_source": description,
            "section_number": section, "section_title": heading,
            "subsection": group, "kind": KINDS[section],
            "source_line": number, "source_status": "USER_REFERENCE_NOT_INDEPENDENTLY_VERIFIED",
            "license": "NOT_CHECKED", "installed": "UNKNOWN",
            "benchmark": "NOT_RUN", "production_permission": False,
            "tags": _tags(name + " " + description + " " + (group or "")),
        })
    if current_flow:
        flows.append(current_flow)
    if len({x["section_number"] for x in rows} | {11}) != 18:
        raise ValueError("MISSING_ENCYCLOPEDIA_SECTION")
    if len(flows) != 8 or [x["id"] for x in flows] != [
        f"STUDY_WORKFLOW_{i:02d}" for i in range(1, 9)
    ]:
        raise ValueError("MISSING_EIGHT_STUDIO_WORKFLOWS")
    return rows, flows, {"inventory_sha256": _sha(SOURCE),
                         "encyclopedia_sha256": _sha(FULL_SOURCE)}


def load_company_knowledge() -> dict:
    rows, flows, provenance = _user_records()
    radar = load_technology_radar()
    rnd = json.loads(RND_SOURCE.read_text(encoding="utf-8"))
    if rnd.get("schema") != "cine.technology.professional_studio_research.v214":
        raise ValueError("INVALID_RND_CATALOG")
    if rnd.get("items_count") != len(rnd["items"]):
        raise ValueError("RND_COUNT_MISMATCH")
    baseline = []
    for tool in radar["items"]:
        baseline.append({
            "source_id": "BASE_" + tool["id"], "name": tool["name"],
            "description_from_user_source": "",
            "kind": "BASELINE_96", "section_number": None, "subsection": None,
            "status": "BASELINE_REGISTRY_CANDIDATE_NOT_APPROVED",
            "tags": _tags(tool["name"] + " " + tool["category"] + " " + tool["department"]),
            "installed": tool["local_runtime"], "license": tool["commercial_gate"],
            "benchmark": "NOT_VERIFIED_BY_KNOWLEDGE_BASE",
            "production_permission": bool(tool["deploy_approved"]),
            "source_link": tool["official_or_project_url"],
        })
    for tool in rnd["items"]:
        baseline.append({
            "source_id": "RND_" + tool["id"], "name": tool["name"],
            "description_from_user_source": tool["role"],
            "kind": "PRO_STUDIO_RND_V214", "section_number": None, "subsection": None,
            "status": tool["status"], "tags": _tags(tool["name"] + " " + tool["role"]),
            "installed": "UNKNOWN", "license": tool["caveat"],
            "benchmark": "NOT_RUN", "production_permission": False,
            "source_link": tool["url"],
        })
    # Non-destructive matching. Nothing is discarded; multiple source rows can
    # refer to one family, version or provider and may require human review.
    aliases = {
        _key("comfyanonymous/ComfyUI"): _key("ComfyUI"),
        _key("Blender 4.2+ LTS"): _key("Blender"),
        _key("Blender MCP"): _key("Blender MCP"),
        _key("Meta SAM 2"): _key("Meta Segment Anything 2"),
        _key("facebookresearch/segment-anything-2 (SAM 2)"): _key("Meta Segment Anything 2"),
        _key("OpenAI Whisper"): _key("Whisper"),
        _key("Real-ESRGAN"): _key("Real-ESRGAN"),
        _key("OpenTimelineIO"): _key("OpenTimelineIO"),
        _key("OpenTimelineIO (OTIO)"): _key("OpenTimelineIO"),
        _key("OpenColorIO (OCIO)"): _key("OpenColorIO"),
        _key("AYON (Ynput) (kế thừa OpenPype)"): _key("AYON"),
        _key("Prism Pipeline 2"): _key("Prism Pipeline 2"),
        _key("OpenUSD"): _key("OpenUSD"),
    }
    reference_index: dict[str, list[str]] = {}
    for item in baseline:
        reference_index.setdefault(_key(item["name"]), []).append(item["source_id"])
    for item in rows:
        match = aliases.get(_key(item["name"]), _key(item["name"]))
        item["related_known_record_ids"] = sorted(set(reference_index.get(match, [])))
        item["identity_dedup_status"] = (
            "EXACT_OR_CURATED_ALIAS_MATCH_REVIEW" if item["related_known_record_ids"]
            else "UNMATCHED_OR_VARIANT_REVIEW"
        )
    result = {
        "schema": "cine.company.technology_knowledge.v215",
        "baseline_count": len(radar["items"]), "research_v214_count": len(rnd["items"]),
        "user_source_row_count": len(rows), "workflow_count": len(flows),
        "sections": sorted({x["section_number"] for x in rows} | {11}),
        "user_source_hashes": provenance,
        "entries": baseline + rows, "workflows": flows,
        "owner_approved_installation": False, "paid_api_authorized": False,
        "new_candidates_automatically_qualified": 0,
        "no_proprietary_reference_execution": True,
        "new_tools_production_authority": False,
    }
    return result


def query_company_knowledge(*, query: str = "", minor_niche: str | None = None,
                            department: str | None = None,
                            kind: str | None = None, limit: int = 15) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("QUERY_LIMIT_OUT_OF_RANGE")
    if department and department not in {d.value for d in DepartmentId}:
        raise ValueError("UNKNOWN_DEPARTMENT")
    if kind and kind not in set(KINDS.values()) | {"BASELINE_96", "PRO_STUDIO_RND_V214"}:
        raise ValueError("UNKNOWN_KNOWLEDGE_KIND")
    knowledge = load_company_knowledge()
    family = production_family(minor_niche, None) if minor_niche else None
    focus = set(FORMAT_TAGS.get(family, ()))
    craft = set(DEPT_TAGS.get(department, ()))
    terms = [t for t in re.findall(r"[a-z0-9]{2,}", unicodedata.normalize("NFKD", query).casefold()) if t]
    results = []
    for row in knowledge["entries"]:
        if kind and row["kind"] != kind:
            continue
        if row["kind"] in {"PROPRIETARY_INHOUSE_REFERENCE_ONLY", "HARDWARE_STORAGE",
                           "STUDIO_CRAFT_SKILL", "SECURITY_POLICY"}:
            # These categories remain searchable as knowledge, not runtime executables.
            pass
        tags = set(row["tags"])
        body = (row["name"] + " " + row["description_from_user_source"]).casefold()
        hits = sum(4 for term in terms if term in body)
        score = hits + 3*len(tags & craft) + 2*len(tags & focus)
        if terms and hits == 0:
            continue
        if not terms and focus and not (tags & focus):
            continue
        if not terms and craft and not (tags & craft):
            continue
        if not terms and not focus and not craft:
            score = 1
        if score <= 0:
            continue
        priority = 1 if row["kind"] == "BASELINE_96" else 0
        results.append((score, priority, row))
    results.sort(key=lambda pair: (-pair[0], -pair[1], pair[2]["name"].casefold(), pair[2]["source_id"]))
    items = []
    for score, _, row in results[:limit]:
        items.append({
            "source_id": row["source_id"], "name": row["name"],
            "kind": row["kind"], "tags": row["tags"],
            "source_line": row.get("source_line"),
            "description": row["description_from_user_source"],
            "similar_registry_records": row.get("related_known_record_ids", []),
            "relevance_score_for_research_only": score,
            "rights_verified": False,
            "runtime_or_performance_verified_by_this_query": False,
            "automatically_approved": False,
        })
    return {
        "schema": "cine.company.technology_knowledge_query.v215",
        "query": query, "minor_niche": minor_niche, "format_family": family,
        "department": department, "kind": kind,
        "knowledge_inventory_total": len(knowledge["entries"]),
        "base_registry_count": knowledge["baseline_count"],
        "user_study_rows": knowledge["user_source_row_count"],
        "research_v214_count": knowledge["research_v214_count"],
        "reference_workflows": knowledge["workflow_count"],
        "matching_records": len(results), "shown": len(items), "items": items,
        "research_only": True, "production_permission": False,
    }


def department_knowledge_index(minor_niche: str, *, top_k: int = 5) -> dict:
    if not 1 <= top_k <= 20:
        raise ValueError("TOP_K_OUT_OF_RANGE")
    mapping = {
        d.value: [item["source_id"] for item in query_company_knowledge(
            minor_niche=minor_niche, department=d.value, limit=top_k
        )["items"]]
        for d in DepartmentId
    }
    return {
        "schema": "cine.company.department_knowledge_router.v215",
        "niche": minor_niche, "department_count": len(mapping),
        "department_candidate_references": mapping,
        "citation_reference_only": True,
        "recommendations_do_not_authorize_backend_execution": True,
    }
