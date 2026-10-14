# CineFactory v220 — Claudе Code software/MCP expansion (2026-10-10)

## Executive technical finding

Claude Code can orchestrate dozens of **different integration types**; do not conflate:
- **Official built-in MCP**: Unreal Engine 5.8 (EXPERIMENTAL, Epic); Cinema 4D 2026.4 (Maxon); Unity 6+ via Unity CLI (EXPERIMENTAL); Boris FX Silhouette 2026. These ship with the host app/license.
- **Official hosted MCP**: Runway media generation, Runway Dev administrative/API project portal, ElevenLabs Creative, Magnific, fal.ai, Shotstack. Each provider has different permissions, OAuth/token security and paid generation obligations.
- **Official open-source vendor MCP**: Comfy-Org/comfy-mcp (local beta, explicit paid partner calls and local custom node risks).
- **Community MCP over an official scripting API**: DaVinci Resolve, Nuke, Houdini, Maya, Adobe Premiere Pro, After Effects, Photoshop, REAPER, Audacity, Kitsu, Natron and Godot. MCP existence proves a public code project; installation reliability/license/production quality remain UNVERIFIED on CineFactory.
- **No official MCP**: Autodesk Flow Production Tracking explicitly said as of June 22, 2026 not yet available (still has REST/Python APIs); not to be confused with **Google Flow video creation**.

All 27 records, source URLs and risk descriptions: `config/technology/creative_software_mcp_landscape_v220.json`. This catalog re-includes some older v216/v217/v219 researched options as context; **27 is not the number of new installations or entirely new distinct technologies**.

## Highest-impact candidate combinations

| Priority and department | Suggested practical combination | Distinct incremental value | Conditions |
|---|---|---|---|
| P0 Comfy Image/VFX | Existing 127.0.0.1:8188 local ComfyUI API + CineFactory read-only gateway; evaluate Comfy-Org MCP | Actual AI image/video workflows, node graph/model discovery, without replacing local worker | Currently only GET integration verified, not model generation; safe allowlisted local submission requires independent staging |
| P0 Advanced 3D/cinema | Epic Unreal 5.8 with official experimental MCP | Large realtime procedural scene/virtual camera/lighting and game runtime, especially GTA-style content | Engine actually installed and render-capable, 12GB GPU QC, asset licenses, sandbox and clip benchmark |
| P1 3D/mograph | Maxon Cinema4D 2026.4 native MCP | Procedural motion, reusable animation and Redshift, better typed permission controls | Paid seat, native tool groups/undo/token and vendor install tested |
| P1 2D/game runtime | Unity 6 CLI MCP / official plugin | Native game objects and runtime automation, not necessarily superior to Blender | Project format decision, Unity license, evaluate vs existing runtime |
| P1 Roto/VFX | Boris FX Silhouette 2026 native MCP, Houdini fxhoudinimcp, Nuke MCP | Roto/paint/cloth/fire/smoke/comp nodes | Substantial commercial licenses; isolate Python, confirm ROI in a genuinely VFX-heavy shot |
| P1 Audio | Existing audio chain + REAPER MCP; optional ElevenLabs | Recording/frequency/denoise/mastering and dubbing; separate local vs paid cloud | REAPER installed or pilot, loudness QC, voice/music commercial rights |
| P1 Editorial | FFmpeg/Remotion core + DaVinci Resolve community MCP | Color/Finishing/Fusion/Fairlight when these beat local video editors | DaVinci actual install/OS and external scripting; no blind dependency |
| P1 Asset/shot management | Existing CineFactory company truth + Kitsu/Gazu API + community MCP if gaps | Task/asset/shot/version/dailies review | Avoid replacing source of truth without a migration plan |
| P2 Hero cinematic clips | OpenArt / Higgsfield / Runway creative / Magnific / fal.ai cloud MCP | Specialized premium generative scenes and photoreal enhancements | Credits/paid plan, license, account permissions, per-shot strict budget and image/audience QC |
| P2 Mass editorial | Shotstack MCP/CLI | Cloud scalable edit JSON, cloud jobs, templated export | Compare total costs/feature-quality with FFmpeg/Remotion already owned |

## Critical source confirmations and caveats

