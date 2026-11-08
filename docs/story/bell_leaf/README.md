# Bell & Leaf — Production Story Hub

## EP001 family-first story memory — MANDATORY FOR EVERY LATER EPISODE (2026-11-08)
- [Full 30-scene v2 dramatic story reference](ep001_screenplay/EP001_STORY_V2_MASTER_30_SCENES.md) — exact 00:00–45:00 order, story detail, character decisions, dramatic turns and candidate A2 dialogue. **Authoritative for episode plot development**, subordinate to four original owner source texts.
- [Machine-readable EP001 v2 continuity lock](ep001_screenplay/EP001_STORY_V2_CONTINUITY_LOCK.json) — 30 unique incidents, 11 seeded/payoff motifs, unclosed mysteries, cast/world/prop state at EP001 end, do-not-repeat combinations, visual/audio holds.
- [Current story-quality plan v2](ep001_screenplay/EP001_STORY_QUALITY_PLAN_v2.json) — 15 causal beats, 30 chronologically aligned scene cards; v1 quality plan was Veylora-first and is **legacy only**.
- [Episode story memory registry](EPISODE_STORY_MEMORY_INDEX_V1.json) — BL-0001 reserved incident fingerprints; prevents future episodes replaying the same incident as new.
- **Before EVERY future Bell & Leaf pitch:** run \`python tools/bell_leaf/ep001_story_memory_gate.py verify\` and \`python tools/bell_leaf/ep001_story_memory_gate.py check-candidate --candidate YOUR_EPISODE.json\` (requires the declared inherited state, unique event IDs and source novelty claims). BLOCKED means stop; MANUAL_NOVELTY_REVIEW_REQUIRED still requires human editor and comparison to full previous scripts/1000 proposal slate. Do not declare artistic uniqueness solely from code.
- **EP001 v1.1 shooting draft** remains 270 allocated 10s shots but the **v2 scene-level dramatic treatment is not a freshly shot-timed 270-slot v2 teleplay**. Do not blindly launch batches before one-to-one shot/story reconciliation and asset/voice QC. This is a story-reference lock, NOT media production approval.


**WRITERS' ROOM: OWNER SOURCE-BOUND ENTRYPOINT (2026-11-07).** Read these in order BEFORE writing any Bell & Leaf episode:
1. [Writer Canon Contract](BELL_LEAF_WRITERS_ROOM_CANON_CONTRACT_V1_20261107.md) — authoritative owner-source interpretation and invariant rules.
2. [Owner-source Conflict Register](BELL_LEAF_OWNER_SOURCE_CONFLICT_REGISTER_20261107.md) — explicit resolution / pending-owner decisions.
3. [Writer Workflow SOP](BELL_LEAF_WRITERS_ROOM_SOP_V1_20261107.md) — 12-stage script pipeline, handoffs and per-shot prompts.
4. [Machine-readable writer contract](../../../../config/niches/slow_english_a2/bell_leaf_writer_contract_v1.json) and [Claude skill](../../../../.claude/skills/cine-bell-leaf-writers-room/SKILL.md).

**1,000 EPISODE DEVELOPMENT REGISTRY — UNAPPROVED:** [full 1,000-card draft](slates/BELL_LEAF_1000_EPISODE_DEVELOPMENT_SLATE_UNAPPROVED_20261107.md) + [CSV 1,000-ID proposal index](slates/BELL_LEAF_1000_EPISODE_INDEX_PROPOSAL_20261107.csv). These are NOT 1,000 screenplays.
**ANTI-REPEAT / RESEARCH EVIDENCE:** [reality audit + unresolved gaps](BELL_LEAF_DUPLICATE_RESEARCH_COVERAGE_AUDIT_20261107.md); run `python tools/bell_leaf/episode_uniqueness_gate.py audit` and for every episode `python tools/bell_leaf/episode_uniqueness_gate.py check --candidate PATH_TO_PITCH.json` BEFORE draft/lock. Automated result never constitutes final editorial approval.

**OWNER'S FOUR SOURCE TEXTS:** Full originals are retained locally in Git-ignored data/story/bell_leaf/owner_sources_private/20261107. These owner-provided sources are not automatically published to public GitHub. New AI writers cannot substitute unsupported guesses for missing private materials.

**LEGACY CURRENT CANON:** [BELL_LEAF_CANON_CURRENT.md](BELL_LEAF_CANON_CURRENT.md) v4.8 is supporting prior consolidation, but owner-supplied four-source package dated November 7 has precedence where the two conflict (notably trial old/new/Earth/mixed episode distribution). No automatic retcons; disputed new details require owner decision.

**A2 production entrypoint:** [SERIES_BIBLE.md](../../../../config/niches/slow_english_a2/SERIES_BIBLE.md) supports Bell & Leaf in the unified Slow English A2 niche; never import generic audio-story rules or competitor canon.
**Voice:** [VOICE_BIBLE_CURRENT.md](../../../../config/niches/slow_english_a2/VOICE_BIBLE_CURRENT.md) and registry; voice-casting candidates are NOT approved speaker masters.
**Art:** [Character Visual Canon](CHARACTER_VISUAL_CANON_LOCK_CURRENT.md) and on-device SHA-backed original reference manifest; nine core identities plus supporting Elara. No approved new face can be inferred from the script.
**EP001 trailer:** [trailer/ep001_180s/](trailer/ep001_180s/) contains 18 × 10-second Flow/Muse prompt sources, not an accepted 45-minute screenplay or finished video.
**Working support:** v4.0–v4.8 proposals, atlas, magic ecology, villain psychology only where consistent with the four owner originals.
**Retired:** [_archive/pre_v4/](_archive/pre_v4/) is history, not input for new production.
**Private showrunner:** real masked-opponent identity, secret reveals and ultimate solution remain in local confidential owner source. Do NOT publish to public GitHub, images/video-provider prompts, or trailer material.
**Production:** Story approval alone never establishes voice/art/Muse 10-second I2V/lip-sync QC approval or YouTube upload permission.

**Required test:** python -m pytest -q tests/test_bell_leaf_writer_contract_20261107.py

## Bell & Leaf Memory Hub — mandatory source bootstrap (2026-11-08)

For the exact \`bell_leaf / magical_witch_family_stories\` series, load \`.claude/skills/cine-bell-leaf-memory-hub/SKILL.md\` and **run** \`python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage story --out data/story_quality/<unique>.json\` before writing, reviewing or changing any new scene. For artwork/shot prompts run the same tool with \`--stage image --shot S001\` (or \`video\`) and load ONLY that shot's active face/body and location references. For EP002+ use \`--stage next --episode BL-0002\` first, then story-uniqueness gates. This integrates existing source-of-truth owner Canon, prior episode states, used plot events, Skills, character and location imagery by source/hash; do **not** duplicate their rules or treat historical v1.1 270-shot draft as v2 production script. Story, character face, location reverse angle and video QC approvals remain separate and not automatic. Missing source or conflicting state is BLOCKED.
