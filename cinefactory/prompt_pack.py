"""Picture prompts built from the visual bible, and the prompt pack the owner uses in Gemini / Flow.

Rules come from docs/CINE_STUDIO_OS.md §4 (and the provider guidance summarised there): every
character is described by the SAME canonical sentence every time; prompts say what should be
there (positive phrasing); reference images are one character each on a plain background; at most
two main characters per picture. The pack tells the owner exactly which file name to save.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
MIN_WIDTH = 1280
ASPECT_RANGE = (1.6, 1.9)  # ~16:9
BODY_PARTS = {"face", "hand", "hands", "nose", "eyes", "eye", "head", "arm", "arms", "shoulder", "shoulders", "feet",
              "foot", "ears", "ear", "tail", "paw", "paws", "back", "smile", "tears"}


def load_niche_yaml(niche: str, root: Path | None = None) -> dict:
    path = Path(root or ROOT) / "config" / "niches" / niche / "niche.yaml"
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}


def load_bible(niche: str, root: Path | None = None) -> dict:
    """The niche visual bible; its direction block is completed from the genre playbook
    (config/direction/playbooks.yaml) so every prompt carries the playbook's look notes."""
    path = Path(root or ROOT) / "config" / "niches" / niche / "visual_bible.yaml"
    bible = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}
    if niche == "slow_english_a2":
        from cinefactory.slow_english_unified import audit
        report = audit(Path(root or ROOT))
        if report["logic_consistency"] != "PASS":
            raise ValueError("Bell & Leaf active visual Canon mismatch: " + ", ".join(report["profile_failures"]))
    d = bible.get("direction")
    if isinstance(d, dict) and d.get("playbook") and not d.get("prompt_notes"):
        books = Path(root or ROOT) / "config" / "direction" / "playbooks.yaml"
        if books.is_file():
            book = (yaml.safe_load(books.read_text(encoding="utf-8")) or {}).get(d["playbook"]) or {}
            if book.get("prompt_notes"):
                bible["direction"] = {**d, "prompt_notes": book["prompt_notes"]}
    return bible


def bible_characters(bible: dict) -> dict[str, dict]:
    return {c["id"]: c for c in bible.get("characters") or [] if c.get("id")}


def picture_cast(bible: dict, script: dict, scene: dict, prompt: str, limit: int = 2, who: list | None = None) -> list[str]:
    """Who is really in THIS picture: characters whose name or alias the picture prompt mentions, in the
    order they are mentioned (max `limit`). Describing people who are not in the shot makes the image
    model add them, so a scene's cast is only the candidate list. Scripts without aliases keep the old
    behaviour (the scene's first characters)."""
    if who is not None:
        return list(who)[:limit]
    chars = bible_characters(bible)
    legacy = script.get("characters") or {}
    cands = list(dict.fromkeys(list(scene.get("characters") or []) + list(chars)
                               + [c for c, v in legacy.items() if v.get("guest")]))
    text = " " + prompt.lower() + " "
    hits, any_alias = [], False
    for cid in cands:
        info = {**legacy.get(cid, {}), **chars.get(cid, {})}
        names = [cid, str(info.get("name", "")).split(" ")[-1]] + list(info.get("aliases") or [])
        any_alias = any_alias or bool(info.get("aliases"))
        pos = []
        for n in (x.lower() for x in names if x):
            i = text.find(f" {n}")
            while i >= 0:  # "the guard's cap" is an object, not the guard; "the girl's face" is the girl
                after = text[i + 1 + len(n):]
                if not after.startswith("'s") or after[2:].lstrip().split(" ")[0].strip(",.") in BODY_PARTS:
                    pos.append(i)
                    break
                i = text.find(f" {n}", i + 1)
        if pos:
            hits.append((min(pos), cid))
    if not any_alias:
        return list((scene.get("characters") or [])[:limit])
    return [cid for _, cid in sorted(hits)][:limit]


