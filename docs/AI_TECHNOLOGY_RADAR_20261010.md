# CINEFACTORY — AI TECHNOLOGY RADAR (2026-10-10)

**Snapshot:** 10 Oct 2026, 17:45 ICT. **Purpose:** public-source technical research for local-first commercial video/film production with RTX 3060 12 GB VRAM and 32 GB RAM. **Status:** SOURCE RESEARCH ONLY. No weights downloaded, model installed, runtime benchmark claimed, YouTube upload, paid API credits, or change to currently approved company production routes.

**Scope:** targeted, non-exhaustive discovery across official GitHub repositories, model cards, developer docs and SaaS pages. "Newest" means release or meaningful code/weights update dated near the snapshot; not repository creation age. No claims of checking every Internet repository, model or site.

## Executive findings

1. 2026-10-09: **Qwen-Image-2.1-Turbo** official 8-step image generation and editing. **MODEL LICENSE IS QWEN RESEARCH — NON-COMMERCIAL** in the public weights. HIGH RESEARCH, HOLD COMMERCIAL DEPLOYMENT.
2. 2026-10-07: **FlashML FreeVideo** enables MiniMax H3 video generation reportedly from 8 GB VRAM, including RTX 30-series int8 and preview-before-quality-rerender. HIGH LOCAL BENCHMARK PRIORITY. Its code is Apache-2.0, H3 weights use separate **MiniMax H3 Community License** with territorial/acceptable-use conditions.
3. 2026-10-09: **HeyGen HyperFrames** HTML/CSS/agent-to-video deterministic renderer, Apache-2.0. HIGH BENCHMARK PRIORITY FOR NON-3D LANES (explainers, English lessons, educational, kinetic typography). Compare Remotion's eligibility/license.
4. 2026-10-02: Lightricks **LTX-2** pipeline v1.4.2; license and large-weights requirement make it inappropriate to declare consumer 12 GB deployment without offload benchmark. Separate LTX-2.3/2.5 licenses and checkpoints by exact version.
5. 2026-09-15: **FastVideo FastH3 V2** 8-step open-weight audio+video optimization. The high-end H3 + Qwen3-VL-32B text encoder needs substantial memory/offloading; benchmark FreeVideo's constrained runtime first.
6. 2026-09-20: **Qwen-Image 2.1** 7B/10-reference/RGBA; the later Turbo variant released 2026-10-09. Powerful creative research **NOT cleared for monetized commercial use under public Research License**.
7. 2026-09-13 / Sep 26: **SolarWM** and **AlayaWorld** world models advance long-horizon interactive generation; research horizon only, not qualified film/game runtime substitute.
8. 2026: **Bernini** 1.3B renderer and 7+14B planner/edit pipeline from ByteDance; editing research candidate, do not infer entire model fits 12 GB from its 1.3B submodule.
9. 2026: **AniGen** image->fully skinned articulated 3D assets; Linux + >=18 GB VRAM; component CUBVH derives from a non-commercial Nvidia license. Do NOT deploy commercially without removing/replacing restricted dependency.
10. 2026: **OpenMOSS MOSS-TTS v1.5 / Nano / TTSD / SoundEffect v2** officially Apache-2.0 model family. Together with **ACE-Step 1.5** (MIT, small music option <4 GB according to author), best near-term free/local Sound Studio candidates.

## Structured discovery matrix

**Legend:** P0 = candidate to benchmark now; P1 = secondary benchmark; R&D = research/no deployment; HOLD = do not commercialize until licenses/hardware qualification. Hardware suitability is not a runtime result.

