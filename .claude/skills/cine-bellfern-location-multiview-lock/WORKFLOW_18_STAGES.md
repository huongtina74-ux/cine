# CINE / Bell & Leaf — Mandatory Location Identity Pack across 18 stages

**Policy:** CINE_LOCATION_LOCK_RULE / 2026-10-29  
**Authority:** user-approved Bell & Leaf canon and approved visual assets take precedence over this proposed registry or any AI-rendered draft.  
**Implementation:** extend the existing `cine-bellfern-location-multiview-lock` skill; do not fork a second location truth source.  
**Current state:** registry is DRAFT, 12 sites / 69 spaces / 108 hero/recurring props are inventoried, 483 room-view and 756 prop-view slots remain **PENDING_NOT_GENERATED**. This document does not mark a single image, location, or Muse shot APPROVED.

## 1. Non-negotiable Location Lock rule

Every **recurring location** must have an individual, reusable, human-approved **Location Identity Pack** and a spatially consistent location bible BEFORE any shot involving that location can be declared `APPROVED_FOR_PRODUCTION`. This includes locations used in Google Flow first frames, Muse image-to-video shots, storyboard references, Blender scenes, and later episodes.

A location must not be reinvented independently for each scene. Lock the shape and scale of buildings, number of stories, roof/window/door placement, stairs, corridors, room adjacency, fixed furnishing, gardens, landmark props and original place identity. Only shot-justified temporary props, minor dressing, time/weather/illumination and approved costume variation may change. Even allowed changes cannot contradict architecture, location geometry, geography or character knowledge.

**Minimum pack for each location**
1. **Exterior hero / establishing:** a readable architectural master frame; also capture approaches and rear sides when needed for scene continuity.
2. **Main interior:** the main story/functional space with stable architectural landmarks.
3. **Physically correct reverse angle:** camera placed at the genuinely opposite location according to floorplan; NEVER a horizontally mirrored bitmap.
4. **Identity detail images:** entrances, specific window configuration, stairs, fireplaces, work/dining/bed furniture, shelves, fixed mechanisms, and unique props actually present at this site.
5. **Site/floorplan map:** north reference, room-to-room adjacency, door and window coordinates, scale references and stable scene geography.

**Production multiview standard already defined by the existing skill:** independent native 16:9 `MASTER_WIDE`, `FORWARD`, `REVERSE_TRUE`, `LEFT_3_4`, `RIGHT_3_4`, `DETAIL_ANCHORS` and `PLAN_TOP` plates per significant interior space. `PLAN_TOP` may be a schematic as long as coordinates agree. Hero props need their own `FRONT`, `THREE_QUARTER_LEFT`, `SIDE_RIGHT`, `BACK`, `TOP`, `MACRO_DETAIL`, `PLACED_IN_SCENE` references. If a view is structurally inapplicable, document the reason rather than inventing it.

Every plate is a **separate full native-resolution image**, not a 2x2/3x3 collage, storyboard sheet, thumbnail, mirror, or outpainting of a different angle.

## 2. Locked vs permissible changes

| Fixed after approval | Conditional changes (must respect fixed geometry) |
| --- | --- |
| Building outline; number of storeys; entrance, exterior, roof and window placement | Season, weather and time of day |
| Floorplan; size/shape of rooms; staircase and corridor topology | Physically consistent natural and practical illumination |
| Door/window handedness, sightlines and views to outside | Small movable set dressing, reasonable clutter, episodic props |
| Fixed hero furniture, unique signage/landmarks, hidden mechanisms | Character costume changes that do not change character identity |
| Stable world-axis sun direction for a continuous scene | Camera location, framing and lens only when compatible with plan |
| Function and magic/ordinary-world rules for the space | Scripted effects that do not morph or relocate architecture |

