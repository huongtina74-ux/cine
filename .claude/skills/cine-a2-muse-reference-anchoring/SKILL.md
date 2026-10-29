---
name: cine-a2-muse-reference-anchoring
description: Mandatory Muse Image master-character, face-angle, approved-location and first-frame anchoring skill for CINE Slow English A2 v1.1 / Bell & Leaf.
---

# CINE Slow English A2 v1.1 — Muse Image Reference Anchoring

## Objective and boundaries
Use approved visual anchors to generate consistent, original *Bell & Leaf* 3D CGI characters and settings. This skill supplements the **existing** Character Visual Canon and `cine-bellfern-location-multiview-lock`; it never redefines either. NEVER call source sheets or generated candidate outputs automatically approved.

**Scope:** ST05 story/visual canon, ST07 storyboard, ST08 planning, ST10 visual assets, ST11 direction, ST12 Flow/Muse, ST15 independent visual QC, ST18 audited learning. Research ST01/ST02 may inspire cinematic methods but cannot replace approved character/location assets.

## Exact Flow/Muse character tags
`bo` = Evan; `me` = Mara; `juno` = Juno; `Lia` = Lia; `bubu` = Bubu; `bix` = Bix; `ongngoai` = Orin; `bangoai` = maternal grandmother; `ongnoi` = paternal grandfather; `banoi` = paternal grandmother. Case is significant. Beware the visible tag `me` is Mara; never resolve it to a personal `@me` avatar. Resolve using immutable media IDs.

## Four mandatory stages

1. **Source Master / Identity Lock:** retain and hash the original user-approved character reference files. Extract/select a clean one-character input and store its exact original. Create a new crisp neutral standalone master from that input with Muse Image only when a supported authorized API and model are available; do NOT invent a redesign. Human reviewer approves a master only after reviewing an actual image, preserving face, silhouette, hair, clothing, body scale, material, eye shape and accessory rules.
2. **Angles and Expressions:** render each view as ONE independent image: front, front 3/4, side, back; face angles front/3/4/profile/up/down; expressions neutral, happy, curious, surprised, thoughtful, gentle, worried, excited. Preserve same character and outfit for core turnarounds, and do not synthesize unapproved wardrobe changes. Details may be separately captured as isolated images. A 4x4 collage is never an approved individual anchor.
3. **Background Reference:** reference location master from `cine-bellfern-location-multiview-lock`; load the APPROVED individual plate with `site_id/space_id/view_id/sha256`, not a freely invented generic scene. Reverse angles must be physical, not mirrored. Respect ordinary-Earth secrets, location architecture and fixed props.
4. **Final Story Still / Video:** attach only the visible tagged character master/angle/face anchors and relevant approved location plates; scene action, first-frame pose, blocking, eyeline, emotion and camera are shot-specific. Create one standalone full-bleed 16:9 CGI image, never a storyboard or text panel. Muse video uses the approved first frame where supported; audio voice identity comes from the approved WAV/voice-lock source, not from prompt text alone. Subtitle overlay happens in postproduction, never baked into raw first-frame still.

## Muse Image API contract (verify your account/runtime)
Meta's published Muse Image guide documents `muse-image-1.0` on Responses API, `input_image` content parts for existing references, `previous_response_id` for continuing a compatible conversation, and `image_generation_call.result` as the image output. Require a valid, user-authorized `MODEL_API_KEY`, actual entitlement and budget before paid calls. Never invent an integration or claim a live Muse call when there is none. Do not chain across different characters to avoid unintended blended identity. Store original response ID per character, versioned with image files.

**Reference source:** https://dev.meta.ai/docs/cookbook/anchored-image-series and https://dev.meta.ai/docs/cookbook/image-generation-basics

