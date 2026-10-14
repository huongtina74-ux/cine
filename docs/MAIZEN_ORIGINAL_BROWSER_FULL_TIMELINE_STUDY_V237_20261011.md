# CineFactory v237 — First Maizen original YouTube video: real Chrome playback and frame-by-frame sampled review

**Video:** [Mikey and JJ Choose the Right Hole in Minecraft](https://www.youtube.com/watch?v=ZmT0ITUGUII) (28m04s, 1684.461 s). Date: 2026-10-11.
**Important:** Original public YouTube was really opened and played using Chrome/Playwright on Windows `DESKTOP-HJE6A6D`, not video thumbnail mosaics or just vidIQ. The browser's source-time probe and sequential segments ran to the end; source pictures were inspected from 8 contact sheets. Audio energy was detected but **semantic listening to every original line, mix and sound effect did not happen**. No full source MP4/audio was downloaded; not a false G02 signoff.

## Actual browser playback provenance and scope

- Browser path: `C:\Program Files\Google\Chrome\Application\chrome.exe`; isolated headless Chrome with programmatically monitored HTML5 video for each short consecutive timeline segment.
- YouTube source duration detected: **1684.461 s**, correct video and title.
- A *single* browser session stalls around the end of a streaming chunk (~1 minute in the tests), and reusing a browsing context can encounter a pre-roll advertisement that resets media time. The solution used **independent browser sessions** per 38-second segment, at 2× playback, with a two-second overlap at segment seams; no media file copying.
- **45/45 source timeline segments from 00:00 to 28:04** reached their intended time boundaries. Combined validated monotonic source-position intervals have **0 seam gaps greater than 0.7 s**, from video start through 1684.461 s (machine transcript: `.tools/maizen_browser_full_source_audit_v236.json`).
- **153 sampled real video screenshots** according to the selected 45 segment receipts, distributed across all stages, plus **355 real Web Audio energy/RMS checks, 349 of them non-silent**. Contact sheets for independent visual inspection: `.tools/maizen_visual_pages_v237/page_01.jpg` through `page_08.jpg`.
- Samples are frames every roughly 10–15 video seconds (not *every decoded video frame*); Web Audio RMS measures energy but **does not independently recognize words, melody, music licensing, sound effect identities, dub technique, or human performances**.
- This is **authentic original YouTube browser playback coverage** plus representative direct visual observation, not a cryptographic, independent, full-audio-semantic QC. `G02` strict policy v227 remains **BLOCKED**. Two other required Maizen source videos remain unreviewed.
- No vidIQ credits, new software installations or unauthorized downloads were used for this browser study. A separate earlier vidIQ tool job used pre-existing credits and its narrative report was cross-checked only as a secondary source.

## Scene narrative supported by actual original frame screenshots

| Video time | What really appears in first-party sampled Chrome pictures | Story/visual editing mechanism |
|---|---|---|
| 00:00–03:35 | Two giant TNT and diamond pipes; JJ/Mikey both appear in wide setup then first-person red-sleeved arms/HUD. TNT room, explosions, crater and chests; visibly packed diamond inventory; diamond room with small hostile diamond-shaped creatures | Audience-challenge choice + expectation reversal, reward and consequence. |
| 03:36–07:05 | Lava and water pipes, long side-by-side arenas of floating wooden platforms; boat chest and water traversal, transparent separation and acting reactions | Repeated contrast and easy-to-read simultaneous progress, unusual item enables solution. |
| 07:06–10:23 | Slime/honey pipes, lime-green room with padlocked exit, honeycomb-colored room, bee swarm and characters reacting; held key prop | Search/exploration → hazard → object/door resolution. |
| 10:24–12:43 | Simple 5 or 6 selection, stone arena, interior lever and partition, boulder/punishment and a large red "Defeat the opponent!" overlay | Interactive easy math hook, visually delayed destructive consequence. |
| 12:44–15:29 | Silverfish and Mutant Zombie labeled pipes; contrasting green versus grey rooms, apparent small entity by door, swarm in other room, red/green narration overlay | Size/safety inversion and character contrast. |
| 15:30–18:00 | Android/iPhone signboards, white showroom, recognizable mobile-device-like 3D held items, animated Android mascots attacking other character, colored onscreen text | Familiar real-world object/trademark theme + original hazards; brand rights concern. |
| 18:01–20:05 | DANGER/SAFE chutes, dramatic asymmetric equipment in game chest inventories, one side receiving different supplies | Setup preparation for a longer final test; early investments pay off later. |
| 20:06–24:39 | Stadium with sky-blue walls/white cloud motif, timer displayed over video; white bunker with door, laser-style perimeter fence, redstone wires, lava apparatus, other side dirt structure with giant cobweb field. Countdown visually plunges from about 14:50 to seconds in roughly 4 real minutes. | Compressed scripted stage build under deadline; **in-video timer is not equal to elapsed video minutes**; jump cuts/time acceleration are likely (backend unproven). |
| 24:40–27:50 | Tall long-limbed black boss appears, walks through and damages weak web/dirt defense, attacks area containing lasers and deep lava pit of stronger base, then vanishes before resolution | Long final escalation → double-defense contrast → climax, not seven equal-length short rounds. |
| 27:51–28:04 | Green 2D mascot YouTube end-card, handles, subscribe and next-video blocks | Explicit editorial branding and viewer recirculation. |

**Distinct visual production clues:** consistent first-person Minecraft-like HUD crosshair/hearts/hotbar/inventory, occasional third-person two-character coverage and reaction shots; multiple large purpose-built arena sets with engineered contrast; high-contrast bold color-coded baked English subtitles; custom-looking prop, mob and boss models; visible in-game redstone/item mechanisms; and a clearly separate 2D animated outro. Thus the user was right that simply instructing two people to play Minecraft and record spontaneous footage would not reproduce the authored plot or shot coverage. But these clues do not prove the **exact** Maizen Minecraft version, server actor automation, editor, bot implementation, model licensing or Blender usage.

## Why this is substantially better than the initial 10s sample but STILL not a final source QC

The source VIDEO timeline was played until the end in 45 consecutive chunks. This establishes a stronger original visual record than previous 7 public video metadata snapshots, short storyboards or external vidIQ text. **However:** playback at 2× and sampled stills is not the same as frame-level motion analysis of every action; Web Audio signal checks are not semantic listening or an actual full original audio transcript; no independent second viewer checked the complete native audio or every ≤30s timecode window. Do not silently mark G02 or script/tech workflow finalized.

### Immediate next gates

1. Audio Research: genuinely examine entire original soundtrack/dialogue/music/SFX with authorized listening or reliable local ASR+human spot-check; align language with actual visual/motion windows and verify that silent spots are real.
2. Evidence/independent QC: 57 source intervals no more than 30s; add original video/audio observations with direct timecodes and separate auditor; do not fabricate attestation just because Chrome advanced its playback time.
3. Deep Research still needs full original A/V for `zhPBXzHsLuo` and `oX6Azwe5QLg` with the same standard before Maizen G03 conclusions for all three.
4. After G02 PASS: direct a side-by-side CineFactory proof of the most plausible generic methods (original game-stage controlled scenes, original Blender-authored voxel scenes, hybrid if needed), measure actual render/capture, acting/shot continuity, dialogue/Foley and accepted sec/hour, NOT assumed backend or copying JJ/Mikey.

## Company handoff policy

- Research may mark **SOURCE_VIDEO_TIMELINE_PLAYBACK_VERIFIED** for this one video and keep **SOURCE_AUDIO_SEMANTIC_REVIEW_PENDING**; source evidence has been stored separately from provider analysis v230.
- Script Room: research notes are valuable drafts; do not call the 7-round recipe a globally verified channel formula until other cohort videos are analyzed.
- Production Design: original source visual study strongly supports planning modular purpose-built arenas, reusable choice hub, custom item puzzles and a final larger set; exact original assets must not be copied.
- Character & Acting: shots show staged line delivery with color-coded subtitles, two consistent avatars and alternations between POV and on-screen third-person, but no proof of actor controller.
- Technical Director: consider game-engine staging with custom world/entities/inventory an evidence-consistent candidate; do not exclude external CGI/hybrid or assert named mods (Techguns/Custom Security/Forge/etc.) based on a third-party AI report.
- Audio & Editorial: giant subtitles, strong question/payoff rhythm and highly compressed final build timer are visibly established; sound source inspection remains pending.
- QC: keep all production recipe release gates BLOCKED until actual whole native original audio and original film content undergo independent review.

Files:
- `config/niches/minecraft/maizen_browser_visual_evidence_v237.json` — 10 distinct timed phases with sourced visual evidence and confidence.
- `cinefactory/studio/maizen_browser_source_review_v237.py` — read-only local-receipt verification and strict-G02 coexistence.
- `python -m cinefactory.cli maizen-browser-source` — machine report; local ignored capture receipts are not committed.
- This report — `docs/MAIZEN_ORIGINAL_BROWSER_FULL_TIMELINE_STUDY_V237_20261011.md`.

Source first-party media and screenshots remain in machine-local Git-ignored `.tools` to avoid redistributing third-party video images. Repo commit includes only our descriptive research and proof-checking code.
