# CineFactory — Research to Production Conference v2
Date: 2026-10-10 (Asia/Bangkok) | STATUS: Working **research/prototype decision gate**, NOT a completed full-video creative analysis or proof of Disney-class production.

## Core user goal

When an owner legitimately approves a niche/format, CineFactory must repeatedly investigate it, analyze real popular and underperforming competitor long-form videos, learn replicable yet ORIGINAL creative principles, then perform objective **quality-first** comparative pilot trials across plausible tool combinations. Invest in a production workflow only after adequate real evidence for **both cinematic quality and accepted-shot throughput**. Current 12GB GPU is one temporary worker, not the permanent ceiling: allow multi-GPU 32/48/80GB or cloud workers under separately approved money/license rules.

## Niche owner-approval vs automatic execution

The existing P0 `niche_pod.py` validates the strict Company promotion gate, local owner approval event and evidence hashes before making `pod.json` with jobs `CONFIGURED_NOT_SCHEDULED`. A NEW `production_conference` section in the pod explains when the research-to-production investigation can be pursued, its output obligations and fail-closed policy. It does **not** authenticate the user UI session, schedule an agent, consume paid credits, render or publish automatically. These require a future trusted job runner + approval UX. For unapproved experimental niche studies, use an explicitly labeled `DEMO_ONLY` reference, never impersonate an owner event.

## Professional multi-stage analysis: what an expert video researcher must actually deliver

### Sampling design, per niche
1. Verified topic/format and legal inspection rights before opening footage. Same-niche title is a search proxy ONLY.
2. Leaders: leading creators, age-normalized recent outliers, at least 3 high-view long videos, current uploads and changes across time.
3. Newcomers: real 0–30 day channels and 2 separate 1M+ ≥8min breakout videos with exact channel age/video ID/format; ownership and origin reviewed.
4. Controls: matching creator-format low/outperformed recent videos to expose what *doesn't* work, counterexamples and survivorship bias.
5. Robust sample: multiple channels, multiple uploads, distinct view ages. If a bucket is empty, explicitly request a fresh targeted search rather than invent a channel.
6. Latest content 0–15d: classify organic, trend-related, news-driven, perennial, seasonal or unresolved; trend metrics are relative-age estimates, not claims about recommender algorithm/private analytics.

### Per-video timeline form, not superficial topic keywords
- SOURCE: channel ID, exact video ID, publication/creation timestamps, public views age, official vs rounded metadata, rights and source path/hash, inspected full video or thumbnail-only.
- STORY: concept, originality, logline, first 3/5/15/30 seconds, audience promise, first conflict, character goal, inciting incident, rising action, reversal, emotional climax, payoff and ending.
- ACTING: character silhouette/rig/wardrobe/voice continuity, eye-line, micro-expression, body language, facial articulation, gesture arcs, anticipation, reaction timing, emotion shift per scene. The script is insufficient without physically observable acting.
- CINEMATOGRAPHY: character blocking, staging geography, shot size, lens approximation (not literal focal length unless known), camera height, direction, move, shot-reverse-shot and coverage, depth, focus hierarchy, lighting and art direction.
- WORLD: original sets/locations, material, palette, shading, prop/hand contact, physics consistency and world changes, actor continuity across camera cuts.
- EDIT: time-coded shot cut transitions, shot duration distribution, J/L cuts, reaction cuts, voice/sound bridges, rhythm through acts, pauses and visual jokes.
- AUDIO: separately inspect dialogue, sound design/foley, musical cues, ambience/room tone and mixing; do not infer sound from frames or metadata.
- PACKAGING: observable thumbnail silhouette, focal contrast, text, title promise, degree of match with payoff; avoid derivative recreation.
- EVIDENCE: precise timestamp, original frame/audio pointer, reporter identity, whether direct observation or hypothesis, disagreements and unknowns.
- RESULT: identify repeatable FORM principles, not protected dialogue, artwork, characters or plots. Infer possible audience response only as hypotheses; never assert competitors' private CTR, retention, YPP or RPM.

### Causal humility and learning
Require cross-video patterns with independently reviewed cases; compare successful and weak controls, same upload age/length/language and appropriate baselines. Avoid single-video causality and fabricated quantitative ratings. Agent departments should challenge each other and issue a single source-bound CineCouncil record, not multiple unreviewed winner scores.

## Quality-first production technology conference

Input is **original creative bible, character/world bible, script and sample timecoded references**.

Parallel solutions are candidates, not guaranteed best tools:

| Production challenge | Candidates | Decisive benchmark |
| --- | --- | --- |
| Repeatable Minecraft/R6 animation (dialogue, acting, gestures, identity) | Blender Rig/NLA/ExpressionEngine; Unreal Control Rig if proven; AI-assisted auxiliary assets | 3-shot same rig face/eyes/expression/lips/eye-line, acting and character identity QC |
| High-end cinematic physics/world | Blender Cycles/Eevee or Unreal Sequencer/MRQ | camera/light/material continuity, physics, real render time |
| Controlled AI inserts/complex transition | ComfyUI + properly licensed LTX-2.5, Wan2.2 etc; controlled original reference imagery | temporal coherency, identity, camera, anatomy, output rights, failed-take rate |
| Approved cloud premium complex inserts | Google Gemini video API/Veo/Omni or Flow UI via authorized surface | per-shot consistency, credits/usage, terms, API distinction |
| Physics long-slide/gameplay | approved game runtime + stored level/asset/obstacle/camera generator | deterministic collisions, art identity and repeatable fps |
| ASMR/field fishing/audio sleep | real recorder/mics, cleaned/cleared source audio, Resolve/Fairlight, FFmpeg | authentic tactile/water sound, no abrupt loudness, focus/lighting, seam QA |
| Motion graphics / English lessons | Remotion + FFmpeg, optionally Resolve finishing | real captions, typography accuracy, comprehensible visual rhythm |
| Final film edit/audio/color | DaVinci Resolve Edit/Fusion/Fairlight/Color; FFmpeg conform; Remotion where suitable | actual authored timeline, dialogue mix, delivery QC, real resolution/frames |

### Rules for scouts
- Look at **GitHub official repos, plugin capabilities, installed executables, MCP contracts, SaaS official APIs, model versions and license**. A marketing feature page is CANDIDATE only.
- Each workflow has tool repo URL, checkpoint/model revision, commercial licensing obligations, exact executable/API status and evidence timestamp.
- Try **one controlled original difficult scene** in comparable conditions; avoid selecting a tool based on the quality of a demo assembled by its vendor.
- If paid SaaS is considered, require explicit credits/data/privacy/rights authorization and measure dollar per ACCEPTED second. No silent pay-per-API fallback.
- Hardware scale is not constrained by currently connected desktop; use a configured multi-worker resource pool and GPUs with enough actual memory. Do not equate GPU size alone with guaranteed quality.

### Quality/speed comparative experiments
Maintain each `scene_trial_matrix` as a film-unit benchmark:
- Acting shot: identity, eyes/expression, camera, voice/lip-sync, prop contact, 3 cuts.
- Environment/transition: material & art, motion, lens/lighting, camera and world continuity.
- 30s fine-cut: story beats, sound dialogue music timing, transitions, color, readability, correctness.
- Same source board/bible and durations for all contenders; record rendered video SHA256 + **real ffprobe stream width/height/duration**. Reject a fake video file or renamed payload.
- Measured render time, QC failures, human repair time, retries and actual accepted output seconds per hour. Hard quality gate minimum 0.85 on scenario dimensions (preliminary *reviewer-reported*, not machine-certified).
- First fail any hard visual/script/rights/identity gates; only THEN optimize output accepted seconds per hour and cost.
- Quality reviewer identity and rights clearance currently self-reported, not authenticated: even winning `PILOT_CANDIDATE_FOR_HUMAN_REVIEW` remains ADVISORY, not cleared for publication or production.

## Code and demonstration actually performed

