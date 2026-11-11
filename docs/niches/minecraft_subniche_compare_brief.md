# Minecraft sub-niche comparison for a NEW English long-form channel (2026-11-11)

Method (OBSERVED 2026-11-11 15:31Z): 49 YouTube searches (7 niches x 7 keywords x {this month by views, this month by relevance}),
read in the owner's built-in browser (logged out, VN IP). 954 unique videos, then official YouTube Data API v3
(`Downloads\cine_niche_survey\cf_mc_niche_enrich.py`, 319 units): exact views, duration, publish date, made-for-kids,
705 channels (subs, created date), uploads of 142 channels <= 365 days old. Long-form = >= 4 min, published <= 35 days,
English. Per-niche CSVs + `tools/cf_research_stats.py` output: `reports/research/niche_compare_2026-11-11/`.
Caveats: search ranking samples the top of each query (not a census); keywords overlap (one video can sit in 2 niches);
RPM not measured (no channel analytics); views are a single reading.

| Niche | Long videos | Median views | P75 | Median views/day | Median length | Small-channel hits (<100K subs, >=100K) | New-channel hits (<=365 d, >=100K) |
|---|---|---|---|---|---|---|---|
| A Realistic apocalypse / cinematic survival | 97 | 301K | 646K | 17.2K | 53 m | 22 (19 ch) | **18 (14 ch)** |
| B Mystery / ARG | 107 | **27K** | 489K | 3.4K | 21 m | 14 | 10 (10 ch, mixed: horror/IP) |
| C Engineering / redstone | 112 | 269K | 630K | 13.6K | 20 m | 15 | **3** |
| D Horror mod challenges | 128 | **416K** | **1.50M** | 28.5K | 34 m | 11 (7 ch) | 12 (7 ch) |
| E Lore / history | 124 | 51K | 425K | 4.1K | 18 m | 28 | 7 (mostly drama/other) |
| F Kids animation (JJ&Mikey style) | 96 | **1.06M** | 2.91M | 70.3K | 21 m | 14 | 8 (4 ch, all Maizen/Verity IP) |
| G 100 days builds | 105 | 277K | 1.23M | 20.3K | 91 m | 13 | 10 (10 ch) |

## New channels that broke in (examples, OBSERVED)
- A: Nobody Gets In (41 d, 66K subs, median long 174K, 2D stick-figure "Zombie Outbreak: 30 Days..."), Beanie Survives,
  DoodleSurvivals (28 d, 1.28M), StickFallout, Stick Through Collapse (32 d, 468K), Kit vs The End (45 d, 1.0M),
  Day Zero (37 d, median 1.25M), Tomatikk (280 d, 383K), BlakeCraft (198 d, 4.8K subs, 325K), Clooless Gaming.
- B: BionicTV (266 d, 154K subs, median long 360K, "Investigating Minecraft's Deleted Secrets"), ItzHydra (161 d, 4.7K subs, 132K).
- D: imKaiL00L (212 d, 249K subs, median 519K), Clooless (Phobia mod 1.5M), Smellzzy+ (161 d, 407K), Sage (352 d, 351K).
- C: only 3 (commonLuke physics, ScardJester, Automa/IP). F: Ligabka, Maizen Squad, Zentry, my MONSTER SCHOOL - all third-party IP.

## INFERRED verdict
1. A (+G, same lane) is the right #1: most new-channel breakouts (14 channels in 35 days), 50+ min episodes, not MFK.
   Many winners are SCRIPTED stories (2D stick figures, Day-N structure), so real 100-day gameplay is not required
   if the title is honest ("Zombie Outbreak: 30 Days..." rather than "I Survived").
2. B Mystery/ARG is NOT a good #2: lowest median (27K, 1/11 of A); a few winners (BionicTV) prove it is possible but rare.
3. Best #2 by data is D Horror mod challenges (highest non-IP median 416K, P75 1.5M) - but its new winners are
   personality gameplay channels (facecam/commentary, real mods), the format least compatible with our scripted pipeline.
4. C Engineering has good demand but is closed to new channels (3 hits). E Lore is low. F Kids animation is huge
   but new entrants win only with Maizen/Verity IP -> excluded by our original-IP rule.
