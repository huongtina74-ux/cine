# CineFactory OS — Single-Pass Research-to-Studio Engineering Upgrade
Date: 2026-10-10 (Asia/Bangkok) | Status: IMPLEMENTED bounded paths + tests; **NOT ALL BUSINESS/ARTISTIC ACCEPTANCE GATES PASSED**.

## Contract with owner

Build two branches and a high-fidelity media production company. Branch 1 scans daily for genuinely distinct ideas/new formats, 0–30 day channels with 2 independently confirmed ≥1M view videos of ≥8 minutes, verified enduring demand from mature current winners, achievable economics, rights and competitive entry. Branch 2 starts from owner-approved niche pods and continuously studies leaders, newcomers and 0–15 day breakout trends by VIDEO EVIDENCE and multi-disciplinary analysis; produces original story/world/character bibles, decides tools per shot, benchmarks real rendered footage, edits, QC, learns. Zero fabricated earnings or Disney-quality claims.

**What this release achieves:** reliable evidence-first building blocks, real runtime tests, fail-closed quality and scheduling hooks. **What it does NOT:** authenticate a user click, guarantee niche discovery or generate an 8–15 minute professional film with independently proven cinematic quality. These require additional licensed data/assets, model capabilities, backend integration, money/time and controlled acceptance.

## 1. Verified public age-recheck and source-proven channels

Problem: focused canonical Company discovery found 201 channels and initially visited only 12 About pages, then marked 189 unknown-age channels as established controls because `number(missing_age)=0`. A missing creation date is NOT proof a channel is old, and a valid creation age of 0 days should be within the new-channel window.

Patched the live canonical `Company Youtube` scripts:
- `scripts/build_independent_channel_surface.py`: strict date/age check, distinguish `AGE_UNKNOWN_NEEDS_ABOUT`, correct day 0; keep strict catalog shortlist limited to known public ages 0–90; output a **separate** bounded high-view, long-form UNKNOWN-age About review queue (no niche qualification), preserving independent source and multiple distinct videos.
- `scripts/collect_youtubejs_age_rechecks.mjs`: targeted read-only public About collection of exact channel IDs with bounded API calls; day-precision joined date, no claims of official YouTube Data API.
- `scripts/reconcile_youtubejs_age_rechecks.py`: verifies exact queue/source provenance via SHA256, day/date consistency, merges verified **public** About ages into a NEW frozen surface without mutating the original.
- `scripts/run_complete_niche_discovery.py`: fully integrated step03b/03c/03d recheck and refined surface before collecting video catalogs.
- CineFactory `public_prescreen.py`: consumes lineage-checked refined source when present, still requires catalog/video evidence and 5-gate independent review.
- Tests: `scripts/test_age_unknown_surface.py`, `scripts/test_age_recheck_reconciliation.py` (offline pass) and existing CineFactory reference tests.

Real dry to live:
- October 10 initial live: 201 observed channels, 189 unknown age, 13 high-view unknown-age leads; **13/13** targeted public About lookups completed, none found in 0–90d.
- Full integrated live recheck `CINE-P1-20261010-004`, elapsed ~162s without timeout, 202 public channels, initial 12 About lookups plus targeted 10/10, refined source hash stored; 180 still unknown and 0 eligible video catalogs; **canonical state BLOCKED**, `INSUFFICIENT_CATALOG_COVERAGE`.
- Exact 0–30d + 2×1M eligibility remains NOT VERIFIED due missing official YouTube Data API key and absence of qualifying candidates. Never interpret missing catalogs as proof no market niche exists.
- Current wide US/en surface is inherently sampling-biased: the source has very few independently repeated channel videos. Must improve fresh keyword/subchannel frontier, per-channel coverage and add additional high-RPM markets before an exhaustive global claim.

## 2. Approved niche P2 daily event loop

New `cinefactory/research_intelligence/pod_daily_runner.py`: per-date immutable attempt folders, O_EXCL concurrent-run lock, latest snapshot, safe NO_PODS/BLOCKED statuses. Daily read-only niche watch dispatcher now creates a source-hashed `research_work_orders.json` for:
- established large competitor and recent leader uploads,
- new entrants / candidate breakout,
- fresh high-view 0–15d trend leads.

