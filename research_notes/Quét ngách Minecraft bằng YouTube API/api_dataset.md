# Minecraft YouTube landscape (US, English): raw YouTube Data API v3 dataset, 2026-11-03 UTC

Run: 2026-11-03T19:00:10Z to 19:05:28Z UTC (2026-11-04 02:00 Asia/Saigon), on the owner's Windows PC (Blender 5.2.3 Python 3.13, stdlib urllib), official API only, read-only. The script is `data/cf_mc_api_dataset.py`. The PC copy is `C:\Users\ADMIN\Downloads\cine_niche_survey\cf_mc_api_dataset.py` and its PC output is `...\cine_niche_survey\out\2026-11-03_api_dataset\`. The API key was read inside the process only. A post-run scan found the key in none of the output files or the stdout log.
Labels follow CLAUDE.md: **OBSERVED** means counted from the files in `data/`. **INFERRED** means my reasoning. **OWNER** means the brief said so.

## What the dataset contains: files, fields, counts, quota

### Takeaway
The run made 84 search.list calls: 66 keywords over the last 7 days plus 18 core keywords over the last 15 days. It used 9,111 quota units against a 9,300 cap. It produced 2,827 unique videos, 1,958 channels, and the last ≤50 uploads (11,408 rows) for 308 channels. There were no API errors and no quota stop (OBSERVED, [run_meta.json](data/run_meta.json)).

