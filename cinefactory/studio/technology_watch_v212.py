"""v212: whole-company source watch. Read only fixed public sources.

Never install an MCP server, clone code, change providers, call Claude inference,
or assume that a webpage hash change means an AI model is production-ready.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit, urlencode
import json
import re
import urllib.request

from .technology_discovery_v211 import _safe_event_path, _NoRedirect

# All outbound URLs are derived from this fixed allowlist and constant
# query fragments, never a YouTube title or external server advertisement.
WATCH = {
    "claude_code":("GITHUB_RELEASE","anthropics/claude-code","CLAUDE_AGENT"),
    "claude_agent_sdk":("GITHUB_RELEASE","anthropics/claude-agent-sdk-typescript","CLAUDE_AGENT"),
    "claude_plugins":("GITHUB_COMMIT","anthropics/claude-plugins-official","CLAUDE_PLUGIN"),
    "claude_plugins_community":("GITHUB_COMMIT","anthropics/claude-plugins-community","CLAUDE_PLUGIN"),
    "claude_platform_notes":("VENDOR_PAGE","https://platform.claude.com/docs/en/release-notes/overview","CLAUDE_MODEL_PLATFORM"),
    "mcp_registry_project":("GITHUB_RELEASE","modelcontextprotocol/registry","MCP_PROTOCOL"),
    "mcp_servers_reference":("GITHUB_COMMIT","modelcontextprotocol/servers","MCP_PROTOCOL"),
    "mcp_registry_video":("MCP_REGISTRY","video","MCP_SERVER"),
    "mcp_registry_blender":("MCP_REGISTRY","blender","MCP_SERVER"),
    "mcp_registry_audio":("MCP_REGISTRY","audio","MCP_SERVER"),
    "mcp_registry_youtube":("MCP_REGISTRY","youtube","MCP_SERVER"),
    "comfyui":("GITHUB_RELEASE","Comfy-Org/ComfyUI","PRODUCTION_SOFTWARE"),
    "comfy_workflows":("GITHUB_COMMIT","Comfy-Org/workflow_templates","PRODUCTION_SOFTWARE"),
    "ffmpeg":("GITHUB_RELEASE","FFmpeg/FFmpeg","PRODUCTION_SOFTWARE"),
    "blender":("GITHUB_RELEASE","blender/blender","PRODUCTION_SOFTWARE"),
    "freevideo":("GITHUB_RELEASE","FlashML-org/FreeVideo","VIDEO_AI"),
    "flux2":("GITHUB_COMMIT","black-forest-labs/flux2","IMAGE_AI"),
    "moss_tts":("GITHUB_RELEASE","OpenMOSS/MOSS-TTS","AUDIO_AI"),
    "ace_step":("GITHUB_RELEASE","ace-step/ACE-Step-1.5","AUDIO_AI"),
    "hyperframes":("GITHUB_RELEASE","heygen-com/hyperframes","EDITING_SOFTWARE"),
    "runway_changelog":("VENDOR_PAGE","https://runwayml.com/changelog","SAAS_PLATFORM"),
    "adobe_firefly":("VENDOR_PAGE","https://www.adobe.com/products/firefly.html","SAAS_PLATFORM"),
    "heygen_saas":("VENDOR_PAGE","https://www.heygen.com/","SAAS_PLATFORM"),
}
WATCH_KINDS={"GITHUB_RELEASE","GITHUB_COMMIT","VENDOR_PAGE","MCP_REGISTRY"}
MAX_BYTES=250000
MAX_SOURCES_PER_RUN=6

def _source_url(source_id:str) -> str:
    kind,target,_=WATCH[source_id]
    if kind.startswith("GITHUB"):
        suffix="releases" if kind=="GITHUB_RELEASE" else "commits"
        return f"https://api.github.com/repos/{target}/{suffix}?per_page=1"
    if kind=="MCP_REGISTRY":
        return "https://registry.modelcontextprotocol.io/v0.1/servers?"+urlencode({
            "search":target,"version":"latest","limit":"6",
        })
    return target

def _fetch_url(url:str,timeout:int=8)->bytes:
    if not 1<=timeout<=12:
        raise ValueError("WATCH_TIMEOUT_BUDGET_EXCEEDED")
    opener=urllib.request.build_opener(_NoRedirect())
    req=urllib.request.Request(url,headers={
        "User-Agent":"CineFactoryTechnologySourceWatch/2.12",
        "Accept":"application/vnd.github+json, application/json, text/html",
    },method="GET")
    with opener.open(req,timeout=timeout) as reply:
        if reply.status!=200 or reply.geturl()!=url:
            raise ValueError("WATCH_RESPONSE_HOST_REDIRECTED")
        data=reply.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES:
            raise ValueError("WATCH_RESPONSE_TOO_LARGE")
        return data

def _parse(source_id:str,raw:bytes) -> dict:
    if len(raw)>MAX_BYTES:
        raise ValueError("WATCH_RESPONSE_TOO_LARGE")
    kind,target,category=WATCH[source_id]
    envelope={"source_id":source_id,"kind":kind,"category":category,
              "canonical_source":_source_url(source_id),
              "release_or_page_observed":False,
              "code_weight_rights_verified":False,
              "mcp_execution_allowed":False,
              "claude_paid_inference_allowed":False}
    if kind=="VENDOR_PAGE":
        if not raw.strip():
            raise ValueError("VENDOR_PAGE_EMPTY")
        return {**envelope,"metadata_kind":"VENDOR_PAGE_CONTENT_DIGEST",
                "content_sha256":sha256(raw).hexdigest(),
                "semantic_release_verified":False,
                "reason":"Website HTML changes may be dynamic and are not model release evidence"}
    body=json.loads(raw)
    if kind=="MCP_REGISTRY":
        if not isinstance(body,dict) or not isinstance(body.get("servers"),list):
            raise ValueError("MCP_REGISTRY_INVALID_SHAPE")
        names=[]
        for item in body["servers"][:6]:
            if not isinstance(item,dict):
                continue
            server=item.get("server")
            if not isinstance(server,dict):
                continue
            name=server.get("name")
            if isinstance(name,str) and len(name)<=180 and "/" in name:
                names.append(name)
        return {**envelope,"metadata_kind":"OFFICIAL_MCP_SERVER_NAMES",
                "unverified_server_names":sorted(set(names)),
                "registry_metadata_only":True,
                "server_authentication_verified":False,
                "server_capability_claims_verified":False,
                "server_package_integrity_verified":False}
    if not isinstance(body,list):
        raise ValueError("GITHUB_WATCH_INVALID_SHAPE")
    candidate=body[0] if body else None
    if not isinstance(candidate,dict):
        return {**envelope,"metadata_kind":"EMPTY_OFFICIAL_REPO_RESPONSE",
                "note":"Missing releases is not evidence repository is abandoned."}
    if kind=="GITHUB_RELEASE":
        version=candidate.get("tag_name")
        pub=candidate.get("published_at")
        if not isinstance(version,str) or not version or len(version)>130:
            raise ValueError("GITHUB_RELEASE_TAG_INVALID")
        if not isinstance(pub,str) or len(pub)>40:
            pub=None
        return {**envelope,"metadata_kind":"GITHUB_OFFICIAL_RELEASE_TAG",
                "release_or_page_observed":True,"tag":version,
                "published_at":pub,"source_repo":target,
                "security_dependency_license_checked":False}
    sha=candidate.get("sha")
    if not isinstance(sha,str) or not re.fullmatch(r"[0-9a-f]{40}",sha):
        raise ValueError("GITHUB_COMMIT_SHA_INVALID")
    return {**envelope,"metadata_kind":"GITHUB_OFFICIAL_LATEST_COMMIT",
            "release_or_page_observed":True,"commit_sha":sha,
            "source_repo":target,
            "semantic_release_verified":False}

def _receipt_dir(root:Path)->Path:
    folder=Path(root).resolve()/"data"/"research"/"technology_discovery"/"watch"
    folder.mkdir(parents=True,exist_ok=True)
    return folder

def _store_record(root:Path, source_id:str, entry:dict)->dict:
    directory=_receipt_dir(root)
    canonical=json.dumps(entry,ensure_ascii=False,sort_keys=True,
                         separators=(",",":")).encode()
    digest=sha256(canonical).hexdigest()
    path=directory/(f"{source_id}_{digest}.json")
    if path.is_file():
        if path.read_bytes()!=canonical:
            raise RuntimeError("TECH_WATCH_RECEIPT_TAMPERED")
        was_new=False
    else:
        with path.open("xb") as dst:dst.write(canonical)
        was_new=True
    return {"source_id":source_id,"created":was_new,
            "receipt_sha256":digest,"file":str(path),
            "kind":entry["kind"],"category":entry["category"],
            "record_status":"PENDING_RND_SOURCE_REVIEW"}

def watch_public_sources(root:Path, *,source_ids:list[str]|None=None,
                         max_sources:int=4,fetch=None,
                         day_index:int|None=None) -> dict:
    if not 1<=max_sources<=MAX_SOURCES_PER_RUN:
        raise ValueError("TECH_WATCH_NETWORK_BUDGET_EXCEEDED")
    keys=list(WATCH)
    if source_ids is None:
        # Day-based rotation over Claude, MCP, repo/AI and SaaS categories,
        # not an arbitrary unbounded crawl or self-initiated background loop.
        index=(day_index if day_index is not None else
               datetime.now(timezone.utc).timetuple().tm_yday)
        if type(index) is not int or index<0:
            raise ValueError("TECH_WATCH_DAY_INDEX_INVALID")
        groups={
            "CLAUDE": [x for x in keys if WATCH[x][2].startswith("CLAUDE")],
            "MCP": [x for x in keys if WATCH[x][2].startswith("MCP")],
            "AI_SOFTWARE": [x for x in keys if WATCH[x][2] not in
                            {"MCP_SERVER","MCP_PROTOCOL","SAAS_PLATFORM"}
                            and not WATCH[x][2].startswith("CLAUDE")],
            "SAAS": [x for x in keys if WATCH[x][2]=="SAAS_PLATFORM"],
        }
        groups["AI_SOFTWARE"]=[x for x in groups["AI_SOFTWARE"]]
        chosen=[]
        for g in ("CLAUDE","MCP","AI_SOFTWARE","SAAS"):
            arr=groups[g]
            if arr: chosen.append(arr[index%len(arr)])
        source_ids=chosen[:max_sources]
    if (not isinstance(source_ids,list) or len(source_ids)>max_sources
            or len(source_ids)!=len(set(source_ids))
            or any(k not in WATCH for k in source_ids)):
        raise ValueError("TECH_WATCH_SOURCE_NOT_IN_APPROVED_SET")
    additions=[];unchanged=[];errors=[]
    for source_id in source_ids:
        url=_source_url(source_id)
        try:
            raw=fetch(url) if fetch is not None else _fetch_url(url)
            record=_parse(source_id,raw)
            event=_store_record(root,source_id,record)
            (additions if event["created"] else unchanged).append(event)
        except (OSError,ValueError,RuntimeError,TypeError,KeyError,TimeoutError) as exc:
            errors.append({"source_id":source_id,"reason":type(exc).__name__,
                           "status":"SOURCE_UNAVAILABLE_NO_AUTO_PROMOTION"})
    return {"schema":"cine.technology.watch.v212",
            "sources_requested":source_ids,
            "new_source_snapshots":additions,
            "unchanged_source_snapshots":unchanged,
            "source_errors":errors,
            "fixed_source_count":len(WATCH),
            "automatic_mcp_install":False,
            "automatic_claude_upgrade_or_api_call":False,
            "automatic_production_provider_switch":False,
            "new_technology_production_approvals":0,
            "paid_model_credits_spent":0}

def latest_watch_status(root:Path) ->dict:
    folder=Path(root).resolve()/"data"/"research"/"technology_discovery"/"watch"
    found={}
    if folder.is_dir():
        for path in folder.glob("*.json"):
            raw=path.read_bytes()
            hash_=path.stem.rsplit("_",1)[-1]
            if sha256(raw).hexdigest()!=hash_:
                raise RuntimeError("TECH_WATCH_EVIDENCE_HASH_MISMATCH")
            entry=json.loads(raw)
            key=entry.get("source_id")
            if key not in WATCH:
                raise RuntimeError("UNTRUSTED_TECH_WATCH_SOURCE")
            prev=found.get(key,[])
            prev.append(entry)
            found[key]=prev
    return {"schema":"cine.technology.watch_status.v212",
            "tracked_fixed_sources":len(WATCH),
            "sources_with_any_observed_snapshot":len(found),
            "source_snapshots_total":sum(map(len,found.values())),
            "new_version_candidate_ids":sorted(found),
            "all_unqualified_for_model_install_or_mcp_use":True}