def picture_prompt(bible: dict, script: dict, scene: dict, prompt: str, who: list | None = None) -> str:
    """One prompt: action of the line, who is in it (canonical sentences), place, style, light, camera."""
    chars = bible_characters(bible)
    legacy = script.get("characters") or {}
    described = []
    for cid in picture_cast(bible, script, scene, prompt, who=who):
        if cid in chars and chars[cid].get("canonical"):
            described.append(chars[cid]["canonical"])
        elif cid in legacy and legacy[cid].get("description"):
            described.append(f"{legacy[cid].get('name', cid)}, {legacy[cid]['description']}")
    cam = (bible.get("camera") or {})
    parts = [
        prompt[0].upper() + prompt[1:] if prompt else "",
        ". ".join(described),
        f"Setting: {scene.get('setting', '')}" if scene.get("setting") else "",
        bible.get("style") or script.get("style", ""),
        bible.get("lighting", ""),
        "Camera at eye level, characters' faces clearly visible" if "eye-level" in " ".join(cam.get("heights") or []) else "",
        "Wide 16:9 composition with clean empty space at the bottom for subtitles",
    ]
    return ". ".join(p.strip().rstrip(".") for p in parts if p and p.strip()) + "."


def motion_prompt(bible: dict, motion: str) -> str:
    """Image-to-video prompt: one clear action, gentle camera, same look as the first frame."""
    cam = (bible.get("camera") or {}).get("moves") or ["slow push-in"]
    return (f"{motion[0].upper() + motion[1:]}. {cam[0].capitalize()}. Keep the characters, faces, clothes, colours and "
            f"lighting exactly as in the first frame. {bible.get('style', '')}. Smooth natural motion, 16:9.").replace("..", ".")


# ----------------------------------------------------------------------------- director's shot cards
# A shot card is the director/DP layer on top of the script: what the camera sees, how it is lit, what every
# character does and feels, how the shot moves and where it ends. The image prompt and the image-to-video prompt
# are both written from the card, so the picture and its animation tell the same beat.
SHOT_SIZES = {
    "EWS": "extreme wide establishing shot", "WS": "wide shot", "MWS": "medium wide shot, full body",
    "MS": "medium shot, framed from the waist up", "MCU": "medium close-up, framed from the chest up",
    "CU": "close-up on the face", "ECU": "extreme close-up", "INSERT": "insert close-up of an object",
    "OTS": "over-the-shoulder shot", "POV": "point-of-view shot",
    "COWBOY": "cowboy shot, framed from mid-thigh up", "FULL": "full shot, the whole body head to shoes",
    "ELS": "extreme long shot, the subject tiny in a vast landscape",
}
DOF = {"shallow": "shallow depth of field, soft creamy bokeh background, focus on the eyes",
       "medium": "moderate depth of field, the subject sharp and the background readable",
       "deep": "deep focus, foreground and background both sharp"}
VAGUE_EMOTION = ("happy", "sad", "angry", "scared", "upset", "excited", "nervous", "worried")
FACE_WORDS = ("eye", "brow", "mouth", "lip", "smile", "jaw", "cheek", "gaze", "tear", "frown", "grin", "chin", "nose")
STATIC_POSE = ("stands", "standing", "sits", "sitting")
INTERACTION = ("holding", "holds", "grip", "touch", "lean", "lift", "press", "point", "hug", "carry", "reach", "pull",
               "push", "wave", "hand", "tap", "clutch", "lean", "rest", "throw", "scratch", "pat", "offer", "slide")

CARD_FIELDS = ("shot", "angle", "lens", "frame", "move", "anim")


def card_cast(card: dict) -> list[str]:
    return list((card.get("act") or {}).keys())


def card_problems(card: dict, scene: dict, script: dict) -> list[str]:
    """What a shot card is missing before a director would sign it off."""
    if not card:
        return ["no shot card"]
    probs = [f"no {f}" for f in CARD_FIELDS if not str(card.get(f, "")).strip()]
    if card.get("shot") and card["shot"] not in SHOT_SIZES:
        probs.append(f"unknown shot size {card['shot']}")
    for cid, acting in (card.get("act") or {}).items():
        if len(str(acting)) < 25:
            probs.append(f"{cid}: acting too thin (action + expression + gaze)")
    loc = _location(script, scene, card)
    if not loc:
        probs.append("no location from script.locations (scene or card)")
    if not (card.get("light") or scene.get("light") or loc.get("light")):
        probs.append("no lighting (card, scene or location)")
    if card.get("motion") and not all(card["motion"].get(k) for k in ("start", "action", "end")):
        probs.append("hero motion needs start, action and end")
    return probs


