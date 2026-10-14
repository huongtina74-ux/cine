# CineFactory OS — MANDATORY RESEARCH-FIRST PRODUCTION SOP v264
Effective proposal: 2026-10-11. Status: OPERATING STANDARD PROPOSED; engineering integration and enforced E2E proof are NOT YET COMPLETE.
Owner intent: A professional film/video studio must independently research actual original competing videos, watch and listen fully, then convene departments and plan scripts, shots, assets, tools, post-production and QC at cinematic granularity. No metadata-only production plans.

## Policy 0: Two independent research entrances (canonical Company Youtube source)
Use `C:\Users\ADMIN\Downloads\Company Youtube\sops\canonical-youtube-niche-discovery-workflow.md` as authoritative discovery SOP.
A) Leader channel: subformat exact, highest-view ever, current <=30d, own-channel age-matched outliers, <=5d momentum, view/sub signal.
B) Young competitor: channel actual creation 0–30 days proven; >=2 distinct >=8m videos >=1M, persist to watchlist even after turning older.
C) Cross-keyword 24h/3d/7d/15d/30d, video >=8m, >=1m <=15d preferred, more valuable from very small channel if verified.
D) Continuous dated watchlist and long-horizon versus short-horizon hypotheses with confidence and counterexamples.
Gameplay / cinematic Minecraft animation / other subformats are DIFFERENT markets. No automatic cross-format evidence promotion. Live/Shorts excluded for Maizen longform research.

## Policy 1: Original video acquisition and audiovisual FULL REVIEW (REQUIRED)
For each selected video keep video_id, source URL, duration, publication date, exact observation timestamp, channel_id, credible subscriber provenance, rights/provenance source IDs.
Download of unauthorized copies or reuse of audiovisual assets is not an implicit permission. Source player review under lawful access is enough.
- Original-player or lawfully available native recording must be inspected over full duration at normal 1× playback for both soundtrack and moving picture; use temporal chunks for computer efficiency, but every second must have review coverage. Two-times browser playback or sampled stills do NOT establish this.
- Audio source track: 100% timeline decode + independent review of every segment, speaker turns/diarization (UNKNOWN if cannot separate), ASR with timestamps, music SFX Foley/ambience and musical licensing UNKNOWN unless proven. Never assert complete audio QC from AudioSet on 8s windows.
- Video source track: video shot-boundary timestamps, composition, camera height/azimuth/motion, staging, action continuity, HUD vs rendered animation, color/lighting, acting and effects, transitions. Adaptive frame/sparse analysis may assist, but full-motion semantic coverage and unresolved segments must not be represented as fully watched.
- Reobserve damaged/uncertain seams at 1×; preserve hashes, raw timestamped evidence, coverage maps, uncertain cues. A model cannot infer which proprietary software was used from an end result alone. Cite creator BTS/manual/license if identifying exact tool.
- First reviewer generates observations; a second reviewer/agent independently audits original moving video+sound rather than merely accepting agent 1 notes. Explain reviewer provenance (automated second model / human). A human-certified PASS cannot be claimed without real human signature.

VideoReviewEvidence required for EVERY source: {video_id, url, original_runtime, segments:[{start,end,video_coverage_proof,audio_coverage_proof,transcript_with_confidence,shots,camera,action,scene_transition,audio_event,continuity_observation,uncertainties}], coverage_ratio, audio_1x_reviewed, full_moving_picture_semantics_reviewed, independent_second_pass, disagreements_resolved, signed_by, evidence_paths, toolchain_unknown_flag, source_license_flags}.
Possible status: NOT_STARTED, ACQUIRED_ONLY, STRUCTURALLY_INDEXED, PARTIALLY_SEMANTIC_REVIEWED, AI_INDEPENDENT_REVIEWED, HUMAN_SIGNED_REVIEWED, BLOCKED.
No source coverage -> no source-based production analysis conclusion.

## Policy 2: Video dissection form (each shot/scene, not title summaries)
Timeline shot ledger columns:
- source_video_id, source_start/end, shot_id, objective/plot cause, character actions and emotions, prop states.
- lens/shot scale (wide/medium/close/detail), camera height/position/angle, framing/composition, dolly/tracking/pan/tilt/orbit, focus/axis/continuity.
- game-HUD/first-person or authored animation proof, rig/expression/VFX, environment and lighting/palette.
- actual dialogue transcript and verified speaker confidence, natural sound/foley, music intensity, transitions/cut rhythm, real timestamps.
- audience hook/payoff/measurable promise, observable pacing only (CTR/retention absent unless owned), uncertain causal links.
- repeatability and cost hypothesis, rights/copyright flags, known facts versus estimates.

Creative patterns must be compared against same-subformat low- and median-performing control videos from the SAME channel and age windows, and other channels; no single success is a universal winning formula.

## Policy 3: Mandatory all-department Film Research Conference
Only CONVENE after a usable, clearly labelled source review packet is available. If G02 is partial, hold any source-derived final production instructions; internal original-IP sandbox R&D can proceed separately with no false source-based claims.
Conference members: Intelligence, Research QC, Creative Strategy, Writers Room, Script Logic, Directing, Cinematography, Performance, Production Design, Assets, Sound/VO, Music/SFX, VFX, Editorial, Color, Technical Direction, R&D, Production, Rights/Compliance, Studio Management, Analytics/Packaging.
Conference output MUST include:
1) source evidence map (with uncertainty/reviewer status);
2) subformat taxonomy and winning vs control patterns;
3) concrete audience promise, premise, 10–30s hook, 14m act progression and payoffs;
4) ORIGINAL-IP premise variants, no copying names/skins/voices/competitor shots;
5) narrative feasibility and causal/script continuity risks;
6) practical method routing per scene, not universal Blender or AI/ComfyUI preference;
7) cost/time quality uncertainty and benchmark requirements; named gate owners.
Every department must have INPUT(s), OUTPUT(s), tools candidate, measurable QA and dependencies.

