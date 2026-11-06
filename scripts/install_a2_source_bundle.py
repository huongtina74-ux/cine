#!/usr/bin/env python3
"""Import Bell & Leaf ORIGINAL source identity images from verified R2 full ZIP.
Never approve candidate Muse angles or draft locations. No overwrites."""
from __future__ import annotations
import argparse, importlib.util, pathlib, tempfile, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
INSTALL=ROOT/".claude/skills/cine-a2-muse-reference-anchoring/scripts/install_character_canon_into_cine_v1_2.py"
NAME="CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2_FINAL.zip"
def install_bundle(bundle:pathlib.Path, repo:pathlib.Path=ROOT, verify_only:bool=False):
    if not bundle.is_file():
        raise FileNotFoundError(f"MISSING_SOURCE_ARCHIVE: {bundle}")
    with tempfile.TemporaryDirectory() as tmp:
        path=bundle
        if bundle.name != NAME:
            with zipfile.ZipFile(bundle) as z:
                matches=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==NAME]
                if len(matches)!=1:raise ValueError("Expected exactly one source character ZIP in R2 bundle")
                info=z.getinfo(matches[0])
                if info.file_size>160_000_000:raise ValueError("Embedded source archive implausibly large")
                path=pathlib.Path(tmp)/NAME
                with z.open(info) as src, path.open("wb") as dst:
                    import shutil
                    shutil.copyfileobj(src,dst)
        spec=importlib.util.spec_from_file_location("canon_source_install",INSTALL)
        if spec is None or spec.loader is None:raise RuntimeError("CINE original source installer not found")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module.install(repo,path,verify_only=verify_only)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle",type=pathlib.Path,required=True,help="R2 FULL.zip or character source ZIP (owned/approved)")
    ap.add_argument("--repo",type=pathlib.Path,default=ROOT)
    ap.add_argument("--verify-only",action="store_true")
    args=ap.parse_args()
    install_bundle(args.bundle,args.repo,args.verify_only)
if __name__=="__main__":main()
