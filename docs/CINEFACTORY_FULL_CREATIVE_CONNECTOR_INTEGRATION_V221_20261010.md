# CineFactory v221 — 27 creative software/MCP options integrated into company plans

**Date:** October 10, 2026. The output is a **company capability and staged-activation integration**, not 27 new app installations.

### Implemented in Windows repository

- `cinefactory/studio/company_connector_registry_v221.py`: imports all 27 previously verified v220 entries. Each has an owning department, applicable niche/format, local executable PATH hint (where relevant), integration status, rights/quality approval blockers, and cloud-credit denial.
- `cinefactory/studio/technology_council_v212.py`: each company stage gets `creative_software_mcp_candidate_ids` for its owning department; no executor is activated. Legacy project with missing niche remains resumable.
- `cinefactory/studio/niche_technology_strategy_v213.py`: the regular niche production plan includes department-wide candidate routing plus representative pilot options.
- `cinefactory/studio/claude_mcp_gateway_v218.py`: two new real read-only MCP endpoints `company_connector_inventory(local_probe=False)` and `company_scene_connector_plan(niche, department, limit, local_probe=False)`. The total project MCP tool count is now **13**.
- `cinefactory/cli.py`: CLI command `company-connectors` with `--inventory`, `--minor-niche`, `--department`, and optional `--probe-local`.
- `.claude/skills/studio-capability-onboarding/SKILL.md`: safe staged activation checklist. Explicit installation, credentials and spend require approval; no auto-install or credential creation.

### Local-machine findings

**ComfyUI 0.38.0** responds to fixed localhost 127.0.0.1:8188 with GPU RTX 3060 12GB via CineFactory's **read-only** bridge. This does **not** prove `Comfy-Org/comfy-mcp` itself is installed, connected or able to execute a generation.

Named GUI app executables from the 27-entry list were not detected on `PATH`, nor were matching uninstall records returned by the limited registry check. This cannot prove portable or isolated installations are absent. Running Claude Desktop Blender MCP extensions observed in the previous audit still do not establish a Claude Code connection. Claude Code project `cinefactory-studio` requires owner approval in interactive Claude Code.

**No external MCP automatically enabled; no new production executors; no remote paid credits spent; no commercial model rights guessed.** Older 96 registry entries and existing Blender/Comfy/FFmpeg workflows are unchanged.

### How to inspect

```powershell
cd 'C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6'
python -m cinefactory.cli company-connectors --inventory --probe-local
python -m cinefactory.cli company-connectors --minor-niche minecraft_story_adventure --department VFX
python -m cinefactory.cli company-connectors --minor-niche minecraft_story_adventure --department AUDIO
python -m cinefactory.cli niche-technology-plan --minor-niche minecraft_story_adventure
claude mcp list
```

When the project MCP is manually approved in Claude Code, it can query candidate apps and proposed activation gates directly. The 27 research entries include Unreal, Cinema 4D, Unity, Boris FX, Resolve, Nuke, Houdini, Maya, REAPER, Audacity, AE, Premiere, Photoshop, Natron, Kitsu, Godot, ComfyUI beta and paid cloud tools OpenArt, Higgsfield, Runway, Magnific, fal.ai, ElevenLabs, Shotstack. Some entries overlap v216–v219 catalogues. Neither a native official MCP nor a community MCP should be marked installed without an actual handshake, license and representative quality pilot.

### Real production activation requirement

1. Verify exact installed DCC/service and source permissions.
2. Confirm licensed commercial rights and isolation from user data or paid API credentials.
3. Pin package SHA/version; run limited sandbox proof before write/code-execution privilege.
4. Do a comparable **original** 3D/video/audio test, independent QC, GPU/VRAM, credit and human rework measurements.
5. Only after explicit owner consent and QC pass may an implementation be enabled for a production stage.

This v221 change adds discoverable, governable capabilities to every department. It does not claim cinema-grade media production was validated or external software executors installed.
