#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CINE Audio research handoff: thin creator/checker, Afanta owns QC validator.

No fabricated data, fake third-party source, API call, script generation or upload.
Real researchers complete the CINE-owned source and review manifest explicitly.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def locate_afanta_root():
    explicit=os.environ.get("AFANTA_AUDIO_ROOT")
    if explicit:
        candidate=Path(explicit).resolve()
        if (candidate/"studio_os/research_handoff.py").is_file():return candidate
        raise FileNotFoundError("AFANTA_AUDIO_ROOT_EXPLICIT_PATH_INVALID")
    for parent in ROOT.parents:
        candidate=parent/"AfantaStudio_Viettruyen"/"AfantaStudio_Viettruyen"
        if (candidate/"studio_os/research_handoff.py").is_file():
            return candidate
    raise FileNotFoundError("AFANTA_AUDIO_ROOT_NOT_FOUND_IN_PARENT_CHAIN")

try:
    AFANTA_ROOT=locate_afanta_root()
except FileNotFoundError:
    # CINE may be checked out without Afanta. Remain importable for help and
    # audits, but a real handoff must fail closed until its validator exists.
    AFANTA_ROOT=ROOT/".not_configured_afanta_audio_root"

def run(action,slug,cine_root=None,afanta_root=None):
    cine=Path(cine_root or ROOT).resolve()
    afanta=Path(afanta_root or AFANTA_ROOT).resolve()
    if not (afanta/"studio_os/research_handoff.py").is_file():
        raise FileNotFoundError("AFANTA_CANONICAL_AUDIO_RESEARCH_VALIDATOR_REQUIRED")
    sys.path.insert(0,str(afanta))
    try:
        from studio_os.research_handoff import template,verify
        if action=="template":
            return template(slug,cine_root=cine)
        return verify(slug,cine_root=cine)
    finally:
        sys.path.remove(str(afanta))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("action",choices=("template","check"))
    p.add_argument("--slug",required=True)
    p.add_argument("--afanta-root",type=Path,default=AFANTA_ROOT)
    args=p.parse_args(argv)
    try:
        result=run(args.action,args.slug,afanta_root=args.afanta_root)
    except (ValueError,OSError,TypeError,KeyError) as exc:
        result={"status":"CINE_AUDIO_HANDOFF_HOLD","issues":[str(exc)[:250]]}
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 2 if result.get("issues") else 0

if __name__=="__main__":
    raise SystemExit(main())
