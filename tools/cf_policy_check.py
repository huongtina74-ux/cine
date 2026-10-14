"""Policy check before packaging: does the metadata promise what the video delivers?

YouTube compares title, thumbnail and tags with what is said and shown in the video
(misleading metadata), and penalises tag stuffing, off-platform calls to action and
reused third-party footage. This check runs on our own files before anything is uploaded.

    python tools/cf_policy_check.py --package data/.../upload_package.json \
        --dc data/.../director_cut.json --srt data/.../edit/EP_edit.srt \
        --thumb-text "FINN WINS!" [--json report.json]

Exit: 0 PASS or WARN (read the warnings), 1 FAIL (fix before packaging), 2 bad input.
It is a first filter, not legal advice; the owner still approves every upload.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

STOP = set("""a an the and or but of to in on at for with from by is are was were be been it its this that these those
you your we our they their he she his her i me my as so if then than up down out over into about after before
how what why who when where which vs v ep episode part full new video videos official hd 4k
và của là có cho với trong những các một không được này đó thì mà khi để như từ ra vào lên""".split())
OFF_PLATFORM = ["link in bio", "telegram", "zalo", "whatsapp", "join my group", "join our group", "free money",
                "click the link", "dm me", "inbox me", "cashapp", "earn money fast", "100% free", "sub4sub"]
CLICKBAIT = ["you won't believe", "you wont believe", "shocking", "gone wrong", "not clickbait", "must watch",
             "will blow your mind", "100% real", "insane", "omg"]
KIDS_RISK = ["blood", "kill", "killed", "die", "dies", "dead", "gun", "scary", "horror", "weapon", "murder", "sexy"]
WORD = re.compile(r"[\w'’]+", re.UNICODE)


def tokens(text: str) -> list[str]:
    return [w.lower() for w in WORD.findall(text or "") if len(w) > 2 and w.lower() not in STOP and not w.isdigit()]


def load_json(path: str) -> dict:
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"BAD_INPUT::{path}: {exc}")


def srt_text(path: str) -> str:
    if not path or not Path(path).is_file():  # an edit without narration has no subtitles
        return ""
    lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    return " ".join(l for l in lines if l.strip() and not l.strip().isdigit() and "-->" not in l)


def check(package: dict, dc: dict, spoken: str, thumb: str, transcript_extra: str) -> dict:
    fails, warns, notes = [], [], []
    title = package.get("title", "")
    desc = package.get("description", "")
    tags = package.get("tags") or []
    core_title = title.split("|")[0]
    shown = []
    for shot in dc.get("shots", []):
        vo = (shot.get("vo") or {}).get("text") or ""
        txt = shot.get("onscreen_text")
        txt = txt.get("text") if isinstance(txt, dict) else (txt or "")
        shown += [vo, txt, shot.get("purpose") or "", shot.get("shot_class") or ""]
    synopsis = ((dc.get("source_episode") or {}).get("synopsis") or "")
    content = set(tokens(" ".join([spoken, transcript_extra, synopsis, *shown])))
    has_content = bool(content)

    # 1. hard limits
    if len(title) > 100:
        fails.append(f"title is {len(title)} characters (YouTube limit 100)")
    if len(desc) > 5000:
        fails.append(f"description is {len(desc)} characters (limit 5000)")
    if sum(len(t) for t in tags) + 2 * max(0, len(tags) - 1) > 500:
        fails.append("tags exceed YouTube's 500-character total")

    # 2. title promise vs content
    tw = set(tokens(core_title))
    if tw and has_content:
        missing = sorted(tw - content)
        share = len(missing) / len(tw)
        notes.append(f"title words found in the video: {len(tw) - len(missing)}/{len(tw)}")
        if share > 0.5:
            fails.append("title promises things the video does not say or show: " + ", ".join(missing))
        elif missing:
            warns.append("title words not found in VO/subtitles/on-screen text: " + ", ".join(missing))
    elif not has_content:
        warns.append("no VO, subtitles or on-screen text supplied: title/thumbnail match could not be checked")

    # 3. thumbnail text must appear in the video
    if thumb:
        miss = sorted(set(tokens(thumb)) - content) if has_content else []
        if miss:
            warns.append("thumbnail text not present in the video: " + ", ".join(miss)
                         + " (put it on screen or say it, or change the thumbnail)")

    # 4. tags: count and relevance
    if len(tags) > 15:
        warns.append(f"{len(tags)} tags; keep 5-15 relevant tags")
    meta = set(tokens(title + " " + desc)) | content
    irrelevant = [t for t in tags if not set(tokens(t)) & meta]
    if tags and len(irrelevant) / len(tags) > 0.3:
        warns.append("tags not supported by title/description/content: " + ", ".join(irrelevant))

    # 5. clickbait and off-platform calls to action
    low_title, low_all = title.lower(), (title + " " + desc + " " + spoken).lower()
    hits = [p for p in CLICKBAIT if p in low_title]
    letters = [c for c in core_title if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6 and len(letters) > 12:
        hits.append("mostly CAPITAL LETTERS")
    if hits:
        warns.append("clickbait signals in the title: " + ", ".join(hits))
    cta = [p for p in OFF_PLATFORM if p in low_all]
    if cta:
        warns.append("off-platform calls to action: " + ", ".join(cta) + " (use an on-platform question instead)")

    # 6. kids content
    if package.get("made_for_kids"):
        risky = sorted({w for w in KIDS_RISK if re.search(rf"\b{re.escape(w)}\b", low_all)})
        if risky:
            warns.append("made for kids but text contains: " + ", ".join(risky))

    # 7. AI disclosure is a conscious decision
    if "ai_disclosure_required" not in package:
        warns.append("upload_package has no ai_disclosure_required decision (realistic synthetic people/places must be disclosed)")
    elif package.get("ai_disclosure_required") and "ai" not in low_all and "synthetic" not in low_all:
        warns.append("AI disclosure is required: also say it in the description and a pinned comment")

    # 8. reused third-party footage
    for shot in dc.get("shots", []):
        if shot.get("third_party") and not shot.get("license"):
            fails.append(f"{shot.get('id')}: third-party footage without a recorded license")

    verdict = "FAIL" if fails else ("WARN" if warns else "PASS")
    return {"verdict": verdict, "fails": fails, "warnings": warns, "notes": notes}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--package", required=True, help="upload_package.json (title, description, tags, made_for_kids, ai_disclosure_required)")
    p.add_argument("--dc", default="", help="director_cut.json")
    p.add_argument("--srt", default="", help="subtitles of the final edit")
    p.add_argument("--transcript", default="", help="plain-text transcript (optional)")
    p.add_argument("--thumb-text", default="", help="words printed on the thumbnail")
    p.add_argument("--json", default="", help="write the report here")
    args = p.parse_args(argv)
    package = load_json(args.package)
    dc = load_json(args.dc)
    extra = Path(args.transcript).read_text(encoding="utf-8", errors="ignore") if args.transcript else ""
    report = check(package, dc, srt_text(args.srt), args.thumb_text, extra)
    for n in report["notes"]:
        print("NOTE::" + n)
    for w in report["warnings"]:
        print("WARN::" + w)
    for f in report["fails"]:
        print("FAIL::" + f)
    print("POLICY_" + report["verdict"])
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
