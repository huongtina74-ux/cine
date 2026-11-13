# Finding brand-new (≤15 days old) Shorts channels with huge views in the US and Europe: YouTube Data API v3 and free sources (as of 13 Nov 2026)

Research date: 2026-11-13. No API key was used and nothing was called live. All facts come from web search excerpts of Google docs and other pages, dated where possible.
**Access note:** WebFetch of `developers.google.com/youtube/v3/determine_quota_cost`, `/youtube/v3/revision_history` and `/youtube/v3/docs/search/list` was blocked (the permission request timed out). Those pages were read only through search-engine excerpts, which include "Last updated" stamps. Labels follow CLAUDE.md: OBSERVED (seen in a source or file), INFERRED (my reasoning), and "not verified" for anything unconfirmed.

---

## 1. search.list: what order=viewCount + publishedAfter + regionCode + videoDuration=short + relevanceLanguage (no q) does, plus caps, quota and bias

### Takeaway
Since 1 June 2026, search.list has **its own bucket of 100 calls per day, at 1 per call**. The old "100 units out of 10,000" rule no longer applies. Every extra page counts as another call, so a whole day of searching yields at most about 100 pages × 50 = 5,000 results. `regionCode` only means the video **can be viewed in** that country; it says nothing about the creator's country. `videoDuration=short` means under 4 minutes, not "is a Short". Google now warns that ordering by anything other than relevance, **especially together with publishedAfter/publishedBefore**, can return a smaller or incomplete result set. Independent audits find search results randomized, biased toward recent and popular items, and not reproducible. So search.list is a **sampler for finding channel IDs**. It cannot list every qualifying channel.

