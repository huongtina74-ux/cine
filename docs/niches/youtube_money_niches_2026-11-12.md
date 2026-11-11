# Which faceless English niche earns the most AND lets a new channel in (2026-11-12)

Owner scope (2026-11-11 23:5x ICT): whole YouTube, English, **faceless**, produced by CineFactory.
Labels: MEASURED (panel data) · OBSERVED (our API/search) · INFERRED · ESTIMATED · INSUFFICIENT_EVIDENCE.

## Method
- Search (owner browser, logged out): 11 niches x 5 keywords x {this month by views, this month by relevance}, 2026-11-11 ~16:40Z.
- YouTube Data API v3 (`cf_mc_niche_enrich.py`, 379 units, 17:04Z): 1,634 videos, 1,280 channels, uploads for 160 of 469 channels <= 365 d
  (budget cap -> new-channel repeat counts are a floor). Summary: `reports/research/money_niches_2026-11-12/niche_summary.json`.
- Metrics: English (tag/title heuristic, ESTIMATED), >= 8 min, published <= 35 d. Thumbnails of 29 top new-channel videos and
  storyboards of 4 (Nils History, Ziro History, Rewynd3D, Arthur Revives the Past) inspected; no audio.
- RPM: AIR Media-Tech, 300 channels, real Studio data May 2025-May 2026, 3,595 monetized channel-months (MEASURED; niche medians).

## RPM by niche (MEASURED, AIR Media-Tech 2026, median and P25-P75)
Education & Science **$10.22** ($2.31-$19.50) · Transport* $5.69 · Lifestyle $2.98 · News & Politics* $2.60 · Entertainment $2.43 ·
Crafting $2.39 · Gadgets & Tech $2.33 · Music $2.28 · Food* $2.25 · Gaming $2.05 · Business & Finance* $2.01 · Health & Sport $1.23 ·
Kids & Teens $0.33. (*fewer than 10 channels: directional; Business & Finance only 3 channels.)
=> The "finance = $20-30 RPM" claims are AGG-EST; the only measured panel does not confirm them. Education/science-type content is the
one measured high-RPM class.

## New-channel evidence by niche (OBSERVED)
| Niche | Videos | Median | <100K-sub median | New ch (<=365 d) >=100K / >=1M / repeat >=3x100K | Median length | RPM class (MEASURED) |
|---|---|---|---|---|---|---|
| **History documentary (+sleep)** | 139 | 159K | **54K** | **17 / 6 / 5** | 52 m | Education & Science $10.22 (INFERRED mapping) |
| Family drama / revenge stories | 104 | 74K | 66K | 24 / 9 / 5 | 44 m | Entertainment $2.43 |
| **Disaster / air-crash documentary** | 112 | 103K | 12K | **11 / 7 / 3** | 26 m | News $2.60 / Education if historical |
| Tech / AI / engineering explainers | 119 | 255K | 56K | 11 / 1 / 1 | 24 m | Tech $2.33 or Education |
| Geopolitics / geography | 93 | 88K | 14K | 16 / 2 / 5 | 21 m | News $2.60 / Education |
| True crime / mystery doc | 139 | 141K | 35K | 13 / 3 / 2 | 37 m | Entertainment $2.43 |
| Business / company doc | 130 | 138K | 6K | 12 / 4 / 2 | 22 m | Business $2.01* |
| Space / science doc | 125 | 33K | 6K | 7 / 3 / 4 | 62 m | Education $10.22 |
| Psychology / self-improvement | 93 | 72K | 28K | 5 / 0 / 1 | 24 m | Education/Lifestyle |
| Health / body | 83 | 39K | 19K | 11 / 3 / 2 | 20 m | Health $1.23 |
| Personal finance / investing | 90 | 54K | **1K** | 4 / 1 / 0 | 16 m | Business $2.01* |

Format checks (THUMBNAIL/STORYBOARD): family-drama winners are mostly **AI-generated drama films** (billionaire/mafia/romance
key art) -> high inauthentic-content risk; true-crime winners lean on **police bodycam footage** (reuse, graphic); Nils History is
**presenter on camera** (not faceless); Ziro History (38 d, 10 long >= 100K) = faceless **2D cartoon/stick + maps + archival art**;
Arthur Revives the Past (295 d, 17 long >= 100K) = narrated **AI-photoreal historical scenes**; Rewynd3D (23 d, 2.58M) and Fault Lines
(17 d, 1.93M) = **simple 3D recreations** of a recent jet crash; TALEYE (28 d, 4.45M) and reci share the same 3D plane key art.
One non-English channel (AniMoney, Hindi) slipped through the filter.

## Decision (INFERRED, owner approves)
1. **Faceless history documentaries, 30-60 min** (incl. historical disasters, "how people lived", sleep cuts). Highest measured RPM class,
   most repeatable new-channel evidence (17/6/5; small-channel median 54K), evergreen, long watch time, older US audience; matches
   Afanta's history-for-sleep scripting/TTS. Visual style: CineFactory-made 2D illustration/maps/archival public-domain material/3D
   scenes - not AI-slide slideshows.
2. **3D recreation documentaries of historical disasters and engineering failures** (Blender), 15-30 min. Strongest >= 1M evidence for very
   young channels (7 new channels >= 1M, several < 35 d), and our 3D pipeline fits. Lower/uncertain RPM; stay with historical cases
   (no recent tragedies: sensitive-event ad limits, respect for victims).
Rejected: personal finance (new channels: 1K small-channel median, 0 repeat; YMYL; measured RPM not high), AI drama films (policy),
true crime bodycam (reuse/graphic), health (YMYL, $1.23), business docs (6K small median), psychology, space (small median 6K),
geopolitics (fold into #1).

## Risks
- RPM mapping niche -> AIR class is INFERRED; AIR P25-P75 for Education is $2.31-$19.50 (wide). Our own RPM is UNKNOWN until monetized.
- YPP for new applicants rises to 8,000 watch hours from 2027-02-01 (earlier research) - long videos help.
- Inauthentic content (YPP clarification 2026-07-16): template/AI-slideshow channels can lose monetization channel-wide -> original
  research, real visuals, varied structure; disclose realistic synthetic scenes where YouTube requires (ESTIMATED; rule not re-read today).
- Single reading; search-ranked sample; uploads fetched for only 160/469 young channels.
