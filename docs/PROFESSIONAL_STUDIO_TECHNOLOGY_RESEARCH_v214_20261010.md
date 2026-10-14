# CineFactory Studio Technology — October 2026 evidence review (v214)

Review of the user-provided Vietnamese **"Bách khoa toàn thư: kho vũ khí công nghệ"** (self-dated October 2025, 711 text lines). The source includes 18 actual sections, although its table of contents lists only 17. It mixes genuine tools, marketing slogans, former product names, hardware, paid services, research repos, proprietary non-downloadable in-house systems, and workflow examples. This document does **not** verify every individual item in that encyclopedia.

## 1. Corrections that must precede any integration

- **Modo**: Foundry announced November 7, 2024 that development will wind down after Modo 17.1. Never plan a new long-term pipeline around it. Source: https://www.foundry.com/news-and-awards/foundry-winds-down-modo-development
- **Ziva VFX**: Unity discontinued active sale and support April 2, 2024; surviving incumbent licenses are not new studio adoption. Source: https://unity.com/blog/news/update-about-ziva
- **Clarisse iFX**: media reports cite Isotropix support confirming cessation in 2023; treat as legacy/discontinued, avoid new dependence. Source: https://www.cgchannel.com/2023/04/isotropix-may-have-discontinued-clarisse-and-angie/
- **RealityCapture**: renamed **RealityScan** in June 2025; its old licensing server closed August 3, 2026. Sources: https://www.realityscan.com/news/realityscan-20-new-release-brings-powerful-new-features-to-a-rebranded-realitycapture and https://www.realityscan.com/news/the-realitycapture-legacy-licensing-server-will-close-down-on-august-3
- **Moxion**: **not retired**; renamed **Autodesk Flow Capture**, now incorporating PIX technology. Source: https://www.autodesk.com/products/flow-capture/overview/
- **Adobe Firefly**: Adobe's commercial-safety assertion is a vendor claim, not blanket guaranteed immunity from rights conflicts; scope of enterprise IP indemnification differs from generic consumer plans. Source: https://www.adobe.com/ai/overview/firefly/gen-ai-approach.html
- **Maya mandatory, Nuke supreme, 10x guaranteed productivity**: subjective/marketing claims rather than suitability tests; no universal commercial production prerequisite follows.
- **Depth Anything V2**: SMALL model weights Apache-2.0, Base/Large/Giant CC-BY-NC-4.0 per project README. Do not treat every weight as commercially usable. Source: https://github.com/DepthAnything/Depth-Anything-V2
- **Prism Pipeline 2**: Free core is LGPL and commercially usable but important USD, Unreal, Resolve and Kitsu plug-ins are Plus/Pro, not in the Free tier. Source: https://prism-pipeline.com/docs/latest/general/licensing/
- **Houdini Indie**: commercial usage has revenue/funding thresholds; current SideFX terms control. Source: https://www.sidefx.com/faq/indie-new/
- **OpenTimelineIO**: interchange of *cut timing and media references*, not a package of media or a complete video editor. Source: https://github.com/AcademySoftwareFoundation/OpenTimelineIO
- **No universal production stack**: editorial, 2D motion, stylized 3D, original game capture and real sound recording require different backends.

## 2. Existing 96 vs prioritized discovery backlog

Do not change the immutable v210 96-item reviewed baseline or silently assert installation. Extra research-only rows live in `config/technology/professional_studio_research_v214.json`. Every row is a *candidate*, not an installed backend, benchmarking receipt, cleared model weight, license, or working MCP connection.

### Near-term quality/speed upgrades (recommend tests, not mass installs)
- OpenTimelineIO → internal edit interchange for FFmpeg/Remotion, with correct FPS/timebases, adapter QA.
- OpenColorIO + ACES 2 → consistent scene-linear/color transforms between Blender shots, generated imagery and finishing. Test on identical graded reference stills.
- Prism Pipeline 2 **Free** or custom in-house minimal shot/asset publishing → versioned workfiles, named output receipts, rollback and no more accidental cross-scene asset drift.
- Open RV → frame-accurate **dailies** review and QC; alternatively retain existing FFmpeg/QC if OpenRV dependencies are too burdensome.
- Meta SAM 2 / Depth Anything V2 **Small** → optional masking and scene-aware reference guidance on rights-cleared footage, with actual VRAM, render time and quality verification.

### Second wave
- Kitsu or AYON → only if CineFactory's existing 26-department orchestrator suffers demonstrable task/asset/approval handoff gaps; don't create a duplicate source of truth.
- MaterialX → only when multi-DCC shader interoperability matters; existing OpenUSD is already in the 96 baseline.
- Gaffer → optional lighting/lookdev for higher-fidelity 3D scenes; not essential to stylized voxel pipeline.
- OpenCue → only after multiple independent render machines exist; avoid deploying a farm controller to solve one-GPU job scheduling.
- RealityScan → only for real-world environments/product footage requiring 3D acquisition; little direct benefit to voxel Minecraft.
- Depth Anything V2 Base/Large → HOLD for commercial deployment under CC-BY-NC without a separate valid license.

