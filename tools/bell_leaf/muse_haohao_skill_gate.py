#!/usr/bin/env python3
"""Static prompt + provenance preflight for existing CINE Bell & Leaf Muse/HaoHao batches.

This is NOT a Muse account-policy classifier, a voice lip-sync tool,
a face-recognition verifier, or a production release authorization.
The validated input may contain numerous HOLD rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SHOT_RE = re.compile(r"\bEP\d{3}\s+(S\d{3})\b")
DURATION_RE = re.compile(r"(?i)(?:strictly\s+)?10(?:\.0+)?\s*(?:seconds|sec|s)\b")
FPS_RE = re.compile(r"(?i)\b24\s*fps\b|\b24fps\b")
ACTIVE_RE = re.compile(r"ACTIVE TAGS FOR THIS SHOT:\s*\[([^\]]*)\]")
SPEAKER_RE = re.compile(r'^@[A-Za-z0-9_]+ \[(?:neutral|happy|sad|angry|fearful|surprised|disgusted)\]: "[^\r\n]+"$')
# These are signs of deliberate moderation-evasion instructions, NOT a "list of banned words".
EVASION_RE = re.compile(
    r"\b(?:bypass|evade|disable|circumvent)\s+(?:the\s+)?"
    r"(?:(?:content|account|platform)\s+)?(?:moderation|safety\s+filters?|restrictions)\b",
    flags=re.IGNORECASE,
)


def _read_lines(path: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    if not path.is_file():
        return [], [f"FILE_NOT_FOUND:{path}"]
    raw = path.read_text(encoding="utf-8-sig")
    text = raw.replace("\r\n", "\n")
    if "\r" in text:
        issues.append(f"UNEXPECTED_CR:{path.name}")
    if not text.endswith("\n") or text.endswith("\n\n"):
        issues.append(f"EOF_MUST_BE_SINGLE_NEWLINE:{path.name}")
    if not text.strip():
        return [], [f"EMPTY:{path.name}"] + issues
    if "\n\n\n" in text:
        issues.append(f"MULTIPLE_BLANK_SEPARATORS:{path.name}")
    chunks = text.rstrip("\n").split("\n\n")
    if any("\n" in chunk or not chunk.strip() for chunk in chunks):
        issues.append(f"NOT_EXACTLY_ONE_PHYSICAL_LINE_PER_SHOT:{path.name}")
    return chunks, issues


def _ids(chunks: list[str], name: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    ids: list[str] = []
    for index, value in enumerate(chunks, 1):
        m = SHOT_RE.search(value)
        if not m:
            issues.append(f"{name}:PROMPT_{index}:MISSING_EPISODE_SHOT_ID")
        else:
            ids.append(m.group(1))
    if len(set(ids)) != len(ids):
        issues.append(f"{name}:DUPLICATE_SHOT_IDS")
    if ids and ids != sorted(ids, key=lambda x: int(x[1:])):
        issues.append(f"{name}:SHOT_ORDER_NOT_MONOTONIC")
    return ids, issues


def audit(video_txt: Path, image_txt: Path, manifest_path: Path,
          require_queueable: bool = False) -> dict[str, Any]:
    video, errors = _read_lines(video_txt)
    image, image_errors = _read_lines(image_txt)
    errors.extend(image_errors)
    video_ids, e = _ids(video, "VIDEO")
    errors.extend(e)
    image_ids, e = _ids(image, "IMAGE")
    errors.extend(e)
    if video_ids != image_ids:
        errors.append("IMAGE_VIDEO_SHOT_ORDER_MISMATCH")
    if len(video) != len(image):
        errors.append("IMAGE_VIDEO_COUNT_MISMATCH")

    manifest = None
    if not manifest_path.is_file():
        errors.append(f"MANIFEST_MISSING:{manifest_path}")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            errors.append(f"MANIFEST_INVALID:{exc}")

    hold = 0
    pilot_only = 0
    safety_flags: list[str] = []
    if not isinstance(manifest, list) or not manifest:
        errors.append("MANIFEST_MUST_BE_NONEMPTY_LIST")
        manifest = []
    if len(manifest) != len(video):
        errors.append("MANIFEST_VIDEO_ROW_COUNT_MISMATCH")
    man_ids = [str(row.get("shot_id", "")) for row in manifest if isinstance(row, dict)]
    if man_ids != video_ids:
        errors.append("MANIFEST_SHOT_IDS_MISMATCH")

    for index, (v, im) in enumerate(zip(video, image), 1):
        sid = video_ids[index-1] if index <= len(video_ids) else f"ROW_{index}"
        if not DURATION_RE.search(v):
            errors.append(f"{sid}:NOT_STRICT_10_SECONDS")
        if not FPS_RE.search(v):
            errors.append(f"{sid}:MISSING_24FPS")
        if "16:9" not in v or "16:9" not in im:
            errors.append(f"{sid}:MISSING_16_9")
        if not ACTIVE_RE.search(v):
            errors.append(f"{sid}:MISSING_ACTIVE_TAGS")
        if EVASION_RE.search(v) or EVASION_RE.search(im):
            errors.append(f"{sid}:EXPLICIT_SAFETY_EVASION_INSTRUCTION")
        if re.search(r"(?i)\bnative\s+4k\s+(?:verified|guaranteed)\b", v):
            errors.append(f"{sid}:FALSE_NATIVE_4K_CLAIM")

    for index, row in enumerate(manifest, 1):
        if not isinstance(row, dict):
            errors.append(f"MANIFEST_ROW_{index}:NOT_OBJECT")
            continue
        sid = str(row.get("shot_id", f"ROW_{index}"))
        status = str(row.get("status", ""))
        blockers = row.get("blockers")
        speakers = row.get("voice_speakers")
        char_tags = row.get("character_tags")
        voice_lines = row.get("voice_runtime_lines")
        if not isinstance(blockers, list) or not isinstance(speakers, list) or not isinstance(char_tags, list) or not isinstance(voice_lines, list):
            errors.append(f"{sid}:INVALID_QC_MANIFEST_LISTS")
            continue
        if index > len(video) or row.get("one_line_video_prompt") != video[index - 1]:
            errors.append(f"{sid}:MANIFEST_VIDEO_PROMPT_MISMATCH")
        if index <= len(video):
            tag_match = ACTIVE_RE.search(video[index - 1])
            observed_tags = {
                part.strip().upper()
                for part in tag_match.group(1).split(",") if part.strip()
            } if tag_match else set()
            expected_tags = {str(tag).upper() for tag in char_tags}
            if observed_tags != expected_tags:
                errors.append(f"{sid}:ACTIVE_TAGS_DIFFER_FROM_VISUAL_CAST")
        if row.get("video_prompt_sha256") and row["video_prompt_sha256"] != hashlib.sha256(str(row.get("one_line_video_prompt", "")).encode("utf8")).hexdigest():
            errors.append(f"{sid}:VIDEO_PROMPT_SHA_MISMATCH")
        for line in voice_lines:
            if not SPEAKER_RE.fullmatch(str(line)):
                errors.append(f"{sid}:INVALID_HAOHAO_INTERNAL_VOICE_LINE")
        if len(speakers) > 1 and not status.startswith("HOLD"):
            errors.append(f"{sid}:MULTISPEAKER_MUST_HOLD_CURRENT_HAOHAO")
        if status.startswith("HOLD"):
            hold += 1
        elif status.startswith("PILOT"):
            pilot_only += 1
            if blockers or len(speakers) > 1:
                errors.append(f"{sid}:PILOT_WITH_UNRESOLVED_BLOCKER")
        else:
            # No arbitrary "APPROVED" accepted from existing exported text.
            errors.append(f"{sid}:UNKNOWN_OR_FALSE_APPROVAL_STATUS:{status}")
        if blockers:
            safety_flags.append(f"{sid}:UNRESOLVED_BLOCKERS:{len(blockers)}")

    if require_queueable and (hold or errors):
        errors.append(f"PRODUCTION_QUEUE_REFUSED_HOLD_ROWS:{hold}")

    return {
        "schema": "bell_leaf_muse_haohao_static_preflight_v1",
        "input_video": str(video_txt),
        "input_image": str(image_txt),
        "manifest": str(manifest_path),
        "video_count": len(video),
        "image_count": len(image),
        "manifest_count": len(manifest),
        "hold_count": hold,
        "pilot_only_count": pilot_only,
        "static_structure_pass": not bool(errors),
        "errors": errors,
        "nonfatal_review_findings": safety_flags[:20],
        "rights_review_pass": None,
        "provider_policy_review_pass": None,
        "identity_face_review_pass": None,
        "voice_lipsync_review_pass": None,
        "native_4k_proven": False,
        "production_authorized": False,
        "reason": "Static structure validation does not certify legal content, visual/audio QC or authorized production.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-txt", type=Path, required=True)
    parser.add_argument("--image-txt", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--require-queueable", action="store_true",
                        help="Refuse if any HOLD row exists; still never grants production approval.")
    args = parser.parse_args()
    report = audit(args.video_txt, args.image_txt, args.manifest, args.require_queueable)
    body = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(body, encoding="utf-8")
    print(body)
    return 0 if report["static_structure_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
