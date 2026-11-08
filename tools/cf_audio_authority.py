#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CINE Audio single-source-of-truth audit (thin delegate; NO duplicate QC rules).

Actual production/QC drift logic lives only in Afanta studio_os.authority_bridge.
No mutating action, writing, publishing, or Git stage performed by this tool.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

CINE_ROOT=Path(__file__).resolve().parents[1]

def locate_afanta_root():
    explicit=os.environ.get("AFANTA_AUDIO_ROOT")
    if explicit:
        candidate=Path(explicit).resolve()
        if (candidate/"studio_os/authority_bridge.py").is_file():return candidate
        raise FileNotFoundError("AFANTA_AUDIO_ROOT_EXPLICIT_PATH_INVALID")
    for parent in CINE_ROOT.parents:
        candidate=parent/"AfantaStudio_Viettruyen"/"AfantaStudio_Viettruyen"
        if (candidate/"studio_os/authority_bridge.py").is_file():
            return candidate
    raise FileNotFoundError("AFANTA_AUDIO_ROOT_NOT_FOUND_IN_PARENT_CHAIN")

try:
    AFANTA_DEFAULT=locate_afanta_root()
except FileNotFoundError:
    # Keep audit importable on a fresh CINE-only checkout, but fail closed
    # when invoked without a present Afanta QC validator.
    AFANTA_DEFAULT=CINE_ROOT/".not_configured_afanta_audio_root"

def audit(cine_root=None,afanta_root=None,require_lock=True):
    cine=Path(cine_root or CINE_ROOT).resolve()
    afanta=Path(afanta_root or AFANTA_DEFAULT).resolve()
    if not (afanta/"studio_os"/"authority_bridge.py").is_file():
        return {"status":"AUDIO_RULE_AUTHORITY_HOLD",
                "issues":["AFANTA_QC_CANONICAL_VERIFIER_MISSING"],
                "strategy_owner":"CINE","qc_owner":"AFANTA","can_route_production":False,
                "can_publish":False}
    sys.path.insert(0,str(afanta))
    try:
        from studio_os.authority_bridge import audit as check
        return check(cine_root=cine,afanta_root=afanta,require_lock=require_lock)
    finally:
        sys.path.remove(str(afanta))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command",choices=["audit"])
    p.add_argument("--afanta-root",type=Path,default=AFANTA_DEFAULT)
    args=p.parse_args(argv)
    output=audit(afanta_root=args.afanta_root)
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return 2 if output.get("issues") else 0

if __name__=="__main__":
    raise SystemExit(main())
