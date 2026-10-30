# CINE Bell & Leaf - 11 other Location Packs: phase-one rollout plan

**Location Lock source:** `cine-bellfern-location-multiview-lock/SKILL.md`; existing registry, manifests and `WORKFLOW_18_STAGES.md`. **Draft only**. No planned images/locations/assets have been marked approved. Bell House `BELL` is managed by `BELL_HOUSE_PHASE1_MASTER_DRAFT.md`.

## All remaining site coverage

| Site | Location | Spaces | Seven-view room slots | Props | Seven-view prop slots | State |
|---|---|---:|---:|---:|---:|---|
| `ORIN` | Orin’s Hill House | 8 | 56 | 15 | 105 | PENDING_NOT_GENERATED |
| `ROSE` | The Rose Cottage — nhà ông bà nội | 7 | 49 | 9 | 63 | PENDING_NOT_GENERATED |
| `SCHOOL` | Bellfern Community School | 12 | 84 | 15 | 105 | PENDING_NOT_GENERATED |
| `SQUARE` | Bellfern Town Square | 4 | 28 | 4 | 28 | PENDING_NOT_GENERATED |
| `POST` | Bellfern Post Office | 3 | 21 | 5 | 35 | PENDING_NOT_GENERATED |
| `LIBRARY` | Bellfern Old Library & Archives | 4 | 28 | 4 | 28 | PENDING_NOT_GENERATED |
| `BRIDGE` | Silverbrook Bridge & Riverside | 2 | 14 | 2 | 14 | PENDING_NOT_GENERATED |
| `FOREST` | Whisperwood Forest | 3 | 21 | 4 | 28 | PENDING_NOT_GENERATED |
| `BAKERY` | The Little Oven Bakery | 2 | 14 | 3 | 21 | PENDING_NOT_GENERATED |
| `STATION` | Bellfern Railway Station | 3 | 21 | 3 | 21 | PENDING_NOT_GENERATED |
| `LAKE` | Bellfern Lake & Old Boathouse | 3 | 21 | 5 | 35 | PENDING_NOT_GENERATED |
| **TOTAL** | **11 other locations** | **51** | **357** | **69** | **483** | **840 slots pending** |

The CINE all-series inventory therefore remains 12 sites / 69 spaces / 108 props / 483 room-view + 756 prop-view slots = 1,239 planned slots. All slots remain pending until inspected original files and human approvals exist.

## Production sequence

1. **ORIN - Orin's Hill House:** small gray-stone 2-storey hillside cottage with compact round observatory; interior study, archive, precision lab and **separate personal travel bell** in secure cabinet. No false magical portals. Do not invent missing grandmother's appearance.
2. **ROSE - Grandparents' Rose Cottage:** a modest one-and-a-half-storey ordinary Earth home, sage door, low fence, small rose garden. `ongnoi` and `banoi` are Evan's ordinary parents; no publicly visible magic.
3. **SCHOOL - Bellfern Community School:** public Earth school with two wings and a modest clock tower; 11-year-old Lia in separate younger wing, 13-year-old Juno in older wing. No fantasy academy.
4. **SQUARE:** low single circular fountain and civic clock consistently placed; normal human-scale plaza.
5. **POST:** ordinary post office, blue door, public counter, back sorting space and Evan's real bicycle.
6. **LIBRARY:** old ordinary municipal library with restricted paper archives, no flying books.
7. **BRIDGE:** one stone arch, one willow, stable direction of the brook and reversible real camera geography.
8. **FOREST:** old oak with bent roots and **three** permanent mossy stone markers at the fork.
9. **BAKERY:** blue-gray awning, pastry counter on right from public entrance, two cafe tables left.
10. **STATION:** real old station, small two-car train, one platform and consistently positioned rail track.
11. **LAKE:** one simple silver-gray boathouse, I-shaped wooden dock and a single wooden rowboat.

## Must-have for every site

- A proposed, plausible physical map (north/up convention) showing entrances, exits, room/fixed-anchor relationships, camera view directions, scale estimates explicitly identified as unverified.
- **One independent 16:9 full-frame image per view**, never contact-sheet, 9-panel storyboard or annotated poster: `MASTER_WIDE`, `FORWARD`, `REVERSE_TRUE`, `LEFT_3_4`, `RIGHT_3_4`, `DETAIL_ANCHORS`, `PLAN_TOP`. Reverse must be from a real opposite camera location, never mirrored.
- For each recurring asset, one frame per `FRONT`, `THREE_QUARTER_LEFT`, `SIDE_RIGHT`, `BACK`, `TOP`, `MACRO_DETAIL`, `PLACED_IN_SCENE`. When the asset is a complex location-sized element, the view naming may need scale-specific QA.
- Neutral D55 reference daylight / 5500K where appropriate, no yellow/orange global cast; natural skin and material colors. Physically motivated localized lights are allowed in night/interior scenes. Use 35-50mm or 50mm baseline with sufficiently deep DoF to show geometry, not forced f/1.8 blur.
- **Location plate is created with NO family characters.** For story shots use exact approved character refs only when visible, independent of location pack refs. Never add global 10 character tag text to every image prompt.
- No embedded subtitle/labels/text, border, watermark, added magic, hallucinated props or random unknown faces. 
- Per-view manifest requires original image file path, native dimensions, SHA-256, camera-view/anchor, geometry and D55 checks, human reviewer and review timestamp. Technical API success != visual/canon approval.

## Live-generation procedure (one image at a time)

Start with only the **exterior first master angle** of each relevant site. Generate once, manually review and fix that identity before asking for six additional views or entire 840-plate jobs. Do not automatically spend credits on all plates. Every generated reference starts `NON_CANON_PREVIS`; promote only after human evidence. No network generation or rendering is claimed by this planning document.

**Prompt import contract:** one complete English prompt on exactly one physical line, exactly one empty line between prompts; use `site_id`, `space_id` and `plate_id` in the corresponding structured manifest rather than relying on guessy regex.

## Implementation handoff

The standalone per-location TXT, PDF and CSV manifests are produced as a downloadable CINE artifact package in ChatGPT. The repository's existing `CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json`, `LOCATION_MULTIVIEW_MANIFEST.csv` and `PROP_MULTIVIEW_MANIFEST.csv` remain the **single source of truth**; do not duplicate them or mutate their approval flags while files are still absent. Integrate this rollout via a reviewed PR before the Windows machine pulls it.