**Color/photography skill:** natural cinematic CGI with physically credible surfaces; reference daylight D55 / approximately 5500 K neutral white balance, clean whites and greys, natural skin/fur/material colors, soft physically plausible shadows, restrained saturation, no global yellow/orange cast, sepia, golden wash, neon overload or teal-orange LUT. 50 mm full-frame perspective is a baseline, **not a compulsory camera setting**; choose other lenses when motivated. The f/1.8 aesthetic is limited to isolated focus; use f/2.8–f/5.6 (or equivalent deeper DoF) for group shots and architecture to keep geometric anchors readable. D55 is a grading/reference target rather than a ban on all physically motivated warmer practical lights at night.

**Visual canon and story:** preserve approved original 3D animated faces and bodies, never replace with live-action actors or generic humans. Bell & Leaf home is two storeys; magic is hidden from `bo` (Evan) and paternal grandparents `ongnoi` / `banoi`. Normal Bellfern school is an Earth school, not a fantasy academy. One home bell, Orin's own travel bell, `bubu` collar bell; `bix` gets no bell.

## 3. Source of truth and record schema

Read and extend ONLY the existing files:
- `registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json` for `site_id`, `space_id`, adjacency, fixed props and site identity;
- `registry/LOCATION_MULTIVIEW_MANIFEST.csv` for per-room angles;
- `registry/PROP_MULTIVIEW_MANIFEST.csv` for prop plates;
- `registry/SCHOOL_EARTH_PATCH_v1_0.json` for ordinary-school canon;
- `templates/MUSE_I2V_10S_SHOT_CONTRACT.md` for Muse shot details.

An approved location pack must record, at minimum: `site_id`, `space_id`, canonical location-version, a physical plan with labelled north and scale, `camera_anchor_id`, `view_id`, original image path and native width/height, source `sha256`, approved hero/fixed-prop IDs, `sun_direction_world`, lighting profile/time of day, neutral exposure reference, reviewer and UTC timestamp, topology/character/style QC result and a signed/recorded approval state.

Use `PENDING_NOT_GENERATED`, `DRAFT`, `REVIEW_REQUIRED`, `REJECTED`, `APPROVED` explicitly; NEVER infer APPROVED from filenames, screenshots, a generated image, one prettier variation, a green technical checkbox or a completed API call.

**Location references are distinct from character references.** A shot with `activeCharacterTags: []` may correctly use ZERO character refs while still requiring one or more **approved location plates**. Never attach all 10 family characters because they are named in a master prompt; never treat 0 characters as 0 location evidence.

Exact character tag spellings, only when genuinely visible: `bix`, `bangoai`, `bubu`, `juno`, `Lia`, `ongngoai`, `banoi`, `ongnoi`, `bo`, `me`. A named character in narration or a drawing is not necessarily on screen.

## 4. Required integration into the existing 18-stage CINE pipeline

