# Rising / fastest-growing YouTube trackers — very new, very large Shorts channels (US/EU), read 2026-11-13

Scope: Shorts channels created ~2026-10-14 or later (ideal: after 2026-10-29) with 100M+ views, channel country or audience in US / Europe / CA / AU.
All figures are what the tracker page showed (OBSERVED via tracker, not verified against the YouTube API). "As of" = the tracker's own "Last updated" date; all pages read 2026-11-13.
Method: read-only public pages, no login, no API key. Direct fetches of socialblade.com, playboard.co and tubefilter.com from this machine were blocked by the egress proxy (HTTP 403 connect_rejected) and WebFetch permission timed out; pages were read through a cached/live web-extraction service instead.

## Which public trackers list newly created or fastest-growing channels, and what can be read without logging in?

### Takeaway
vidIQ's free "YouTube Stats" rankings are the most useful public source: they have worldwide and per-country (US, GB, DE, FR, ES, IT, NL, PL, SE, CA, AU, …) "fastest growing (30 days)" and "trending (views gained)" lists, and each channel page shows the exact **Joined** date and **channel country** without login. No tracker found has a true "recently created channels" list filterable by creation date; new channels have to be inferred from rows where *subs gained ≈ total subs* and then confirmed on the channel page.

### Cited Findings
- vidIQ worldwide fastest-growing: top 100 by subscribers gained over "roughly the last 30 days", refreshed daily; "A channel created during the period can count from an inferred zero"; channels vidIQ has no start count for are left out — [vidIQ fastest-growing](https://vidiq.com/youtube-stats/top/fastest-growing-youtube-channels/)
- vidIQ has per-country lists (Most subscribed / Most viewed / Fastest growing / Trending) for US and others; the country lists cover "channels whose country on YouTube is [country]" — [vidIQ US](https://vidiq.com/youtube-stats/top/country/us/); [vidIQ Spain fastest growing](https://vidiq.com/youtube-stats/top/country/es/fastest-growing-youtube-channels)
- vidIQ trending list ranks channels by views gained over ~30 days (e.g., T-Series +4.17B) — [vidIQ trending](https://vidiq.com/youtube-stats/top/trending-youtube-channels/)
- vidIQ channel pages publicly show "N videos Joined <date>", subscribers, total views, country rank and "channel country set to …"; daily history beyond ~14 days and some rows are gated behind "View 16 more days – Sign up free" — e.g. [vidIQ Tiny Tantrums](https://vidiq.com/youtube-stats/channel/@tiny-tantrums/), [vidIQ Top 10s Shorts](https://vidiq.com/youtube-stats/channel/@top10sshorts/)
- Tubefilter publishes weekly Global Top 50 Most Subscribed and Most Viewed charts (data from Gospel Stats) with channel IDs and all-time views/subs; it notes how many of the Top 50 are Shorts-first (37 of 50 for Nov 2–8, 2026); no creation date or country filter — [Tubefilter subs 11/08/2026](https://www.tubefilter.com/?p=195099); [Tubefilter views 11/08/2026](https://www.tubefilter.com/?p=195098)
- NoxInfluencer has a public "Top 100 Most Growing YouTubers" (weekly, updated 2026-11-07) with channel IDs, subscribers and 30-day views; no creation date shown in the list — [NoxInfluencer growth](https://www.noxinfluencer.com/youtube-channel-rank/top-100-all-all-youtuber-sorted-by-growth-weekly)
- Social Blade top lists are public (e.g., Top 100 US by subscribers with subs/views/videos), but the cached copy available was from 2026-08-22 and showed no "recently created" filter; live pages could not be reached from this environment — [Social Blade Top 100 US](https://socialblade.com/youtube/lists/top/100/subscribers/all/US)
- Playboard has public chart pages with country, Daily/Weekly/Monthly period and date pickers, and marks entries "NEW" (e.g., Kai ASMR, Slicora ASMR new in Sep 2026 worldwide monthly "most popular"); the specific "most-subscribed … daily" URLs tried returned 404 — [Playboard most popular monthly](https://playboard.co/en/youtube-ranking/most-popular-all-channels-in-worldwide-monthly); [Playboard Shorts KR daily](https://playboard.co/en/chart/short/most-viewed-all-videos-in-south-korea-daily)
- Vuela "viral AI Shorts" study (weekly) lists breakout AI Shorts with channel age, but only for channels under 30K subscribers, found via YouTube search on AI topics — [Vuela](https://vuela.ai/data-studies/viral-ai-shorts)
- Subsrank "fastest growing" list is not usable: it shows impossible values such as @wildclov3r at 2,000,000,000 subscribers and +19,175,157% gains — [Subsrank](https://subsrank.com/rankings/growing)
- FindAChannel "Rising Stars" lists only channels with 1,000–25,000 subscribers started in the last 3 years — [FindAChannel](https://www.findachannel.net/Home/RisingStars)
- TunePocket has public Top 100 / Trending / Fastest Growing lists measured over 7 days (top-100-scale channels only) — [TunePocket](https://www.tunepocket.com/youtube-top-100)

### Inferences
- The practical public workflow is: vidIQ country "fastest growing" list → flag rows where subs gained ≈ total subs (or where the observation start is "unavailable") → open the vidIQ channel page for the Joined date and country. That is how the candidates below were found.
- "Subs gained = total subs" does not prove the channel is new; it can mean vidIQ only began tracking it (e.g., Di @di0403daily joined 2022, The Waterfowl Sanctuary joined 2024). The Joined date must be checked.
- Country lists use the self-declared YouTube channel country, which does not prove a US/EU audience (e.g., a Chinese-language GTA6 channel is listed under the United States).

### Gaps
- HypeAuditor, Kolsquare, Favikon, ViewStats, NoxInfluencer "rising" and Social Blade "recently created/top new" pages were not reached or not checked within the time box; whether they offer a creation-date filter without login is not measured.
- Playboard "rising"/"most subscribed by country" correct URLs not found; the two guessed URLs returned 404.
- Social Blade live data (blocked from this environment) — not measured.

## Which channels created in Oct–Nov 2026 have 100M+ views in US/EU/CA/AU?

### Takeaway
Five Shorts channels created **2026-10-08 to 2026-10-17** were found with 100M+ views and a US, CA or ES channel country; the largest, **GTA6-罪恶都市** (US channel country, joined 2026-10-14), shows **1,074,677,282 views** after ~30 days. No channel created after 2026-10-29 with 100M+ views was found in any tracker.

### Cited Findings
Candidates in the window (joined 2026-10-08 or later), figures as the vidIQ channel page showed:

| Channel | Handle / URL | Joined | Country (YouTube setting) | Subs | Total views | Videos | As of | Niche / format | Source |
|---|---|---|---|---|---|---|---|---|---|
| GTA6-罪恶都市 | @gta6-罪恶都市 — youtube.com/@gta6-罪恶都市 | 2026-10-14 | United States (ranked #26,436 in US) | 543,000 | 1,074,677,282 | 115 | 2026-11-13 | GTA6 gameplay/clip Shorts, Chinese-language titles ("#gta #gta6 #shorts"); top Shorts 85.39M (Oct 16) and 82.09M (Oct 25) | [vidIQ](https://vidiq.com/youtube-stats/channel/@gta6-%E7%BD%AA%E6%81%B6%E9%83%BD%E5%B8%82/); also #60 in [vidIQ US fastest growing](https://vidiq.com/youtube-stats/top/country/us/fastest-growing-youtube-channels/) (+522K, 1.01B views, 86 videos, list updated 2026-11-06) |
| GTA6 | @gta6-w7m | 2026-10-14 | United States | 396,000 | 369,403,425 | 93 | 2026-11-06 | GTA6 Shorts with Chinese titles (e.g., "露西娅变成什么了 #GTA6" 63.78M) | [vidIQ](https://vidiq.com/youtube-stats/channel/@gta6-w7m/) |
| GlowStrike | @glowstrikeshop | 2026-10-08 (36 days; just outside 30) | Canada | 112,000 | 238,592,414 | 46 | 2026-11-04 | Product/gift Shorts ("The BEST Christmas gift!? #boymom #giftforboys") | [vidIQ](https://vidiq.com/youtube-stats/channel/@glowstrikeshop/) |
| Te Cuento Blox | @tecuentoblox | 2026-10-10 | Spain | 165,000 | 147,948,113 | 83 | 2026-11-09 | Spanish Roblox story Shorts ("En este pueblo, solo tienes QUINIENTOS MIL pasos…") | [vidIQ](https://vidiq.com/youtube-stats/channel/@tecuentoblox/) |
| LumaRein | @lumarein | 2026-10-17 | Canada | 105,000 | 139,717,006 | 66 | 2026-11-04 | Horse / riding-gear product Shorts ("Comment 'Horse' if you need this… #gallop #horse #usa", 17.14M) | [vidIQ](https://vidiq.com/youtube-stats/channel/@lumarein/) |

Near-window or under-100M items (for context):
- Magic_की_ दुनियां (@magic_की_दनिया): joined 2026-10-17, 918,000 subs, 51,763,383 views, 15 videos as of 2026-11-06; mini wood-toy Shorts with Hindi titles; country not shown (not US/EU) — [vidIQ](https://vidiq.com/youtube-stats/channel/@magic_%E0%A4%95%E0%A5%80_%E0%A4%A6%E0%A4%A8%E0%A4%BF%E0%A4%AF%E0%A4%BE/)
- Oi Raja (UC8aRG41OZcf-qtWnfo6L9IQ): 868,000 subs, 120,184,468 all-time views, +277,000 subs in Nov 2–8 (+13,750% vs last week); India, ENO-tablet Shorts; creation date not shown — [Tubefilter](https://www.tubefilter.com/?p=195099)
- Zedar Short (UCTxBcuBqoBtX6M6MvjA8Vww): 581,000 subs, 34,981,212 views, +327,000 subs in Nov 2–8; creation date and country not shown — [Tubefilter](https://www.tubefilter.com/?p=195099)

Older channels that look new on growth lists but were created before the window (label: OLDER):
- Haaland - KPOP (@rumi-kpopstory): joined 2026-01-02, US, 729,000 subs, 664,611,175 views, 76 videos (2026-11-07); football "respect" Shorts (90.35M top) — [vidIQ](https://vidiq.com/youtube-stats/channel/@rumi-kpopstory/)
- YamalXeo (@yamalxeo): joined 2026-07-02, India rank, 1,680,000 subs, 1,894,553,410 views, 65 videos (2026-11-12); views went 562.57M (Oct 14) → 1.58B (Oct 29) — [vidIQ](https://vidiq.com/youtube-stats/channel/@yamalxeo/)
- Tiny Tantrums (@tiny-tantrums): joined 2026-08-29, US, 1,040,000 subs, 107,065,810 views, 81 videos (2026-11-03) — [vidIQ](https://vidiq.com/youtube-stats/channel/@tiny-tantrums/)
- Latina Mami (@latinamami-br): joined 2026-07-31, Australia, 114,000 subs, 146,248,684 views (119.83M in 28d), 137 videos (2026-11-10); Spanish family-comedy Shorts — [vidIQ](https://vidiq.com/youtube-stats/channel/@latinamami-br/)
- Foline studio (@folinestudio): joined 2026-07-07, Spain, 188,000 subs, 91,073,119 views, 66 videos (2026-11-04); Roblox animation Shorts — [vidIQ](https://vidiq.com/youtube-stats/channel/@folinestudio/)
- The History Rooster (@roosterhistory): joined 2026-05-26, US, 438,000 subs, 39,634,557 views, 27 videos (2026-11-06); family-drama Shorts — [vidIQ](https://vidiq.com/youtube-stats/channel/@roosterhistory/)
- GoShorts (@goshorts-00): joined 2025-10-11, Netherlands, 35,300 subs, 152,764,089 views of which 149.91M in 28 days, 156 videos (2026-11-12); slime ASMR Shorts — [vidIQ](https://vidiq.com/youtube-stats/channel/@goshorts-00/)
- OddFrame (@oddframefilms67): joined 2025-11-09, Australia, 181,000 subs, 256,487,934 views, 63 videos (2026-11-05); WW2/engineering explainer Shorts — [vidIQ](https://vidiq.com/youtube-stats/channel/@oddframefilms67/)
- The Waterfowl Sanctuary (@thewaterfowlsanctuary): joined 2024-07-01, listed in UK fastest-growing, 243,000 subs, 211,618,475 views (192.51M in 28d), one Short at 102.01M in 5 days (2026-10-31) — [vidIQ](https://vidiq.com/youtube-stats/channel/@thewaterfowlsanctuary/)
- GreenBroRants (@greenbrorants): joined 2025-10-07, US, 1,380,000 subs, 1,115,692,818 views (110.84M on Oct 14 → 702.4M on Oct 29) — [vidIQ](https://vidiq.com/youtube-stats/channel/@greenbrorants/)
- Gelo Stories (@gelostories98) joined 2024-11-07, US, 211.3M views; Di (@di0403daily) joined 2022-11-09, US, 138M views — [vidIQ Gelo](https://vidiq.com/youtube-stats/channel/@gelostories98/); [vidIQ Di](https://vidiq.com/youtube-stats/channel/@di0403daily/)

Country lists checked and their "Last updated" dates (vidIQ fastest growing): US 2026-11-06, GB 2026-11-01, DE 2026-11-06, FR 2026-11-06, ES 2026-11-08, IT 2026-11-09, NL 2026-11-13, PL 2026-11-09, SE 2026-11-11, CA 2026-11-04, AU 2026-11-05 — [vidIQ US](https://vidiq.com/youtube-stats/top/country/us/fastest-growing-youtube-channels/), [GB](https://vidiq.com/youtube-stats/top/country/gb/fastest-growing-youtube-channels/), [DE](https://vidiq.com/youtube-stats/top/country/de/fastest-growing-youtube-channels/), [FR](https://vidiq.com/youtube-stats/top/country/fr/fastest-growing-youtube-channels/), [ES](https://vidiq.com/youtube-stats/top/country/es/fastest-growing-youtube-channels/), [IT](https://vidiq.com/youtube-stats/top/country/it/fastest-growing-youtube-channels/), [NL](https://vidiq.com/youtube-stats/top/country/nl/fastest-growing-youtube-channels/), [PL](https://vidiq.com/youtube-stats/top/country/pl/fastest-growing-youtube-channels/), [SE](https://vidiq.com/youtube-stats/top/country/se/fastest-growing-youtube-channels/), [CA](https://vidiq.com/youtube-stats/top/country/ca/fastest-growing-youtube-channels/), [AU](https://vidiq.com/youtube-stats/top/country/au/fastest-growing-youtube-channels/)
- In the DE, FR, IT, PL, SE and GB lists, no channel with subs gained ≈ total subs had 100M+ views; the largest new-looking rows were below ~35M views (e.g., DE "Unhinged" 33.8M, PL "GrzesiuRoblox" 29.95M, SE "John Ranking" 33.68M) — same vidIQ country pages as above

### Inferences
- The only window channel with 1B+ views (GTA6-罪恶都市) has a US channel-country setting but Chinese-language titles; its real audience region is unknown and may not be US/EU.
- Of the window candidates, the ones whose content clearly targets Western viewers are LumaRein (English, "#usa" horse gear), GlowStrike (English Christmas gifts) and Te Cuento Blox (Spanish Roblox stories, Spain). The two CA product channels look like shoppable/product-promo Shorts rather than original-IP entertainment.
- Speed observed: GTA6-罪恶都市 averaged ~36M views/day over 30 days (1.07B / ~30 days — INFERRED arithmetic); GlowStrike ~8.5M/day over 28 days; LumaRein ~7.4M/day over 19 days.

### Gaps
- Channel IDs (UC…) for the vidIQ candidates were not shown on the pages read; only @handles are recorded. Resolve via the YouTube API (channels.list forHandle) later.
- vidIQ "Last updated" dates for some channels are 2026-11-04 to 2026-11-09, so current totals are higher than shown.
- Audience geography (where viewers are) is not visible on any free tracker; only the self-declared channel country.

## Are there any channels created within ~15 days (on/after ~2026-10-29) with 1B+ views?

### Takeaway
None found. No tracker read showed any channel joined on or after 2026-10-29 with 100M+ views, let alone 1B+. The largest verified figure for a very new US-country channel is GTA6-罪恶都市: joined 2026-10-14 (30 days before 2026-11-13), 1,074,677,282 views as of 2026-11-13.

### Cited Findings
- GTA6-罪恶都市: joined 2026-10-14, 543,000 subs, 1,074,677,282 views, 115 videos, US country rank #26,436, as of 2026-11-13 — [vidIQ](https://vidiq.com/youtube-stats/channel/@gta6-%E7%BD%AA%E6%81%B6%E9%83%BD%E5%B8%82/)
- The youngest 100M+ channel in a US/EU/CA country found is LumaRein, joined 2026-10-17, 139,717,006 views as of 2026-11-04 — [vidIQ](https://vidiq.com/youtube-stats/channel/@lumarein/)
- The youngest large channel in any country found is Magic_की_ दुनियां, joined 2026-10-17, 51.76M views as of 2026-11-06 — [vidIQ](https://vidiq.com/youtube-stats/channel/@magic_%E0%A4%95%E0%A5%80_%E0%A4%A6%E0%A4%A8%E0%A4%BF%E0%A4%AF%E0%A4%BE/)
- Vuela's weekly scan for the week of 2026-11-09 found only 3 breakout AI Shorts from small channels, 2 of them on channels under 3 months old, the largest 17M views (India, @UltiDuniyaAI-c7n) — [Vuela](https://vuela.ai/data-studies/viral-ai-shorts)
- No 2026 news article about a channel exploding to 1B views within ~2 weeks was found in searches; Tubefilter's Nov 2–8 commentary covers ENO-tablet Shorts channels in India (Danka Fun, Oi Raja) — [Tubefilter](https://www.tubefilter.com/?p=195099)

### Inferences
- vidIQ only lists a channel after it has a starting snapshot and enough growth to rank in a top-100, so a channel created after ~2026-10-29 may not appear yet even if large. Absence here is "not found", not "does not exist".
- To catch channels under 15 days old, a re-check of the vidIQ US/CA/GB lists in ~7 days, or the YouTube API search for Shorts with high views and channel publishedAt ≥ 2026-10-29, is needed.

### Gaps
- Social Blade, Playboard, HypeAuditor and ViewStats could not be checked for under-15-day channels from this environment; not measured.
- No verification through the YouTube Data API was done (forbidden by the task); every figure above is tracker-reported.
