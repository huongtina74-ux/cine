# CineFactory Minecraft Subniche Routing v207
Date: 2026-10-10
STATE: CODE TESTED / MEDIA PRODUCTION NOT QUALIFIED

## Core policy: Minecraft is a content ecosystem, NOT one production type

A channel and a video must have coherent *audience promise*, *source truth*, *creative grammar*, and *production technology*. The large Minecraft niche does not authorize putting an unscripted live player session inside an animated story series.

| Subniche | Audience promise | Source / production |
|---|---|---|
| minecraft_story_adventure | Original story/adventure | Authored 3D animation, Blender |
| minecraft_school_comedy | Original school ensemble comedy | Authored 3D animation, Blender |
| minecraft_monster_fantasy | Original monster/fantasy | Authored 3D animation, Blender |
| minecraft_animated_challenge | Original animated challenge | Authored 3D animation, Blender |
| minecraft_recorded_survival | Real player progression | Authorized REAL game-session recording |
| minecraft_gameplay_tutorial | Authentic instructional gaming | Authorized REAL game-session recording |
| minecraft_live_gameplay | Interactive live player | REALTIME authentic game runtime, EXCLUDED from longform-breakout views |
| minecraft_scripted_machinima | Scripted film staged inside game | Actual Minecraft game runtime capture, not Blender fake footage |

The old internal label minecraft_challenge_survival is mapped to *ANIMATED* challenges only, not authentic player survival recording. It is a historic compatibility alias, not a second independent niche.

## Noninterchangeable media and safe knowledge transfer

Generic creative hypotheses such as video hook, title clarity, audience question and viewer retention can be tested across formats, but never accepted as proven without same-audience data. Narrative beats may transfer from scripted machinima to original animation (with independent script review). Source footage, rig libraries, copyright, game-runtime capture, livestream mechanics, and character names/skins are not transferable just because two videos have "Minecraft" in the title.

Cross-series coherence is a testable constraint; story and school animated series are structurally compatible, gameplay guidance and true unscripted livestream are not automatically compatible with that original-fiction promise. Expanding to a different production/viewer family requires separate channel strategy review.

## Default characters: NEW, not automatically recurring

Project-level reuse_series_characters = false by default.
- No flag: NEVER automatically inherit previous episode characters, visual skins or rigs. Planning may reuse a channel's high-level audience promise and user-selected series/world rules, but new actors must get a new episode-specific cast identity, Minecraft rig link, and an externally trusted Ed25519-signed rights-review document before production. The fresh cast file is data/projects/PROJECT_ID/inputs/original_episode_cast.json.
- Brand-only standalone film: supply --channel-brand-id without --series-id and --episode-id. The owner channel's audience/brand promise carries over, but the video receives a NEW standalone episode strategy; no previous cast, world plot or series continuity is inherited. This requires independently created new actor rigs.
- Series film: supply all three brand/series/episode identifiers. Series continuity applies as an editorial constraint, but prior cast/skins/voices still require the explicit --reuse-series-characters opt-in.
- Explicit --reuse-series-characters: reusable characters are loaded from the owner's approved original series, then checked against actual registered CharacterRigRegistry entries, rig identity IDs, style and rights. Still requires full film QC.
- A selected series/episode constrains story logic but is not by itself consent to reuse actor designs. The prompt/gate reminds Script Room to invent original character arcs for videos without opt-in.

## Production routing (actual code)

CompanyOrchestrator writes minecraft_route into CompanyBlueprint. If prompt is uncertain, the planner raises MINECRAFT_MODE_REQUIRES_REVIEW rather than silently assuming animated film. Explicit contradictory subniche + source description is rejected.

Blender original animation keeps the professional story/film DAG. Authenticated game capture, staged in-game machinima, and live player streams enter separate MC_MODE_INTAKE > MC_FORMAT_RESEARCH > MC_GAME_SOURCE_RIGHTS > MC_REAL_CAPTURE > MC_CAPTURE_QC > MC_CAPTURE_PACKAGING > PUBLISHING > ANALYTICS_LEARNING stages. Those nonanimation executable adapters remain BLOCKED until real qualified game footage / livestream infrastructure, original rights, and provider authentication exist. This upgrade does NOT create or fake playable livestreams.

## Research and the best-subniche question

