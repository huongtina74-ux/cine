---
name: cine-bellfern-location-multiview-lock
version: "1.2.0-proposed"
description: "MANDATORY CINE Bell & Leaf location/prop multi-angle identity and camera topology lock for image generation, Muse I2V 10s, character canon, lighting and production QA."
status: "INSTALLED IN GITHUB MAIN — LOCATION IMAGES NOT CANON-APPROVED"
---

# CINE / Bellfern — Location Identity & Multi-Angle Reference Skill

## Trigger
Use before ANY generated image, storyboard, image-to-video Muse clip, camera reverse, spatially repeated set, or hero prop for Bell & Leaf / Bellfern. This skill extends, but never overrides, `CINE_Bell_Leaf_Visual_Canon_v1.3_QA_Locked/SKILL.md`, character identity, approved script, and voice-lock rules.

## Invariants (non-negotiable)
- Story precedence: user-approved canon + locked screenplay > approved character ref > APPROVED location/prop pack > proposed design > loose AI concept. An AI concept is NEVER a `LOCKED` source by itself.
- Bellfern school is a REGULAR EARTH PUBLIC SCHOOL, normal teaching equipment, no Hogwarts or open magic. Juno 13 and Lia 11 study in different rooms/wings. Grandparents/Evan are ordinary humans and do not know witchcraft.
- Bell & Leaf: home main 2-storey, inherited/renovated, visible magic predominantly in secret Mara workshop/chamber. One home bell, Orin's separate personal travel bell, Bubu's collar bell; never add bell to Bix.
- Architecture physically stable: rooms, entry doors, windows, stairs, fixed props, road and garden geography must not move. TRUE REVERSE needs a different actual camera position, NEVER a horizontal mirror of a first frame.
- Colour: neutral D55 5500K photographic color science. White remains neutral white, no yellow/orange, sepia or teal-orange LUT. Natural green foliage and sky. No fake warm haze. For dark/night scenes, LOCAL practical fixtures allowed but retain neutral reference textures and no global cast.
- Lens: 50mm FF baseline, f/1.8 aesthetic only when architecture/face detail stays in focus. Group or room geometry often demands f/2.8–f/5.6 or greater equivalent DoF. Main spatial anchors critically sharp.
- Composition: native full-frame 16:9, NO border/blurred side panel/collage/contact sheet/text overlays. One independent asset for every angle.
- Design: subtle fairy-tale mystery, practical modern Earth materials, free uncluttered actor staging space, few bells/plants, one dominant focal object per room.

## Required resolvers
Resolve `site_id` and `space_id` from `registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json`. Resolve every hero prop from the same registry and its `PROP_MULTIVIEW_MANIFEST.csv`. Resolve school override via `registry/SCHOOL_EARTH_PATCH_v1_0.json`. Read `references/EXTERNAL_CONCEPT_REFERENCES.json`; a linked source is only concept, NOT an embedded image. Do NOT infer permanent geometry from one image.

## Image creation order per site
1. Verify site geography and one plan / camera coordinate sketch with north/E/W labels.
2. Establish building master front and 3/4, other exterior approach, rear/entry-to-road reverse; check window and roof count.
3. For each interior zone create independent `MASTER_WIDE`, `FORWARD`, `REVERSE_TRUE`, `LEFT_3_4`, `RIGHT_3_4`, `DETAIL_ANCHORS`, `PLAN_TOP` plates; keep camera anchors and fixed physical layout across plates.
4. For hero prop create independent `FRONT`, `THREE_QUARTER_LEFT`, `SIDE_RIGHT`, `BACK`, `TOP`, `MACRO_DETAIL`, `PLACED_IN_SCENE`; establish absolute size against approved character or scale bar after physical plausibility validation.
5. Human reviewer MUST approve topology, room adjacency, relative scale, color, prop faces and every camera angle. Record SHA-256, image path, date/reviewer and state. No fake PASS with missing image evidence.

## Muse 10-second image-to-video use
Inputs: `episode_id`, `script_lock_id`, `shot_id`, `site_id`, `space_id`, `approved_angle_id`, `approved_image_file`, image SHA-256, `camera_anchor_id`, `prop_ids`, `prop_state_ids`, `character_ref_ids`, `voice_WAV_master_ids`, exact spoken A2 line, SFX/ambience beds, original image resolution, lens and color intent.
- Gate failure if any referenced location is unapproved. Development previews must carry `NON_CANON_PREVIS` and never be silently sent as finals.
- One continuous 10.00s take. Animate characters, face, hand and believable material motion; no fake camera-only zoom substituting for performance. No morphing furniture or spawning windows, extra bells, plants, people, text.
- For voiced clips: generate speech externally with the voice-locked cast master and align/lip-sync. Do NOT ask Muse to invent new speech timbres across clips. No general narrator unless approved in screenplay.
- Video staging template: `templates/MUSE_I2V_10S_SHOT_CONTRACT.md`.

