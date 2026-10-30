# CINE niche hierarchy — Bell & Leaf

**Single CineFactory repository** `huongtina74-ux/cine`. **Hierarchy: Slow English (parent) → Slow English A2 (level/format) → Magical Witch Family Stories (subniche / chuyện gia đình phù thủy) → Bell & Leaf (one original series).**

This classification is binding for research cohorts, screenplay/story canon, voice and visual registries, shot preflight, production QC, packaging and Analytics. **Bell & Leaf does not represent every Slow English or Slow English A2 project**; future non-magical A2 stories or other learning formats must remain separate within the same company.

**Do not rename** existing `project_id=slow_english_a2_bell_leaf`, `niche_id=slow_english_a2`, folder or character/location voice reference IDs: those are stable backward-compatible operational identifiers. `subniche_id=magical_witch_family_stories` differentiates the actual storytelling segment. Comparisons must use the subniche cohort as the direct baseline, treating generic Slow English only as adjacent market context.

# Slow English A2 / Bell & Leaf — canonical CINE niche

One repository: `huongtina74-ux/cine`. This is an in-repo niche configuration, **not another CINE project**. It reuses the existing Studio Kernel, Project DNA, research, writers, director, production design, audio, QC, publishing and analytics departments.

See `production.json` for exact source paths and readiness. This directory owns only the niche/series configuration; it does not clone the character/location/prop registries or the 1,239-image queue. The canonical location/prop registry is the existing `cine-bellfern-location-multiview-lock/registry`, and the original character identity lock is `cine-a2-muse-reference-anchoring/canon`.

Current truthful status: 10 approved-original character identity sources and 90 source crops in a private CINE asset ZIP, **not yet installed in Windows CineFactory**. AI-generated new angles are NOT approved. Location/prop manifests still have 483+756 pending views and 0 human-approved images. Muse 10s I2V, face continuity across generated views, WAV identity and lip sync are not end-to-end verified.

Every scene uses explicit `activeCharacterTags` only, `location_id`, `space_id`, `location_view_id`, `duration_seconds: 10`, optionally `activePropIds`, `dialogue`. A scene with no people has `activeCharacterTags: []`. The CINE runtime must never derive visible characters by scanning the entire prompt, guess missing media IDs, add a narrator or label a contact sheet an approved frame.

Use `cinefactory.studio.slow_english_a2.BellLeafCanon` for verified source reference routing. Flow first frames and Muse video prompts remain separate; image prompts must be one physical line each with exactly one blank line between jobs. Raw frames 16:9 full-bleed; no subtitles, text, contact sheets or global amber grade. Voice must use a rights-cleared approved WAV per speaker; lipsync provider capability must be verified with actual media.

Historical PR #2 Location and PR #3 Character were superseded by PR #4, which was merged into main; PR #5 added the ten voice casting descriptions. Physical multi-view plates and approved WAVs remain outstanding.

## Official Master Skill

One entrypoint for Bell & Leaf research-to-script: `.claude/skills/cine-script-factory/SKILL.md`. To resume existing CINE episode work: `python tools/cf_a2_master_skill.py next --id EPISODE_ID`; after an agent actually creates the specified artifacts, run `record`, then the original Script Factory human-reviewed stage gate. This is one CINE workflow, not another project.