### Cited Findings
- **Quota (OBSERVED, [run_meta.json](data/run_meta.json)).** Units used were 9,111: search 84×100 = 8,400, videos.list 363, channels.list 40, playlistItems.list 308. Each attempt was counted. `errors: []`, `quota_stop: null`, `groups_skipped_for_budget: []`. The OWNER said ~1 unit was used earlier today, so the total for the Pacific-time quota day is ≈9,112 (INFERRED: 19:00 UTC = 11:00 PST, so this is the same quota day). That leaves ≈888 units. search.list costs 100 units and list calls cost 1 unit each ([Google quota cost table](https://developers.google.com/youtube/v3/determine_quota_cost?authuser=1)).
- **Search parameters (OBSERVED, [raw_search.json](data/raw_search.json)).** type=video, regionCode=US, relevanceLanguage=en, order=viewCount, maxResults=50, one page per query. publishedAfter = 2026-10-27T19:00:10Z (7 d) or 2026-10-19T19:00:10Z (15 d).
- **Keywords (OBSERVED, [keywords.txt](data/keywords.txt)).** 66 keywords: 25 short seeds, 31 long-tail seeds, and 10 expanded from the most frequent word pairs in the top 300 titles of the seed results.
  - Expanded keywords: `minecraft maizen animation`, `smartest player`, `player donut`, `donut deathnote`, `deathnote skit`, `skit funny`, `mikey`, `verity`, `noob pro`, `animation trending`.
  - These 18 also ran over 15 days: minecraft, animation, horror, 100 days, shorts, movie, challenge, but, smp, manhunt, roleplay, noob vs pro, poor vs rich animation, found footage, mod, survival, build, lore explained.
- **Files in `data/` (OBSERVED):**

| File | Rows / size | What it is |
| --- | --- | --- |
| `videos.csv` | 2,827 rows, 35 cols | every unique video returned by any search, with derived fields |
| `channels.csv` | 1,958 rows, 30 cols | every channel owning a search result, plus upload-sample stats when fetched |
| `uploads.csv` | 11,408 rows, 24 cols | last ≤50 uploads of 308 selected channels (playlist order) |
| `search_hits.csv` | 3,903 rows | one row per (keyword, window, rank, video): the keyword→video join |
| `keywords.txt` | 66 lines | final keyword list, type (seed_short / seed_longtail / expanded_from_titles), windows |
| `raw_search.json` | 2.0 MB | search.list items per "keyword\|days", with fetched_at and totalResults |
| `raw_videos.json` | 4.4 MB | full videos.list items (snippet, statistics, contentDetails, status) for search videos |
| `raw_channels.json` | 1.7 MB | full channels.list items (snippet, statistics, contentDetails, status) |
| `raw_uploads.json` | 14.2 MB | per-channel playlist order + groups + videos.list items for upload videos |
| `run_meta.json`, `progress.log` | small | quota, call counts, errors, timeline |
| `cf_mc_api_dataset.py` | 26.5 KB | the exact collector that ran (sha256 prefix acc34fb3e312409e) |

  In raw JSON, descriptions are trimmed to 1,000 characters, and thumbnails and localized fields are dropped.
- **`videos.csv` fields (OBSERVED).**
  - Identity: video_id, url, title, channel_id, channel_title.
  - Time: published_at, fetched_at (UTC per batch), age_days = (fetched_at − published_at) in days.
  - Stats: views, likes (blank = hidden), comments (blank = disabled).
  - Format: duration_s, is_short_candidate (0 < duration ≤ 180 s).
  - Status and metadata: made_for_kids, category_id, live_broadcast_content, default_language, default_audio_language, tags (`|`-joined).
  - Search join: keywords_7d, keywords_15d, n_keywords, best_search_rank.
  - Channel join: channel_subs, channel_subs_hidden, channel_created_at, channel_age_days, channel_country.
  - Derived: views_per_day = views / max(age_days, 1); views_div_subs.
  - Channel median: channel_median_views, channel_median_basis, channel_median_views_same_format, views_div_channel_median, views_div_channel_median_same_format.
- **`channels.csv` fields (OBSERVED).**
  - Profile: channel_id, title, custom_url, created_at, age_days, country, subscribers, hidden_subscriber_count, video_count, total_views, made_for_kids, fetched_at, uploads_playlist.
  - Search sample: sample_videos, sample_views_sum, sample_max_views, sample_shorts.
  - Groups: groups (leader_top30 / new_le_365d_100k / new_le_30d), uploads_fetched.
  - Upload sample: uploads_n, uploads_long, uploads_shorts, median_views_all, median_basis, median_views_long, median_views_shorts, uploads_last_30d, newest_upload, oldest_upload_in_sample, outliers_3x_same_format.
- **`uploads.csv` fields (OBSERVED).** channel_id, channel_title, fetch_groups, upload_position, the same per-video fields as videos.csv, plus channel medians and views ÷ median (all formats and same format).
- **Median rule (OBSERVED, in the script).** The median uses uploads aged ≥3 days when there are ≥3 of them. Otherwise it uses all fetched uploads. `median_basis` records which rule applied: 293 channels used "age>=3d" and 15 used "all". The video's own views are included in its channel median.
- **Upload groups (OBSERVED, [channels.csv](data/channels.csv)).** 308 channels in total.
  - 30 leaders: top 30 channels by summed views of their search-result videos.
  - 223 channels created ≤365 days ago with a result of ≥100K views.
  - 77 channels created ≤30 days ago (all of them, any views).
  - 134 of the 308 had fewer than 50 uploads, so the sample is their whole channel.

### Inferences
- The budget covered everything requested. Remaining room was too small for more searches, so the 15-day subset is 18 keywords, not ~20.

### Gaps
- The Google Cloud console quota page was not checked. The unit count comes from the script's own counter.

## (A) What is popular for Minecraft keywords in the last 1–7 (and 15) days

### Takeaway
The broad head terms are dominated by Shorts. Every one of the top 50 7-day results for "minecraft" has ≥1M views, and 78% of them are ≤3 min. Long-tail story and horror formats get much smaller numbers in 7 days. "minecraft found footage" has a 7-day median of 367 views, and "minecraft analog horror" a median of 32K (OBSERVED, [search_hits.csv](data/search_hits.csv) joined to [videos.csv](data/videos.csv)).

### Cited Findings
- **Per-keyword result medians (OBSERVED; window, median views of returned results, count ≥1M, share ≤3 min):**
  - **15 d:** `minecraft` 6.33M, 50/50 ≥1M, 68% Shorts. `minecraft animation` 3.28M, 94%. `minecraft movie` 2.00M, 30%. `minecraft horror` 1.47M, 32%. `minecraft 100 days` 618K, 12%. `minecraft smp` 933K, 28%. `minecraft manhunt` 90K. `minecraft roleplay` 50K, 0 ≥1M. `minecraft poor vs rich animation` 32K. `minecraft found footage` 1.7K. `minecraft lore explained` 1.3K (27 results only).
  - **7 d:** `minecraft` 3.50M, 78% Shorts. `minecraft update` 2.71M, 96%. `minecraft shorts` 2.25M. `minecraft funny` 2.16M. `minecraft animation` 2.08M. `minecraft mod` 1.34M. `minecraft challenge` 1.33M. `minecraft but` 1.23M. `minecraft maizen animation` 1.16M. `minecraft verity` 871K. `minecraft horror` 209K. `minecraft hardcore` 168K. `minecraft 100 days` 164K, 8% Shorts. `minecraft monster school` 56K. `minecraft analog horror` 32K. `minecraft arg` 15K. `minecraft creepypasta` 15K. `minecraft found footage` 367. `minecraft villager life` 424. `minecraft parody song` 107.
  - All 84 rows are in a per-keyword recompute from `search_hits.csv`. INFERRED: the low medians for long-tail queries partly reflect irrelevant or low-view filler results in the 50, not only weak demand.
- **Top 7-day videos (OBSERVED, [videos.csv](data/videos.csv)).**
  - "This feels like a scene from interstellar", lowkiMC, Short: 18.9M.
  - "Smartest Player VS Dr Donut #deathnote #skit", PumpBrine, created 2025-08-11: 12.5M.
  - "Minecraft Mods Then vs Now!", BlobbyClips: 11.5M.
  - "No One Helped Evil JJ…", Cheesy Animation: 10.2M.
  - The top long-form video is "10,000 Player Minecraft War: Nether VS Overworld", Parrot, 4.45M subs: 7.2M at 2.1 days.
- **Top long-form videos in 15 days (OBSERVED).**
  - Spoke, "10,000 Players Simulate COLD WAR in Minecraft", 4 h: 13.4M.
  - Dream, "Speedrunner VS 6 Hunters FINALE": 13.1M.
  - Stay Wild, "Surviving HOT vs COLD For 24 Hours!": 12.7M.
  - Also in the list: Omenasito and Verity 7.7M, Maizen "SURVIVING in BUS During ZOMBIE APOCALYPSE" 4.9M, ProBoiz 95 "Testing Trending Minecraft Scary Myths" 6.3M.
- **Format split (OBSERVED).** 1,952 of 2,827 videos are ≤180 s. Of the 590 videos with ≥1M views, 502 are ≤180 s and 88 are long-form.

### Inferences
- The "minecraft"/"animation"/"funny"/"update" results are a Shorts market of millions of views per video. Long-form breakouts in 15 days come mostly from established channels with millions of subscribers: player simulations or wars, manhunts, challenges, and Maizen-style roleplay (INFERRED from the lists above).

### Gaps
- Genre labels were not assigned in this dataset. Use titles/tags, or the `classify()` rules in the PC's `cf_youtube_niche_survey.py`.

## (B) New channels (created 0–30 days and 0–12 months ago)

### Takeaway
564 of 1,958 sampled channels were created in the last 365 days, and 77 in the last 30 days. Only 15 channels aged ≤30 days have a video with ≥100K views. Those breakouts are almost all Shorts (OBSERVED, [channels.csv](data/channels.csv), [videos.csv](data/videos.csv)).

### Cited Findings
- **Counts (OBSERVED).** 779 of 2,827 videos belong to channels ≤365 days old. 223 of those channels have a ≥100K result. 129 of the 590 videos with ≥1M views (from 87 channels) come from channels ≤365 days old. Only 4 videos with ≥1M views come from channels ≤30 days old.
- **Best channels ≤30 days old (OBSERVED; channel, age in days, subs, top result):**
  - Erzxck (21.8 d, 17.3K): "Minecraft Verity Match The Block Game", Short, 12.07M.
  - CHIRAG FACTO (11.3 d, 26K): "Slither Run with Steve - Funny Animation", Short, 2.62M.
  - Mochi & Pals (19.7 d, 1,060 subs): "Who can dig down the fastest?", 1.42M, 1,344× subs.
  - Verity Verifies MC (9.0 d, 1,790): 1.35M Short.
  - parsamehrj (30.0 d): 828K.
  - The first long-form entry is Banazen Craft (9.5 d, US, 4,290 subs): "JJ and Mikey Grow SECRET VERITY from Seeds in Minecraft!", 394K.
- **Long-form breakouts from channels ≤365 days old (OBSERVED).** 30 videos with ≥100K views from 27 channels. Examples:
  - Clooless Gaming (348 d): "Beating Minecraft With The Phobia Mod", 1.21M.
  - SirCloaked (346 d): "Something On My Farm Wants Me Dead...", 956K.
  - Kit vs The End (37 d, 9,730 subs): "Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship", 673K, 34× its channel median.
  - Day Zero (29 d): "I Survived 100 Days in a DEADLY OUTBREAK", 370K.
- **Country field (OBSERVED).** US 527, blank 504, IN 290, ID 55, GB 54, BR 52.

### Inferences
- Channel creation date ≠ the first Minecraft upload. Old channels that were renamed or repurposed count as old, and new "Clips" or second channels of established creators count as new (INFERRED; e.g. "Sleepy Mikey! - Minecraft", created 2026-05-29, appears among the leaders).

### Gaps
- Owner identity, network or second-channel status is not in the API. That needs a manual check.

## (C) 1M+ videos in 0–15 days, views ÷ subs, and upload histories for outlier work

### Takeaway
590 videos published 0–15 days ago have ≥1M views: 342 aged ≤7 days and 248 aged 7–15 days. They come from 355 channels. 428 videos have ≥100K views and views ÷ subs ≥10. Per-channel baselines exist for the 308 upload-sampled channels, which cover 618 of the search videos (OBSERVED).

### Cited Findings
- **Highest views ÷ subs among ≥1M videos (OBSERVED).**
  - Mochi & Pals, 1.42M on 1,060 subs (1,344×).
  - MrMangoHands, "Dream Cheated Every World Record", 3.34M long-form on 2,520 subs (≈1,325×).
  - Beazle, 10.7M Short on 8,360 subs (1,279×).
  - Gamity (49 d old), 1.73M (1,108×).
- **Upload sample (OBSERVED, [uploads.csv](data/uploads.csv)).** 11,408 uploads: 9,876 ≤180 s and 1,532 long. Oldest upload 2023-06-15. 7,101 are ≤30 days old. 71 long-form uploads have ≥5× their channel's same-format median (where the median ≥1,000). Examples: "JJ AND MILKY ANIMATION STORYS" (82×) and "xbowed – I Fought The Best Larptubers" (60×).
- **Leaders (OBSERVED, top by sample views).** BlobbyClips 73.4M, PumpBrine 48.9M, Stonecraft Studios 45.2M, Joeysaf 38.0M, MSToons Shorts 32.8M, elElias 29.9M, Dannika 28.2M, Omenasito 27.9M. All columns are in channels.csv.

### Inferences
- For Shorts-heavy channels, the last 50 uploads can span only days. That makes `median_views_long` thin or blank: many leaders have no long-form upload in the sample (INFERRED from blank median_views_long).

### Gaps
- No retention, CTR or revenue data: the public API does not expose them.

## Data-quality caveats

### Takeaway
Treat this as one ranked snapshot, not a census. Language, region, subscriber and Shorts fields all carry known noise (OBSERVED and INFERRED below).

### Cited Findings
- **search.list is not exhaustive.** It returns one page of ≤50 results per query, ranked by YouTube. 11 of the 84 query runs returned fewer than 50. Examples: "but i can shapeshift" 6, "1000 players simulate civilization" 7, "family roleplay" 12, "lore explained" 13 (7 d) and 27 (15 d), "poor vs rich animation" 31 (7 d). The others were parody song 34, donut deathnote 36, villager life 42, survival movie full 47 and scary seed 48. 2,373 of 2,827 videos were found by only one keyword (OBSERVED, [search_hits.csv](data/search_hits.csv)).
- **The 7–15 day band is biased.** Videos aged 7–15 days come only from the 18 core 15-day queries, so the 7–15 day band is under-sampled compared with 0–7 days (OBSERVED: age > 7 d in 456 rows, all from 15-day queries).
- **relevanceLanguage=en/regionCode=US do not filter strictly (OBSERVED).** default_audio_language: en* 1,037, blank 1,009, hi 205, es 66, pt-BR 49, id 46, tr 44. Spanish and Portuguese titles appear (e.g. elElias, Jazzghost, Rubius Z). Filter on audio language, title language or channel country before "US English" conclusions.
- **Views are a snapshot (OBSERVED).** Fetched 2026-11-03 19:00:33–19:05:27Z. Young videos are still climbing, and views_per_day uses max(age, 1 day).
- **Subscriber counts are rounded.** Public subscriber counts are rounded to 3 significant figures ([RivalIQ help](https://help.rivaliq.com/en/articles/9788197-why-youtube-subscriber-counts-are-rounded)). views_div_subs on tiny channels is coarse. No channel had a hidden count (OBSERVED).
- **Shorts flag.** It is duration ≤180 s, because Shorts can be up to 3 minutes since October 2024 ([Tubefilter](https://www.tubefilter.com/2024/10/03/youtube-shorts-three-minutes-max-length-redesign-trends-templates/)). The API has no Shorts flag, so a ≤3 min long-form upload is misclassified as a Short (INFERRED).
- **made_for_kids is True for only 3 videos (OBSERVED).** Do not treat this as an audience measure. It is the uploader's declaration.
- **Missing values (OBSERVED).** 278 videos hide likes, 9 have comments off, 1 is an upcoming live with no duration, and 1,155 have no tags.
- **Expanded keywords.** They are mechanical title n-grams and include very specific ones ("donut deathnote", "player donut") that echo one viral Short series (INFERRED).

### Inferences
- When comparing niches, use the niche median and per-channel same-format ratios, not the top video. This matches CLAUDE.md research policy (OWNER).

### Gaps
- The [search.list documentation page](https://developers.google.com/youtube/v3/docs/search/list) could not be fetched in this session (the permission request timed out), so its exact wording on relevanceLanguage and totalResults was not quoted. The relevanceLanguage leakage above is OBSERVED from our own data.
