# BELL & LEAF HOUSE — LOCATION MASTER DESIGN / PHASE 1 (DRAFT)

**Site ID:** `BELL`. **Status:** `DRAFT_TOPOLOGY_AWAITING_REVIEW`. **Date:** 2026-10-29.  
**Authoritative references:** `registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json`; `registry/LOCATION_MULTIVIEW_MANIFEST.csv`; `SKILL.md`; `WORKFLOW_18_STAGES.md`.

This design contract **does not override existing canon** and is not an approval of generated images. All 126 BELL room-view plate slots remain `PENDING_NOT_GENERATED`.

## Existing canonical-vs-proposed boundary

Proposed location identity consistent with the current registry: an inherited, renovated, grounded **two-storey limestone family house** with blue-grey slate roof, centered SOUTH oak-arched main door, three easily readable aligned window clusters, restrained ivy-leaf carved relief and a small round attic window. No castle, no ornate magic tower, no invented conservatory. An ordinary **public Mara repair atelier attaches on the EAST side** and has a separate east-side entrance. Only a **locked storage room behind that workshop** leads through a hidden stair to the **single sealed home-bell chamber underground BELOW the east annex**. Do not place the chamber or atelier in the attic or ordinary family living rooms.

### Proposed site topology — North up, East right

| Level | WEST / SOUTHWEST | CENTER | EAST / NORTHEAST | NORTH / BELOW |
| --- | --- | --- | --- | --- |
| Ground | Living room (north-wall fireplace, front window) | South foyer, oak stair rising along east side | Kitchen east, dining northeast, separate atelier attached farther east | North rear garden accessed via dining |
| Upper | Parents' bedroom southwest | Landing, family bath | Juno east bedroom with workbench and Bix nook | Lia north bedroom with reading nook and Bubu pad |
| Below east atelier only | No ordinary-house cellar magic route | No shortcut from living room | Locked storage -> hidden limestone stair | Protected underground single-bell chamber |
| Exterior | Low stone path and gate south | SOUTH oak arched front door | Public workshop entrance on east side | NORTH garden with dining access |

**This is a topology/adjacency proposal, NOT a measured floorplan.** Do not invent precise physical coordinates, scale or `APPROVED` camera-anchor IDs without a reviewed source/plan.

## Phase 1: Exterior master and seven independent plates

First generate only `BH-EXT__MASTER_WIDE`. Review and choose the preferred visual identity. Then attach the actual chosen source image as a source reference when generating other views. Never perform all seven at once without a reviewed master, and never accept 3x3 image boards as individual plates.

The exact seven plate IDs are:
1. `BH-EXT__MASTER_WIDE`
2. `BH-EXT__FORWARD`
3. `BH-EXT__REVERSE_TRUE`
4. `BH-EXT__LEFT_3_4`
5. `BH-EXT__RIGHT_3_4`
6. `BH-EXT__DETAIL_ANCHORS`
7. `BH-EXT__PLAN_TOP`

The matching single-prompt-per-line Flow import file is `templates/BELL_EXT_7_FLOW_CANDIDATE_PROMPTS.txt`. Every prompt is independent and separated by exactly one empty line. Each output is ONE image in native 16:9. The `PLAN_TOP` view is an architectural reference, **not** evidence of a survey until geometry has been independently checked.

## Room packs: 18 spaces × seven views = 126 proposed BELL plates

`BH-EXT`, `BH-FOYER`, `BH-LIVING`, `BH-KITCHEN`, `BH-DINING`, `BH-POWDER`, `BH-LANDING`, `BH-PARENTS`, `BH-JUNO`, `BH-LIA`, `BH-BATH`, `BH-WORK-EXT`, `BH-ATELIER`, `BH-STORAGE`, `BH-STAIR-SECRET`, `BH-BELLCHAMBER`, `BH-REAR-GARDEN`, `BH-PATH`.

Follow the existing manifest's native seven-view contract for **each** space: `MASTER_WIDE`, `FORWARD`, `REVERSE_TRUE`, `LEFT_3_4`, `RIGHT_3_4`, `DETAIL_ANCHORS`, `PLAN_TOP`. Do not duplicate or replace the 483-location master manifest; record all approvals in that existing manifest with original image path/hash and human evidence.

### Production-wave priority

`BH-EXT`, `BH-FOYER`, `BH-KITCHEN`, `BH-DINING`, `BH-ATELIER`, `BH-BELLCHAMBER`, `BH-REAR-GARDEN` first (49 angle slots), because their geography matters for most Bell & Leaf family/secret-room shots. Remaining 11 spaces stay pending until needed.

## Image quality / location continuity acceptance

- Every plate: ONE full 16:9 image, not tiled, poster, contact sheet, caption, watermark, text, subtitles or comic.
- Approved family-feature CGI, original stylized world, real limestone/slate/oak materials, coherent scale and buildable floorplan. Do not invent live actors in empty location reference plates.
- Neutral D55 daylight reference ~5500K where sunlight is physically available; softly plausible shadows; whites/greys neutral. Underground chamber has **no daylight window** and only physically motivated neutral practicals with localized silver-gate highlights. No global amber/orange cast.
- Reverse view requires a genuinely opposite camera position, not a mirrored bitmap. Door/window/stairs/prop positions must match across view plates.
- Keep the original ordinary-world secrecy rule: Evan and paternal grandparents cannot see active magic. Public atelier looks like a practical restoration workshop.
- One home bell only in locked chamber; Orin personal travel bell is elsewhere; Bubu has collar bell; Bix no bell.
- `QC_PASS` for geometry and identity requires actual full-resolution original source, SHA-256, stated physical camera view, lighting consistency and reviewer/time; a prompt or displayed thumbnail is not an approval.

**Acceptance checkpoint:** Do not call any BELL room `APPROVED_FOR_PRODUCTION` until individual required view plates have image evidence and human review. The first exterior candidate is intentionally `NON_CANON_PREVIS` until reviewed.

## Cross-department workflow

Read `WORKFLOW_18_STAGES.md` for ST01/ST02 research through ST18 learning. The location pack is required at ST05 Canon, ST07 Storyboard, ST10 Art, ST11 Director and ST12 Flow/Muse; ST15 independent QC examines real frames. A scene with ZERO family characters may still REQUIRE an approved BELL location plate.
