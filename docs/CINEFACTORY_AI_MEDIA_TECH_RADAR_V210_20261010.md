# CINEFACTORY AI / REPO / SAAS TECHNOLOGY RADAR — V210 (2026-10-10)

**Scope:** Broad curated scan, **not every repository or website on the Internet**. User machine: RTX 3060 12 GB, Windows, ~32 GB RAM. Goal: deploy qualified, commercial-compliant zero-paid-API local pipelines whenever suitable, retain commercial SaaS as paid quality benchmarks. This report integrates prior 10/10 snapshot with refreshed official documentation and a 96-entry machine-readable registry.

## Where to find the entire inventory

- Canonical versioned JSON: `config/technology/ai_media_radar_20261010.json`
- Read-only CLI: `python -m cinefactory.cli technology-radar`
- Filter candidates: `python -m cinefactory.cli technology-radar --category video --show-items`
- Filter P0: `python -m cinefactory.cli technology-radar --priority P0 --show-items`
- Categories: `orchestration`, `image`, `video`, `3d`, `animation_motion`, `audio`, `editorial`, `saas`, `research`.
- Full previous technical baseline: `docs/AI_TECHNOLOGY_RADAR_20261010.md`.

The registry stores name, canonical/project URL, owner department, priority, published evidence state, licensing gate, RTX3060 estimate, actual local state and deployment flag for all 96 entries. Labels marked SOURCE_REVIEWED mean official public documentation was inspected, NOT files installed or rendered. Others are leads requiring source recheck. Every entry has `deploy_approved=false`.

## Important NEW / FRESH FACTS checked this scan

| Date / evidence | Product/repository | Why it matters | Verdict |
|---|---|---|---|
| 2026-10-09 official | Qwen-Image 2.1 Turbo — https://github.com/QwenLM/Qwen-Image-2.1 | 8-step image create/edit; multi-reference, RGBA; native ComfyUI support | MODEL Research License: noncommercial only unless separately licensed, HOLD monetization. |
| 2026-10-02 to Oct 7 repo | FreeVideo — https://github.com/FlashML-org/FreeVideo | Consumer VRAM H3 optimization and workflow metadata, 8GB author claim | Code Apache; MiniMax H3 weights/output region-restricted, HOLD worldwide releases. |
| 2026-08-03 original | MiniMax H3 — https://github.com/MiniMax-AI/MiniMax-H3 | Full model: FL2VA and distinct Ref2VA reference-conditioned audio-video; 4–15 sec native A/V; separate 2K regeneration | ComfyUI nodes are not weights, and USD/EU/UK/KR license regions require owner legal review. |
| 2026-09-15 official | FastVideo FastH3 8-step V2 — https://github.com/hao-ai-lab/FastVideo | Sparse video attention and inference/post-training acceleration | Do not assume RTX3060 5s generation time from 3090/H100 claim. |
| 2026-10-05 tag | HyperFrames — https://github.com/heygen-com/hyperframes/releases | HTML/CSS/Three.js+GSAP programmable video renderer for agents | Code Apache 2.0; P0 comparison with Remotion and FFmpeg for English/explainer and template-video lanes. |
| 2026-06-18 official | MOSS-TTS Local Transformer v1.5 — https://github.com/OpenMOSS/MOSS-TTS | Longer multilingual TTS and SGLang; ~100M Nano CPU alternative | P0 local voice test; model family Apache 2.0; voice owners must consent. |
| 2026-05 official | ACE-Step 1.5 — https://github.com/ace-step/ACE-Step-1.5 | Local music and short/loop cue generation, MIT repo | P0 sound/music test with song/style plagiarism checks. |
| Current Oct 2026 | ComfyUI and 2026 model ecosystem — https://github.com/Comfy-Org/ComfyUI | Native support for multiple model families; workflow templates and node registry | Use as orchestration node engine; qualify model weights separately. |
| 2026 verified | TRELLIS.2 — https://github.com/microsoft/TRELLIS.2 | High-fidelity image->GLB PBR assets, H100 benchmark | R&D; H100 seconds are not RTX3060 performance. |
| 2026 verified | AniGen — https://github.com/VAST-AI-Research/AniGen | Image->rigged mesh/skeleton/skin | Linux 18GB+ and restricted third-party CUBVH; HOLD on local/monetized pipeline. |
| Oct2 Runway changelog | Runway — https://runway.com/changelog | Seedance 2.5 draft, Ideogram 4.5 via MCP, DaVinci plugin Sep23, ElevenLabs V4 Sep29 | New cross-model production orchestration benchmark; hosted/paid, not local. |

**Do not infer release times from GitHub 'updated' stamps.** Use exact repo date/release/commits as relevant. Watch out for duplicate GitHub forks imitating official repos.

## Source-truth and LICENSE RED FLAGS

