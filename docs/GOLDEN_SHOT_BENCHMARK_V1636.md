# CineFactory v1.6.36 — REAL Golden Shot Multi-Render-Engine Benchmark

**Date:** 2026-10-09. **Status:** repeatable, same-scene real Blender dual-renderer A/B, candidate promotion BLOCKED. No license/creative signoff or production change.

## Goal and scope boundary

Choose the best qualified production method **for each niche and specific shot** based on actual results at stable quality. This version starts the Experimental Selection Lab with a real controlled *Blender Workbench vs Blender Eevee Next* pilot. Both share the **same original CineFactory .blend**, voxel rigs, geometry, animation, shot camera, key/fill light objects, timeline, FPS and output resolution. Workbench uses its studio-shading look; Eevee uses PBR lighting. Only renderer/shading settings and process start order vary.

**This is two render engines inside one Blender application, NOT Blender vs Godot vs ComfyUI**, nor a high-quality long-form 4K benchmark. The result is valuable technical evidence for the Minecraft department only. It cannot certify CoComelon-like 3D child singing, AI family drama, game physics or the best universal engine.

## Actual CineFactory same-scene build

- Built with the existing trusted `scripts/blender_animation_worker.py` **real production procedural Minecraft character and classroom constructors**, using `mc_a` and `mc_b` identity/config from `data/verification/v190_real_rig_dataset/rig_snapshot_v190.json`.
- New source: `scripts/blender_golden_scene_v196.py`. It creates two characters, arm and torso keyframe acting, slight camera push and scene lighting. The original locked scene is `data/verification/v196_golden_benchmark/golden_cinefactory_original_scene.blend`.
- Shared scene SHA-256: `8778a1829efcbae3c0dc34aa43e7046814b9fe8da2d122b65985fbb91473177c`. Each renderer process opens **this exact saved file**. No worker output/scene used by active production was modified.
- 480x270 at 12fps, 24 frames = 2 seconds, H.264 `libx264 -preset fast -crf 20`, silent output. These are 2s test snippets, not a film ready for publication.

## Real render engine A/B results (RTX 3060 host, 2026-10-09)

| Engine | First run total render seconds, includes Blender startup | Median across 4 process runs | Maximum of 4 runs | First-run MP4 size | Mean sampled PNG luminance [0..255] |
|---|---:|---:|---:|---:|---:|
| Workbench | 4.5284s | **1.3196s** | 4.5284s | 39,996 bytes | 67.6369 |
| Eevee Next | **3.8427s** | 3.8560s | 3.8812s | 72,903 bytes | 133.2106 |

- Four subprocess runs per renderer, counterbalanced order: `Workbench→Eevee; Eevee→Workbench; Workbench→Eevee; Eevee→Workbench`. One first-run sample misleadingly favored Eevee, while multiple runs showed Workbench was consistently quicker after its cold start. Tiny clips and startup warm-up make *both* findings inappropriate for feature-length production choice.
- All 8 runs have 24 real PNG frames with 480x270 dimensions, valid H.264 MP4, video stream frame count 24, signed SHA256 of output/scene, and 12fps.
- The same source scene produced `pixel_repeatability_v196.json`: **72 frame comparisons per renderer** (3 replays against baseline for 24 frames), **144/144 decoded PNG frames EXACT at the pixel/channel level (median MAE 0.0)**. Compressed PNG file **byte hashes differ across runs** despite decoded pixel equality, so distinguish packaging/file-byte repeatability from actual image-pixel repeatability. No moving scene frame within the video is treated as identical to another frame.
- Workbench has much darker shaded output, whereas Eevee appears brighter with different shadow/grain character. Mean luminance, Laplacian edge variance and file size are observed, **not blind perceptual quality, aesthetic preference, acting or story scores**.
- Global `nvidia-smi` memory observations were collected, e.g. first-run baseline ~8778MiB on shared GPU. Workbench observed peak ~8796MiB, Eevee ~9571MiB. This is **TOTAL GLOBAL GPU USED**, not measured per-Blender-process allocated VRAM. Other programs and background activity are not isolated; do not use these as required VRAM specs.
- Blender process startup included in wall time; FFmpeg mux time separately measured. No dollar electricity measurement, retries at scale, human touch time, music rights or final-accepted-minute denominator, so **USD per accepted minute UNKNOWN**.

## QA/artistic conclusions (not signed)

Review image `data/verification/v196_golden_benchmark/golden_renderer_comparison_v196.jpg` shows the same two orange/green original voxel characters and classroom at frames 1, 12, 24. The Workbench look is dark and graphic; the Eevee look is brighter and has softer illumination, a different rendering aesthetic. The clip demonstrates **some arm/torso and camera movement**. It is NOT ready for Disney-level artistic approval; character emotion, staging, acting timing, voice, music, storyboard and scene logic remain unreviewed.

This experiment **does not select a production render engine**: the fastest technical implementation is not necessarily the highest-quality approved output. The workbench variant may be a practical *preview candidate*, Eevee a *lighting/cinema candidate*, but both require an original high-quality niche rubric and actual 4K/longform or 30–60s feature tests to qualify.

## Modules, files, safe operation