| Family | Repository / primary source | Primary application | 12GB Windows | License/deployment |
| --- | --- | --- | --- | --- |
| Image | https://github.com/black-forest-labs/flux2 | FLUX.2 Klein 4B concept/edit/reference | P0 | Apache-2.0 for 4B; other variants NOT automatically commercial |
| Image | https://github.com/QwenLM/Qwen-Image-2.1 | Qwen Image 2.1 / Turbo, RGBA, 10-ref | P1, benchmark only | Qwen Research License: non-commercial without separate rights |
| Image | https://github.com/krea-ai/krea-2 | Krea 2 RAW/Turbo artistic concept/LoRA | R&D/HOLD | Community model license, separate commercial terms |
| Image | https://github.com/ideogram-oss/ideogram4 | 2K typography/design and layout | R&D/HOLD | Ideogram 4 Non-Commercial weights |
| Image | https://github.com/Tongyi-MAI/Z-Image | Realistic image, distilled 6B family | P1, confirm exact checkpoint | Reinspect model card before commercial production |
| Image | https://github.com/Comfy-Org/ComfyUI | Pipeline execution/graph/VRAM offload | P0 infrastructure | Open source; model weight terms separate |
| Video | https://github.com/FlashML-org/FreeVideo | Consumer-GPU H3 video through VDN/INT8 | P0 benchmark | Apache code; H3 weights community terms |
| Video | https://github.com/bytedance/Bernini | Generative editing / semantic planner | P1 controlled experiment | Audit exact submodel/checkpoint license, requirements |
| Video | https://github.com/hao-ai-lab/FastVideo | FastH3 / FastWan / inference optimization | P1 after resource proof | GPU/model/weights per supported variant |
| Video | https://github.com/Wan-Video/Wan2.2 | Open video generation and animation | P1 constrained variant | Standard 5B path ~=24GB VRAM; local 12GB only optimized/offload benchmark |
| Video | https://github.com/Lightricks/LTX-2 | LTX 2.x audio+video, control and effects | R&D | Heavy storage/VRAM and version-specific community terms |
| Video | https://github.com/MeiGen-AI/InfiniteTalk | audio-driven long talking/dubbing video | P1 | Check checkpoint rights/VRAM; not rigged original animation replacement |
| Video | https://github.com/meituan-longcat/LongCat-Video | LongCat Video Avatar v1.5 | P1/R&D | Voice-driven expressive character, not guaranteed local budget |
| Video | https://github.com/AlayaLab/AlayaWorld | Interactive long-horizon world model | R&D | 2026-09 release, highly experimental video |
| Video | https://github.com/Junchao-cs/SolarWM | Streaming long-horizon world-model open data | R&D | Large models and datasets, not 12GB operational target |
| Video | https://github.com/mvp-ai-lab/RAVEN | Causal / streaming Wan/H3 acceleration | R&D | H3 24GB path, preview weights immature |
| 3D | https://github.com/VAST-AI-Research/UniRig | skeleton/skin prediction | P1 | Author reports 8GB minimum; review terms/model/dependencies |
| 3D | https://github.com/VAST-AI-Research/AniGen | mesh+skeleton+skin from image | R&D/HOLD | Linux >=18GB; CUBVH noncommercial component |
| 3D | https://github.com/VAST-AI-Research/SkinTokens | learned skeletal skinning/token rig | R&D | >=14GB VRAM |
| 3D | https://github.com/microsoft/TRELLIS.2 | image to complex PBR mesh | R&D | H100 benchmarks are NOT RTX3060 results |
| 3D | https://github.com/microsoft/World-R1 | 3D-aware generative video physical consistency | R&D | Research not a production 3D renderer |
| 3D | https://github.com/NVIDIA/Audio2Face-3D | audio-driven blendshapes facial performance | P1 | Third-party model and NIM service licenses separate |
| 3D | https://github.com/OpenX-Inc/clay | open self-hosted asset pipeline (model, LOD, rig) | P1 | Inspect real dependencies and rights; not magic one-pass mesh |
| 3D | https://github.com/ig-shadow-walker/AlphaPlugin-Blender | Blender AI modeling/retopo/rigging | R&D/HOLD | Some API actions consume credits |
| Audio | https://github.com/OpenMOSS/MOSS-TTS | TTS longform/dialogue/realtime/SFX | P0 | Apache-2.0 model family, use only owned/consented voices |
| Audio | https://github.com/mudler/moss-tts.cpp | local portable GGUF TTS backend | P1 | MIT engine; original model terms still apply |
| Audio | https://github.com/QwenLM/Qwen3-TTS | voice generation/cloning/design | P0 | Check exact model card and voice rights |
| Audio | https://github.com/resemble-ai/chatterbox | emotive TTS | P0 | MIT repo; verify checkpoint and input voice rights |
| Audio | https://github.com/ace-step/ACE-Step-1.5 | music generation and sound design | P0 | MIT; base lightweight, XL needs >=12GB with offload |
| Editing | https://github.com/heygen-com/hyperframes | deterministic HTML-to-video, agent skills | P0 | Apache-2.0; compare effects/subtitles/frame accuracy against Remotion |
| Editing | https://github.com/remotion-dev/remotion | programmatic video using React | EXISTING | Free for individuals and businesses <=3 employees; company terms otherwise |
| Editing | https://www.blackmagicdesign.com/products/davinciresolve | color/edit/sound/finishing professional | R&D / optional | Commercial application; executor qualification required |

## SaaS frontier as QUALITY BENCHMARK, not free local factory

