# Mine-imator adapter (block animation → .miproject)

Status: **UNCALIBRATED** — code and tests pass here; not yet opened in Mine-imator on the owner PC.

## What it does

Mine-imator 2.x has no API or headless render, but its project file is JSON
(source-verified in `stuffbydavid/Mine-imator`, `project_save_*.gml`).
`cinefactory/block_animation/mineimator.py` takes the same `CompiledEpisode`
the Blender worker renders and writes it into a **copy** of an owner-made
template project:

| From the episode | Written to Mine-imator |
| --- | --- |
| actor placement, yaw, visibility per shot | character `POS_*`, `ROT_Z`, `VISIBLE` keyframes |
| actions + reactions (clips in `animations.yaml`) | body-part `ROT_X/ROT_Z` swing and `BEND_ANGLE_X` keyframes |
| walk/run root motion | character moves along its facing |
| gaze | head yaw toward the target |
| first camera take per shot | camera orbit (`CAM_ROTATE_*`), distance by shot size, FOV from lens |
| episode mix (`--audio`) | replaces the sound file of the template's audio track |

Not exported (reported as warnings): facial expressions (Mine-imator faces come
from the skin), props, crowd, VFX events. Shots are joined with hard cuts.

## Owner steps (once)

0. Install Mine-imator 2.0.2 and upgrade Trial → Full: the Trial build burns a watermark into every exported movie/image.
   The Full key is free at https://www.mineimator.com/upgrade ("I'd rather not donate" → Get key); it is stored in
   `<Mine-imator>/Data/key.midata`. OBSERVED 2026-11-01 on the owner PC: installed at `C:\Users\ADMIN\Mine-imator`, title shows `v2.0.2` (no TRIAL).
1. In Mine-imator 2.x create `template.miproject` with:
   - the original cast as characters, named like the actor ids (or use `--map actor=Name`),
   - one camera,
   - one audio track with any sound file,
   - the set/world.
2. Check it: `python -m cinefactory.cli block-mineimator-inspect --file template.miproject`
3. Export an episode:
   `python -m cinefactory.cli block-mineimator-export --file examples/block_animation/original_episode.json --template template.miproject --out out/ep.miproject --map builder=Nova --map friend=Pip --audio out/ep_mix.wav`
4. Open `out/ep.miproject` in Mine-imator and check: do arms swing forward, does the
   character walk the way it faces, does the camera look at the actors?
   Wrong direction = flip the matching `sign` in `config/block_animation/mineimator.yaml`.
   When all are right set `calibration_status: CALIBRATED` and log it with `tools/cf_decision.py`.
5. Render from the Mine-imator UI, then continue with `tools/cf_auto_edit.py` / QC as usual.
