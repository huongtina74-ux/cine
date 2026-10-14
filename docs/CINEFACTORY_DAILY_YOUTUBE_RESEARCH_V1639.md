# CineFactory v1.6.39 — Local Daily YouTube Research

Date: 2026-10-09. Status: public-source daily scanner, evidence ledger, local 08:00 Windows schedule CREATED. NOT video streaming, AI reasoning runtime or production-qualified content.

## Corrected architecture

The previous advisory/one-off research modules were not an autonomous CineFactory discovery system. v199 implements the missing local durable process: Windows Task Scheduler -> daily YouTube public search (7 research lanes) -> verify video metadata (20 per scheduled run) -> filter long-form >=8min, no livestream, windows 2/3/4/5/6/7/14/30 days -> SQLite observations -> persistent channel followlist -> early-view research heuristics -> optional public storyboard low-res temporal thumbnails -> daily Markdown and Claude Code JSON handoff. Claude Code is installed locally but NOT automatically invoked (subscriber/budget permission is separate).

Code: cinefactory/studio/daily_youtube_breakout_v199.py; cinefactory/studio/youtube_storyboard_research_v199.py; scripts/run_daily_cinefactory_youtube_v199.py; scripts/seed_reference_channels_v199.py; scripts/daily_cinefactory_research_v199.ps1; scripts/install_daily_cinefactory_task_v199.ps1; tests/test_daily_youtube_breakout_v199.py. CineFactory appctx and professional_company share lazy daily_youtube_breakout_research advisor; initializing it performs no network operations.

## Actual observed public-source runs

2026-10-09: initial bounded YouTube queries returned recent English Minecraft/animation and other candidates; a full rerun verified 7 search lanes, 14 detailed video metadata attempts, 5 recent >=8 min videos, and 18 low-resolution official Youtube storyboard thumbnail samples for two shortlisted candidates. Rerun status RESEARCH_PARTIAL (3 failed metadata lookups), not falsely 100% coverage. True growth not known from one short-time-series observation. No video/audio streams decoded.

Seeded competitor watchlist with Maizen (UCJHBJ7F-nAIlMGolm0Hu4vg) and BigSchool (UC-Diq5SjWZDol8C0_E_1Y7A), identifiers verified from the two user-supplied YouTube video IDs. Channel creation dates UNKNOWN, not <30d proven. Each day refresh recent uploads of saved followed channels and automatically follow high-view recent discovered channels. Search is non-exhaustive, upload-time precision is UTC day only, no precise YouTube recommendation or RPM claims.

## Windows schedule

Registered native task CineFactory-Daily-YouTube-Research. Windows confirmed Ready, next run 2026-10-10 08:00 +07:00 local. Windows must be running and the user signed in: task LogonType InteractiveToken, StartWhenAvailable enabled. This is NOT a cloud daemon when computer is powered off. No paid provider, subscription account, Google API key, or third-party installer.

Manual from repository root: python scripts/run_daily_cinefactory_youtube_v199.py --live --with-storyboards
Check actual task with Get-ScheduledTask -TaskName CineFactory-Daily-YouTube-Research; Get-ScheduledTaskInfo -TaskName CineFactory-Daily-YouTube-Research.
Disable if desired: Disable-ScheduledTask -TaskName CineFactory-Daily-YouTube-Research.

Storage: data/research/youtube_breakout/cinefactory_breakout.sqlite3, runs/, daily_reports/, storyboards/, claude_handoffs/, logs/ and seed_competitors_v199.json. No files uploaded. Claude brief is an advisory JSON task packet; no Claude LLM invoked, no tool or publishing authorization.

## Critical limitations and follow-up

1. Official YouTube Data API (within user's free quota, key not yet configured) improves published-date filtering and channel creation date; public yt-dlp search cannot guarantee it has seen every channel/video across 2-30 day windows.
2. Storyboard JPEGs are selected static public thumbnails, not video playback, full shot analysis or actual audio hearing. YouTube media 403 prevents claiming fully watched competitor footage.
3. A Claude Code agent with explicit account usage/budget permission must be connected for autonomous model reasoning and production tasks. Packet cannot pretend a model ran.
4. Video virality is not guaranteed by any scanner, model or tool. Need original content differentiation, real A/B production pilots, retention data from own channel, human and copyright approval.
5. Internal tests/real run do not certify fully automatic multi-niche film studio: this version only closes the daily discovery/evidence/follow-up research gap.

No Git commit/reset/clean, installs, revenue promise, automatic upload or paid video watch performed.
