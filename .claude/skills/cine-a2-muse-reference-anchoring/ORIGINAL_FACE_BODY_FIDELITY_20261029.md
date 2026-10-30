# Bell & Leaf — ORIGINAL FACE & BODY FIDELITY LOCK (2026-10-29)

**User visual direction:** the **11 source images re-uploaded on 2026-10-29** are the visual identity authority for the 10 Bell & Leaf characters. Maintain their beautiful, natural, nuanced, cinematic realistic-CGI faces and body shapes. Generated second-generation sheets that simplify faces, enlarge eyes, alter age, facial proportions or silhouettes are **NOT replacements**. A prettier sheet is not necessarily a more faithful character.

## Source archive — immutable
Persistent user Library path:
`/CINE/Slow_English_A2/Character_Reference_Packs/CINE_BELL_LEAF_10_CHARACTER_SOURCE_VS_CANDIDATE_20261029.zip`

Manifest with original PNG SHA-256 and candidate PNG SHA-256:
`/CINE/Slow_English_A2/Character_Reference_Packs/CHARACTER_FIDELITY_MANIFEST_20261029.json`

Includes 10 separate user-uploaded original reference sheets, the user-uploaded original family lineup, 10 new *generated draft* character sheets, and side-by-side visual review HTML. The 10 original sheets are provenance/face-body anchors, NOT proof that any additional camera view was rendered in Muse. **All 10 newly generated draft sheets are REVIEW_REQUIRED_NOT_CANON.**

## Priority order and blocking rule
1. Direct user-approved original image for that exact character and role.
2. Separate human-approved identity-close and full-body reference generated or extracted from the same source and validated against original.
3. Independently generated human-approved view/expression/pose derived from approved anchor and checked for both face geometry and anatomy/height.
4. A reviewed variant outfit that cannot change face, hair volume, age/body proportions, or signature visual elements.
5. Descriptive prompt text, the lowest-priority fallback; never override visual original.

When an approved individual image for the exact view is missing, **hold the shot**; use only original/reference images in test mode. Do not silently create a generic new face or label a collage as full-frame approved reference. Scene final first-frame/video output must be independently checked.

## Exact tags, source image names and distinguishing identity
| Tag | Original user upload | Fixed identity points |
|---|---|---|
| `bo` | `bo(1).png` | Evan: adult postman, tousled brown hair, stubble, original lean adult facial and body scale |
| `me` | `me(1).png` | Mara: adult face and distinctive curls/braids, deep teal embroidered costume, original age/proportions |
| `juno` | `juno(1).png` | Juno: 13-year-old boy, unmistakable young face, hair, proportions and practical inventor gear |
| `Lia` | `Lia(1).png` | Lia: 11-year-old girl, big expressive brown eyes, freckles, deep chestnut curls, source body proportions and floral outfit |
| `bubu` | `bubu(1).png` | Bubu: vivid purple cat, ivory muzzle/paws, amber eyes, star-and-moon collar with ONE bell, unmistakably spiraling sparkling magical tail; sparkles are required in ALL views |
| `bix` | `bix(1).png` | Bix: small teal/brass mechanical turtle-pangolin, round amber-brown eyes, four articulated feet, rounded shell; NO BELL even if a concept sheet shows one |
| `ongngoai` | `ongngoai(1).png` | Orin: white wavy hair and beard, explorer wizard clothing; ONE personal travel bell; do not introduce glasses/extra bells absent in original |
| `bangoai` | `bangoai(1).png` | Maternal grandmother: long silver braided hair, taller flowing navy embroidered costume, distinct face and figure from paternal grandmother |
| `ongnoi` | `ongnoi(1).png` | Paternal grandpa: brown tweed flat cap, round glasses, tweed vest/jacket, short compact gentle figure, no magic |
| `banoi` | `banoi(1).png` | Paternal grandma: silver curly updo, round glasses, floral dress with burgundy cardigan; no magic |

`cagiadinh(1).png` is an overall family identity/cross-character scale reference but does not replace individual originals.

## QC actions for ST10/ST11/ST12/ST15
- Compare model's front AND three-quarter face against user original at similar head size; also compare body silhouette and characteristic garments, using side-by-side proof.
- Hold drift if eyes, cheeks, nose, brow, jaw, head-to-body ratio, apparent age, hair curl silhouette or skin textures change noticeably.
- Prefer neutral D55 5500K color reference; no overall yellow/amber tint, over-bloom, smoothing into generic doll/chibi, or live-action face recast.
- Bubu sparkles (especially spiral tail) must remain visible across turnaround and action frames, not only the cover hero.
- For character pack, export independent single-view and single-expression PNGs, not only labels and mini-panels inside a poster.
- Keep `SOURCE_ORIGINAL`, `DRAFT_GENERATED`, `REVIEW_REQUIRED`, `APPROVED_FOR_REFERENCE` explicit. Original received != all generated 3D views approved.
- Never update `CHARACTER_CURRENT.json` to point to generated candidates without reviewed image evidence, source and output SHA-256, approver/time and matching frame inspection.

## Runtime integration
CINE runtime must import the original source bundle from persistent Library (or its downloaded ZIP). This GitHub document does NOT itself upload image binaries into the Windows repo and DOES NOT constitute installed runtime canon; the device must sync when online. Parent skill: `SKILL.md`, schema and ref resolver in `integration/`.
