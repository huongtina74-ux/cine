# CineFactory P0 — Candidate-First Public → Official Verification
Date: 2026-10-09 (Asia/Bangkok) | State: IMPLEMENTED_AND_TESTED / NOT PRODUCTION CERTIFIED

## Architecture

The original Company Youtube remains the **only canonical collector**.

1. `Company Youtube/scripts/collect_youtubejs_recent_search.mjs` and `collect_youtubejs_channel_catalogs.mjs` obtain public read-only search, About and catalog clues.
2. CineFactory `public_prescreen.py` reads the existing two canonical raw files **without re-searching**: `raw/lane_b_broad_market_surface.json` + `raw/lane_b_age_1_90_catalogs.json`.
3. Public source dates are date-only and view labels are rounded. Even two displayed million-view videos are `PROVISIONAL_PUBLIC_SOURCE`; the queue is a **request to verify** and no content-production approval is conferred.
4. `targeted_official.py` verifies only shortlisted channel/video IDs using `channels.list` and `videos.list`. Both endpoints are currently documented at **one quota unit per request**. No expensive search.list API calls are made by this module. Quota is bounded by `max_requests` and `max_channels`, with source hash check and candidate-to-queue ID validation.
5. Targeted official metadata is transformed into the contract used by `breakout_proof.py` (exact channel creation date, publication timestamps, views, duration, publication privacy, ownership and live status). It does not prove niche/topic match, originality, YPP status, earnings, evergreen or new-channel competitive access.
6. After strict breakout witness verification, remaining four Five-Gate reviews and CineCouncil still need independent source-backed validation and authenticated owner approval.
7. Daily controller now writes `public_prescreen.json` for a canonical run with eligible raw files, even when discovery is partial, but NEVER labels partial results verified or automatically invokes the official API. It records `public_prescreen.state`, candidate and queue counts.

## Severe data-integrity bug found and fixed upstream

Historical `youtubei.js` catalog rows were sometimes parsed as **millions of views** from UI strings such as `Novira Stories and 4 more`. Old parser regex `([\\d.]+)\\s*([KMB])?` could accept `4 m` from the English word `more`.

* In Company Youtube, `scripts/youtube_public_view_parser.mjs` now parses strict view labels. Bare compact values like `30K` are accepted **only when paired with a recognized publication-age string in the same metadata row**. Source extraction no longer assumes the first metadata part is always a views field.
* `collect_youtubejs_channel_catalogs.mjs` now exports `view_count_status=PUBLIC_ROUNDED_ESTIMATE` when a valid view label is present and `views=null`/UNKNOWN when absent, instead of pretending 0 views.
* CineFactory's independent `public_prescreen.py` defense-in-depth rejects parsed values inconsistent with the original `views_text` and stores samples of rejected suspicious records.
* A safe original-script backup exists at `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\collect_youtubejs_channel_catalogs_before_view_fix.mjs`.
* Company Youtube source directory does not currently have established git history; backup and Node test are provided, and changes are limited to the collector + new pure parser and test.
* **Important correction:** before this gate the July public archive seemed to have one two-million-video candidate (Novira Stories) appearing in two runs. That candidate was invalid: the displayed views strings were actually channel UI strings. After validation there were **ZERO** such qualifying public leads in the four historical datasets inspected. Do not reuse the wrong old `public_audit_batch/*.json` outputs; use files ending `_corrected.json`.

## Real experiments, not just mocks

- Four archived canonical `youtubei.js` lane-B datasets were inspected: 7 + 27 + 29 + 18 = **81** suspicious source view labels at or above the 700,000 proxy threshold. After rejection, **zero** two-million candidates remained from those four source batches. Historical archives do not establish current October opportunities.
- A live public catalog check on 2026-10-09 against the identified channel `UCex6Dlxtpo36FWRsYU6pICQ` returned eight video records with `collection_status=VERIFIED` for the **unofficial** channel-video page retrieval. Example: `30K` with `22h ago` was stored as approximately 30,000 views; `1.5K` / `2d ago` stored as approximately 1,500. `PUBLIC_ROUNDED_ESTIMATE`, not exact official API evidence.
- Source for live smoke: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\live_smoke_catalog_v2.json`.
- Company Youtube validators + native parser Node tests + full CineFactory regression passed. No real official recheck was made because no usable `YOUTUBE_DATA_API_KEY` / `YOUTUBE_API_KEY` / `GOOGLE_API_KEY` was detected. Exact official API logic has been tested with injected stubbed responses only.

## Commands

Run after Company Youtube has a fresh canonical dataset:

```powershell
cd "C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6"
python -m cinefactory.research_intelligence public-prescreen --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --run-dir "C:\Users\ADMIN\Downloads\Company Youtube\research\markets\<CANONICAL_RUN>" --output "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\fresh_prescreen.json"
python -m cinefactory.research_intelligence targeted-verify --prescreen "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\fresh_prescreen.json" --output-dir "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\fresh_official" --max-channels 8 --max-requests 4
```

The second command deliberately returns `BLOCKED_NEEDS_OFFICIAL_API_KEY` with 0 network requests when no key is available. It rejects historical queues older than 48 hours. The API key is read from the process environment only, never persisted or logged, and exceptions are sanitized to avoid secret leakage.

Run validation:
```powershell
python -m pytest tests -q
python -m compileall -q cinefactory
cd "C:\Users\ADMIN\Downloads\Company Youtube"
node --test scripts\test_youtube_public_view_parser.mjs
node --check scripts\collect_youtubejs_channel_catalogs.mjs
python scripts\run_all_validators.py
```

## Remaining blockers before closing P0

- A new October discovery run must reach complete source coverage; previous real run was PARTIAL due to timeout.
- Exact official metadata verification needs a permitted credential/data source; none was active during this phase.
- Complete the separate novelty, evergreen-demand, entrant-access and economic/rights gates with real evidence, and then CineCouncil cross-examination.
- Current canonical scanner US/en market restriction and Windows interactive-only scheduler still need operational hardening.
- Retention/CTR/RPM of competitors cannot be obtained from public API and must not be guessed.
- Benchmark multi-day reliability, topic-fit precision and false-positive rate, then audit owner decision permissions before marking P0 complete.
