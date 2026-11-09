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


### Verified 90-crop source library — complete package

**Latest installable asset ZIP:** `/CINE/Slow_English_A2/Character_Reference_Packs/CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2_COMPLETE.zip` (SHA-256 `2783de7204e315f89743f9dde0d0715fc023b4ed532443fba6f1e6c57c13fafe`). Unlike the earlier source-only package, this contains **10 original images + 90 native source crops + 10 individual master crops + 2 Bubu detail anchors**. Exact cryptographic and pixel-region provenance was checked for all 90 crop assets: see [canon/ALL_90_SOURCE_CROPS_QC_V1_2.json](canon/ALL_90_SOURCE_CROPS_QC_V1_2.json) and [canon/ALL_90_SOURCE_CROPS_MANIFEST_V1_2.json](canon/ALL_90_SOURCE_CROPS_MANIFEST_V1_2.json). Nothing here proves the new AI-generated variant sheets are face-identical.

**Operational hard rule**: In production, only SOURCE_ORIGINAL and verified source-crop references may be used as identity anchors before independent Muse image candidates receive explicit approval. Crop-to-original pixel correctness does not imply full new perspective or wardrobe identity correctness. Never silently consider a new AI-rendered angle APPROVED. CINE local install must pass verification and then code-level resolver/Flow/Muse integration tests before reporting production READY.


### Source-lock v1.2 FINAL — CLI and acceptance

**Authoritative packaged version:** `/CINE/Slow_English_A2/Character_Reference_Packs/CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2_FINAL.zip`, SHA-256 `a9ad67f96ffac90e87dec97f6829b2c7de152514f5f7b61bace90a8f8d05c8c4`. All other v1.2 ZIP variants are intermediate; **use FINAL**.

- `scripts/install_character_canon_into_cine_v1_2.py` validates 10 original SHA-256, 90 original-image crop SHA-256 and Bubu hero/tail anchors before safely installing source files into the CINE worktree; re-running must be idempotent and never overwrite conflicting files.
- `scripts/resolve_canon_source_references_v1_2.py` maps structured per-shot `activeCharacterTags` only to matching source crops, validates exact SHA-256 and selects two Bubu-specific attachments (hero face and spiral-tail sparkle detail). It does **not** fabricate Flow or Muse media IDs, and it does not mark newly generated frames as QC approved.
- `tests/test_canon_source_reference_resolver_v1_2.py`: 8/8 local tests passed (no unknown/duplicate tag, correct Lia+Bubu refs, correct 0-ref landscapes, fail closed if file missing). Importer also verified safe install and idempotent re-run in a mock Git worktree.
- Every shot still requires location-lock refs, real Flow/Muse upload IDs and frame-by-frame visual QC. **CINE local device was offline at this check, so runtime E2E installation and production readiness remain UNVERIFIED.**

`APPROVED_FOR_REFERENCE` is not a synonym for `SOURCE_PIXEL_EXACT`. The source files are user-selected identity truth; they remain 100%-faithful as pixels where cropped, but 10 newly AI-generated sheets and unseen angles remain unapproved.


## Owner visual source package 2026-11-08: mandatory for Bell & Leaf (EP001–EP1000+)

Owner provided 23 reference PNGs in Windows folder SLOW NGLISH PHÙ THUỶ. Consult docs/story/bell_leaf/OWNER_VISUAL_REFERENCE_HANDOFF_20261108.md, config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json and the existing character source lock at config/niches/slow_english_a2/CHARACTER_VISUAL_CANON_LOCK_CURRENT.json before every shot. Do NOT change names, faces, clothing identity, prop shape or locked house appearance.

Official existing CINE location registry .claude/skills/cine-a2-muse-reference-anchoring/integration/config/LOCATION_CURRENT.json now includes owner_source_anchors_20261108 on nine existing BELL rooms, but the multi-view approval_state is still PENDING_NOT_GENERATED. All original one-angle plates and 3 concept boards are inspectable at assets/canon/location_refs/slow_english_a2/bell_leaf/owner_provided_20261108. The 3 collages have alternative façades; never use as production geometry or single independent 16:9 shot images. A huge central bell hall is NOT yet verified as Earth's private newly built fixed station. True camera reverses, night angles, room adjacencies and props still require independent approval.

EP001 reference file docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json has 270 S001–S270 rows; each row gives location anchor path/SHA if supplied, candidate visible character refs and explicit active tags. Shot cast tags are inferred from the screenplay and MUST be human director-verified. Offscreen actors must not receive face refs. AILA has NO owner-approved face: do not invent it. No media upload IDs or video QC PASS have been fabricated. Provider upload and independent image/video validation remain required for each generated shot.

Run python tools/bell_leaf/inspect_visual_reference_20261108.py --require-assets --shot S001 before an EP001 production test; if owner binary assets are absent or SHA mismatches, BLOCK. Native 16:9 one frame, neutral D55 daylight, no subtitles or 9-grid, 10s take with acting/lip-sync, Bix without bell, Bubu with one gold neck bell and permanently sparkling purple spiral tail.

