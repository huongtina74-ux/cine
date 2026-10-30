---
name: cine-a2-fixed10s-asset-bridge
description: Production-asset audit/queue gateway for Bell & Leaf / Slow English A2 v1.1 STRICT 10-second skillpack. Resolves original character identity, 12 location concepts and 1,239 location/prop view targets without false approval.
---

# CINE Slow English A2 v1.1 — FIXED 10S Asset Integration Bridge (R2)

**Hard rule:** This skill NEVER claims that a prompt, a concept sheet, a source crop, or a successful queue/test means an independent 16:9 image was generated and visually approved. Production must fail closed until original evidence and human acceptance exist.

## Source archives, canonical registries and actual coverage

- Exact source registry: `.claude/skills/cine-bellfern-location-multiview-lock/registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json`: 12 sites, 69 spaces, 108 props, DRAFT topology. Do not replace with the invented floorplans in concept sheets.
- `LOCATION_MULTIVIEW_MANIFEST.csv`: **483/483 PENDING_NOT_GENERATED** at audit time.
- `PROP_MULTIVIEW_MANIFEST.csv`: **756/756 PENDING_NOT_GENERATED** at audit time.
- Source character archive: 10 user-uploaded reference sheets and 90 verified exact source pixel crops, in the user's private Library. New render/view identity checks are NOT completed. Do not promote generated face variants as canon.
- Concept sheets: 12 user-facing location composites available but **not** independent plates or physically correct plans; retain them as `CONCEPT_DRAFT` only.
- Future video/voice: fixed 10.0s per shot is user production policy, NOT proof of an actual Meta Muse video API contract; approved voice WAV, voice licensing, sync and actual output must be checked.

## Required A2 eight-skill handoff

1. `cine-a2-orchestrator`: run `audit_and_import.py`, check source and approved evidence before calling generation workers.
2. `cine-a2-script-director`: output scene site_id/space_id and only visible character tags; do not let screenplay mention of other people trigger extra refs.
3. `cine-a2-shot-director`: each planned shot exactly 10.00 seconds, physical camera direction, real reverse angle; no 3–9 sec padding/zoom.
4. `cine-character-continuity`: original images > human-approved perspective-specific images > prompt; 10 tags `bo, me, juno, Lia, bubu, bix, ongngoai, bangoai, ongnoi, banoi`, with the original nine core and `bangoai` conditional. **Bubu has spiral glittering magical tail** at all angles and one collar bell. **Bix has NO bell**.
5. `cine-voice-performance`: approved speaker WAV/transcript per speaking character, US English A2 performance; no voice consistency claim based solely on text prompts.
6. `cine-muse-image`: one 16:9 **standalone still per asset**, never a collage, poster, subtitles or watermark; natural D55 / approximately 5500 K neutral color, no global yellow/orange wash. One prompt one uninterrupted line, precisely one blank line separating shots/jobs.
7. `cine-muse-video`: image-to-video 10.0s using approved first-frame reference; expressive character animation, not camera-only zoom; lip sync only where provider truly supports the user-authorized audio. Inspect actual rendered video/metadata.
8. `cine-a2-production-qc`: verify source SHA, real output SHA, 16:9, non-panel output, position of doors/windows/stairs/props, faces/body proportions, timing, spoken voice WAV, independent human sign-off. Mock/test passes do not imply visual approval.

## Location exceptions — mandatory repair before production promotion

- `BELL`: attached EAST workshop and chamber below workshop; reject the old sheet showing workshop as attic.
- `BRIDGE`: registry ONE true arch; reject multiarched redesign.
- `POST`: small one-storey + attic building with blue entrance, not large multi-floor mansion.
- `LAKE`: old small gray boathouse, one rowboat and simple dock; old concept sheet's `Moonwater` label should not override Bellfern canon.
- `SCHOOL`: ordinary Earth community school, not ornate magic academy.
- Remaining locations: check exact source registry's topology, floors, directional geography and prop anchors before approving.

## Reusable work order and validator files

The companion **production ZIP** in the user's private Library:
`/CINE/Slow_English_A2/Fixed_10S_Asset_Bridge/CINE_A2_FIXED10S_ASSET_BRIDGE_R2_FULL.zip`.

Inside this ZIP:
`source_snapshots/`, `source_archives/`, `queue/FLOW_483_LOCATION_ONE_LINE_BLANK.txt`, `queue/FLOW_756_PROP_ONE_LINE_BLANK.txt`, `queue/ALL_1239_ASSET_WORK_ORDERS.jsonl`, `scripts/build_asset_queue.py`, `scripts/audit_and_import.py`, `scripts/run_queue_sequential.py`, `config/CINE_A2_FIXED10S_REFERENCE_BINDING.json`, `tests/`.

Run build, audit and dry-run before any provider calls. The queue's `PENDING_NOT_GENERATED` state is truthful. Actual vendor image generation requires authorized CLI/API, individual review, geometry validation and approval; **do not call any provider or spend credits without user-authorized access and budget**.

No hidden installation claim: the user's Windows CINE machine was OFFLINE at this audit. GitHub PR #2 Location Lock and PR #3 Character Lock remain DRAFT and unmerged. This R2 skill can coordinate their future integration after review and actual asset import; do not mark the desktop runtime ready from this GitHub commit alone.

## Blocking production conditions

- Original character SHA mismatch or missing => `BLOCK_CANON_SOURCE`.
- Active character missing approved identity and perspective => `BLOCK_CHARACTER_REFERENCE`.
- Location/prop without approved plate and documented topology => `BLOCK_LOCATION_REFERENCE`.
- Missing approved voice WAV for speech => `BLOCK_VOICE_REFERENCE`.
- Provider produces collage, embedded subtitles, yellow wash, altered face, mismatched geometry => `REJECT_VISUAL_OUTPUT`.
- 10s actual video not verified => `BLOCK_MUSE_VIDEO`.
- Never invent a file path, media ID, voice identity, or APPROVED status.

**End-to-end green production readiness is not yet achieved.**

## Unified CINE niche path (2026-10-30)

The active production profile for this original CINE repo is `config/niches/slow_english_a2/production.json`. The Python runtime preflight is `cinefactory/studio/slow_english_a2.py`; the 10s character/space/prop/voice gates use the real CINE canonical registries. **Do not create new `CINE_*` projects**, do not treat `source_snapshots/` as authoritative, and do not install unreviewed concept sheets as production plates. PR #4 consolidates PR #2 and PR #3 content pending review; 10 source identity sheets are held privately with hash checks, not embedded here. This project remains NOT PRODUCTION READY until actual assets are reviewed and the existing Studio runner is wired and verified end-to-end.
