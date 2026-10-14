# CineFactory OS — STUDIO EXCELLENCE / DIRECTOR-LED PRODUCTION POLICY
Date: 2026-10-09. State: DESIGN CONTRACT + PRODUCTION PLAN GATE CODED, NOT DISNEY-LEVEL CERTIFICATION.

## Executive directive

CineFactory is a **media company** with screenplay/storyboard, direction, performance, character/world continuity, animation/VFX, lighting/camera, editorial, sound, color, QA, rights and research feedback. Not merely a prompt-to-video wrapper.

QUALITY BAR is judged using screened final output with human-adjudicated benchmarks and repeatability. "As beautiful as Disney" = ambitious aspiration, never claimed as a certified property of generated outputs or an AI model alone. Every media tool is a subordinate production instrument. Story/emotional direction and continuity are inputs.

## Permanent non-negotiable creative contract

1. Script: audience, hook, premise, conflict, stakes, rising complications, turning points, setup/payoff, motivation, emotional payoff, pacing, scene duration and originality.
2. Characters: canonical character ID, approved proportions and silhouette, rig version, topology/face, expression set and facial range, wardrobe/hair/accessories, voice identity, props, poses, acting arcs and test turnaround sheets. No unexplained identity drift between shots.
3. Worlds: location map, geography, prop continuity, asset IDs and material/version, lighting continuity, backgrounds, art direction palette, depth, physical plausibility. Ensure setting serves narrative.
4. Director: shot objective, subject blocking, staging and eye-lines, screen direction and 180-degree rule where suitable, shot size/lens, camera motion, depth of field, reaction shot, cutaway, emotional tension/release. Animatic timing BEFORE full production.
5. Motion/performance: clean anticipation, clear action, arcs, secondary motion, expressive pose/eyes/mouth, believable reactions, contact and collision; lip-sync / phoneme events where dialogue exists. A still-image generative clip does not automatically replace a rig with controllable performance.
6. Lighting/render: consistent look development, physically coherent shading where desired, no clipping/flickering, strong subject separation, color pipeline, compositing passes, true output-resolution review. Hero-shot retakes allowed.
7. Audio: character voice identity, dialogue intelligibility, ambience, physical foley, music beats and rights, spatial perspective, no pops/clicks; separate mix stems and technical loudness QC. Sleep channels have special no-jarring-sounds gates.
8. Editing: narrative continuity and beat-led cut choices; J/L cuts, reactions, sound bridges, restraint in transitions, motivated rhythm. Professional editorial approval is distinct from automatic assembly.
9. QA: script, continuity, expression, camera readability, lip-sync, materials, render artifacts, subtitles, audio, color, rights, packaging, retention hypothesis and production throughput. No green light solely because a model score exists.
10. Post-release: own traffic sources, 30-second retention and full relative curves when available, CTR, AVD, RPM, audience satisfaction signals, causal uncertainty, versioned creative changes and controlled tests. Competitors' private metrics are UNKNOWN.

## Per-niche production conference (two branches)

Branch A DAILY discovery: source-backed breakouts; creator ≤30d + 2 distinct ≥1M longform ≥8min; independent evergreen demand; original-entry opportunity; economics; topic/format novelty; rights. Do not author portfolio approvals from search or inflated view estimates.

Branch B OWNER-APPROVED pod: daily competitor and mature-leader updates; identify 0–15d videos, rank against age/velocity baselines and estimate volatility; watch actual video where lawful and accessible, thumbnail + audio + scene/camera/acting annotations by timestamp; propose creative differentiation. Keep immutable evidence and council dissent.

Per studied video produce a **Competitor Scene Breakdown**, with evidence-backed vs hypothesis statuses:
- exact video ID, created/published dates, author/rights, sample availability and provenance;
- scene timeline and visual/audio evidence with timecodes; hook at 0–30s, narrative arc, shot changes, dialogue, expressive acting, humor/tension cadence, world, camera, mix, thumbnail, title;
- observed repeated patterns across at least 3 videos/channels rather than one viral success;
- original story pitch and distinctive creative grammar rather than reproducing competitor copyright-protected expression;
- translate to `creative_brief` with shot-by-shot direction and resource requirements; CineCouncil disagreement resolved first.

### Niche-specific blueprints