1. `FLUX.2 [klein] 4B` checkpoint is Apache 2.0. The 9B, 9B KV and Dev models carry different license, so NOT approved based on 4B terms. Official: https://github.com/black-forest-labs/flux2 .
2. `Qwen/Qwen-Image-2.1` and `Qwen/Qwen-Image-2.1-Turbo` checkpoint license: **Qwen RESEARCH LICENSE: NON-COMMERCIAL**. Details https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE .
3. `MiniMaxAI/MiniMax-H3` Community License: excludes USA, EU, UK, South Korea from Applicable Territory, restricts output use and distribution outside region. Details https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE . H3 and FreeVideo MUST NOT be promoted to worldwide monetized release without licensor/legal clearance. Code Apache 2.0 on FreeVideo does not override H3 weight terms.
4. `Tencent-Hunyuan/Hunyuan3D-2.1` Community License excludes EU, UK, South Korea and covers model outputs; world-distribution needs license review. Official https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/main/LICENSE .
5. `VAST-AI-Research/AniGen` main code MIT but third-party CUBVH component restricts commercial use. Official https://github.com/VAST-AI-Research/AniGen .
6. `NVIDIA Audio2Face-3D` sample repository and NIM pretrained models have different licenses. https://github.com/NVIDIA/Audio2Face-3D-Samples .
7. `ComfyUI-Manager`, `ComfyUI-GGUF`, `ComfyUI VideoHelperSuite` may be free code but external model terms and node/plugin dependencies may differ. Never auto-install arbitrary custom nodes (supply chain and arbitrary code execution).
8. Hosted Runway, Veo, Seedance, Kling, ElevenLabs, Adobe, HeyGen, Meshy are contract/credits/API services unless proven otherwise. No credential use and no credits consumed during this update.
9. GitHub and Hugging Face popularity, stars, public weights and high-quality demo do not certify original legal chain-of-title or right to copy branded characters.

## Measured LOCAL reality, versus vendor claims

Local prior read-only machine evidence (10 Oct):
- ComfyUI 0.38.0 at localhost:8188 returned 200 on NVIDIA RTX3060 12GB.
- Native six MiniMax H3 node types were present. **No matching H3 checkpoint/VDN weights or FreeVideo custom-node install was confirmed**. Presence of node does not mean video generation is ready.
- Existing SD1.5 checkpoint (~4GB), WAN2.1 Fun I2V 1.3B (~2.9GB) and UMT5 encoder (~6.3GB) were observed. Complete validated WAN workflow has NOT been proven; multiple modules may exceed VRAM together.
- Blender 4.5.14 binary, FFmpeg and FFprobe exist; whole-filmmaking QC and continuously active Blender worker remain unverified.
- No new model weights downloaded, ComfyUI node install, paid service use, or model render benchmark during this research.

## Workflow recommendation, NEVER a 1-to-1 substitution for Disney

**Stage 1: Research** — v208 channel-first format triage, real 0–30d channel evidence, competitor same-format matching, original brief, qualified sources.
**Stage 2: Creative** — Script Room, shot plan and human/director style approval, original character DNA and rights.
**Stage 3: Assets** — FLUX.2 Klein 4B P0 (if actual rights and resource checks pass); deterministic Blender for Minecraft/Roblox and stylized characters. UniRig only for arbitrary non-block articulated meshes; TRELLIS.2/AniGen R&D.
**Stage 4: Production** — original authored animation in Blender; real gameplay from real runtime; generative video/ComfyUI only for film shot styles that can pass continuity. H3/FreeVideo are technical R&D only pending worldwide output rights.
**Stage 5: Performance** — owner-consented TTS MOSS/Qwen/Chatterbox; NVIDIA Audio2Face evaluation for arbitrary rig blendshapes; not automatically for block characters.
**Stage 6: Post** — FFmpeg/Blender, HyperFrames vs Remotion for non-3D editing; music from ACE-Step with sound/music QC.
**Stage 7: Film QC** — v209 real media probe, independent story/acting/camera-edit/audio/originality/rights reviewers, producer approval. No invented full 8–10 minute film.
**Stage 8: Publish** — private-first signed YouTube owned channel + verified Analytics, only on owner consent; learning after real audience evidence.

## Benchmark slots ranked for 12 GB RTX3060 (proposal only)