### Cited Findings
- Quota (OBSERVED, Google, "Last updated 2026-11-12 UTC"): "Projects that enable the YouTube Data API have a default quota allocation of 100 `search.list` calls, 100 `videos.insert` calls, and 10,000 units per day combined for all other endpoints… Daily quotas reset at midnight Pacific Time (PT)." "The `search.list` and `videos.insert` methods have their own quota buckets. Each of these methods has a default daily limit of 100 per day. The quota cost is 1 per call." "…each request to retrieve an additional page of results incurs the estimated quota cost." Table row: "search | list | 100 quota per day. Each call costs 1 quota." "All API requests, including invalid requests, incur a quota cost of at least one point." — [Quota Calculator](https://developers.google.com/youtube/data/determine_quota_cost); same text at [?hl=en, updated 2026-11-10](https://developers.google.com/youtube/data/determine_quota_cost?hl=en) and [Overview](https://developers.google.com/youtube/data/getting-started)
- Timeline (OBSERVED): revision history entry of **1 June 2026**: "The YouTube Data API is transitioning to a granular quota system covering smaller sets of methods, starting with videos.insert and…" — [Revision History](https://developers.google.com/youtube/v3/revision_history). A secondary source states that on 1 June search.list and videos.insert moved to their own buckets, and that "Since 2014 a search had cost 100 units of the shared 10,000" — [Social SDK guide, 9 Nov 2026](https://social-sdk.dev/guides/youtube-data-api); [SociaVault, 30 Oct 2026](https://sociavault.com/blog/youtube-data-api-quota-2026)
- Quota beyond the default needs an audit: "To request quota beyond the default, an audit demonstrating compliance… is required" — [Quota and Compliance Audits, updated 2026-09-14](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits)
- Stale cache warning (OBSERVED): an older cached copy of `/youtube/v3/determine_quota_cost` (2026-10-08) carries an AI "Page Summary" that still says videos.insert costs 1600. That summary is outdated. Upload cost fell from about 1600 to about 100 units on 4 Dec 2025 — [Revision History](https://developers.google.com/youtube/v3/revision_history?authuser=1)
- `regionCode` (OBSERVED): "instructs the API to return search results for videos that **can be viewed in the specified country**" (clarified in a 2016-era revision) — [search.list reference, updated 2026-11-12](https://developers.google.com/youtube/data/reference/rest/v3/search/list); [Revision History](https://developers.google.com/youtube/v3/revision_history?authuser=1)
- `relevanceLanguage` (OBSERVED): "return search results that are **most relevant** to the specified language". It affects ranking and is not a filter — [search.list reference](https://developers.google.com/youtube/data/reference/rest/v3/search/list)
- `videoDuration` (OBSERVED): "**short** – Only include videos that are less than four minutes long"; medium = 4–20 min; long = >20 min — [search.list reference](https://developers.google.com/youtube/v3/docs/search/list)
- `order=viewCount` (OBSERVED, new warning on the 2026-11-12 page): "viewCount – Resources are sorted from highest to lowest number of views… **Important: Specifying a sort order other than relevance might result in a smaller or incomplete result set, particularly when combined with date filters like publishedAfter or publishedBefore.** In addition, using the order parameter can sometimes affect the behavior of the type filter." — [search.list reference](https://developers.google.com/youtube/data/reference/rest/v3/search/list)
- `order=date` (OBSERVED): "Because this relies on the search index, you may experience **indexing delays for new content** or receive incomplete result sets. To reliably retrieve a channel's most recently uploaded videos, do not use search.list. Instead, use the playlistItems.list method…" — [search.list reference](https://developers.google.com/youtube/data/reference/rest/v3/search/list)
- Google confirmed this behaviour back in 2022: "Using 'order' by will filter out results… how the search queries work in the backend which we cannot further elaborate", Won't Fix (Intended Behavior) — [Issue Tracker 245018357](https://issuetracker.google.com/issues/245018357)
- `totalResults` (OBSERVED): "an approximation and may not represent an exact value… maximum value is 1,000,000. You should not use this value to create pagination links" — [search.list reference](https://developers.google.com/youtube/v3/docs/search/list)
- 500 cap (OBSERVED): the docs state the hard cap of "a maximum of 500 videos" only for channelId + type=video requests — [search.list reference](https://developers.google.com/youtube/v3/docs/search/list). A general ~500-per-query ceiling (50/page × ~10 pages) appears in practice and in research — [Efstratiou, IMC 2025](https://arxiv.org/abs/2506.04422) (cited in the earlier project note `research_notes/Tube Atlas cao thủ tìm ngách/data_standards.md`)
- Bias (OBSERVED, peer-reviewed): "the search endpoint returns highly variable results between queries… the API seems to randomize returned videos based on the relative popularity of the respective topic during the query period… the API may prioritize shorter, more popular videos, although the role of channel popularity is not as clear" — [Efstratiou, "On YouTube Search API Use in Research", IMC 2025](https://arxiv.org/abs/2506.04422)
- Bias (OBSERVED, peer-reviewed): weekly searches over six months found limits on "completeness, representativeness, consistency, and bias"; videos drop out of search "within just 20–60 days of publication, even though these videos remain on the platform"; identical queries return different sets; "a very significant recency bias" — [Rieder, Padilla, Coromina, Information, Communication & Society, 24 Nov 2025](https://portalrecerca.uab.cat/en/publications/forgetful-by-design-a-critical-audit-of-youtubes-search-api-for-a); [arXiv](https://arxiv.org/html/2506.11727v2)
- Our own run (OBSERVED, 3 Nov 2026): 84 keyword searches with type=video, regionCode=US, relevanceLanguage=en, order=viewCount, 7 and 15-day windows. 11 of 84 queries returned fewer than 50 results. Audio language was en* 1,037, blank 1,009, hi 205, es 66 and so on, so **regionCode/relevanceLanguage leak heavily** — local file `research_notes/Quét ngách Minecraft bằng YouTube API/api_dataset.md`. The same file counted search at 100 units per call, which was the pre-June-2026 rule. Under current docs those 84 calls used 84 of the 100-call search bucket.
- A new-channel study (OBSERVED, secondary, Japan): "new channels from category new uploads (within 2 days of publication)… the new-upload search **mostly returned existing channels**"; channels found through view-count-sorted search did not survive the new-channel filter — [Zenn, 475 new JP Shorts channels, 3 Nov 2026](https://zenn.dev/acerola_jp/articles/youtube-shorts-new-channel-hit-rate?locale=en)

### Inferences
- INFERRED: a query with no `q` + `order=viewCount` + `publishedAfter=now−15d` + `regionCode=US` + `videoDuration=short` + `type=video` is the most "global" view-sorted request possible. Google's own warning means it may return **fewer** items than requested. It can still be useful, because the very top (100M+ in ≤15 days) is exactly what view-count ordering should surface first. Even so, it will not be exhaustive, and the same request can return a different set each day.
- INFERRED: the top result is dominated by old, big channels. The age filter has to be applied **after** retrieval: collect the channelIds, call channels.list (1 unit per 50 channels), and keep `snippet.publishedAt ≥ now−15d`.
- INFERRED: with only 100 search calls per day, spend them on **variety** (window slices, languages, regionCodes, a few keyword families) rather than deep pagination. Each page is one call. The audits show pages 6–10 add few new items.
- INFERRED: `videoDuration=short` (<4 min) is wider than Shorts (≤3 min since Oct 2024), so landscape clips under 4 minutes also get in. Verify Shorts membership separately (section 3).
- INFERRED: regionCode = "watchable in" means US, GB, DE, FR and similar return heavily overlapping global sets. Use the language/region combinations to vary the ranking, not to filter by market.

### Gaps
- No quoted primary source says whether `q` can be omitted together with order=viewCount in 2026. The parameter is optional in the reference, but I did not re-quote it this session. Test it on the first call tomorrow.
- I found no documentation of a new-channel penalty in search. Efstratiou says the role of channel popularity "is not as clear". Rieder et al. document recency bias, which should *help* fresh videos.
- The exact search.list cap per query in 2026 (500 or less) was not re-measured. Record `nextPageToken` exhaustion tomorrow.

---

## 2. videos.list chart=mostPopular: does it include Shorts in 2026, how many results, what does it cost?

### Takeaway
Since **21 July 2025**, `chart=mostPopular` returns only videos from the **Trending Music, Movies and Gaming** charts, because the general Trending page was removed. It is not a general "most viewed" list and is a poor tool for finding new Shorts channels outside music and gaming. It costs 1 unit per call (videos.list) with up to 50 items per page.

### Cited Findings
- "As of July 21, 2025, YouTube will adjust the content that is returned by the video.list method's mostPopular chart. In the past, the mostPopular chart reflected the videos featured on the Trending Now list. Now, the mostPopular chart will feature videos from the Trending Music, Movies, and Gaming charts. This API change is in tandem with the deprecation of YouTube's Trending page." — [Revision History, 10 Jul 2025](https://developers.google.com/youtube/v3/revision_history?authuser=1)
- The implementation guide repeats it: "The mostPopular chart includes trending music, movies, and gaming videos." `regionCode` "Instructs the API to return a list of videos for the specified region" — [Implementation: Videos, updated 2026-11-10](https://developers.google.com/youtube/data/guides/implementation/videos)
- Parameters: `chart=mostPopular` "Return the most popular videos for the specified content region and video category"; `regionCode` "select a video chart available in the specified region"; `videoCategoryId` default 0 (no restriction); `maxResults` 1–50; error `videoChartNotFound` "The requested video chart is not supported or is not available" — [videos.list reference, updated 2026-11-12](https://developers.google.com/youtube/data/reference/rest/v3/videos/list); [v3 videos.list](https://developers.google.com/youtube/v3/docs/videos/list)
- Cost: "videos | list | 1" — [Quota Calculator](https://developers.google.com/youtube/data/determine_quota_cost?hl=en)
- YouTube removed the Trending page and Trending Now list and pointed users to category charts (Trending Music Videos, Weekly Top Podcast Shows, Trending Movie Trailers), with the Gaming Explore page for gaming — [TeamYouTube post, 10 Jul 2025](https://support.google.com/youtube/thread/356702168/changes-to-discovering-trending-content-on-youtube?hl=en); [TechCrunch, 10 Jul 2025](https://techcrunch.com/2025/07/10/youtube-is-getting-rid-of-its-trending-page-and-trending-now-list)
- A 2026 secondary source agrees: "A script that used chart=mostPopular as a trending feed now gets those three categories only." — [Mellow Hub, 8 Nov 2026](https://www.mellow.world/hub/answers/how-to-find-youtube-shorts-trends)

### Inferences
- INFERRED: whether mostPopular contains Shorts depends on whether the Music or Gaming charts include Shorts. No source confirms it either way. Expect few or none. Only categories 10 (Music) and 20 (Gaming) are likely to return anything. Other categoryIds may return `videoChartNotFound` or an empty list (not verified).
- INFERRED: it still costs only about 1–4 units per region, so it is a cheap side probe for US/GB/DE/FR/IT/ES (music/gaming Shorts channels). It should not be the main method.

### Gaps
- The maximum result count per region chart in 2026 (historically about 200) was not verified.
- Whether mostPopular returns any Shorts after July 2025 was not verified. Test it tomorrow by checking UUSH membership or duration of the returned items.

---

## 3. channels.list fields for checking channel age and region; Shorts detection; costs

### Takeaway
One `channels.list` call (1 unit) checks up to 50 channels. It returns `snippet.publishedAt` (the channel's creation date, which is the age test), `snippet.country`, `statistics.viewCount` (all formats, including Shorts, counted from the first frame since 24 Aug 2026), `statistics.subscriberCount` (**rounded down to 3 significant figures**), `hiddenSubscriberCount`, `videoCount` and `contentDetails.relatedPlaylists.uploads`. `forHandle` resolves an @handle in 1 unit. The API has no "isShort" flag. Google marked that feature request **Won't Fix (Infeasible)** in March 2025. Use the unofficial UUSH playlist or the /shorts/ HTTP check instead.

### Cited Findings
- Cost: "A call to this method has a quota cost of 1 unit." — [channels.list, updated 2026-11-12](https://developers.google.com/youtube/data/reference/rest/v3/channels/list)
- `forHandle`: "specifies a YouTube handle… The parameter value can be prepended with an @ symbol" — [channels.list](https://developers.google.com/youtube/v3/docs/channels/list). Only one filter (id, forHandle, forUsername…) can be used per request — [same page](https://developers-dot-devsite-v2-prod.appspot.com/youtube/v3/docs/channels/list?authuser=0)
- Resource fields: `snippet.publishedAt`, `snippet.country`, `contentDetails.relatedPlaylists.uploads`, `statistics.viewCount`, `subscriberCount` ("rounded down to three significant figures"), `hiddenSubscriberCount` ("Indicates whether the channel's subscriber count is publicly visible"), `videoCount` ("number of public videos") — [Channels resource, updated 2026-11-10](https://developers.google.com/youtube/data/reference/rest/v3/channels)
- `statistics.viewCount`: "The sum of the number of times all the videos in all formats have been viewed for a channel. Starting August 24, 2026, for all video formats (long-form, Live, and Shorts)… viewCount will be updated to count views the moment a video begins to play (includes autoplay, hold the pointer over, and click/tap to play)." — [Channels resource](https://developers.google.com/youtube/data/reference/rest/v3/channels)
- Earlier change: from 31 Mar 2025, Shorts views count "the number of times your Short starts to play or replay, with no minimum watch time requirement", and this applies to `channels.statistics.viewCount` and `videos.statistics.viewCount` — [Revision History, 26 Mar 2025](https://developers.google.com/youtube/v3/revision_history?authuser=1)
- New channels: "The snippet.thumbnails object… might be empty for newly created channels and might take up to one day to populate." — [Revision History](https://developers.google.com/youtube/data/revision_history)
- Getting uploads: "Call the channels.list method to retrieve the ID of the playlist that contains the channel's uploaded videos… part… must include contentDetails" — [Implementation: Videos](https://developers.google.com/youtube/data/guides/implementation/videos). playlistItems.list costs 1 per call — [Quota Calculator](https://developers.google.com/youtube/data/determine_quota_cost?hl=en)
- Shorts-only playlist (unofficial): replace "UC" in the channel ID with **"UUSH"** for a Shorts-only uploads playlist (UULF = videos, UULV = live, UUPS = popular Shorts) — [Stack Overflow 71192605](https://stackoverflow.com/questions/71192605/how-do-i-get-youtube-shorts-from-youtube-api-data-v3); [Stack Overflow 19795987](https://stackoverflow.com/questions/19795987/youtube-channel-and-playlist-id-prefixes). One answer reports playlistItems.list with `playlistId=UUSH…&videoId=X` returns totalResults 1 if X is a Short and 0 if not, but notes "with auto-generated YouTube channels… this does not work" — [Stack Overflow 78597268](https://stackoverflow.com/questions/78597268/is-there-a-way-using-youtubes-v3-api-to-determine-if-a-video-by-id-is-a-shor). A Google engineer advised: "There is not a guideline and they may always change. I strongly suggest not to depend on them" — [same thread 19795987](https://stackoverflow.com/questions/19795987/youtube-channel-and-playlist-id-prefixes)
- HTTP check (unofficial): a HEAD request to `youtube.com/shorts/{id}` returns 200 for a Short and 303 redirect for a non-Short. Google declined to add an API flag ("Status: Won't Fix (Infeasible)", 10 Mar 2025) — [Issue Tracker 232112727](https://issuetracker.google.com/issues/232112727); [QuadMeUp](https://blog.quadmeup.com/2023/03/31/how-to-check-if-youtube-video-is-a-short). One asker warns it "could easily result in ratelimits… Google will flag the request as suspicious" — [Stack Overflow 72050850](https://stackoverflow.com/questions/72050850/youtube-data-api-v3-to-check-whether-video-id-is-a-short)
- `videos.batchGetStats` (added 3 June 2026): 1 unit "in its own granular quota bucket… default quota is 10,000 units per day" — [Revision History](https://developers.google.com/youtube/v3/revision_history)

### Inferences
- INFERRED, core age test: `age_days = now − channels.snippet.publishedAt`. Keep a channel only if ≤15. Then pull the UUSH/UU playlist (1 unit) to get the **first upload date**. If the channel is old but its first upload is recent, it is an old account that was revived or bought, so flag it rather than keep it as "new". The Zenn study used first-upload date for this reason.
- INFERRED: `snippet.country` is optional and self-set by the owner, so many channels will have it blank. Treat it as weak evidence. Add title/description language, `defaultAudioLanguage` on the videos, and comment language before calling a channel "US/EU".
- INFERRED: subscriber rounding (e.g., 1,230,000 → step 10,000) makes "subs gained" noisy. Use viewCount, which is not rounded, for velocity.
- INFERRED: since 24 Aug 2026, views count from the first frame including autoplay, so Shorts view totals in Nov 2026 run **higher** than before. A "100M in 15 days" figure is not comparable to pre-August numbers.
- INFERRED, cost of one verification pass for 2,000 candidate videos: videos.list 40 units + channels.list ≤40 units + UUSH playlistItems 1 per channel. That fits easily in 10,000 units. Quota is not the limit here; the 100 search calls are.

### Gaps
- No Google page quoted this session states that `snippet.country` is self-declared or how often it is blank.
- Whether UUSH playlists populate immediately for channels only a few days old was not verified.

---

## 4. Ways to find these channels without the API, and which ones show channel creation date

### Takeaway
YouTube's own **Charts** cover music (including "Top Songs on Shorts", which ranks songs, not channels), podcasts, movie trailers, and gaming through Explore. They do **not** show a general top-Shorts-by-country list or channel creation dates. Free third-party trackers fill the gap: **Playboard** has a daily "Most viewed Shorts" chart by country including the US, UK, DE and ES; **youtube.trends24.in** and **shortstrends.com** list trending Shorts per country with "Rising on Shorts" views per hour; **vidIQ** has a free fastest-growing-channels list. Creation dates can be read from the channel's "About" page or by putting the IDs through channels.list. Google Trends gives topics, not channels.

### Cited Findings
- YouTube Charts list: Trending chart, Daily Top Music Videos, **Daily Top Songs on Shorts**, Trending Movie Trailers, Weekly Top Songs/Artists/Music Videos, **Weekly Top Songs on Shorts**, Weekly Top Podcast Shows — [YouTube Help 9014376](https://support.google.com/youtube/answer/9014376?hl=en). The US Shorts chart is "Daily ranking of the songs used most by creators on Shorts" — [charts.youtube.com US Daily Top Shorts Songs](https://charts.youtube.com/charts/TopShortsSongs/us/daily); "Today's ranking of most used songs in Shorts creation" — [YouTube Music playlist, Global](https://music.youtube.com/playlist?list=PL4fGSI1pDJn5zxUTEGNA74l6oct9Cqc4R)
- How trending charts rank: signals include "View count; How quickly the video's view count… is growing; Where views are coming from…; The age of the video; How the video performs compared to other recent uploads from the same channel". "**Views from YouTube ads are not included** in a video's view count when measuring videos for trending charts." Charts "are updated roughly every 30 minutes" and are not personalized per country — [YouTube Help 7239739](https://support.google.com/youtube/answer/7239739?hl=en)
- Playboard: "Most viewed Youtube Shorts" with Country (Worldwide, United States, Germany, Spain, United Kingdom… all countries) × Period (Daily/Weekly/Monthly…) × Dimension (Most Viewed/Liked/Commented). It lists each Short's publish date, views and channel subscribers. "The Short-form Chart will be updated to the Shorts Chart on November 11, 2025. From then on, it will include only Shorts videos." — [Playboard worldwide daily, 2 Nov 2026 snapshot](https://playboard.co/en/chart/short/most-viewed-all-videos-in-worldwide-daily); [Brazil daily, 11 Nov 2026](https://playboard.co/en/chart/short/most-viewed-all-videos-in-brazil-daily)
- trends24: "Top Shorts in United States" (338 Shorts in the snapshot) with "Channels on Shorts Chart" and "**Rising on Shorts**" (views/hr). Small channels appear there: e.g., "yoinked 42K subscribers · 2 Shorts · 67M views"; worldwide "Epicvids 37K subscribers · 3 Shorts · 14M views" — [trends24 US Shorts](https://youtube.trends24.in/united-states/shorts/); [trends24 World Shorts](https://youtube.trends24.in/shorts/)
- shortstrends.com: "Countries tracked 111; Countries with Shorts lists 49", including many European countries (Austria, Belgium, France, Germany, Ireland, Italy…) and the US — [shortstrends.com](https://shortstrends.com/youtube/)
- vidIQ fastest-growing (last ~30 days, updated 8 Nov 2026, daily): "A channel created during the period can count from an inferred zero. YouTube rounds public subscriber counts…" — [vidIQ](https://vidiq.com/youtube-stats/top/fastest-growing-youtube-channels)
- Paid/niche tools with a channel-age filter: NicheBreakout uses "detected within 45 days of channel creation" — [NicheBreakout](https://www.nichebreakout.com/youtube-shorts-niche-finder) (vendor page)
- Compliance (secondary, not checked against the primary policy this session): API data fetched without user sign-in may be stored for at most 30 days, and derived metrics are restricted except under a June 2026 addendum — [Mellow Hub](https://www.mellow.world/hub/answers/how-to-find-youtube-shorts-trends)

### Inferences
- INFERRED, best free discovery funnel: (1) Playboard daily/weekly Shorts for US, GB, DE, FR, ES, IT and trends24/shortstrends "Rising on Shorts" give **candidate video and channel names**. (2) Resolve to channelIds with channels.list `forHandle` or videos.list on the video IDs (1 unit). (3) Apply the age test in channels.list. This catches channels that search.list misses, because these sites track country-specific popularity rather than "viewable in".
- INFERRED: these third-party pages are scraped or derived, so their "country" label means where the Short trends, not where the creator lives.
- INFERRED: Google Trends helps choose `q` keywords for search.list but cannot find channels.

### Gaps
- I could not confirm which third-party sites show **channel creation date** directly. Social Blade historically shows "User Created", but this was not verified for 2026. Playboard shows subscribers, not creation date.
- Data freshness and methods of Playboard, trends24 and shortstrends are not documented in the excerpts.

---

## 5. Spotting views inflated by paid ads, and re-uploaded or stolen content

### Takeaway
Paid ads **do** add to the public view count from the first frame (Shorts ads, in-stream, bumper, non-skip), but YouTube's trending charts exclude ad views. The API has no "ad views" field, so detection is heuristic. Look for engagement rates far below niche peers, views far ahead of subscriber growth, and a video that has huge views yet never shows on country charts or trackers. There is also no API field for re-uploads. Check uploads that predate the channel, signs that an old account was renamed, and duplicate titles or thumbnails across channels.

### Cited Findings
- Ad views in the public counter: "YouTube public views, which represent ad views contributing to the public view count, are counted the moment a video ad starts to play across Shorts and in-stream ads." Billable "TrueView" for Shorts ads requires a click or ≥10 s — [YouTube Help 2991785, 24 Aug 2026](https://support.google.com/youtube/answer/2991785?hl=en)
- Google Ads: YouTube public views count for skippable in-stream, in-feed, non-skippable, bumper and Shorts ads ("Shorts ads will count a YouTube public view the moment the video playback starts"); "Public view count is the total number of views (paid as ads, and viewed organically)" — [Google Ads Help 2375431](http://support.google.com/google-ads/answer/2375431?hl=en&ref_topic=10513217); table "Can increment YouTube public view count? … Yes" for all formats — [YouTube Help 2375464](https://support.google.com/youtube/answer/2375464?hl=en)
- Charts exclude ads: "Views from YouTube ads are not included in a video's view count when measuring videos for trending charts." — [YouTube Help 7239739](https://support.google.com/youtube/answer/7239739?hl=en)
- YouTube can "temporarily slow down, freeze, or change your metric count, and discard low-quality playbacks" — [YouTube Help 2991785](https://support.google.com/youtube/answer/2991785?hl=en); invalid-traffic review "can take up to 30 days to fully complete" (quoted from Google Ads Help by [Sprizzy, 7 Oct 2026](https://sprizzy.com/blog/paid-youtube-views-vs-analytics/), secondary)
- The view-count change lowered like rates: "On the median channel, likes per view fell by 41% for videos published after it" (vendor's own study, secondary) — [SociaVault, 30 Oct 2026](https://sociavault.com/blog/youtube-data-api-quota-2026)
- Reuse policy: reused and inauthentic content rules are "judged across the whole channel, with a 15 July 2025 update note" (secondary summary) — [EditorOP, 26 Oct 2026](https://editorop.com/blog/how-to-go-viral-on-youtube-shorts)

### Inferences
- INFERRED, ad-inflation red flags, computed from videos.list `statistics` (1 unit per 50 videos):
  1. likes/views and comments/views well below the **median of comparable new Shorts from the same crawl**. Compare against the crawl median, not a fixed number, because post-Aug-2026 like rates fell sharply.
  2. Channel views per subscriber far above peers. Paid views rarely convert to subscribers.
  3. Big views on 1–2 Shorts while the channel's other Shorts sit near zero (check the UUSH playlist).
  4. A video with tens of millions of views that never appears on Playboard, trends24 or Charts for its country. Charts exclude ad views, though this is a weak signal.
  5. Brand or app channels (links in the description, product names) are more likely to promote.
- INFERRED, re-upload or stolen-content flags: first upload in UU earlier than `channels.publishedAt` is impossible, so watch instead for **video publishedAt dates close together but content clearly older**, titles/hashtags copied from big channels, watermarks of other apps in thumbnails, and the same title on multiple channels (one search.list call with the exact title in quotes). Final judgement needs a human to view the video. Per CLAUDE.md, never download third-party videos.
- INFERRED, feasibility: 100M–1B views on a channel ≤15 days old is an extreme outlier. A 2026 study of 475 new Japanese Shorts channels found **0** with 20M cumulative views (median ~26K). Expect tomorrow's run to find **0–a few** such channels in US/EU, and record a "none found" result honestly. Lowering the threshold to ≥10M as a fallback list is a decision for the OWNER.

### Gaps
- No public API metric separates ad views from organic views for third-party channels. That data is only visible to the owner in YouTube Analytics (traffic source "YouTube advertising").
- No primary source gives a numeric like-rate threshold for "paid".

---

## Appendix A: Proposed run for tomorrow (INFERRED, based on the cited limits; not yet executed)

**Reset time:** midnight PT. PST (UTC−8) is in effect after DST ended on 1 Nov 2026, so the reset is 08:00 UTC = **15:00 Vietnam (ICT)**. This matches the OWNER's figure.

**Budget:** 100 search calls + 10,000 units + 10,000 batchGetStats units.

| Step | Call | Count | Quota |
|---|---|---|---|
| 1 | search.list `part=snippet,type=video,order=viewCount,videoDuration=short,publishedAfter=now−15d,maxResults=50`, no q, × regionCode {US, GB, DE, FR, ES, IT, NL, PL, SE} × relevanceLanguage {en, de, fr, es, it, nl, pl, sv} (paired), pages 1–3 | ~27 | 27 search calls |
| 2 | Same, sliced into 3 windows (0–5d, 5–10d, 10–15d with publishedBefore) for US/en and GB/en, pages 1–2 | ~12 | 12 search calls |
| 3 | Keyword families with q (e.g., "shorts", "#shorts", top Playboard/trends24 topic words) × US/en, page 1 | ~40 | 40 search calls |
| 4 | Reserve for follow-ups (exact-title duplicate checks, new keywords from the first results) | ~20 | 20 search calls |
| 5 | videos.list `part=statistics,contentDetails,snippet` on all unique IDs (50/call) | ~100 | ~100 units |
| 6 | channels.list `part=snippet,statistics,contentDetails` on unique channelIds (50/call). Keep `publishedAt ≥ now−15d` | ~60 | ~60 units |
| 7 | playlistItems.list UUSH (and UU) for the survivors: first-upload date, Shorts share, per-Short views | ≤500 | ≤500 units |
| 8 | Free side sources: Playboard Shorts daily/weekly for US, GB, DE, FR, ES, IT; trends24/shortstrends "Rising on Shorts". Resolve to IDs with videos.list or `forHandle` | — | ~50 units |
| 9 | chart=mostPopular probe, categories 10 and 20 × 6 regions (cheap test of whether Shorts appear) | 12 | 12 units |

**Keep rule:** channel `publishedAt` ≤15 days **and** first upload ≤15 days **and** channel viewCount between 100M and 1B (unrounded) **and** Shorts confirmed via UUSH or duration ≤180 s **and** origin evidence for US/EU (country field, language, comments). Flag ad risk and re-upload risk using section 5. Log every call, its params, items returned and nextPageToken state in a run file (Measure, don't guess).