## QA and rejection
`qa/ALL_ANGLE_QA_GATE_PENDING.csv` is a production checklist (initially ALL PENDING). Review: true 16:9 independent high-resolution image, D55 neutral, architecture left/right consistency, invariant props and geometry, correct speaker timbre, no global warming filter, no merged 2x2 grid, approved actor identity, exact 10s clip duration and readable A2 speech. Fail closed on missing evidence.

## Naming conventions
- Immutable ID `SC-LIA` remains same across episodes; camera variants use `SC-LIA__FORWARD.png` etc.
- Proposed v1.1 cannot overwrite an approved v1.0 asset. Approved file is immutable; changes create new version and require new review.
- Recommended file tree `/Locations/<site_id>/<space_id>/plates/<plate_id>.png` and `/Props/<prop_id>/plates/<prop_id>__<view>.png`.

## Current factual completion
12 sites and 69 rooms/areas and 108 registered props are enumerated. 483 room view-slots and 756 prop view-slots exist ONLY as planned records, not complete photography. The links to Adobe generated concept images are stored but not downloaded/embedded. Four new supplementary concept angles are included as URLs. All room and prop approvals remain `PENDING` until actual assets and geometric check. This skill package is NOT yet installed in any CineFactory Windows repository.

## v1.2 persistence and angle-to-light contract (2026-10-29)
- This repository skill is an **instruction/registry integration**, not proof that any Adobe/AI image was downloaded, geometry-locked, or approved. Keep all unverified plates at PENDING.
- For every requested shot, resolve the stable `site_id`, `space_id`, `view_id`, `camera_anchor_id`, `sun_direction_world`, `lighting_profile_id`, `time_of_day`, and `source_image_sha256`. Fail closed if one required identifier or approved source image is missing.
- Each venue has an explicit physical local-coordinate system (X east, Y north, Z up as a PROPOSED convention until site survey), entrance/exit adjacency, registered fixed objects and semantic front/reverse meanings. Do not move walls/doors/windows/furniture to improve an isolated composition.
- Seven separate native-resolution plates per room: MASTER_WIDE, FORWARD, REVERSE_TRUE, LEFT_3_4, RIGHT_3_4, DETAIL_ANCHORS, PLAN_TOP. TRUE REVERSE is a new physically placed camera, not a horizontally flipped bitmap. Top plan may be schematic rather than CGI but must maintain coordinates.
- For lighting consistency use reference D55 neutral calibration for daylight; lock exposure intent, practical sources, key/fill ratio intent, world-space sun direction and neutral cards across multi-angle views. A new camera angle does NOT relocate the sun. Night may have physically motivated practical warmth, without applying a global warm grade. NO yellow/orange cinematic LUT.
- Camera baseline 50mm equivalent, restrained DoF. Shift f/2.8-f/5.6 for multi-character/group or architectural coverage as required for clear anchored geometry; no false f/1.8 obsession.
- Approval record: approved source file path, SHA-256, reviewer, UTC review timestamp, checked floorplan, view-to-view anchor match, D55 QC, original image pixel dimensions, and status. Do not mark APPROVED without an actual inspected full-resolution reference.
- Muse fixed 10.00 seconds, one continuous take, original reference first-frame + pre-defined end frame when supported, actor animation and real lip sync using externally locked voice WAV. Camera-only zoom does not satisfy action. Check at least start/middle/end frames, dialogue and original props.
- Generated storyboard/collage/infographic/mockup is NOT a production camera plate; scenic image must be one clean independent 16:9 plate. Any concept contradicting Bell & Leaf (e.g., resort/villa/pool or excessive amber tint) must be rejected, never stored as approved location.
- Before generating, consult `registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json` for 12 site/69 space/108 prop IDs, `registry/LOCATION_MULTIVIEW_MANIFEST.csv` and `registry/PROP_MULTIVIEW_MANIFEST.csv` for outstanding plates, and `templates/MUSE_I2V_10S_SHOT_CONTRACT.md` for shot schema.
- This skill is available in the repository main branch. It will reach the Windows machine only after a successful git pull/deployment; presence in GitHub is not proof of runtime installation.
