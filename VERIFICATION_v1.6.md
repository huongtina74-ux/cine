# Verification v1.6

Build-environment verification is intentionally separated from target-machine beauty/render verification.

## Build environment

- `pytest -q`: 66 passed.
- `python -m compileall -q cinefactory scripts tests`: PASS.
- Persistent-worker same-PID protocol: covered by test suite and acceptance harness.
- Zero-API FFmpeg black/freeze QC: covered by dedicated tests.
- EpisodeAssembler → BlockExecutionPlanner coverage: covered by dedicated tests.

## RTX 3060 target machine

Run:

```bash
python scripts/acceptance_block_v16.py
python scripts/benchmark_block_rtx3060_v16.py
```

Do not claim real Blender beauty quality, VRAM use or seconds/frame until those commands are run on the actual machine with Blender and NVIDIA drivers available.
