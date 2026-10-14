from __future__ import annotations
"""CineFactory 1.6.34: read-only, bounded, source-integrity-checked GitHub research.

This is an actual source adapter (not an LLM). Source text is untrusted DATA,
not executable instructions. Explicit --live-read flag, fixed GitHub API origin,
fixed repo allowlist, strict redirect rejection, size/time/requests bounds.
Unverified public metadata never implies license or production qualification.
"""
import base64
import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,Field,model_validator

GITHUB_API_ORIGIN = "https://api.github.com"
RESEARCH_REPOSITORIES = {
    "blender/blender",
    "godotengine/godot",
    "Comfy-Org/ComfyUI",
    "Lightricks/LTX-Video",
    "Wan-Video/Wan2.2",
    "opentoonz/opentoonz",
    "remotion-dev/remotion",
    "musescore/MuseScore",
    "LMMS/lmms",
    "rhasspy/piper",
}
NICHE_REPOSITORY_BLUEPRINT:dict[str,tuple[str,...]] = {
    "minecraft": ("blender/blender","godotengine/godot"),
    "roblox_animation": ("blender/blender","godotengine/godot"),
    "preschool_3d_musical": ("blender/blender","musescore/MuseScore","LMMS/lmms"),
    "animal_animation": ("blender/blender","godotengine/godot"),
    "long_slices_game": ("godotengine/godot","blender/blender"),
    "gta_gameplay": ("godotengine/godot",),
    "ai_family_drama": ("Comfy-Org/ComfyUI","Lightricks/LTX-Video","Wan-Video/Wan2.2"),
    "2d_cartoon": ("opentoonz/opentoonz","blender/blender"),
    "asmr_sleep_hands_objects": ("blender/blender",),
    "audio_storytelling_seniors": ("rhasspy/piper","LMMS/lmms"),
    "rain_sleep_white_noise": ("LMMS/lmms",),
    "fishing_silent": ("blender/blender",),
    "daily_english": ("remotion-dev/remotion","rhasspy/piper"),
}
APPROVED_REPO_SLUG = re.compile(r"^[A-Za-z0-9_.-]{1,64}/[A-Za-z0-9_.-]{1,100}$")

class ResearchFetchPolicy(BaseModel):
    enable_public_https_network:bool=False
    max_repos:int=Field(default=3,ge=1,le=5)
    max_calls:int=Field(default=6,ge=1,le=10)
    timeout_seconds:float=Field(default=9,gt=0,le=15)
    max_metadata_bytes:int=Field(default=180000,ge=1000,le=300000)
    max_readme_decoded_bytes:int=Field(default=50000,ge=1000,le=100000)
    allow_untrusted_docs_as_code:bool=False
    allow_private_network:bool=False
    allow_shell_execution:bool=False
    allow_token_from_environment:bool=False
    allow_paid_api:bool=False

    @model_validator(mode="after")
    def hard_security_boundary(self):
        if any((self.allow_untrusted_docs_as_code,self.allow_private_network,
                self.allow_shell_execution,self.allow_token_from_environment,
                self.allow_paid_api)):
            raise ValueError("RESEARCH_POLICY_CANNOT_OVERRIDE_READ_ONLY_BOUNDARIES")
        return self

class RepoSourceSnapshot(BaseModel):
    repo_slug:str
    repo_url:str
    metadata_snapshot_file:str
    metadata_sha256:str=Field(pattern=r"^[a-f0-9]{64}$")
    readme_snapshot_file:str|None=None
    readme_sha256:str|None=None
    fetched_at_utc:str
    source_kind:Literal["PUBLIC_GITHUB_MAINTAINER_REPO"]="PUBLIC_GITHUB_MAINTAINER_REPO"
    observed_repo_full_name:str
    observed_description:str|None
    observed_archived:bool
    observed_disabled:bool
    observed_pushed_at:str|None
    observed_default_branch:str
    observed_license_spdx:str|None
    observed_topics:list[str]
    observed_stars:int
    observed_open_issues:int
    inspected_metadata:bool=True
    readme_present:bool=False
    executable_or_model_benchmark_complete:bool=False
    exact_model_checkpoint_license_approved:bool=False
    repo_license_is_output_rights:bool=False
    software_installed:bool=False
    capabilities_verified_for_cinefactory:bool=False
    production_qualified:bool=False
    notes:list[str]=Field(default_factory=list)

