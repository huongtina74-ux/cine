# CineFactory v208 — Channel-First Niche Forensics and Competitor Discovery

Date: 2026-10-10. Canonical Git repository: CineFactory OS integration branch.
Engineering state: metadata forensics integrated, NOT full visual/audio analysis, NOT a verified "winning niche" verdict.

## User contract

When the owner supplies a YouTube channel link (or a linked video), Research must:
1. Resolve the exact channel from the provided YouTube URL, not guess by similar handle or search title.
2. Enumerate a bounded recent-video catalogue, resolve video IDs and use public watch metadata where accessible.
3. Classify EACH video separately: major market, minor subniche, viewer promise / genre, genuine gameplay vs scripted 3D/film vs livestream/machinima, format grammar and source uncertainty.
4. Decide whether the sampled channel is DOMINANT, MIXED or UNKNOWN; do not call two metadata matches a verified whole-channel niche.
5. Generate specialized English-primary format search queries, with safe recurring generic motifs from the actual sampled titles. Never take a competitor's unique title, proprietary character name, thumbnail or script as a creative template.
6. Search videos with the existing free public yt-dlp collector, then read source metadata and reject same-keyword but different-format, different audience, wrong media truth, live or short entries.
7. Group peer videos by exact channel ID. Only channels with >=2 different matching sampled >=8-minute NON-LIVE videos enter the metadata competitor shortlist. A single video is a lead, not a confirmed competitor.
8. Readback of exact YouTube provider data and actual visual/audio/timestamped video review remain separate verification gates. Do NOT claim to have watched a video merely from title/thumbnail metadata.
9. Preserve unresolved sources and known failures. No Research result alone authorizes a paid video API, factory production, copying reference characters or public publishing.

## Where the upgrade actually lives

- cinefactory/studio/channel_forensics_v208.py: per-video taxonomy, channel mix evaluation, keyword ontology, generic recurring topic extraction, strict video peer scoring, two-sample channel peer threshold.
- cinefactory/research_intelligence/channel_forensics_runner_v208.py: bounded public catalogue + watch metadata using the EXISTING PublicYoutubeClient/yt-dlp transport in daily_youtube_breakout_v199.py. Canonical YouTube host/path validation, limits, error receipts, optional peer search, source snapshot SHA.
- cinefactory/cli.py: channel-forensics with --channel-url, optional --search-peers, --max-videos, --snapshot-json and --output-file.
- tests/test_channel_forensics_v208.py: offline fake-public-provider scenarios, URL/SSRF guardrails, mixed catalogue, livestream exclusion, precise search phrases, competitor matching, metadata fallback, evidence immutability.

Research outputs are stored in data/research/channel_forensics/<UC-id>/<timestamp>_hash.json by default; explicit custom output path is allowed. Reports contain the raw metadata rows with source flags and a derived interpretation; neither source flags nor "verified" strings in a supplied JSON establish independent evidence.

## Example: correct matching vs keyword noise

Input sample: Minecraft animated school comedy videos.
Expected path: Minecraft > Minecraft Animation > School/Comedy > FILM_ANIMATION.
Search focuses on "Minecraft school animation full episode", "Minecraft classroom animated comedy story", etc.; if repeated observed topics include "teacher", a generic thematic query can supplement precise format queries.

A "Minecraft livestream of real players" search result is rejected as Minecraft Story competitor despite sharing the word Minecraft. A Minecraft gameplay survival result is NOT an animation competitor. A title-only "Minecraft cinematic" is AMBIGUOUS because it might be Blender animation or in-game machinima.

Real livestreams and past livestream uploads never contribute views to the owner's long-form >=8min breakout/RPM niche qualification. Even a livestream archive falsely labeled NOT_LIVE is excluded from long-form peers if its underlying format is LIVE_RUNTIME.

## Live no-paid-credit smoke on user machine