def _name(bible: dict, script: dict, cid: str) -> str:
    c = {**(script.get("characters") or {}).get(cid, {}), **bible_characters(bible).get(cid, {})}
    name = str(c.get("name") or cid)
    return name if name[:1].isupper() and name.lower() not in ("boy", "old lady") else f"The {name.lower()}"


def _location(script: dict, scene: dict, card: dict) -> dict:
    return (script.get("locations") or {}).get(card.get("location") or scene.get("location", ""), {})


def _describe(bible: dict, script: dict, cid: str) -> str:
    chars, legacy = bible_characters(bible), script.get("characters") or {}
    if cid in chars and chars[cid].get("canonical"):
        return chars[cid]["canonical"]
    if cid in legacy and legacy[cid].get("description"):
        return f"{legacy[cid].get('name', cid)}, {legacy[cid]['description']}"
    return ""


LADDER = ["ELS", "EWS", "WS", "FULL", "MWS", "COWBOY", "MS", "MCU", "CU", "ECU"]  # shot-size ladder for cut rules


def _wardrobe(bible: dict, script: dict, scene: dict, cid: str) -> str:
    over = (scene.get("wardrobe") or {}).get(cid)
    if over:
        return over
    return bible_characters(bible).get(cid, {}).get("wardrobe", "")


def axis_order(scene: dict) -> list[str]:
    """Scene axis as an ordered list of characters from screen-left to screen-right (180-degree line)."""
    axis = scene.get("axis") or []
    if isinstance(axis, dict):
        return [c for c in (axis.get("left"), axis.get("right")) if c]
    return list(axis)


def shot_refs(bible: dict, script: dict, scene: dict, card: dict, folder_name: str, niche: str) -> list[tuple[str, str]]:
    """Ordered reference images for this shot: each character (front; + side view for profile angles), then the
    location plate. The prompt names them by number ("reference image 2") so the model maps each one right."""
    chars, legacy = bible_characters(bible), script.get("characters") or {}
    refs: list[tuple[str, str]] = []
    angle = str(card.get("angle", "")).lower() + " " + str(card.get("frame", "")).lower()
    for cid in card_cast(card):
        if cid in chars:
            files = chars[cid].get("references") or [f"config/niches/{niche}/characters/{cid}/front.png"]
            refs.append((cid, files[0]))
            if re.search(r"\bprofile\b|\bside (view|angle|on)\b", angle) and len(files) > 2:
                refs.append((cid, files[2]))
        elif legacy.get(cid, {}).get("guest"):
            refs.append((cid, f"{folder_name}/characters/{cid}.png"))
    loc_id = card.get("location") or scene.get("location")
    if loc_id and loc_id in (script.get("locations") or {}) and not script["locations"][loc_id].get("no_plate"):
        refs.append((f"location:{loc_id}", f"{folder_name}/locations/{loc_id}.png"))
    return refs[:6]


def _default_dof(card: dict) -> str:
    if card.get("dof"):
        return card["dof"]
    return "shallow" if card.get("shot") in ("CU", "ECU", "MCU", "INSERT") else \
        "deep" if card.get("shot") in ("ELS", "EWS", "WS") else "medium"


def _frame_note(bible: dict) -> str:
    d = bible.get("direction") or {}
    aspect = d.get("aspect") or "16:9"
    shape = {"16:9": "Wide 16:9 frame", "9:16": "Vertical 9:16 frame", "1:1": "Square 1:1 frame"}.get(aspect, f"{aspect} frame")
    subs = " with clean space at the bottom for subtitles" if (bible.get("typography") or {}).get("caption_box") else ""
    return f"{shape}{subs}, no text, letters or watermarks in the image"


