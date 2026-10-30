# Slow English A2 / Bell & Leaf — canonical CINE niche

One repository: `huongtina74-ux/cine`. This is an in-repo niche configuration, **not another CINE project**. It reuses the existing Studio Kernel, Project DNA, research, writers, director, production design, audio, QC, publishing and analytics departments.

See `production.json` for exact source paths and readiness. This directory owns only the niche/series configuration; it does not clone the character/location/prop registries or the 1,239-image queue. The canonical location/prop registry is the existing `cine-bellfern-location-multiview-lock/registry`, and the original character identity lock is `cine-a2-muse-reference-anchoring/canon`.

Current truthful status: 10 approved-original character identity sources and 90 source crops in a private CINE asset ZIP, **not yet installed in Windows CineFactory**. AI-generated new angles are NOT approved. Location/prop manifests still have 483+756 pending views and 0 human-approved images. Muse 10s I2V, face continuity across generated views, WAV identity and lip sync are not end-to-end verified.

Every scene uses explicit `activeCharacterTags` only, `location_id`, `space_id`, `location_view_id`, `duration_seconds: 10`, optionally `activePropIds`, `dialogue`. A scene with no people has `activeCharacterTags: []`. The CINE runtime must never derive visible characters by scanning the entire prompt, guess missing media IDs, add a narrator or label a contact sheet an approved frame.

Use `cinefactory.studio.slow_english_a2.BellLeafCanon` for verified source reference routing. Flow first frames and Muse video prompts remain separate; image prompts must be one physical line each with exactly one blank line between jobs. Raw frames 16:9 full-bleed; no subtitles, text, contact sheets or global amber grade. Voice must use a rights-cleared approved WAV per speaker; lipsync provider capability must be verified with actual media.

Historical PR #2 Location and PR #3 Character files are consolidated into the existing PR #4 branch. After a reviewed unified merge, the original PRs should be closed as superseded instead of merged again.
