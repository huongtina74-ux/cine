# Expert niche-validation method (exploding + durable), mapped to Tube Atlas + spreadsheet — as of 13 Nov 2026

Scope note. These notes cover how practitioners and tool vendors decide that a niche is (a) exploding now and (b) durable, what thresholds they publish, the named methods, the pitfalls and policy risks, and how each signal maps onto Tube Atlas v1.0.6.7. The statistics side (sampling bias, median vs mean, the 24 Aug 2026 view-count definition change, RPM benchmarks) is in the sibling file `data_standards.md`. These notes do not repeat it.

Labels follow the studio rule:
- **OBSERVED**: a cited source states it.
- **INFERRED**: my reasoning from cited facts.
- **OWNER**: from the brief (the Tube Atlas column list). I did not verify it publicly.

**Bias warning (applies to almost every source below).** Nearly all the quantitative "niche method" material is published by tool vendors who sell the outlier finders they describe: 1of10, OutlierKit, OverseerOS, TubeLab, NexLev, vidIQ, AIR Media-Tech. I found no independent academic validation of any outlier threshold. Treat the thresholds as practitioner conventions, not laws. 1of10 says so itself: the lines are "creator conventions, not YouTube metrics".

---

## Signals for "EXPLODING now": outlier multiple vs channel baseline, views/sub, age-normalised velocity, number of new channels breaking out, upload-to-breakout time

### Takeaway
Every credible method measures performance against the video's own channel, not raw views. The calculation is views ÷ the channel's recent baseline (last 10–20 uploads). A niche counts as "rising" when several different, mostly new channels break out on the same demand. A single viral video does not count.

The age-normalised signal is views/day, or early views compared with the channel's usual first 7 days. Momentum on a topic-level trend is reported to last only about 2–6 weeks. So "exploding" alone is a short window, and it must be paired with the durability tests in the next section.