def shot_prompt(bible: dict, script: dict, scene: dict, card: dict, refs: list[tuple[str, str]] | None = None) -> str:
    """Image prompt from a director's shot card in S.C.E.N.E order (docs/DIRECTING_STANDARD.md):
    S subject & action (who, interaction with objects, micro-expression, identity lock with numbered references)
    C camera & composition (size, angle, lens, depth of field, framing, blocking / screen direction)
    E environment (location plate, set dressing, time)
    N narrative & lighting (beat, mood, motivated light, colour script)
    E extra tech (render style, quality, aspect, no text)."""
    loc = _location(script, scene, card)
    refs = refs if refs is not None else []
    num: dict[str, int] = {}
    for i, (key, _) in enumerate(refs):
        num.setdefault(key, i + 1)  # a character with front + side refs is named by its first image
    size = SHOT_SIZES.get(card.get("shot", ""), card.get("shot", ""))
    cast = card_cast(card)
    chars, legacy = bible_characters(bible), script.get("characters") or {}

    # S - subject & action
    acting = [f"{_name(bible, script, cid)} {txt.strip().rstrip('.')}" for cid, txt in (card.get("act") or {}).items()]
    lock = []
    for cid in cast:
        name = _name(bible, script, cid)
        ref = f" = reference image {num[cid]}" if cid in num else ""
        if cid in chars:
            c = chars[cid]
            ident = c.get("identity") or c.get("canonical", "")
            wear = _wardrobe(bible, script, scene, cid)
            hook = f"; signature detail: {c['hook']}" if c.get("hook") else ""
            lock.append(f"{name}{ref}: same face and hair ({ident}){hook}" + (f"; wearing {wear}" if wear else ""))
        elif cid in legacy:
            lock.append(f"{name}{ref}: {legacy[cid].get('description', '')}")
    scale = "; ".join(chars[c]["scale"] for c in cast if c in chars and chars[c].get("scale"))

    # C - camera & composition
    camera = f"{size[0].upper() + size[1:]}, {card.get('angle', 'eye level')}, {card.get('lens', '50mm')} lens, " \
             f"{DOF.get(_default_dof(card), _default_dof(card))}"
    framing = f"Composition: {card.get('frame', '')}" + (f"; focus: {card['focus']}" if card.get("focus") else "")
    blocking = ""
    order = [c for c in axis_order(scene) if c in cast]
    if len(order) >= 2 and not card.get("cross_axis"):
        if len(order) == 2:
            placed = f"{_name(bible, script, order[0])} on screen left, {_name(bible, script, order[1])} on screen right"
        else:
            placed = "from screen left to screen right: " + ", ".join(_name(bible, script, c) for c in order)
        blocking = f"Blocking: {placed}; keep the same sides as the rest of the scene"
    if card.get("eyeline"):
        blocking = (blocking + "; " if blocking else "Blocking: ") + f"eyeline: {card['eyeline']}"
    if card.get("screen_dir") or (scene.get("screen_direction") and card.get("moving")):
        blocking = (blocking + "; " if blocking else "") + f"movement direction on screen: {card.get('screen_dir') or scene['screen_direction']}"

    # E - environment
    loc_key = f"location:{card.get('location') or scene.get('location')}"
    env = f"Location{' (reference image ' + str(num[loc_key]) + ' for architecture, colours and light)' if loc_key in num else ''}: " \
          f"{loc.get('description', scene.get('setting', ''))}" + (f"; {card['set']}" if card.get("set") else "")

    # N - narrative & lighting
    light = card.get("light") or scene.get("light") or loc.get("light", "")
    colour = scene.get("color") or loc.get("color", "")

    # E - extra tech
    tech = bible.get("render_tech") or ""
    parts = [
        card.get("beat", ""), ". ".join(acting),
        ("Characters, identical to their reference images. " + ". ".join(lock)) if lock else "",
        f"Scale: {scale}" if scale and len(cast) >= 2 else "",
        camera, framing, blocking,
        env, f"Time: {scene['time']}" if scene.get("time") else "",
        f"Mood: {scene.get('emotion', '')}" if scene.get("emotion") else "",
        f"Lighting: {light}" + (f"; colour palette: {colour}" if colour else ""),
        f"Continuity: {card['props']}" if card.get("props") else "",
        (bible.get("direction") or {}).get("prompt_notes", ""),
        bible.get("style", ""), tech,
        "Consistent character design, expressive readable faces with clear symmetrical eyes, natural hands with five fingers",
        _frame_note(bible),
    ]
    return ". ".join(p.strip().rstrip(".") for p in parts if p and p.strip()) + "."