- https://seed.bytedance.com/en/seedance2_5 — Seedance 2.5, official up to 30s single output, references/editing/extension. No free-credit assumption.
- https://deepmind.google/models/veo/ — Veo 3.1 / Flow, audio/video, characters and camera references; source is vendor statement.
- https://runwayml.com/ — Runway Gen 4.5 and editing; paid API/service model.
- https://klingai.com/ — Kling video/cloud benchmark; check exact version API/rights.
- https://www.adobe.com/products/firefly.html — Firefly + partner video models including Veo, Kling 3, Ray, Runway.
- https://www.krea.ai/ — Krea SaaS; differs from open-weight research model licensing.
- https://www.heygen.com/ — hosted avatar/video; independent of Apache HyperFrames framework.
- https://www.autodesk.com/products/maya/overview — Maya 2026.1 MotionMaker and Bifrost procedural rigging: key professional benchmark.

## Production routing and economic decision

CineFactory must choose by video and shot **source truth**:
- Minecraft/Roblox scripted original film: Blender deterministic rigs/camera/scene continuity first; local image AI for concept; audio AI for licensed voices; video diffusion for approved background/VFX shots with art QC.
- Real Minecraft/GTA gameplay/livestream: real authorized game-runtime recording, not invented AI "real live" footage.
- Long Slide: deterministic Blender/game physics and original animated animals; auto 3D generation is optional, not authority over exact geometry.
- Audio storytelling: MOSS-TTS / Chatterbox / Qwen3-TTS, Audio QC and original music license.
- ASMR/Fishing/Rain: authentic owned/cleared footage and audio; AI postproduction optional, do not create fake provenance.
- Explainers/Daily English: HyperFrames vs Remotion head-to-head; compare subtitle rendering, video encoding, visual fidelity and video seconds produced per GPU/CPU hour.

Quantify *accepted footage* per hour and $ per accepted minute, not nominal seconds generated in a model demo.

## Proposed A/B technical benchmarks (NOT yet performed)

- P0A Image: FLUX.2 Klein 4B against Qwen 2.1 Turbo **research only**; original Minecraft character at 3 angles, same skin across expressions, CC0/original reference; measure drift and actual license.
- P0B Audio: MOSS-TTS Nano/v1.5, Chatterbox, Qwen3-TTS on same 90-second English script, character voice identity and pronunciation, with rights-qualified references.
- P0C Music: ACE-Step 1.5 on 30s tension/fantasy/background loop; inspect motif continuity, clean looping, rights, loudness/peaks.
- P0D Video: FreeVideo H3 on RTX 3060 12GB for 5s original motion, preview and max modes; measure **peak VRAM, system RAM, total E2E time, output frame count, facial drift, video + audio quality, model terms**. Only then compare Bernini and Wan constrained modes.
- P0E Programmatic video: HyperFrames vs existing FFmpeg/Remotion on 60s visual-English explainer with captions and animated graphics; quality and performance measured after actual rendered MP4.
- P1 3D: UniRig real geometry & Blender import/weight deformation only after original 3D asset and license checks. AniGen/SkinTokens require GPU upgrade or separate approved remote budget.
- P1 whole film: only after original character-led 30–60s pilot accepted, build and independently accept 8–10min film with audio, story and rights. No technical self-certification.

## Evidence links for date/license-critical claims

- Qwen new release 2026-10-09: https://github.com/QwenLM/Qwen-Image-2.1 ; license https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE
- FreeVideo 2026-10-07 and model terms: https://github.com/FlashML-org/FreeVideo
- HeyGen HyperFrames 2026-10-09: https://github.com/heygen-com/hyperframes
- LTX update 2026-10-01: https://github.com/Lightricks/LTX-2/commit/main ; license https://github.com/Lightricks/LTX-2/blob/main/LICENSE
- FastVideo 2026-09-15: https://github.com/hao-ai-lab/FastVideo
- AlayaWorld 2026-09-26: https://github.com/AlayaLab/AlayaWorld
- SolarWM 2026-09-13: https://github.com/Junchao-cs/SolarWM
- Krea weights community license: https://github.com/krea-ai/krea-2/blob/main/docs/KREA-2-COMMUNITY-LICENSE
- Ideogram 4 public noncommercial: https://github.com/ideogram-oss/ideogram4
- AniGen GPU/license: https://github.com/VAST-AI-Research/AniGen/blob/main/AGENTS.md
- MiniMax H3 Comfy weights size/licensing: https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_multiframe_reference.json
- MOSS-TTS 2026 and Apache terms: https://github.com/OpenMOSS/MOSS-TTS
- ACE-Step 2026 and MIT: https://github.com/ace-step/ACE-Step-1.5
- Autodesk MotionMaker: https://help.autodesk.com/cloudhelp/2026/ENU/Maya-WhatsNew/files/GUID-17799E4D-3691-41B1-8B19-6D6B7E281393.htm
- Official Seedance 2.5 launch 2026-07-31: https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5
- Remotion license: https://github.com/remotion-dev/remotion/blob/main/packages/core/LICENSE.md

