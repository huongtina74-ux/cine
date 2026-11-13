# Data standards and statistics for YouTube niche research from scraped/exported metadata (Tube Atlas, YouTube Data API v3), as of 13 Nov 2026

Scope note. These notes cover sampling, metrics and formulas, benchmarks, verification and snapshot practice for public metadata. Labels follow the studio rule: OBSERVED means a cited source states it. INFERRED means my reasoning from cited facts. OWNER means it came from the brief and I could not verify it publicly.

**Read this first: two definition breaks make older numbers non-comparable.**
1. **Shorts views since 31 Mar 2025.** A Shorts view counts every start or replay, with no minimum watch time. The old definition survives as "engaged views" ([YouTube Analytics API revision history](https://developers.google.com/youtube/analytics/revision_history)).
2. **All formats since 24 Aug 2026.** Long-form, Live and Shorts views count "the moment a video starts to play", including autoplay and hover ([YouTube Help: How engagement metrics are counted](https://support.google.com/youtube/answer/2991785); [YouTube Blog, 19 Aug 2026](https://blog.youtube/inside-youtube/engaged-views-youtube-explained)). The Data API `viewCount` on channels changed the same way: "includes autoplay, hold the pointer over, and click/tap to play" ([channels resource](https://developers.google.com/youtube/v3/docs/channels)).

Any view count, views/day or engagement rate collected before 24 Aug 2026 is not like-for-like with one collected after it.

---

## Sampling: how many videos and channels, search-ordering bias, survivorship, including failing channels, mixing languages and countries

### Takeaway
Keyword search (YouTube UI, Tube Atlas, or API `search.list`) is a popularity-weighted, non-random sample. It is capped at about 500 results per query and leans toward recent, shorter, more popular videos. A median taken from it describes "videos YouTube chooses to surface", not "a typical upload in the niche".
- The real typical YouTube video has about 35–41 views.
- Make benchmarks trustworthy by:
  - computing channel-level medians first, then the median across channels;
  - using at least 10, preferably 20, comparable videos per channel;
  - separating Shorts from long-form, and fixing video age;
  - adding a deliberately recency-sliced sample (for example "published in last 48h", sorted by date) to see active channels that are failing.

### Cited Findings
**How search sampling works and why it is biased**
- `search.list` returns at most 500 results per query (50 per page × 10 pages), so YouTube must sample. Researchers split time with `publishedAfter`/`publishedBefore` to get around the cap — [Efstratiou, "On YouTube Search API Use in Research", IMC 2025](https://arxiv.org/html/2506.04422v2)
- Identical queries run over 12 weeks returned "highly variable results". The API "seems to randomize returned videos based on the relative popularity of the respective topic during the query period", which makes representative historical samples "nearly impossible". It "may prioritize shorter, more popular videos" and can return zero videos when topical density is low — [arXiv 2506.04422 abstract](https://arxiv.org/abs/2506.04422); [ACM DL](https://dl.acm.org/doi/10.1145/3730567.3764492)
- Time-sliced querying shows "a strong recency bias, with a much higher volume of videos for dates closer to the query date than for historical dates" (citing Rieder et al., 2025) — [Efstratiou v2](https://arxiv.org/html/2506.04422v2)
- Empty or general queries do not approximate random sampling. "We could only collect 597 videos with the query 'cats' and 251 videos with an empty query." Seed-by-popular-channel methods miss viral Shorts from small channels — [Shorts vs Regular Videos, ACM WebSci 2024](https://dl.acm.org/doi/fullHtml/10.1145/3614419.3644023)
- Keyword results may be limited to videos "that have been vetted or exceed a certain threshold of popularity". The TubeStats authors recommend random prefix sampling (validated against true random-ID "dialing") for representative samples — [TubeStats/TokStats, Media and Communication, Jun 2026](https://www.cogitatiopress.com/mediaandcommunication/article/viewFile/12085/5149)

**What a truly random sample looks like (the survivorship baseline)**
- Random sample of 10,016 videos (late 2022):
  - mean 5,868 views, median 35 views;
  - 4.88% had zero views;
  - only 3.67% had ≥10,000 views, yet they held 93.61% of all views;
  - 72.64% had no comments.

  — [McGrady et al., "Dialing for Videos", JQD:DM 2023](https://journalqd.org/article/download/4066/3766/13646)
- Distribution of that sample: 65.44% under 100 views, 86.93% under 1,000. A TubeStats update gives a median of 39 — [YouTubeScribe summary, Oct 2026](https://youtubescribe.com/blog/youtube-statistics); [SQ Magazine](https://sqmagazine.co.uk/how-many-videos-are-on-youtube) (aggregators of the UMass work)
- Selected corpora are far above that baseline:
  - OverseerOS 7-day Shorts median: 20,851 views. The authors say it "must not be interpreted as the typical result of every Short", because "the dataset contains a substantial number of high-performing videos" — [OverseerOS Shorts 7-day study, 29 Oct 2026](https://www.overseeros.com/blog/youtube-shorts-views-after-7-days)
  - OverseerOS Shorts million-view rate: 2.6% in "library" records vs 22.9% in "channel-analysis" records. The rate depends on how videos entered the sample — [OverseerOS, 8 Nov 2026](https://www.overseeros.com/blog/what-percentage-of-youtube-shorts-reach-1-million-views)

**Failure base rates for new channels (what search hides)**
- vidIQ tracked 36,163 newer gaming channels for 360 days:
  - Minecraft (n=2,752): 26% reached ≥1,000 subs, 2.73% reached 10,000; median gain **78 subscribers**.
  - Roblox: 42% / 5.22%; median gain 268.
  - Other gaming: 16% / 1.30%; median gain 23.

  — [vidIQ Research, Sep 2026](https://vidiq.com/research/minecraft-roblox-small-creators) (vendor)
- vidIQ also tracked channels created Jan–Jun 2025 that posted ≥10 same-format uploads in 90 days. Median 30-day views:
  - first long-form upload: 180;
  - tenth long-form upload: 272;
  - first Short: 1,362.

  Selection excludes channels that stopped before 10 uploads (survivorship is acknowledged) — [vidIQ first-10-videos study, Jul 2026](https://vidiq.com/tr/research/youtube-first-10-videos-study)
- Viddar has scored about 296,000 channels; 58.4% are under 1,000 subscribers — [Viddar, Aug 2026](https://viddar.io/en/blog/how-accurate-are-social-blade-earnings) (vendor)

**Minimum videos per channel, and weighting**
- On 67 channels with 2,580 mature long-form videos:
  - The latest-10 median differed from the fuller-catalog median by a median 38.8%; the latest-20 differed by 20.9%.
  - For 27 of 67 channels, the latest-10 median was off by more than 50%.
  - Recommendation: "At least 10 videos, preferably 20".

  — [OverseerOS average-views study, Aug 2026](https://www.overseeros.com/blog/average-views-per-youtube-video)
- OverseerOS computes "channel-level medians before calculating group benchmarks, rather than pretending all 2,043 videos are independent". It also re-ran with prolific channels (25+ videos) removed; the median barely moved (20,851 → 20,323) — [views-to-subscriber study](https://www.overseeros.com/blog/youtube-views-to-subscriber-ratio); [Shorts 7-day study](https://www.overseeros.com/blog/youtube-shorts-views-after-7-days)

**Countries and languages**
- Engagement varies by country. In a top-100-channels study, India had the lowest median — [Mark Studios, Oct 2026](https://www.markstudios.com/research/youtube-engagement-rate-study)
- One small-channel corpus "skews to India (41.7%)". The authors warn it is a scale reference, not a benchmark — [Grow Creator, Aug 2026](https://growcreator.pro/blog/small-youtube-channel-statistics)
- RPM by market spans about 6× the worldwide figure (Australia $7.16, 6.07× worldwide) — [EarningsOf citing Dynamoi/AIR](https://earningsof.com/en/rpm)
- The channel resource exposes `snippet.country` and `snippet.defaultLanguage`, which can be used to stratify — [channels resource](https://developers.google.com/youtube/v3/docs/channels)
- `search.list` filters (checked against Google's reference, Sep 2026):
  - `regionCode` returns videos "that can be viewed in the specified country". It is a viewability filter, not the creator's country.
  - `relevanceLanguage` returns results "most relevant to" a language. It ranks; it does not filter strictly.

  — [search.list reference](https://developers.google.com/youtube/v3/docs/search/list)

**Google's own warnings about search completeness (same reference page)**
- `order=date` "relies on the search index, you may experience indexing delays for new content or receive incomplete result sets". "To reliably retrieve a channel's most recently uploaded videos, do not use `search.list`", use the uploads playlist (`playlistItems.list`) instead.
- "Specifying a sort order other than `relevance` might result in a smaller or incomplete result set, particularly when combined with date filters like `publishedAfter` or `publishedBefore`."
- `maxResults` is 0–50 per page, and "the API may return fewer items than the requested `maxResults` per page ... even if additional results are available".
- `pageInfo.totalResults` "is an approximation", is capped at 1,000,000, and should not be used for counts. Do not use it as a "niche supply" or "competition" number.
- Searches restricted to one channel (`channelId` + `type=video`) are capped at 500 videos.

— [search.list reference](https://developers.google.com/youtube/v3/docs/search/list)

### Inferences
- **Sample size for a stable median (INFERRED, standard non-parametric statistics).** The 95% confidence interval for a median runs between the order statistics at about n/2 ± 0.98·√n.

  | Sample size | 95% interval covers roughly | Use |
  | --- | --- | --- |
  | n = 30 videos | P32–P68 of the distribution | wide |
  | n = 100 | P40–P60 | |
  | n = 400 | P45–P55 | |

  With view distributions spanning 10×–50× between P25 and P75 (see Benchmarks), the practical floors are:
  - ≥30 **channels** for a niche-level "median of channel medians", ≥10–20 videos per channel;
  - about 200–400 videos minimum for a pooled video median.
  - Report P25/P50/P75, not just P50.
- **Two-sample design for every niche (INFERRED).**
  - (A) A "what wins" sample: relevance or view-count search. This is biased toward winners and should be labelled as such.
  - (B) A "who is trying" sample: `order=date` with `publishedAfter` = now − 48h (or 7 days), several keyword variants, repeated daily for a week. Then pull every channel found, list its uploads via the uploads playlist, and read stats with `videos.list`/`batchGetStats`.

  Sample B exposes small and failing channels. It is still not random, for two reasons. The API can return zero when topic density is low, and Google itself says `order=date` with date filters can be "smaller or incomplete". Label it "recent-upload sample".

  Use search **only to discover channel IDs**. Once you have a channel, take its full upload history from its uploads playlist, which Google recommends over `search.list` for that purpose. This removes the search engine's video-level selection from each channel's median, although the choice of which channels you found is still biased.
- **Supply counts (INFERRED).** Never use `pageInfo.totalResults` or Tube Atlas "results found" as a measure of competition. Count supply directly: the number of distinct channels and uploads you actually retrieved in a dated window, labelled with the query set used.
- **Market filter (INFERRED).** `regionCode=US` means "watchable in the US", which almost every video is. To isolate an English/US-market sample, filter on the channel's `snippet.country` and on title/description language after retrieval. `relevanceLanguage=en` only changes ranking.
- **Shorts vs long-form (INFERRED).** Treat them as separate populations, never pooled (views are defined differently; see the top note). Classify by duration ≤180 s only as a proxy. OverseerOS notes that duration-based classification "is not independent Shorts-feed verification".
- **Language and country (INFERRED).** Do not mix markets in one benchmark. Stratify by channel `country` or detected title language. If the target is the US/English market, drop or separately report channels from other markets, because both engagement and RPM differ several-fold.
- **Labelling.** Benchmarks computed from Tube Atlas keyword exports should carry the label "OBSERVED (surfaced-by-search sample, not random)".

### Gaps
- No published study gives a "minimum sample per niche" specific to YouTube niche research; the sizes above are standard statistics (INFERRED).
- I found no documentation of how Tube Atlas orders or limits its keyword results (UI scrape vs API). Assume it inherits YouTube search ordering (INFERRED).

---

## Metrics and formulas: median vs mean, outlier multiple, views/subscriber, engagement rate, velocity, decay curve

### Takeaway
- **Use medians and percentiles, never the mean.** On a typical channel the mean is about 2× the median.
- **Outlier = video views ÷ the channel's median of comparable same-format, same-age videos.** About 2× is top-quartile and about 4.6× is top-decile.
- **Views/subscriber falls steeply with channel size**, so only compare within a size band.
- **Engagement (likes + comments) ÷ views has a median of about 2–4% for long-form and is lower for Shorts.** It fell mechanically after 24 Aug 2026.
- **Velocity must come from two snapshots of the same video.** Lifetime views ÷ age misleads because views are front-loaded: about 54% of week-one long-form views arrive in the first 24 h, and about 94% of 30-day views arrive by day 7.

### Cited Findings
**Median vs mean**
- On 67 channels, the median channel's mean was **1.97×** its median.
  - On the median channel, the top video held 19.6% of views, the top 10% of videos 48.7%, and the top 20% 64.6%.
  - Dropping the top 10% brought the mean to 1.19× the median.

  — [OverseerOS, Aug 2026](https://www.overseeros.com/blog/average-views-per-youtube-video)
- In SaaS channels, the top 10% of videos drove 42.2% of channel views — [Grizzle, Sep 2026](https://grizzle.io/blog/saas-youtube-study)
- With the mean, "one viral video was enough to more than triple the average" in the under-10K tier — [ytgrowth engagement study, Aug 2026](https://ytgrowth.io/blog/youtube-engagement-rate)

**Outlier multiple (channel-relative)**
- Within-channel thresholds (views ÷ channel median): top quartile **2.14×**, top 20% 2.59×, top 10% **4.62×**, top 5% **7.33×** — [OverseerOS](https://www.overseeros.com/blog/average-views-per-youtube-video)
- TubeAI defines a breakout as ≥2× the channel's typical views. In gaming (1.8M long-form videos), the breakout rate is 16.1–21.4% per duration band, and the median video lands at 0.95–1.03× its channel norm — [TubeAI gaming benchmarks, Sep 2026](https://tubeai.app/blog/youtube-niches/gaming-youtube-benchmarks) (vendor)
- Outlier score = "video's views divided by its channel's usual (median) views" — [TubeSpace](https://tubespace.cloud/) (vendor)
- Paid-promotion contamination: Grizzle excluded videos with ≥50,000 views **and** engagement below 0.05% as "paid-promoted" — [Grizzle](https://grizzle.io/blog/saas-youtube-study)

**Views/subscriber ratio**
- Channel-weighted median (videos 7–30 days old): long-form **11.9%**, Shorts 21.7%.
  - Long-form by size: <10K 170.7%; 10K–99K 36.2%; 100K–999K 11.3%; 1M+ 5.2%.
  - On channels with both formats, the Shorts ratio was higher in only 39% of them.

  — [OverseerOS views-to-subscriber study, Aug 2026](https://www.overseeros.com/blog/youtube-views-to-subscriber-ratio)
- Day-7 views/subscribers by size: <1K 76.5%; 1K–9.9K 147.9%; 10K–99K 38.8%; 100K–999K 19.3%; 1M+ 2.66% — [OverseerOS benchmarks 2026](https://www.overseeros.com/blog/youtube-benchmarks-2026)
- Gaming views per subscriber (average views): 0.77 at 1K–10K; 0.49 at 10K–100K; 0.19 at 1M+ — [TubeAI gaming](https://tubeai.app/blog/youtube-niches/gaming-youtube-benchmarks)
- Large gaming channels (29 channels): median 4.4%; 7 of 29 had not posted long-form in 90 days — [SoInfluential, Oct 2026](https://soinfluential.com/blog/gaming-youtubers-by-the-numbers-2026/)

**Engagement rate = (likes + comments) ÷ views**
- OverseerOS, 2,251 videos aged 7–30 days:

  | | Long-form | Shorts |
  | --- | --- | --- |
  | Median | 3.48% | 2.71% |
  | P75 | 4.91% | 4.55% |
  | P90 | 7.26% | 6.67% |
  | Median like rate | 3.11% | 2.60% |
  | Median comment rate | 0.238% | 0.032% |

  — [OverseerOS engagement benchmarks, Aug 2026](https://www.overseeros.com/blog/youtube-engagement-rate-benchmarks)
- Across 49,802 tracked videos, long-form beat Shorts in every niche by about 1.4×. Gaming long-form median was **3.809%** (n=2,912) — [ytgrowth, Aug 2026](https://ytgrowth.io/blog/youtube-engagement-rate) (vendor)
- Gaming medians from two other sources: 4.18% (SociaVault) and 4.40% (CreatorDB, ~1.46M channels, measured under the old view standard) — [SoInfluential engagement guide, Jul 2026](https://soinfluential.com/blog/good-engagement-rate-youtube-2026/)
- The top 100 most-subscribed channels in Oct 2026 (post-change) had a median channel of **0.82%** on regular videos and 1.52% on Shorts. Other published benchmarks span 2.2–2.6% median (TubeStats 2.24%; another 1.59M-video study 2.6%, with Kids & Animation 0.2%). After 24 Aug 2026, "a channel's engagement rate falls when more of its plays count as views". Benchmarks built on 2025 data "are therefore not like for like" — [Mark Studios, Oct 2026](https://www.markstudios.com/research/youtube-engagement-rate-study)
- Metricool's 2026 study: long-form engagement fell from 2.38% (2025) to 1.30% (2026), −45% — [Metricool YouTube Study 2026 PDF](https://metricool.com/wp-content/uploads/youtube-study-2026-EN.pdf) (vendor)
- Agentio (75,000+ videos): on average only **6 in 10 public views are engaged views** (≈549M public vs 330M engaged), a 1.67× overstatement. The gap is larger on micro channels (<50K) — [Tubefilter, 4 Sep 2026](https://www.tubefilter.com/2026/09/04/youtubes-new-public-viewcounts-over-report-actual-engagement-by-40) (Agentio is an ad platform, so vendor)

**Velocity and decay (published data)**
- **Long-form, hourly tracking** (N=321,220 uploads, Aug 31–Sep 24 2026):
  - share of first-week views: 9% by hour 6, **54% by hour 24**, 84% by day 3;
  - **93.3% of 14-day views by day 7**;
  - videos whose first 24 h were ≥2× their channel's usual first day became breakouts **80.1%** of the time; those under 0.5× did so 2.1% of the time.

  — [TubeAI, 2026](https://tubeai.app/blog/youtube-algorithm/how-long-youtube-video-views) (vendor; served-creator channels; 100+ views by day 7)
- **Same videos tracked to day 30** (18,423 videos, 837 channels): median 94.5% of day-30 views by day 7 and 97.6% by day 14. Shorts 95.0% vs long-form 94.1% by day 7 — [ytgrowth, Aug 2026](https://ytgrowth.io/blog/youtube-view-growth-curve) (vendor)
- **Shorts, matched day 7 → day 30** (160 videos):
  - median **80.7%** of day-30 views at day 7 (P25 56.3%, P75 91.7%);
  - 21.3% at least doubled after week one;
  - videos with ≥100K at day 7 had only 63.6% of day-30 views by then.

  — [OverseerOS Shorts study](https://www.overseeros.com/blog/youtube-shorts-views-after-7-days). This conflicts in magnitude with ytgrowth's 95% for Shorts; the samples differ (selected high performers vs a tracked-channel panel).
- **Library effect**, median lifetime views/day by age cohort (SaaS long-form):
  - 0–90 days: 8.60/day, with 88% still earning ≥1 view/day;
  - 90–180 days: 1.26/day (56%);
  - 180–365 days: 0.68/day (40%).

  — [Grizzle](https://grizzle.io/blog/saas-youtube-study)
- **Academic studies:**
  - In every category, 50–60% of videos peak on day 1. About 85% of News/Sports videos peak within 4–5 days. Most videos decay after an early peak and "relatively few videos ever return to near their peak" — [Chowdhury & Makaroff, WEBIST 2013](https://www.scitepress.org/Papers/2013/43728/43728.pdf)
  - Correlation between 7-day views and views at 24 h / day 1 / day 2: 0.59 / 0.88 / 0.94. Day-one counts are unstable for videos exposed only a few hours — [Cha et al., SMU repository](https://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=6327&context=sis_research)
  - Top videos: "50% of them receive between 31% and 100% of their views on a single (peak) day" — [Figueiredo et al., arXiv 1402.1777](https://arxiv.org/html/1402.1777v3)
  - Over 2 years and 172K videos, videos pass through multiple phases. Nearly 3/4 of the top-5% videos had ≥3 phases; >60% of news videos are one long power-law decay — [Yu, Xie & Sanner, ICWSM 2015](https://ojs.aaai.org/index.php/ICWSM/article/view/14609)
- Cross-sectional cohorts cannot be chained into a curve. OverseerOS's separate day-7 / 30 / 90 medians (28,604 / 27,831 / 45,608) "come from different cohorts". "You can only measure actual view accumulation by following the same video through multiple checkpoints" — [OverseerOS benchmarks](https://www.overseeros.com/blog/youtube-benchmarks-2026)

### Inferences
Proposed standard formulas. All are INFERRED, built on the findings above.

1. **Typical performance.** Median views of comparable videos: same format, measured at the same age checkpoint (D1, D7, D30 or D90), ideally at least 20 per channel. Always report P25/P50/P75 and n.
2. **Outlier multiple.** `x_channel = views_at_age_A / median(views_at_age_A of the same channel's other videos, same format)`.
   - Require ≥10 comparable videos per channel. With fewer than 10, flag the multiple as "LOW-N" and do not rank on it.
   - Thresholds: ≥2× notable, ≥3× outlier (the studio's current `cf_research_stats.py` default), ≥5× strong.
   - The current tool requires only ≥3 videos per channel. Per OverseerOS, that makes the channel median unstable; raise the floor to 10 (INFERRED recommendation).
3. **Age-normalised comparison.** For videos of mixed age without snapshots, compare only within age buckets (0–7 d, 8–30 d, 31–90 d, 90+ d), never on lifetime views. Tube Atlas's "Average Views per Day" (= lifetime views ÷ age) **overstates** current velocity for old videos and **understates** it for very new videos (hour 6 is about 9% of week one). Treat it as a ranking hint only.
4. **Velocity.** `v = (views_t2 − views_t1) / (t2 − t1 in days)` from two dated snapshots of the same video ID, at least 24 h apart. Label the result OBSERVED (delta) and the window. Lifetime views/day is labelled "lifetime average", never "velocity".
5. **Views/subscriber.** Report it only within subscriber bands (<1K, 1K–10K, 10K–100K, 100K–1M, 1M+) and at a fixed age. Subscriber counts above 1,000 are rounded (see Verification), so the ratio is approximate.
6. **Engagement.**
   - Formula: `(likes + comments) / views`, plus separate like-rate and comment-rate.
   - Compute separately for Shorts and long-form, and tag every value "pre-24-Aug-2026" or "post-24-Aug-2026".
   - A post-change long-form engagement rate below about 1% can be normal for big channels (Mark Studios 0.82%).
   - Engagement below 0.05% on a high-view video suggests paid promotion; exclude it from organic benchmarks.
7. **Day-1 forecast.** For one's own channel, first-24 h views ÷ the channel's usual first-24 h views is the best early signal (TubeAI: ≥2× → 80% breakout). For competitors this needs hourly or daily snapshots from upload.

### Gaps
- **No published day-1 / 7 / 30 share of *lifetime* (multi-year) views** for long-form or Shorts. Published curves stop at day 14–30. Search and evergreen formats (tutorials, sleep audio) likely keep earning longer (Grizzle's library effect), but there is no niche-specific curve.
- **No public engagement or decay study specific to Minecraft.** The gaming figures are the closest.
- The vendor decay studies (TubeAI, ytgrowth) use creator panels, not random samples. Methods are summarised but not peer-reviewed.

---

## Benchmarks: views by subscriber band, Shorts vs long-form, gaming/Minecraft, RPM by category, and why scraped "estimated earnings" must not be used

### Takeaway
Published 2026 benchmarks (vendor panels, not random samples):
- **Long-form views at about day 30, by band:** about 45 (<1K), 5.4K (1K–10K), 11.6K (10K–100K), 29K (100K–1M), 293K (1M+), with P25–P75 spreads of 10–50×.
- **Gaming averages per band:** 5.2K / 13K / 80K / 392K.
- **RPM:** median about $2.30 overall and about $2.05 for gaming, with gaming's P25–P75 at $0.70–$3.62. Kids is $0.33. Shorts RPM is 3–14% of long-form RPM.

A flat "estimated earnings" column ($1.85 per 1,000 views per the brief; Social Blade uses $0.25–$4.00) ignores whether the channel is monetized, the Shorts/long mix, country, made-for-kids status and the post-Aug-2026 public-vs-engaged view gap. **Do not use it for any decision.**

### Cited Findings
**Views by subscriber band (long-form)**
- OverseerOS 30-day cohort (1,051 uploads, 486 channels, ages 28–32 days):

  | Subscriber band | P25 | Median | P75 |
  | --- | --- | --- | --- |
  | <1K | 14 | 45 | 157 |
  | 1K–9.9K | 366 | 5,428 | 28,181 |
  | 10K–99K | 3,950 | 11,582 | 55,231 |
  | 100K–999K | 8,128 | 29,255 | 134,665 |
  | 1M+ | 63,847 | 292,667 | 1.16M |

- OverseerOS 7-day cohort (436 uploads), medians: 40 / 5,840 / 11,381 / 36,175 / 254,270.
- OverseerOS 90-day cohort (1,035 uploads), medians: 67 / 3,538 / 12,314 / 74,089 / 364,233; pooled P10 910, P50 45,608, P90 891,026.

  — [OverseerOS benchmarks 2026](https://www.overseeros.com/blog/youtube-benchmarks-2026) (vendor, selected corpus)
- Small channels (360 audited, India-skewed), median lifetime views per video: 1,260 (1K–5K), 2,209 (5K–10K), 8,219 (10K–25K), 12,864 (25K–50K) — [Grow Creator](https://growcreator.pro/blog/small-youtube-channel-statistics)
- **Gaming** (32,839 channels with ≥1K subs and a long-form upload in the last 180 days). Median of channel average views: 5,194 (1K–10K); 13,052 (10K–100K); 80,009 (100K–1M); 392,185 (1M+). Typical cadence is about 0.62 uploads/week — [TubeAI gaming](https://tubeai.app/blog/youtube-niches/gaming-youtube-benchmarks). These are per-channel **means**, so they run higher than medians.
- Minecraft topic snapshots (30-day windows):
  - "Minecraft challenge" averaged 595,666 views/video over only 13 videos (May 2026);
  - "Minecraft" averaged 897.3K over 30 videos (Aug 2026).

  These are means of trending-topic videos, i.e. a winners-only sample — [Hype gaming trends Aug 2026](https://hype.ad/blog/trending-topics/gaming/august-2026); [May 2026](https://hype.ad/blog/trending-topics/gaming/may-2026)

**Shorts vs long-form**
- Tubular, 2025 through May: videos under 60 s were 75% of views and 57% of uploads; 20+ minute videos delivered 57% of minutes watched — [The Measure, Jun 2025](https://www.themeasure.net/longer-form-videos-dominate-youtube-watch-time-tubular-bloomberg-shorts/)
- Metricool 2025→2026:
  - long-form views +76%, but view duration −37% (3.98 → 2.51 min);
  - long-form ad revenue per account −55%;
  - channels posting about 5 Shorts/month averaged 8,789 views per long-form video vs 4,364 for channels with no Shorts.

  — [Metricool YouTube Study 2026](https://metricool.com/wp-content/uploads/youtube-study-2026-EN.pdf) (vendor; correlational)
- In SaaS channels with both formats, the median Shorts:long-form views ratio was 1.48×, and the distribution was bimodal — [Grizzle](https://grizzle.io/blog/saas-youtube-study). For large channels, the median channel's Shorts got 0.45× its long-form views — [SoInfluential](https://soinfluential.com/blog/good-engagement-rate-youtube-2026/). The direction depends on the sample.

**RPM by category (real Studio data)**
- AIR Media-Tech: 300 channels, 3,595 monetized channel-months, May 2025–May 2026, Studio data.

  | Niche | Median RPM | P25–P75 |
  | --- | --- | --- |
  | All niches | **$2.30** | |
  | Education & Science | $10.22 | $2.31–$19.50 |
  | Lifestyle | $2.98 | |
  | Entertainment | $2.43 | |
  | **Gaming** | **$2.05** | $0.70–$3.62 (Studio CPM $4.05; ad load 1.44) |
  | Health & Sport | $1.23 | |
  | **Kids & Teens** | **$0.33** | $0.16–$0.88 |

  - The median channel monetizes only **53% of its views**.
  - The top 10% of channels capture 58% of ad revenue.
  - Niches with fewer than 10 channels are marked directional.

  — [AIR: which niche makes the most money](https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm); [AIR RPM glossary](https://air.io/en/youtube-glossary/what-is-youtube-rpm-full-breakdown); [Vidpuff table](https://vidpuff.com/blog/youtube-niche-rpm-data-2026)
  - **Vendor bias:** AIR is an MCN selling audits, and the panel is its own partner channels.
  - **Internal inconsistency:** AIR's livestream article cites gaming *video* RPM as **$1.15** on a 404-channel dataset — [AIR livestream study](https://air.io/en/air-data-findings/livestream-rpm-revenue-and-subscribers-by-youtube-niche-the-2025-numbers). A local note cites AIR gaming long-form at $3.29–$3.42 by Shorts usage (`research_notes/Ngách Minecraft RPM cao bền vững/rpm_economics.md`).
- Shorts RPM was 3–14% of long-form RPM in almost every niche, "so most channels need 11,000 to 34,000 Shorts views to earn what 1,000 long-form views do" (274 channels) — [AIR fastest-growing niches, Nov 2026](https://air.io/en/audience-growth/whos-growing-fastest-on-youtube-and-which-niches-are-hot-in-2025)
- **RPM is computed per 1,000 *engaged* views.** It includes ads, memberships, Premium and Super Chat — [YouTube Help: ad revenue analytics](https://support.google.com/youtube/answer/9314357)
- One estimator therefore multiplies public views by an engaged-view rate of 46–67% before applying RPM — [EarningsOf](https://earningsof.com/en/rpm)
- YPP thresholds for new applicants from 1 Feb 2027 are reported as 8,000 watch hours in 365 days or 20M Shorts views in 90 days. Shorts revenue sharing would need 10M qualified Shorts views per 90 days — [EPR, Oct 2026, citing PPC Land](https://everything-pr.com/youtube-first-frame-views) (secondary; verify against YouTube Help before relying on it)

**Why scraped "estimated earnings" are unusable**
- Social Blade uses a flat $0.25–$4.00 RPM × daily views ÷ 1,000. It "assumes that every view on the channel is monetized, which is usually not the case. It is entirely possible NO views are monetized, or views come from a lower monetized medium such as shorts" — [Social Blade FAQ](https://socialblade.com/help/how-are-estimated-earnings-calculated)
- Tube Atlas advertises "estimated earnings from ad revenue for all videos" and columns "Estimated Video Earnings" and "Estimated Earnings per Day" — [tubeatlas.com](https://tubeatlas.com/). Reviewers note "Earnings and search volume figures are estimates, not real data" — [SaaSPic, Nov 2026](https://saaspic.com/tools/tube-atlas). The local note says the formula is undisclosed — `research_notes/Cách dùng Tube Atlas/reviews_comparison.md`.
- The flat **$1.85 per 1,000 views** rate is OWNER/brief-reported. I found no public documentation of it.
- vidIQ also labels channel earnings as estimates, for example "Est. ad revenue" on the official Minecraft channel page — [vidIQ channel stats](https://vidiq.com/youtube-stats/channel/@minecraft)

### Inferences
- **Why a flat rate is wrong for this studio (INFERRED).** A flat $1.85 sits near the gaming median ($2.05), so it looks plausible. But:
  - (a) gaming's interquartile range is $0.70–$3.62, a 5× spread;
  - (b) Shorts earn 3–14% of that;
  - (c) made-for-kids or kids-skewing Minecraft content earns about $0.33;
  - (d) after 24 Aug 2026 public views overstate engaged views by about 1.67× (Agentio), so a per-public-view RPM should be about 0.6× the Studio RPM;
  - (e) many scraped channels are not monetized at all.

  A Minecraft Shorts channel with 1M public views could plausibly earn about $30–$150 (0.6 × 1M/1000 × ~$0.05–$0.25), while the flat column would show $1,850 (INFERRED arithmetic).
- **Proposed revenue rule (INFERRED).** The studio should store "est_revenue" only as an INFERRED range:
  - Formula: `public_views × engaged_share(0.46–0.67) × format_RPM_range / 1000`.
  - `format_RPM_range` is the AIR gaming P25–P75 for long-form and 3–14% of that for Shorts, or $0.16–$0.88 if the content is made for kids.
  - Always show it as a range, with the monetization status unknown unless verified.
  - Delete or ignore the Tube Atlas earnings columns at import.
- **Using benchmarks (INFERRED).** Use the published bands only as sanity checks ("is this niche's median abnormally high or low for its size band?"). The decision benchmark should be the niche's own channel-weighted median from the studio's own samples, as CLAUDE.md requires.

### Gaps
- **No Minecraft-specific RPM or views-by-band study from Studio data.** Minecraft rows are gaming proxies or winners-only topic reports.
- **No public confirmation of Tube Atlas's $1.85 constant.** The repo has no Tube Atlas CSV export to test it: the CSVs under `research_notes/Quét ngách Minecraft bằng YouTube API/data/` came from the API, not Tube Atlas. To check it on the owner's first export: `est_earnings / views × 1000` should be identical on every row if the rate is flat. Also check whether "Estimated Earnings per Day" equals that rate × lifetime views ÷ age.
- vidIQ, Tubular and Social Blade did not publish (in what I found) a 2025–2026 views-by-subscriber-band median table with disclosed methods. OverseerOS and TubeAI are the only band tables, and both are vendor panels.

---

## Verification: spot-checking scraped numbers against the API, channel age, hidden or rounded subscribers, deleted/private videos, re-uploads, view corrections

### Takeaway
- Spot-check every scraped export against the Data API:
  - `videos.list` (1 unit per call, up to 50 IDs; returns `viewCount`, `likeCount`, `commentCount`, `publishedAt`, duration);
  - the newer `videos.batchGetStats` (own 10K-unit bucket; reports `failedVideoIds`);
  - `channels.list` (`snippet.publishedAt`, `statistics.subscriberCount` rounded down to 3 significant figures, `hiddenSubscriberCount`, `videoCount` = public videos only).
- Treat subscriber counts as approximate. Treat missing or failed IDs as deleted, private or blocked. Expect later downward view corrections. Dedupe re-uploads.

### Cited Findings
**Quota (2026)**
- Default allocation: 100 `search.list` calls/day, 100 `videos.insert` calls/day, and 10,000 units/day for all other endpoints. `search.list` and `videos.insert` "have their own quota buckets", 1 per call. Each extra page costs again. Quotas reset at midnight PT — [Quota Calculator, updated 12 Nov 2026](https://developers.google.com/youtube/data/determine_quota_cost); [Quota and compliance audits](https://developers.google.com/youtube/data/guides/quota_and_compliance_audits)
- Granular quota system from 1 Jun 2026. `videos.batchGetStats` was added on 3 Jun 2026 (1 unit, own 10,000-unit/day bucket). Upload cost fell from about 1,600 to about 100 units on 4 Dec 2025 — [API revision history](https://developers.google.com/youtube/v3/revision_history?hl=en); [feed](https://developers.google.com/static/youtube/v3/feeds/data-api-revision-history.xml)
- Older guides that say "a search costs 100 units of your 10,000" are outdated — [SociaVault, Oct 2026](https://sociavault.com/blog/youtube-data-api-quota-2026) (secondary, consistent with Google docs)
- More than the default quota requires an API compliance audit — [Quota and compliance audits](https://developers.google.com/youtube/data/guides/quota_and_compliance_audits)

**Fields and rounding**
- `statistics.subscriberCount` is "rounded down to three significant figures". Example: 123,456 → 123,000. This has applied to counts >1,000 since Sep 2019, even on authorized requests — [channels resource](https://developers.google.com/youtube/v3/docs/channels); [revision history](https://developers.google.com/youtube/data/revision_history)
- `statistics.hiddenSubscriberCount` is a boolean showing whether the count is publicly visible. `statistics.videoCount` reflects "public videos only, even to owners". `snippet.publishedAt` gives the channel creation date; `snippet.country` is available — [channels resource](https://developers.google.com/youtube/v3/docs/channels)
- `videos.batchGetStats` returns `snippet.publishTime`, `viewCount`, `likeCount`, `commentCount`, `duration` and `durationMillis`. It also returns `summary.failedVideoIds[]` and requested/succeeded/failed counts. No authentication is needed for public videos — [batchGetStats](https://developers.google.com/youtube/v3/docs/videos/batchGetStats)
- The `mostPopular` chart content changed on 21 Jul 2025 — [revision history](https://developers.google.com/youtube/v3/revision_history?hl=en). Old "trending" samples are not comparable.

**View corrections and lags**
- YouTube is "constantly confirming and adjusting engagement events". Counts can look frozen, and low-quality playbacks (multiple devices, tabs) are removed — [YouTube Help](https://support.google.com/youtube/answer/2991785)
- Over 17 months, 270,133 videos from 1,064 French news channels were tracked hourly for 7 days. View corrections (removals) are inferable only from drops in cumulative counts. Views concentrate on day one — [Scientific Reports 2024, "Fake views removal and popularity on YouTube"](https://www.nature.com/articles/s41598-024-63649-w)
- Social Blade updates about once a day across about 100M profiles, so numbers lag. Daily view deltas can be negative or zero — [Social Blade FAQ](https://socialblade.com/help/why-do-my-views-differ-from-socialblade)

**Re-uploads and aliases**
- "A large number of aliases are uploaded on the same day as the original video or within a week". One alias that appeared more than 200 days later got about 1,000× the original's views — [Cha et al., IMC 2007](https://www.cl.cam.ac.uk/~jac22/camhor/mia_imc07_sumitted.pdf)

**Paid views**
- Ad views contribute to the public view count ("YouTube public views ... counted the moment a video ad starts to play") — [YouTube Help](https://support.google.com/youtube/answer/2991785)
- Paid-promoted videos show extreme views with engagement an order of magnitude below organic — [Grizzle](https://grizzle.io/blog/saas-youtube-study)

### Inferences
Proposed verification protocol. All steps are INFERRED from the facts above.

1. **Spot-check per import.**
   - Take a random 5% of rows (at least 20) from every Tube Atlas CSV.
   - Re-read them with `videos.list`/`batchGetStats` within 24 h of the export.
   - Pass if `|api − scraped| / api ≤ 2%` for views (counts move between reads), with exact match on `publishedAt` date and duration.
   - Fail the whole import if more than 10% of the sample fails, and log the result in the decision log.
2. **Missing or failed IDs.** If an ID is absent from `videos.list` items or listed in `failedVideoIds`, mark it `status=unavailable` (deleted, private, region-blocked or terminated). Keep the row for survivorship accounting, but exclude it from current medians.
3. **Hidden subscribers.** If `hiddenSubscriberCount=true`, store subscribers as NULL (not 0) and exclude the channel from views/subscriber and band assignment.
4. **Rounded subscribers.**
   - Store the raw value plus `subs_quantum = 10^(floor(log10(S)) − 2)` for S > 1,000. Examples: 1,230,000 has a quantum of 10,000; 45,600 has a quantum of 100.
   - A subscriber delta smaller than one quantum is "no measurable change", not zero growth.
   - For channels above 100K, measure subscriber growth only over windows long enough to cross several quanta (weeks, not days).
5. **Channel age.**
   - `age_days = as_of − channels.snippet.publishedAt`.
   - Also record the first and latest upload dates from the uploads playlist (`contentDetails.relatedPlaylists.uploads` → `playlistItems.list`).
   - A channel created years ago with its first upload recently is a repurposed or "new" channel. Classify "new competitor" by first public upload date, not account creation (INFERRED; account creation can predate content).
6. **Re-uploads and duplicates.**
   - Dedupe by video ID.
   - Flag likely re-uploads: same normalized title and duration within ±2 s across channels. Exclude them from originality and outlier lists.
   - Flag compilations or re-uploads of competitor content as non-benchmark rows.
7. **Paid-promotion filter.** Exclude rows with views ≥50K and (likes + comments)/views < 0.05% from organic benchmarks.
8. **Format classification.** Shorts if duration ≤180 s (proxy). Store `durationMillis` and keep the classification rule versioned.
9. **Quota planning** (INFERRED arithmetic from the docs):
   - 100 searches/day × up to 50 results gives at most about 5,000 search hits/day.
   - Stats refresh via `videos.list` costs about 1 unit per 50 IDs, so 10,000 units refresh about 500,000 video IDs/day. `batchGetStats` adds its own bucket.
   - Search is the bottleneck. Discover channels via search, then crawl uploads playlists (1 unit per 50 items) instead of searching repeatedly.

### Gaps
- The docs I fetched do not state the exact `videos.list` behaviour for deleted or private IDs (silently omitted vs error). Treating them as missing items follows common practice (INFERRED). Neither do they state the maximum IDs per `batchGetStats` call; 50 is assumed by analogy (INFERRED).
- What `subscriberCount` returns when `hiddenSubscriberCount=true` is not stated in the fetched page (commonly 0). Handle it as NULL (INFERRED).
- No public accuracy audit of Tube Atlas exports against the API exists (local note `reviews_comparison.md` says the same).

---

## Snapshot and time-series practice: re-scrape cadence, dated CSVs, deltas, OBSERVED vs INFERRED

### Takeaway
- Keep immutable, dated raw snapshots (one file per pull, timestamped in UTC).
- Re-read the same video IDs on a fixed schedule:
  - hourly or every few hours for the first 48 h if early-signal detection matters;
  - daily through day 7;
  - then about day 14, 30 and 90.
- Compute velocity only as deltas between snapshots of the same ID. Never chain separate cohorts into a curve. Tag every value with its as-of time and the view-definition era.

### Cited Findings
- **Fixed age checkpoints.** "Choose a fixed checkpoint such as 7 days, 14 days, 28 days, 90 days", then compare every upload at that checkpoint. For subscriber growth, OverseerOS required ≥7 days between comparable snapshots and normalized to a monthly-equivalent rate (median 3.10%; Spearman −0.683 between size and % growth) — [OverseerOS average views](https://www.overseeros.com/blog/average-views-per-youtube-video); [OverseerOS benchmarks](https://www.overseeros.com/blog/youtube-benchmarks-2026)
- **Never chain cohorts.** Separate day-7, day-30 and day-90 cohorts gave medians of 28,604, 27,831 and 45,608. "A video cannot lose views from day 7 to day 30", so these are not a curve — [OverseerOS](https://www.overseeros.com/blog/youtube-benchmarks-2026)
- **How fast the window closes.**
  - Long-form: about 54% of week-one views arrive in 24 h and 84% by day 3, so day 1–3 snapshots carry most of the information — [TubeAI](https://tubeai.app/blog/youtube-algorithm/how-long-youtube-video-views)
  - By day 2, views correlate 0.94 with day-7 views — [Cha et al.](https://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=6327&context=sis_research)
  - Day-1 views alone are unstable — [same](https://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=6327&context=sis_research)
- **Selecting the nearest snapshot.** Researchers pick the observation nearest the target age within tolerance (OverseerOS days 6–8 and 28–32; ytgrowth ±3 days). Videos without a real snapshot near the checkpoint are excluded rather than estimated — [ytgrowth growth curve](https://ytgrowth.io/blog/youtube-view-growth-curve); [OverseerOS Shorts](https://www.overseeros.com/blog/youtube-shorts-views-after-7-days)
- **Lag and corrections.** Once-a-day scraping attributes views to the wrong day, and negative deltas occur — [Social Blade FAQ](https://socialblade.com/help/why-do-my-views-differ-from-socialblade). Corrections can only be inferred from drops in cumulative counts — [Scientific Reports 2024](https://www.nature.com/articles/s41598-024-63649-w)
- **Definition eras.**
  - Public view counting changed on 24 Aug 2026 (all formats) and on 31 Mar 2025 (Shorts) — [YouTube Help](https://support.google.com/youtube/answer/2991785); [Analytics API revision history](https://developers.google.com/youtube/analytics/revision_history)
  - Analytics keeps "engaged views". YouTube says "the vast majority of analytics remain anchored on engaged" metrics — [YouTube Blog](https://blog.youtube/inside-youtube/engaged-views-youtube-explained)
- **Snapshot-dated aggregate tables are standard practice.** Example: vidIQ publishes "Study version: 2026-09-22" with downloadable aggregate CSVs and notes observation dates — [vidIQ research](https://vidiq.com/research/minecraft-roblox-small-creators)

### Inferences
Proposed snapshot standard for the studio. All of it is INFERRED from the findings above. It is compatible with `tools/cf_research_stats.py`, which already writes snapshots and computes `growth()` against a previous file.

1. **Raw layer (immutable).**
   - Location: `data/research/<niche>/raw/<source>_<YYYY-MM-DDTHHMMZ>.csv`. `<source>` is `tubeatlas` or `api`.
   - Never edit a raw file. Store the export tool's version and the query or keyword used.
   - Required columns: `video_id, channel_id, as_of_utc, published_at, duration_s, format(short|long), views, likes, comments, subs_raw, subs_hidden, subs_quantum, channel_published_at, country, source, query`.
2. **Cadence.**
   - **Watchlist videos** (outliers and new-competitor uploads): T+0 (discovery), then every 6 h to 48 h if the owner wants early signal; otherwise daily to day 7, then day 14, 30 and 90.
   - **Channel-level stats** (subs, total views, videoCount): daily, but interpret subscriber deltas against the rounding quantum.
   - **Niche re-sample** (new search pull): weekly, plus the 48 h recent-upload slice.
3. **Delta table.** `delta_views = views_t2 − views_t1`, `days = (as_of_t2 − as_of_t1)` in fractional days, `velocity = delta_views / days`.
   - If the delta is below 0, mark it `correction` and do not floor it to 0 in raw. Exclude it from velocity medians.
   - Report the velocity window ("views/day over Nov 10 → Nov 12").
4. **Checkpoint table.** For each video, take the snapshot nearest D1, D7, D30 and D90 within ±1, ±1, ±3 and ±5 days. Leave it blank if none; never interpolate as OBSERVED. Interpolated values are labelled INFERRED.
5. **Era tag.** `view_era = pre_2025-03-31 | 2025-03-31..2026-08-23 | post_2026-08-24`, applied per format. Do not compute deltas across 24 Aug 2026 for long-form without flagging them, because the jump is definitional, not growth.
6. **Labels in reports.**
   - **OBSERVED:** raw counts with as-of time; deltas between two raw snapshots.
   - **INFERRED:** lifetime views/day, revenue estimates, interpolated checkpoints, cross-cohort comparisons, Shorts classification by duration.
   - **OWNER:** decisions and manual inputs, such as the claimed $1.85 Tube Atlas rate.
   - Every benchmark line carries n (videos and channels), sample type (search-surfaced vs recent-upload), format, age checkpoint and era.
7. **Minimum to call something "velocity".** Two snapshots ≥24 h apart for the same ID. A single Tube Atlas export only ever supports "lifetime average views/day (INFERRED proxy)".

### Gaps
- No public standard (academic or industry) prescribes a re-scrape cadence for niche research. The cadence above comes from the decay data (most views in days 1–3; a strong correlation by day 2).
- I did not verify whether Tube Atlas can re-pull a fixed list of video IDs, as opposed to re-running a keyword search. If it cannot, the API (`videos.list`/`batchGetStats`) should handle all re-snapshots, and Tube Atlas only discovery.