def video_prompt(bible: dict, script: dict, scene: dict, card: dict, seconds: float | None = None,
                 speech: list[tuple[str, str]] | None = None) -> str:
    """Image-to-video prompt (Veo/Flow 'Frames to Video', Wan, Kling...): start frame = the picture, ONE camera
    movement, a short action timeline, who speaks which line, an end pose that the next shot can start from."""
    names = ", ".join(_name(bible, script, c) for c in card_cast(card)) or "everything in the frame"
    m = card.get("motion") or {}
    action = str(m.get("action") or card.get("anim", "")).strip()
    action = action[:1].upper() + action[1:]
    talking = [(sp, txt) for sp, txt in (speech or []) if sp in card_cast(card)]
    parts = [
        f"{SHOT_SIZES.get(card.get('shot', ''), '').capitalize()}, {card.get('angle', '')}. Camera: {m.get('camera') or card.get('move', 'static')} (one movement only)",
        f"Start: exactly the first frame ({m['start']})" if m.get("start") else "Start: exactly the first frame",
        f"Over {seconds:.0f} seconds: {action}" if seconds else action,
        (" ".join(f"{_name(bible, script, sp)} says: \"{txt}\" (lips in sync, mouth moves only while speaking)."
                  for sp, txt in talking)) if talking
        else ("No one in the shot speaks; mouths stay closed" if card_cast(card) else ""),
        f"End pose: {m['end']}" if m.get("end") else "",
        f"Background: {card['bg_motion']}" if card.get("bg_motion") else "",
        f"Keep {names} identical to the first frame: same face, hair, clothes, colours, proportions and lighting",
        f"{bible.get('style', '')}, smooth natural motion",
        "No morphing, no warping, no extra people, no text or subtitles, no camera shake",
    ]
    return ". ".join(p.strip().rstrip(".") for p in parts if p and p.strip()) + "."


