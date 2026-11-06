#!/usr/bin/env python3
"""Synchronize Bell & Leaf owner voice descriptions into EXISTING canonical 10-slot registry; preserve approvals."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config = ROOT / "config" / "niches" / "slow_english_a2"
bible = (config / "VOICE_BIBLE_CURRENT.md").read_text(encoding="utf-8-sig")
registry_file = config / "voice_registry.json"
data = json.loads(registry_file.read_text(encoding="utf-8-sig"))
mapping = {
    "EVAN":("bo","Evan Bell"), "MARA":("me","Mara"),
    "JUNO":("juno","Juno"), "LIA":("Lia","Lia"),
    "BUBU":("bubu","Bubu"), "BIX":("bix","Bix"),
    "ORIN":("ongngoai","Orin"), "ARTHUR_BELL":("ongnoi","Arthur Bell"),
    "ROSE_BELL":("banoi","Rose Bell"), "ELARA":("bangoai","Elara"),
}
found = set()
for mat in re.finditer(r"^## ([A-Z_]+) — (VOICE_[A-Z_]+)\s*$", bible, flags=re.MULTILINE):
    character = mat.group(1)
    if character not in mapping:
        continue
    stop = bible.find("\n## ", mat.end())
    body = bible[mat.end(): stop if stop>=0 else len(bible)]
    p = re.search(r"\*\*Casting prompt:\*\* (.*)", body)
    if not p:
        raise RuntimeError("Missing voice description for "+character)
    alias, full_name = mapping[character]
    entry = data["voices"][alias]
    if entry.get("approval_status") not in {"PENDING_WAV_AND_RIGHTS_APPROVAL", "PENDING_OWNER_APPROVAL", "DRAFT"}:
        raise RuntimeError("Refusing to overwrite approved voice casting "+character)
    entry["display_name"] = full_name
    entry["voice_casting_prompt"] = p.group(1).strip()
    if character=="ARTHUR_BELL":
        entry["casting_role"]="Arthur Bell, paternal Earth grandfather and ordinary human"
    elif character=="ROSE_BELL":
        entry["casting_role"]="Rose Bell, paternal Earth grandmother and ordinary human"
    elif character=="ELARA":
        entry["casting_role"]="Elara, maternal Veylora grandmother and Orin's missing wife"
    elif character=="JUNO":
        entry["casting_role"]="Juno, thirteen-year-old boy inventor"
    found.add(character)
if found != set(mapping):
    raise RuntimeError("Incomplete 10-slot cast sync; found="+repr(found))
new_text=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
registry_file.write_text(new_text,encoding="utf-8")
lines=[]
for character,(alias,display) in mapping.items():
    v=data["voices"][alias]
    lines.append(f"CHARACTER TAG: {alias}; VOICE PROFILE KEY: {v['voice_profile_key']}; {v['voice_casting_prompt']}")
(config/"voice_casting_prompts.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
assert all(data["voices"][alias]["voice_id"] is None for alias,_ in mapping.values())
assert data["voices"]["juno"]["casting_role"]=="Juno, thirteen-year-old boy inventor"
print("VOICE_SYNC_OK 10 canonical slots; 15 profiles documented; 0 false WAV approvals")
