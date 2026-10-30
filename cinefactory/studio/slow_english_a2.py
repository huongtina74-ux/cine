"""Production-safe Slow English A2/Bell & Leaf canonical reference resolver.

Uses the existing CINE character and location registries; no invented approval,
media ID or new project directory. All evidence gates fail closed.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

PROFILE = "config/niches/slow_english_a2/production.json"

class CanonError(ValueError):
    pass

def _read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def _csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def _verify(base, rel, expected):
    if not rel or not expected:
        return None
    base = base.resolve()
    file = (base / rel).resolve()
    if not file.is_relative_to(base) or not file.is_file():
        return None
    h = hashlib.sha256(file.read_bytes()).hexdigest()
    return file if h == expected.lower() else None

def _approved(row, prop=False):
    fields = ("human_approved","scale_verified","d55_review") if prop else ("human_approved","geometry_verified","d55_review")
    return row.get("approval_status") == "APPROVED" and all(
        str(row.get(k,"")).upper() in ("YES","TRUE","PASS") for k in fields
    )

class BellLeafCanon:
    def __init__(self, repo_root):
        self.root = Path(repo_root).resolve()
        self.profile = _read(self.root / PROFILE)
        self.paths = self.profile["source_registries"]
        self.locations = _read(self.root / self.paths["sites"])
        self.characters = _read(self.root / self.paths["characters"])
        self.rooms = _csv(self.root / self.paths["room_views"])
        self.props = _csv(self.root / self.paths["prop_views"])
        self.voices = _read(self.root / self.paths["voices"])["voices"]

    def inventory(self):
        return {
            "sites":len(self.locations["sites"]),
            "spaces":len(self.locations["spaces"]),
            "props":len(self.locations["props"]),
            "room_slots":len(self.rooms),
            "prop_slots":len(self.props),
            "approved_room_metadata":sum(_approved(x) for x in self.rooms),
            "approved_prop_metadata":sum(_approved(x, True) for x in self.props),
            "character_originals":len(self.characters["characters"]),
        }

    def resolve_shot(self, shot):
        tags = shot.get("activeCharacterTags")
        if not isinstance(tags,list) or any(t not in self.profile["active_tags"] for t in tags) or len(tags)!=len(set(tags)):
            raise CanonError("activeCharacterTags must be a unique exact known-tag list")
        if shot.get("duration_seconds") != 10:
            raise CanonError("Bell & Leaf shot must be exactly 10s")
        site,space,view = [shot.get(k) for k in ("location_id","space_id","location_view_id")]
        if site not in {s["site_id"] for s in self.locations["sites"]}:
            raise CanonError("Unknown site; approve a new world location pack first")
        if space not in {s["space_id"] for s in self.locations["spaces"] if s["site_id"]==site}:
            raise CanonError("Space does not belong to site")
        room = [r for r in self.rooms if (r["site_id"],r["space_id"],r["view"])==(site,space,view)]
        if len(room)!=1:
            raise CanonError("Unknown or ambiguous physical camera view")
        blockers=[];char_refs=[];location_refs=[];prop_refs=[];voice_refs=[]
        source_root=self.root/self.paths["physical_character_files"]
        for tag in tags:
            c=self.characters["characters"][tag]
            source=[c["locked_identity_original"]]
            if tag=="bubu":
                source+=c.get("mandatory_visual_cues",[])
                if len(source)<3: blockers.append("BUBU_SPARKLING_SPIRAL_TAIL_SOURCE_MISSING")
            for ref in source:
                rel=ref.get("path") or ref.get("file")
                path=_verify(source_root,rel,ref.get("sha256"))
                if path is None: blockers.append("CHARACTER_SOURCE_MISSING_OR_CHANGED:"+tag)
                else: char_refs.append({"tag":tag,"path":str(path),"sha256":ref["sha256"],"provider_media_id":None,"scope":"ORIGINAL_IDENTITY_ONLY"})
        r=room[0]
        if not _approved(r):
            blockers.append("LOCATION_VIEW_NOT_APPROVED:"+r["plate_id"])
        else:
            p=_verify(self.root,r.get("image_file"),r.get("image_sha256"))
            if p is None: blockers.append("LOCATION_VIEW_MISSING_OR_CHANGED:"+r["plate_id"])
            else: location_refs.append({"plate_id":r["plate_id"],"path":str(p)})
        propids=shot.get("activePropIds",[])
        if not isinstance(propids,list) or len(propids)!=len(set(propids)):
            raise CanonError("activePropIds must be a unique list")
        for pid in propids:
            matches=[p for p in self.props if p["prop_id"]==pid and p["site_id"]==site and (p.get("space_id") or p.get("default_space_id"))==space]
            approved=[p for p in matches if _approved(p,True)]
            if not approved: blockers.append("PROP_NOT_APPROVED:"+str(pid));continue
            r=approved[0];p=_verify(self.root,r.get("image_file"),r.get("image_sha256"))
            if p is None: blockers.append("PROP_MISSING_OR_CHANGED:"+str(pid))
            else: prop_refs.append({"prop_id":pid,"path":str(p)})
        dialogue=shot.get("dialogue",[])
        if not isinstance(dialogue,list): raise CanonError("dialogue must be a list")
        for line in dialogue:
            tag=line.get("speaker_tag")
            if tag not in tags: raise CanonError("Speaker must be present in activeCharacterTags")
            voice=self.voices.get(tag,{})
            if voice.get("approval_status")!="APPROVED":
                blockers.append("VOICE_WAV_NOT_APPROVED:"+tag);continue
            p=_verify(self.root,voice.get("sample_wav"),voice.get("sample_sha256"))
            if p is None: blockers.append("VOICE_WAV_MISSING_OR_CHANGED:"+tag)
            else: voice_refs.append({"tag":tag,"wav":str(p),"voice_id":voice.get("voice_id")})
        return {
            "project_id":self.profile["project_id"],"shot_id":shot.get("shot_id"),"duration_seconds":10,
            "activeCharacterTags":tags,"character_refs":char_refs,"location_refs":location_refs,"prop_refs":prop_refs,"voice_refs":voice_refs,
            "blockers":sorted(set(blockers)),"provider_media_ids":[],
            "status":"BLOCKED_FOR_PRODUCTION" if blockers else "REFERENCES_VERIFIED_UPLOAD_TO_PROVIDER_REQUIRED",
            "muse_i2v_real_10s_verified":False
        }

    def flow_prompt(self,shot):
        r=self.resolve_shot(shot)
        action=" ".join(str(shot.get("action","")).split())
        cam=" ".join(str(shot.get("camera","medium cinematic shot")).split())
        tags=", ".join(r["activeCharacterTags"]) or "none"
        return (f"Bell & Leaf source-anchored original cinematic CGI, SHOT {r['shot_id']}; "
                f"ACTIVE TAGS FOR THIS SHOT: {tags}; site {shot['location_id']}, space {shot['space_id']}, view {shot['location_view_id']}; "
                f"action {action}; camera {cam}; exact character face/age/height and building topology from attached approved references; "
                "one standalone native full-bleed 16:9 image; refined realistic CGI materials, natural neutral D55 ~5500K, "
                "no global yellow/orange cast, no collage, lettering, watermark, titles or subtitles; "
                "Bubu has sparkling spiraling purple tail and ONE collar bell; Bix has NO bell.")
