# CineFactory v225 — Maizen Studio A: actual departmental desk kickoff

**Date:** 2026-10-10. **Selection:** user chose Maizen-style before BigSchool-style. Company priority is now `MAI01_WATERFALL`; BigSchool remains available but no simultaneous large-scale production. Maizen gameplay = staged/authentic Minecraft Java game session, **not Blender render pretending to be real gameplay**.

## What was actually executed in this phase

- Work products in `config/niches/minecraft/maizen_studio_a_v225.json` for **all 26 existing CineFactory departments**: original English pilot script, storyboard shot breakdown, 14min/7 chapter episode outline, creative cast Nova/Pip, original world props, two actor requirement, camera plan, sound cues, edit timeline, character/world licensing, gameplay authenticity, scene QA, hardware stack, retention measurement and postmortem rules.
- New project-specific Python control `cinefactory/studio/maizen_studio_kickoff_v225.py` validates all departments and every beat; generates **26 real JSON desk receipts + one hash manifest** in `data/verification/v225_maizen_studio_a_kickoff/` when run with `--start`. This is deterministic creation of preproduction artifacts, **not proof of 26 independently running LLM agents, real actor performances, recordings or game control**.
- Live read-only `cinefactory/studio/maizen_runtime_preflight_v225.py` checks OBS, Java/Minecraft standard path indicators, ffmpeg, Node and localhost OBS WebSocket TCP port. It never launches a program, bypasses game rights or writes a world.
- Claude Code's project MCP now exposes three additional read-only tools: `maizen_studio_status`, `maizen_department_work`, `maizen_runtime_readiness`; existing `minecraft_company_roadmap` references the selected kickoff when Maizen gameplay lane is queried.
- No automatic Claude Code approval, paid AI credits, game purchase, software install, model download, video render, video upload, or game source rights approval.

## Current machine verified and important risks

On Windows `DESKTOP-HJE6A6D`, OBS Studio exists at `C:\Program Files\obs-studio\bin\64bit\obs64.exe` with file/Product version **32.1.2**. OBS was not running when checked, and TCP 4455 (OBS WebSocket) was not listening; this does **not** mean OBS lacks WebSocket support. FFmpeg and Node were found on PATH. No Java or Minecraft Launcher executable found on PATH, no standard `%APPDATA%\.minecraft` directory, and no matching Microsoft Store Minecraft Appx package found in this limited audit. A portable/nonstandard game install may exist — **game ownership/license is UNKNOWN, not denied**. Company must not buy/install or use third-party Microsoft accounts without owner action.

**Microsoft/Mojang Minecraft usage guidelines:** https://www.minecraft.net/en-us/usage-guidelines — review real game footage monetization limits and game license before first take.
**Official OBS websocket:** https://github.com/obsproject/obs-websocket — bundled with OBS >=28; authenticate and keep loopback/private.
**ReplayMod:** https://www.replaymod.com/download/ — cinematic replay camera, version/Fabric compatibility and commercial terms must be verified.
**Flashback:** https://github.com/Moulberry/Flashback — alternative replay/camera, custom nonredistribution license and noncompatible replay format. Use one, pinned, not both indiscriminately.
**Mineflayer:** https://github.com/PrismarineJS/mineflayer and https://github.com/PrismarineJS/mineflayer-pathfinder — programmable actor/walking possibility; only optional after local private server and anti-abuse/game-version/rights tests. No claim it produces a complete movie automatically.

## Locked original episode for desk production

**MAI01** `We Found a Secret Base Behind a Waterfall`, planned **14:00** in English with original actors **Nova** (cautious builder) and **Pip** (impulsive explorer), no JJ/Mikey likenesses. The **seven** chapter arcs:

1. 0:00–0:50: waterfall flashes, unanswered clue.
2. 0:50–2:45: river exploration and safe traversal.
3. 2:45–4:55: tunnel and strange mechanical marks.
4. 4:55–7:25: build hidden entrance, basic power and escape route.
5. 7:25–9:35: unexpected threat/consequence.
6. 9:35–11:55: recover lost map and solve symbol puzzle.
7. 11:55–14:00: escape, secure base, mystery hook.

**45-second proof of concept:** 9 distinct **5-second original** game-capture shots from waterfall wide → player approach → two-actor reaction → camera passes behind waterfall → torch interaction → danger → block placement → map chest → cliffhanger. Precise English dialogues, world locations, camera requirements and each hard dependency are in `maizen_studio_a_v225.json`. These are **written shot specifications, NOT recorded frames**. A full 840-second episode cannot be declared ready before the 45-second genuine game clip passes actual video/audio quality review.

## Department handoffs

Each of 26 owners writes an individual first-person work product receipt on kickoff. Structured statuses:
- `DRAFT_CREATED`: an actual planning/preproduction draft now exists, not a finished render.
- `PARTIAL_EVIDENCE`: actual metadata/availability/rights evidence partial; missing proof remains named.
- `BLOCKED_EXTERNAL_DEPENDENCY`: cannot create qualifying gameplay or release without legal game+camera+actors+capture, full footage QC.

Every desk file gets SHA256 and is intentionally **not overwritten if a person edited it**. There is a single idempotent manifest; no made-up video SHA, and no false claims of real LLM agents working in the background.

## Execute/report (from repository root)

```powershell
python -m cinefactory.cli maizen-runtime
python -m cinefactory.cli maizen-studio
python -m cinefactory.cli maizen-studio --start
python -m cinefactory.cli maizen-studio --department WRITERS_ROOM
python -m cinefactory.cli maizen-studio --department AUDIO
python -m cinefactory.cli minecraft-company-roadmap --lane SCRIPTED_MINECRAFT_GAMEPLAY
claude mcp list
```

For Claude Code, user must approve the local project `cinefactory-studio` MCP if Pending approval. The new tools report current desk outputs and machine readiness **without authorizing Claude/remote providers to run unattended**.

## Stage tasks and the exact next blocker

- **G01/G02 Research:** Seven long videos' public metadata verified; three sparse YouTube storyboard preview groups inspected, not continuous footage, soundtrack or private CTR. New channels 0–30d with 2 long 1M-in-14d still not proven.
- **Creative/Script:** pilot dialogue 9 scenes + 14min story arc complete as **draft**.
- **Tech/Production:** must verify game license/runtime, pinned Minecraft Java version/Fabric, world save, original 2 actors, choose ReplayMod or Flashback, OBS capture/loudness, and perform a real **10-second** test before attempting 45 seconds.
- **Assets:** first-party Nova/Pip skins and game-world map not yet authored.
- **Audio:** voice/foley/music cue-sheet prepared; no voice recorded, no rights assumption.
- **QC:** 1080p>=24fps real moving game footage and recorded sound; scene continuity; game provenance; independent accepted review and measured accepted seconds/hour.
- **Release:** explicitly BLOCKED. Do not automatically upload a pilot/episode.

Do not conflate **studio kickoff and generated desk artifacts** with actual gameplay video. Next true production gate is real, authenticated and licensed Minecraft gameplay runtime plus a reproducible OBS (or native capture) test, then working two-character cinematic capture. The BigSchool animation lane is unchanged.
