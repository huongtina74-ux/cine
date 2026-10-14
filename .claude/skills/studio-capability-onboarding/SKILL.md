---
name: studio-capability-onboarding
description: Safely stage newly researched creative software, official or community MCP, and AI cloud providers as production capabilities after verification.
---
# CineFactory v221 — External software onboarding

Use `company_connector_inventory`, `company_scene_connector_plan`, `studio_software_mcp_research`, `comfyui_local_status` and `niche_production_brief` in Claude Code. All **27** reviewed software/MCP candidates are now cross-referenced by CineFactory scene and owning department; none is installed or authorized by the registry.

Process each proposed installation in this order:
1. Confirm exact app version, local process/runtime, provider identity, license, hardware/GPU and appropriate audience/creative use. NOT_ON_PATH != NOT_INSTALLED.
2. Separate **official native**, **community server**, **local beta** and **paid remote**. Claude Desktop extension process != Claude Code MCP connection.
3. Review scripts/subprocesses/arbitrary bpy or Python, remote file and account access, credentials, downloads, auto-updates, backup and rollback. Keep secrets out of Git.
4. Require explicit owner authorization before paid API credentials, model downloads, untrusted third-party installations or production backend modifications.
5. Register the approved server only in a controlled test context, prove MCP initialize/list/call, and run sandbox pilots with sample ORIGINAL footage and audio.
6. Benchmark footage identity, camera/lighting continuity, dialogue/foley/audio, commercial rights, GPU/VRAM, retries, accepted seconds/hour, costs and QC. Quality first; speed second.
7. Promote only verified versioned adapters after regressions, approval and rollback test. Otherwise keep RESEARCH_ONLY.

Keep the existing Blender 4.5 worker, local ComfyUI API and FFmpeg/Remotion production paths unchanged unless the new tool measurably improves the particular shot. The official Comfy-Org MCP and Blender Lab MCP may execute paid partner nodes or arbitrary Python respectively; both require special review. Do not equate an available OpenArt/Higgsfield MCP URL to permitted paid generation.