- **Minecraft/Roblox hero animation**: persistent voxel/R6 rigs, canonical skin/clothing, hierarchical facial rigs and expression library, NLA animation clips, reaction engine, controlled props, stage/world registry. Prefer Blender/Unreal deterministic actors; AI assists concepting, textures/background montage and safe auxiliary shots, not serially recreating hero faces for every take.
- **Long Slide Game**: physics/engine runtime; persistent animals, obstacle kit, procedural level generation, repeatable collisions and camera coverage. Preview simulations then high-fidelity batch render.
- **GTA/action**: rights-aware assets; rigged action, reusable environments/crowds, stunt blocking, animation and physical simulation. Observe game/software license, not imply actual GTA source assets are unrestricted.
- **ASMR tactile / silent fishing**: controlled physical capture and excellent microphones first; macro lighting, no unintended noise, authentic hands/actions and ambience. Generative overlays optional where accuracy permits.
- **Rain sleep / audio stories**: source/license-clear recorded sound and voice, robust seamless audio assembly; scene layers only where visually valuable. Narrated books require permission to read/reproduce copyrighted text.
- **English learning/education**: pedagogy and fact review, actor/voice continuity, subtitles and tempo; procedural Remotion graphics for clear repeatable editorial segments.

Unknown niche = no inherited pipeline by default; run a new Production Conference, design DNA and pilot A/B.

## Department design

1. Research & Competitive Intelligence: public evidence with verified IDs, timestamped scene facts.
2. Creative Strategy & Originality: differentiation, audience fit, series arc.
3. Script Room: logline, treatment, outline, beat sheets, scripts, table-read and story editor.
4. Art Direction: character/setting style guide, concept sheets, reference art.
5. Technical Direction: choose tool/method per shot, benchmark actual quality and time.
6. Asset Library: rig, expression controls, costumes, world/prop versioning, materials, licensed source audit.
7. Animation & Acting: character posing, anticipation, weight, secondary motion, lip-sync, emotional performance.
8. Cinematography: framing/coverage/camera blocking/lens/lighting continuity.
9. VFX & Compositing: render passes, effects, clean-up, graphic elements.
10. Sound: voice, foley, ambience, score, dialogue edit and mixing.
11. Editorial: animatics → assembly → fine cut → conform → final delivery.
12. QC + Rights + Production Operations: independent challenge, take selection, cost/queue/risk, export and owner decision.
13. Audience Research & Growth: packaging, owned analytics, learn/versioned creative experiments.

Every department works from the SAME locked `EpisodeCreativeBible` / `ShotWorkOrder`, not free-form untracked competing prompts.

## Tool choices and verified reference links (CHECK AT DEPLOY TIME)

| Stage | Preferred engine/editor | Why | Integration / rights caveat |
| --- | --- | --- | --- |
| Original rigged heroes, acting, repeatable scenes | **Blender**, possibly Unreal for high-end cinematic realtime | editable control, reusable assets/NLA/rig library, continuity | existing CineFactory Blender workers; benchmark in production |
| Physics game-style, long-slide | **Unity/Unreal deterministic runtime** | consistent physical staging and repeatable runs | pipeline adapter + licensing/asset QC |
| Visual concepts, controlled inserts, stylization | **ComfyUI** with approved workflow models | graph-based I2V/keyframes/LoRA/VFX, server `/prompt` and WebSocket automation | workflow version and model license must be pinned; current deployments not assumed |
| Local generative video candidate | **LTX-2.5** (newer than LTX-2), Wan2.2; candidate-specific eval | LTX docs: native audio/video, multi-shot, fast/pro / LoRA | LTX-2.5 official minimum **32GB+ GPU VRAM**, recommended A100/H100 (in October 2026 docs). Not a fit for the current 12GB unless future optimized variants explicitly benchmarked. Licensing of weights has conditions. |
| Cloud/SaaS premium inserts if authorized | **Google Flow / Veo / Gemini Omni**, other verified providers | references, frames/ingredients and scene-editing capabilities; fast creative iteration | subscription/credits, usage rights, data handling; **NOT** assumed API/MCP ready, use an authorized official API or manual operator/approved computer interaction |
| Editorial automated assembly, scalable subtitles/cards | **Remotion + FFmpeg** | versioned, parametric high-volume output, deterministic timecode | not a substitute for high-quality narrative fine-cut |
| Professional master editing, sound and grading | **DaVinci Resolve Edit + Fusion + Fairlight + Color + Deliver** | professional edit, audio mix, color match, VFX finishing, conform | scripting capabilities verified per local version / UI; executable presence cannot be assumed |
| Effects/graphics alternatives | After Effects, Nuke or Fusion candidate | specialty comp/tracking/expression if proven better | evaluate ROI, license and actual installed executable |
| Final quality validation | FFmpeg/ffprobe, pixel/audio QC, independent visual review | preserve frame integrity, color audio, no missing segments | Quality approval separate from generation |

