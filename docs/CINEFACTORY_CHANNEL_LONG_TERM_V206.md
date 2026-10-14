# CineFactory Channel and Franchise OS v206

Date: 2026-10-10.
Canonical checkout: C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6
Release verdict: ENGINEERING FOUNDATION ONLY. NOT A COMMERCIALLY CERTIFIED CHANNEL OR FILM STUDIO.

## Purpose and operating structure

CineFactory v205 delivered single-video ProjectDNA and FormatDNA, but lacked long-lived channel/series identity. The v206 layer introduces:

Company portfolio -> Minecraft main niche -> subniche -> format -> proposed original channel brand -> series -> season -> episode -> film project -> rendered shots -> independently accepted film -> owner-owned Analytics.

Maizen and BigSchool are channel examples within Minecraft; JJ & Mikey is a character duo, not an independent niche. Their structures are research benchmarks ONLY. No reference script, character, skin, voice, title/thumbnail treatment or copyrighted asset becomes reusable source material.

## Actual v206 implementation

- cinefactory/studio/channel_franchise_v206.py defines original ChannelBible, OriginalCharacter, SeriesBible, EpisodeCard, GrowthPolicy, episode-specific source-hash strategy, risk and long-term slate diagnostics.
- The canonical storage is data/channels/{brand_id}/channel_bible.json. Registration is create-only and revalidates all Pydantic fields on writing. A changed bible invalidates a previously compiled source-hash-locked blueprint.
- StudioProjectSpec includes three optional fields channel_brand_id, series_id and episode_id, which must be supplied together.
- CompanyOrchestrator attaches CHANNEL_IDENTITY and SERIES_EDITORIAL stages to existing professional Minecraft story blueprints; CREATIVE_STRATEGY, STORY_ARCHITECTURE, WRITING, PRODUCTION, FINAL_QC and PACKAGING depend on episode/series lineage. Existing v205 projects without channel binding keep their stage graphs.
- FilmCompanyHandlers rereads source channel identity before recording, checks source SHA-256 and locks channel character/world/promise, passes an original episode hook/conflict/payoff and series continuity policy to the story scaffolding, then records script source lineage. Planning is NOT an independent artistic signoff.
- Before channel-backed Minecraft PRODUCTION, the character factory must assign each original cast ID a distinct existing MINECRAFT rig in BlockAnimationLibraries and bind rig.identity.original_character_id to the correct actor. Draft actors with missing rigs, mismatched identity or unreviewed rights fail closed. Technical rig linkage does not certify actor performance or genuine legal rights.
- Packaging includes series and episode IDs and explicitly states release is not authorized.
- cinefactory/studio/channel_growth_v206.py uses the already-connected GoogleYouTubeOwnedAnalyticsTransport from v205 for live owned-channel observations. Saves immutable observations under the same channel, generates experiment hypotheses that are always unpromoted until independent verification. Never uses public competitor RPM as owned metrics.

## Minecraft subniches in one shared production engine

1. Minecraft Story/Adventure - original character arcs, exploration and emotional payoffs.
2. Minecraft School/Comedy - original ensemble conflicts and recurring school/world assets.
3. Minecraft Challenge/Survival - original puzzles and fair rules, not copied stunts.
4. Minecraft Monster/Fantasy - original creature lore and mythology, to be developed.

New subniches and formats reuse the same approved Minecraft character-rig, animation, scene/camera and technical QC factories. They do not become separate repositories or costly API-based pipelines.

## Draft starter example (not an owned channel)

The draft working name Lantern Vale Stories is NOT brand/trademark verified. It contains original draft characters Orin, Tessa and Nori; three series called lantern_trails, workshop_days, redstone_trials; nine original episode premises; world rules and continuity/character-growth constraints. The 12-week planner has only nine candidate episode slots, so reports an editorial inventory gap instead of fabricating a full schedule. No signed rights, finished movie or YouTube brand exists from this starter.

## Safe commands in canonical PowerShell

cd "C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6"

Create DRAFT channel (only when owner chooses a working name):
python -m cinefactory.cli channel-init --brand-id my_original_minecraft --working-name "Original Brand Pending Clearance"

Preview a 12-week candidate slate with no scheduled publication:
python -m cinefactory.cli channel-slate --brand-id my_original_minecraft --weeks 12

