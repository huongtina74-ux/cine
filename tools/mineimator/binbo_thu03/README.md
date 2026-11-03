# Bin & Zu: Mine-imator test scene 03 — "Zu smells pizza" (16 s, no dialogue)

This is an expression and camera reel. It was built after a frame-by-frame look at competitor videos (`reports/research/2026-11-03_expression_camera_study.md`) and the measured benchmark (`reports/research/2026-11-03_quality_benchmark_thu02.md`).

| Shot | Frames | Acting | Camera |
|---|---|---|---|
| S1 | 0–71 | Zu sniffs; heart eyes snap on, blush pops, hearts float up, head rolls side to side, hands clasped | Low-angle push-in ECU, dutch 8°, DOF |
| S2 | 72–107 | The pizza is revealed: sparkles, steam | Over-the-shoulder crash zoom (FOV 55 → 17 in 6 frames) |
| S3 | 108–167 | Bin's double take: anticipation dip, head stretch → squash → elastic settle, brows jump off the face, popped eyes, scream mouth, arms fly up, "!" pops | MCU push, dutch −6°, camera shake |
| S4 | 168–239 | Zu crouches (squash), launches (stretch), arcs onto the table, lands with a squash, sparkle eyes | Worm's-eye tracking, dutch 10°, shake on landing |
| S5 | 240–311 | Zu eats: squeeze eyes, chewing mouth, 3D cheeks puff with each chew, crumbs fly | High-angle ECU, DOF |
| S6 | 312–383 | Bin: awkward wavy smile, sweat drop slides, "?", scratches head, then laughs; Zu hops happily | Pull out from MCU to the wide set, vignette |

## Pipeline

    python prep.py WORK          # skins + face parts (scene 02 kit + new states) + fx textures
    python build.py WORK         # -> WORK/proj/BinBo MI thu 03.miproject (+ timing.json); ships only the textures it uses
    # copy WORK/proj to C:\Users\ADMIN\Mine-imator\Projects\BinBo MI thu 03\ ; Render > Render animation (1080p, 24 fps)
    python mix.py                # (in WORK) SFX on every beat + light loop, -14 LUFS

**Set.** The set uses Mine-imator's own blocks: `planks` (oak, birch, dark oak), `bookshelf`, `flower_pot` and `wool`. It is built from block templates with `repeat`, so no third-party world or pack is needed.
