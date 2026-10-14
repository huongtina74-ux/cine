# CineFactory Maizen v262 — G02 source QC & original preproduction continuity

Date: 2026-10-11. Status: **STRUCTURAL_SOURCE_QC_COMPLETED; SEMANTIC_G02_BLOCKED; DESK_PREPRODUCTION_ONLY**. No rendered video, asset licensing, production approval or publication.

## Evidence first
Owner's 3 previously collected original YouTube Chrome-player captures from `.tools/maizen_peer_av_v260/` were checked using `cinefactory/studio/maizen_source_structural_qc_v262.py`, not by title/VTT alone.

| Video | Source runtime | Browser segments | 30s QC windows | Source frames | Decodable hashed audio files | Windows requiring source checks |
|---|---:|---:|---:|---:|---:|---|
| Mine Block [RjyeHZ5hSaE](https://www.youtube.com/watch?v=RjyeHZ5hSaE) | 26:01 | 42 | 53 | 205 | 42 / 42 | 6 |
| JJ Cartoons [7jgzaEmqVQU](https://www.youtube.com/watch?v=7jgzaEmqVQU) | 22:34 | 36 | 46 | 177 | 36 / 36 | 3 |
| MSToons [qtWfSIqNfdU](https://www.youtube.com/watch?v=qtWfSIqNfdU) | 10:13 | 17 | 21 | 81 | 17 / 17 | 2 |
| **Total** | **58:48** | **95** | **120** | **463** | **95 / 95** | **11** |

The old browser receipt reported 0 seam gaps using its own threshold; detailed per-window checks found small positive time gaps (roughly 0.31–0.47 s) plus the first ~0.8–1.1s not covered and tail windows without frames. **Do not claim gap-free coverage or continuous frame-by-frame watching.** Machine decode is technical integrity, not listening / song / SFX / dialogue comprehension. Source sound was captured while Chrome played at 2×, **not independently listened at original speed**. All 120 windows retain `independent_native_audio_semantic_review=PENDING`; full moving-picture semantic QC also PENDING. An independent qualified reviewer must review every original film fully and sign G02 before competitor-derived production methods are certified.

Exact reviewed-window evidence is local-only: `data/verification/v262_maizen_source_structural_audit/thirty_second_windows.json`; originals/sampled browser captures under private `.tools/` are not committed.

## New major creative continuity defect caught
`v243` contains two internally inconsistent original planning artifacts. The 21-beat 14-minute MAI01 Waterfall story opens:
- B01 00–15 sec: distant amber pulse and wet sketch seen **not collected**
- B02 15–32 sec: Pip collects sketch at river rock shelf
- B03 32–50 sec: broken bridge versus safe ridge choice, **no cave entry yet**
But the old 9-shot 45-second pilot already had characters inside a cave, placing torches, sealing a passage, and finding a different map in a chest. That cannot be the first 45 seconds of the main episode without teleport / prop duplication.

A **new v262 original-IP pilot revision** keeps exactly 9 shots × 5 sec, preserving source v243 unchanged:
- P01–P03 (0–15): waterfall amber mystery, Nova/Pip reactions, sketch glimpsed by river but unowned
- P04–P06 (15–30): Pip retrieves sketch, sees three dots, Nova voices caution
- P07 (30–35): both move to broken bridge fork **at time 32 sec beat boundary**
- P08–P09 (35–45): bridge shown unsafe, Nova points to safer stones, choice remains unresolved until B03 finishes at 50
Output `data/verification/v262_maizen_story_alignment/corrected_pilot_and_continuity.json`. **Original 9 shots not rendered. Revised voice is scratch original writing, not recorded, script not locked.**

Eight additional 14-minute continuity fixes are recorded without silently changing the original immutable beat sheet: three build blocks and inventory spent, two door IDs, blue–amber–blue valve-code foreshadowing, hook prop preplant, physical workshop drain → relief grate connection, route to retrieve map, valve reset panel access, map on shelf and lower tunnel still locked at sunset.

## 26-room company handoff — dependent phases
1. **EVIDENCE, QC, INTELLIGENCE:** review source at original playback speed, correct 11 flagged windows; write native audio/music/SFX, visual motion and causality findings into each 30-second case record. Until independent G02 signoff, no competitor production stack claim.
2. **WRITERS_ROOM, SCRIPT_LOGIC, CREATIVE_STRATEGY, DIRECTION:** apply v262 eight continuity amendments to an original revised draft, complete human-reviewable natural VO and causal logic, verify 45-second pilot matches 14-minute act. No "script locked" claims.
3. **PERFORMANCE, CINEMATOGRAPHY, PRODUCTION_DESIGN, ASSETS, RIGHTS:** storyboard revised 9-shot plan, world route/river/gate mechanism, brand-distinct Nova/Pip rigs and original source license matrix. No asset yet certified.
4. **TECHNICAL_DIRECTION, RND, OPERATIONS, PLANNING, PRODUCTION:** compare *same original 45s/9 shots* in licensed Minecraft runtime vs Blender once real software paths, gameplay rights, G02, character assets and owner production permission are documented. Machine preflight RTX3060 12GB + FFmpeg found; Blender missing from PATH is not proof of absent installation.
5. **AUDIO, EDITORIAL, COLOR, VFX, GENERATIVE_MEDIA:** original voice/ambient/water/foley plans, EDL, lighting continuity; actual mixed audio/render **not created**.
6. **STUDIO_MANAGEMENT, PACKAGING, ANALYTICS, RD_KNOWLEDGE:** decide original series release/packaging only after playable media acceptance, independent reviewer, and all rights; do not invent RPM, CTR or retention.

The company must keep **Minecraft Gameplay and Voxel Animation separate**. Format and method selection remain hypotheses until benchmarked with measured accepted seconds/hour, fixes, 1080p24 QC, native audio, actual VRAM, game runtime license and signed asset provenance.

### Acceptance checkpoint
- G01: market research sample sufficient for **candidate ranking**, not full-channel exhaustive exploration.
- G02: **BLOCKED**, all 120 windows structurally indexed, 11 require additional source review, independent native video+audio approval missing.
- G03–G04: **PROVISIONAL**, age-matched outliers and new-channel strict two-million condition unresolved.
- G05–G15: **DESK_PREPRO_REVISION** only; 9-shot original scene alignment corrected, 8 unresolved amendment notes.
- G16–G28: **HOLD**, no media created or permission to publish.
- Zero external paid credits, no copying of Maizen/JJ/Mikey/Spider-Man skins/voices/music or images into produced film, no uploads.
