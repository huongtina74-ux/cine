# CineFactory v219 — actual AI / Claude Code / Software connector integration

Snapshot: 2026-10-10. This release corrects the impression that merely researching an external SaaS/MCP makes it installed, connected or production-ready.

## What was actually done and verified

1. **ComfyUI local connected through a real read-only MCP gateway**: The CineFactory project Python MCP server now exposes:
   - `comfyui_local_status()`: fixed GET `http://127.0.0.1:8188/system_stats`, OS/Python/Comfy/PyTorch version and GPU VRAM. Does not return credentials, prompt bodies or arbitrary file paths.
   - `comfyui_local_capabilities(query="Checkpoint", limit=15)`: GET `/object_info` and return only filtered node *class names* to assess actual available workflows, not authorizing them.
   - `comfyui_local_queue()`: GET `/queue`, counts only, no prompt contents.
   - `claude_external_connector_plan()`: a source-reviewed catalog of 12 provider/product bridges, with security and billing activation gates, all unapproved.
2. Claude Code project `.mcp.json` still registers ONE intentionally safe CineFactory studio MCP server. The server's tool count is now **10** (6 existing v218 + 4 new). No external cloud MCP is silently enabled.
3. CLI `python -m cinefactory.cli ai-connector-status --probe-local` fetches the exact same real local readiness info, without running a workflow.
4. Added `.claude/skills/studio-ai-mcp-router/SKILL.md` and updated `CLAUDE.md` so Claude knows it must consult real local capabilities before selecting AI/software/MCP per scene.
5. Reviewed provider statuses and licensing in `config/technology/claude_external_connector_catalog_v219.json`.

**Live machine observation during integration**: ComfyUI version `0.38.0` responds at `127.0.0.1:8188`; its API reports RTX 3060 with 12,884,377,600 bytes of VRAM, CUDA PyTorch environment and `--disable-all-custom-nodes --disable-api-nodes`. Thus local core nodes can be inspected; paid partner API nodes are explicitly disabled in that observed server process. Queue showed zero running and zero pending at this point. No video or image generation was performed.

**Blender MCP discovery**: Two `blender-mcp.exe` processes from the Claude Desktop extension location were observed. The presence of those background processes does *not* prove Blender itself or CineFactory's 4.5 persistent worker is connected to Claude Code. Claude Code extension compatibility and permissions remain not tested. Official Blender Lab MCP requires 5.1+ and runs unsandboxed model-written Python. Do not auto-attach the Desktop MCP server to the CineFactory project.

## What is still NOT installed/connected

| Integration | Current observed status | Next safe gate |
|---|---|---|
| ComfyUI LOCAL via CineFactory MCP | **CONNECTED_READ_ONLY** (HTTP GET live) | Test pinned permitted *local* workflow with new explicit owner scope, disable all paid nodes |
| Official Comfy-Org MCP (comfy-mcp) | **NOT FOUND ON PATH** | Isolated reviewed install of `comfy-mcp` and `comfy-cli >=1.14.0`, version-pinned, remove/deny partner spending and arbitrary tool deployment |
| Claude Desktop Blender MCP extension | Process present, **Claude Code unconnected** | Confirm renderer/addon version, sandbox filesystem, identity of MCP maintainer and smoke-test safe scene in a clone |
| Blender Lab MCP | Requires Blender 5.1+, **not installed** | Separate Blender test environment; do not replace factory 4.5 without acceptance |
| OpenArt MCP | Official paid remote MCP; **not added to Claude Code** | OAuth and per-project credit budget approval |
| Higgsfield MCP / Skills | Official paid remote MCP; **not added to Claude Code** | OAuth/CLI and explicit credit budget |
| Google Flow | Cloud web creative tool, **not a local MCP** | Use official Gemini/Veo API only after paid access scope approval |
| MagicLight, Krea, Freepik, PicLumen | SaaS research references | Verify dev API/MCP and commercial licensing, benchmark; no blind activation |
| FFmpeg / Remotion CineFactory | Existing editor stack | Use existing reviewed handlers, no replacement warranted |

Every new connector in the manifest has `auto_enabled=false`, and all models/services retain `production_qualified=false` until evidence.

## Claud Code live use

Open PowerShell in actual CineFactory repo:

```powershell
cd 'C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6'
python -m cinefactory.cli ai-connector-status --probe-local
claude
```

Within Claude Code approve only the reviewed **local** `cinefactory-studio` project MCP if prompted, then check `/mcp`. You can say: "Call `comfyui_local_status`, `comfyui_local_capabilities`, `claude_external_connector_plan`, and `niche_production_brief` for minecraft_story_adventure. Suggest best local methods per shot. Do not use paid AI, download models, run Python in Blender, or change production configs."

### Opt-in paid external MCP (NOT run)

OpenArt vendor source: https://openart.ai/mcp/ ; remote URL `https://mcp.openart.ai/mcp`. Provider says OAuth and cloud generations spend OpenArt credits. On an approved project, owner may configure Claude Code remote HTTP MCP separately, after reviewing permissions and setting credit budget.

Higgsfield official source: https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-ai-agent ; even "unlimited" web subscriptions can be billed for MCP/CLI credits. No automatic use.

Comfy-Org official local server: https://github.com/Comfy-Org/comfy-mcp ; does local CLI shell invocation, install/download/manage tools and can invoke partner paid generation. Prefer this v219 **limited direct local-API read bridge** while no audited tool-permission proxy exists.

Blender Lab official MCP: https://www.blender.org/lab/mcp-server/ ; its unsandboxed `bpy` risk is a blocker on the working production workstation.

## Development rules

- Live ComfyAPI GET calls can fail if service is offline. Return `UNAVAILABLE` rather than claim zero nodes or zero VRAM.
- No input-supplied URLs, hosts, methods, POST, job submit, file operations, filesystem shell access, secrets or model downloads in v219 bridge.
- Each actual creative generation requires separately authorized execution adapter (not included here) with node allowlist, model provenance/license checks, per-shot spend ceiling, human approved intent, receipts and QC. We DO NOT claim the system is a fully functioning multi-provider paid cloud production orchestrator.
- CineFactory remains 26 departments; baseline 96 reviewed registry and v215-v217 research catalogs remain intact. Public source evidence is not video execution evidence.

## Validation

```powershell
python -m pytest tests/test_local_ai_connector_v219.py tests/test_claude_mcp_gateway_v218.py -q
python -m cinefactory.cli ai-connector-status --probe-local
claude mcp list
```

MCP protocol validation via the Python SDK `ClientSession` probes the actual stdio server and can call new local Comfy endpoints without cloud credits. Claude Code project human trust approval remains separate; `claude mcp list` may display Pending approval until owner approves.