New:
- `cinefactory/production/niche_production_conference.py`: frozen same-source research, cohort-balanced selection (fresh million, 0–30d newcomer, established leader, within-channel weak control and diverse remainder), 3-part initial timeline worklist, tool scout registry (9 categories), specific pilot bake-off, **real ffprobe + render SHA** and an interface to existing `studio_director.py`.
- `cinefactory/production/scene_study.py`: verifies exact local authorized observation plus 8-frame pixel measurements, produces frame-timestamp worklist; human scene annotations must cite existing frame+timestamp, cannot assert audio from a still. Thus actual visual evidence is not confused with inferred plot.
- `cinefactory/research_intelligence/niche_pod.py`: new production conference config under owner-approved research pods. No automatic execution.
- New tests in `tests/test_niche_production_conference.py`, `tests/test_scene_study.py`.

Demo source: October 9 Company YouTube publicly collected Minecraft animation `evidence_live_04` snapshot (October 10 local date for demonstration). NOT OWNER APPROVAL and NOT FULL CONTENT VIDEO STUDY.
- Selection: 34 title-aligned sample videos; 18 assigned for analysis from 5 channels, including 3 fresh-million public-proxy videos, 4 mature leader items and 3 weak controls; no 0–30d newcomer item in this sample.
- 9 tool lane candidates, 3 hard pilot scenarios, precise `UNKNOWN` content fields rather than fictional competitor camera/story analysis.
- Two-shot ORIGINAL Minecraft demo director routes: Blender acting rig vs Comfy controlled montage, linked by SHA256 to the exact conference. Blocked because storyboard/project approvals incomplete.
- No actual comparative Blender/Comfy/Unreal/Resolve output available: `pilot_bakeoff.state=NO_VERIFIED_ACCEPTABLE_PILOTS`.
- Separate genuine 8-frame FFmpeg owned synthetic test passed the scene study QA; does NOT prove any competitor was watched.
- Stored files:
  - `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\conference_pipeline_demo_v2\conference.json`
  - `...\conference_pipeline_demo_v2\inspection_template.json`
  - `...\conference_pipeline_demo_v2\director_plan.json`
  - `...\conference_pipeline_demo_v2\director_plan_research_link.json`
  - `...\conference_pipeline_demo_v2\pilot_bakeoff.json`
  - `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\synthetic_scene_study.json`

## Next criteria before calling this fully automatic or production quality
1. Actually acquire access to full competitor videos or authorized excerpts in an approved way, time-coded scene/audio/caption analysis, checked on multiple videos. Public thumbnail alone cannot do this.
2. For each selected video: department-specific VLM/audio/screenplay review with source timestamps and a real rebuttal/Quality signoff. No local VLM configuration currently passed quality benchmark; 256M CPU model was rejected (66.7% of 3 synthetic questions).
3. Connect approved pod to actual durable on-approval task scheduler with permissions and rate limits. Pod configuration exists, but jobs are not scheduled/executing on approval automatically.
4. Build real original rigs/characters/worlds and two/three professional pilots in Blender/Comfy/Unreal. Measure native quality, identity stability, acting, render cost/throughput, independent baseline quality and necessary retakes.
5. Implement trusted tool capability evidence registry and authenticated production budget/rights approval (the registry currently lists CANDIDATES, not installed verified engines).
6. Only then choose production routes, connect director-plan to actual renderer, fine-cut/Resolve pipeline and QC. Release authority remains with the owner.

### Official references checked (2026-10-10)
- https://docs.blender.org/manual/en/latest/files/linked_libraries/library_overrides.html
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.ltx.io/open-source-model/getting-started/system-requirements (LTX-2.5 GPU ≥32GB, CPU/GPU environment requirements)
- https://github.com/Lightricks/LTX-2/blob/main/LICENSE (LTX-2.5 community licensing conditions; do not assume universal commercial permission)
- https://ai.google.dev/gemini-api/docs/video (Gemini Omni/Veo API are distinct from the Flow UI)
- https://www.remotion.dev/docs/license/pricing (Remotion license changes with company/automation scale)
- https://www.blackmagicdesign.com/products/davinciresolve

**Verdict:** Research-to-production decision architecture is materially improved and tested. End-to-end professional full-video viewing, real tool bakeoff and cinematic quality are NOT yet demonstrated; do not mark the niche production ready.
