# CineFactory v218 — Claude Code + in-house studio MCP integration

Date: 2026-10-10. Current branch: `integration/unified-cinefactory-20261010`.

## Purpose and actual implementation
The studio now has a true read-only local stdio MCP server `cinefactory-studio-readonly` using the Python MCP SDK's `FastMCP`. It wraps previously implemented v210/v213/v215/v216/v217 registries and reports, not third-party cloud AI, Blender Python execution or compositor scripts. One project-local `.mcp.json` launches `python -m cinefactory.studio.claude_mcp_gateway_v218` after Claude Code project trust approval. No tokens/URLs for external paid services are in configuration.

Six tools:
1. `studio_status` — actual baseline 96, 477 knowledge refs, 26 departments, fixed official-source watcher, approval policy.
2. `search_technology(query, minor_niche, department, limit)` — source-labeled, read-only retrieval.
3. `department_research(minor_niche, department)` — bounded department source references.
4. `niche_production_brief(minor_niche)` — research and QC blockers, format, review requirements, scene intents and editorial/R&D references.
5. `mcps_for_niche(minor_niche, department, limit)` — vetted R&D advisory on third-party Claude/MCP/SaaS, with cost/rights caveats.
6. `studio_review_protocol()` — standard competitor-first, quality-before-speed, owner approval gates.

All MCP calls are **non-executing**. They do not modify CineFactory source or production outputs, run model jobs, install packages, issue shell commands, access remote APIs, spend credits or approve tool installations. User-supplied niche/query inputs have bounded schemas; filesystem paths are not accepted.

## Current Claude Code connection status

Claude Code executable was found on machine (version 2.1.220 at verification). Project `.mcp.json` was accepted as configuration:
`claude mcp list` reported `cinefactory-studio: ... - Pending approval (run claude to approve)`.
A protocol-level Python SDK client successfully performed **initialize → tools/list → tools/call** against this actual local server. This proves server implementation is functional, **not that the human Claude Code approval has been completed**. User must open Claude Code from project directory and approve the project server; we do not bypass this permission.

### Run after owner acceptance

```powershell
cd 'C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6'
claude
```

When prompted, review `cinefactory-studio` and approve this local read-only server if desired. In Claude Code run `/mcp` to check status. Then query: "Use studio_status and niche_production_brief for minecraft_story_adventure. Delegate video evidence to competitor-researcher, shot planning to studio-technical-director, and requirements review to studio-quality-auditor. Do not spend credits or install third-party MCPs."

If MCP import fails in another Python environment, install only the explicit **optional** SDK in your reviewed project environment:
`python -m pip install -e ".[claude]"`.
The optional dependency is declared in `pyproject.toml` and doesn't change default core requirements.

## Claude Code project artifacts

- `CLAUDE.md`: 26-department operating instructions and rights/QC/budget/RTX 3060 gates.
- `.claude/skills/studio-niche-research/SKILL.md`
- `.claude/skills/studio-production-conference/SKILL.md`
- `.claude/skills/studio-shot-benchmark/SKILL.md`
- `.claude/agents/competitor-researcher.md`
- `.claude/agents/studio-technical-director.md`
- `.claude/agents/studio-quality-auditor.md`
- `.claude/agents/studio-tool-researcher.md`

Each agent declares `permissionMode: plan` and disallows direct edit/write/bash, so these specialist roles remain advisory. These definitions are local project files — they do not start background autonomous agents or automatically make any generation.

## Recommended staged MCP/AI upgrades (NOT installed)

**P0 — done now**: own read-only studio MCP, Claude project Skills/Subagents and evidence-first technology routing.

**P1 — isolated pilot, no cloud credits**:
- Existing direct ComfyUI API vs official `Comfy-Org/comfy-mcp` (beta; local-first). Risk: commands for partner models/cloud credits, workflows may contain paid nodes, custom nodes can call arbitrary APIs. Apply explicit capability allowlists, audited workflow JSON, credential isolation and a budget service owned by CineFactory.
- Blender 4.5 current persistent worker vs Blender Lab MCP requiring Blender >=5.1. Use a separate pinned Blender 5.1 test installation, sandboxed file/network permissions; official Blender Lab warns it will execute LLM-created Python code without guardrails. Production 4.5 worker remains untouched.
- FFmpeg/Remotion job/asset/audio/color QC: design read-only feedback receipts and then approved job-submit adapters. OpenTimelineIO / OpenColorIO only after proof of current problems.

**P2 — subject to real throughput bottleneck**:
- AYON/Kitsu/Prism shot/asset/version tracking: start from existing studio source of truth, do not duplicate databases.
- OpenArt/Higgsfield official MCP/CLI and Google Gemini video API: explicit credits/paid budgets and commercial licensing. Use for selected hero shots only.
- Freepik/Krea/MagicLight/PicLumen: use for research or artistic brief if a clear gap; PicLumen Basic has no commercial rights, and MagicLight's marketing about very-long-form videos is not benchmark proof.

**HOLD**:
- Random community Blender/Maya/Unreal MCPs with unrestricted arbitrary Python/system command, forced code auto-update, uncertain maintainer/license or no matching installed DCC.
- All third-party MCP install in production until pinned SHA, signature/trust, dry-run smoke tests, network/fs sandbox, secrets, audit log and real QC acceptance.

## Desired professional film studio quality loops

1. *Full, lawfully accessible competitor footage and audio*: timestamped hook/beat/scene/camera/animation/edit and evidence fidelity, including poor-performing controls.
2. *Original story bible and reusable asset identity*: rigs, materials/lighting, camera coverage, procedural action library and references.
3. *Per-scene conference*: choose deterministic 3D/captured footage/local Comfy/approved cloud; reserve AI video for scenes in which it wins.
4. *Pilot*: comparable clips, accept visual/anatomical physics continuity/characters/audio/licensing gates before speed.
5. *Delivery*: preview/dailies, audio mixing/loudness, shot continuity, color management, editorial, titles, packaging, release and rollback receipts.
6. *Postmortem*: log root cause, update skill/test/technology data only after verified improvement.

## Verification
Run:
```powershell
python -m pytest tests/test_claude_mcp_gateway_v218.py -q
python -m cinefactory.cli niche-technology-plan --minor-niche minecraft_story_adventure
claude mcp list
```
The test suite verifies actual stdio MCP initialize/tools/list/tools/call and strict no-permission policy, but it does not claim real commercial studio-grade render output yet.

Official docs:
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents
- https://www.blender.org/lab/mcp-server/
- https://github.com/Comfy-Org/comfy-mcp
- https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices
