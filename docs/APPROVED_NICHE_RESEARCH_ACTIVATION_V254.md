# CineFactory v254 — selected niche -> immediate competitor/breakout research dispatch

Date: 2026-10-11. Scope: fix an observed user-selection/activation break, not certify a complete research factory.

## Verified incident
- On live remote PC: `data/research/youtube_breakout/cinefactory_breakout.sqlite3` existed with **zero** `research_niche_approvals`, **12** `videos`, **25** `observations`, zero `research_peer_links`.
- Real 2026-10-11 daily scout log: `branch2_status=NO_USER_APPROVED_NICHES`, `approved_keyword_scan=NO_APPROVED_NICHES_NO_NETWORK_CONTACT`, `approved_keyword_metadata_checks=0`.
- Root: selections expressed in ChatGPT were not durably written to approved-format DB. The standalone `--approve-niche` CLI used to return *before* running any search, even after a valid explicit confirmation.
- The independent daily global scout is capped and **not** a comprehensive within-niche rival/video popularity ranking; channel discovery and full-media QC have their own separate gates.
- Need 3 cohorts: leaders + full popular/recent catalogue, channels born <=30 days + actual creation-proof, long videos >=8 min with >=1M in <=14 days; exclude Shorts/livestreams. Never substitute total lifetime views / simple views-per-day for measured recent growth.

## Fixed now in code
1. After CLI user-confirmed approval, immediately invoke approved-niche keyword research and generate the two-track owner report instead of returning. Research-only; auto-publishing and paid credits remain off.
2. Increase bounded keyword first pass from 3x4 search and 24 total full metadata checks to 4x20 search and 48 total checks for approved formats, while retaining source verification and explicit niche-format title quarantine.
3. Add Minecraft-specific search phrases for JJ/Mikey, Maizen, monsters, Verity and animation; generic unrelated sources no longer dominate that query pack.
4. Store `candidate_competitor_channels` grouped from metadata-verified videos, sorted by observed views, with explicit `verified_same_format_competitor=false` and full-A/V/creation review pending.
5. Regression tests confirm explicit approval dispatches immediately, wrong/missing confirmation does zero network, candidates cannot self-certify as verified rival.

## Important remaining blockers (not represented as DONE)
- Nothing automatically interprets every ChatGPT utterance as a selected-niche database event. The assistant must invoke the explicit approved CLI command when the user has actually selected a niche/format. Do not record approvals from guesses.
- The original DB still has 0 approvals until real selected scope is explicitly confirmed/registered. No specific format was silently approved in this patch.
- The first pass checks max 48 watch metadata records across approved formats. That is **not enough** to claim "all popular videos", and cannot replace the independent v253 broad scan of 575 candidates. Needs separate deeper, paginated, ranked competitor/catalogue collector and independent per-channel discovery.
- Cohort A's verified leader links and B's channel creation provenance still need their own source evidence. Merely collecting candidate channels must not populate `research_peer_links` as verified peers.
- Metadata/title-based format labeling is hypothesis only. Before choosing competitor production pipelines, full native moving-picture/audio review with separate QC is still required.
- The actual scheduler can continue periodic approved niche research only after the DB contains valid approval entries and corresponding scope is selected.

## Operational steps
To approve a **specifically chosen** format in the authorized remote terminal:
`python scripts/run_two_track_research_v201.py --approve-niche minecraft minecraft_gameplay --confirmation "DUYET minecraft minecraft_gameplay"`
Or, for the distinct 3D Minecraft Animation format:
`python scripts/run_two_track_research_v201.py --approve-niche minecraft minecraft_animation --confirmation "DUYET minecraft minecraft_animation"`
Either command triggers an immediate research first pass and owner report. These are EXAMPLES ONLY; do not run without explicit user choice. For repeated daily reports: scheduler already invokes `--scan-approved`.

## Acceptance
- 43 targeted tests pass (approval, metadata guard, two-track). Broader regression suite should be run before production.
- Gitignored screenshot/audio/video material is not committed, third-party IP provenance not inferred.
- Status: **DISPATCH_LINK_FIXED, FULL_DEEP_COMPETITOR_DISCOVERY_PARTIAL**.