See the immutable series episode:
python -m cinefactory.cli channel-episode --brand-id my_original_minecraft --series-id lantern_trails --episode-id lt_bridge

Compile the REAL company episode plan using the persistent channel:
python -m cinefactory.cli company-plan --project-id lt_bridge_001 --prompt "Produce one original Minecraft pilot with persistent original characters and world continuity" --niche minecraft --channel-brand-id my_original_minecraft --series-id lantern_trails --episode-id lt_bridge --duration 60

Only after separately authorized actual private upload, observe owned-channel performance:
python -m cinefactory.cli channel-observe --brand-id my_original_minecraft --series-id lantern_trails --episode-id lt_bridge --verified-private-receipt "PATH_TO_REAL_PROVIDER_RECEIPT_JSON" --owner-analytics-oauth-file "PATH_TO_OWNER_OAUTH_TOKEN"

The last command requires owner-verified Google OAuth for an existing owned channel and a real provider receipt. It does not upload videos or change privacy. Never commit OAuth tokens or signing private keys. It does not claim causal learning after a single observation.

## Sustainable channel operating policy

- Stable audience and entertainment promise, identifiable original characters with consistent looks and behavior, persistent world geography, episodic closure plus multi-episode arcs.
- 70% minimum evergreen editorial inventory; experiments max 20%; trend chasing max 15%; do not produce near-duplicate content or filler.
- Candidate publishing cadence is a planning target, never a forced release: quality over schedule, with a target buffer of three genuinely QC-accepted episodes.
- Real growth KPIs: accepted footage seconds per worker-hour, first-pass scene/art/audio QC rates, original asset/rig reuse, repeat viewers and watch-time obtained from owner-authorized YouTube Analytics when available. No fabricated CTR, RPM, impressions, or earnings projections.
- Brand, world, script/characters, artwork, music, release rights and title/thumbnail expression need independent approval.
- Pilot gate: a completed original 30-60 second film approved for acting, lighting, camera, audio, identity, copyright and continuity, not a synthetic slate.
- Scale gate: an independently accepted 8-10 minute complete film, then measured retention across multiple comparable releases, then controlled experiments and reviewed improvements.

## Pending work

1. No registered YouTube channel created by the software upgrade. All draft brand names need independent availability, ownership and legal review.
2. No genuinely qualified 8-10 minute original Minecraft film. Prior v197 pilot was not art-qualified. Models/assets/camera/acting/sound must still be validated through real production.
3. Real Research -> authorized Production greenlight and owner-only public publishing remain fail-closed until source evidence and permissions exist.
4. Three historical Blender provenance SHA checks are not waived; do not edit original evidence.
5. Existing 26 department charters do not prove every department has Disney-class skilled execution.

No changes here authorize spending paid AI credits, copying competitor characters, deleting historical artifacts, public uploads, or unreviewed self-modification of channel rules.

**ENGINEERING VERDICT: CHANNEL IP + SERIES/EPISODE CONTINUITY WIRED TO CINEFACTORY; AUDIENCE LOYALTY AND COMMERCIAL SUCCESS NOT YET VERIFIED.**


## Actual validation report: v206 final complete suite

- Final complete regression from the canonical Git checkout: **1,360 passed / 3 failed**, runtime 195.32 seconds. Log: .tools/deep_audit_20261010/v206_final_exact_suite.log.
- The three outstanding failures are the existing v190/v196 original Blender animation worker source SHA lineage checks. No test fixture/hash was rewritten or suppressed to hide these mismatches.
- Final targeted v206 channel/series, original character rig and v205 handoff regression: **45/45 passed**. Log: .tools/deep_audit_20261010/v206_final_actor_regression.log.
- Python compileall passed, Git whitespace diff verification passed. The code changes are confined to canonical CineFactory source, CLI, its docs and regression tests. No channel upload, copyright-source ingestion, paid external video API calls or production deployment occurred.
- The character factory now refuses original-channel renders with missing rigs, DEBUG_BLOCK rigs, reused rig identities, unreviewed declared character rights, or a mismatch between an original actor ID and the actual registered Minecraft rig identity.
- Final acceptance remains **WIP / NOT PRODUCTION QUALIFIED**. Real channel owners, unique brand clearance, original finished pilot, independent performance/art/rights QC, a qualified full-length episode and owned-channel Analytics are still required.