## Image prompt compilation (mandatory)
Build per-image prompt as `ID + SOURCE MASTER + SINGLE VIEW/EXPRESSION OR FIRST-FRAME ACTION + CAMERA + MATERIAL/LIGHT + CONSTRAINTS`. A one-line English prompt is one request; exactly one blank line separates prompts in batch TXT. Do NOT dump the ten-character roster inside each prompt. Do not paste screenplay dialogue into image generation. Keep no random actors, no image-grid, no text/subtitles/logos/watermarks. Choose 50 mm equivalent as portrait starting point and appropriate depth of field to keep face or room critically sharp. Neutral D55 / 5500K photographic color balance with accurate whites and greys, natural complexion/fur and no GLOBAL yellow/orange cast; real warm sources can be locally present if motivated but do not replace the neutral grade.

## Mandatory reviews / approval gates
- `SOURCE_CROP_UNREVIEWED` means a pixel-exact crop of user-provided source art, **not** a Muse-generated or approved image.
- `DRAFT_GENERATED` means a model returned an image but visual identity may still be wrong.
- `REVIEW_REQUIRED` means human character/visual canon review is pending.
- `APPROVED_FOR_REFERENCE` is set only by recorded reviewer, dated original image/hash and positive character and style checks.
- `QC_FAIL_IDENTITY`, `QC_FAIL_UNAPPROVED_PROP`, `QC_FAIL_WRONG_LOCATION`, `QC_FAIL_MULTIPANEL`, `QC_FAIL_TEXT`, `QC_FAIL_COLOR`, `QC_FAIL_PHOTOREAL_RECAST` are failures, not completion.

**Important canon conflicts to watch:** Bix must NOT acquire a bell; Bubu alone wears his approved collar bell; Orin has a separate travel bell, the home bell lives in the protected Bell chamber. Some uploaded/generated concept sheets show extra bells and costume variations; do not treat these as automatically approved. Avoid exposing home magic to bo, ongnoi and banoi.

Each accepted record must include `character_tag`, `original_source_id`, `original_source_sha256`, `master_media_id`, `view_id`, `output_sha256`, `generation_model`, `response_id` if available, `continuity_version`, `reviewer`, `reviewed_at`, `qc_report` and `approval_state`. Keep original files unchanged and safely downloadable.

## Required pilot
A2 Bell & Leaf: start with `Lia` and `bubu` individually from the user-supplied master sheets. Produce one single clean master each, front/3/4, neutral/curious expression, then combine them with the **approved** Bell workshop or forest location master. Only after visual review expand to `bo`, `me`, `juno`, `bix`, `ongngoai`, `bangoai`, `ongnoi`, `banoi`. No automatic 18-shot production until the identity and location QC gates pass.

## Handoff
The working export may contain 10 ORIGINAL_USER_SOURCE files and standalone SOURCE_CROP candidates plus individual request prompts. The crop pack is only a preparation kit and must never be represented as Muse generation results. Multi-shot 10s animation requires separate I2V gating and voice-lipsync testing.


## CINE Slow English A2 v1.1 — executable reference resolver and pending-image gate

For `project_id=slow_english_a2_bell_leaf`, the mandatory technical integration lives at `integration/`:
- `config/slow_english_a2_bell_leaf_project_profile.json`
- `config/CHARACTER_CURRENT.json`, `config/LOCATION_CURRENT.json`: **all not-yet-reviewed assets remain pending**. No hypothetical approved file paths.
- `schemas/CHARACTER_REGISTRY.schema.json`, `schemas/LOCATION_REGISTRY.schema.json`, `schemas/SHOT.schema.json`
- `src/bellLeafCanonResolver.ts`: `resolveCharacterRefs`, `resolveLocationRefs`, `buildBellLeafPrompt`, `runBellLeafQC`, `verifyReferenceFiles`, `resolveShot`.
- `tests/bellLeafCanonResolver.test.mjs`: fixture-only metadata tests (12/12 locally passed, not a live Muse/Flow run).
- `scripts/muse_reference_render_queue.py`: **dry run by default**; real Meta Muse API calls require `--execute`, a supported account and `MODEL_API_KEY`.
- `docs/INSTALL_AND_QC.md` and `docs/SHOT_METADATA_TEMPLATE.md` for installation, shot planning and approval handoff.