| Stage | Department/owner | Location Lock handoff / blocking rule |
| --- | --- | --- |
| ST01 Research Radar | Research Intelligence | Observe cinematic location continuity as a research dimension; source/citation required, competitor location never becomes CINE canon. |
| ST02 Competitor Forensics | Film Deconstruction | Study actual timecoded set/reverse/camera/lighting geography and methods; extract film-language lessons only, do not copy protected designs. |
| ST03 Opportunity Scoring | Content Strategy | Include location-pack creation and reuse cost and risk in feasibility. |
| ST04 Packaging | Creative Strategy | Location can inspire truthful thumbnail/hook, but thumbnail concept cannot rewrite canon geometry. |
| **ST05 Episode Canon Snapshot** | Story Governance | **HARD GATE L01:** load exact `site_id/space_id`, approved location version, topology and character/world canon; pending/mismatched pack blocks production greenlight. |
| ST06 Writers Room | Screenplay | Each scene declares location and interior zone, entry/exit, relevant fixed hero props, time of day and known continuity states; writers cannot silently redesign a place. |
| **ST07 Storyboard / Animatic** | Visual Story | **HARD GATE L02:** show physically plausible floorplan, true camera reverse, eyelines, blocking and window direction; previs may be low fidelity but not a substitute for approved plates. |
| ST08 Production Planning | Producer | Enumerate missing packs/plates, dependent shots, candidate reuse and real budgets; approved plate IDs attached to shot contracts. |
| ST09 Voice Performance | Voice | Indoor/acoustic space affects ambiance/reverb only; stable voice IDs and approved WAVs remain authoritative. |
| **ST10 Visual Development** | Art / Asset | **HARD GATE L03:** create/inspect master exterior, interior, reverse, detail and floorplan plates; QA material, 5500 K neutrality and geometry; human reviewer freezes approved versions with hashes. |
| **ST11 Director / Animation** | Director / DOP / Animation | **HARD GATE L04:** shot blocking, camera coordinates, perspective, scale, eyelines and light directions are derived from approved set layout and view anchors. |
| **ST12 Rendering / Flow / Muse** | Render / Technical | **HARD GATE L05:** exact one full-frame 16:9 still for each Flow shot; approved location plate and relevant approved character images only; Muse 10.00 s from approved first frame; no furniture/window morph, no random subtitles. |
| ST13 Editorial / Compositing | Editor | Shot/reverse continuity, screen direction, correct room order and no unexplained relocation between cuts; add optional subtitles only after visual generation. |
| ST14 Sound / Mix | Sound | Motivate indoor/outdoor ambience, room tone and acoustic transitions; voice consistent and dialogue clear. |
| **ST15 Independent Master QC** | Independent QC | **HARD GATE L06:** compare at least start/mid/end frame to approved plates/floorplan, true 16:9, geometry/window/prop placement, identity, neutral color and absence of embedded text; do not approve with only technical PASS. |
| ST16 Publishing | Distribution | Release requires independently accepted visual/location continuity and owner authorization. |
| ST17 Analytics | Analytics | Measure audience response to location/series world-building only from owned and verifiable data. |
| ST18 Controlled Learning | Studio Learning | Log scene drift issues, update design/lighting/shot compilers by reviewed versioned change; never silently rewrite approved canon from one failed render. |

No new 19th standalone department is needed. Location Lock is a **cross-department production invariant** enforced by the existing location skill and 18 handoffs.

## 5. Location Identity Pack production workflow

1. **Describe the site** — narrative role, emotional tone, ordinary/magical permission, real-world architecture, stable floorplan, fixed landmarks, relation to streets/garden and adjoining rooms.
2. **Create a plan and reference series** — architecture master, independently rendered exterior/interior/reverse/left/right/detail/top where appropriate, props at consistent scale and camera coordinates; start with low-cost drafts.
3. **Review against canon** — Art Director, DOP/location continuity and independent reviewer check real wall/window/stair/door adjacency, true reverse, scale, fixed prop signatures, world-sun direction and D55 color. Record approvals and original image hashes.
4. **Freeze Location Bible** — store approved plates, absolute coordinates, orientation, materials, fixed props and versioned reference metadata; do not edit approved originals in place.
5. **Produce shot contracts** — each 10-second shot resolves script lock, `site_id`, `space_id`, `approved_view_id`, `camera_anchor_id`, `location_plate_sha256`, world sun/light, `character_ref_ids`, prop states, first-frame output and voice WAV when applicable.
6. **Generate and QC** — Flow makes a single isolated 16:9 still with no text/subtitle; Muse animates 10.00s (where supported), respecting original 3D character models and locked voice files; human QC may reject/retry but may not secretly move architecture.
7. **Reuse unchanged across episodes** — approved location pack remains shared by all episodes; any structural modification requires a new version, a change record and explicit approval.

For multi-shot bulk import, retain the user's format: **one English prompt on a single unbroken line; exactly one blank line between shots**. Store structured location IDs and refs *alongside* that text instead of listing all reference IDs in every prompt.

## 6. Bell & Leaf location pack priority and coverage