A work order lists frame/source investigation, storytelling/script room, character expression, director camera blocking, animation, world/art, audio/foley, editing beats, packaging, risk and technical bake-off; it NEVER asserts unseen content or owner permission.

Optional `--authorized-media-manifest` and `--max-media-videos` in `pod-dispatch` invoke `niche_media_intake.py` only on paths whose expected SHA and declared rights are verified. No downloads of unlicensed competitor clips.

Windows local script `C:\Users\ADMIN\Downloads\CineResearch_DailyState\run_cine_pod_watch.cmd` is installed as `CineFactory_NichePod_Watch_P2`, scheduled **09:00 daily**, interactive user context. Manual run completed `NO_PODS` correctly. Directories:
- `...\CineResearch_DailyState\approved_pods`
- `...\CineResearch_DailyState\verified_bridges`
- `...\CineResearch_DailyState\pod_dispatch_daily`

**Gaps:** no real owner-approved pod in designated runtime directory; official verified fresh bridges not present. Windows Task Scheduler's actual unattended future execution and after-click activation remain unproven; logged-in Windows account required by task settings. User-facing owner-approval app UI not yet wired to pod activation.

## 3. Actual locally authorized video mechanics + frame/audio research packets

Added `research_intelligence/media_mechanics.py`: on owned/licensed footage, FFprobe and FFmpeg compute true video duration/coverage, approx visual cut timings, approximate cuts/minute, silence start/end, plus source SHA and per-scene unknown semantic review tasks. Does **NOT** mistake silence for dialogue semantics, sparse frame samples for full story or cutting frequency for watch-retention causality.

Extended `niche_media_intake.py`: for each matched owned/licensed source, runs:
1. Mechanical full/bounded timeline + silence analysis;
2. `deep_video_intelligence.observe_authorized_footage` to produce sampled actual frames/audio measurements and seven departmental Claude/reviewer work packets;
3. `production.scene_study.prepare_timestamped_study` to pin every visual note to real image bytes/timestamp.
4. Emits an immutable media intake report without granting rights or production.

No GPU heavy VLM is silently installed or invoked; previous 256M CPU VLM experiment was below quality bar. **Full-video narrative, voice, acting and exact camera intent remain pending a proven multimodal reviewer**. External media rights declarations still require verification.

## 4. Local tool search & live model proof

New `production/tool_runtime_audit.py`: read-only probe of FFmpeg/FFprobe/Blender executables, Comfy localhost endpoint, NVIDIA GPU, nine tool lane metadata and actual render proof if supplied. No paid models, cloud, SaaS, MCP setup or license self-approval. RTX 3060 is merely current measured worker, not a permanent CineFactory hardware ceiling.

