# CineFactory OS — Connection Recovery, P0 Research Improvements
Date: 2026-10-10 Asia/Bangkok | Scope: actual code and evidence check, not a cinema-grade output certification.

## Confirmed starting checkpoint

- After reconnection: main branch `visual/v1.6.2-fidelity`, HEAD `093a103`, six partially written source/test changes from disconnected session.
- Recovered three new modules: `shot_timeline.py`, `niche_work_orders.py`, focused scanner budget in daily CLI. Prior failed attempt had NOT committed these.
- Resumed safely, verified original tests and completed missing tests.

## Scanner — actual public run on 10 October

CineFactory attempt `CINE-P1-20261010-002`, original canonical Company Youtube run `cine_p1_daily_20261010_002`:
- `focused` scan completed in 131.15 seconds, `runner_timed_out=false`, 30/30 P0 frontier/coverage queries complete, exit code 1 due to missing required official proof, not timeout.
- Canonical run itself did 60 discovery queries, 60 successful, 240 observations, 201 unique channels; it spent its configured budget on only 12 About lookups (approx 5.97% of public channel surface). No age 1–90 public channel shortlist found and **zero video catalogs** collected.
- There is NO official YouTube Data API key in environment. Independent 0–30d channel age and 2× 1M ≥8min conditions **are not verified**; five-gate niche readiness and current evergreen/market economics are not evidenced.
- **Critical semantics corrected:** previous prescreen output said `NO_PROMISING_PUBLIC_CANDIDATES` despite 0 catalogs. Code now returns `INSUFFICIENT_CATALOG_COVERAGE`, with public channel count, About lookup count/coverage and a source-proven limitation about unexamined channels. Recheck result stored at
  `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\focused_prescreen_corrected.json`.
- This is a bounded proof the focused path can finish; it is **not** proof a new channel with two million-view videos has been discovered. Longer scans with broader About and catalog budget/credential may be required. Do not simply reclassify old channel candidates as winners.

## Approved niche Research Pod — three actual work-order lanes

`niche_work_orders.py` generates source-hashed, immutable assigned video research tasks from a `watch.json`:
1. `leader_historic_and_new`: mature leader videos for format/acting/style comparison;
2. `newcomer_breakout`: provisional new-channel leads, even if not strict two-million yet; watchlist only;
3. `fresh_trends_0_15d`: fast recent clips/long-form leads requiring exact format check.

The task packet lists mandatory script/director/acting/camera/art/audio/edit/packaging/rights/tool-scout research, all `NOT_OBSERVED` until actual inspected footage exists. The dispatcher now writes `research_work_orders.json` beside each valid `watch.json`. Neither module silently uses Claude, YouTube APIs, videos, SaaS credits, automatic publishing or unauthenticated approvals.

**Limitation:** owner-authorized pods and fresh cryptographically verified Company bridge snapshots are prerequisites; the current local state previously returned `NO_PODS`. The dispatcher is not itself a job scheduler, and it does not acquire fresh media.

## Actual footage structure — objective FFmpeg shot segmentation

`shot_timeline.py`:
- Requires explicit authorization `OWNED`, `LICENSED` or `SOURCE_OWNER_PERMISSION`.
- FFprobe establishes duration, video stream geometry/audio stream existence; FFmpeg detects visible scene cuts from sampled frames in a bounded time window.
- Returns approximate segment start/end/time, source SHA-256, coverage ratio and estimated boundary resolution; does NOT infer plot, emotion, true camera lens, lip-sync or audio semantics.
- CLI `python -m cinefactory.research_intelligence shot-timeline ...`.
- Live run: original owned synthetic 12s video successfully processed, `VISUAL_BOUNDARIES_ONLY_FULL`, **1 detected segment** (the content did not present a strong cut at the configured threshold), 100% duration coverage. This is not an animation-quality benchmark.
- Report:
  `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\local_scene_timeline_verified_run01.json`.

## New CLI entrypoints

```powershell
python -m cinefactory.research_intelligence daily-run --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState" --day 2026-10-10 --retry --profile focused --timeout 210
python -m cinefactory.research_intelligence pod-dispatch --pods-root "<AUTHORIZED_POD_ROOT>" --bridges-root "<VERIFIED_BRIDGE_ROOT>" --output-root "<NEW_WATCH_OUTPUT_ROOT>"
python -m cinefactory.research_intelligence shot-timeline "<OWNED_OR_LICENSED_VIDEO.mp4>" "<NEW_TIMELINE_JSON>" --permission OWNED --max-seconds 180 --fps 3
```

## Acceptance boundary & remaining P0

- Need more effective fresh-channel discovery and expanded About checks; current focused scanner collected 12/201 About rows and 0 age-fit catalog, not exhaustive market evidence.
- Need official channel and video verification via quota-limited channels.list/videos.list, plus 5-gate evergreen/novelty/entry/economics/rights review.
- Need durable approved-pod scheduling that handles target date, snapshots, task retries, failure alerts and owner approval UX.
- Need actual full-video VLM+audio inference, independently reviewed scene-level actor/character/camera/animation studies. The local 256M VLM experiment FAILED quality and is not auto-routed into production.
- Need real benchmarked Blender/Unreal/Comfy workflows on identical creative pilot shots, human-adjudicated expressive acting/identity/continuity, Resolve editorial/color/sound finishing, and 8+ min long-form acceptance.
- Current model/tool inventory and local RTX 3060 are not treated as hardware ceilings; larger GPUs/cloud/SaaS require separate rights, cost and runtime evidence.
- All plans and study packets are provisional until evidence supports them. No revenue, virality or Disney-parity guarantee.

**Bottom line:** Improvements recover missing partial modules, make focused public discovery operational within a bounded attempt, add honest coverage diagnostics and real preliminary scene timeline + three-lane work orders. Research and cinematic output are NOT yet production-certified.


## Actual Windows scheduler improvement after code checkpoint

Existing daily scheduled task `CineFactory_Research_Daily_P1` is enabled, interactive ADMIN, set for 08:10 Asia/Bangkok. Its prior script used `--profile light --timeout 5400` and did not include `--retry`. On 2026-10-10 the two earlier attempts already created daily reports, so the prior script would have collided with the daily partition if triggered.

The external script `C:\Users\ADMIN\Downloads\CineResearch_DailyState\run_cine_daily.cmd` has been updated to `--profile focused --timeout 600 --retry` without changing the scheduled clock time. Exact original backup: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\run_cine_daily_before_focused_20261010.cmd`. Both backup and new live script were read back and compared.

This task has **NOT YET BEEN OBSERVED RUNNING SUCCESSFULLY THROUGH TASK SCHEDULER** at the time of patch. It uses `Interactive only`, so the account may have to be logged in. A quick focused scan can be incomplete/blocked; it improves bounded schedule reliability but reduces About/channel coverage. The owner may restore the backed-up longer light profile for deeper scans once timeouts and throughput have been addressed.

The schedule does not replace official API verification, full-video competitor study, per-scene agent research, production-pipeline bakeoff or rights review.
