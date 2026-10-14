# CineFactory P1 — Daily Research Operations
Updated 2026-10-09 | Scope: canonical Company Youtube scanner daily execution, source integrity, monitored handoff.

## What P1 does now
- Does **not** replace Company's canonical `scripts/run_complete_niche_discovery.py`.
- Creates daily run IDs with canonical scanner flags `--channel-age-min 0 --channel-age-max 30`. This narrows the runner's channel age but **does not change the runner's legacy niche qualification policy** to the strict two-million-video requirement.
- Archives a manifest, decision packet, sources and normalized snapshots per attempt with SHA-256 hashes.
- Maps `channel_snapshot_official_api.csv` and `fresh_video_observations_clean_official_api.csv` into `cine_p1_normalized/niche_radar_channel_snapshot.csv` and `niche_radar_video_snapshot.csv`.
- Records `topic_fit=UNKNOWN` until video-to-niche fit is separately reviewed. No candidate is automatically promoted through the five-gate Market Bridge.
- Tracks `COMPLETE`, `PARTIAL`, `BLOCKED`, `FAILED`, or `DRY_RUN` and logs gaps rather than inventing niches. `COMPLETE` means canonical collection + artifact health, NOT independently verified opportunity.
- Rejects concurrent runs with an exclusive lock; daily run is idempotent unless operator explicitly passes `--retry` (creates a new attempt and preserves the earlier one).
- Checks latest report health: no report, blocked/partial, or stale after 36 hours => local alert exit code.

## Local Windows schedule actually installed
Host: `DESKTOP-HJE6A6D`; Windows timezone: `SE Asia Standard Time`.
- Task `CineFactory_Research_Daily_P1`: daily 08:10 local (first scheduled execution 2026-10-10). Runs `C:\Users\ADMIN\Downloads\CineResearch_DailyState\run_cine_daily.cmd`. Lightweight budget: 2 queries/market, 3 queries/window, 20 results/query, 1000 estimated API quota units, 35 max catalog channels; runner timeout 5400 seconds.
- Task `CineFactory_Research_Health_P1`: daily 19:00 local (first scheduled execution 2026-10-10). Runs `C:\Users\ADMIN\Downloads\CineResearch_DailyState\run_cine_health.cmd`.
- Both tasks **Enabled / Ready**, Windows `ADMIN`, **Interactive only**. Computer must be on, not sleeping and user must be signed in. Not a cloud 24/7 service.
- Health task writes a local log and returns nonzero on errors. It DOES NOT send phone/email/push alerts.
- Only a dry-run was executed against the real Company canonical runner as of this revision. Full live execution is not yet independently verified.
- No paid model or Claude Code inference is scheduled and no videos are uploaded.

## Critical current limitations (2026-10-09)
1. No recognized `YOUTUBE_DATA_API_KEY`, `YOUTUBE_API_KEY` or `GOOGLE_API_KEY` in the scanner's environment at verification. Without official proof the canonical runner may collect keyless public discovery clues but marks strict verification blocked. DO NOT claim any qualifying niche purely from those snapshots.
2. Company's single canonical runner is still locked to `US/en`. Other high-RPM markets require tested extension and coverage accounting.
3. Official video metadata does not provide competitor retention, CTR, RPM, paid traffic sources, sponsorship status or guaranteed organic growth.
4. Scanner output does not automatically prove the five owner criteria (novel format, 0–30d channel with two distinct >=1M long-form videos, mature recent audience demand, plausible multi-thousand-dollar economics and newcomer competitiveness). Manual `bridge-import` with audited review packet and `CineCouncil` remains the gate.
5. There is no proof that tomorrow's scheduled live run will finish successfully. Review its result and task history; do not infer healthy operation from Task Scheduler status `Ready`.
6. Scanner writes data to its own `research/markets/<run_slug>` and derives `cine_p1_normalized` inside that newly created run directory. Existing Company scripts, old research runs and channel workspaces are not rewritten. The separate Cine state archive stores copies and hashes.

## Runbook
Run locally from `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`.

```powershell
python -m cinefactory.research_intelligence daily-run --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState" --profile light --dry-run --day 2026-10-11
python -m cinefactory.research_intelligence daily-health --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState"
schtasks /Query /TN CineFactory_Research_Daily_P1 /V /FO LIST
schtasks /Query /TN CineFactory_Research_Health_P1 /V /FO LIST
```

Every day's files: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\daily\YYYY-MM-DD\attempt_001\daily_report.json`; the `snapshot/` folder stores copied evidence + hash metadata. `latest_health.json` points to the last attempt. Local logs: `scheduled_daily.log` and `scheduled_health.log`.

Manual retry of a completed/blocked day creates `attempt_002`:
```powershell
python -m cinefactory.research_intelligence daily-run --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState" --profile light --day 2026-10-10 --retry
```

To pause automatic scanning (no deletion of files), or resume it:
```powershell
schtasks /Change /TN CineFactory_Research_Daily_P1 /DISABLE
schtasks /Change /TN CineFactory_Research_Health_P1 /DISABLE
schtasks /Change /TN CineFactory_Research_Daily_P1 /ENABLE
schtasks /Change /TN CineFactory_Research_Health_P1 /ENABLE
```
To remove tasks only: `schtasks /Delete /TN CineFactory_Research_Daily_P1 /F`, `schtasks /Delete /TN CineFactory_Research_Health_P1 /F`.

A stale `run.lock` following interruption is **not auto-deleted** to avoid two concurrent scanners. Verify there is no active scanner before manual lock recovery.

## How P1 feeds P0 / P2
1. Daily canonical runner produces public evidence (or BLOCKED report).
2. `native_adapter.py` normalizes publicly observed channel/video data; it explicitly leaves topic fit `UNKNOWN`.
3. An audited reviewer packet records originality, mature channels/recent demand, entry proof and a monetization scenario with source timestamps. Absent proof remains WATCHLIST.
4. `market_bridge.py` enforces two distinct videos, >=8 minutes, >=1M views each, 0–30d channel age, no Shorts/live, exact video URL/ID, novelty/evergreen/business/entry. `AUDIT_READY` still requires independent authenticity verification.
5. Only canonical owner portfolio promotion + explicit owner event can configure `niche_pod.py`. Watch tasks use imported immutable snapshot hashes; no automatic paid Claude work.
6. `CineCouncil` reviews same evidence, debates and proposes experiments; owned-channel Analytics must be linked and QC pass before learning can be authorized.

## Acceptance tests so far and next gate
- Unit/integration fake canonical runner: lock, once-per-day, retry, blocked semantics, output hashes, data normalization, health.
- Real Company canonical `--dry-run` on 2026-10-09: executed successfully with `DRY_RUN` state and `api_key_present=false`.
- First real scheduled task output and reliability have **not yet been measured**.
- Next: evaluate first real daily run logs, improve US/en limitation and official/keyless source validation, compare normalized data to real ground truth, then implement a truly verified niche report with market breadth and a licensed/authed owner approval flow. No declaration of `PROFESSIONAL_OPERATIONAL` until observed.
