---
name: cine-yoga-kids-character-memory
version: "1.0.0-proposed"
description: "CINE Yoga Kids cast registry, single-character identity and fashion lock, yoga grip-sock footwear gate, and image-to-video character continuity."
status: "GITHUB BRANCH PROPOSAL — NOT LOCAL INSTALLED — NO APPROVED IMAGE MASTERS"
---
# CINE / Yoga Kids — Character Identity + Wardrobe + Grip Sock Skill

## Trigger
For any Yoga Kids / Kids Yoga / Bright Moves / CINE Yoga series character selection, outfit design, image, thumbnail, yoga-mat pose, storyboard, I2V video shot, character consistency or cast comparison.

## Files and routing
Read `config/niches/yoga_kids/character_registry.json` then `config/niches/yoga_kids/README.md`. This skill ONLY applies to Yoga Kids and MUST NOT override A2 Bell & Leaf canon, voice and location packs.

## Mandatory input contract
`character_id` from registry; `character_name`; `target_asset_type`; `outfit_id` (yoga|casual|street|sport|chill); `reference_image_path` + SHA256 if available; camera/view; approval status; pose if yoga; footwear and surface specification. If reference is missing, generate `CONCEPT_ONLY` with identity not guaranteed. Never call the model's output canonical merely from text prompting.

## Lock procedure
1. Resolve immutable character ID and cross-check original face/eye/hair, age-appropriate body, ornaments and personal palette. Keep repeatable facial proportions and fixed signature hair silhouette.
2. Generate exactly ONE character identity per image, except if explicitly creating that SAME character's 5-outfit turnaround page. A team poster does not count as an individual master.
3. Outfit must use the registry five look descriptions. Do not force skirts, athletic trousers or the same garments on everyone. Clothing may be elaborate and striking but practical, not restricting limbs; accessory position must not interfere with exercise.
4. **Yoga surface decision rule:** if character's foot touches or is on top of any yoga mat, footwear == **SOFT_THEMED_GRIP_SOCKS** and `SHOE_COUNT_ON_MAT=0`. Check every hero pose, turnaround, inset and thumbnail independently. Grip dots on sole where visible. This instruction overrides any source poster showing yoga in sneakers.
5. Everyday street/sport outfit displays that are NOT yoga mat poses may have sneakers; do not silently delete them from wardrobe showcase.
6. Keep 5500K neutral white balance, detailed premium CGI, realistic hands/feet/toes, no copy of branded third-party IP or competitor frames. No invented endorsements or empirically untested claim kids universally prefer an outfit.
7. Keep pose instruction age appropriate and approachable. Reject excessive backbend/flexible hero poses as a recommended exercise unless certified by a competent instructor.

## Output manifest
For every character create `<character_id>__MASTER_FRONT.png`, `__SIDE.png`, `__BACK.png`, `__3Q.png`, `__EXPRESSIONS.png`, `__YOGA.png`, `__CASUAL.png`, `__STREET.png`, `__SPORT.png`, `__CHILL.png`, `__SOCK_TOP.png`, `__SOCK_SOLE.png`, `__POSE_QA.png` (all individual images; no falsely assembled tiny grids as originals). Pair each with real file SHA-256, model/seed when obtainable, owner review time, version, and `approval_status`.

## Fail-closed QC
- `IDENTITY_MATCH`: real face/hair reference and view consistency; if missing set PENDING.
- `OUTFIT_DISTINCT`: five visibly different fits, not palette-only swaps.
- `YOGA_MAT_NO_SHOES`: zero shoes/boots/sneakers in ALL on-mat panels; fail if any detected, including inset.
- `YOGA_GRIP_SOCK_QA`: styled socks present on both feet, visible sole grip where exposed, no floating/extra body parts.
- `ANATOMY_AND_SAFE_MOVEMENT`: five fingers each hand, natural joints, attainable stretches.
- `ASSET_PROVENANCE`: actual source path, SHA, rights record, reviewer; absent => pending, never pass.
- `KIDS_POLICY_REVIEW`: consider audience classification correctly; packaging target is US elementary and middle-school children, don't promise that teacher-directed titles alone avoid Made-for-Kids treatment.
All gates must pass independently before moving status from CONCEPT_ONLY to APPROVED_CANON. Only owner can finally approve master designs.

## Rio special continuity lock (latest user-approved direction)
Boy Rio with black/brown curls and ONE orange front streak, cheerful brown-eyed face, tropical orange/teal wave and palm sun identity. Five distinct yoga-ready outfits (Explorer, Street, Athleisure, Adventure, Chill). On the yoga mat all have themed fitted grip socks, no shoes. Do not convert Rio into generic Kai blue lightning or Milo orange curls. Original reference remains external to repo pending file import and owner acceptance.

## Dedupe policy
Same face and hair lock with only wardrobe/camera difference = outfit variant. Different person evidenced by approved full-res multiple angles = new stable character ID. Similar single images alone are NOT enough to merge by name/color. Special caution: Sky vs Skye, Luna vs Sunny, Zoe vs Zuri, Zara vs Kaya and blonde/pink designs.

## Evidence status (2026-10-31)
33 named concepts recorded (23 female / 10 male). This is a proposed reference and a review queue, **not** 33 file-verified, human-approved image masters, and not proof of local integration. No networked image binary assets are uploaded by this PR.
