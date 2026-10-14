# CINEFACTORY OS — UNIVERSAL MULTI-NICHE MEDIA COMPANY MASTER PLAN V2

**Date:** 2026-10-09  
**Status:** PLANNING ONLY, NOT IMPLEMENTED OR PRODUCTION CERTIFIED  
**Repository baseline:** studio/v1.6.6-universal-company; 1.6.30 last confirmed 744 full pytest passed, release for detector still BLOCKED.  
**Hard requirements:** Local-first/free-first, no automatic paid API usage, RTX3060 12GB, preserve existing work and APIs, model/tool license review, production evidence, fail-closed gates, self-QC, shot-level repair. No claim of Disney-level output without viewer/expert evidence.

## Mission and operating principles

CineFactory will be an autonomous multi-domain media company, not a Blender-centric renderer. Any new project may start from a niche, script, competitor/style reference, prompt, reference image or video, or owned footage. Every new niche gets researched and validated; every scene/shot gets its own production method chosen from **actually executable** tools. Unavailable or unlicensed tools are candidates, not production solutions. The user/rights owner authorizes any external connections, software installs, paid subscriptions and publishing.

Reuse existing foundations: `cinefactory/studio/niche_os.py` (`NicheManifest`), `production_conference.py`, `scene_conference.py`, `production_method_switch.py`, `capability_acquisition.py`, `capability_execution_lab.py`, `production_economics.py`, `shot_routing.py`, `professional_company.py`, block animation and v1.6.30 real-rig detection. Extend, don't rewrite these systems.

## Eight specialized production studios

| Studio | Niche examples | Audio/visual engine options | Key domain QA |
|---|---|---|---|
| 1. 3D Characters/Animation | Minecraft Maizen BigSchool, Roblox, animal LooZoo-like, cinematic animals | Blender 4.5 persistent workers, licensed rig libraries, Godot/Unreal optional | face expression, character ID, body motion, camera, eye lines, rig collision, continuity |
| 2. Preschool Musical Animation | 3D educational family songs in *genre* of CoComelon (original IP only), ABC/counting/nursery music | Blender organic rigs with shapes/morphs, Music Production DAW/MIDI, TTS/authorized singers, video compositor | learning goal, age appropriateness, beat/syllable/music-mouth choreography, child-safe action, music rights |
| 3. Game/Simulation | Long Slices animal sliding, obstacles, racing, procedural physics, authentic gameplay/GTA | Godot/Unity/Unreal for real-time runtime, Blender animation and physics offline, screen recorder FFmpeg | playable and stable physical path, camera following, obstacle collisions, game/access rights |
| 4. AI Cinema | family drama with fictional characters, short cinematic montage, visual fantasy | ComfyUI locally conditional on model/VRAM/workflow qualification; 3D hybrid; FFmpeg | character continuity, composition consistency, morph artefacts, material permissions |
| 5. 2D/Motion | English lessons, explainers, infographic, cartoon cut-outs, educational visuals | Blender Grease Pencil, OpenToonz, Remotion where license permits, SVG/canvas/FFmpeg | legibility, timing, correct terminology, typography, motion readability |
| 6. Audio/Story/Music | long audio stories, senior-friendly narratives, sleep ambience/rain/white noise, ASMR audio | DAW/audio.cpp/local TTS tools, FFmpeg, licensed audio captures, music generation only if licensed | intelligibility, accents, loudness, loop clicks, transient distortion, repetitions, rights |
| 7. Real Footage / Capture | silent fishing, hand ASMR, authentic ambient/live capture | Real camera/mic, OBS, audio restoration, DaVinci Resolve if executable, FFmpeg | recording authenticity, noise, stabilisation, consent/property rights, capture failures |
| 8. Editorial / Localization | all genres | FFmpeg, Remotion where permitted, Resolve when installed/certified, captions, QA | audio peak, frame quality, encodes, localization consistency, metadata and delivery |

**Production/studio distinction:** Departments are workflow-specialist divisions, not commitments to install all listed engines. Different niches may use the same studio and engines but distinct grammars/tests. Quality and copyright compliance matter more than superficial resemblance to a reference brand.

## Preschool musical animation specialty (new)

Full production sequence:
1. Early Childhood Curriculum (age band, single learning objective, educational correctness, positivity/safety)
2. Original Character Universe Bible (legally distinct characters, age/speech/actions, color/identity & family bonds)
3. Songwriting Studio (rights ledger, melody, lyric, structure, tempo/time signature, accompaniment)
4. Music arrangement & dry vocal recording (master stems, timing, syllable and acoustic phoneme alignment)
5. Story-beats synchronized to each bar (storyboard/animatic, choreography action blocks)
6. Original organic character & facial rigs (shapes/blend shapes, eyes, brows, mouth phonemes, hands, hair/clothes)
7. AnimationClip library (walking, hugs, cooking, brush teeth, dance/wave, prop handling)
8. Lighting/set designer (pleasant, readable colors, eye-safe movement, clear visual instructional cues)
9. Rig performance/beat/viseme stage and final 3D render
10. Educational, child safety, animation, sound, rights and Made-for-Kids audit
11. Editing+localization+versioned export, human editorial sign-off

