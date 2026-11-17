# blockfilm Shorts factory — "Who can …?" from one SPEC file

One JSON file per Short → one command → finished vertical MP4 (1080×1920, 30 fps, −14 LUFS) + technical QC + measured times.

```bash
python tools/blockfilm/factory/make_short.py tools/blockfilm/factory/specs/s02_tower.json --workers 2 [--stills]
# -> tools/blockfilm/factory/out/s02_tower/{s02_tower.mp4, production.json, qc/, cues.json, mix.wav}
```

Then the **independent** gate: the qc-reviewer agent reads `qc/` + frames and writes `qc_notes.md` (maker ≠ checker).

## SPEC

```json
{"id":"s02_tower","title":["WHO CAN BUILD","THE TALLEST TOWER?"],"challenge":"pillar","lanes":["bin","bo","zu"],
 "attempts":[{"who":"bin","score":10},{"who":"bo","score":16,"style":"fast"},{"who":"zu","score":3,"style":"flop"}],
 "twist":{"type":"backfire","to":30},"winner":"bin","boast":"WATCH THIS!","ruler":32}
```

| key | meaning |
| --- | --- |
| `challenge` | `launch` (spring pads, jump height) or `pillar` (tower building) |
| `attempts` | exactly 3, in story order: **A** tries, **B** beats A, **C** flops. `style`: `fast`, `slow`, `flop`, `double` |
| `twist.type` | `glow` — C charges up and rockets to the top (C wins); `backfire` — B gets greedy, builds to `twist.to`, tower collapses (A wins) |
| `winner`, `win_text`, `boast`, `ruler` | result, optional win banner, B's boast line, height of the measuring pole |

Story template (proven on S01): hook ≤0.35 s → A → B (sly) → C flop → laugh → twist → wait → result → loop back to the first frame.

## Pieces

| file | job |
| --- | --- |
| `build.py` | assembles the page: shared core (ep01) + cast (ep03 Bin/Bo/Zu) + `web/world.js` (arena, voxel mesher with ambient occlusion) + `web/contest.js` (story engine) |
| `web/contest.js` | timeline, acting, cameras, towers/debris, particles, overlay; exports `CUES_EXPORT()` |
| `render.js` | headless Chromium: `cues`, `stills`, `video`, `pvideo` (parallel segments → concat) |
| `audio.py` | music + SFX from the cue list only (original synthesis, `../sfxkit.py`); no per-episode audio editing |
| `make_short.py` | the one command; writes `production.json` with MEASURED seconds per step |

All textures, characters, music and SFX are drawn/synthesised in code — original, no Mojang assets.
Hero-quality versions (Mine-imator/Blender) reuse the same SPEC timeline — see the hybrid plan.

Check: `python -m pytest tests/test_blockfilm_factory.py -q`
