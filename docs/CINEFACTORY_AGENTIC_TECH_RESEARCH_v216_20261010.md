# CineFactory v216 — October 2026 Agentic/VFX research verification

> **Superseded point (v217 verification, 2026-10-10):** There IS now an official experimental Blender Lab MCP server at https://www.blender.org/lab/mcp-server/ , requiring Blender 5.1+. The v216 warning that community repos cannot be treated as Blender Foundation official still applies specifically to those third-party repos. The official server itself runs arbitrary generated Python without safeguards and is not approved for CineFactory 4.5 production. See `docs/CREATOR_STUDIOS_OPENART_HIGGSFIELD_FLOW_MCP_V217_20261010.md`.

Date: 2026-10-10. Scope: the user's 109-line Oct 2026 Agent Leap brief, retained at `config/technology/agent_leap_user_study_20261010.md`. Distinguish **user assertions** from **official or repo self-reports** and verified runtime benchmarks. The brief claims work by four researchers; no individual methodology or independent measurements were attached.

## Facts corrected against official sources

1. **Sora sunset CONFIRMED**: OpenAI states web/app discontinued April 26, 2026 and API September 24, 2026. It does **not** corroborate the brief's asserted causal explanation regarding production pipeline control. https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation
2. **FLUX 3 PARTIALLY CONFIRMED**: BFL announced a multimodal FLUX 3 early access preview July 23 2026, generating joint audio/visual content. No evidence that downloadable local weights or end-to-end production on RTX 3060 12GB is available. https://bfl.ai/blog/flux-3-mimic
3. **Runway Gen-4.5 CONFIRMED SAAS**: official documentation shows paid usage (12 credits/second) and typical generation duration 2–10 seconds. No assumption of free/long-film production. https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5
4. **UE6 IN DEVELOPMENT, NOT A CONFIRMED PRODUCTION RELEASE**: June 2026 Epic roadmap says Unreal 6 is in development. UE5.8 is the released product. Therefore hold UE6 scene-aware full fidelity claim. https://www.unrealengine.com/news/the-road-to-ue-6 and https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available
5. **Houdini 22 MENTIONED BY SIDEFX**, but exact claims like default ONNX Native Inference require release-note confirmation. https://www.sidefx.com/
6. **Maya MotionMaker CONFIRMED** in official Maya 2026 docs; the cited 80% rig compression number was not verified. https://help.autodesk.com/cloudhelp/2026/ENU/Maya-MotionMaker/files/GUID-473B9D09-124C-4A5C-94F8-F3B4B89FAB18.html
7. **Nuke 17.0v4 CONFIRMED** released 2026-07-28, but no validation here of SmartRoto 4x, BigCat or native 4D splat support. https://learn.foundry.com/nuke/content/release_notes/17.0/nuke_17.0v4_releasenotes.html
8. **KHR_gaussian_splatting**: Khronos' February 2026 baseline extension release candidate explicitly supports **3D** Gaussian splats in glTF 2.0. It does not establish a standardized 4D temporal splat extension. https://www.khronos.org/news/press/gltf-gaussian-splatting-press-release
9. **Figma official MCP CONFIRMED** in vendor docs. It is optional and has account/client/paid feature gates. This does not establish Blender Foundation “official Blender MCP”. https://developers.figma.com/docs/figma-mcp-server/
10. Claim of **40%–75% power savings via agents** has no controlled measurement and remains unsupported.

## Repo vetting snapshots

- **P0 research**: `artokun/comfyui-mcp` (MCP, live workflow editing), `deepbeepmeep/Wan2GP` (local video-image-audio engine), subject to dependency, model license and 12GB VRAM QC.
- **P1 research**: `dcc-mcp/dcc-mcp-core` (multi-DCC), `sebastianstarke/AI4Animation` (animation methodology), `dramaclaw/dramaclaw` (script-to-film patterns), `NVIDIA-Omniverse/usd-optimize`, `GraphiteEditor/Graphite`, `pbakaus/impeccable`, official Figma MCP; do not install without provenance assessment.
- **HOLD security**: `6xvl/blender-mcp` README states forced code updates on Blender startup without a default opt-out. Do not use on production machine unchanged.
- **HOLD license review**: `RFingAdam/mcp-blender` repository page is labeled AGPL-3.0 while README says MIT. Establish true license/submodule rights from pinned checkout before integration.
- **R&D secondary**: Maya, Houdini, Nuke community MCPs. Actual DCC executable and commercial license are prerequisites; there is no benefit from an MCP bridge to unavailable software.
- The claim “Official Blender MCP” is **not** evidence of Blender Foundation endorsement. Github existence verifies an available project page, not security, tool counts, stability or RTX 3060 performance.

The frozen backlog: `config/technology/agentic_research_verified_v216.json` lists 24 scoped reference entries, including already-known 96 family entries and 10 claim assessments. **24 is a curated candidate count, not all distinct tools in the original brief.** Original brief is archived without omission.

## How to use in CineFactory

Existing registry **96 remains unchanged**. Prior v215 comprehensive knowledge still holds 477 indexed research references. v216 adds source-graded *R&D-only* candidates to `niche-technology-plan`, with a standalone CLI:

```powershell
python -m cinefactory.cli agentic-technology-review --minor-niche minecraft_story_adventure --department EDITORIAL
python -m cinefactory.cli agentic-technology-review --minor-niche long_slices_game --department RND
python -m cinefactory.cli niche-technology-plan --minor-niche minecraft_story_adventure
```

Workflow gates per niche:
- Observe actual legally authorized competitor video+sound, annotate timecodes and study opening/action/acting/camera/light/material/audio/edit.
- Break into specific scene requirements, then compare existing Blender worker, ComfyUI APIs, FFmpeg/Remotion with candidate MCP/agent technologies; do not assume third-party repo knows whole-video story automatically.
- For any external MCP, static security review first: pin commit/hash, disable arbitrary auto updates, network/file allowlist, untrusted Python execution, credentials, model downloads, plugin hooks and remote write privileges. Run isolated test in disposable working directory.
- Generate a **same-difficult-shot** pilot. Record artifact hashes, quality hard gates, accepted finished seconds/hour, rework, cost, VRAM, license, reproducibility. Select quality qualified methods before speed.
- Human approval is required for new dependencies, install, API credits, backend change and commercial release.

No repo cloned, software installed, model downloaded or paid API called; statuses are references for investigation. The existing daily technology watch covers selected fixed sources but is not an exhaustive scan of all new repos or SaaS.