- `scripts/blender_golden_scene_v196.py`: creates a locked .blend once, or renders Workbench/Eevee from it without changing canonical worker.
- `cinefactory/studio/golden_shot_benchmark_v196.py`: exact source SHA and actual render subprocess, global VRAM observations, PNG count, image proxy metrics, FFmpeg mux and ffprobe validation. `run_real_golden_benchmark`, `repeat_4_trials_on_same_scene`, `GoldenShotBenchmarkLab`.
- `scripts/audit_golden_repeatability_v196.py`: CV2-decoded per-pixel cross-run comparisons.
- `tests/test_golden_shot_benchmark_v196.py`: 27 evidence/security/false-confidence tests.
- `cinefactory/appctx.py` and `cinefactory/studio/professional_company.py`: share new laboratory advisory service; constructor makes no video. Both `run_explicit` and `repeat_explicit` require `approved_original_scene=True` at time of invocation. Existing active render routes and production selection remain unchanged.
- `data/verification/v196_golden_benchmark/scene_contract_v196.json` + `golden_cinefactory_original_scene.blend` — original scene provenance.
- `real_render_engine_ab_evidence_v196.json` — two first-run render audits.
- `repeatability_benchmark_evidence_v196.json` — 8 actually rendered subprocess runs.
- `pixel_repeatability_v196.json` — 144 frame pixel comparisons across replays.
- `contact_sheet_frame_manifest_v196.json` — six original rendered thumbnails hashes.
- `golden_renderer_comparison_v196.jpg` — side-by-side visual evidence.
- `workbench.mp4`, `eevee.mp4` plus repeatability/round_02..04 video+frames and render logs.
- `benchmark_run_v196.txt`, `repeatability_run_v196.txt`, `pixel_repeatability_console.txt`.
- `regression_v196.txt` — whole project suite once completed.

## Scope-specific promotion gates

Every method stays **PRODUCTION_BLOCKED** until:
1. Exactly the same original shot/video brief has qualified candidates from **two distinct SOFTWARE backends** if cross-software choice is claimed (e.g. Blender versus Godot, not Workbench/Eevee).
2. Machine-aware repeated sample benchmark at meaningful production resolution/duration, frame QC, lights, temporal stability, identity, camera, audio, VRAM and true electricity/walltime.
3. **Blind human reviewer** judges emotion, character silhouette, readability, story, musical sync and production style; stage-specific required quality floor must be met before optimizing time or cost.
4. Assets/character designs/music/voice, game captures, commercial model weights and software licences are verified for the **actual business use**.
5. True **USD per accepted video minute** with render failures, retries, manual animation/cleanup, electric power consumption and storage. Unknown is NOT zero.
6. Multiple independent projects and fail-closed QA, no accidental universal winner.

## Next software milestones

**v1.6.37:** Validate Godot availability via authorized install/portable runtime and build same ORIGINAL physics scene via real-time engine as a different software/backend; if unavailable, report BLOCKED instead of fake comparisons. Increase shot duration and resolution to representative quality pilots.

**v1.6.38:** Original music-first Preschool 3D characters with real original singing/vocal sync, organic deformation, educational review, approved voice/music rights and 30–60s pilot.

**v1.6.39:** Model/ComfyUI actual local video pipeline qualification on 12GB with exact checkpoint model card/weights rights, first-frame/last-frame identity, reroll/retry total cost.

**v1.6.40:** Scene-aware visual/audio QC and real human acceptance data; multi-niche long-form/factory reliability and learning promotion, still under original code and copyright gates.

No commit, reset, cleanup, deployment, new plugin install, paid API or automated YouTube publication is part of this milestone.


## Verified closure — 2026-10-09

- **Full CineFactory suite: 936 passed, 0 failed**, 145.32 seconds, process exit code 0. Previous v1.6.35 baseline was 909 tests; v1.6.36 introduced **27** tests, all focused 27/27 PASS.
- `python -m compileall -q cinefactory scripts tests`: PASS; tracked diff check on active source PASS. Windows newline conversion warnings informational.
- **One actual first-party source .blend** produced **8 complete 2-second H.264 videos**: 4 Workbench and 4 Eevee, each with 24 verifiable PNG frames and a valid 24-frame MP4. Same scene geometry, exact camera and actors verified by source-scene SHA. **Not** a Blender-vs-Godot or Blender-vs-ComfyUI comparison.
- Median render seconds in this short startup-inclusive host benchmark: Workbench 1.3196s, Eevee 3.8560s. First single run favored Eevee, demonstrating warm-up/cold-start confounding. Neither has an approved artistic quality or dollars-per-accepted-minute score.
- Exact pixel reproducibility: 144/144 decoded frame comparisons match channel-for-channel in the same engine against rerendered original, despite PNG container SHA differences. `pixel_repeatability_v196.json` is the independent decoded-pixel verification.
- Side-by-side contact sheet `golden_renderer_comparison_v196.jpg`: human/creative approval PENDING, lighting/look varies substantially; brightness is not quality.
- Global `nvidia-smi` memory observed only, not allocated per-process VRAM. Electricity price, labor, discarded scenes and repeat renders at scale remain unmeasured. No engine automatically promoted.
- Original production workers / deployment left untouched; this milestone was **read-only opt-in evidence collection, local test rendering only**, no model or runtime install, API payment, Git commit/reset/clean or publication.
