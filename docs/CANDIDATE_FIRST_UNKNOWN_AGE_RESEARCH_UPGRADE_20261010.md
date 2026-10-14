# CineFactory: Candidate-First Unknown-Age Channel Discovery — Real Implementation
Date: 2026-10-10 Asia/Bangkok
Status: BOUNDED LIVE RESEARCH WORKFLOW VERIFIED; STRICT CHANNEL-AGE/2×1M NICHE GATE NOT PASSED.

## The production root cause that was fixed
Earlier P1 scans saw approximately 200 channels, but very few About lookup completions. The scanner collected Videos-tab catalogs **only** for channels with a known 0–90 day joined date. Thus with 0 such known-aged channels, it collected 0 catalogs and could not distinguish unknown age from absence of breakout talent.

New canonical Company Youtube Lane-B steps after public About reconciliation and before strict known-age catalogs:

1. `build_unknown_age_catalog_shortlist.py` — select a bounded and market-diverse group of UNKNOWN-age channels with >=1 distinct public longform (>=8 minutes) high-view keyword observation, deduplicate by video ID, log exact source SHA; NEVER qualify age.
2. `collect_youtubejs_channel_catalogs.mjs` — sample 15 or more recent Videos-tab entries for each of up to 12 candidate-first UNKNOWN-age channels using the existing read-only youtubei collector.
3. `triage_unknown_age_catalogs.py` + `youtube_public_view_parser_bridge.py` — reject invalid '4 more' or mismatched view labels, filter >=480s, require distinct video IDs, count displayed million/near-million proxies. Produce source-locked triage and targeted About queue for channels with multiple strong videos.
4. `collect_youtubejs_age_rechecks.mjs` — exact About checks for triaged channel IDs. Public day-only join date does not equal official API precision.
5. `join_unknown_catalog_age_review.py` — join source-linked public age and catalog witnesses; exclude mature channels; always set qualified count to zero until official independent metadata verification.
6. Updated CineFactory `public_prescreen.py` consumes the optional, SHA-linked unknown-age review sidecar and exposes separate research-watch fields while keeping strict 0–30d, >=2M and owner approval gates unchanged.

No YouTube Data API key or paid model service was used for this targeted fallback.

## Live results, repeatable evidence

### Isolated trial on Company scan CINE-P1-20261010-004
- Observed 34 unknown-age/high-view-long-form candidate channels from the source after About reconciliation.
- Selected 10 market-diverse unknown-age channels, **10/10 catalogs complete**, **187 Videos-tab entries**.
- Catalog `Ha Sisters` showed five 8+ min million-display public video witnesses; a direct 3-channel About recheck returned joined dates. `Ha Sisters` joined in 2012, and was correctly removed from new-channel breakout consideration.
- No 0–30d 2×1M claim.

### Integrated canonical P1 daily scanner CINE-P1-20261010-005
- `daily-run --profile focused --retry --timeout 600`; runtime approx **156.46 seconds**, no timeout, 30/30 headline market query coverages.
- UNKNOWN-age catalog lane: **12/12 complete**; **180 public Videos-tab items**.
- One two-million-display longform channel (`Bi Huỳnh Gaming`) found; public About joined date **2021-12-31**, far older than 30 days, so **NOT_NEW_CHANNEL**.
- Four catalog-derived About targets queried; 4/4 public About joined dates returned.
- Strict known-0–30d catalog lane remains empty. Official YouTube Data API key absent. Current Company result: `BLOCKED` and not a verified niche find.
- Updated CineFactory public prescreen separately exposes 12 unknown-age catalog review channels, 1 two-million-display proxy, and zero valid new-channel 2×1M candidates, still `INSUFFICIENT_CATALOG_COVERAGE` for official breakthrough proof.
- Witness/evidence root:
  `C:\Users\ADMIN\Downloads\Company Youtube\research\markets\cine_p1_daily_20261010_005\processed\lane_b_unknown_age_catalog_age_review.json`
- Source-linked Cine report:
  `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\candidate_first_prescreen_005.json`

## New tests / no false qualification
- Company: `scripts/test_unknown_catalog_pipeline.py` tests unknown-age and known-old separation, malformed views text, multiple distinct long video IDs, public-age rechecks and explicit NOT_APPROVED.
- CineFactory: `tests/test_public_to_official.py` new independent sidecar test checks cryptographic linkage and rejects modified triage; prior targeted official verification tests remain passing.
- Key operational invariants:
  - An unknown-age video catalog is a lead, not evidence a channel is new.
  - One long-form viral video cannot satisfy the two-distinct-million condition.
  - Rounded display views, non-8min or unverified Video tab text are not official exact view data.
  - No owner/Council/production authorization from these public observations.
  - Sources are immutable per run and hashed. An observed mature channel gets research-demand status, not newcomer proof.
  - Current Company broad discovery is US/en only and samples channels/videos. The daily 12-catalog budget cannot establish exhaustive market nonexistence.

## Follow-on requirements not certified
To meet the requested daily 0–30d 2×1M proof, further expand keyword/format discovery and compare separate fresh channels; acquire exact official API channel/video metadata, filter >=8m + nonlive, 2 videos each within time bounds, independent mature evergreen proof, entry feasibility, rights, economics, and authenticated CineCouncil/owner decision. No daily routine can promise genuinely new niches every day.

## Final test and backup checkpoint

- CineFactory full `pytest tests`: **322/322 passed**; Python compileall and `git diff --check`: PASS.
- Company Youtube two age tests and two new candidate-first tests: PASS; all **56/56** Company validation cases and JS public-view parser **3/3** PASS.
- Separate Company Youtube source tree is not tracked at its current Git index. An immutable ZIP snapshot of 11 changed / newly created source and regression files was stored at:
  `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261010\company_candidate_first_source_v2.zip`
  SHA-256: `b830600e21298829dc4631f483bd7ecb5993b89500732ef8345819b2729717eb`.
- Company production scheduler `CineFactory_Research_Daily_P1` is enabled at 08:10 but its latest Task Scheduler result code `2` corresponds to an expected `BLOCKED` research result, **not** a qualified niche report. `CineFactory_NichePod_Watch_P2` at 09:00 completed with result 0 and `NO_PODS`. These are separate states; success of a scheduled job does not establish market or production success.
