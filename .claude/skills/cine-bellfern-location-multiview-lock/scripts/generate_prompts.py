#!/usr/bin/env python3
"""Build import-ready one-line prompts for independent Bellfern concept plates.

Prompts are *not* approvals or rendered images. One continuous English line per
view and exactly one empty line between prompts, suitable for batch ingestion.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "registry" / "CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json").read_text(encoding="utf-8"))
OUT = ROOT / "prompts"
OUT.mkdir(exist_ok=True)

ROOM_VIEWS = {
    "MASTER_WIDE": "establish the complete spatial layout in one stable wide shot, centered on fixed anchors",
    "FORWARD": "forward camera from recorded main approach at eye level, show door/window geometry",
    "REVERSE_TRUE": "genuine 180-degree reverse camera from opposite physical position looking back to the original approach, never mirror the image",
    "LEFT_3_4": "physical three-quarter left camera revealing depth and unchanged wall and prop relationships",
    "RIGHT_3_4": "physical three-quarter right camera revealing depth and unchanged wall and prop relationships",
    "DETAIL_ANCHORS": "single close camera showing immutable architectural and prop recognition details",
    "PLAN_TOP": "clean orthographic overhead architectural plan showing consistent doors windows, fixed object positions and north arrow, not a collage",
}
PROP_VIEWS = {
    "FRONT": "clean front orthographic-like hero asset view",
    "THREE_QUARTER_LEFT": "three-quarter left perspective of the same physical object",
    "SIDE_RIGHT": "right-side elevation preserving shape, markings and scale",
    "BACK": "physical rear view showing same object construction, not a mirrored front",
    "TOP": "overhead top view with unchanged physical dimensions",
    "MACRO_DETAIL": "macro photograph showing genuine material and unique details",
    "PLACED_IN_SCENE": "placed within its registered space at believable scale and physical contact",
}
STYLE = ("CINE Bell and Leaf fictional family-world, high-quality stylized-real 3D CGI with photographic material "
         "fidelity; bright clean neutral D55 5500K daylight reference, white and gray must remain neutral; "
         "natural soft physically correct shadowing, no amber/yellow/orange LUT, no sepia or teal-orange, "
         "no neon bloom; tasteful restrained colors; 16:9 full-bleed single independent picture, never "
         "montage/contact sheet/grid/labels/text overlays; 50mm full-frame look with useful crisp architectural "
         "focus and restrained depth of field, f/2.8-f/5.6 when needed; no people or cast characters in "
         "empty environment master plates; no invented bells, extra plants, magical particles or clutter.")
def clean(value: object) -> str:
    return " ".join(str(value or "").split())
def one_line(value: str) -> str:
    return " ".join(value.replace("\n", " ").split())
rooms = []
for space in DATA["spaces"]:
    for view, direction in ROOM_VIEWS.items():
        rooms.append(one_line(
            f"PLATE {space['space_id']}__{view}; SITE {space['site_id']}; SPACE {clean(space['name'])}; "
            f"CAMERA {direction}; PROPOSED PLACEMENT {clean(space.get('placement'))}; "
            f"IMMUTABLE VISUAL ANCHORS {clean(space.get('fixed_visual_anchors'))}; "
            f"NEVER ALTER {clean(space.get('forbidden_change'))}; "
            f"Do not assert unverified meter coordinates or copy a reverse as a flip. {STYLE}"
        ))
props = []
for p in DATA["props"]:
    for view, direction in PROP_VIEWS.items():
        props.append(one_line(
            f"PLATE {p['prop_id']}__{view}; SITE {p['site_id']}; REGISTERED SPACE {p.get('default_space_id','')}; "
            f"PROP {clean(p['name'])}; CAMERA {direction}; "
            f"DESIGN ANCHOR {clean(p.get('design_anchor'))}; "
            f"PHYSICAL RULE {clean(p.get('immutable_rule'))}; "
            f"Keep size relative to approved actors and scene anchors until real centimeters are approved. {STYLE}"
        ))
assert len(rooms) == 483 and len(props) == 756
(OUT / "LOCATION_MULTIVIEW_IMAGE_PROMPTS_EN.txt").write_text("\n\n".join(rooms) + "\n", encoding="utf-8")
(OUT / "PROP_MULTIVIEW_IMAGE_PROMPTS_EN.txt").write_text("\n\n".join(props) + "\n", encoding="utf-8")
print(f"Generated {len(rooms)} location + {len(props)} prop prompts; ONE line per prompt, ONE blank line between.")