### Cited Findings
**Outlier definition and baseline**
- 1of10 defines "Outlier ratio = video views / the channel's average views per video". The baseline is the last 10–20 uploads, not the lifetime average, because a lifetime average "can make everything look like an outlier". Ratio beats raw views: a 25x video on a small channel outranks a 1.25x video on a large one (published 24 Oct 2026, vendor) — [1of10, Outlier Method](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/)
- OverseerOS uses the median of the 10 most recent long-form uploads, each at least 30 days old, as the baseline. It separates Shorts from long-form and says to wait at least 30 days before comparing a video (published 19 Sep 2026, vendor) — [OverseerOS, The YouTube Outlier Trap](https://www.overseeros.com/blog/youtube-outlier-trap)
- vidIQ's Outlier score compares views with "the average performance of other videos on the same channel" within "a similar timeframe", but does not state the window length. Its colour bands are <2x black, 2–5x blue, 5–10x purple, >10x red. Its filters include views per hour, video length, subscribers and publish date (undated help article, vendor) — [vidIQ Help: Outliers](https://intercom.help/vidiq/en/articles/9660010-outliers)

**Velocity (age-normalised)**
- 1of10 calls velocity, for example 3x the channel's usual seven-day count, "the freshest signal". It recommends weighting the last 6–12 months and sorting by Recent, not Popular, because "Popular favors old videos and channel growth" — [1of10, Outlier Method](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/)
- vidIQ exposes "views per hour" as a filter, with 500+ as its example — [vidIQ Help](https://intercom.help/vidiq/en/articles/9660010-outliers)

**Views/subscriber ratio**
- TubeLab filters for channels with roughly "2X more views vs the acquired audience" (views ≈ 2× subscribers) and uses total views ÷ total subscribers. No cutoff is given beyond about 2x (undated guide; meta says 2025; vendor) — [TubeLab, How to find rising YouTube niches](https://tubelab.net/guides/rising-niches)

**Rising niche = several new channels winning**
- TubeLab: multiple new channels doing well in one topic is "a strong indicator of a rising niche". It gives no number for "multiple" — [TubeLab](https://tubelab.net/guides/rising-niches)
- 1of10: outliers on one channel may be luck or an existing audience. "Two or three outliers on the same topic across different channels" suggest the algorithm favours that content. If nobody else has covered the topic yet, that is an entry window (published 10 Jun 2026, modified 6 Oct 2026, vendor) — [1of10, How to find viral YouTube videos](https://1of10.com/blog/how-to-find-viral-youtube-videos/)
- NexLev markets "recently added outlier channels", "realtime 48-hour views per channel", "Viral Videos" on small channels over the past 30/60/90 days, "Faceless Outliers" and "Future Competition". The public page discloses no thresholds or scoring logic — [NexLev Niche Finder](https://www.nexlev.io/niche-finder)

**Upload-to-breakout and trend window**
- 1of10: an outlier typically leads to a visible trend "two to four weeks later". Outlier momentum lasts "two to six weeks before the topic becomes saturated". It recommends scanning weekly across about 10–15 channels, at 2–4 hours per manual session — [1of10, How to find viral YouTube videos](https://1of10.com/blog/how-to-find-viral-youtube-videos/)

**How common outliers are (calibrates thresholds)**
- In 625 channels, the top video vs the recent-10 median was:
  - median 37.6x, 25th percentile 11.7x, 75th percentile 165.1x;
  - 92.0% of channels had a top video ≥5x and 77.6% had one ≥10x;
  - within the recent 10 only, the peak was a median 3.79x and 21.4% of channels reached 10x+.

  — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)

### Inferences
- **INFERRED.** Because 92% of channels own a ≥5x video somewhere in their history, "this channel has a 5x video" is close to meaningless. The useful signal is a ≥3–5x video *inside the recent 10–20 uploads*, and appearing on *several independent channels*. The base rate inside the recent 10 is lower (median peak 3.79x), so a recent ≥5x is more informative.
- **INFERRED.** Tube Atlas's "Avg Views per Day" is lifetime views ÷ age. That is not velocity in the 1of10 sense (first-7-day views vs the channel's usual first 7 days). Views decay over time, so a 400-day-old video's views/day is structurally lower than a 10-day-old video's. Only compare views/day within age buckets (0–30, 31–90, 91–365 days), or take two dated snapshots and use Δviews/Δdays. See `data_standards.md` for the decay discussion.
- **INFERRED.** The 2–6-week momentum window means the "exploding" layer suits the topic/episode level (what to make next). It cannot by itself justify committing a whole channel.

### Gaps
- No source gives a standard number of breakout channels (for example "≥3" or "≥5") or a standard channel-age cutoff (<6 or <12 months) for a "rising niche". TubeLab says "multiple" and 1of10 says "two or three outliers across different channels". The commonly quoted "≥3–5 new channels under 6 months" rule has no traceable primary source.
- NexLev's actual filter values are behind a paywall and not disclosed publicly.
- ViewStats (MrBeast's tool) methodology: I found no public primary documentation in this session.
- No source measured how upload-to-breakout time differs by format. The 2–4 week figure is one vendor's statement with no dataset shown.

---

## Signals for "DURABLE": multiple independent winners, repeatable formats, evergreen demand/seasonality, back-catalogue still earning, long-form, RPM/advertiser demand, low policy/IP/reuse risk

### Takeaway
Durability is shown by three things together:
- **Repeatability:** the same channel breaks out again on the same topic family, and so do other channels.
- **Persistence:** older channels and older videos still get views, and search or Trends interest is steady rather than spiking.
- **Monetisability:** the category's RPM, a non-kids audience, and a format that passes YouTube's inauthentic and reused content rules.

### Cited Findings
**Repeatability**
- Across 241 channels and 4,820 videos, channels with 0, 1 and 2+ prior 3x breakouts produced another 3x+ breakout in their next 10 videos at 50.0%, 63.2% and 77.1%. For ≥5x the rates were 23.3%, 32.4% and 56.6% (observational, vendor data) — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)
- Topic continuations confirmed by title became another 3x breakout 37.8% of the time (n=37), vs 15.9% for other follow-ups (n=353). Small n — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)
- Paddy Galloway, via Colin & Samir: proven formats ("$1 vs $100", "10 minutes vs 24 hours", superlatives, matchups) can be adapted across niches, and a working format should be run "until they stop you". The page shows "9 April" with no year — [Colin & Samir: The New Rules of YouTube from Paddy Galloway](https://www.colinandsamir.com/resources/the-new-rules-of-youtube-from-paddy-galloway)

**Persistence and evergreen demand**
- TubeLab's durability tests: check whether older channels still perform, whether older videos still get views, and whether Google Trends shows a sustained rather than spiking trend. "Attention bubbles … tend to burst quickly". Filter videos to the last year, because videos about 2 years old may reflect past demand only — [TubeLab](https://tubelab.net/guides/rising-niches)
- OverseerOS: median top-video age is about 410 days, and only 13.9% of channels have their all-time top video among the recent 10. Old winners keep dominating, so the "is the old winner still relevant now?" check is needed — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)
- OutlierKit compared monthly search volume with breakout hit rate across six niches and found that "search volume did not track breakout rate". The data is a single-day snapshot that cannot show growth or decline (19 Aug 2026, vendor) — [OutlierKit Trending Niches Report](https://outlierkit.com/resources/youtube-trending-niches-report/)

**Monetisation and category RPM**
- AIR Media-Tech, from real Studio data on 300 channels (3,595 monetised channel-months, May 2025–May 2026), gives these median RPMs:

  | Niche | Median RPM |
  |---|---|
  | Education & Science | $10.22 (P25–P75 $2.31–$19.50) |
  | Lifestyle | $2.98 |
  | Entertainment | $2.43 |
  | Music | $2.28 |
  | Gaming | $2.05 |
  | Business & Finance | $2.01 (n=3, directional) |
  | Health & Sport | $1.23 |
  | Kids & Teens | $0.33 (P25–P75 $0.16–$0.88) |

  The source warns that top and bottom channels in a niche differ several-fold (published 1 Jul 2026; vendor sells audits) — [AIR Media-Tech RPM by niche 2026](https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm)
- TubeLab says to avoid topics that are hard to monetise, such as "100% AI stories, compilations, and heavy third-party material" — [TubeLab](https://tubelab.net/guides/rising-niches)

**Sustainability**
- OutlierKit: use hit rate to rule topics out, not to pick one. Judge the sub-format rather than the category label, and pair the decision with what you can sustain for about a year — [OutlierKit Trending Niches Report](https://outlierkit.com/resources/youtube-trending-niches-report/)

### Inferences
- **INFERRED.** The strongest durability evidence available from public data has three parts:
  1. ≥2 independent channels, each with ≥2 breakouts in the same topic family. Repeat breakouts predict more breakouts in OverseerOS's data.
  2. Videos older than 12 months still accruing views between two dated snapshots.
  3. A Trends line that is flat or rising, with recurring seasonal peaks rather than a single spike.
- **INFERRED.** "Long-form watch time" cannot be observed in any public scraper. Video Length is only a proxy for the format, not for retention. Real retention needs the owner's own YouTube Analytics after upload.
- **INFERRED.** Category RPM is a prior, not a forecast. The P25–P75 spread within Education ($2.31–$19.50) is wider than the gap between most category medians, so audience geography and format matter as much as category.

### Gaps
- No source quantified a Trends slope threshold for "evergreen" (for example, "≤X% decline over 5 years"). Tube Atlas Trends covers only 12 months (OWNER), which cannot separate seasonality from decline. A 5-year Google Trends view is needed, from another tool.
- Advertiser demand per topic (as opposed to category) was not measurable from public sources here. Keywords Everywhere CPC (OWNER: optional in Tube Atlas) is Google Search CPC, not YouTube ad CPM. That proxy is unverified.

---

## Concrete thresholds practitioners use, and how to avoid survivorship bias

### Takeaway
The published thresholds cluster around:
- **Outlier multiple:** ≥3x worth a look, ≥5x worth studying, ≥10x strong.
- **Baseline:** the last 10–20 uploads (median preferred), each ≥30 days old.
- **Recency:** the last 6–12 months.
- **Views/subs:** about 2x.
- **Channel floor:** about 1,000 subscribers.

The subscriber floor matters a lot. Without it, tiny channels produce huge "outlier" ratios that are "arithmetic, not evidence". Survivorship bias is reduced by the same-channel failure test and by sampling channels that tried and failed.

### Cited Findings
**Published thresholds**

| Item | Threshold | Source |
|---|---|---|
| Outlier multiple | 3x "worth a look"; ≥5x "worth studying" | [1of10](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/) |
| Outlier multiple | 3x noting, 5x strong | [1of10 viral](https://1of10.com/blog/how-to-find-viral-youtube-videos/) |
| Outlier multiple | 3x breakout; 5x/10x stronger tiers | [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap) |
| Outlier multiple | 2/5/10x colour bands | [vidIQ](https://intercom.help/vidiq/en/articles/9660010-outliers) |
| Outlier multiple | about 5–15x, as described of Galloway by OutlierKit (outside analysis, not Galloway's words) | [OutlierKit on Galloway](https://outlierkit.com/resources/paddy-galloway-growth-strategy/) |
| Pre-filming validation | at least one ≥5x outlier on the topic in the last 12 months | [1of10](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/) |
| Benchmark channels | 1–3 size tiers above yours (5k subs → 50k–500k); 30–50+ uploads in the last 6–12 months | [1of10](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/) |
| Baseline | median of the recent 10 long-form uploads, ≥30 days old | [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap) |
| Baseline | 10–20 recent uploads, average | [1of10](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/) |
| Recency | ≥1 year filter; views/subs about 2x; "1 in 10" top videos per channel; 10–20 candidate topics before choosing | [TubeLab](https://tubelab.net/guides/rising-niches) |

**Survivorship bias and small-channel inflation**
- In OutlierKit's sleep/ambient audit:
  - 19 of 120 videos hit ≥10x (15.8%), but 11 of the 19 (58%) came from channels under 1,000 subscribers;
  - a 1,000-subscriber floor cut the rate to 6.7%;
  - extreme cases were a 7-subscriber channel at 12,792x and an 18-subscriber channel at 251x.

  The author calls 1,000 subs "a judgment call" matching the YPP threshold (20 Aug 2026, vendor) — [OutlierKit Sleep & Ambient Audit](https://outlierkit.com/resources/sleep-ambient-niche-audit/)
- OverseerOS's "same-channel failure test": one of four "Why AI Will Replace X" videos hit 8x and the others sat near baseline, so the title formula is not proven. It also says "Never confuse an extreme result with a repeatable strategy" and asks "Did similar attempts also fail?" — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)
- OutlierKit lists saturation signals:
  - a few channels taking most of the attention;
  - the same few channels winning most breakouts;
  - near-identical channel names suggesting a cloned format.

  — [OutlierKit Sleep & Ambient Audit](https://outlierkit.com/resources/sleep-ambient-niche-audit/)
- OutlierKit found that niches usually called "opportunities" scored worst: the faceless/cash-cow niche had a 3.1% hit rate, and all its winners were under 2,500 subs. The niches called "saturated" (personal finance 16.7%, true crime 12.5%, cooking 11.7%) scored best. The samples are small: 3–20 qualifying videos per niche, six queries, one day — [OutlierKit Trending Niches Report](https://outlierkit.com/resources/youtube-trending-niches-report/)

### Inferences
- **INFERRED.** A defensible house rule from these sources:
  - **Baseline:** the median of the last 10–20 long-form uploads aged ≥30 days.
  - **Outlier:** ≥3x is a candidate, ≥5x is a signal, ≥10x is strong.
  - **Floors:** count only channels with ≥1,000 subs and ≥10 uploads in the window.
  - **Rising niche:** ≥3 distinct such channels, each with ≥1 recent ≥5x video in the same topic family, where at least 1–2 of those channels are under 12 months old.
  - **Durable:** at least 2 channels with ≥2 breakouts each.

  These cutoffs are my synthesis. No single source publishes this combination.
- **INFERRED.** To sample failures, run the same keyword with a date-sorted, recent-upload slice, then analyse the channels that posted in that topic and did not break out. The hit rate is breakout channels ÷ all channels that tried, not breakouts ÷ breakouts. Keyword search over-samples winners, as covered in `data_standards.md`.

### Gaps
- No source reported a hit rate *per channel that entered the niche* (the true denominator for "chance a new entrant succeeds"). All published hit rates are per video fetched by search.
- I found no published "views/sub ≥ X" cutoff other than TubeLab's about 2x.

---

## Named methods: 1of10 outlier method, TubeLab/NexLev niche finders, Paddy Galloway, ViewStats, "copy the format not the content", niche-bending

### Takeaway
All the named methods share one core: find channel-relative outliers, isolate *why* each worked, then reuse the structure with your own topic or angle. The Galloway-attributed contributions are format portability (move proven frameworks into new niches) and packaging-first effort. "Niche-bending" in his usage means content recognisable in the niche with a twist, or packaging broadened beyond the core niche.

### Cited Findings
**1of10**
- The rule is "Copy the structure, never the execution", with three moves:
  1. same format with a new topic;
  2. same topic from your own perspective;
  3. one outlier's format filled with another outlier's topic.

  The originality test asks whether a viewer of the original would still learn or feel something new. If not, "it is a cover version". Thumbnails reuse the structural signal (one face, one number), not the look. 1of10 also says to keep benchmarks in the same category, language and market — [1of10](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/)

**TubeLab**
- The model moves from whitespace (supply < demand) to breakeven to saturation, and you start "on the whitespace". The workflow:
  1. use the Breakout Channels filter;
  2. bookmark channels and open similar channels;
  3. build 10–20 candidate topics;
  4. analyse formats, hooks and production cost;
  5. choose by skill fit and profitability.

  TubeLab also says "any topic is breakable" with enough quality — [TubeLab](https://tubelab.net/guides/rising-niches)

**NexLev**
- Positioned as finding niches "before they get saturated". It monitors channels continuously but discloses no criteria — [NexLev](https://www.nexlev.io/niche-finder)

**Paddy Galloway (via Colin & Samir)**
- Win the click first: small creators spend about 95% of their time filming and editing, while top creators spend about 30% on ideation and packaging.
- Make content recognisable in the niche plus a twist.
- Broadened packaging took Andrew Millison's permaculture Sahara video past 15M views.
- Keep about 80% audience overlap and reserve about 20% for experiments.
- Borrow comparison frameworks from other niches.

— [Colin & Samir](https://www.colinandsamir.com/resources/the-new-rules-of-youtube-from-paddy-galloway)

- **Attribution caution:** OutlierKit's "Galloway method" (ignore averages, find 5–15x outliers, isolate variables, build on them) is explicitly "an outside analysis" of his public videos, not his own words (10 Jul 2026) — [OutlierKit](https://outlierkit.com/resources/paddy-galloway-growth-strategy/)

**OverseerOS**
- Signal separation asks whether success came from topic, packaging, format, timing or the creator. Its cross-channel test asks whether related channels show outliers on the same demand — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)

### Inferences
- **INFERRED.** For CineFactory's original-IP rule, 1of10's moves 1 and 3 (structure plus new topic, or recombining two outliers) are the compliant ones. Copying a competitor's characters or world is excluded by both the CLAUDE.md hard rules and YouTube's reused/inauthentic policies.

### Gaps
- ViewStats: no primary methodology page found this session.
- Paddy Galloway's own written niche-selection method: the Colin & Samir page says it contains none. I found no first-party Galloway article on niche selection, only interviews and threads (Thread Reader links appeared in search but were not fetched).
- "Niche-bending" as a formal named method has no canonical primary source found. It appears in vendor landing pages (for example niche-bender-landing.pages.dev, not fetched or assessed).

---

## Pitfalls: chasing one viral video, kids/Made-for-Kids, IP-based niches, saturated AI-slop niches, inauthentic-content policy (July 2026)

### Takeaway
The two biggest traps are:
- copying a single extreme result;
- picking a niche whose content format is itself the policy risk, meaning templated or AI mass-produced work, reused or compiled third-party material, or made-for-kids audiences.

YouTube's 16 July 2026 update relabelled and clarified, but did not change, the rule that cookie-cutter, template-made or emotionally manipulative channels cannot monetise. Made-for-kids status removes personalised ads and most engagement features.

### Cited Findings
**Policy text and the July 2026 update**
- The YPP policy (last updated 15 Jul 2025) renamed "repetitious" content to "inauthentic content":
  - **Not allowed:** content that "looks like it's made with a template" or feels repetitive after several videos from one channel; image slideshows or scrolling text with minimal narrative; AI-generated content from generic templates lacking the creator's perspective.
  - **Allowed:** recurring intros and outros, and series with distinct storylines.
  - **Reused content:** clips strung together without narrative, content already uploaded by others, and song collections are not allowed even with permission. This applies channel-wide.

  — [YouTube Help: YPP monetization policies](https://support.google.com/youtube/answer/1311392)
- The July 2026 update (rollout 16 Jul 2026 per TechCrunch) splits inauthentic content into three non-monetisable types:
  1. generic or repetitive, including "characters put in the same situation over and over again with the same outcome";
  2. unsatisfying or off-putting: "emotionally manipulative formulas", shock for views, stitched clips without progression;
  3. AI personas presenting as human experts on health, legal, finance or politics.

  Tubefilter calls this a communications update with no new demonetisation grounds — [Tubefilter, 13 Jul 2026](https://www.tubefilter.com/2026-07-13/youtube-inauthentic-content-monetization-policy-update/); [TechCrunch, 20 Jul 2026](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)
- YouTube trust and safety chief Matt Halprin: AI-assisted volume is fine if high quality ("you can create a higher volume of high-quality content that we want to encourage and have in YPP"). Content farming means videos that exist "solely to generate revenue". No numeric threshold was given — [TechCrunch](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)

**Made for kids**
- Features unavailable on made-for-kids videos include:
  - personalised ads, comments, cards and end screens;
  - the notification bell, miniplayer, and save to playlist/Watch Later;
  - channel memberships, Super Chat, merch, and home-page autoplay.

  — [YouTube Help: features not available on made for kids](https://support.google.com/youtube/answer/9527654)
- Made-for-kids videos "are more likely to be recommended alongside other kids' videos". Mis-setting has COPPA legal consequences — [YouTube Help](https://support.google.com/youtube/answer/9684541)
- Kids & Teens median RPM is $0.33, against Gaming at $2.05 and Entertainment at $2.43 — [AIR Media-Tech](https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm)

**Chasing one viral video**
- "A 1.5x video with 3M views is weaker than a 20x video with 500K views". Treat a viral video as a hypothesis, because public counts cannot show which ingredient caused it — [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)

**Saturated "faceless/AI" niches**
- The faceless/cash-cow category had a 3.1% hit rate, and all its winners were under 2,500 subs, mostly content *about* making money with faceless channels — [OutlierKit](https://outlierkit.com/resources/youtube-trending-niches-report/)
- TubeLab names "100% AI stories, compilations, heavy third-party material" as hard to monetise — [TubeLab](https://tubelab.net/guides/rising-niches)

### Inferences
- **INFERRED.** The July 2026 example "characters put in the same situation over and over again with the same outcome" bears directly on animated series niches, including Long Slide game and Bell & Leaf. Each episode needs a distinct storyline, focus or concept, which the YPP text explicitly allows for series. This is a format-design requirement, not a niche-selection veto.
- **INFERRED.** IP-based niches (fan content built on someone else's characters or world) carry two independent risks: copyright claims, and the reused/inauthentic monetisation rules. CLAUDE.md already bans them for CineFactory. No public scrape column detects IP risk; it needs a human read of titles and thumbnails.
- **INFERRED.** Kids-appeal animation niches can look "exploding" on views while earning roughly 1/6–1/7 of Gaming or Entertainment RPM by median. That is the gap between $0.33 and $2.05–$2.43 in AIR's data. They also lose comments, so the Comments analyzer returns nothing. Gate them on the owner's revenue target, not on views.

### Gaps
- YouTube publishes no numeric threshold for "too much" templated content per channel.
- The current YouTube Help page text after the 16 Jul 2026 rollout was not fetched. The 1311392 page I fetched shows "last updated 15 Jul 2025", so the 2026 three-category wording is sourced from press (Tubefilter, TechCrunch), not the Help page itself.

---

## Translation: each signal → Tube Atlas v1.0.6.7 column/feature + spreadsheet formula (or "needs API / other tool")

### Takeaway
Every signal except four can be computed in a spreadsheet from Tube Atlas exports: the Videos grid plus Channels → "analyze all videos in channel". The four that cannot are retention/watch time, real RPM, the Made-for-Kids flag, and 5-year seasonality.

The key manual step is building each channel's baseline. Tube Atlas has no outlier score and no channel-age column in the Videos grid (OWNER). So each candidate channel's full video list must be exported, and the channel's median joined back onto the keyword sample. A second dated export 7–30 days later turns lifetime averages into real velocity and back-catalogue growth.

### Cited Findings
- **OWNER.** Tube Atlas v1.0.6.7 provides the following. I did not verify these publicly.
  - **Videos grid columns:** Views, Likes, Comments, Video Length in Seconds, Date Published, Published Age (Days), Avg Views per Day, Est. Earnings (flat $1.85 RPM), Category, Subtitles, Is Shorts, Channel Name/Link, Total Channel Subscribers, Tags, Title.
  - **Channels tab:** total views, total videos, subscribers, Date Joined, analyze-all-videos.
  - **Other features:** Keywords (autosuggest plus optional Keywords Everywhere volume), Trends (12 months, 258 countries), Get Related Videos, Comments analyzer, and Tag/Title analyzers.
- The baseline must be recent (10–20 uploads) and median-based, with each video ≥30 days old and Shorts separated — [1of10](https://1of10.com/blog/viral-youtube-video-ideas-outlier-method/); [OverseerOS](https://www.overseeros.com/blog/youtube-outlier-trap)
- Apply a 1,000-subscriber floor — [OutlierKit](https://outlierkit.com/resources/sleep-ambient-niche-audit/)
- Use channel category RPM medians as the RPM prior — [AIR Media-Tech](https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm)

### Inferences
**Signal map (INFERRED, built from the cited methods above)**

| Signal | Tube Atlas source | Spreadsheet formula / rule | Status |
|---|---|---|---|
| Channel baseline | Channels → analyze all videos (per candidate channel) → Views, Date Published, Is Shorts | `baseline = MEDIAN(Views)` of the 10–20 most recent long-form videos with Published Age ≥30 | Doable (manual, per channel) |
| Outlier multiple | Videos grid Views + joined baseline | `outlier = Views / baseline`; flag 3x / 5x / 10x | Doable |
| Subscriber floor | Total Channel Subscribers | Exclude <1,000 (also report the result with no floor, as a sensitivity check) | Doable |
| Views/sub | Views ÷ Total Channel Subscribers (video); channel total views ÷ subscribers (Channels tab) | About ≥2x at channel level (TubeLab) | Doable. Subscriber counts are rounded publicly (see `data_standards.md`) |
| Age-normalised velocity | Avg Views per Day, Published Age (Days) | Compare only within age buckets 0–30 / 31–90 / 91–365. True velocity = (Views_t2 − Views_t1)/(t2 − t1) from two dated exports | Partial. A single export gives a lifetime average only |
| First-7-day vs channel norm | — | Needs daily snapshots, or the YouTube Data API polled from upload | Needs API or repeated scrapes |
| Channel age | Channels tab Date Joined (not in the Videos grid) | VLOOKUP onto video rows. Better: `first_upload = MIN(Date Published)` from analyze-all-videos, because old accounts get repurposed | Doable via join |
| New channels breaking out | Derived | `COUNTIFS` distinct channels: first_upload ≤365 days, subs ≥1,000, ≥1 recent video ≥5x, same topic family. Rising if ≥3 (house rule) | Doable |
| Upload-to-breakout time | Date Published of the first ≥5x video − first_upload | Days from the channel's first upload to its first breakout | Doable (approximate, because the outlier is measured at scrape time) |
| Repeatability | Per-channel outlier list | Count of ≥3x videos in the recent 20 per channel. Durable if ≥2 channels have ≥2 each | Doable |
| Failure sample | Keyword search sorted by upload date (if Tube Atlas supports it), plus Get Related Videos | Hit rate = breakout channels ÷ all channels that posted on the topic in the window | Doable if a date-sorted search exists. Otherwise needs API `search.list order=date` |
| Back-catalogue still growing | Two dated exports of analyze-all-videos | Δviews on videos >365 days old; share of channel views/day from videos >365 days old | Doable with two snapshots, 7–30 days apart |
| Evergreen demand / seasonality | Trends (12 months), Keywords volume | 12-month slope plus visible repeat peaks. Spiky with a single peak = fad | Partial. 5-year seasonality needs Google Trends directly |
| Long-form / watch time | Video Length in Seconds, Is Shorts | Share of winners ≥8–10 minutes as a format proxy only | Retention needs the owner's own YouTube Analytics |
| RPM / advertiser demand | Category (Est. Earnings ignored: flat $1.85) | Map Category to AIR median RPM as a prior. Keywords Everywhere CPC is only a web-search proxy | Real RPM needs owner Analytics or partner data |
| Made-for-Kids | Comments (zero/disabled is a hint), Category | Comments = 0 on high-view videos suggests MFK. Verify per video | Needs YouTube Data API `status.madeForKids`. The field name is from my prior knowledge, not verified this session |
| Templated / AI-slop risk | Title analyzer, Tags, thumbnails (open the links) | Near-identical title templates across a channel; same-situation/same-outcome plots; clone channel names | Human review |
| Reused / IP risk | Title, Tags, Channel Name | Mentions of other franchises, "compilation", movie/show names | Human review |
| Audience demand / complaints | Comments analyzer | Recurring requests ("do X next") plus complaints that are format gaps | Doable |
| Engagement sanity | Likes, Comments ÷ Views | Compare within the niche only | Doable. Note the 24 Aug 2026 view definition change |

**Step order (INFERRED)**
1. **Seed.** Use Keywords plus Trends to list 10–20 candidate topic families (TubeLab's shortlist size). Discard any where Trends is a single spike.
2. **Sample.** For each topic, keyword-search long-form and Shorts separately and export the Videos grid. Also pull a recent-upload slice for failures.
3. **Shortlist channels.** Take the 20–40 distinct channels in the sample with ≥1,000 subs. Run Channels → analyze all videos for each and export. This is the slow, rate-limited step.
4. **Compute.** Calculate baseline, outlier multiple, first upload, breakouts per channel, and new-channel breakout count.
5. **Classify the topic.** EXPLODING if ≥3 new (≤12 months) channels have a recent ≥5x video. DURABLE if ≥2 channels have ≥2 breakouts, old videos still grow between snapshots, and Trends is flat or rising. Prefer topics that are both.
6. **Screen.** Apply the policy, kids, IP/reuse and RPM screens by human review plus the category RPM prior.
7. **Re-scrape.** Repeat after 7 and 30 days to confirm velocity and back-catalogue growth before committing a channel. Store dated CSVs.
8. **Log.** Record the decision with `tools/cf_decision.py` per CLAUDE.md. Label every number OBSERVED/INFERRED.

- **INFERRED.** `tools/cf_research_stats.py` already computes "medians, outliers, views/day from saved research rows" (per CLAUDE.md). It is the natural place to run steps 4–5 on Tube Atlas CSV exports, instead of hand-built spreadsheet formulas. Its fit was not measured; the tool was not run in this session.

### Gaps
- Not verified this session:
  - whether Tube Atlas keyword search can sort or filter by upload date;
  - whether Trends reflects YouTube search or web search interest;
  - whether "Avg Views per Day" equals Views ÷ Published Age.

  The owner should check these in-app.
- The `status.madeForKids` API field was not verified against current API docs in this session.
- The house-rule cutoffs above (≥3 new channels, ≤12 months, ≥2 repeat breakouts) are synthesised. They need calibration against the owner's own past niche scans before they are treated as standards.
