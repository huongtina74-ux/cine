# CineFactory — Minecraft approved niche research actual activation (2026-10-11)

## Production control status
- User approved both Minecraft Gameplay and Minecraft Animation for **research** (no video publication or paid API).
- Remote desktop: DESKTOP-HJE6A6D. Both `research_niche_approvals` rows are APPROVED in the existing SQLite database.
- Live activation initially hit a **legacy DB schema** PRIMARY KEY(niche_id), incompatible with the current composite PK (niche_id,format_id). Pre-migration consistent SQLite backup made at `.tools/backup_before_niche_approval_v255.sqlite3` (integrity_check ok); code added transactional idempotent migration preserving rows.
- Approval next hit old `per_query<=6` guard while activation requested 20. Allowed ceiling aligned to 20 and covered in tests.
- Crucial quota bug: initial actual scan gave 28 admitted Minecraft Animation and ZERO Gameplay because 48 slots filled in candidate insertion order. **Fixed deterministic round-robin per approved format**. Retried real public scan 2026-10-11: 48 metadata checks, **19 animation admitted + 20 gameplay admitted**, 8 quarantined, 0 errors.
- Two branch owner reports and two approved department handoff packets were created in `data/research/youtube_breakout/`. The daily task already calls `--scan-approved`; future normal runs use these newly approved formats.

## Scoping and evidence discipline
- Independent wide YouTube discovery earlier on 2026-10-11 yielded 575 candidates, 546 usable metadata records. Initial samples covered multiple games, geographies and English-title formats. It was NOT exhaustive YouTube.
- Supplementary v256 merge joins approved-keyword public DB observations with the historical wide public scan, deduping by exact video ID; normalizes title-format signals and isolates ambiguous/cross-niche results.
- At the end of this run: **46 Minecraft Animation matching long-form video candidates**, **20 animation channel candidates**, 27 of the clips posted within 30 days; **44 Minecraft Gameplay video candidates**, **32 gameplay channel candidates**, 32 posted within 30 days, within the available <=90-day metadata scope.
- "Channel candidate" != verified same-format competitor. "Source video views" != recent VPH. Current view counts from changing YouTube metadata are snapshots and may increase.
- Newly created channel <=30 days with 2x 8+min 1M views in <=14 days: **NOT YET VERIFIED**. MSToons channel created 2017-11-18 according to https://socialblade.com/youtube/handle/mstoonss ; Takuto has videos from July, so not a new Oct 2026 channel.

## Cohort A — competitor baseline
### Minecraft Animation
- MSToons, UCc2RL8jvY1rJPuCnJVsIQWw: 16 format-related sampled videos; 11 already had >=1M view snapshots in this bounded 90-day+approved-keyword sample. Historical channel established, so proof of current demand, **not new channel proof**.
- Takuto, UCjexTPeQMiM7v3vqjnU0MmQ: 6 candidate clips, 4 >=1M views.
- GameToons +, GameToons Movies, GameToons, Cubeee Animation, BLOCKSHEEP, Kamui Animation: additional candidate checks; titles alone do not establish identical style or software.
### Minecraft Gameplay
- Maizen, UCJHBJ7F-nAIlMGolm0Hu4vg: 7 recent candidate clips, 5 >=1M snapshots (one source-video Pokemon title required separately documented browser visual evidence).
- Mozi (Hardcore 100 days), Cryptozoology (100-days themed), Unbounded Builds, EYstreem, aCookieGod, LuckyRNG, WelcominTV and others are distinct channel cohorts. Do NOT automatically group them with Maizen's JJ/Mikey narrative gameplay sub-format.
- Prefer narrower subformats: A) 100 days + changing rules, B) one-block world, C) noob/pro build vs survival; test demand and production cost **separately**.

## Cohort C — verified <=14 day age at measured >=1M views (as of Oct 11)
### Minecraft Animation (3)
- [MSToons JJ VERITY vs Mikey CURIOSITY](https://www.youtube.com/watch?v=W7R8k10Kjfk), Oct 03, 14:13; 1,966,301 observed in a later refresh.
- [MSToons JJ's Girl EAT JJ CAKE](https://www.youtube.com/watch?v=qtWfSIqNfdU), Oct 05, 10:13; 1,846,909 observed in a later refresh.
- [MSToons JJ Enderman SAD ORIGIN Story](https://www.youtube.com/watch?v=69xvH7z9sE4), Oct 07, 10:34; 1,282,477 observed in a later refresh.
### Minecraft Gameplay (2)
- [Maizen 100 Days in an EXPANDING WORLD](https://www.youtube.com/watch?v=t5wy_OsuMvM), Oct 05, 41:31; 1,860,940 observed in prior wide scan.
- [Maizen 100 Days on ONE BLOCK of POKEMON](https://www.youtube.com/watch?v=yuM6o-8gz_4), Oct 03, 19:17; 1,580,555 prior wide scan. Source browser video played 31/31 segments in a separate prior study, but semantic soundtrack independent QC still pending. Pokémon franchise ownership risk must be separately reviewed.

## Creative/technical research priorities (hypotheses pending full AV)
- Animation: recurring monsters / transformed characters / visual drama and high-concept emotional hooks. Prioritize verified full-source reviews of recent MSToons W7R8k10Kjfk, qtWfSIqNfdU, 69xvH7z9sE4, and compare Takuto BARbfz8ik8k.
- Gameplay: 100-day rule/visible HUD, day milestones, asset/team upgrades, and prepared boss payoff (supported by original Maizen Pokémon source screenshots and full English captions on previous study).
- MSToons company describes an end-to-end studio with proprietary production management and specific roles: https://mstoons.com/ . Their recruiting reference mentions Mine-imator/Modelbench as workflow tools; cannot infer exact rendering software of every uploaded video from these references alone.
- Originality gate: do not simply clone JJ & Mikey, skin designs, copyrighted Pokémon/Spider-Man/third-party audio. Propose original IP while studying format.

## Source movie review queue and constraints
- Original-browser moving player + audio acquisition targeted for W7R8k10Kjfk at `.tools/mstoons_breakout_source_v257/` (private/gitignored). Completion must be checked against actual per-segment audit; do not assert watched in full before it says all segments COMPLETE/no gaps.
- Unreviewed 20 video queue in catalogue JSON: per-scene goals, plot continuity, camera, acting, lip sync, props, VFX, music, SFX, editing, asset creation method, original-IP viability and production cost measurement are still pending full source AV.
- Review evidence must be separated from viewer metadata; no source download or third-party asset reuse in produced episodes.
- The user approved *research* of two formats; did not approve a final money spend, video rendering, channel publishing, or commercialization of competitor IP.

## Paths
- `data/research/youtube_breakout/approved_deep_research/minecraft_approved_catalogue_v256_20261011.json`: scoped ranked channel/video data, source-view metadata, breakout cohort and AV priority queues.
- `data/research/youtube_breakout/two_track_reports/`: branch owner reports, daily scheduler snapshots.
- `docs/MINECRAFT_BREAKOUT_CORRECTED_V253_20261011.md`: wide-scan historical evidence and error correction.
