# CineFactory Minecraft G01/G02 evidence progress v224 (10/10/2026)

**VERDICT: G01 PARTIAL, G02 PREVIEW-ONLY. No full competitor moving video or full audio was watched. Zero credits spent. No external game/MCP/mod installed.**

## 1. Direct public YouTube metadata, not third-party totals

Retrieved via `yt_dlp` public YouTube extractor with `download=False` from the authorized Windows workstation. Date 2026-10-10; these are **one-time counters**, not exact 14-day growth and not evidence a 0–30-day-old channel has two 1M long-form hits.

| Role | Direct original URL | Day returned by extractor | Exact duration | Public views in snapshot |
|---|---|---|---|---|
| Maizen choices | https://www.youtube.com/watch?v=ZmT0ITUGUII | 2026-08-29 | **28:04** | **4,677,671** |
| Maizen secret base | https://www.youtube.com/watch?v=zhPBXzHsLuo | 2025-10-15 | **18:37** | **19,583,823** |
| BigSchool long compilation | https://www.youtube.com/watch?v=X09yxFuKLAs | 2020-08-18 | **1:09:33** | **135,751,858** |
| Maizen *Item Drops Multiplying* (contemporary comparator) | https://www.youtube.com/watch?v=oX6Azwe5QLg | 2026-09-09 | **17:11** | **1,499,485** |
| Kamui Animation 2026 long-form (control) | https://www.youtube.com/watch?v=w2U4rcZlKnQ | 2026-10-03 | **8:45** | **381,224** |
| Daiki Animation long-form (control) | https://www.youtube.com/watch?v=cSrlIx-rT0Y | 2026-07-24 | **8:35** | **721,964** |
| MineBuzz long-form (control) | https://www.youtube.com/watch?v=le0yTRqFRro | 2026-10-04 | **8:17** | **242,920** |

Notes: Machine-extracted date for *Choose the Right Hole* is Aug 29, while previously indexed YouTube display showed Aug 28. An offset/time-zone interpretation is plausible but **not verified**, therefore keep discrepancy open until UTC publishing timestamp resolved. Every record has `channel_id`, `duration_seconds`, `view_count_as_of_date`, source URL, proof class and `UNKNOWN_NO_DAILY_VIDEO_HISTORY`. Kamui/Daiki/MineBuzz are comparison cases, **not proven new channels**. They also use third-party JJ/Mikey fan characters; analyze storytelling only, don't copy.

Strong current strategic observation: Maizen has 17+ minute 2026 long videos with meaningful public views. BigSchool's 2026 new uploads skew Shorts in indexed snapshots; its 2020 historical compilation does not by itself validate current long-form breakout in 2026. Compare current animation example Kamui 8:45 to dated mature/weak controls. Search listings: https://vidiq.com/youtube-stats/channel/%40bigschoolminecraft/ , https://digitalcreators.jp/channel/UC-IC1Sv1onK1kWlJTTQfrkw/videos/ .

## 2. Author chapter boundaries: metadata evidence, not playback analysis

### Maizen – *Built a House inside BED* (18:37)

| Source chapter interval | Seconds | Title published in source metadata |
|---|---:|---|
| 00:00–01:32 | 92 | Breaking in as tiny people |
| 01:32–04:07 | 155 | Building a base in the bed |
| 04:07–06:33 | 146 | Designing the interior |
| 06:33–08:29 | 116 | Creating a hidden farm |
| 08:29–11:51 | 202 | Installing security systems |
| 11:51–14:07 | 136 | Recovering stolen diamonds |
| 14:07–18:37 | 270 | Defending the base |

**Evidence-backed narrative hypothesis:** This chapter structure moves from character scale/entry to hidden construction, resource support, defenses, objective retrieval and payoff. Source chapter titles and time bounds confirm the author-supplied structure, NOT every visual action, cut or audio beat.

### Maizen – *Item Drops Multiplying* (17:11)

| Source chapter interval | Seconds | Title in metadata |
|---|---:|---|
| 00:00–01:27 | 87 | Mastering item duplication |
| 01:27–03:08 | 101 | Gathering rare resources |
| 03:08–05:54 | 166 | Raiding the pyramid trap |
| 05:54–08:14 | 140 | Mining for diamonds |
| 08:14–10:21 | 127 | Crafting premium gear |
| 10:21–13:21 | 180 | Preparing for the End |
| 13:21–16:40 | 199 | Defeating the Ender Dragon |
| 16:40–17:11 | 31 | Conclusion |

**Evidence-backed format hypothesis:** A fresh modifying rule creates escalating resource mechanics, gear progression, challenge climax, conclusion.

### BigSchool 2020 compilation (1:09:33)

The public description lists seven titled chapter markers. Machine-extracted chapter structure returned only four named chapters plus an unlabeled first second; it merges the later remaining runtime into the fourth chapter. **Treat the extractor chapter list as incomplete.** Use the seven public description timestamp labels from `master_company_plan_v223.json`, then verify each border with actual permitted player review, before measuring cut density or original vs compiled reissues.

## 3. Actual visual sampling, deliberately partial

Used public `https://i.ytimg.com/sb/<videoId>/storyboard3_L3/M...jpg` previews, downloaded **three first/middle/final publicly served thumbnail mosaic fragments** from each of Maizen Bed, Maizen Drops, BigSchool Season3. No source video stream downloaded. No audio captured; motion between sparse thumbnail tiles cannot be judged. Video preview mosaic files are stored in ignored `.tools/minecraft_preview_v224/`, NOT Git and NOT redistributed. The SHA256 hashes of each preview mosaic tile are recorded in `config/niches/minecraft/g01_g02_public_evidence_v224.json`.