def direction_report(script: dict, bible: dict, pictures_fn) -> dict:
    """Script-analysis and directing rules a professional director would check before shooting.
    FAIL: scene without a script breakdown; multi-character scene without an axis (180-degree line).
    WARN: framing text that contradicts the axis, a new location that does not open wide, cuts between
    shots less than two sizes apart, speaking lines with nobody visible to say them."""
    fails, warns = [], []
    chars = bible_characters(bible)
    names = {cid: {cid, *[str(a).lower() for a in (chars.get(cid, {}).get("aliases") or [])],
                   *[str(a).lower() for a in ((script.get("characters") or {}).get(cid, {}).get("aliases") or [])],
                   str(((script.get("characters") or {}).get(cid) or chars.get(cid) or {}).get("name", cid)).lower().split(" ")[-1]}
             for cid in set(chars) | set(script.get("characters") or {})}
    small_cuts, flips, offscreen, seen, jumps, off = 0, [], 0, set(), [], []
    for scene in script.get("scenes") or []:
        an = scene.get("analysis") or {}
        missing = [k for k in ("question", "wants", "obstacle", "turn", "arc") if not an.get(k)]
        if missing and scene.get("kind") != "learning_wrap":
            fails.append(f"{scene['id']}: script breakdown missing {', '.join(missing)}")
        pics = pictures_fn(scene)
        multi = any(len(card_cast(p.get("card") or {})) >= 2 for p in pics)
        order = axis_order(scene)
        if multi and not order and scene.get("kind") != "learning_wrap":
            fails.append(f"{scene['id']}: two or more characters share shots but no axis (who is screen-left/right)")
        prev, prev_cast = None, None
        for i, pic in enumerate(pics):
            card = pic.get("card") or {}
            loc = card.get("location") or scene.get("location")
            if loc not in seen and scene.get("kind") not in ("cold_open", "learning_wrap") \
                    and card.get("shot") not in ("EWS", "WS", "MWS"):
                warns.append(f"{pic['id']}: first shot ever in {loc} is {card.get('shot')} (open wider to orient the viewer)")
            seen.add(loc)
            size, cast = card.get("shot"), sorted(card_cast(card))
            if prev in LADDER and size in LADDER and cast and cast == prev_cast \
                    and abs(LADDER.index(prev) - LADDER.index(size)) < 2:
                small_cuts += 1  # same subject, nearly the same size: reads as a jump cut
                jumps.append(pic["id"])
            prev, prev_cast = size, cast
            present = [c for c in order if c in cast]
            if len(present) >= 2 and not card.get("cross_axis"):
                frame = " " + str(card.get("frame", "")).lower()
                def side_of(cid):
                    for n in names.get(cid, set()):
                        for side in ("left", "right"):
                            if n and any(f" {n}{mid}{side}" in frame for mid in (" on the ", " on screen ", " in the ")):
                                return side
                    return None
                sides = {c: side_of(c) for c in present}
                for a in range(len(present)):
                    for b in range(a + 1, len(present)):
                        if sides[present[a]] == "right" or sides[present[b]] == "left":
                            flips.append(f"{pic['id']} ({present[a]} should be left of {present[b]})")
                            break
            speakers = {scene["lines"][j].get("speaker") for j in pic["lines"]} - {"narrator", None}
            if speakers and not (speakers & set(card_cast(card))) and card.get("shot") not in ("INSERT", "POV", "OTS") \
                    and not card.get("offscreen"):
                offscreen += 1
                off.append(pic["id"])
    vague, static = [], []
    for scene in script.get("scenes") or []:
        for pic in pictures_fn(scene):
            for cid, txt in ((pic.get("card") or {}).get("act") or {}).items():
                low = f" {str(txt).lower()} "
                if any(f" {w}" in low for w in VAGUE_EMOTION) and not any(f in low for f in FACE_WORDS):
                    vague.append(f"{pic['id']}:{cid}")
                if any(f" {w} " in low for w in STATIC_POSE) and not any(i in low for i in INTERACTION):
                    static.append(f"{pic['id']}:{cid}")
    if vague:
        warns.append(f"{len(vague)} acting note(s) name an emotion without the face that shows it (micro-expression): "
                     + ", ".join(vague[:6]))
    if static:
        warns.append(f"{len(static)} acting note(s) just stand/sit with nothing in their hands (give an interaction): "
                     + ", ".join(static[:6]))
    if flips:
        warns.append(f"{len(flips)} shot(s) break the scene axis (180-degree rule): " + ", ".join(flips[:4]))
    if small_cuts:
        warns.append(f"{small_cuts} cut(s) on the same subject less than two shot sizes apart (jump cut); change size or angle more: " + ", ".join(jumps[:8]))
    if offscreen:
        warns.append(f"{offscreen} shot(s) where the speaking character is not in the picture (fine for reactions; check): " + ", ".join(off[:8]))
    return {"fails": fails, "warnings": warns}


def model_sheet_prompts(bible: dict) -> list[dict]:
    out = []
    style = bible.get("style", "")
    for c in bible.get("characters") or []:
        if c.get("references_status") == "approved":
            continue
        for view, words in (("front", "front view, standing, arms relaxed"),
                            ("three_quarter", "three-quarter view, standing, friendly smile"),
                            ("side", "side view, standing")):
            same = "" if view == "front" else "The same character as in the attached front image, identical face, hair, colours and clothes. "
            out.append({"character": c["id"], "view": view,
                        "file": f"config/niches/{{niche}}/characters/{c['id']}/{view}.png",
                        "attach": None if view == "front" else f"config/niches/{{niche}}/characters/{c['id']}/front.png",
                        "prompt": f"{same}{c.get('canonical', c.get('name', c['id']))}. Full body, {words}. "
                                  f"Only this one character, centred, on a plain light grey background, even soft studio light. {style}."})
    return out