| Priority | Benchmark | Inputs / outputs | Must capture |
|---|---|---|---|
| P0 | FLUX.2 Klein 4B | 3 views of a completely original character + background + face expressions | RAM/VRAM, time, identity/style drift, actual license |
| P0 | MOSS TTS Nano, Chatterbox, Qwen3 TTS | 90 sec English original dialogue + narrator, rights-cleared voice | pronunciation, expressiveness, pauses, resource use and stability |
| P0 | ACE-Step 1.5 | 30–60 sec score cue and ambiance | looping, latency, loudness, originality, rights |
| P0 | HyperFrames vs Remotion vs FFmpeg | 60 sec original English explainer with captions | frame accuracy, templates, effects, edit reproducibility, cost |
| P1/HOLD | FreeVideo vs native ComfyUI H3 | One licensed research-only 3–5 sec original shot IF rights reviewed and weights acquired | base/ref model distinction, GPU peak, RAM, render timing, audio sync, failure receipts |
| P1 | UniRig | Original arbitrary character mesh -> skeleton/skin -> Blender | deform QA, joint naming, rig stability, export |
| P1 | Story/film continuity acceptance | Original character-led 30–60 sec 1080p24 film, then 8–10 min | independent artistic QC + measured accepted seconds/hour |

No provider model is promoted to `QUALIFIED` from a README alone. The v210 registry refuses automatic deployment and can be reviewed through CLI filtering. The v209 production release requirements remain unchanged.

## Direct URLs and primary-source audit trail

- MiniMax H3 repo: https://github.com/MiniMax-AI/MiniMax-H3
- MiniMax H3 restricted weights: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
- FreeVideo: https://github.com/FlashML-org/FreeVideo
- Qwen Image 2.1 release/turbo: https://github.com/QwenLM/Qwen-Image-2.1
- Qwen license: https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE
- FLUX variants: https://github.com/black-forest-labs/flux2
- ComfyUI official: https://github.com/Comfy-Org/ComfyUI
- Official Comfy workflows: https://github.com/Comfy-Org/workflow_templates
- ComfyUI Manager: https://github.com/Comfy-Org/ComfyUI-Manager
- ComfyUI GGUF: https://github.com/city96/ComfyUI-GGUF
- ComfyUI Wan wrapper: https://github.com/kijai/ComfyUI-WanVideoWrapper
- ComfyUI VideoHelperSuite: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
- FastVideo latest FastH3: https://github.com/hao-ai-lab/FastVideo
- UniRig: https://github.com/VAST-AI-Research/UniRig
- AniGen: https://github.com/VAST-AI-Research/AniGen
- TRELLIS.2: https://github.com/microsoft/TRELLIS.2
- Hunyuan3D license: https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/main/LICENSE
- NVIDIA Audio2Face model/server terms: https://github.com/NVIDIA/Audio2Face-3D-Samples
- MOSS-TTS: https://github.com/OpenMOSS/MOSS-TTS
- ACE-Step 1.5: https://github.com/ace-step/ACE-Step-1.5
- HyperFrames releases: https://github.com/heygen-com/hyperframes/releases
- Runway vendor changelog: https://runway.com/changelog

**RELEASE STATE:** Technology candidates and risk gates are documented. No user-authorized installation or weight download occurred, no GPU model benchmark was performed in this radar update, and none of these results independently certifies Disney-level original filmmaking.


## Added direct local ComfyUI audit (read-only, 10 Oct)

The active ComfyUI endpoint returned **669 node class names** from object_info, including 6 MiniMaxH3, 32 Wan, 30 LTX, 7 QwenImage, 10 Flux, 14 Hunyuan and 36 names containing Audio. These counts are matches to built-in API **node type names**, not installed model families and not verified generated media. No VHS-prefixed or GGUF-matched node class names were returned. Some search terms (e.g. ACE) can match unrelated names and MUST NOT be treated as an ACE-Step integration.

Read-only raw evidence: `.tools/deep_audit_20261010/v210_comfyui_installed_node_types.json`.

Local node type support is useful for selecting templates. It does **not** mean model weights are present, license is cleared, runtime fits RTX3060 or an AI-generated film has passed full artistic QC.


## Late-discovered original film/editing repositories (Oct 10)

- ArtCraft, https://github.com/storytold/artcraft : AI-directed 2D/3D scene staging, posing and shot blocking. Film-adjacent P1. Requires an actual Blender/CineFactory interchange test; inspect repository and output rights.
- Huashu Art Motion, https://github.com/alchaincyf/huashu-art-motion : coding agent animation skill and original explainer styles. MIT program components; demo character/font/reference assets NOT presumed commercial. P1 for scripted original visual lessons.
- HeyGen TAVR, https://github.com/heygen-com/TAVR : SIGGRAPH Asia 2026 talking avatar research; developer specifies Hopper H100 80GB-class GPU, and AGPL 3.0 dependent YOLO component. Not RTX3060 deployable; R&D.
- MV-S2V, https://github.com/Szy-Young/MV-S2V : SIGGRAPH 2026 multi-view subject consistency, 14B scale. R&D; not a qualified 12GB local model.

These four bring the research registry to **96 curated entries**. As with every registry candidate, actual installed weights, cinematic quality and monetization rights remain unverified.