1. **Unreal 5.8 official** https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available ; not Unreal 6 release.
2. **Cinema 4D native, Sept 30 2026** https://www.maxon.net/en/article/maxon-adds-support-for-cinema-4d-mcp-server ; selective tool permissions, token authentication, optional Python, undo/audit.
3. **Unity 6+ official** https://unity.com/features/ai ; `unity mcp configure claude-code` from Unity CLI docs https://docs.unity.com/en-us/unity-cli/release-notes.
4. **Boris FX Silhouette 2026 official** https://borisfx.com/products/silhouette/ ; native RPC/MCP for roto/paint/frames; powerful executable privileges require isolation.
5. **REAPER community** https://github.com/xDarkzx/Reaper-MCP ; community stated local Lua IPC. Do not claim 181 tools benchmarked by us.
6. **DaVinci Resolve community** https://github.com/lordhoell/davinci-resolve-mcp ; author exposes hundreds of tools, software/version license not checked locally.
7. **Adobe AE community** https://github.com/solomondivyananth/aftereffects-mcp ; supports rendering a frame and inspecting before edits, but can execute AE expressions. **Adobe Premiere community** https://github.com/josegroove/adobe_premiere_pro_mcp author validation Mac only; Windows unverified.
8. **Runway generation MCP** https://help.runwayml.com/hc/en-us/articles/51931843164691-Connecting-to-Runway-MCP is paid credits, no Explore Mode. **Runway Dev MCP** https://docs.dev.runwayml.com/guides/mcp/ is a distinct account/model catalog/configuration integration.
9. **Magnific MCP** https://www.magnific.com/ai/docs/magnific-mcp requires paid plan. **Generation/edit/upscale spends credits** even with web unlimited, but viewing balance/history is free.
10. **fal.ai MCP** https://blog.fal.ai/connect-your-ai-to-1-000-models-with-the-fal-mcp-server/ has a large cloud model catalogue, must bill/test.
11. **ElevenLabs** https://elevenlabs.io/mcp supports speech, music, SFX, dubs, images and video; company account, output commercial rights and spend need verification.
12. **Shotstack** https://shotstack.io/docs/guide/agents/mcp-server/ has official MCP, CLI and Skills; draft preview without API key, finished export billed separately.
13. **Kitsu MCP** https://github.com/huikku/kitsu-mcp community atop Zou/Gazu API. `CGWire` does not claim this fork as official.
14. **Autodesk Flow Production Tracking** https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Does-Flow-Production-Tracking-plan-to-implement-or-support-an-MCP-connection-for-AI-integrations.html June 2026 statement: official MCP not available then.
15. **Comfy Partner MCP** https://github.com/Comfy-Org/docs/blob/main/agent-tools/partner-mcp.mdx is PRIVATE PREVIEW as of source, not public ComfyUI local MCP.

## How CineFactory Claude can research these tools now

```powershell
cd 'C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6'
python -m cinefactory.cli creative-mcp-landscape --minor-niche minecraft_story_adventure --department VFX
python -m cinefactory.cli creative-mcp-landscape --minor-niche long_slices_game --department PRODUCTION
python -m cinefactory.cli creative-mcp-landscape --minor-niche minecraft_story_adventure --department AUDIO
claude
```

After Claude Code project MCP trust approval, call `studio_software_mcp_research` for the same niche and department. It returns source references and gates, not executors. Existing CineFactory v219 **actually connected local ComfyUI only via read-only localhost HTTP GET**; neither third-party apps nor remote services were installed or given paid permissions in this v220 research expansion.

## Next technical delivery for a genuinely high-end automated studio

- Verify local installed software, licensing and reachable API before adding any external MCP config.
- Create **media-production sandbox** with permission allowlists, task IDs, output hashes, irreversible-op confirmations, limited file trees, no network secrets and model/credit deny-by-default.
- Benchmark scene apples-to-apples: USD rigging vs realtime, sound editing, video motion + camera coverage, color and compositing, asset reuse. Measure accepted seconds per hour and real retouch/rework.
- Add only those MCPs that provide a measurable advantage over existing CineFactory Blender workers, ComfyUI native API and FFmpeg/Remotion. Keep 96 baseline and releases unchanged by research.