The source asset bundle is kept as an independent **59 MB private library ZIP**, not falsely claimed committed to GitHub: `/CINE/Slow_English_A2/Character_Reference_Packs/CINE_A2_CHARACTER_REFERENCE_LIBRARY_V1_1_R1.zip`. A portable end-to-end integration kit with exact files is at `/CINE/Slow_English_A2/Canon_Lock_Integration/CINE_A2_CANON_LOCK_INTEGRATION_V1_1_COMPLETE.zip`.

**Runtime warning:** These files in a GitHub branch do not mean the Windows CINE runtime has imported them; integration with its actual orchestrator and local assets must be performed/verified when that device is online. The 270 Muse independent view/expression targets are **PENDING_NEW_RENDER**, not manufactured or approved by documentation. Existing location plates also remain pending.

## Mandatory original-image fidelity override (2026-10-29)

Before generating, approving, or resolving any Bell & Leaf character view/expression, **MUST read [ORIGINAL_FACE_BODY_FIDELITY_20261029.md](ORIGINAL_FACE_BODY_FIDELITY_20261029.md)**. The latest 10 user-reuploaded source images are the primary visual identity authority; generated reference sheets in the associated review archive are ALL drafts. Lock exact original face geometry, proportions, age, skin/fur texture, signature hairstyle, body scale, and accessories. Bubu's purple tail MUST retain sparkles/glow across all individual views. Do NOT promote a prettier but different face into `CHARACTER_CURRENT`. Stage ST15 must verify side-by-side actual source vs candidate before human approval. This constraint takes precedence over generic 'cute', 'Pixar-like', beauty, doll, or stylization prompt words.


## REQUIRED SOURCE-CANON MANIFEST v1.2 (2026-10-29, character identity hard lock)

All Bell & Leaf Slow English A2 shots MUST load the **user-approved original-source identity authority** from [canon/CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json](canon/CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json) and its original file SHA-256. Verify bytes before accepting them as actual references. See [canon/PIXEL_PROVENANCE_QC_V1_2.json](canon/PIXEL_PROVENANCE_QC_V1_2.json) and [canon/FINAL_QC_REPORT_V1_2.md](canon/FINAL_QC_REPORT_V1_2.md).

The full source PNG asset kit is stored persistently in user's CINE Library at `/CINE/Slow_English_A2/Character_Reference_Packs/CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2.zip`; these 22 PNGs are **not** committed to this text-only GitHub branch. When device is available, use `scripts/install_character_canon_into_cine_v1_2.py` to verify and install them into local CINE. If missing/unverified, report `CANON_SOURCE_NOT_INSTALLED` and do NOT silently generate new random identities.

**Status distinctions are non-negotiable**:
- 10 original sheets: `USER_APPROVED_SOURCE_IDENTITY` — immutable identity reference for future generations.
- 10 extracted source masters: `SOURCE_EXACT_PIXEL_VERIFIED` — 10/10 full RGB exact-crop checks; identity matches source **only for visible pixels**, not a new-angle approval.
- Bubu supplemental HERO and SPARKLING-TAIL reference: use both to avoid the original low-resolution cropped master losing the glow or the spiral.
- 10 generated replacement multi-panel sheets: `REVIEW_REQUIRED_NOT_CANON`, none authorized to replace user originals.
- 270 proposed independent Muse angle/expression renders: still `PENDING_NEW_RENDER`.
- Any location still without an approved plate: BLOCK final production shot, even if character's source identity was locked.

**Mandatory precedence:** ORIGINAL SOURCE > exact source crop and Bubu sparkle detail > independently human-approved new angle/pose/expression > words-only prompt. Do not mark a generative output as identity-verified just because its seed, title, SHA or input character reference matches; SHA validates file identity, NOT facial likeness for newly generated pixels. Never promote new variant without source/target side-by-side review and human acceptance.
