# Minecraft niche — toolchain plan (owner tool list, 2026-11-01)

Source of truth for each tool's status: `config/niches/minecraft/research_backlog_v222.yaml`
(`control`, `priority`, `gate`). This page says how to combine them.

## 1. What Cine can actually drive

| Control level | Tools | Meaning for production |
| --- | --- | --- |
| CODE_HEADLESS | Blender 4.5 worker, MCprep (inside Blender), FFmpeg, ComfyUI, Mineflayer bots | Cine runs it unattended |
| CODE_FILE | Mine-imator (`.miproject`), Blockbench (`.bbmodel`) | Cine writes the project; a person opens it and renders |
| GUI_ONLY | Replay Mod, BBS, Mixamo, map sites, Incompetech music, Kenney/Pixabay SFX | a person operates it (or slow screen control) |
| REPLACED_BY_CINE | CapCut → `tools/cf_auto_edit.py`; Audacity pitch → FFmpeg; TTS → audio-post local TTS | use the Cine tool |
| POLICY_BLOCKED | community/competitor skins (NameMC, skin sites), NovaSkin wallpapers as thumbnails | original-IP rule; draw our own |

Facts checked 2026-11-01 (OBSERVED from the sources):
- Mine-imator: project file is JSON; the app passes launch arguments only to Qt (no open-file or render command found), so rendering is manual.
- MCprep 3.6.3: one install for Blender 2.83–5.2.
- Blender MCP (ahujasid): one tool `execute_blender_code` = arbitrary Python in a live Blender, socket :9876. Interactive use only.
- Mineflayer: Minecraft 1.8–26.1, `auth: 'offline'` for an owner-run offline server.
- Incompetech: CC BY 4.0; credit "Title Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0" in the description; monetisation allowed.
- Freesound API: token for search/previews (60/min, 2000/day); original files need OAuth2. Use CC0/CC-BY only.
- TTSMaker: commercial use allowed per its FAQ; free tier 20,000 characters/week; Vietnamese listed.
- Mixamo: royalty-free in videos; raw files may not be redistributed or used for ML training; no API.

## 2. Three production routes

| Route | Look | Automation | Use when |
| --- | --- | --- | --- |
| R1 Blender 4.5 worker (+MCprep rigs/world, Blockbench original props) | cinematic, full lighting control | end to end (`block-enqueue` → factory) | daily volume, effects shots |
| R2 Mine-imator (`block-mineimator-export`) | classic Mine-imator animation (owner priority) | Cine writes the project; owner renders | episodes where the Mine-imator look is wanted |
| R3 In game (owner world + Mineflayer actors + Replay Mod or BBS capture) | authentic gameplay | bots scripted; capture/render manual | "real gameplay" formats |

All three share the same front and back of the loop:
script (showrunner / script skills) → voice first (audio-post) → **route** → Director Cut → `cf_auto_edit` (music, SFX, captions, −14 LUFS) → `cf_qc` + qc-reviewer → packaging-seo + `cf_policy_check` → HANDOFF.

Assets for every route: original cast skins (64×64, drawn in NovaSkin's editor or generated), sets built by us or maps whose licence is recorded; music from Incompetech (CC BY 4.0 credit); SFX from Kenney (CC0), Pixabay (no attribution, no standalone redistribution) or Cine-synthesised — Freesound skipped (OWNER 2026-11-01); thumbnails from our own render frames.

## 3. Choosing a route — measure, don't guess

Render the same 45-second original pilot (`pilot_plan` in the register) through R1 and R2 (R3 optional). For each, record in `data/production_ledger.jsonl`: person-minutes, render minutes, QC pass/fail, accepted seconds per hour. Pick the default with `tools/cf_decision.py add --kind render`. Until then: R1 is the automatic default, R2 is the owner-priority option.

## 4. Owner actions to unlock

1. Merge PR #12, pull on the Windows machine without overwriting local changes.
2. Mine-imator 2.x: make `template.miproject` (cast, camera, audio track) → `block-mineimator-inspect` → one calibration export (`docs/MINEIMATOR_ADAPTER.md`).
3. Blender: install MCprep 3.6.3 in a test copy of Blender 4.5 and run one rig/world import.
4. Optional R3: local Fabric server in offline mode, Replay Mod or BBS in the owner's client.
5. Blender 4.5.15 (official MSI, SHA-256 verified) as the MCprep test install; production worker stays untouched.
