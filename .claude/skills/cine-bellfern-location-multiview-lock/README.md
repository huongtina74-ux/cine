# Bellfern Location Reference Skill — v1.2 proposed

This directory implements reference *memory and review gates* for CINE Bell & Leaf. The folder is versioned on a **feature branch**, not an approved visual master and not automatically loaded by the Windows CineFactory runtime.

## Coverage

- 12 sites, 69 spaces, 108 named props.
- 483 room plate slots, 756 prop plate slots, **all pending**.
- Muse fixed 10.00s; daylight reference D55 neutral / 5500K, no global yellow/orange tint; 50mm full-frame baseline, moderate depth-of-field; 16:9 standalone image per view.
- Every approved image must carry a path, SHA256, camera world position, geom/lighting QA evidence and human review date. Do not promote AI concepts to canon by default.

## Site registry (all provisional, not canon locked)

| ID | Site | Spaces | Props |
|---|---|---:|---:|
| `BELL` | Bell & Leaf House | 18 | 39 |
| `ORIN` | Orin’s Hill House | 8 | 15 |
| `ROSE` | The Rose Cottage — nhà ông bà nội | 7 | 9 |
| `SCHOOL` | Bellfern Community School | 12 | 15 |
| `SQUARE` | Bellfern Town Square | 4 | 4 |
| `POST` | Bellfern Post Office | 3 | 5 |
| `LIBRARY` | Bellfern Old Library & Archives | 4 | 4 |
| `BRIDGE` | Silverbrook Bridge & Riverside | 2 | 2 |
| `FOREST` | Whisperwood Forest | 3 | 4 |
| `BAKERY` | The Little Oven Bakery | 2 | 3 |
| `STATION` | Bellfern Railway Station | 3 | 3 |
| `LAKE` | Bellfern Lake & Old Boathouse | 3 | 5 |

## Files

- `SKILL.md`: mandatory stable location, topology, lighting and Muse gate.
- `registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json`: descriptive site, room and prop registry; proposed geometry only.
- `registry/LOCATION_MULTIVIEW_MANIFEST.csv`: required independent room plates, all pending.
- `registry/PROP_MULTIVIEW_MANIFEST.csv`: required independent prop plates, all pending.
- `templates/MUSE_I2V_10S_SHOT_CONTRACT.md`: 10s shot contract.
- `scripts/validate_registry.py`: deterministic registry/coverage/approval-evidence checks.

## Approval stages

1. Canon cross-check and topology survey; choose stable reference scale, axes, room/prop placement and truthful camera positions.
2. Generate an independent 16:9 native-resolution image for each angle. A single infographic/contact sheet does not count; no horizontal mirroring of reverse angles.
3. Human checks each plate for coherent doors/windows/props/sun direction and color. Record original file and SHA256, then approve the relevant row with review evidence.
4. Only then use those images as Muse source frames for individual 10.00s shots. QA checks true actor motion, preserved set geometry, voice-locked WAV and timing.

## Pending work

There is currently no trusted user-approved set of independent native-resolution view plates embedded in this repository. External concept URLs and existing reference collages cannot replace source images. Generated previews that depict unrelated villas/resorts or orange lighting must be rejected. Camera coordinates for unmeasured locations are blank intentionally rather than invented.

No content on this branch should be treated as a completed 3D survey or verified Muse render.
