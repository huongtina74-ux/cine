"""Select verified optional Story Skills techniques for an existing CINE A2 role.

Original Story Skills repo stays read-only, not installed as a parallel Studio OS.
Its book-writing file conventions DO NOT override Bell & Leaf source Canon.
"""
from __future__ import annotations
import hashlib,json,pathlib,re,subprocess
from typing import Optional
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAP="config/story_factory/a2_bell_leaf_external_skill_sources.json"
DEFAULT_SOURCE=pathlib.Path(r"C:\Users\ADMIN\Documents\CINE_A2_Research_Audit_20261022\repos\story-skills")
PER_SKILL_LIMIT=3000
TOTAL_LIMIT=6000

def load_for_role(role_id,repo=ROOT,source=DEFAULT_SOURCE):
    repo=pathlib.Path(repo)
    info=json.loads((repo/MAP).read_text(encoding="utf-8"))
    refs=info.get("role_skill_references",{}).get(role_id)
    if not isinstance(refs,list):raise ValueError("Unknown CINE role in external craft map")
    source=pathlib.Path(source)
    if not source.is_dir():
        return {"status":"OPTIONAL_REPO_NOT_INSTALLED","items":[],"injected_to_writer":False}
    expected=next(x["observed_windows_commit_prefix"] for x in info["repositories"] if x["id"]=="story-skills")
    try:
        commit=subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True,timeout=10).strip()
    except (subprocess.CalledProcessError,OSError,subprocess.TimeoutExpired) as exc:
        raise ValueError("Story Skills checkout not verifiable") from exc
    if not commit.startswith(expected):
        raise ValueError("Story Skills checkout commit changed; review source before injection")
    items=[]
    for name in refs:
        if not re.fullmatch("[a-z][a-z0-9-]{1,72}",name):
            raise ValueError("Invalid external skill name")
        f=(source/"skills"/name/"SKILL.md").resolve()
        if not f.is_relative_to(source.resolve()) or not f.is_file():
            raise ValueError("Mapped Story Skills skill missing: "+name)
        raw=f.read_text(encoding="utf-8")
        # Include original method intro up to bounded character count.
        # Do not impose the upstream project's book directories on CINE.
        excerpt=raw[:PER_SKILL_LIMIT]
        items.append({"skill":name,"license":"MIT","sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
           "usage":"ADVISORY_CRAFT_TECHNIQUES_ONLY_NO_UPSTREAM_BOOK_FILE_CONVENTIONS",
           "technique_excerpt":excerpt})
    if sum(len(x["technique_excerpt"]) for x in items)>TOTAL_LIMIT:
        raise ValueError("External guidance exceeds bounded context")
    return {"status":"EXTERNAL_CRAFT_READ_ONLY_LOADED","items":items,
       "injected_to_writer":bool(items),"observed_commit":commit,"model_or_cli_executed_from_external_repo":False}