def write_sheets(niche: str, root: Path | None = None) -> Path:
    """Character reference sheets only (art-director, Stage 3), before any episode exists."""
    root = Path(root or ROOT)
    bible = load_bible(niche, root)
    sheets = model_sheet_prompts(bible)
    lines = [f"# Character sheets — {niche}", "",
             "Owner, in the Gemini app (Nano Banana), one NEW chat per character:",
             "1. Paste the *front* prompt; ask for a 1:1 or 3:4 image; regenerate until the face is right; save under the file name.",
             "2. In the same chat attach that front image and paste the *three_quarter* prompt, then the *side* prompt.",
             "3. Check: same face, hair, clothes and colours in all three; eyes symmetric; hands correct.",
             "4. When all characters are done, run `python tools/cf_niche.py audit " + niche + "` and tell Claude; the art-director "
             "checks them and you approve (`references_status: approved`).", ""]
    for s in sheets:
        f = s["file"].format(niche=niche)
        done = "DONE" if (root / f).is_file() else "TODO"
        att = f"attach `{s['attach'].format(niche=niche)}`" if s.get("attach") else "make this one first"
        lines += [f"## {s['character']} — {s['view']} — {done}", f"Save as `{f}` · {att}", "", "```", s["prompt"], "```", ""]
    out = root / "config" / "niches" / niche / "characters" / "SHEETS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def find_picture(folder: Path, pic_id: str) -> Path | None:
    for ext in IMAGE_EXTS:
        p = folder / "images" / f"{pic_id}{ext}"
        if p.is_file():
            return p
    return None


def check_picture(path: Path) -> str:
    """'' if usable, else the reason."""
    from PIL import Image
    try:
        with Image.open(path) as im:
            w, h = im.size
    except Exception as exc:  # noqa: BLE001
        return f"cannot open ({exc})"
    if w < MIN_WIDTH:
        return f"too small {w}x{h} (need >= {MIN_WIDTH} wide)"
    if not ASPECT_RANGE[0] <= w / h <= ASPECT_RANGE[1]:
        return f"not 16:9 ({w}x{h}); regenerate as wide 16:9"
    return ""


def normalise_png(path: Path) -> Path:
    """Owner may save .jpg/.webp; the pipeline reads <id>.png."""
    if path.suffix.lower() == ".png":
        return path
    from PIL import Image
    target = path.with_suffix(".png")
    with Image.open(path) as im:
        im.convert("RGB").save(target)
    return target


