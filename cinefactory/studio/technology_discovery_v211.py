"""CineFactory v211: niche-aware technology discovery with safe persistent backlog.

Production never executes source repositories or downloads model weights. Public
GitHub search (optional) is fixed-origin, bounded and metered API-free. Research
can append candidates to immutable local receipts, NOT core qualified registry.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlencode, urlsplit
import urllib.request
from urllib.request import Request
import json
import re

from .technology_radar_v210 import load_technology_radar

# Each entry is a production technology FAMILY / medium, not a generic
# YouTube keyword. Game capture is not animation and live is not a film.
FAMILY = {
    "FILM_3D": ("blender","flux_klein4b","comfyui","qwen3tts","moss",
                "chatterbox","acestep","ffmpeg","unirig","audio2face"),
    "GAME_CAPTURE": ("ffmpeg","whisper","fasterwhisper","remotion","hyperframes"),
    "LIVE_CAPTURE": ("ffmpeg","whisper","fasterwhisper"),
    "MACHINIMA": ("blender","ffmpeg","chatterbox","qwen3tts"),
    "SLIDE_3D": ("blender","flux_klein4b","ffmpeg","unirig","acestep"),
    "VOICE_STORY": ("moss","qwen3tts","chatterbox","acestep",
                    "ffmpeg","hyperframes"),
    "REAL_ASMR": ("ffmpeg","demucs","pyannote"),
    "FIELD_CAPTURE": ("ffmpeg","whisper"),
    "AMBIENCE": ("ffmpeg","acestep","demucs"),
    "EXPLAINER": ("hyperframes","remotion","ffmpeg","moss","chatterbox",
                  "flux_klein4b"),
    "MUSICAL_3D": ("blender","flux_klein4b","acestep","moss","ffmpeg"),
    "ANIMATION_2D": ("comfyui","flux_klein4b","ffmpeg","hyperframes"),
    "UNRESOLVED": (),
}
MINECRAFT_GROUP = {
    "minecraft_story_adventure": "FILM_3D",
    "minecraft_school_comedy": "FILM_3D",
    "minecraft_monster_fantasy": "FILM_3D",
    "minecraft_animated_challenge": "FILM_3D",
    "minecraft_recorded_survival": "GAME_CAPTURE",
    "minecraft_gameplay_tutorial": "GAME_CAPTURE",
    "minecraft_live_gameplay": "LIVE_CAPTURE",
    "minecraft_scripted_machinima": "MACHINIMA",
}
OTHER_GROUP = {
    "roblox_animation":"FILM_3D", "animal_animation":"FILM_3D",
    "long_slide_game":"SLIDE_3D", "long_slices_game":"SLIDE_3D",
    "asmr_sleep":"REAL_ASMR",
    "asmr_sleep_hands_objects":"REAL_ASMR",
    "rain_sleep_white_noise":"AMBIENCE",
    "fishing_silent":"FIELD_CAPTURE",
    "audio_storytelling_seniors":"VOICE_STORY",
    "daily_english":"EXPLAINER",
    "preschool_musical":"MUSICAL_3D",
    "cartoon_2d":"ANIMATION_2D",
    "gta_gameplay":"GAME_CAPTURE",
}
# Only owned generic production language is sent to GitHub; a competitor
# title, private audience intelligence or user secret is never forwarded.
GITHUB_QUERIES={
    "FILM_3D": ("blender procedural character animation addon",
                "blender automatic lip sync rigging"),
    "GAME_CAPTURE": ("gameplay recording ffmpeg automation",
                     "game video edit highlights automation"),
    "LIVE_CAPTURE": ("open source game stream capture obs"),
    "MACHINIMA": ("minecraft machinima camera animation tool"),
    "SLIDE_3D": ("blender animal animation physics procedural"),
    "VOICE_STORY": ("offline expressive text to speech long form",
                    "audio drama speech sound design"),
    "REAL_ASMR": ("audio noise reduction ffmpeg tool"),
    "FIELD_CAPTURE": ("footage selection auto editor wildlife"),
    "AMBIENCE": ("ambient audio seamless looping synthesizer"),
    "EXPLAINER": ("programmatic video render caption animation",
                  "automatic kinetic typography video"),
    "MUSICAL_3D": ("blender character animation musical rhythm"),
    "ANIMATION_2D": ("2d animation automated tween tool"),
}
# GitHub's unauthenticated public search is very limited. Use one or two
# separate bounded source calls (default one) and do not retry automatically.
GH_HOST="https://api.github.com"
SLUG=re.compile(r"^[A-Za-z0-9_.-]{1,80}/[A-Za-z0-9_.-]{1,100}$")
MAX_RESULTS=5

def _homepage_hint(value) -> str | None:
    """Store an unverified vendor-site claim but NEVER follow/fetch the URL."""
    if not isinstance(value,str) or len(value)>300:
        return None
    u=urlsplit(value)
    host=(u.hostname or "").lower()
    if (u.scheme!="https" or not host or u.username or u.password
        or u.port is not None or host in {"localhost","127.0.0.1","::1"}
        or host.endswith((".local",".internal",".lan"))
        or host.startswith(("10.","192.168.","172.16.","172.17.","172.18.",
                            "172.19.","172.20.","172.21.","172.22.",
                            "172.23.","172.24.","172.25.","172.26.",
                            "172.27.","172.28.","172.29.","172.30.","172.31."))):
        return None
    return value

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        raise ValueError("EXTERNAL_TECH_SEARCH_REDIRECT_BLOCKED")

_OPENER=urllib.request.build_opener(_NoRedirect())

# Fixed technology vocabulary, independent of a competitor's title.
# An irrelevant GitHub result can never enter the pending queue.
TECH_VOCAB={
    "FILM_3D":("blender","rig","animation","character","lip sync","motion"),
    "GAME_CAPTURE":("gameplay","record","capture","ffmpeg","video edit"),
    "LIVE_CAPTURE":("stream","broadcast","obs","capture"),
    "MACHINIMA":("machinima","minecraft","camera","game cinematic"),
    "SLIDE_3D":("blender","3d","animation","physics","simulation"),
    "VOICE_STORY":("speech","tts","audio","voice","narration"),
    "REAL_ASMR":("audio","noise","ffmpeg","sound"),
    "FIELD_CAPTURE":("video","footage","wildlife","editor"),
    "AMBIENCE":("audio","sound","ambient","music","loop"),
    "EXPLAINER":("video","caption","typography","render","animation"),
    "MUSICAL_3D":("blender","animation","music","rhythm"),
    "ANIMATION_2D":("2d","animation","tween","cartoon"),
}
def _repo_relevant(item:dict,family:str)->bool:
    s=(str(item.get("name") or "")+" "+
       str(item.get("description") or "")).casefold()
    if not any(k in s for k in TECH_VOCAB.get(family,())):
        return False
    if family=="GAME_CAPTURE" and any(k in s for k in (
        "minecraft animation","animation-only","cartoon studio")):
        return False
    if family=="FILM_3D" and any(k in s for k in (
        "livestream capture","obs stream","speedrun recorder")):
        return False
    return True

def production_family(minor_niche: str | None,
                      major_niche: str | None = None) -> str:
    if minor_niche in MINECRAFT_GROUP:
        return MINECRAFT_GROUP[minor_niche]
    if minor_niche in OTHER_GROUP:
        return OTHER_GROUP[minor_niche]
    if major_niche in OTHER_GROUP:
        return OTHER_GROUP[major_niche]
    return "UNRESOLVED"

def propose_technology_for_format(
    minor_niche: str | None, major_niche: str | None = None,
    *, radar: dict | None = None,
) -> dict:
    radar=radar or load_technology_radar()
    family=production_family(minor_niche,major_niche)
    ids=FAMILY[family]
    inventory={x["id"]:x for x in radar["items"]}
    proposals=[]
    for i,id in enumerate(ids):
        row=inventory.get(id)
        if row is None:
            continue
        proposals.append({
            "id":id, "name":row["name"], "department":row["department"],
            "candidate_url":row["official_or_project_url"],
            "priority_within_format":i+1,
            "commercial_gate":row["commercial_gate"],
            "local_runtime":row["local_runtime"],
            "state":"RESEARCH_CANDIDATE_NOT_PRODUCTION_QUALIFIED",
            "licensed_commercial_output_verified":False,
            "actual_runtime_qualified":False,
        })
    return {
        "schema":"cine.research.niche_technology_matching.v211",
        "minor_niche":minor_niche,"major_niche":major_niche,
        "format_family":family,
        "recommendations":proposals,
        "network_queries_allowed_only_in_public_discovery":list(GITHUB_QUERIES.get(family,())),
        "automatic_production_backend_selected":False,
        "competitor_actual_tools_attributed":False,
        "cross_media_lanes_combined":False,
        "requires_human_license_and_security_review":True,
    }

def _canonical_repo(item: dict) -> dict | None:
    if not isinstance(item,dict) or item.get("private") is not False:
        return None
    name=item.get("full_name")
    if not isinstance(name,str) or not SLUG.fullmatch(name):
        return None
    if item.get("html_url")!="https://github.com/"+name:
        return None
    desc=item.get("description")
    lic=item.get("license") or {}
    if not isinstance(lic,dict):lic={}
    # A search result cannot prove that an entire project/weights are
    # commercially usable, even with MIT or Apache listed at repo level.
    return {
        "source_kind":"GITHUB_PUBLIC_SEARCH_METADATA",
        "canonical_url":"https://github.com/"+name,
        "display_name":str(item.get("name") or name.split("/")[-1])[:120],
        "source_identity":name,
        "description":(desc[:400] if isinstance(desc,str) else ""),
        "observed_stars":max(0,int(item.get("stargazers_count") or 0)),
        "observed_last_push":item.get("pushed_at") or None,
        "repo_license_claim":str(lic.get("spdx_id") or "UNKNOWN")[:48],
        "unverified_vendor_website_hint":_homepage_hint(item.get("homepage")),
        "vendor_website_ownership_verified":False,
        "model_weight_license_verified":False,
        "commercial_output_rights_verified":False,
        "producer_tool_chain_attribution_verified":False,
    }

def search_public_github(family: str, *,max_queries:int=1,
                         max_results:int=5, timeout_seconds:int=8,
                         fetch=None) -> tuple[list[dict],list[dict]]:
    if family not in GITHUB_QUERIES:
        return [],[]
    if not (1<=max_queries<=2 and 1<=max_results<=MAX_RESULTS
            and 1<=timeout_seconds<=12):
        raise ValueError("PUBLIC_REPO_DISCOVERY_BUDGET_EXCEEDED")
    found=[];errors=[]
    for query in GITHUB_QUERIES[family][:max_queries]:
        # URL is derived exclusively from the static ontology.
        url=GH_HOST+"/search/repositories?"+urlencode({
            "q":query+" archived:false","sort":"updated",
            "order":"desc","per_page":str(max_results),
        })
        try:
            if fetch is None:
                req=Request(url,headers={
                    "User-Agent":"CineFactoryTechnologyDiscovery/2.11",
                    "Accept":"application/vnd.github+json",
                },method="GET")
                with _OPENER.open(req,timeout=timeout_seconds) as response:
                    if response.status!=200 or response.geturl()!=url:
                        raise ValueError("PUBLIC_GITHUB_RESPONSE_NOT_ORIGIN")
                    raw=response.read(250001)
            else:
                raw=fetch(url)
            if len(raw)>250000:
                raise ValueError("PUBLIC_SEARCH_BODY_TOO_LARGE")
            response=json.loads(raw)
            if not isinstance(response,dict) or not isinstance(response.get("items"),list):
                raise ValueError("GITHUB_SEARCH_SHAPE_INVALID")
            for obj in response["items"][:max_results]:
                record=_canonical_repo(obj)
                if (record and _repo_relevant(obj,family) and
                    not obj.get("archived") and not obj.get("disabled")):
                    record["candidate_relevance"]="CURATED_FAMILY_METADATA_MATCH_NOT_AUDITED"
                    record["discovery_axis"]=family
                    record["query"]=query
                    found.append(record)
        except (OSError,ValueError,RuntimeError,TimeoutError,TypeError,KeyError) as err:
            errors.append({"query":query,"error_type":type(err).__name__,
                           "network_status":"FAILED_NO_MODEL_PROMOTION"})
    return found,errors

def _repo_canonical_from_registry(url: str) -> str | None:
    parsed=urlsplit(url)
    if parsed.netloc.lower()!="github.com":
        return None
    slug=parsed.path.strip("/").split("/")
    return (slug[0]+"/"+slug[1]).casefold() if len(slug)>=2 else None

def _safe_event_path(root: Path) -> Path:
    base=Path(root).resolve()/"data"/"research"/"technology_discovery"/"events"
    base.mkdir(parents=True,exist_ok=True)
    return base

def merge_to_pending(
    root: Path, *,context: dict, candidate_rows:list[dict],
    radar:dict | None=None, now:datetime|None=None,
) -> dict:
    """Append immutable, content-addressed source receipts, never core registry."""
    radar=radar or load_technology_radar()
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError("UTC_RESEARCH_TIMESTAMP_REQUIRED")
    known={s for x in radar["items"]
           if (s:=_repo_canonical_from_registry(x["official_or_project_url"]))}
    # Include previously discovered pending technologies in de-duplication.
    # These are still NOT qualified registry entries.
    dest=_safe_event_path(root)
    for previous in dest.glob("github_*.json"):
        try:
            old=json.loads(previous.read_text(encoding="utf8"))
            if old.get("schema")=="cine.research.technology_candidate.v211":
                name=old["source"].get("source_identity")
                if isinstance(name,str) and SLUG.fullmatch(name):
                    known.add(name.casefold())
        except (OSError,ValueError,KeyError,TypeError):
            # Never rely on corrupted evidence for a production approval.
            raise RuntimeError("PENDING_TECHNOLOGY_EVIDENCE_CORRUPTED") from None
    seen=set()
    new=[];existing=[];rejected=[]
    root=_safe_event_path(root)
    for raw in candidate_rows[:10]:
        item=_canonical_repo({
            "full_name":raw.get("source_identity"),
            "html_url":raw.get("canonical_url"),
            "name":raw.get("display_name"),
            "description":raw.get("description"),
            "private":False,
            "stargazers_count":raw.get("observed_stars"),
            "pushed_at":raw.get("observed_last_push"),
            "license":{"spdx_id":raw.get("repo_license_claim")},
            "homepage":raw.get("unverified_vendor_website_hint"),
        }) if isinstance(raw,dict) and raw.get("source_kind")=="GITHUB_PUBLIC_SEARCH_METADATA" else None
        if not item or raw.get("discovery_axis")!=context.get("format_family"):
            rejected.append("UNSUPPORTED_SOURCE_OR_NICHE_MISMATCH")
            continue
        slug=item["source_identity"].casefold()
        if slug in seen:continue
        seen.add(slug)
        if slug in known:
            existing.append(item["source_identity"])
            continue
        # Canonical source URL bound to actual GitHub search result; source is
        # untrusted and cannot set arbitrary tool IDs, command or output path.
        event={
            "schema":"cine.research.technology_candidate.v211",
            "candidate_status":"PENDING_DISCOVERY_REVIEW",
            "source":item,
            "context":{
                "format_family":context["format_family"],
                "minor_niche":context.get("minor_niche"),
                "major_niche":context.get("major_niche"),
                "origin":"AUTOMATIC_NICHE_OR_COMPETITOR_RESEARCH",
            },
            "production_permissions":{
                "auto_install":False,"repo_clone":False,
                "run_unknown_code":False,"model_download":False,
                "paid_api":False,"switch_backend":False,
                "publish":False,"license_approved":False,
                "gpu_benchmark_passed":False,
            },
            "admission_steps":[
                "MAINTAINER_IDENTITY_AND_COMMIT_REVIEW",
                "CODE_AND_DEPENDENCY_SECURITY_AUDIT",
                "MODEL_WEIGHT_AND_GLOBAL_OUTPUT_LICENSE_CLEARANCE",
                "RTX3060_EXECUTION_BENCHMARK",
                "ORIGINAL_CREATIVE_SCENE_QC",
                "OWNER_APPROVAL_BEFORE_INSTALL_OR_SWITCH",
            ],
        }
        blob=json.dumps(event,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
        content_hash=sha256(blob).hexdigest()
        output=root/("github_"+content_hash+".json")
        if output.exists():
            if output.read_bytes()!=blob:
                raise RuntimeError("TECHNOLOGY_DISCOVERY_RECEIPT_TAMPERED")
        else:
            with output.open("xb") as f:f.write(blob)
        new.append({"url":item["canonical_url"],"path":str(output),
                    "source_sha256":content_hash,"status":"PENDING_DISCOVERY_REVIEW"})
    return {
        "schema":"cine.research.technology_discovery_receipt.v211",
        "pending_additions":new,"already_in_96_base":existing,
        "rejected_count":len(rejected),
        "base_radar_not_mutated":True,
        "production_auto_adopted":False,
        "no_paid_api_used":True,
    }

def run_technology_discovery(
    root:Path, *, minor_niche:str|None, major_niche:str|None=None,
    discover_public:bool=False, max_queries:int=1,
    fetch=None,
) -> dict:
    recommendations=propose_technology_for_format(minor_niche,major_niche)
    found=[];errors=[]
    hf_found=[];hf_errors=[]
    if discover_public and recommendations["format_family"]!="UNRESOLVED":
        found,errors=search_public_github(
            recommendations["format_family"],max_queries=max_queries,fetch=fetch,
        )
        hf_found,hf_errors=search_public_huggingface(
            recommendations["format_family"],fetch=fetch,
        )
    pending=merge_to_pending(root,context=recommendations,
                             candidate_rows=found)
    model_pending=merge_hf_to_pending(
        root,context=recommendations,items=hf_found)
    return {
        "schema":"cine.research.technology_extension.v211",
        "niche_fit":recommendations,
        "discovery_enabled":discover_public,
        "public_queries_attempted":min(max_queries,len(GITHUB_QUERIES.get(
            recommendations["format_family"],()))) if discover_public else 0,
        "source_errors":errors+hf_errors,
        "pending_queue":pending,
        "model_pending_queue":model_pending,
        "public_network_sources":(
            ["GITHUB_PUBLIC_SEARCH","HUGGINGFACE_PUBLIC_MODEL_SEARCH"]
            if discover_public else []
        ),
        "production_technologies_changed":False,
        "actual_competitor_production_stack_verified":False,
        "no_model_installation":True,
        "no_paid_api_used":True,
    }


# Optional public Hugging Face discovery is separate from GitHub source
# repositories. Model-card license and weight rights must be reviewed later.
HF_QUERY={
    "FILM_3D":"character animation",
    "GAME_CAPTURE":"video tracking",
    "LIVE_CAPTURE":"speech recognition",
    "MACHINIMA":"motion capture",
    "SLIDE_3D":"image to 3d",
    "VOICE_STORY":"text-to-speech",
    "REAL_ASMR":"audio enhancement",
    "FIELD_CAPTURE":"video classification",
    "AMBIENCE":"audio generation",
    "EXPLAINER":"text-to-speech",
    "MUSICAL_3D":"music generation",
    "ANIMATION_2D":"image-to-video",
}
HF_ID=re.compile(r"^[A-Za-z0-9_.-]{1,80}/[A-Za-z0-9_.-]{1,130}$")

def search_public_huggingface(
    family: str,*, max_results: int=4,timeout_seconds:int=8,fetch=None,
) -> tuple[list[dict],list[dict]]:
    query=HF_QUERY.get(family)
    if query is None:
        return [],[]
    if not 1<=max_results<=5 or not 1<=timeout_seconds<=12:
        raise ValueError("PUBLIC_MODEL_DISCOVERY_BUDGET_EXCEEDED")
    url="https://huggingface.co/api/models?"+urlencode({
        "search":query,"limit":str(max_results),"sort":"lastModified","direction":"-1",
    })
    try:
        if fetch is None:
            req=Request(url,headers={"User-Agent":"CineFactoryTechnologyDiscovery/2.11",
                                      "Accept":"application/json"},method="GET")
            with _OPENER.open(req,timeout=timeout_seconds) as res:
                if res.status!=200 or res.geturl()!=url:
                    raise ValueError("HUGGING_FACE_RESPONSE_NOT_ORIGIN")
                raw=res.read(250001)
        else:
            raw=fetch(url)
        if len(raw)>250000:
            raise ValueError("HUGGING_FACE_SEARCH_TOO_LARGE")
        rows=json.loads(raw)
        if not isinstance(rows,list):
            raise ValueError("HF_SEARCH_RESPONSE_MALFORMED")
        out=[]
        for item in rows[:max_results]:
            if not isinstance(item,dict) or item.get("private") is True:
                continue
            key=item.get("id")
            if not isinstance(key,str) or not HF_ID.fullmatch(key):
                continue
            # Proprietary-character/brand named fine-tunes are not suitable
            # automatic proposals for the owner's ORIGINAL character assets.
            # Quarantine from shortlist, not a conclusion about infringement.
            if any(term in key.casefold() for term in (
                "pixar","disney","cocomelon","mickey","pokemon",
                "marvel","maizen","jj-and-mikey",
            )):
                continue
            # A speech-to-text checkpoint cannot be recommended as a TTS
            # generator merely because its id contains "speech".
            task=str(item.get("pipeline_tag") or "").casefold()
            if family in {"VOICE_STORY","EXPLAINER"}:
                if task and task not in {"text-to-speech","text-to-audio"}:
                    continue
                # English-first original channels: source-specific mono-
                # language models are not direct English voice candidates.
                if any(token in key.casefold() for token in (
                    "hindi","marathi","urdu","bengali","spanish-only",
                    "arabic-only","telugu",
                )):
                    continue
            out.append({
                "source_kind":"HUGGINGFACE_PUBLIC_MODEL_SEARCH",
                "canonical_url":"https://huggingface.co/"+key,
                "source_identity":key,
                "display_name":key.split("/")[-1],
                "description":str(item.get("pipeline_tag") or "")[:110],
                "observed_downloads":max(0,int(item.get("downloads") or 0)),
                "observed_last_push":item.get("lastModified"),
                "model_card_license_claim":"UNKNOWN_NOT_FETCHED",
                "gated":bool(item.get("gated")),
                "discovery_axis":family,
                "query":query,
                "model_weight_license_verified":False,
                "commercial_output_rights_verified":False,
                "producer_tool_chain_attribution_verified":False,
            })
        return out,[]
    except (OSError,ValueError,TypeError,RuntimeError,TimeoutError,KeyError) as err:
        return [],[{"query":query,"error_type":type(err).__name__,
                    "network_status":"FAILED_NO_MODEL_PROMOTION"}]

def merge_hf_to_pending(root: Path, *,context:dict,
                        items:list[dict],radar:dict|None=None)->dict:
    radar=radar or load_technology_radar()
    known={x["official_or_project_url"].casefold() for x in radar["items"]}
    folder=_safe_event_path(root)
    for previous in folder.glob("hf_*.json"):
        try:
            old=json.loads(previous.read_text(encoding="utf8"))
            if old.get("schema")=="cine.research.technology_candidate.v211":
                existing=old["source"].get("canonical_url")
                if isinstance(existing,str):
                    known.add(existing.casefold())
        except (ValueError,OSError,KeyError,TypeError):
            raise RuntimeError("PENDING_MODEL_EVIDENCE_CORRUPTED") from None
    queued=[];old=[];rejected=0
    for row in items[:5]:
        key=row.get("source_identity") if isinstance(row,dict) else None
        url="https://huggingface.co/"+key if isinstance(key,str) and HF_ID.fullmatch(key) else None
        if (not url or row.get("canonical_url")!=url or
            row.get("source_kind")!="HUGGINGFACE_PUBLIC_MODEL_SEARCH" or
            row.get("discovery_axis")!=context.get("format_family")):
            rejected+=1;continue
        if url.casefold() in known:
            old.append(url);continue
        # No model card/weight rights check can be derived from search metadata.
        record={
            "schema":"cine.research.technology_candidate.v211",
            "candidate_status":"PENDING_MODEL_CARD_WEIGHT_LICENSE_REVIEW",
            "source":{
                "source_kind":"HUGGINGFACE_PUBLIC_MODEL_SEARCH",
                "source_identity":key,"canonical_url":url,
                "observed_downloads":row.get("observed_downloads"),
                "observed_last_push":row.get("observed_last_push"),
                "model_card_license_verified":False,
                "commercial_output_rights_verified":False,
            },
            "context":{
                "format_family":context["format_family"],
                "minor_niche":context.get("minor_niche"),
                "major_niche":context.get("major_niche"),
                "origin":"AUTOMATIC_NICHE_OR_COMPETITOR_RESEARCH",
            },
            "production_permissions":{
                "auto_install":False,"repo_clone":False,
                "run_unknown_code":False,"model_download":False,
                "paid_api":False,"switch_backend":False,
                "publish":False,"license_approved":False,
                "gpu_benchmark_passed":False,
            },
            "admission_steps":[
                "MAINTAINER_AND_MODEL_CARD_IDENTITY",
                "CODE_AND_DEPENDENCY_SECURITY_AUDIT",
                "MODEL_WEIGHTS_AND_WORLDWIDE_OUTPUT_LICENSE",
                "RTX3060_BENCHMARK_ON_APPROVED_LOCAL_INSTALL",
                "INDEPENDENT_ORIGINAL_MEDIA_QC",
                "OWNER_APPROVAL_BEFORE_PRODUCTION_USE",
            ],
        }
        content=json.dumps(record,ensure_ascii=False,sort_keys=True,
                           separators=(",",":")).encode()
        digest=sha256(content).hexdigest()
        target=folder/("hf_"+digest+".json")
        if target.exists():
            if target.read_bytes()!=content:
                raise RuntimeError("PENDING_MODEL_EVIDENCE_TAMPERED")
        else:
            with target.open("xb") as stream:stream.write(content)
        queued.append({"url":url,"path":str(target),"source_sha256":digest,
                       "status":"PENDING_MODEL_CARD_WEIGHT_LICENSE_REVIEW"})
    return {"pending_additions":queued,"already_in_96_base":old,
            "rejected_count":rejected,"base_radar_not_mutated":True,
            "production_auto_adopted":False,"no_paid_api_used":True}


def inspect_pending_technologies(root:Path, *,limit:int=100)->dict:
    """Read-only R&D queue, hash-verifies each receipt; no trust escalation."""
    if not 1<=limit<=300:
        raise ValueError("PENDING_REVIEW_LIMIT_EXCEEDED")
    folder=Path(root).resolve()/"data"/"research"/"technology_discovery"/"events"
    if not folder.is_dir():
        return {"schema":"cine.research.technology_backlog.v211",
                "total":0,"displayed":0,"items":[],
                "all_are_unqualified":True}
    files=sorted(folder.glob("*.json"),key=lambda p:p.stat().st_mtime,reverse=True)
    if len(files)>10000:
        raise ValueError("UNBOUNDED_TECH_DISCOVERY_EVENT_STORE")
    data=[]
    for path in files:
        if not (path.name.startswith(("github_","hf_")) and
                path.name.endswith(".json")):
            continue
        # Ignore no file: an inconsistent or modified receipt breaks review.
        actual=sha256(path.read_bytes()).hexdigest()
        if path.stem.split("_",1)[-1]!=actual:
            raise RuntimeError("PENDING_SOURCE_RECEIPT_HASH_MISMATCH")
        record=json.loads(path.read_text(encoding="utf8"))
        if record.get("schema")!="cine.research.technology_candidate.v211":
            raise RuntimeError("PENDING_SOURCE_RECEIPT_SCHEMA_MISMATCH")
        rights=record.get("production_permissions") or {}
        if any(rights.get(key) is not False for key in (
            "auto_install","run_unknown_code","model_download","paid_api",
            "switch_backend","publish","license_approved",
            "gpu_benchmark_passed",
        )):
            raise RuntimeError("PENDING_RECEIPT_TRIED_TO_ESCALATE_PERMISSIONS")
        data.append({
            "candidate_url":record["source"]["canonical_url"],
            "source_kind":record["source"]["source_kind"],
            "format_family":record["context"]["format_family"],
            "candidate_status":record["candidate_status"],
            "receipt_sha256":actual,
            "independent_license_and_benchmark_required":True,
        })
    return {
        "schema":"cine.research.technology_backlog.v211",
        "total":len(data),
        "displayed":min(limit,len(data)),
        "items":data[:limit],
        "all_are_unqualified":True,
        "automatic_install_or_use_allowed":False,
    }
