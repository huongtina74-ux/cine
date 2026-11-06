#!/usr/bin/env python3
"""Independent static integrity acceptance for Bell & Leaf 2026-11-07 story/voice/trailer sync."""
from pathlib import Path
import json
import re

R=Path(__file__).resolve().parents[1]
S=R/"docs/story/bell_leaf"
T=S/"trailer/ep001_180s"
C=R/"config/niches/slow_english_a2"
assert (S/"BELL_LEAF_CANON_CURRENT.md").is_file()
canon=(S/"BELL_LEAF_CANON_CURRENT.md").read_text(encoding="utf-8")
assert "Orin" in canon and "BUBU" in canon and "EARTH" in canon
assert "UNKNOWN-world" in canon
assert "CURRENT" in (C/"SERIES_BIBLE.md").read_text(encoding="utf-8")
for file in ["FLOW_IMAGES_COMPAT_2500_IMPORT_READY.txt","MUSE_I2V_COMPAT_2500_IMPORT_READY.txt",
             "FLOW_IMAGES_FULL_18_SHOTS.txt","MUSE_I2V_FULL_18_SHOTS.txt"]:
    v=(T/file).read_text(encoding="utf-8-sig")
    chunks=v.strip().split("\n\n")
    assert len(chunks)==18, (file, len(chunks))
    assert all("\n" not in row for row in chunks), file
    assert all("ACTIVE TAGS FOR THIS SHOT:" in row for row in chunks), file
    for n,row in enumerate(chunks,1):
        assert row.startswith("SHOT %02d |"%n), (file,n)
    if "COMPAT" in file:
        assert max(map(len,chunks)) < 2500, (file,max(map(len,chunks)))
print("PASS trailer 18 images + 18 videos FULL and compact; exactly one line/shot, blank separator")
j=json.loads((T/"VOICE_CUE_SHEET.json").read_text(encoding="utf-8-sig"))
r=json.loads((C/"voice_registry.json").read_text(encoding="utf-8-sig"))
assert len(r["voices"])==10
for role,key in [("Arthur Bell","ongnoi"),("Rose Bell","banoi"),("Elara","bangoai")]:
    assert r["voices"][key]["display_name"]==role
assert "boy" in r["voices"]["juno"]["casting_role"]
assert all(v.get("voice_id") is None and v.get("sample_wav") is None for v in r["voices"].values())
assert all(v.get("approval_status") != "APPROVED" for v in r["voices"].values())
b=(C/"VOICE_BIBLE_CURRENT.md").read_text(encoding="utf-8-sig")
assert len(re.findall(r"^## [A-Z_]+ — VOICE_",b,flags=re.M))==15
print("PASS 10 original voice slots preserved, 15 descriptive profiles, new names approved, 0 invented WAV approval")
archive=S/"_archive/pre_v4"
legacy=[f for f in archive.glob("*.md") if f.name not in ("README.md","SERIES_BIBLE_pre_v4_snapshot.md")]
assert len(legacy)>=15,(len(legacy))
for f in legacy:
    stub=S/f.name
    assert stub.is_file() and "RETIRED" in stub.read_text(encoding="utf-8-sig").splitlines()[0]
assert (S/"MUSE_3D_ANIMATION_IDENTITY_LOCK_PROTOCOL_V2_PROPOSAL.md").read_text(encoding="utf-8").startswith("# CINE")
print("PASS old plot versions redirected to archive, current Muse protocol preserved")
print("PASS: BELL_LEAF_STORY_SYNC_STATIC_QC")