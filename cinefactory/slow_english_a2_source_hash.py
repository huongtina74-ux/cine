"""Portable source-only Bell & Leaf character pixel verification.

Do not import cinefactory.studio at module import time: CI runs with minimal deps.
Require exact original PNG SHA or pinned RGBA-equivalent pixels, never fuzzy match.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

def _read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def _verify(base, rel, expected):
    if not rel or not expected:
        return None
    base=Path(base).resolve()
    path=(base/rel).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        return None
    return path if hashlib.sha256(path.read_bytes()).hexdigest()==expected.lower() else None

def _verify_character_source(base, rel, expected):
    """Accept immutable original PNG bytes, or an independently pinned RGBA match.

    Allows only exact user-approved source pixels after lossless PNG re-encoding,
    never a perceptually similar AI image or a regenerated camera angle.
    The byte SHA in the official Canon manifest is never silently replaced.
    """
    original = _verify(base, rel, expected)
    if original is not None:
        return original
    if not rel or not expected:
        return None
    base = base.resolve()
    candidate = (base / rel).resolve()
    if not candidate.is_relative_to(base) or not candidate.is_file():
        return None
    metadata = base / "metadata/LOCAL_PIXEL_EQUIVALENCE_V1_2.json"
    if not metadata.is_file():
        return None
    try:
        from PIL import Image
        from scripts.recover_bell_leaf_local_pixel_canon import (
            ORIGINAL_RGBA, MASTER_RGBA, BUBU_DETAIL_RGBA)
        manifest = _read(metadata)
        record = manifest.get("files", {}).get(rel)
        if not record or record.get("canonical_png_sha256") != expected:
            return None
        if record.get("local_png_sha256") != hashlib.sha256(candidate.read_bytes()).hexdigest():
            return None
        parts = Path(rel).parts
        if len(parts) == 3 and parts[0] == "assets" and parts[1] == "originals" and parts[2].endswith("_SOURCE_CANON.png"):
            tag = parts[2].removesuffix("_SOURCE_CANON.png")
            pinned = ORIGINAL_RGBA.get(tag)
        elif len(parts) == 3 and parts[0] == "assets" and parts[1] == "masters" and parts[2].endswith("_EXACT_SOURCE_CROP.png"):
            tag = parts[2].removesuffix("_EXACT_SOURCE_CROP.png")
            pinned = MASTER_RGBA.get(tag)
        else:
            pinned = BUBU_DETAIL_RGBA.get(rel, (None, None))[0]
        if not pinned or record.get("canonical_rgba_sha256") != pinned:
            return None
        with Image.open(candidate) as source:
            rgba_sha = hashlib.sha256(source.convert("RGBA").tobytes()).hexdigest()
        return candidate if rgba_sha == pinned else None
    except (ValueError, OSError, ImportError, KeyError, TypeError):
        return None