| Site ID | Location | Mandatory spaces / notes (detail registry is authoritative) |
| --- | --- | --- |
| `BELL` | Bell & Leaf House | Exterior front/rear, foyer, living, kitchen/dining, Evan/Mara bedroom, Juno bedroom, Lia bedroom, Mara workshop, secret bell chamber, stairs/hallway, rear garden; physically consistent interior reverse views. |
| `ORIN` | Orin's Hill House | Exterior, research, sleeping/living space, archive, bell fabrication/workshop; separate travel bell. |
| `ROSE` | Paternal grandparents' Rose Cottage | Exterior, sitting room, kitchen/dining, bedroom, porch/small yard; ordinary Earth details, no exposed magic. |
| `SCHOOL` | Bellfern Community School | Exterior, playground, separate age-appropriate classrooms, hallways, ordinary library/common teaching space; no fantasy-school retcon. |
| `SQUARE` | Bellfern Town Square | Street-to-square establishing, main landmark, crossings. |
| `POST` | Bellfern Post Office | Exterior, public counter, sorting/work area. |
| `LIBRARY` | Bellfern Old Library & Archives | Exterior, library halls, shelves, archives. |
| `BRIDGE` | Silverbrook Bridge & Riverside | Bridge approaches and true reverse along river. |
| `FOREST` | Whisperwood Forest | Path/clearing, stable landmarks, readable travel geography. |
| `BAKERY` | The Little Oven Bakery | Exterior, customer area, work/baking area. |
| `STATION` | Bellfern Railway Station | Exterior, platform, waiting/ticket spaces. |
| `LAKE` | Bellfern Lake & Old Boathouse | Shore, dock, boathouse, stable waterside views. |

**Rollout principle:** prioritize actual next-production locations rather than spending resources generating all 1,239 planned plates at once. However, no shot may be classified production-approved until the **specific location and angles it uses** meet the required location-approval evidence. Other sites may remain PENDING and must be honestly labelled.

## 7. Acceptance and failure policy

Reject or hold when:
- actual location plate/source path or SHA-256 is missing, stale or unapproved;
- reverse-angle image is simply horizontally mirrored or architecture changes;
- door/window/stairs/room relationships, fixed props, road/garden geography or world-sun light direction change unintentionally;
- one output image is a collage, 9-panel board, blurred side-fill, text/subtitle render or a low-resolution crop;
- character identities drift or `bo` / grandparents see magic contrary to story;
- global image becomes yellow/orange, scene's dominant light origin moves without cause, or the frame hides mandatory anchors;
- Muse has no actual actor animation, voice identities are improvised, speech alignment is unknown, or any 10-second clip is falsely reported accepted.

`PENDING_NOT_GENERATED` is the honest default. A file exists != human approved. QC automation can flag failures and collect evidence but cannot self-approve style or architectural canon.

## 8. Next implementation tests (must not falsely auto-pass)

1. `BELL` exterior/front/real-reverse preserve roof, window counts, entrance, and cardinal orientation.
2. `BELL` kitchen forward/reverse preserve the identical dining table, doors, window and stair sightlines.
3. `BELL` Juno vs Lia bedrooms remain in their approved floors/relative positions.
4. `BELL` Mara workshop and secret bell chamber are distinct and spatially stable, with no unauthorized bell replication.
5. `ORIN`, `ROSE`, `SCHOOL` use independent location packs; school stays normal.
6. Repeat one `BELL` shot in two episodes from the same approved location source; compare semantic geometry and reference checksum.
7. Shot with zero family characters still resolves its appropriate approved location plate; only character refs are 0.
8. Live Flow and Muse generation results must be inspected frame-by-frame before claiming PASS, including voice/audio and geometry.

**Cross-reference:** this policy supplements the existing `SKILL.md` and the current CINE ST01–ST18 workflow; it does not override approved Story Bible, Visual Canon or rights approvals.