## Policy 4: Script Room -> script lock
Required production script per episode: theme and original IP, logline, synopsis, 3-act/beat sheet, fully spoken EN dialogue timed to character action, scene-level goals/conflict/choice/climax, character arcs, transitions, plot holes, dependencies, prop geography, music/FX intentions.
Automatic state bible: where each character is, possessions, number of consumables, wounds/costume, switches/doors and color-codes, spatial water/mechanics continuity.
The 840-second written script may be fully drafted yet NOT script-locked until read-through and actual scratch VO timing verify it. One paragraph/shot does not prove a believable 14-minute film.
Script Lock Gate: causal checks PASS; no unrealized props; time-constrained dialogue performable; source proof and IP cleared for source-derived choices; director/editor signoff.

## Policy 5: Director -> storyboard -> shot/animatic
For EVERY shot: camera ID, source beat and scene ID, frame in/out, angle, shot scale, axis, focal intent, camera height/lens idea, movement path/speed, character blocking, gesture/expression/eye line, props, lighting, cut motivation, voice/SFX/Music timecode, shot dependencies, focal attention and retention purpose.
Storyboard boards with distinct compositions and frame positions, not same decorated schematic repeated with different words. Editable SVG/3D animatic and frame source metadata. Real animatic includes time-based motion and scratch voice.
Production shot packet = approved screenplay + approved storyboard + shot tech spec + asset list + audio cue + rights + QA + backend choice.
No production packet after metadata-only scanning.

## Policy 6: Production tech routing by SHOT type, with proof
For gameplay: license-qualified Minecraft game/runtime, world/level scripting, replayable character actions, camera and capture pipeline; do not describe 3D rendering as authentic gameplay.
For animation: Blender/Mine-imator/other lawful licensed stack only after real executable/model availability, character rig quality and speed benchmark. Voxel rigs, animation library, camera rig, hair/face/expression, model identity continuity.
For special FX/montage: ComfyUI/local diffusion only if VRAM, artifacts, source rights, visual consistency and cost/quality gates pass.
For edit: FFmpeg/Remotion/Resolve as tools candidates dependent on executable availability; audio ducking, equal loudness, cuts and reaction timing; do not promise proprietary NLE automation without test.
ToolDecision for every shot: {shot_id, candidate_tools, inputs/assets, required_version/license, gpu_vram_estimate, execution_proof, output_quality_requirement, measured_performance, fallback, fail_closed}. UNKNOWN not silently replaced with "working".

## Policy 7: Department production and post chain
Intelligence source pack -> Story Conference -> Original Concept -> Writers Room -> Script QA -> Director Shot List -> Cinematography Storyboard/Animatic -> Casting/Rigs/Assets & Rights -> Technical Preflight & same-shot benchmark -> Production -> Editor/Voice/Music/SFX/VFX/Color -> independent film QC -> Packaging -> owner release approval -> Upload -> Retention/analytics loop.
Gate each upstream handoff, no shortcuts. Director prepares reaction and camera coverage, not merely visuals. Audio dept reviews entire dialog and Foley cue timeline. Editor uses EDL to cut source footage and original frames from actual render, not screenshots.
Production QC: playable native video+audio full timeline, shot match storyboard, cinematic coherence, character identity/prop state, no jump cuts unless intentional, dialogue and music intelligible, mobile clarity, 1080p24 pilot then upgrade on proven hardware, frame/codec/audio check, no unlicensed material, render speed and accepted seconds/hour measured.
Release QC: YouTube policy, IP rights, metadata accuracy, thumbnail honesty, channel strategy, safety and owner signoff.

## Policy 8: Current Maizen project v263, factual status
- Maizen gameplay vs Mine Block / MSToons animation must be treated separately. Existing source captures: 95 browser segments, 120 30s windows; 11 recaptured at 1x. Source evidence improvements verified. **No independent full native AV semantic signoff; G02 BLOCKED.**
- Original Nova/Pip Waterfall packet: 840s/82 timed scripted shots, 82 illustrative PNG/SVG storyboard panels, 27 static OBJ+MTL blockout assets. **Not** 82 cinematographically approved panels, production rigs, full dialogue audio, or rendered film. Script requires a believable full VO rehearsal and director review.
- Practical allowed next: implement thorough original source motion+audio review/independent second-pass; run script read-through and correct narration timing; build original rigs and true animatic, verify toolchain/licenses; pilot render after appropriate approval.
- Do NOT claim the current system enforces this SOP in every entry point until gate code is integrated and tested across all routes. The policy file itself is not a production system.

## Hard-fail checklist before production brief approval
- [ ] Multiple representative videos in the exact same subformat and context; strongest winners plus weak/median control.
- [ ] Original moving-video full-duration review for each critical reference, no unreviewed timeline gaps.
- [ ] Entire native audio semantic review and timed event/speaker notes.
- [ ] Genuine independent second-pass, all discrepancies resolved; reviewer identity/type recorded accurately.
- [ ] Claim ledger: source-backed facts/interpretations/hypotheses/right ownership clearly separated.
- [ ] Research conference sign-off and per-department inputs/outputs.
- [ ] Full original production screenplay timed by voiced performance.
- [ ] Per-shot camera/acting/staging storyboard and animatic, continuity verified.
- [ ] Exact tool licensing, execution proof and measured cost/quality benchmark.
- [ ] Real full video+audio film QC and authorized release.