| Reference | OBSERVED in public thumbnail previews | CANNOT CLAIM |
|---|---|---|
| Maizen Bed | Crosshair/HUD/hotbar, exterior wooden house, furnished brightly colored interior, English action subtitles and security equipment, social endcard | Actual game version, shader/mod stack, original sound design, exact cut count, 3D tool chain |
| Maizen Drops | HUD/hotbar, crafting/inventory menus, resource/crafting/End-like settings, explanatory captions, endcard | Real specific game/mod config, audio/VO timing and precise whole-film pacing |
| BigSchool S3 | Third-person wide/medium shots, characters staged in outdoor street and school/interior sets with varied poses; no HUD observed in **sampled** frames | No-HUD entire film, Blender/Mine-imator identity, rig/keyframe method, sound, total animation frames per shot |

Do not misreport sparse thumbnail preview as full review. For G02 PASS, obtain legitimately accessible whole moving video and soundtrack, independently verify full decode, then code OBSERVED for every shot and timecode with voice/sound annotation.

## 4. Real software gap: Maizen-style requires authentic game runtime

At snapshot workstation:
- `%APPDATA%\.minecraft` standard Java profile did **not** exist; Minecraft Launcher / `java` / `javaw` / `obs64` were not found on PATH. This limited check does not rule out portable or Store installed applications.
- Existing Blender 4.5 can make authored voxel animation, but **cannot be falsely described as actual Minecraft gameplay**.
- **ReplayMod** https://www.replaymod.com/download/ supports Fabric and Minecraft 1.21.x and newer versions; record and reframe legally run Minecraft sessions.
- **Flashback** https://github.com/Moulberry/Flashback and https://flashback-mod.com/ provides in-game recording and cinematic camera; custom license (not freely redistributable). Flashback replay files are **not compatible** with ReplayMod.
- OBS Studio https://obsproject.com/ is an optional real capture backend for output + mic; use deterministic project-recorded files and original game action.
- **Test ONE replay mod variant on a licensed, pinned Minecraft Java/Fabric setup**, not both in the same profile by default. No automatic mod JAR download or install has been approved, no proof of headless filming automation.
- Camera+scene script concept: original Minecraft map and rules → original cast/actors → repeatable action takes/commands → ReplayMod/Flashback camera path → OBS/FFmpeg encode + audio → edited story with honest source labeling.

For BigSchool-style, no game runtime is necessary; priority remains original 64×64 voxel art and identity, advanced rigs/eyes/mouth/props, camera staging, acting/NLA and believable Foley; v197 existing two-second pilot fails **12 art blockers**. Do not try to solve those with cloud-only upscale.

## 5. What each department does NEXT in G01/G02

| Owner | Next verifiable work | Acceptance |
|---|---|---|
| INTELLIGENCE | Confirm ages of Kamui/Daiki/MineBuzz; find weak non-viral 8min controls and precise daily 0,7,14-day velocity if available | Cannot state new channel 2×1M/14d without upload-time snapshot |
| EVIDENCE | Acquire authorized playable full video+audio; record exact timestamps, provenance, observed visual/audio | Hash/license, full decode/inspection and shot evidence |
| DIRECTION + SCRIPT_LOGIC | Build timeline comparisons for 7 Maizen Bed chapters and 8 Item Drops chapters | Contrast causal action, choice/progression, reveal/payoff as OBSERVED not caption inference |
| CINEMATOGRAPHY | For each chapter, measure camera type, cuts, framing, movement and geography from actual frames | Quantified shot table only after playback |
| AUDIO | Annotate voice/narration, Foley, transitions, music and sync from real soundtrack | No audio claims from thumbnails |
| ASSETS + PERFORMANCE | For 3D, compare original rig models to BigSchool sampled staged scene sets and acting needs | Own-character visual rig test with clear art/QC result |
| TECHNICAL_DIRECTION + RND | Decide original Blender worker vs installed Minecraft game capture + ReplayMod/Flashback after free isolated benchmark | Machine/license/VRAM and reproducibility receipts, quality first |
| QC + RIGHTS | Enforce original actor/IP, no snippets reuploaded, no fake viewing or Shorts metrics mixed with 8+min | Fail closed until verified |
| STUDIO_MANAGEMENT | Approve 45s one-lane pilot after Research + Rights conditions; do not authorize paid SaaS implicitly | Signed scoped budget/version |

Research study in code:
- `config/niches/minecraft/g01_g02_public_evidence_v224.json` (direct metadata, chapters and thumbnail SHA/observations)
- `cinefactory/studio/minecraft_source_evidence_v224.py` (read-only retrieval + strict false-positive gate)
- `python -m cinefactory.cli minecraft-source-evidence [--video-id zhPBXzHsLuo]`
- `python -m cinefactory.cli minecraft-company-roadmap --lane SCRIPTED_MINECRAFT_GAMEPLAY`
- Claude Code internal studio MCP: `minecraft_g01_g02_evidence` plus v223 roadmap.

**Final state v224: G01 PARTIAL, G02 PARTIAL_PREVIEW_ONLY, G03 STORY/PRODUCTION INFERRED, no 45-second professional render, no 8–18min YouTube release.**
