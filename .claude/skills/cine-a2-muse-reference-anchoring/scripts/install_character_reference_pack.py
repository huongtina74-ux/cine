#!/usr/bin/env python3
"""Import user-provided Bell & Leaf image assets into local CINE without overwriting canon."""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import stat
import tempfile
import zipfile

SCHEMA="cine.a2.character_reference_library.v1.1.r1"
TAGS={"bo","me","juno","Lia","bubu","bix","ongngoai","bangoai","ongnoi","banoi"}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_unpack(pack, tmp):
    if pack.suffix.lower() == ".zip":
        with zipfile.ZipFile(pack) as archive:
            for entry in archive.infolist():
                name=pathlib.PurePosixPath(entry.filename)
                if name.is_absolute() or ".." in name.parts or (entry.external_attr >> 16) & 0o170000 == stat.S_IFLNK:
                    raise ValueError("Unsafe ZIP member: " + entry.filename)
            archive.extractall(tmp)
        root=pathlib.Path(tmp)
    else:
        root=pack
    candidates=list(root.rglob("metadata/CHARACTER_REFERENCE_REGISTRY.json"))
    if len(candidates)!=1:
        raise ValueError("Expected one unambiguous registry in asset pack")
    source=candidates[0].parent.parent
    manifest=json.loads(candidates[0].read_text(encoding="utf-8"))
    if manifest.get("schema")!=SCHEMA:
        raise ValueError("Unrecognized asset pack schema")
    if {c["tag"] for c in manifest["characters"]}!=TAGS or len(manifest["assets"])!=90:
        raise ValueError("Incorrect character tags/count; refusing to alter CINE")
    for character in manifest["characters"]:
        source_file=source/character["original"]["file"]
        if not source_file.is_file() or digest(source_file)!=character["original"]["sha256"]:
            raise ValueError("Original image missing or damaged: "+str(source_file))
    for asset in manifest["assets"]:
        if asset.get("approved") or asset.get("canonical") or asset.get("muse_generated"):
            raise ValueError("Misleading approval or generation flag: "+asset["asset_id"])
        for path_key,hash_key in (("native_image","native_sha256"),("convenience_preview","preview_sha256")):
            f=source/asset[path_key]
            if not f.is_file() or digest(f)!=asset[hash_key]:
                raise ValueError("Asset missing or damaged: "+str(f))
    return source

def install(cine_path, pack):
    if not cine_path.is_dir() or not (cine_path/".git").exists():
        raise ValueError("CINE repository must be an existing Git worktree")
    with tempfile.TemporaryDirectory() as tmp:
        source=verify_unpack(pack, tmp)
        dest=cine_path/"assets/canon/character_refs/slow_english_a2/v1_1_r1"
        if dest.exists():
            existing=dest/"metadata/CHARACTER_REFERENCE_REGISTRY.json"
            source_manifest=source/"metadata/CHARACTER_REFERENCE_REGISTRY.json"
            if not existing.exists() or digest(existing)!=digest(source_manifest):
                raise ValueError("Different version already installed: stop to preserve original files")
            print("Already installed; originals and candidate hashes unchanged")
            return
        dest.parent.mkdir(parents=True,exist_ok=True)
        staging=dest.with_name(dest.name+".tmp_"+str(os.getpid()))
        try:
            shutil.copytree(source,staging)
            staging.rename(dest)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        print("CINE assets imported: "+str(dest))
        print("10 original sheets + 90 independent SOURCE CROPS: PENDING HUMAN REVIEW")
        print("270 target Muse views/expressions are PENDING_NEW_RENDER, not present as new Muse images")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("cine_repo",type=pathlib.Path)
    parser.add_argument("asset_pack_directory_or_zip",type=pathlib.Path)
    args=parser.parse_args()
    install(args.cine_repo.resolve(),args.asset_pack_directory_or_zip.resolve())