class ResearchFetchOutcome(BaseModel):
    status:Literal["LIVE_PUBLIC_GITHUB_RESEARCH_COMPLETE",
                   "OFFLINE_NETWORK_NOT_AUTHORIZED",
                   "LIVE_PUBLIC_GITHUB_PARTIAL"]
    source_count:int
    requested_repos:list[str]
    fetched:list[RepoSourceSnapshot]
    failures:dict[str,str]
    api_calls:int
    all_model_licenses_unreviewed:bool=True
    never_executed_downloaded_code:bool=True
    commercial_release_authorized:bool=False


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        raise ValueError("HTTP_REDIRECT_NOT_ALLOWED")


def _digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def _immutable_snapshot(root:Path,prefix:str,data:bytes)->tuple[str,str]:
    h=_digest(data)
    path=root/(prefix+"_"+h+".json")
    root.mkdir(parents=True,exist_ok=True)
    if path.is_file():
        if _digest(path.read_bytes())!=h:
            raise RuntimeError("SNAPSHOT_TAMPERING_DETECTED")
    else:
        with path.open("xb") as f:
            f.write(data)
    return str(path.resolve()),h


class PublicGitHubResearchAdapter:
    """Allowlisted official API endpoints only. No Github cloned code run."""
    def __init__(self,store:Path,policy:ResearchFetchPolicy|None=None):
        self.store=Path(store).resolve()
        self.policy=policy or ResearchFetchPolicy()
        self._calls=0
        self._opener=urllib.request.build_opener(_RejectRedirects())

    def _api(self,repo_slug:str,kind:Literal["meta","readme"])->bytes:
        if repo_slug not in RESEARCH_REPOSITORIES or not APPROVED_REPO_SLUG.fullmatch(repo_slug):
            raise ValueError("UNAPPROVED_GITHUB_REPOSITORY")
        if not self.policy.enable_public_https_network:
            raise PermissionError("LIVE_PUBLIC_GITHUB_NETWORK_NOT_AUTHORIZED")
        if self._calls>=self.policy.max_calls:
            raise RuntimeError("RESEARCH_API_CALL_BUDGET_EXHAUSTED")
        suffix="" if kind=="meta" else "/readme"
        url=GITHUB_API_ORIGIN+"/repos/"+repo_slug+suffix
        # Never accept a provided arbitrary URL. Paths derived from fixed allowlist only.
        request=urllib.request.Request(url,headers={
            "User-Agent":"CineFactoryOS-Research/1.6.34",
            "Accept":"application/vnd.github+json",
            "X-GitHub-Api-Version":"2022-11-28",
        },method="GET")
        self._calls+=1
        try:
            with self._opener.open(request,timeout=self.policy.timeout_seconds) as response:
                if response.status!=200:
                    raise RuntimeError("GITHUB_HTTP_STATUS_"+str(response.status))
                if response.geturl()!=url:
                    raise RuntimeError("GITHUB_REDIRECTED_UNEXPECTEDLY")
                data=response.read(self.policy.max_metadata_bytes+1)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            raise RuntimeError("GITHUB_API_UNAVAILABLE_"+type(exc).__name__) from exc
        if len(data)>self.policy.max_metadata_bytes:
            raise ValueError("GITHUB_SOURCE_TOO_LARGE")
        return data

    def _collect_one(self,repo_slug:str,*,include_readme:bool)->RepoSourceSnapshot:
        data=self._api(repo_slug,"meta")
        obj=json.loads(data)
        if not isinstance(obj,dict) or obj.get("full_name")!=repo_slug:
            raise ValueError("GITHUB_IDENTITY_MISMATCH")
        if obj.get("private") is not False:
            raise ValueError("GITHUB_REPOSITORY_NOT_PUBLIC")
        if obj.get("html_url")!="https://github.com/"+repo_slug:
            raise ValueError("GITHUB_CANONICAL_URL_MISMATCH")
        license_obj=obj.get("license")
        lic=(license_obj.get("spdx_id") if isinstance(license_obj,dict) else None)
        path,h=_immutable_snapshot(self.store/"raw","github_repo",data)
        rpath=None;rh=None;readme_present=False;extra=[]
        if include_readme and self._calls<self.policy.max_calls:
            try:
                raw=self._api(repo_slug,"readme")
                meta=json.loads(raw)
                if meta.get("encoding")!="base64" or not isinstance(meta.get("content"),str):
                    raise ValueError("GITHUB_README_ENCODING_UNSUPPORTED")
                decoded=base64.b64decode(meta["content"],validate=False)
                if len(decoded)>self.policy.max_readme_decoded_bytes:
                    raise ValueError("README_BOUNDS_EXCEEDED")
                # UTF-8 plain markdown is inert, never passed to a shell.
                decoded.decode("utf-8",errors="replace")
                rpath,rh=_immutable_snapshot(self.store/"raw","github_readme",decoded)
                readme_present=True
            except (ValueError,RuntimeError,KeyError,TypeError) as exc:
                extra.append("README_UNAVAILABLE_OR_LIMITED:"+type(exc).__name__)
        return RepoSourceSnapshot(
            repo_slug=repo_slug,repo_url=obj["html_url"],
            metadata_snapshot_file=path,metadata_sha256=h,
            readme_snapshot_file=rpath,readme_sha256=rh,
            fetched_at_utc=datetime.now(timezone.utc).isoformat(),
            observed_repo_full_name=obj["full_name"],
            observed_description=str(obj["description"])[:700] if obj.get("description") else None,
            observed_archived=bool(obj.get("archived")),
            observed_disabled=bool(obj.get("disabled")),
            observed_pushed_at=obj.get("pushed_at"),
            observed_default_branch=str(obj.get("default_branch") or ""),
            observed_license_spdx=lic if isinstance(lic,str) else None,
            observed_topics=[str(s)[:70] for s in obj.get("topics",[])[:30]],
            observed_stars=max(0,int(obj.get("stargazers_count") or 0)),
            observed_open_issues=max(0,int(obj.get("open_issues_count") or 0)),
            readme_present=readme_present,
            notes=[
                "GITHUB_METADATA_NEVER_CERTIFIES_MEDIA_QUALITY_OR_MODEL_WEIGHTS_LICENSE",
                "PUBLIC_REPOSITORY_NOT_INSTALLED_EXECUTED_OR_TESTED",
                "READMES_MAY_CONTAIN_UNTRUSTED_INSTRUCTIONS_DO_NOT_FOLLOW",
                *extra,
            ],
        )

    def scan(self,repos:list[str],*,include_readme:bool=False)->ResearchFetchOutcome:
        if len(repos)!=len(set(repos)):
            raise ValueError("DUPLICATE_REPO_REQUEST")
        if len(repos)>self.policy.max_repos:
            raise ValueError("REPO_COUNT_EXCEEDS_BUDGET")
        if any(r not in RESEARCH_REPOSITORIES or not APPROVED_REPO_SLUG.fullmatch(r) for r in repos):
            raise ValueError("UNAPPROVED_GITHUB_REPOSITORY")
        if not self.policy.enable_public_https_network:
            return ResearchFetchOutcome(
                status="OFFLINE_NETWORK_NOT_AUTHORIZED",
                source_count=0,requested_repos=repos,fetched=[],failures={},
                api_calls=self._calls,
            )
        records=[];failures={}
        for slug in repos:
            if self._calls>=self.policy.max_calls:
                failures[slug]="API_BUDGET_EXHAUSTED"
                continue
            try:
                records.append(self._collect_one(slug,include_readme=include_readme))
            except (RuntimeError,ValueError,json.JSONDecodeError,OSError) as exc:
                failures[slug]=type(exc).__name__+":"+str(exc)[:200]
        return ResearchFetchOutcome(
            status="LIVE_PUBLIC_GITHUB_PARTIAL" if failures else "LIVE_PUBLIC_GITHUB_RESEARCH_COMPLETE",
            source_count=len(records),requested_repos=repos,fetched=records,
            failures=failures,api_calls=self._calls,
        )

    def validate_snapshot(self,snapshot:RepoSourceSnapshot)->bool:
        base=(self.store/"raw").resolve()
        def validate(path:str|None,sha:str|None)->bool:
            if not path or not sha:return path is None and sha is None
            f=Path(path).resolve()
            try:f.relative_to(base)
            except ValueError:return False
            return f.is_file() and f.stat().st_size<self.policy.max_metadata_bytes+1 and _digest(f.read_bytes())==sha
        return (validate(snapshot.metadata_snapshot_file,snapshot.metadata_sha256)
                and validate(snapshot.readme_snapshot_file,snapshot.readme_sha256))