Music-first chronology: compose tempo/lyrics/vocals BEFORE expensive character animation so scenes follow audio. Do not assume a phoneme forced aligner verifies the sung words; ASR and a reviewer must check. Never use CoComelon trademarks, distinctive copyrighted characters or proprietary audio/arrangements as assets.

## Niche Intelligence and Research Conference

For every niche:
- Market intelligence: language/regions, evergreen versus trending, views/channel age, video length, competing formats, saturation, audience, RPM hypothesis backed by evidence (never fabricate).
- Content DNA: video structure, hook/retention, recurring characters, storyboard density, voice/music ratio, environment, style grammar, editing cadence.
- Asset requirements: existing controlled IP, rights licensed assets, procedural generation feasibility, human footage needed.
- Technical feasibility: quality bar, quality failures, tool readiness, VRAM, runtime, render resolution/time, measured cost per minute.
- Policy/rights: source analysis permission; no unlicensed replication; Made-for-Kids/YouTube low-quality inauthentic and content safety gates.
- Output `NicheOpportunityReport`, `NicheCapabilityGapReport`, `NicheRecipe` (versioned), priorities and blockers.

New niche is not ACTIVE until a golden short clip renders end-to-end, an independent eval passes, all licenses cleared for selected components, and a human has reviewed creative quality.

## Universal production router — per-SHOT decision and fallback

INPUT -> `ProjectDNA` -> `NicheManifest` -> Research and Legal -> Editorial Plan -> `SceneIntent` -> `ShotSpec` -> `CandidateMethodSet` -> Feasibility Trial -> `ExecutionPlan` -> Run -> QC -> Shot repair -> Assemble.

Hard filters BEFORE scoring:
1. Rights/policy and expected child-safety constraints.
2. Tool availability: actually installed/executable, adapter functional, local checkpoint present, supported format, plugin connection granted.
3. Hardware cost/capacity: RTX3060 12GB, peak VRAM, GPU use, duration, memory leak/resume.
4. Required style continuity, identity, exact camera/physics/phoneme/beat sync, if applicable.
5. Auditable outputs and deterministic/provenance metadata.

Among survivors, score measured `visual_quality`, `audibility`, `continuity`, `budget`, `runtime`, `reproducibility`, `repairability`, `workflow_reuse`. Weights vary by niche and shot objective. Save all candidates, failed veto reasons, measured estimates and chosen model/adapter/checkpoint version. If no valid method -> BLOCKED_ACQUISITION, do NOT silently choose Blender or paid API.

Sample:
- Preschool singing close-up -> Blender organic facial rig + vocal/beat timeline; fallback change animatic, not unstable AI face.
- Preschool colorful establishing shot -> Blender reusable scene or ComfyUI if copyright and consistency validated.
- Real-time Long Slide physics -> Godot runtime with deterministic seed, Blender assets/camera if justified.
- Live GTA gameplay -> authorized gameplay recording rather than Blender pretending to run the actual game.
- Rain sleep -> source-licensed clean ambience, non-repetitive loop QC, simple low-flicker visual.
- Story narration -> voice-first full audio master with sound/longform/editorial; Blender optional.

## Capability Registry 2.0 / tool research engine

`CapabilityManifest` per tool and model:
`tool_id, version, source_url, license, legal_status, install_status, executable_test, adapter_version, formats, performance_profile, vram_measured, cost_per_unit, required_human_approval, benchmark_ref, capability_tags, qualification_status, update_policy`.

Statuses: DISCOVERED -> LICENSE_REVIEW -> ISOLATED_INSTALL -> SMOKE_TESTED -> BENCHMARKED -> QUALIFIED_FOR_SCOPE -> READY; on expiry -> STALE or BLOCKED.
Explicit difference among installed, candidate, connected, executable, performance qualified and product qualified.

Acquisition lab may consult official docs, GitHub, model cards, tool manuals, MCP plugins, books/tutorials, internal defects. Download/install or license changes only under approved security/rights policy. Prefer isolated environment, pinned versions/checksum/SBOM, controlled workflows and supply-chain tests. No uncontrolled execution of arbitrary external downloaded code.

## Video production standard contracts

`NicheManifest`: classification and per-niche policy.
`ProjectDNA`: audience, language, IP, content type, risk, output target, quality SLA, budget.
`SceneSpec`: narrative goal, characters, style, continuity anchors, audio, locations, camera, storyboard, rights.
`ShotSpec`: duration, frame rate, 2D/3D/game/capture/audio category, action choreography, dialogue or music, actor IDs, asset refs, acceptance QC.
`ToolDecision`: candidates, proven features, constraints, score, decision reasons, fallback, human approval if needed.
`ShotRenderBundle`: encoded frames/audio, intermediate masks/depth/cryptomatte/metadata when available, source hashes, compute/runtime provenance, codec, versioned quality report.
`EpisodeMaster`: assembled MP4/MOV/WAV, subtitles, metadata, full content/right lineage, final approval and rollback refs.

Across engines all outputs use same time-base/fps/colorspace/audio sample rate/shot frame dimensions, standardized *at final conform*, with suitable source-specific intermediate formats. Never discard raw masters/stems until final QC and audit proof.