The true best current Minecraft subniche has not been verified in this upgrade. Real selection must validate channel creation (0-30 days), two DISTINCT longform >=8-minute videos each reaching >=1M views within 14 days, established recent audience demand with >=100k-view longform episodes, repeatability, rights, cost/throughput and opportunity for a new English-speaking channel. Real-time livestream views are excluded.

The v207 ranked helper does not accept a user-provided string "independently reviewed" as conclusive proof. Its outputs are PROVISIONAL_RESEARCH_SHORTLIST, not a real externally validated breakout verdict or any asserted RPM/profit. Without actual provider archives, candidates are UNVERIFIED. Previous channel examples Maizen and BigSchool can only teach generic original narrative patterns; JJ & Mikey is a character pair, not a separate niche or reusable asset identity.

The first operationally plausible CineFactory film test is original scripted Minecraft animation / story + school comedy (shared production and potentially coherent audience); that is an EXECUTION-FIRST HYPOTHESIS, not a market ranking or income forecast.

## Example commands on user Windows PC

cd "C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6"

python -m cinefactory.cli minecraft-format-map

python -m cinefactory.cli company-plan --project-id original_mc_story_001 --niche minecraft --minecraft-subniche minecraft_story_adventure --prompt "Original animated Minecraft 3D adventure" --duration 60

python -m cinefactory.cli company-plan --project-id real_minecraft_live_001 --niche minecraft --minecraft-subniche minecraft_live_gameplay --prompt "Minecraft realtime livestream of actual players" --duration 900

python -m cinefactory.cli company-plan --project-id new_film_in_series_001 --niche minecraft --minecraft-subniche minecraft_story_adventure --channel-brand-id ORIGINAL_BRAND --series-id ORIGINAL_SERIES --episode-id ORIGINAL_EPISODE --prompt "Original animated Minecraft adventure" --duration 60

To deliberately reuse the existing original series cast, supply --reuse-series-characters on the last command. Without it, a fresh actor manifest and independently signed rights review are mandatory before rendering.

For locally declared research leads:
python -m cinefactory.cli minecraft-research-candidates --records-file "PATH_TO_REVIEW_CANDIDATES_JSON"

Research filter output is NOT a definitive winners list; it cannot prove API authenticity by itself.

## Limits and acceptance

- No real livestream capture, no user channel uploads, no paid-generation-credits, no fabricated YouTube counts.
- Channel default cast switching and format routes have targeted unit/integration tests; full company regression should be consulted before release.
- Three inherited Blender worker provenance SHA v190/v196 failures are not silently overwritten.
- Need full original film pilot, real character/rights approvals, scene-QC and independent acceptance of an 8-10min feature episode before labeling CineFactory a professional autonomous studio.

VERDICT: ROUTING CONTRACTS AND OPT-IN CHARACTER LOGIC INTEGRATED; MARKET RANKINGS AND GAMECAPTURE EXECUTION NOT INDEPENDENTLY VERIFIED.


## Final engineering verification, 2026-10-10

- Canonical full repository pytest: **1,387 PASS / 3 FAIL**, log .tools/deep_audit_20261010/v207_final_standalone_source_truth.log, 213.37 sec. All three remaining failing tests are inherited historical SHA checks for Blender worker v190/v196, unchanged from the previous v206 acceptance. No new regression failures.
- Focused Minecraft v207 + channel v206 + professional company handoffs: **72/72 PASS**, log .tools/deep_audit_20261010/v207_standalone_final.log.
- Real company-plan CLI probes confirmed FILM_ANIMATION -> PROJECT_INTAKE and recorded gameplay / livestream / machinima -> MC_MODE_INTAKE. GAMEPLAY plans now have format=GAMEPLAY and actual_gameplay_required=True from the source product onwards, with a blocked empty production recipe until a real capture engine is proven.
- Standalone original video can specify channel_brand_id without prior series or episode; it inherits the brand/audience promise only and requires new per-video actors, registered Minecraft rigs, and a trusted independent rights signature. Existing series actor identity requires explicit reuse_series_characters=True.
- Research ranking is only provisional and cannot declare a best-performing Minecraft subniche without genuine independently audited YouTube evidence. No actual live capture engine or YouTube publishing was enabled. This is a development integration milestone, not a production release.