## Owner-art public-repository safeguard (2026-11-08)

Repository huongtina74-ux/cine is PUBLIC. GitHub main contains owner visual registry paths, hashes and code only, NOT the 44 source PNGs. The real owner images are in local CINE and isolated Git commit bc5972e. Do not publish those PNGs or base64/ZIP equivalents to the public repository without explicit owner consent to public release. Remote asset backup requires private authenticated storage; missing binaries on GitHub clone remain a hard production blocker.

## Bell & Leaf Muse 3D animation drift prevention (2026-11-08)

For the exact niche slow_english_a2 / magical_witch_family_stories / bell_leaf ONLY, read docs/story/bell_leaf/MUSE_I2V_PROVIDER_STYLE_CONTINUITY_20261108.md and config/niches/slow_english_a2/i2v_provider_contracts_20261108.json. "Muse" alone does not identify a provider: Meta Muse Video, Fawna Muse and unrelated websites cannot be treated as one model. No remote model/paid generation has been verified or authorized. Before I2V, call tools/bell_leaf/muse_i2v_preflight.py for the exact EP001 shot and first-frame. For 10s video inspection call tools/bell_leaf/muse_i2v_frame_qc.py, which produces only human-review PENDING screenshots at 0/2/5/8/9.7 seconds. Require source face SHA, one standalone approved 16:9 CGI first frame, exact on-screen cast, approved site/space and camera topology, explicit account/model and provider receipt. Never use a 9-grid as the rendered scene frame, even if a third-party model suggests it as a composite identity input. Voice comes from approved fixed WAV, not a VOICE_NAME prompt. Failure on ANY real-human recast, altered Bubu spiral sparkle/one neck bell, Bix added bell, wrong stage geometry or camera-only zoom is a hard rejection. The unrelated generic character examples Mia, Grandpa Walter, Biscuit must never enter the Bell & Leaf prompts. This contract does not modify other CINE subniches or grant production PASS.

## Mandatory Bell & Leaf 3D Prompt Director (2026-11-08)

For magical_witch_family_stories/Bell & Leaf (NOT unrelated generic Slow English/audio), load .claude/skills/cine-bell-leaf-stylized-3d-prompt-director/SKILL.md BEFORE preparing any image or Muse 10-second video prompt. Production prompt compiler: tools/bell_leaf/compile_3d_animation_prompts.py; canonical style/format contract: config/niches/slow_english_a2/stylized_3d_prompt_contract_v1.json. Image must be one independent 16:9 scene with SHA-verified owner face/hero and correct owner location plate; video must animate that approved first-frame with one purposeful 0-2/2-7/7-10s acting arc and genuine moving character (not camera zoom). Cast visible in one shot ONLY, voice-only character references excluded, BIX no bell, BUBU exactly one gold collar bell and continuous sparkling spiral purple tail, no live-action recast or legacy Mia/Walter/Biscuit. Output separate image and video TXT with exactly one prompt line, one blank line between shots. A prompt template or SHA does not authorize I2V: missing angles, Aila face, authorized provider or human visual/voice QC remain BLOCKED.

## Bell & Leaf Memory Hub — mandatory source bootstrap (2026-11-08)

For the exact \`bell_leaf / magical_witch_family_stories\` series, load \`.claude/skills/cine-bell-leaf-memory-hub/SKILL.md\` and **run** \`python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage story --out data/story_quality/<unique>.json\` before writing, reviewing or changing any new scene. For artwork/shot prompts run the same tool with \`--stage image --shot S001\` (or \`video\`) and load ONLY that shot's active face/body and location references. For EP002+ use \`--stage next --episode BL-0002\` first, then story-uniqueness gates. This integrates existing source-of-truth owner Canon, prior episode states, used plot events, Skills, character and location imagery by source/hash; do **not** duplicate their rules or treat historical v1.1 270-shot draft as v2 production script. Story, character face, location reverse angle and video QC approvals remain separate and not automatic. Missing source or conflicting state is BLOCKED.

## Bell & Leaf HaoHao source-reference runtime supplement (2026-11-09)
Before composing or reviewing Bell & Leaf I2V, load `../cine-bell-leaf-stylized-3d-prompt-director/references/MUSE_HAOHAO_OPERATING_STANDARD_20261109.md`. It clarifies that HaoHao's `@name` attaches all matching character and location images, while the app may strip `@` from the Muse-visible text. A name tag does not lock pixels or facial identity. Isolate one verified original-source facial anchor, one approved outfit/angle and only the needed location plate; fail closed on multi-panel collage references, nonexistent reverse-angle plates, nonmatching names, and unverified SHA. Keep this skill's original Canon hash/angle approval requirements as highest authority.