Real local Comfy 0.38.0 `/object_info`:
- 669 nodes present; Wan, LTX nodes visible, but *nodes alone do not imply weights installed*.
- A local Wan 2.1 Fun Inpaint **1.3B** checkpoint, UMT5 fp8 text encoder, Wan2.1 VAE identified and actually executed with native ComfyUI nodes.
- `production/comfy_wan_pilot.py`: approved-LOCAL-only, bounded technical text-to-video workflow, artifacts SHA, default 17 frames at 320×192, 8 sampler steps, output H.264 via FFmpeg. Actual result file:
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\wan_1_3b_technical_pilot\wan_technical_smoke.mp4`
- Real output **17 frames, 2.125s, 320×192**, wall ~**16.5s**, playable media confirmed by ffprobe and direct frame inspection. Original robot's silhouette stable across three sampled frames, but little expressive motion, missing requested blue lamp, no sound, extremely small resolution, not a quality film or independent proof of identity consistency. Commercial weight licensing NOT cleared.
- `tool_runtime_audit.py` validates video hash and ffprobe (not just `passed=true`) and labels `LOCAL_VIDEO_EXECUTED_UNREVIEWED`. Blender executable was not found at the preconfigured executable paths; do not claim Blender currently ready simply because Blender worker code is in repo.
- The resulting trial was linked to `production/niche_production_conference.evaluate_comparable_pilots`: **`NO_VERIFIED_ACCEPTABLE_PILOTS`**, resolution below actual ≥720p bakeoff gate, no independent qualitative scores, no rights review, no post-production, no hand-acting/dialogue. This is the expected fail-closed company behavior.

## 5. QC and production integration inherited from earlier commits

`093a103` and `b6cbe71` already eliminated missing-QC=1.0 faults, segregated slate from premium, source-linked director plan and reviewed production conference, and prohibited silent Comfy substitution for a Blender scene. New tests also preserve frozen metadata hashes, invalid model/footage results and immutable observations.

**Still NOT closed:** professional Blender expression/rig episodes, Unreal/Resolve executable integration, original asset library licenses, separate multi-GPU render scheduler, creative fine-cut, shot-to-shot identity consistency, long-form native 4K editorial quality, independent human rights+artistic QC, and real post-publication retention-based learning. These are product acceptance phases, not problems solvable simply by changing an approval Boolean.

## Evidence and reproducible commands

From CineFactory repo:
```powershell
python -m pytest tests -q -p no:cacheprovider
python -m cinefactory.research_intelligence daily-run --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState" --profile focused --timeout 600 --retry
python -m cinefactory.research_intelligence.pod_daily_runner --pods-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState\approved_pods" --bridges-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verified_bridges" --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState\pod_dispatch_daily"
python -m cinefactory.research_intelligence.media_mechanics "<owned_video.mp4>" "<new_output_directory>" --permission OWNED
python -m cinefactory.production.tool_runtime_audit --output "<new_capability_audit.json>" --pilot-report "<real_verified_smoke.json>"
```
Canonical Company (separate, currently untracked working repo) must also test
`python scripts/test_age_unknown_surface.py`,
`python scripts/test_age_recheck_reconciliation.py`,
`python scripts/run_all_validators.py`,
`node --test scripts/test_youtube_public_view_parser.mjs`.

**Release verdict:** A sizeable interoperable technical system is in code, and local video inference truly works. **Do NOT claim cinematic parity with professional competitors or automated YPP profitability.** Next unclosed gates require owner-approved real long-form footage, a capable multimodal VLM/audio model, an original 8–15-minute pilot, professional asset/expression rig and tool install/license/benchmark under suitable hardware, independent human QC and trusted release workflows. These require real-world inputs and repeated evidence, not additional stubs.


## Versioned safety snapshot of the separate canonical Company scanner

Because `C:\Users\ADMIN\Downloads\Company Youtube` currently has no tracked Git baseline for its scripts, the six touched/new source+test files were placed in an immutable ZIP:
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\company_youtube_age_recheck_patch_v1.zip`
SHA-256: `29a8cc7f44d1d1ed4dc3890096f801029008604f23ff6ec6dff8b4f24eb65dd6`.
Its `PATCH_MANIFEST.json` records exact source paths and hashes. This is an archive, **not** an executable installer or permission to overwrite the canonical scanner without review.

The Windows Task Scheduler P2 watch task was confirmed present and enabled. It is **Interactive only**, and its first real scheduled execution has not been observed; a separate manual CLI run returned `NO_PODS` with no model/API calls. The current research strategy cannot truthfully report newly qualified 2×1M videos until sufficiently deep channel catalogs and official metadata have been acquired.


## Final tool-version probe correction

The initial auditor used `--version` for FFmpeg/FFprobe (incorrect flag, caused false VERSION_COMMAND_FAILED despite healthy binaries). Patched `tool_runtime_audit._safe_version` to use `-version` for FFmpeg/FFprobe, `--version` for Blender, plus regression test. Repeated live audit at
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\local_tool_runtime_corrected_v2.json`: **FFmpeg 7.1 and FFprobe executable/version PASS**, ComfyUI 0.38.0 API live with technical Wan render, RTX 3060 12288 MiB. Blender still not present in probed executable locations.

This local Wan clip was also input to the shared Production Conference comparison and correctly rejected: source file hash and FFprobe stream valid, but clip is only 320×192 (strict bakeoff requires ≥1280×720), has no speech/music, no independent quality/rework scores or clearance. Thus `NO_VERIFIED_ACCEPTABLE_PILOTS` remains correct.
