# CineFactory OS 1.6.0 — Execution Completeness / Zero-API Quality

Built directly on v1.5. The goal of 1.6 is not another layer of contracts: it makes the existing Block Animation contracts materially executable by the persistent Blender runtime while keeping production API spend at zero.

## What changed

- Added manifest-driven render-quality profiles with `rtx3060_quality` as the default.
- Added AgX/high-contrast color management, three-point lighting, depth of field, motion blur hooks, higher local render bitrate, bevel/material defaults, and quality/preview separation.
- Added `BlockExecutionPlanner`, a Blender-free normalization layer that turns compiled shots into deterministic execution plans.
- Scene templates now execute either real library `.blend` collections or local procedural room/classroom/street/arena sets.
- Prop bindings now instantiate local/library props and attach them to rig bones or procedural sockets for the requested time range.
- Crowd cues are compiled into actual action/expression streams instead of remaining passive metadata.
- Camera coverage now carries shot size, target mode, framing margin, DOF and motion strength; Blender executes push/pull/track/orbit/snap motion.
- Semantic VFX events execute local impact flashes / sparkle bursts; sound events are preserved in shot/episode sidecars for the audio/editor stage.
- Added deterministic actor facing and basic ground-contact safety.
- Added zero-API FFmpeg visual QC for black/frozen render failures.
- Added procedural zero-API scene library entries suitable for block-style classroom, street and arena work.
- Persistent worker still caches external collections/actions across shots.

## Verification in this build environment

- `pytest`: 66/66 PASS.
- `compileall`: PASS.
- FFmpeg local visual-QC tests: PASS.
- Persistent-worker protocol regression: PASS through existing same-PID test.
- Real Blender/RTX image quality is **not claimed** in this environment because Blender and NVIDIA telemetry are not available here. `scripts/acceptance_block_v16.py` records that honestly and is intended to be rerun on the target RTX 3060 PC.
