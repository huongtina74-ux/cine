# E — Minecraft lane scan dataset (YouTube Data API v3, US / English) — 2026-11-04

Targeted sub-niche ("lane") scan to test which Minecraft lanes may be low-risk, sustainable, high-view, open to new channels and higher-RPM.
**This file is a dataset description, not an analysis.** All numbers are OBSERVED (computed from the CSVs listed below) unless labelled otherwise.

- Run: owner's Windows PC (`desktop-hje6a6d`), Blender 5.2 used only as a Python bridge (background `blender -b --factory-startup --python`), no render.
- Script: `C:\Users\ADMIN\Downloads\cine_niche_survey\cf_mc_lane_scan.py` (variant of `cf_mc_api_dataset.py`: same `api()` / quota guard / key handling). Copy: `data/2026-11-04/cf_mc_lane_scan.py`.
- Run window: started 2026-11-04T12:00:37Z, finished 12:05:13Z (OBSERVED `run_meta.json`).
- Official API only (search.list, videos.list, channels.list, playlistItems.list). No scraping, downloads or login. API key read from `.env` inside the PC process only; a post-run byte scan of every output file (CSV, JSON, logs, raw) found the key in **0 files** (OBSERVED).
- Raw JSON (`raw_search.json`, `raw_videos.json`, `raw_channels.json`, `raw_uploads.json`, `raw_resnapshot.json`) kept on the PC only: `C:\Users\ADMIN\Downloads\cine_niche_survey\out\2026-11-04_lane_scan\raw\`.

## Quota

| item | value |
|---|---|
| hard cap for this run | 6,000 units (OWNER); 25 of them reserved for the re-snapshot |
| used by this run | **5,788 units** (OBSERVED; counted per attempt, so it is an upper bound) |
| calls | search 52 (5,200 u) · videos 308 · channels 24 · playlistItems 256 |
| errors / quota stops | 0 / none |
| used earlier today (before this run) | ~13 units (OWNER) → day total ≈ 5,801 + whatever the daily scheduled job uses (not measured) |

## Files (`data/2026-11-04/`)

| file | rows | what |
|---|---|---|
| `lane_videos.csv` | 1,814 | one row per unique search-result video (all lanes, 30d + 15d) |
| `lane_channels.csv` | 1,192 | every channel of a result + all 32 watchlist channels |
| `lane_uploads.csv` | 9,373 | last ≤50 uploads of 256 channels (median 50 per channel) |
| `lane_search_hits.csv` | 2,353 | keyword × rank × video_id (one row per hit) |
| `lane_keywords.txt` | 44 | keyword, lane, type (lane_seed / expanded_from_titles), windows |
| `resnapshot_24h.csv` | 795 | re-snapshot of the 795 ids in `derived_C_snapshot2_growth.csv`, joined to snapshots 1 and 2 |
| `run_meta.json` | — | units, calls, errors, 15d picks, per-lane summary (no key) |
| `progress.log` | — | per-call log (keyword, hit count, running units) |
| `cf_mc_lane_scan.py` | — | exact script that ran |

### Fields

**lane_videos.csv**: video_id, url, title, channel_id, channel_title, published_at, fetched_at, age_days, views, likes, comments, duration_s, **is_short** (0 < duration ≤ 180 s), made_for_kids, category_id, live_broadcast_content, default_language, default_audio_language, **lanes** (pipe list), n_lanes, keywords_30d, keywords_15d, n_keywords, best_search_rank, views_per_day (= views / max(age_days, 1)), channel_subs, channel_subs_hidden, channel_created_at, channel_age_days, channel_country, views_div_subs, channel_median_views, channel_median_basis, channel_median_views_same_format, views_div_channel_median, **views_div_channel_median_same_format**, tags.
Channel-median fields are filled only when that channel's uploads were pulled (481 of 1,814 videos).

**lane_channels.csv**: channel_id, title, custom_url, created_at, age_days, country, subscribers, hidden_subscriber_count, video_count, total_views, made_for_kids, fetched_at, uploads_playlist, lanes, sample_videos, sample_views_sum, sample_max_views, sample_shorts, groups (why uploads were pulled), uploads_fetched, uploads_n, uploads_long, uploads_shorts, median_views_all, median_basis, median_views_long, median_views_shorts, uploads_last_30d, newest_upload, oldest_upload_in_sample, outliers_3x_same_format.

**lane_uploads.csv**: channel_id, channel_title, fetch_groups, upload_position, video fields as above (incl. is_short, made_for_kids, default_audio_language), in_lane_results, views_per_day, channel_median_views, channel_median_views_same_format, views_div_channel_median, views_div_channel_median_same_format, tags.

**lane_search_hits.csv**: keyword, lane, window_days (30 or 15), published_after, fetched_at, rank, video_id, channel_id, title.

**resnapshot_24h.csv**: video_id, title, channel_id/title, published_at, duration_s, fmt, is_en (from the 2026-11-03 file), views_s1/fetched_at_s1, views_s2/fetched_at_s2, found_s3, views_s3, likes_s3, comments_s3, fetched_at_s3, gap_h_s2_s3, d_views_s2_s3, vph_s2_s3, views_per_day_24h_equiv, growth_pct_s2_s3, age_days_s3, vph_lifetime_s3, decel_ratio (= vph_s2_s3 / vph_lifetime_s3; >1 means still accelerating).

### Definitions

- Median basis: median of the channel's pulled uploads with age ≥ 3 d if there are ≥ 3 of them, otherwise all pulled uploads (same rule as the 2026-11-03 dataset). Same-format = Shorts vs long (≤180 s / >180 s).
- Uploads groups (`groups` column): `watchlist` (32, all from `watchlist_2026-11-04.csv`), `lane_leader:<lane>` (top 5 channels per lane by summed result views in that lane → 40 slots, 32 unique channels), `new_le_30d` (47 channels ≤30 d old with a result), `new_le_365d_100k` (176 channels ≤365 d old with a 100K+ result). 256 unique channels; none skipped for budget.
- 15d picks: per lane, the seed query with the highest median views among its 30d results was re-run with publishedAfter = now−15 d (8 queries, listed in `run_meta.json` → `picks_15d`).

## Query design

- 38 lane seed queries (the owner's list, verbatim) + 6 auto-expanded (most frequent title words/bigrams from each lane's top-60 titles, max one per lane; roblox/robux/fortnite/gta stop-listed), all with publishedAfter = 2026-10-05T12:00:37Z (now−30 d); 8 re-runs with publishedAfter = 2026-10-20T12:00:37Z (now−15 d). All: type=video, regionCode=US, relevanceLanguage=en, order=viewCount, maxResults=50, one page.
- Auto-expanded keywords that ran: `minecraft verity` (→ mystery), `minecraft maizen` (→ family), `minecraft mod insane` (→ AI), `minecraft rich poor` (→ but/roleplay), `minecraft mobs` (→ battle), `minecraft choose right` (→ interactive). Two are creator names (Verity, Maizen), so they pull one creator's ecosystem rather than a format, and the lane assigned to them is a heuristic (the lane whose titles used the word most).

## Counts per lane (OBSERVED, seed queries only, 30-day window)

Expanded keywords and 15d re-runs are excluded here so lanes are comparable (each lane has 3–7 seed queries, so raw counts also depend on how many queries the lane had).

| lane | seed q | videos | channels | Shorts | ≥100K | ≥1M | median views | median views/day | channels ≤365 d with a 100K+ video | channels ≤30 d | extra videos from expanded kw |
|---|---|---|---|---|---|---|---|---|---|---|---|
| scripted_survival_movie | 6 | 167 | 138 | 15 | 143 | 38 | 463,714 | 27,969 | 23 | 8 | 0 |
| mystery_horror_gameplay | 5 | 229 | 188 | 122 | 121 | 56 | 130,741 | 9,700 | 18 | 9 | 45 |
| family_emotional_animation | 7 | 285 | 166 | 216 | 218 | 105 | 543,049 | 37,533 | 42 | 6 | 33 |
| interactive_shorts | 4 | 138 | 120 | 109 | 77 | 28 | 151,146 | 17,745 | 23 | 11 | 45 |
| mob_army_battle_sim | 5 | 192 | 128 | 86 | 102 | 27 | 125,705 | 7,621 | 10 | 4 | 45 |
| ai_in_minecraft | 4 | 148 | 124 | 60 | 109 | 44 | 377,111 | 24,244 | 12 | 4 | 43 |
| lore_facts_explainers | 4 | 177 | 124 | 124 | 81 | 17 | 74,890 | 5,128 | 10 | 5 | 0 |
| minecraft_but_roleplay | 3 | 149 | 83 | 75 | 149 | 78 | 1,127,757 | 61,533 | 16 | 1 | 5 |

15-day re-runs (one query per lane, 50 results each): videos ≥1M / of those from channels ≤365 d old — survival 7/0 · mystery 18/1 · family 26/5 · interactive 5/3 · battle 9/1 · AI 10/0 · lore 3/1 · "minecraft but" 50/2 (OBSERVED).

Lane leaders pulled (top 5 by summed result views; subs · channel age · country as returned by the API):
- scripted survival: MrBeast Gaming, ProBoiz 95, Forge Labs, EYstreem, **Nobody Gets In (58.1K subs, 34 d, EG)**
- mystery/horror: ohnepixel raw (off-topic, see caveats), Omenasito, Alex Drawly, TheOlarte, Sean Andrew
- family/emotional: BlobbyClips, MSToons, **Manic Craft (66.1K subs, 40 d)**, FoxiLu (73.6K, 690 d), Monit
- interactive Shorts: MrBeast Gaming, Johnny and Marty, Blitzen, **Henreee (82K subs, 85 d, US)**, Tg Jamal Shorts 44 (315 d)
- mob/army battle: BlobbyClips, Shunkiwii, Joeysaf, MrBeast Gaming, Bayashi TV
- AI in Minecraft: ohnepixel raw (off-topic), Jazzghost, Dream, kehnt (131K, 583 d), Forge Labs
- lore/facts: BlobbyClips, FlameFrags, KeyroNN (43K, 210 d), Fact Casso, Rust
- "Minecraft but"/roleplay: Joeysaf, dayta, Cayce, Spoke, Dream

Whole dataset: 1,814 videos, 1,070 Shorts (59%), made_for_kids=true on 4 videos; 106 videos hit more than one lane; 0 results older than 30 d; channels ≤30 d old: 52, ≤365 d: 361; hidden subscriber counts: 0; channel country: US 386, blank 271, IN 127, BR 36, GB 35 (OBSERVED).

## 24 h re-snapshot (`resnapshot_24h.csv`)

- 795 / 795 ids returned (none removed or private). Snapshot 3 fetched 2026-11-04 ~12:05Z; **gap from snapshot 2 = 16.8 h, not 24 h** (OBSERVED). `views_per_day_24h_equiv` scales the 16.8 h delta to 24 h linearly (INFERRED, assumes a constant rate).
- Median growth s2→s3 = +1.87%; median decel_ratio = 0.213 (current speed ≈ 21% of the lifetime average); 24 videos still faster than their lifetime average (decel_ratio > 1); 6 videos had 0 new views (counter frozen or stalled); 0 negative deltas (OBSERVED).
- Largest 16.8 h gains: XOXU MINECRAFT "Who Will ADOPT JJ Kitten?!" +2.21M (ratio 1.03) · Parrot "10,000 Player Minecraft War" +1.99M (long-form, 0.86) · PumpBrine "Smartest Player VS Dr Donut Part 29" +1.33M (OBSERVED).

## Caveats (read before analysis)

1. **Search ≠ market.** search.list (order=viewCount) returns at most 50 results per query and a non-exhaustive, relevance-filtered set. Lane counts are sample counts, not market sizes. Lanes with 3–4 queries (but/roleplay, AI, interactive, lore) are under-sampled compared with lanes that had 6–7.
2. **Off-topic / non-English leakage.** regionCode/relevanceLanguage only bias results. Share of lane results with a Minecraft term in title/tags: survival 80%, mystery 86%, family 88%, interactive 75%, battle 83%, AI 91%, lore 77%, but/roleplay 91%. `default_audio_language` is en on 787 of 1,814 videos, blank on 652, hi 133, es 57, pt 38. Example: "ohnepixel raw" (a DE non-Minecraft channel) ranks as a leader in two lanes. Filter on `default_audio_language` / title before drawing conclusions.
3. **Generic queries dominate.** "minecraft but", "who will win minecraft", "every mob vs" and "minecraft AI" return the biggest generic Minecraft channels (MrBeast Gaming, Dream, Joeysaf), so a high median there does not mean the lane format is open to new channels. Use the `channels ≤365 d` columns and `views_div_channel_median_same_format`.
4. **Expanded keywords** include two creator names (Verity, Maizen); their hits (~200 videos) are lane-tagged by a heuristic. They are excluded from the per-lane table above but included in `lane_videos.csv` (see `keywords_30d`).
5. **Third-party IP.** Many top results use third-party characters (Maizen JJ & Mikey, Dr Donut, Herobrine fan universes, Death Note). This dataset does not classify IP; per CLAUDE.md we use it only as a benchmark, never as a source.
6. **RPM is not in the API.** Nothing here measures RPM; "higher RPM" must come from category/audience reasoning (INFERRED) or the owner's own analytics (OWNER).
7. **made_for_kids** is the uploader's declared flag (4 true out of 1,814); it does not say who actually watches.
8. Channel medians use only the last ≤50 uploads; for Shorts-heavy channels that can be under 2 weeks of history. `median_basis` gives n.
9. Views are a single point-in-time snapshot (fetched 12:00–12:05Z); age_days and views_per_day use each row's own `fetched_at`.
10. Quota: units counted per attempt (upper bound); the separate daily scheduled job's usage today was not measured.