## Departments shared by all studios

1. Executive & portfolio — niche strategy, experiment budget, project selection, channel priorities.
2. Research & A/B evidence — YouTube market research, competitor style analysis not copying.
3. Creative — ideation, scripts, lyrics, storyboard, hooks and educational value.
4. Art & IP — characters, visual style bible, asset rights & licensing.
5. Rigging & animation, environments, cameras & cinematography.
6. Music, voices, sound design, Foley, ASMR postproduction.
7. Tech R&D and capability/lab, security/SBOM/license review.
8. Resource scheduler, persistent GPU worker, workload budget and fallback.
9. Editorial/graphics/colour/subtitles/localization/mastering.
10. QA/QC multi-layer and human expert review; legal/children safety channel-specific gates.
11. Distribution/YouTube packaging/SEO/publishing and analytics.
12. Ops reliability — telemetry, queues, backups, recovery, audit logs.
13. Continuous improvement — regression from confirmed mistakes, experiment comparisons, versioned rules.

## Universal QA gates

G0 requirements and rights; G1 script/storyboard or curriculum; G2 assets/IP/character/rig; G3 shot planning/tool safety and executable evidence; G4 render frame/geometry/audio; G5 cross-shot continuity and musical synchronization; G6 edit/frame rate/colour/audio/encoded MP4; G7 safety/legal/YouTube originality/Made-for-Kids policy; G8 editorial human approval for risky or new content; G9 publish authorization; G10 performance feedback.

Red/critical hard gates cannot be softened by overall good grades. Auto-repair by precise component and bounded attempts; if repeated failure or ambiguous artistic quality, route to human. All negative controls and known limitations preserved; no fake PASS.

## Roadmap: incremental upgrades, without rewriting codebase

| Phase | Milestone | Deliverable | Entry acceptance |
|---|---|---|---|
| F0 | v1.6.31 | Capability + Niche audit V2, gap classification, tool evidence snapshots | Existing 744 baseline tests stay passing; no tool marked executable without smoke |
| F1 | v1.6.32 | `NicheIntelligenceConference` reads prompts/script/reference and generates fully typed NicheRecipe | 7 original + all newly prioritized niches scored with traceable evidence and rights |
| F2 | v1.6.33 | Universal `ShotDecisionEngine` integrates current scene conference/method switch/hardware/licensing | Golden fixtures select at least 4 distinct studio pipelines, bad candidates blocked |
| F3 | v1.6.34 | Multi-backend adapters and production media contracts: Blender, Godot/game runtime, ComfyUI opt-in, FFmpeg/2D/capture | At least two real end-to-end non-Blender rendered media shots on hardware |
| F4 | v1.6.35 | Preschool studio prototype (song/music-first/organic rig/character bible/beat+viseme) | 45–90s original song pilot with age/learning/music human approval and full source rights |
| F5 | v1.6.36 | Multi-niche asset registry and automatic scene/props/animation/voice catalogue | Stable asset IDs, license provenance, versioned updates and reusable clips |
| F6 | v1.6.37 | GPU/audio/video workload scheduler and per-scene cost estimation | Measured RTX3060 VRAM max, restart/recovery, resource conflicts prevented |
| F7 | v1.6.38 | Cross-backend continuity + automated shot repairs + human review UX | Multi-shot failures correctly flagged/repairs bounded, final MP4 audiovisual QC |
| F8 | v1.6.39 | Three niche proof-of-production pilots: Preschool Music, Minecraft, one non-Blender (rain/story/game) | 3 end-to-end varied formats with QC and reviewer approval |
| F9 | v1.6.40 | Long-form reliability, multi-language variants, release workflow, metrics feedback | Verified full-length episode, rollback, costs, quality floor and no unauthorized publish |

**Prioritization:** do not buy/install all tools before the benchmark shows necessity. Keep existing Minecraft, Roblox and Long Slide lanes operational. Preschool music has its own rights/child safety editorial checkpoints. Financial and GPU constraints are hard gates. Each milestone must run targeted negative tests and the full pytest suite, with an actual artifact where appropriate.

## Confirmed source/policy references (verify license status during implementation)

- CoComelon own curriculum/music production values: https://www.cocomelon.com/about
- YouTube kids quality principles: https://support.google.com/youtube/answer/10774223
- YouTube Made for Kids setup: https://support.google.com/youtube/answer/9527654
- YouTube Inauthentic/reused content: https://support.google.com/youtube/answer/1311392
- Blender 4.5 shape keys: https://docs.blender.org/manual/en/4.5/animation/shape_keys/introduction.html
- Godot MIT license: https://godotengine.org/license/
- ComfyUI official: https://github.com/Comfy-Org/ComfyUI
- Remotion licensing (entity size restrictions): https://github.com/remotion-dev/remotion/blob/main/packages/core/LICENSE.md
- OpenToonz: https://opentoonz.github.io/e/
- Meta SAM2 licensing: https://github.com/facebookresearch/sam2

**This document is a plan only. No code changes, installs, external account access, publishing, or deployment are implied by its creation.**