Checked public playlist link: https://www.youtube.com/@LooZoo-f3y/videos
Current flat listing exposed source channel ID UCLeWuM6ZWZ8gLnUCxcUqlSA and two newest sampled listing items:
- 3DZ-_KBK43A : 24m43s ; title concerns Indonesian school bus/car children's nursery rhymes
- 21ez619ezrw : 15m08s ; title concerns Indonesian colors/surprise eggs children's nursery rhymes
The local classifier returned major preschool_3d_musical and minor preschool_musical as a **TITLE/CATALOGUE HYPOTHESIS**, not a visually verified 3D animation finding. Current playlist label was "Car Wheel Song" while the supplied handle was LooZoo-f3y; the EXACT channel ID from the returned listing takes precedence over legacy brand assumptions.

Both individual watch metadata fetches returned "This video is not available" from public yt-dlp access. The runner therefore fell back to flat playlist title and duration, preserving views=null, published_at=null, live_state=UNKNOWN and watch_metadata_readback_complete=false. NO actual video was watched; no age, millions-of-views growth rate, real 3D/render method or RPM is verified. No downloaded media, no credit-spending services.

Raw runtime evidence (not committed to Git):
.tools/deep_audit_20261010/v208_real_loo_zoo_catalogue_only.json
.tools/deep_audit_20261010/v208_live_probe_stderr.txt

## Commands

PowerShell from canonical Git root:

python -m cinefactory.cli channel-forensics --channel-url "https://www.youtube.com/@EXAMPLE/videos" --max-videos 10

Also perform bounded public competitor searches (may be blocked by YouTube; errors are recorded):
python -m cinefactory.cli channel-forensics --channel-url "https://www.youtube.com/@EXAMPLE/videos" --max-videos 12 --search-peers

For externally saved catalogue metadata where live access is blocked:
python -m cinefactory.cli channel-forensics --channel-url "https://www.youtube.com/@EXAMPLE/videos" --snapshot-json ".\local_catalogue.json" --output-file ".\local_research_dossier.json"

Offline snapshots remain USER_SUPPLIED_UNTRUSTED and cannot be mistaken for provider-verified.

## Missing for fully professional channel investigation

- Independent whole-video analysis using authorized frames/audio, actual on-screen media provenance, visual style/characters/camera/animation/editing and professional QC
- Independent API validation of join date, publication dates, views, video duration, channel owner, non-live video status
- Broad channel catalogue cohorts (most viewed / recent / evergreen), rather than only N recent titles, when officially available
- 0-30 day channel cohorts with 2x distinct >=8min >=1M views in <=14 days, demand proof from established channels and actual risk/rights assessment
- Connected YouTube owned-channel Analytics for first-party retention; private competitor watch time and RPM cannot be recovered from public metadata
- Full production technology attribution must be supported by actual media and tool-chain inspection, not invented from titles

Verdict: channel-first format-driven Research and truthful competitor discovery are operational as bounded, testable metadata workflows. Not a human-quality full-video researcher; not a claimed winner scanner without stronger evidence.


## Final test and release assessment, October 10, 2026

- Canonical full regression: **1,435 passed / 3 failed** in 191.53 seconds; no new v208 failures. Raw log: .tools/deep_audit_20261010/v208_final_full_suite.log.
- Research cross-suite for v208, prior daily breakout v199, two-track v201, evidence research and Minecraft v207: **158/158 passed**. Log: .tools/deep_audit_20261010/v208_research_integration.log.
- v208 standalone topic/URL/public-search/fallback guards: **48/48 passed**; no paid API keys and no downloaded competitor videos. Log: .tools/deep_audit_20261010/v208_final_targeted.log.
- The three historical failures are SHA-256 lineage mismatches in test_golden_shot_benchmark_v196 and two assertions in test_real_rig_dataset_v190. Their evidence/worker hashes are preserved unchanged. A clean Python compileall was recorded.
- Real YouTube smoke report: source catalogue available for https://www.youtube.com/@LooZoo-f3y/videos, but watch pages unavailable through yt-dlp. The dossier correctly preserved missing views/date/live metadata and did not elevate the source to a verified visual/audio analysis. See raw evidence above.
- Engineering verdict: READY FOR OPERATOR-SUPPLIED CHANNEL URL METADATA RESEARCH, NOT FOR AUTOMATED FINAL NICHE/COMPETITOR CERTIFICATION OR PRODUCTION GREENLIGHT.
