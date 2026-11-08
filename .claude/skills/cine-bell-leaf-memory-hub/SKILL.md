---
name: cine-bell-leaf-memory-hub
description: Source-bound memory bootstrap for every Bell & Leaf story, episode script, image, video, scene and shot. Never invent Canon or promote unreviewed drafts.
---

# CINE Bell & Leaf — Single-Source Story/Character/Location Memory Hub

## Mandatory FIRST action, before any creative generation
- Identify the exact series: `bell_leaf` / `magical_witch_family_stories`. Never apply the Bell family Canon to other Slow English A2, history, science or senior-audio channels.
- From the CINE root run `python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage story --out data/story_quality/BL0001_story_context_<unique>.json`. Read the resulting context **in full before composing**, especially all 30 scene cards, current owner contract, EP001 end-state, unresolved mysteries and protected 30 events. Never substitute ChatGPT conversation memory for this immutable source set.
- For individual first frames and videos, run `python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage image --shot S001 --out data/story_quality/<unique>.json` (use `--stage video` for animation); use exactly the *shot's* active tags and the original media paths/SHA; do NOT attach every character in its scene.
- For an episode not yet written (e.g., BL-0002), run `python tools/bell_leaf/story_memory_resolver.py --stage next --episode BL-0002 --out data/story_quality/<unique>.json`; inherit BL-0001 end state and check all 30 protected event IDs before pitching anything new. This is NOT an approval of a nonexistent episode.
- Each command produces an auditable digest list of actual source files; it exports public Canon and episode memory but NEVER copies owner's four private full texts or private villain identity into public files.
- If Canon/episode/scenes/shot-source is missing or contradictory, **HALT**. Do not synthesize from memory or source another episode's layout.

## Authority and continuity
1. Owner's four confidential full originals (local restricted) + public owner contract outrank all earlier series proposals.
2. Current `BELL_LEAF_CANON_CURRENT.md` + writers-room SOP/conflict register; never resurrect pre-v4 known-Earth / arbitrary portal retcons.
3. `EP001_STORY_V2_MASTER_30_SCENES.md` and `EP001_STORY_V2_CONTINUITY_LOCK.json` are EP001 *writer-reference*, not an approved screenplay. The 270-slot v1.1 shooting document is HISTORICAL, and must be rewritten against the v2 30 scene cards. Do not use it to replace newer plot.
4. `CHARACTER_VISUAL_CANON_LOCK_CURRENT.json` + `OWNER_VISUAL_REFERENCE_BIBLE_20261108.json` are image/geometry sources. The original character sheets and one-angle location plates have SHA references, but no generative-video identity guarantee.
5. `EPISODE_STORY_MEMORY_INDEX_V1.json` records used plots and warns of BL-0003 "Aila's Flying Suitcase" collision; 1000-card slate remains UNAPPROVED development pitches.
6. Future episodes are appended to the episode memory registry only after actual human creative and owner approvals, never invented by an agent or simulated tests.

## Department routing; don't duplicate underlying Canon
- Research: `cine-per-niche-radar` → `cine-story-insight-transfer`.
- Story and original script: `cine-bell-leaf-writers-room`, `cine-story-quality-memory`, `cine-script-factory`, `cine-script-doctor` and independent review.
- Image: `cine-bell-leaf-stylized-3d-prompt-director` + `cine-bellfern-location-multiview-lock`.
- Video 10s: `cine-a2-muse-reference-anchoring`, 10s image-to-video with **real physical character motion**, no camera-zoom-only, no 3x3 grid, no real-human conversion.
- Scripts and stage Skills refer to this hub for retrieval, then refer to the owning Canon files for rules; never copy character inventories or rewrite the lore in the Skills themselves.

## No false acceptance
- `production_authorized:false` is permanent for a memory-bundle alone.
- A missing original PNG, unapproved supporting Aila face/voice, single-view location lacking reverse angle, invalid scene/shot tag, or unapproved V2 shooting script is a HOLD.
- Do not say "we locked all 1000 episodes" or "1000 screenplays are original" based on an outline or lexical similarity test.
- `--verify` checks structure and linkage, NOT the script's artistic quality or Muse visual identity.
