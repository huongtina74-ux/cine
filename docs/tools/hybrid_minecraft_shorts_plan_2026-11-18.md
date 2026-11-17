# Hybrid Minecraft Shorts plan — fast factory + hero renders (2026-11-18)

Owner request (OWNER, 2026-11-17): combine three.js, Blender, Mine-imator and Minecraft "to make products as fast and as good as possible".

## One source of truth: the SPEC

Every Short starts as one JSON SPEC (`tools/blockfilm/factory/specs/*.json`). The contest engine turns it into a
timeline (segments + motion + sound cues). Every renderer reads that same timeline, so story, timing and sound never
have to be redone when the renderer changes.

| tier | renderer | when | speed |
| --- | --- | --- | --- |
| 1 — daily | three.js factory on the cloud (`make_short.py`) | every "Who can …?" Short | see `out/<id>/production.json` (MEASURED per Short) |
| 2 — hero | Mine-imator on the PC, keyframes baked from the same timeline | the 1-in-5 Shorts that test best | 1.35 s/frame OBSERVED (S01 v3) |
| 3 — physics / satisfying (MC-S2) | Blender EEVEE on the PC | rigid-body / fluid shots three.js can't fake | 2.2–6.3 s/frame OBSERVED |
| capture | real Minecraft Java (datapack + camera) | only when "it's the real game" is the point | real time, needs the PC awake |

## Rules

1. Tier 1 ships first; a hero render is an upgrade of a Short that already exists, never a blocker.
2. Overlay (title, chips, counters) and the sound mix are produced once from the cues and reused by every tier
   (`render.js overlay` → transparent .mov; `audio.py` → mix.wav), as done for S01 Mine-imator v3.
3. Mojang block textures only in tiers that need them and only per owner decision D-8c718c6f; tier 1 is fully original.
4. One heavy job at a time on the RTX 3060; the cloud factory runs in parallel with PC work.

## Next engineering steps

- `render.js bake` — dump per-frame character transforms + tower heights + camera to `bake.json` (pending, task #102).
- `tools/mineimator/from_bake.py` — write a .miproject from `bake.json` (reuses the S01 builder's keyframe writer).
- More challenge types in `contest.js` (fastest race, longest bridge, deepest dig) — each is a new `challenge` value, not a new file.