**Verdict**: a source-backed research inventory, NOT a proven ranking of all Internet AI systems; GPU/model benchmarks and 3rd-party commercial licenses still require validation. Production routes v209 remain untouched.


## CRITICAL ADDENDUM 10/10/2026: MiniMax H3 / ComfyUI / FreeVideo are three separate layers

**Correction:** MiniMax H3 is a first-class source video model, not just a feature of FreeVideo.

### 1. MiniMax H3 (original model and weights)
Official: https://github.com/MiniMax-AI/MiniMax-H3 and https://huggingface.co/MiniMaxAI/MiniMax-H3
- MiniMax announced public weights August 3, 2026. 4–15s 24fps synchronous stereo audio, baseline 768px short edge; 2K uses additional H3-Regenerate-2K workflow, not an automatic property of consumer GPU inference.
- FL2VA: text, first-frame, last-frame, first+last frame. Ref2VA: distinct checkpoint supporting <=9 reference images, <=3 reference videos and <=3 reference audios, 12 mixed media files at most.
- Commercial warning: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE . Its Community License excludes USA, EU, UK and South Korea from the Applicable Territory, and Section V(4) restricts use/distribution of both model and outputs outside the Territory. Worldwide YouTube/US RPM channels **MUST HOLD pending licensor/legal review**; merely rendering on a Vietnam PC does not prove global permission. Commercial services above $20m annual revenue need separate written authorization. Also obey AUP and notices.

### 2. ComfyUI core and its actual installation
Official: https://github.com/Comfy-Org/ComfyUI and https://github.com/Comfy-Org/workflow_templates .
- Public templates include T2V, I2V, R2V for MiniMax H3, with native video+audio decode and model family-specific checkpoints.
- Read-only check on user's Windows machine: ComfyUI 0.38.0 at http://127.0.0.1:8188 HTTP 200, RTX 3060 ~12GB; object_info advertises six built-in MiniMax H3 nodes: EmptyMiniMaxH3LatentAV, MiniMaxH3ImageToVideo, MiniMaxH3AddGuide, MiniMaxH3ReferenceToVideo, MiniMaxH3SigmaShift, MiniMaxH3FunControlNetApply.
- **No MiniMax H3 / VDN weight files found** under .tools/ComfyUI/models by matching names, and **no FreeVideo/H3 custom-node folder found** under .tools/ComfyUI/custom_nodes. Node availability is NOT checkpoint readiness or a successfully rendered H3 film. Large Qwen3-VL text encoders may impose high RAM/VRAM requirements.

### 3. FreeVideo (hardware optimization and ComfyUI plugin)
Official: https://github.com/FlashML-org/FreeVideo .
- Implements a local MiniMax H3 / OpenVDN 8-step acceleration runtime, streamed weights and adaptive precision. Author reports 8GB minimum VRAM, 16GB RAM; Oct 7 update adds RTX 30-series INT8 and preview-first two-pass rendering. The RTX 3090 speed claim does NOT establish RTX 3060 throughput.
- Adds Windows installer, native ComfyUI custom node/workspace, LoRA, four quality levels and reproducible embedded workflow metadata.
- FreeVideo CODE Apache-2.0; H3 / VDN weights under separate MiniMax H3 Community License; ComfyUI and other dependencies have their own license requirements. See https://github.com/FlashML-org/FreeVideo/blob/main/THIRD_PARTY_NOTICES.md .

### Mandatory CineFactory acceptance
1. Read exact model, output, commercial and worldwide-territory rights BEFORE any monetized release.
2. With owner approval only, benchmark one original 3–5s shot on RTX3060 at bounded quality, using correct FL2VA or Ref2VA weights and no paid API.
3. Record peak VRAM, RAM, disk, generation time, frames/audio sync, retakes and source hashes. Compare native ComfyUI against FreeVideo quantized implementation only after both workflows actually load.
4. Preserve original Blender scene, rig, acting and camera contracts; never replace 8–10min cinematic quality with disconnected AI-generated 5s demos.
