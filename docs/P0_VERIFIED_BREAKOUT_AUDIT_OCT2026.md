# CineFactory — P0 Verified Breakout Evidence, October 9 2026

## Decision

**P0 PARTIALLY IMPLEMENTED, NOT PROFESSIONAL-OPERATIONAL.** This phase closes the deterministic *channel breakout witness* sub-gate. It does NOT certify five-gate niche opportunity or monetization.

## Single architecture, no duplicate scanner

- The canonical public discovery and official data collection remain in `Company Youtube/scripts/run_complete_niche_discovery.py`.
- CineFactory `research_intelligence/breakout_proof.py` audits the existing canonical `raw/official_api_integrated_scan.json`. No new API costs, collector or paid model is introduced.
- The daily controller invokes the strict audit **only when canonical scanning exits successfully, reports COMPLETE, provides normalized data and passes artifact health**. Partial or timed-out source files never become new verified candidates.
- The new CLI command is:
  ```powershell
  python -m cinefactory.research_intelligence official-breakout-audit "C:\Users\ADMIN\Downloads\Company Youtube\research\markets\<RUN>\raw\official_api_integrated_scan.json" "C:\Users\ADMIN\Downloads\CineResearch_DailyState\audits\<RUN>.json"
  ```
- The daily report field `channel_breakout_audit` includes the audit state, witness count and evidence path. `owner_review_eligible` remains false until all five niche gates and owner verification are completed.

## Gate details

Each witness channel must have:
1. Channel ID and matching channel data from canonical official source with an exact timezone-aware creation timestamp.
2. 0–30 days age **at source observation**, not 0–30 days as of now when replaying archived records.
3. At least **two different** verified video IDs owned by that channel, each with an exact publication time no earlier than the channel creation date and no later than the observation date.
4. Each video at least 480 seconds, at least 1,000,000 exact integer views at observation; videos must not be Shorts, live, private, wrong-format, invalid URL or have unresolved global catalog duplicate IDs.
5. A historical snapshot that already shows >=1M views while the video is <=14 days old is sufficient proof that the video passed 1M within 14 days (no inference of the exact hour it crossed 1M).

The report never infers competitor CTR, true RPM, monetization approval, ownership rights, post-14-day breakout from a single older snapshot or audience retention. Title-level rights heuristics such as `Hindi dubbed` and `full movie` prompt human review, not a legal infringement judgment.

Each witness yields a **pending review worklist** for niche/format distinction, independent mature-channel demand, newcomer competitiveness, revenue economics and rights/originality review, and CineCouncil cross-examination.

## Real archived API data validation

The verifier was run against **13 historical official API datasets** from Company Youtube (June–July 2026; one source contained zero channel/catalog records). There was one source snapshot satisfying the new-channel, two-long-form, two-million-video evidence sub-gate:

- Snapshot: `us_broad_niche_discovery_2026-07-03_v2`, originally observed 2026-07-03T09:36:29Z.
- Channel: Movie Art Studios, `UCNpt-MWs1ROKxTw3xV_WUMQ`, created 2026-06-05, **28.02 days old at observation**.
- Video `oDgmJhYdnPY`: 1,544,045 views at 9.953 days age, length 7,564 seconds.
- Video `r70AsAsncac`: 1,047,279 views at 6.806 days age, length 6,207 seconds.
- Both surpassed 1M within 14 days according to the locally stored historical API snapshot taken before each video reached 14 days of age. **The snapshot has not been independently reacquired today.**
- The videos are described as "Action Blockbuster Movie" / "Hindi Dubbed"; rights/originality require clearance. **DO NOT RECOMMEND copying this format or uploading copyrighted film content.**
- **Zero niches certified.** Demand sustainability, originality, entrant access, licensing and actual economics have not been established.

Archived output evidence:
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\historical_audit\us_broad_niche_discovery_2026-07-03_v2.json`

## Test evidence and limitations

- P0 unit tests: both million videos, age bounds, duplicate/cross-channel IDs, malformed URLs, live/short/private exclusion, channel metadata source integrity, historical freshness, copyright-risk signalling and 14-day breakout age.
- Daily controller integration test: the canonical runner emits an official artifact; CineFactory recognizes channel witnesses without converting the legacy scanner's decision into a five-gate approved niche.
- Entire repository regression: 158/158 tests PASS, compileall PASS (checked on Windows host).
- **Still missing:** a successfully completed *current* October official scan (no YouTube Data API key found last verification), cross-market coverage, semantic originality/format QA, evergreen and business gates on real current candidates, daily-to-CineCouncil automatic execution, and a continuous Research Pod with authenticated approval.
- Do NOT report the July 2026 snapshot as a new October 2026 channel. The frozen source is usable for validating the verifier, not for today's opportunity shortlist.

## Next engineering handoff

1. Build a cost-bounded **candidate-first** keyless/public observation lane using the existing canonical youtubei.js outputs; treat its relative dates/rounded counts as `PROVISIONAL`, not official exact evidence.
2. When a candidate might satisfy two-million-longform, request authorized official metadata (YouTube Data API, or independently validated source plus manual review) only for those shortlisted IDs. Preserve failing and missing-data reasons.
3. Attach actual niche/topic classification evidence with video title/thumbnail/transcript when permitted, then mature competitors (2 independent active channels, recent 100k+ videos).
4. Measure per-market quota, duplicate/supply coverage, economics and originality/YPP risks; require CineCouncil to cross-examine each accepted case.
5. Only promote a niche after the canonical five-gate evidence registry and authenticated owner action. `SUPPORTED_FOR_TEST` is advisory and never auto-publishes.