## 3. Per-niche director's routing

| Niche or format | Core production method | Specialist experiments | Avoid |
|---|---|---|---|
| Minecraft / Roblox episodic film | Blender persistent worker, rig/action/scene templates, FFmpeg + audio QC | OTIO, color management, scoped audio-to-face, VFX layering, optional procedural tools | Random per-shot AI video if it changes character identity |
| Animal long-slide | Blender procedural obstacle/camera/motion library; deterministic physics; fast assembly | MaterialX/OpenRV only if the pilot indicates a gap | Cloud image-to-video for each repeated slide |
| GTA/gameplay channels | Lawfully captured actual runtime, programmable video editor and sound design | OpenTimelineIO, shot detection/audio QC | Pretending a rendered animation is real gameplay |
| Preschool 3D musical | Consistent original characters, directing, precise lip-sync, choreo/rigging, music, episodic world bible | Better lighting/color, mocap retargeting, facial animation | Clone branded characters, rapid random scene generation |
| Real ASMR hands + objects | Controlled mic/room, authentic stereo sound, visual capture, FFmpeg, repair/QC | selective SAM2 masking and low-noise processing | Synthetic Foley falsely described as real |
| Rain/white noise | Owned/cleared ambience, transparent loops, audio seam and loudness validation | Layering and royalty-checked synthesis | Audible repetitive seams and misleading copyrighted loops |
| Audio stories for seniors | Reviewed original script, rights-cleared TTS, sound/music, long-form audio QC | OTIO and voice/pacing A/B | Reading copyrighted books verbatim without permission |
| Quiet fishing | Real field camera and capture-led documentary assembly | Stabilization, mask/cleanup for legally acquired footage | Video diffusion posing as authentic wildlife footage |
| English explainer | Remotion / FFmpeg procedural motion, reviewed narration & packaging | OpenTimelineIO, lightweight asset pipeline | Full 3D character rig without a storytelling need |

## 4. Agency standards to borrow, not necessarily buy

From Maya/Houdini/Nuke/Katana/Mari, borrow *reviewable shot stages, workfile versions, reproducible renders, procedural assets, AOV/multi-pass output, color managed interchange, shot-level quality gates, and clear source/rights provenance*. 
From Autodesk Flow Production Tracking, Kitsu, AYON and Prism, borrow *shot/asset/department ownership, approvals, dailies, status and rollback* without blindly importing multiple competing orchestration databases.
From motion/VFX teams borrow *contact sheets, rig/skin QC, object interaction, blocking/eye lines, continuity, timing/audio sync, physical causality, asset fidelity*.
From hardware/cloud guides, defer expensive farms until a measured queue/GPU bottleneck warrants one.

## 5. Claude / MCP supply chain

The 2025 source names generic "Blender MCP", "Maya MCP", "ComfyUI MCP" etc without stable verified maintainer/release identity. **Do not treat a name as a trusted installable server.** 
Research vendor releases, Claude Code / Agent SDK / plugin changes and the official MCP Registry. Record source URL, publisher, transport, code permissions, requested filesystem/network access, license, dependencies, sandbox profile, version hash, security review and successful isolated smoke test.
Anthropic notes local plugins may execute skills/hooks/agents/MCP on the operator's machine: https://support.claude.com/en/articles/13837440-use-plugins-in-claude .
Existing v212 watcher follows selected fixed official sources; the v213 strategy is read-only. This new 18-item curated backlog does **not** install tools, schedule new tasks, spend paid credits or grant any auto-promotion.

## 6. Measurable pilot acceptance

For each niche and each relevant difficult shot:
1. Reconfirm **full competitor visual + audio/timecode observations**; private CTR, retention, RPM and undisclosed production tool remain UNKNOWN.
2. Test at least 2 plausible methods on the SAME original 10–30 s shot, same machine, same resolutions/quality rubric, recording software/model versions and GPU utilization.
3. Preserve character identity, spatial consistency, acting, intended emotional timing, speech/lip sync, material/lighting design, audio mix and rights.
4. Only benchmark speed after passing quality gate. Measure **accepted finished seconds per wall hour**, human rework, peak VRAM, actual cost, repeated-run stability and failure rate.
5. Require human/owner approval, revert path and regression suite before activating a changed tool.
6. Report `SOURCE_REVIEWED`, `INSTALLED`, `EXECUTABLE`, `BENCHMARKED`, `QUALIFIED`, and `APPROVED` as separate statuses. Never claim cinematic superiority without real comparable renders.

This document is a scoped, source-backed **October 2026 verification pass**, not an exhaustive validation of every 2025 catalog line. Resume future research when new niche demand or official-source changes justify it.