def write_pack(niche: str, script: dict, folder: Path, pictures_fn, root: Path | None = None) -> Path:
    bible = load_bible(niche, root)
    chars = bible_characters(bible)
    lines = [f"# Prompt pack — {script.get('episode_id')} — {script.get('title', '')}", "",
             "How to use (owner):",
             "1. Open the Gemini app (Nano Banana) or Flow. Start a NEW chat for each character sheet.",
             "2. Make the character sheets first (section A) and save them under the file names given. "
             "Approve them once: set `references_status: approved` in visual_bible.yaml.",
             "3. For each picture (section B): attach the reference images listed, paste the prompt, ask for a wide 16:9 image, "
             f"save it as the given file name inside `{folder.name}/images/` (.png or .jpg).",
             "4. Run RUN_<episode>.bat again. Cine checks size/shape and makes the video.", ""]
    sheets = model_sheet_prompts(bible)
    if sheets:
        lines += ["## A. Character reference sheets (one character per image)", ""]
        for s in sheets:
            att = f" — attach `{s['attach'].format(niche=niche)}`" if s.get("attach") else " — make this one first"
            lines += [f"**{s['character']} {s.get('view', '')} → `{s['file'].format(niche=niche)}`**{att}", "", "```", s["prompt"], "```", ""]
    guests = {cid: c for cid, c in (script.get("characters") or {}).items() if c.get("guest") and c.get("description")}
    if guests:
        lines += ["## A2. Guest characters of this episode (one reference each, make before the pictures)", ""]
        for cid, c in guests.items():
            f = f"characters/{cid}.png"
            done = "DONE" if (folder / f).is_file() else "TODO"
            lines += [f"**{c.get('name', cid)} — {done} → `{folder.name}/{f}`**", "", "```",
                      f"{c.get('name', cid)}, {c['description']}. Full body, front view, standing, friendly. Only this one "
                      f"character, centred, on a plain light grey background, even soft studio light. {bible.get('style', '')}.",
                      "```", ""]
    plates = {k: v for k, v in (script.get("locations") or {}).items() if not v.get("no_plate")}
    if plates:
        lines += ["## A3. Location plates (one per place, NO characters; make them before the pictures)",
                  "Every shot in that place attaches its plate, so architecture, colours and light stay the same.", ""]
        for lid, loc in plates.items():
            f = f"locations/{lid}.png"
            done = "DONE" if (folder / f).is_file() else "TODO"
            lines += [f"**{lid} — {done} → `{folder.name}/{f}`**", "", "```",
                      f"Extreme wide establishing shot, eye level, 24mm lens, empty of people in the foreground. "
                      f"{loc.get('description', '')}. Lighting: {loc.get('light', '')}"
                      + (f"; colour palette: {loc['color']}" if loc.get("color") else "")
                      + f". {bible.get('style', '')}. Wide 16:9, no text.", "```", ""]
    from cinefactory import directing  # company default: every shot is directed
    cards_required = directing.cards_required(niche, root) or bool(script.get("shot_cards_required"))
    lines += ["## B. Pictures", ""]
    for scene in script["scenes"]:
        for pic in pictures_fn(scene):
            refs = []
            for cid in picture_cast(bible, script, scene, pic["prompt"], who=pic.get("who")):
                if cid in guests:
                    refs.append(f"{folder.name}/characters/{cid}.png")
                    continue
                refs += [r for r in (chars.get(cid, {}).get("references") or [])][:1] or [f"config/niches/{niche}/characters/{cid}/front.png"]
            status = "DONE" if find_picture(folder, pic["id"]) else "TODO"
            card = pic.get("card")
            if card:
                refs = shot_refs(bible, script, scene, card, folder.name, niche)
                said = " / ".join(f"{scene['lines'][j].get('speaker', 'narrator')}: {scene['lines'][j]['text']}" for j in pic["lines"])
                attach = "; ".join(f"{i + 1}) `{path}`" for i, (_, path) in enumerate(refs)) or "(none)"
                hero = " — **HERO CLIP**" if pic.get("motion") else ""
                lines += [f"### {pic['id']} — {status} — {card.get('shot')} · {card.get('angle')} · {card.get('lens')}{hero} — save as `images/{pic['id']}.png`",
                          f"*Beat:* {card.get('beat', pic['prompt'])}  ", f"*Lines:* {said}  ",
                          f"*Attach in this order:* {attach}", "", "Image prompt:", "```",
                          shot_prompt(bible, script, scene, card, refs), "```",
                          "Animation prompt (Frames to Video, if this shot is animated):", "```",
                          video_prompt(bible, script, scene, card,
                                       speech=[(scene["lines"][j].get("speaker", "narrator"), scene["lines"][j]["text"])
                                               for j in pic["lines"]]), "```", ""]
                if pic.get("motion"):
                    clip_done = any((folder / "images" / f"{pic['id']}{e}").is_file() for e in (".mp4", ".mov", ".webm"))
                    lines += [f"**HERO CLIP — {'DONE' if clip_done else 'TODO'}** — in Flow use *Frames to Video* with "
                              f"`images/{pic['id']}.png` as the first frame, paste the animation prompt above, then save as "
                              f"`images/{pic['id']}.mp4` (by hand; no scripts).", ""]
                continue
            if cards_required:
                lines += [f"### {pic['id']} — NO SHOT CARD — director must write it",
                          "This niche requires a director's shot card for every picture "
                          "(`python tools/cf_direction.py check <script.json> --niche " + niche + "`). "
                          "No prompt is printed: a card-less prompt has no camera, acting or light and is not to be used.", ""]
                continue
            lines += [f"### {pic['id']} — {status} — save as `images/{pic['id']}.png`",
                      f"Attach: {', '.join(refs) if refs else '(no character)'}", "", "```",
                      picture_prompt(bible, script, scene, pic["prompt"], who=pic.get("who")), "```", ""]
            if pic.get("motion"):
                clip_done = any((folder / "images" / f"{pic['id']}{e}").is_file() for e in (".mp4", ".mov", ".webm"))
                lines += [f"**HERO CLIP — {'DONE' if clip_done else 'TODO'}** — in Flow use *Frames to Video* with "
                          f"`images/{pic['id']}.png` as the first frame, paste the motion prompt, then save as "
                          f"`images/{pic['id']}.mp4` (do it by hand; no scripts).", "", "```",
                          motion_prompt(bible, pic["motion"]), "```", ""]
    out = folder / "prompt_pack.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
