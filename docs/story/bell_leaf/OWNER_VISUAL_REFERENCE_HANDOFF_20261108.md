# CINE / Bell & Leaf — Owner Visual Reference Lock (2026-11-08)

**Source:** user-supplied Windows folder SLOW NGLISH PHÙ THUỶ (23 PNG pictures). 10 character sheets, 1 complete family reference, 9 independently framed location plates and 3 composite Bellfern reference maps. Source files are not modified or deleted.

## Image identity and evidence
The 11 original owner character sheets have **pixel-exact** correspondence with the already-local CINE v2 owner-locked character sheets, validated by comparing every RGB pixel. PNG SHA256 differs solely due to file re-encoding/metadata; canonical face and body pixels are unchanged. All 21 v2 exact pixel crops and character sheets retain their existing SHA256 proof.

- Master structured reference ledger: config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json
- Existing official character source: config/niches/slow_english_a2/CHARACTER_VISUAL_CANON_LOCK_CURRENT.json
- Existing official location registry, extended not replaced: .claude/skills/cine-a2-muse-reference-anchoring/integration/config/LOCATION_CURRENT.json
- 9 source location photos: assets/canon/location_refs/slow_english_a2/bell_leaf/owner_provided_20261108/plates
- 3 composite location maps: assets/canon/location_refs/slow_english_a2/bell_leaf/owner_provided_20261108/moodboards
- EP001 S001–S270 binding: docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json
- Verification: python tools/bell_leaf/inspect_visual_reference_20261108.py --require-assets

## Locked owner source views; geometry still requires multiple angles
| Existing CINE space | Direct source photograph | Observed immutable design cues |
|---|---|---|
| BELL BH-EXT | BELL_HOUSE_EXTERIOR_DAY | Stone house, glass conservatory camera-right, garden and lake; different exteriors in maps are not replacements |
| BELL BH-FOYER | BELL_FOYER_DAY | Curved carved stair rises right, open arch/greenery left, blue wall hanging |
| BELL BH-KITCHEN | BELL_KITCHEN_DAY | Long wood dining table, slate-blue cabinets, windows and fireplace |
| BELL BH-PARENTS | BELL_PARENTS_BEDROOM_DAY | Dark-blue bed linen, timber bed, wide windows |
| BELL BH-JUNO | BELL_JUNO_BEDROOM_CANDIDATE | Blue bed and mechanical workspace; room-person assignment not formally approved |
| BELL BH-LIA | BELL_LIA_BEDROOM_CANDIDATE | Cream/pink canopy bed and cat bed; room-person assignment not formally approved |
| BELL BH-ATELIER | BELL_MARA_ATELIER_DAY | Heavy wooden central desk, arched window and craft tools |
| BELL BH-BELLCHAMBER | BELL_CENTRAL_BELL_HALL_CANDIDATE | Monumental bell hall has potential size/history conflict with the recently built hidden Earth station; use blocked until owner reconciles |
| BELL BH-REAR-GARDEN | BELL_REAR_GARDEN_DAY | Mature tree, birdbath, stone path, flowerbeds, lake backdrop |

**Three collage maps are LOCATION CONCEPTS ONLY.** They contain variant building façades and cannot be treated as independent shot images, or silently replace the standalone daytime exterior. Do not invent physical reverses by mirroring a primary source photo. A single owner-supplied view locks its visible design, not the entire unseen house geometry. Existing 483 room and 756 prop multiview backlog remains honest; room-level production approval stays PENDING_NOT_GENERATED.

## Shot and production contract
The binding file has EXACTLY 270 shot rows. Each gives an existing site/room code (or explicit UNREGISTERED location), source-plate path/SHA where available, plausible visible actor tags from screenplay, real source image/crop paths and missing-character warnings. All character-tag candidates remain pending independent director shot review; they are not face recognition results. No media IDs or final approval have been invented.

Do not attach a face reference for a character who is offscreen or voice-only. No visible person means no character reference images. Strictly preserve Evan, Mara, Juno male 13, Lia female 11, tiny bell-free Bix, purple Bubu with ONE GOLD COLLAR BELL and PERMANENT SPARKLING SPIRAL TAIL, Orin, paternal grandparents Arthur/Rose and supporting Elara. **Aila has no approved owner face** and cannot be rendered as an invented person.

The screenplay requires additional set references: historical Veylora, Earth creek, grandparents' cottage, Bell guest/refuge room, night plates and the private Earth fixed bell station. Do not substitute the Bellfern house, decorative map collage or huge old bell hall for those. Freeze topology before image production. Each output must be independently authored native 16:9 with neutral daylight around D55 5500K, no false 9-grid/contact sheet, no subtitles, and one coherent 10.0s video performance shot. Require lipsync, face and voice QC separately.

## Status / do not overclaim
Local copied asset sources: 11 character and family sheets, 21 face/hero/tail crops, 9 standalone location photos and 3 moodboards = 44 binary files. EP001 binding: 270 shots; 246 with ≥1 inferred owner-locked known cast; 64 have unapproved/unavailable actor visuals; 161 have some owner location plate. **0 shot has independent complete multi-angle, voice and I2V production approval.** Script is DRAFT, not owner-final.

Source files are recorded with original SHA256, as are the preserved canonical binaries. If a GitHub checkout lacks binaries, tools must BLOCK with ASSETS_MISSING_NOT_PRODUCTION_READY rather than pretending that the source hashes in Git prove an actual picture is present.

New episodes EP002–EP1000+ must resolve actors/locations from this same master registry, not independently redesign the family, house, school or bells. Any new source is a new immutable revision requiring owner review.

## GitHub publication and intellectual property safeguard

As checked on 2026-11-08, repository huongtina74-ux/cine has visibility **PUBLIC**. Its GitHub main contains the text reference registry and validation code, **not the 44 PNG owner character/location originals**. A developer or agent MUST NOT promote an owner-source image, the entire local binary asset commit, a ZIP, or an equivalent base64-encoded copy to this public repository without specific owner approval of public distribution. The source images are safely installed in owner Windows CINE with checksum validation and locally committed in isolated worktree branch feat/bell-leaf-owner-visual-canon-20261108 (commit bc5972e). The Windows Git client currently has no write authentication; this is an additional upload blocker. To synchronize images remotely without revealing commercial source artwork, use an authenticated PRIVATE asset repository or a restricted artifact store, and preserve the existing Canon paths/hashes. A public text manifest does not count as remote image backup. Keep `ASSETS_MISSING_NOT_PRODUCTION_READY` on fresh GitHub clones until genuine binary source files have been supplied via authorized private storage.
