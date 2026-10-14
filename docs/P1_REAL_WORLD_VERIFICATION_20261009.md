# P1 REAL-WORLD VERIFICATION — 2026-10-09 (Asia/Bangkok)

## Verdict

**PARTIAL — keyword discovery proven, strict new-channel winner verification NOT proven.**

This was an actual remote execution on Windows host DESKTOP-HJE6A6D, not merely a unit test.

## System and schedule checked
- Git starting point: `a1e90d3` on `visual/v1.6.2-fidelity`.
- Scheduler `CineFactory_Research_Daily_P1`: Enabled/Ready, scheduled 08:10 ICT daily; next at 2026-10-10 08:10, Interactive only, Windows ADMIN.
- Scheduler `CineFactory_Research_Health_P1`: Enabled/Ready, scheduled 19:00 ICT daily; next at 2026-10-10 19:00, Interactive only.
- Real canonical dry run: `CINE-P1-20261009-001` on 2026-10-09, state DRY_RUN.
- Official environment credential discovery: NONE of `YOUTUBE_DATA_API_KEY`, `YOUTUBE_API_KEY`, `GOOGLE_API_KEY` present; no credential value was copied.
- The canonical Company runner is locked to US/en. No other high-RPM countries have been validated.
- Windows task status Ready is *not* proof of any completed scheduled run.

## Actual bounded live run
- `run_id=CINE-P1-20261009-002`, on 2026-10-09 20:29:22–20:35:22 local.
- Invocation: `python -m cinefactory.research_intelligence daily-run --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --state-root "C:\Users\ADMIN\Downloads\CineResearch_DailyState" --day 2026-10-09 --retry --profile light --timeout 360`.
- Only the keyword frontier stage completed before cutoff; no qualification score or end-to-end success was inferred.
- Verified step01 direct Google/YouTube autocomplete calls: `requests=718`, `errors=0`, `baseline_markets=30`, `dynamic_unique_signals=1197`, `frontier_after_dedup=120`. Coverage matrix has `30/30 COMPLETE` for baseline topic buckets.
- Independent channel discovery lane produced `90` broad-market search queries, but not a complete video/channel evidence set within the six-minute execution.
- Terminal report: `state=PARTIAL`, `canonical_runner_exit_code=-1`, `canonical_run_status=IN_PROGRESS`, `canonical_verdict=BLOCKED`.
- `qualified_niches=null`, `strict_0_30_two_1m_niche_gate=NOT_EVALUATED_WITH_FULL_PROOF`, `owner_review_eligible=false`, `bridge_ready=false`. **No niche is certified**.
- Report: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\daily\2026-10-09\attempt_002\daily_report.json`.
- Canonical raw evidence: `C:\Users\ADMIN\Downloads\Company Youtube\research\markets\cine_p1_daily_20261009_002\`.
- Critical gap: missing official channel snapshot and fresh video snapshot; source verification cannot complete.

## Confirming the keyless research route
One targeted `youtubei.js` search with `upload-date week`, `max-results 5`, `max-about-channels 2` ran on a public `minecraft animation` query:
- `status=COMPLETE`, `successful_query_count=1`, `observation_count=5`, `unique_channel_count=5`, `about_lookup_channel_count=2`.
- Both enriched channel About records belonged to channels older than 181 days; this tiny probe is **NOT** a study of new-channel breakout opportunity.
- Public metadata and about details do not prove a 1M+ long-form strict winner, organic traffic, CTR, retention, actual RPM or YPP.
- Output: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\youtubejs_probe.json`.
- No paid API, OAuth, uploads, comments or private analytics used.

## Real failure found and corrected
The original daily wrapper used `subprocess.run(..., timeout=360)` and killed the canonical Python parent on timeout **but not its Node.js child process**. A live leftover `node scripts\collect_youtubejs_recent_search.mjs` process (PID 23932) was observed after timeout and deliberately stopped with `taskkill /PID 23932 /T /F`. A later process check showed `NO_ORPHAN_FOUND`.

Remediation in code:
1. `_run_with_timeout_tree` launches scanner in its own Windows process group and uses `taskkill /T /F` for the parent and all descendants on cutoff (POSIX process-group stop in other environments).
2. Runner records `runner_timed_out` and a clear `TIMEOUT` gap in daily report; remains blocked/partial rather than falsely complete.
3. Tightened `light` profile from the earlier **12 roots / 26 suffixes** to **2 roots / 2 suffixes** and caps Lane B and recursive exploration. This optimization was code-reviewed/tested but **not measured in a second full live discovery scan**; do not claim a known runtime improvement.
4. Added a Windows regression test that spawns a grandchild process and requires the grandchild to be killed after timeout.

## What the tests establish
- End-to-end local fixture for complete/blocked/missing-key reports.
- Frozen artifact hashes and durable reports, replay prevention, retries.
- Historical native Company artifact mapping (isolated copied official API CSVs) with `topic_fit=UNKNOWN`.
- Watcher doesn't promote hypotheses into owner-approved niche.
- Bounded process-tree termination including child process.
- Native source integrity, council gates and previous CineFactory tests.

## Remaining blockers for Professional Operational
1. No full live successful strict 0–30d/two ≥1M long-form-video discovery run.
2. No validated high-RPM multi-country coverage; canonical is currently US/en.
3. No official API key in runner environment and no equivalent independently validated high-confidence channel-age/video-count source.
4. Scheduled daily task has not yet executed for the first time; only manual run and dry-run tested.
5. No owner-authorized UI approval, no long-running Research Pod executor, no proven semantic video analysis.
6. Health check only writes local log and exit status, no remote phone/push alerts.
7. Windows tasks are Interactive only; unavailable when not signed in.
8. Strict monetization predictions remain modeled, not verified payouts.

## Next gate
Evaluate next complete scheduled run's health and artifact manifest, then run a bounded end-to-end live probe of the full metadata collector with stable immutable snapshots. Only after actual video/channel source confirmation should Market Bridge and CineCouncil generate a proposed niche for owner review. Keep existing WATCHLIST candidates distinct from VERIFIED candidates.