Official sources:
- ComfyUI: https://docs.comfy.org/development/comfyui-server/comms_routes
- Blender NLA: https://docs.blender.org/manual/en/latest/editors/nla/introduction.html
- Blender overrides: https://docs.blender.org/manual/en/latest/files/linked_libraries/library_overrides.html
- LTX-2.5: https://docs.ltx.io/open-source-model/getting-started/overview/ and https://docs.ltx.io/open-source-model/getting-started/system-requirements
- Google Flow: https://labs.google/fx/tools/flow
- DaVinci Resolve 21: https://www.blackmagicdesign.com/products/davinciresolve/edit
- Remotion: https://www.remotion.dev/docs/parameterized-rendering

## Quality first with credible speed

Three creative passes:
- **P0 storyboard/animatic**: fastest cheap slate/proxy shots, validate storytelling, scene logic and framing. Do not spend 4K render time on a broken idea.
- **P1 proof of 2–3 hard scenes**: actual hero face expression, complicated interaction, camera performance and continuity, with QC. If it fails, revise production method before batch.
- **P2 batch**: reuse known-good rigs/expressions/animation clips, cache stable assets, dispatch per GPU/backend memory + measured seconds/shot, auto-edit a first cut. Complex hero takes have more retakes; simpler backgrounds use lower-cost lanes.
- **P3 finishing**: film edit / resolve, foley, dialogue and music, color grade, native 4K or transparent upscaling labeling, QC and rights.
- **P4 learning**: owned retention/CTR/RPM hypothesis and long-term tests.

Cost/quality scheduler should minimize `measured compute time + retakes + rendering waste` while satisfying hard acting/identity/story/rights gates, rather than always choosing minimum inference latency. Use actor/library caching and worker parallelism for real speed.

## Code implemented in this step

`cinefactory/production/studio_director.py`: create structured plan from `cine.studio.creative_brief.v1`, with required script beat, scene goal, blocking, camera, lighting, sound, transition, storyboard, performance and canonical actor bible; choose primary production lane based on scene nature, independent of current RTX 3060; require real benchmark evidence before `CAPABILITY_BENCHMARKED`. Each plan includes departmental tasks and post plan. Never a video render or final approval.

`tests/test_studio_director.py`: blocks absent script/acting/identity/boards, keeps multiple-GPU pools possible, routes each niche differently, never grants production permission even on benchmark-stamped tool metadata. This is a director decision planning gate, not visual QC certification.

### Existing code limitation to close next
- Existing `StoryboardGate._review` / `VideoFactory._visual_review` can accept without a visual QC implementation, inherited legacy behavior. For a strict premium production profile, integrate this new plan in the main orchestration and **require a real independent Visual QC implementation**. Do not claim an engine rendered professional footage because the router selected it.
- `ShotRouter` still scores GREEN/YELLOW/RED/HERO independently of fully quality-aware niche planning. Implement phase-aware layered routing that can use the new director plan.
- Need authentic video/scene analysis, approved original character rigs and real side-by-side pilot quality comparison before Disney-scale aspiration can be measured.

## Acceptance status

Designed & implemented planning contract, representative simulation/automated tests. Not yet live rendered with new 32GB+ production GPU or owner-authorized SaaS. No tool availability, quality score or production throughput is assumed without execution evidence.


## Clarifications added after engineering test

- A complete `episode_beat_plan` with at least 3 substantive beats is required for director review, together with `script_editor_approved=true`. ASMR and ambient episodes use a sensory/audio progression instead of forcing a traditional 3-act film plot.
- A `BENCHMARKED_READY` tool flag does NOT bypass script-editor approval, actual rights clearance or owner budget authorization. A reviewer-supplied flag is a planning claim, not authenticated proof of installation.
- The pilot test of two ORIGINAL Minecraft shots routed character acting to Blender and controlled weather montage to ComfyUI. It correctly returned `PLANNED_BLOCKED_CREATIVE_REQUIREMENTS` because one storyboard and other project approvals remained missing. No footage was produced by this specific director-plan tool.
- For long-form fishing, use a dedicated observational documentary style, not the tactile ASMR preset.
- **Remotion licensing:** official FAQ as of 2026-09-30 allows free use for individuals and small teams up to 3; for a larger organization/company production automation, Company License terms can apply, including automator billing. Remotion is source-available rather than OSI-approved open-source; always check specific current terms before scaling: https://www.remotion.dev/docs/license/faq
- **Google Flow:** official creative UI capabilities do not automatically establish official MCP support or automation permission. Research only authorized integration points. https://labs.google/fx/tools/flow
- **Model commercial license:** open weights are not universally Apache. Each LTX checkpoint, fine-tune, image/audio source and generated output must receive a license/terms check; the app might be subscription/credit governed. LTX docs refer to different open-weight commercial rights depending on model release.
- Current Cinema Flagship plan represents a director review and resource allocation policy, **not actual validated cinematic visual excellence**.
