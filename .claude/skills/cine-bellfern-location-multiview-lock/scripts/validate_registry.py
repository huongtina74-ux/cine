#!/usr/bin/env python3
"""Static review gate for the proposed CINE Bellfern location/prop skill.

No network, no model calls, no image generation. All approvals must have evidence.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json"
VIEWS_LOCATION = {
    "MASTER_WIDE", "FORWARD", "REVERSE_TRUE", "LEFT_3_4",
    "RIGHT_3_4", "DETAIL_ANCHORS", "PLAN_TOP",
}
VIEWS_PROP = {
    "FRONT", "THREE_QUARTER_LEFT", "SIDE_RIGHT", "BACK",
    "TOP", "MACRO_DETAIL", "PLACED_IN_SCENE",
}

def read_csv(filename: str) -> list[dict]:
    with (ROOT / "registry" / filename).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)

def validate() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    sites, spaces, props = data["sites"], data["spaces"], data["props"]
    check((len(sites), len(spaces), len(props)) == (12, 69, 108),
          "Expected 12 sites, 69 spaces and 108 props")
    site_ids = {s["site_id"] for s in sites}
    space_ids = {s["space_id"] for s in spaces}
    prop_ids = {p["prop_id"] for p in props}
    check((len(site_ids), len(space_ids), len(prop_ids)) == (12, 69, 108),
          "Duplicate site/space/prop ID")
    check(all(s["site_id"] in site_ids for s in spaces), "Unknown site for room")
    check(all(p["site_id"] in site_ids for p in props), "Unknown site for prop")
    loc = read_csv("LOCATION_MULTIVIEW_MANIFEST.csv")
    pro = read_csv("PROP_MULTIVIEW_MANIFEST.csv")
    check((len(loc), len(pro)) == (483, 756), "Manifest coverage mismatch")
    for rows, key, ids, views, label in [
        (loc, "space_id", space_ids, VIEWS_LOCATION, "room"),
        (pro, "prop_id", prop_ids, VIEWS_PROP, "prop"),
    ]:
        check(len({r["plate_id"] for r in rows}) == len(rows),
              f"Duplicate {label} plate ID")
        counts = Counter(r[key] for r in rows)
        check(set(counts) == ids and all(count == 7 for count in counts.values()),
              f"Expected seven plates for each {label}")
        for k in ids:
            check({r["view"] for r in rows if r[key] == k} == views,
                  f"Missing/duplicate {label} view: {k}")
        for row in rows:
            status = row["approval_status"]
            check(status in ("PENDING_NOT_GENERATED", "PENDING_REVIEW",
                             "NON_CANON_PREVIS", "APPROVED_FOR_PRODUCTION"),
                  f"Unsupported approval status: {status}")
            if status == "APPROVED_FOR_PRODUCTION":
                check(bool(row["image_file"] and row["image_sha256"] and row["human_approved"] == "YES"),
                      "Unsubstantiated approved image!")
                if label == "room":
                    check(bool(row["camera_anchor_id"] and
                               row["camera_anchor_id"] != "UNSET_PENDING_PLAN" and
                               row["geometry_verified"] == "YES" and
                               row["d55_review"] == "YES"),
                          "Unverified room geometry / lighting")
                else:
                    check(row["scale_verified"] == "YES" and row["d55_review"] == "YES",
                          "Unverified prop size / lighting")
    approved = sum(r["approval_status"] == "APPROVED_FOR_PRODUCTION" for r in loc + pro)
    print(f"PASS: 12 sites, 69 rooms, 108 props, {len(loc)+len(pro)} view slots")
    print(f"APPROVED_FOR_PRODUCTION with evidence: {approved}/{len(loc)+len(pro)}")

if __name__ == "__main__":
    validate()
