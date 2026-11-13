# tube-atlas-oss (quyenmanhnguyen) — full feature inventory, formulas, install, limits, studio workflow

Research date: 2026-11-13. Method: the GitHub REST API and github.com HTML were blocked for this session (HTTP 403 from the proxy), so the repository's git objects were fetched read-only into a bare scratch repository (no working-tree checkout, no code executed, no keys entered) and files were read with `git show master:<path>`. Every file claim below refers to master commit `f0b2a0dd1e025b00969f5afc9d5cfefc624738e6` (2026-04-29). Link base used below: `https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/<path>`. Repo counters (stars/forks/PRs) come from one WebFetch of the repo page on 2026-11-13.

Labels follow CineFactory's convention: OBSERVED = read in a file or tool output; INFERRED = my reasoning from the code; not measured = nothing was run.

---

## 1. Repo identity, health, maintainer, history

### Takeaway
This is a small, young, single-maintainer Vietnamese repo (0 stars, 0 forks, no releases) whose master branch was written mostly by the Devin AI agent in five days (2026-04-25 → 2026-04-29). There have been no master commits since 2026-04-29. Its scope moved from a "10-tool" clone of the commercial Tube Atlas product to a 5-page "research → script → video" pipeline.

### Cited Findings
- Repo URL: https://github.com/quyenmanhnguyen/tube-atlas-oss. Default branch is `master` (`main` returns 404 on raw.githubusercontent). — [raw README on master](https://raw.githubusercontent.com/quyenmanhnguyen/tube-atlas-oss/master/README.md)
- Licence: MIT ("Copyright (c) 2026"), except `core/pixelle/`, which is Apache-2.0 code adapted from AIDC-AI's Pixelle-Video and has its own NOTICE. — [LICENSE](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/LICENSE), [core/pixelle/NOTICE](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/NOTICE)
- Repo page on 2026-11-13: 0 stars, 0 forks, 0 watchers, 12 open pull requests, 13 commits on master, no releases. GitHub topics: deepseek, keyword-research, python, seo-tools, streamlit, tubebuddy-alternative, vidiq-alternative, youtube, youtube-analytics, youtube-api. The page description still says "10 tools" while the README says "Five focused tools". The open-issue count was not shown. — [GitHub repo page](https://github.com/quyenmanhnguyen/tube-atlas-oss)
- No git tags exist (`git tag` was empty), so there is no release or tag history. — [repo](https://github.com/quyenmanhnguyen/tube-atlas-oss)
- Commit history on master (13 commits):
  - First commit e0161c8 on 2026-04-25, author "TubeAtlas <tubeatlas@users.noreply.github.com>": "feat: Tube Atlas OSS v1.0 — 10-tool YouTube research hub".
  - 2026-04-26 commits by quyenmanhnguyen added screenshots, CI, Dockerfile and ruff.
  - Most later commits were authored by `devin-ai-integration[bot]`.
  - Last master commit: f0b2a0d on 2026-04-29 18:38 +0700, "PR-A5: Grok video provider (Veo 3) + composer video clips (#20)".
  - — [commits](https://github.com/quyenmanhnguyen/tube-atlas-oss/commits/master)
- Maintainer: GitHub user quyenmanhnguyen, display name "Nguyễn Mạnh Quyền", who merged PR #9 on 2026-04-28. — [commits](https://github.com/quyenmanhnguyen/tube-atlas-oss/commits/master)
- Pull requests #1–#20 come from `devin/<unix-timestamp>-…` branches. The newest PR ref, #21 "Added Dev Container Folder" (2026-07-07, author "OutLand"), only adds `.devcontainer/devcontainer.json` and is not on master. — [pulls](https://github.com/quyenmanhnguyen/tube-atlas-oss/pulls)
- Evolution, from the PR head commit subjects:
  - #1 "VidIQ-parity features (Outlier, Audit, Best Time, cache, transcript fallback)"
  - #4 "Content Remix tab in Video Analyzer"
  - #6 "ai_detector …"
  - #10 "Redesign UI (IOCO-style hero) + consolidate to 5 focused tools + EN/KO/JA/VI i18n"
  - #12 "Add Outlier Finder, VidIQ-style keyword gauges, Trend Pulse + yt-dlp transcript fallback"
  - #13 "Merge Niche+Keyword into 01 · Research …"
  - #14–#20 Pixelle/Producer/ComfyUI/Grok work
  - — [pulls](https://github.com/quyenmanhnguyen/tube-atlas-oss/pulls)
- The v1.0 tree had 10 pages: 1_Keyword_Generator, 2_Trends_Generator, 3_Video_Analyzer, 4_Channel_Analyzer, 5_Title_Generator, 6_Video_To_Text, 7_Content_Spinner, 8_Browser_Extractor, 9_Comment_Analyzer, 10_Shorts_Analyzer. The PR #1 branch added 11_Channel_Audit. None of these page files exist on current master. — [v1.0 commit e0161c8](https://github.com/quyenmanhnguyen/tube-atlas-oss/tree/e0161c8)

### Inferences
- Most PR branches are "not merged" by ancestry. Their content reached master through squash merges, for example "Merge Niche+Keyword … (#13)" and "PR-A3 … (#16)". The GitHub "12 open PRs" are probably stale Devin branches whose ideas were partly superseded (INFERRED).
- Development stopped after five intense days. In the ~6.5 months since, only an outside dev-container PR appeared. Treat it as an unmaintained prototype, not a supported product (INFERRED).
- Features from older branches that never reached master include Channel Audit, Best Time to post, Content Remix, AI-detector, Channel Analyzer and Shorts Analyzer. They exist only on unmerged branches or in v1.0 history (INFERRED from the page lists).

### Gaps
- The exact open-issue count is unknown: the API was blocked and the repo page did not show an issues count, so Issues may be disabled.
- The GitHub "created_at" timestamp was not retrieved. The first commit is dated 2026-04-25.

---

## 2. Every page/module on current master: inputs, filters, outputs

### Takeaway
Current master has a landing page plus 5 Streamlit pages:
1. **01 Research**: the old Keyword Finder and Niche Finder merged into one page with two tabs.
2. **02 Video Cloner**.
3. **03 Outlier Finder**.
4. **04 Studio**: a 5-step DeepSeek script wizard.
5. **05 Producer**: script to 9:16 short, or a long-form scene/prompt breakdown, with Edge-TTS, ComfyUI and Grok.

The README is out of date. It still lists page files `01_Niche_Finder.py`/`02_Keyword_Finder.py` and does not mention Producer.

### Cited Findings

**Landing page `app.py`**
- Shows a hero and five numbered cards linking to `pages/01_Research.py`, `02_Video_Cloner.py`, `03_Outlier_Finder.py`, `04_Studio.py` and `05_Producer.py`.
- Shows API status metrics, "active" or "missing", for YOUTUBE_API_KEY and DEEPSEEK_API_KEY.
- Has a sidebar language selector: English / 한국어 / 日本語 / Tiếng Việt.
- — [app.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/app.py)
- The README's "Cấu trúc" tree lists `01_Niche_Finder.py, 02_Keyword_Finder.py, 03_Video_Cloner.py, 04_Studio.py`, which is outdated. Its feature table numbers Niche Finder 01, Keyword Finder 02, Video Cloner 03, Outlier Finder 04 and Studio 05. — [README.md](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md)

**01 Research (`pages/01_Research.py`): the "Niche Finder" + "Keyword Finder"**

Shared form inputs:
- Seed keyword.
- Region `gl` ∈ {US, KR, JP, VN, GB, ID, CN}, default US.
- Autocomplete language `hl` ∈ {en, ko, ja, vi, zh-CN}.
- — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)

Tab A, "Long-tail keywords":
- (a) YouTube autocomplete suggestions for the seed, from `suggestqueries.google.com/complete/search?client=youtube&ds=yt`, with no key.
- (b) If YOUTUBE_API_KEY is set, a "Keyword Score" panel for the seed with three 0–100 gauges (Keyword Score, Volume, Competition), plus a "VPH" bar chart of the top-10 relevance results.
- (c) An optional "KGR" toggle that queries competition (`totalResults`) for up to 25 suggestions and grades each easy/medium/hard.
- (d) Cards for the first 15 suggestions showing chars, words, grade, score and competition, each with a "→ Send to Studio" button.
- (e) A full table with CSV download (columns keyword, length, words, competition, score, grade).
- (f) "Question buckets": autocomplete for language-specific question words + seed. English: how, what, why, when, where, can, should, is. Vietnamese: làm sao, tại sao, khi nào, ở đâu, có nên, có thể. Up to 8 suggestions per prefix.
- The UI caption itself says the gauges are "Proxy score from autocomplete + YouTube search totals — not VidIQ."
- — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py), [core/autocomplete.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/autocomplete.py), [core/keywords.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/keywords.py), [core/i18n.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/i18n.py)

Tab B, "Niche analysis":
- **Google Trends** (pytrends, `gprop='youtube'`). Timeframe ∈ {now 7-d, today 1-m, today 3-m (default), today 12-m}. Shows an area chart, Avg/Peak/"Last 7-pt avg" metrics, and "Top related" and "Rising" query tables.
- **Trend Pulse 7d** (HOT / cooling / stable). Shows uploads in the last 7d versus the prior 7d and a growth %.
- **Niche metrics:**
  - Opportunity score 0–100 with grade high/medium/low.
  - Recent uploads (14d).
  - Competition = `totalResults` for the seed.
- **Breakout videos:** up to 8 rows with title, channel, views, "× median" and URL.
- **Top channels:** up to 10, sorted by subs, with channel, subs, total views, videos and URL.
- **Audience pulse:**
  - Scrapes 150 comments from the #1 video with youtube-comment-downloader (no API key).
  - Scores each comment with VADER `compound`. The thresholds are ±0.05 for negative, neutral and positive.
  - Shows a donut chart and the top 5 comments by votes.
- **AI verdict (DeepSeek JSON):** verdict hot/warm/cold, a 0–100 score, competition, and lists of opportunities, risks and content gaps, plus a summary. A button sends the seed to Studio.
- — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py), [core/trends.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/trends.py), [core/comments.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/comments.py), [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py)

**02 Video Cloner (`pages/02_Video_Cloner.py`)**
- Inputs:
  - YouTube URL. It accepts watch?v=, youtu.be/, shorts/, /embed/ or a raw ID.
  - Optional "New topic for the clone".
  - Number of title clones, 5–20 (default 10).
  - Output language override (auto, en, ko, ja, vi).
- Outputs:
  - **Fingerprint:** thumbnail, title, channel, duration, publish date, views, likes, comments, and engagement % = (likes+comments)/views×100. Original tags appear in an expander.
  - **Transcript:** youtube-transcript-api first, then a yt-dlp auto-sub fallback. Language is auto-detected with langdetect.
  - **DeepSeek "clone kit":** hook_analysis (first 0–15 s, emotional triggers, pacing, structural beats), N title clones each with a Send-to-Studio button, a ~600–900-word Hook·Body·CTA script downloadable as `.md`, 5 thumbnail text overlays of ≤6 words, and 12 SEO tags.
  - **Style kit:** saves a slim "style kit" into session for Producer.
- The transcript is clipped to 8,000 characters before it is sent to the LLM.
- — [pages/02_Video_Cloner.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/02_Video_Cloner.py), [core/transcript.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/transcript.py), [core/transcript_ytdlp.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/transcript_ytdlp.py), [core/lang_detect.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/lang_detect.py), [core/utils.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/utils.py)

**03 Outlier Finder (`pages/03_Outlier_Finder.py` + `core/outliers.py`)**
- Inputs:
  - Seed.
  - Region ∈ {VN (default), US, JP, KR, GB, ID}.
  - Window 7 / 14 / 30 days (default 7).
  - Max subs, 1,000–5,000,000 (default 100,000).
  - Min outlier ratio slider, 0.5–10 (default 1.5).
- Header metrics: outliers found, max VPH, avg VPH, avg outlier score.
- Each result row shows thumbnail, title, channel, subs, days ago, YouTube link, views, VPH, and the outlier score colour-coded (≥5× green, ≥2× amber). It has two buttons: "🎯 Clone" opens Video Cloner with the URL prefilled, and "📝 Use topic" sends the title to Studio.
- CSV export columns: title, channel_title, subs, views, vph, outlier_score, hours_since, url.
- Results are cached for 15 min (`st.cache_data(ttl=900)`).
- — [pages/03_Outlier_Finder.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/03_Outlier_Finder.py), [core/outliers.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/outliers.py)

**04 Studio (`pages/04_Studio.py` + `core/llm.py`)**
- A 5-step wizard whose state lives in `st.session_state["studio"]`. A sidebar shows progress and has a "Restart pipeline" button. — [pages/04_Studio.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/04_Studio.py), [core/llm.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/llm.py)
- The five steps:
  1. 20 topic ideas as {topic, emotion, hook}.
  2. 10 titles of ≤100 chars, each with a reason, and the top 3 flagged by "predicted CTR". You can add optional must-include keywords.
  3. An 8-part outline: Hook, Empathy, Problem 1, Small change, Story, Problems 2&3, Reflection, Closing+CTA. Each part has role/emotion/expansion and is sized for 800–1,200 words.
  4. The long-form script, written in two LLM calls (parts 1–4, then parts 5–8 continuing from the last 800 chars). The default target is 18,000 chars, with per-part minimum = target/8; the README says "up to 24,000 chars".
  5. A "humanize rewrite" to remove AI tells without shortening.
- Other pages can prefill the Studio: `studio_seed_in` jumps to step 1, `studio_topic_in` to step 2 and `studio_title_in` to step 3.
- The code comment says the prompts mirror the 'H2Dev "PROMPT NGÁCH NHỎ PHẬT PHÁP" workflow'.
- — [core/llm.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/llm.py), [pages/04_Studio.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/04_Studio.py)

**05 Producer (`pages/05_Producer.py` + `core/pixelle/*`)**
- Two modes. — [pages/05_Producer.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/05_Producer.py)
- **`short` mode:**
  - Edge-TTS voice-over with word timing turned into captions.
  - Composes a 9:16 mp4 with moviepy.
  - The background is either a gradient Ken Burns preset (violet-pink, sunset, ocean, mono, …) or per-scene images from a visual provider: ComfyUI local at `COMFYUI_URL`, RunningHub cloud, or Grok image/video.
  - Visual style can come from the Cloner style kit, a manual reference, or a preset.
- **`long_form` mode:**
  - An LLM breaks `script_final` from Studio into N scenes, sized at 150 WPM (configurable).
  - Each scene has: title, verbatim narration, an "ultra-detailed" image prompt, a 3–4 sentence video prompt (for Veo 3 / Sora / Wan / Kling), and a duration.
  - Templates: cinematic, educational, lifestyle, factory, custom.
  - Exports `.md` and `.json`.
  - Also builds a thumbnail prompt.
- — [core/pixelle/scene_breakdown.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/scene_breakdown.py), [core/pixelle/styles.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/styles.py), [core/pixelle/tts.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/tts.py), [core/pixelle/config.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/config.py)
- **Grok provider:**
  - Logs into `accounts.x.ai/sign-in` with the user's email and password through Playwright (Chromium).
  - Captures cookies plus the `x-statsig-id` / `x-csrf-token` headers.
  - Calls unofficial grok.com endpoints (`/rest/app-chat/conversations/new`, `/rest/media/post/create`) for images and for 6/10-second 480p/720p "Veo 3" videos.
  - The docstrings say it "mirror[s] the AutoGrok Electron reference implementation" and that "There is no public xAI API behind this".
  - — [core/pixelle/grok_browser.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_browser.py), [core/pixelle/grok_web_client.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_web_client.py), [core/pixelle/grok_video_client.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_video_client.py)

**Supporting modules that have no page of their own on master**
- `core/youtube.py` also has `trending_videos` (chart=mostPopular), `video_categories`, `channel_by_handle`, `channel_recent_videos` and `playlist_video_ids`.
- `core/autocomplete.py` has `expand()` (seed + a…z alphabet soup).
- `core/trends.py` has `trending_searches`.
- `core/transcript.py` has `transcript_to_srt`.
- No current page calls these helpers; they are leftovers of the v1.0 tools.
- — [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py), [core/autocomplete.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/autocomplete.py), [core/trends.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/trends.py), [core/transcript.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/transcript.py)

### Inferences
- Nothing on master is a standalone "Channel Analyzer", channel audit, "best time to post", RPM/revenue estimator, or saved/watch-list feature. A grep of master for `rpm|revenue|cpm|monetiz` found no code hits (OBSERVED via `git grep`; INFERRED that the feature is absent).
- "Niche Finder" on master means Research → tab "Niche analysis". When the user says "Niche Finder" and "Outlier Finder", the mapping is 01 Research (tab B) and 03 Outlier Finder (INFERRED).
- Streamlit tabs execute both bodies on every run. One click on "Run" therefore runs the keyword tab and the whole niche tab, including the DeepSeek verdict and comment scraping (INFERRED from the code structure).

### Gaps
- Not measured: no page was rendered or run, so output quality, speed and UI behaviour are unverified.
- The unmerged branch pages (Channel Audit, Best Time, Content Remix, ai_detector) were not read in detail.

---

## 3. Formulas, and YouTube API quota per run

### Takeaway
All scores are simple heuristics with hard-coded anchors.
- **Outlier score** = views ÷ max(subs, 1,000) for videos found by one `search.list`.
- **Niche "breakouts"** = views > 2.5 × the median views of the top-25 search results.
- **Opportunity score** = activity(0–40) + reach(0–40) + (20 − saturation).
- **Keyword Score** = 0.7·Volume + 0.3·(100 − Competition).

Quota is dominated by `search.list` at 100 units per call. One Research run costs about 500 units (≈3,000 with KGR on), and one Outlier run costs about 102 units.

### Cited Findings
- **Outlier score.** `compute_outlier_score(views, subs) = views / max(subs, 1000)`. The docstring says "a ratio of 1.5+ is interesting; 5+ is 'clonable' territory".
  - Pipeline: `search.list(q=seed, type=video, order=viewCount, publishedAfter=now−window, maxResults=50, regionCode)`, then `videos.list` (snippet, statistics, contentDetails, topicDetails, status), then `channels.list`.
  - Rows are dropped when subs > max_subs or ratio < min_outlier, then sorted by ratio.
  - VPH = views ÷ hours since publish, with hours floored at 1.
  - — [core/outliers.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/outliers.py), [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py)
- **Breakouts (Niche tab).** `detect_outliers(videos, multiplier=2.5)` flags videos where views > 2.5 × median. The median is the upper median of the ≤25 hydrated top-viewCount results for the seed, and the ratio shown is views/median. — [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py), [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)
- **Opportunity score:**
  - activity = min(recent_uploads_14d/50, 1)×40
  - reach = min(top_video_views/5,000,000, 1)×40
  - sat = min(totalResults/5,000,000, 1)×20
  - score = clamp(round(activity + reach + 20 − sat), 0, 100)
  - Grades: ≥70 high, ≥40 medium, otherwise low.
  - recent_uploads comes from `search.list(order=date, publishedAfter=now−14d, maxResults=1)` → `pageInfo.totalResults`.
  - top_video_views is the views of the first hydrated top-viewCount result.
  - — [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py)
- **Trend Pulse 7d:**
  - recent = totalResults over 7d; prior = max(totalResults over 14d − recent, 0)
  - growth = (recent − prior)/prior×100, or 100 if prior=0 and recent>0
  - Status "hot" if growth ≥30% and recent ≥5; "cooling" if growth ≤ −20%; otherwise "stable".
  - — [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py)
- **Keyword gauges:**
  - Volume = min(autocomplete_count/12, 1)×80 + min(log10(totalResults)/6, 1)×20.
  - Competition = min(log10(totalResults)/8, 1)×100, plus up to +10 when the top-10 average views exceed 1M (5·log10(avg/1M)).
  - Keyword Score = 0.7×Volume + 0.3×(100−Competition).
  - Grades: ≥70 great, ≥50 good, ≥30 ok, otherwise weak.
  - — [core/keywords.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/keywords.py)
- **KGR:**
  - raw = competition ÷ breadth, where competition = `totalResults` for the exact suggestion and breadth = number of autocomplete suggestions for the seed.
  - raw ≤500 → 90 "easy"; ≤5,000 → 70 "medium"; ≤50,000 → 40 "medium"; otherwise 15 "hard".
  - — [core/keywords.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/keywords.py), [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)
- **Other formulas:**
  - Engagement % = (likes + comments)/views × 100. — [core/utils.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/utils.py)
  - Sentiment: VADER compound, bins [−1,−0.05) negative, [−0.05,0.05) neutral, [0.05,1] positive. — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)
- **README quota table:** search.list 100 units (~100 searches/day); videos.list 1 unit per 50 IDs; channels.list 1; commentThreads.list 1; daily quota 10,000 units. — [README.md](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md)
- **Endpoints the code calls:**
  - YouTube Data API: `search.list`, `videos.list`, `channels.list`, `playlistItems.list`, `videoCategories.list`.
  - Comments do **not** use `commentThreads.list`. They are scraped with youtube-comment-downloader (no key), even though the README lists commentThreads.
  - — [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py), [core/comments.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/comments.py)

### Inferences
These quota figures are INFERRED by tracing the code with the README unit costs. Nothing was run.

**One Research run (both tabs, KGR off)**

| Part | Calls | Units |
|---|---|---|
| Tab A | `search.list` (seed relevance) + `videos.list` | 100 + 1 |
| Tab B | `search.list` (viewCount top-25) | 100 |
| Tab B | `recent_uploads_count` 14d | 100 |
| Tab B | `trend_pulse` (7d + 14d) | 2 × 100 |
| Tab B | `videos.list` + `channels.list` | 1 + 1 |
| **Total** | | **≈ 503** |

- Turning KGR on adds up to 25 × 100 = **2,500**, so a run costs ≈ 3,003 units.
- The 10,000/day quota therefore allows about 19 Research runs without KGR, or about 3 with KGR.
- The Research page has no `st.cache_data`, so every re-run spends quota again.

**Other pages**
- One Outlier Finder run ≈ 100 + 1 + 1 = **102 units**, so about 98 runs/day. Repeating identical inputs within 15 min is free because of the cache.
- Video Cloner ≈ 1 unit per run (`videos.list`), plus transcript scraping that uses no quota.
- Studio and Producer use no YouTube quota.

**Method weaknesses**
- **Outlier score vs subscribers.** The score compares views with **subscribers**, not with the channel's own typical views. Small channels with one lucky video, or channels with hidden subscriber counts (which return 0 and are floored to 1,000), can rank high. The ratio is also not age-normalised: a 30-day-old video has had more time than a 1-day-old one.
- **Breakouts vs search median.** The comparison is against the median of the search-result set, not the channel baseline. It mixes channels of every size.
- **`totalResults` is approximate.** YouTube's `totalResults` is a rough estimate. Trend Pulse, Competition and KGR all depend on it, so growth % and KGR grades can be noisy or quantised.
- **KGR ignores breadth in practice.** `breadth` is the same number for every row on a page, so the KGR grade depends only on each suggestion's competition.
- **Opportunity score anchors.** The anchors (50 uploads/14d, 5M views, 5M results) are arbitrary. A VN-language niche will rarely reach them.
- For CineFactory, the benchmark should still be the niche median, computed with `tools/cf_research_stats.py`, rather than these scores.

### Gaps
- The official Google quota cost table was not re-fetched in this session; costs are taken from the README.
- I found no evidence about a "separate search.list limit" beyond the 10,000 units/day. Not verified.
- Not measured: the actual units consumed per run.

---

## 4. What DeepSeek / LLMs are used for

### Takeaway
DeepSeek (model `deepseek-chat` by default) is reached through the OpenAI SDK at `https://api.deepseek.com/v1`. It is used for:
- the Niche AI verdict (JSON),
- the Video Cloner kit (JSON),
- all 5 Studio steps,
- Producer scene prompts and the long-form breakdown.

Gemini is an optional fallback in the Pixelle chain. No YouTube metric is computed by the LLM. The LLM only interprets numbers and generates text.

### Cited Findings
- `client()` uses `OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")`. The model is read from `DEEPSEEK_MODEL`, default `deepseek-chat`. `chat_json` uses temperature 0.4 and `response_format=json_object`. — [core/llm.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/llm.py)
- **Niche AI verdict.** The prompt asks for `{verdict: hot|warm|cold, score 0-100, competition, opportunities[], risks[], content_gaps[], summary}`. The payload sent is:
  - trend avg/peak/recent,
  - long-tail count and 10 samples,
  - top-10 channels,
  - sentiment breakdown and 5 sample comments,
  - recent uploads (14d) and total competition.
  - — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)
- **Studio temperatures:** the script is written at 0.85 and the humanize rewrite runs at 0.6. — [core/llm.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/llm.py)
- **Pixelle LLM settings:** `PIXELLE_LLM_PRIMARY` (default deepseek) and `PIXELLE_LLM_FALLBACK` (default gemini, using `GOOGLE_API_KEY`/`GEMINI_API_KEY` and `gemini-2.5-flash`). The same config also defines ComfyUI/RunningHub and TTS settings. — [core/pixelle/config.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/config.py)

### Inferences
- The AI verdict "score" is an LLM opinion layered on top of the heuristic opportunity score. It is not reproducible: re-running the same seed can give a different verdict.
- In CineFactory terms it is INFERRED-grade, not OBSERVED.

### Gaps
- DeepSeek token cost per run was not measured.

---

## 5. Installation and running (incl. Windows, Docker)

### Takeaway
You need Python 3.10+ (CI and Docker use 3.12), then `pip install -r requirements.txt`, then copy `.env.example` to `.env` and fill in `YOUTUBE_API_KEY` and `DEEPSEEK_API_KEY`. Run it with `streamlit run app.py` and open http://localhost:8501. A Dockerfile is provided. Playwright is only needed for the Grok provider and is not in requirements.

### Cited Findings
- **README install steps:** `git clone …`, `pip install -r requirements.txt`, `cp .env.example .env`, add YOUTUBE_API_KEY and DEEPSEEK_API_KEY, `streamlit run app.py`, open http://localhost:8501.
- **Docker:** `docker build -t tube-atlas-oss .` then `docker run -p 8501:8501 --env-file .env tube-atlas-oss`.
- **Streamlit Community Cloud:** fork the repo and put the keys in Secrets (TOML).
- — [README.md](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md)
- `.env.example` contains `YOUTUBE_API_KEY=`, `DEEPSEEK_API_KEY=` and `DEEPSEEK_MODEL=deepseek-chat`. — [.env.example](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/.env.example)
- **Optional environment variables:**
  - `TUBE_ATLAS_TRANSCRIPT_BACKEND=ytdlp` (skip youtube-transcript-api) — [core/transcript.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/transcript.py)
  - `COMFYUI_URL` (default http://127.0.0.1:8188), `COMFYUI_CLOUD_ONLY`, `RUNNINGHUB_API_KEY`, `RUNNINGHUB_INSTANCE`, `PIXELLE_IMAGE_WORKFLOW` (image_flux.json), `PIXELLE_VIDEO_WORKFLOW` (video_wan2.1_fusionx.json), `PIXELLE_PROMPT_PREFIX`
  - `PIXELLE_TTS_ENGINE` (edge-tts), `PIXELLE_TTS_VOICE` (en-US-AriaNeural), `PIXELLE_TTS_RATE`, `PIXELLE_TTS_VOLUME`
  - `GOOGLE_API_KEY`/`GEMINI_API_KEY`, `GEMINI_MODEL`
  - — [core/pixelle/config.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/config.py)
- **requirements.txt:** streamlit≥1.36, google-api-python-client≥2.120, youtube-transcript-api≥1.0, youtube-comment-downloader≥0.1.76, pytrends≥4.9.2, yt-dlp≥2024.8.6, requests, pandas, plotly, python-dotenv, openai≥1.40, vaderSentiment, wordcloud, matplotlib, langdetect, edge-tts≥6.1, mutagen, moviepy≥1.0.3,<2, imageio-ffmpeg, Pillow≥10. — [requirements.txt](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/requirements.txt)
- **Docker image:** based on `python:3.12-slim`, exposes 8501, has a healthcheck on `/_stcore/health`, and its entrypoint is `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`. — [Dockerfile](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/Dockerfile)
- **CI:** GitHub Actions runs ruff lint, compileall and pytest on Python 3.12. — [.github/workflows/ci.yml](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/.github/workflows/ci.yml)
- **Playwright** is lazily imported and "not a hard dependency". If it is missing, the code raises `GrokBrowserUnavailable` with install instructions. — [core/pixelle/grok_browser.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_browser.py)
- **yt-dlp** is called as an external CLI via `subprocess.run(["yt-dlp", …])`, so the executable must be on PATH. — [core/transcript_ytdlp.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/transcript_ytdlp.py)

### Inferences
These Windows steps are INFERRED and were not run:

```
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
streamlit run app.py
```

- Activating the venv puts `yt-dlp.exe` on PATH, so the transcript fallback works.
- moviepy 1.x on Pillow 10 relies on an ANTIALIAS shim (PR #15 subject). Version drift (moviepy, youtube-transcript-api ≥1.0 API changes, pytrends) is the most likely install breakage.
- For CineFactory, keep this in a separate folder and venv. Do not mix it into the CineFactory repo, per the CLAUDE.md rule "Do not create another CineFactory repo".

### Gaps
- Not measured: whether `pip install` resolves cleanly in Nov 2026, and whether the tests pass.

---

## 6. Limits, bugs, security, telemetry

### Takeaway
This is a usable prototype with real limitations:
- quota-heavy niche runs,
- proxy/heuristic scores,
- scraping-based comments, transcripts and trends that can break,
- a stale README,
- and one serious compliance problem: the Producer's Grok provider automates grok.com logins and unofficial endpoints.

Keys sit in plaintext `.env`. No telemetry was found, and Streamlit usage stats are off.

### Cited Findings
- **Telemetry and outbound hosts.** `.streamlit/config.toml` sets `gatherUsageStats = false`. A grep of `core/` and `pages/` for outbound URLs found only: suggestqueries.google.com, the YouTube Data API (google client), api.deepseek.com, the ComfyUI local URL, runninghub.cn, accounts.x.ai, grok.com and assets.grok.com. There are also scraping libraries (pytrends, youtube-comment-downloader, youtube-transcript-api, yt-dlp). No analytics endpoint was found. — [.streamlit/config.toml](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/.streamlit/config.toml), [core/pixelle/comfy_client.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/comfy_client.py)
- **Key storage:**
  - Keys are read from `.env` via python-dotenv.
  - Producer has a credentials panel that writes `DEEPSEEK_API_KEY` in plaintext into the repo-root `.env` (`_save_env_var`).
  - Grok email and password are typed into the Streamlit UI and used once for a Playwright login. The session is kept in `st.session_state`; the docstring says "Nothing is persisted to disk."
  - — [pages/05_Producer.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/05_Producer.py), [core/pixelle/grok_browser.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_browser.py)
- **Grok client behaviour.** It "race-download[s] several CDN URL variants and keep[s] the largest one — moderated images on the CDN are blurred …, while the unblurred version sits on the asset host for a brief window". In other words, it is designed to get around content moderation. — [core/pixelle/grok_web_client.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_web_client.py)
- **Language detection** maps only en/ko/ja/vi. Chinese and every other language fall back to "en". — [core/lang_detect.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/lang_detect.py)
- **Transcripts.** youtube-transcript-api is "blocked from many cloud-IP ranges", hence the yt-dlp fallback. — [core/transcript.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/transcript.py)
- **`channel_details` is not batched:** a single `channels.list` call with all IDs, whose API max is 50. PR #8 ("batch channel_details in chunks of 50") is not on master. — [core/youtube.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/youtube.py), [PR #8 branch](https://github.com/quyenmanhnguyen/tube-atlas-oss/pull/8)
- **README vs code:**
  - The README says Keyword Finder needs "None / YouTube" key and lists commentThreads in the quota table. The code scrapes comments instead.
  - The README omits Producer.
  - The GitHub description says "10 tools".
  - — [README.md](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md), [GitHub repo page](https://github.com/quyenmanhnguyen/tube-atlas-oss)
- **Error handling.** Most YouTube and Trends failures are swallowed with `try/except` and shown as warnings, or simply leave scores missing. For example, the gauges silently disappear if `search_raw` fails. — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py)

### Inferences
- **Likely UX bug (INFERRED, not run).** Research and Outlier pages gate on `run = st.form_submit_button(...)` followed by `if not run: st.stop()`. A later rerun, such as toggling "KGR" or changing the Trends timeframe selectbox, makes `run` False, so the page stops and the results vanish. The user must press Run again, which spends another ~500 quota units on Research.
- **Shared-key risk.** A Streamlit Cloud deployment (as the README suggests) has no login. Anyone with the URL can spend your YouTube quota and DeepSeek credit.
- **Plaintext keys.** `.env` is in `.gitignore`, but it is plaintext. It must never be committed or shared.
- **CineFactory compliance conflicts.**
  - The Grok provider (Playwright login, unofficial endpoints, moderation-bypass downloads) conflicts with CineFactory's hard rule "Don't automate third-party apps against their terms". Do not use Producer → Grok.
  - Video Cloner's "script clone" and "title clones" of a competitor video conflict with "Original IP only: no competitor … scripts". Use Cloner only for structural analysis (hook timing, beats), never to produce our script.
  - Studio/Producer DeepSeek calls are metered API spend and need the owner's approval under CLAUDE.md.
- **Fragile dependencies.** Comment scraping, transcripts, pytrends and yt-dlp all depend on unofficial YouTube/Google scraping. pytrends in particular is often rate-limited (HTTP 429); the page then shows "Trends unavailable".

### Gaps
- Not measured: the bugs above are from code reading only.
- No GitHub issues were read: the API was blocked and the issue count is unknown.

---

## 7. Relationship to commercial tools (Tube Atlas, VidIQ/TubeBuddy, TubeLab, NexLev, 1of10)

### Takeaway
The OSS repo began as an open re-implementation of the commercial "Tube Atlas" desktop toolkit. Its v1.0 tool names match the commercial tool names almost exactly. It later chased VidIQ parity (branch "vidiq-parity", topics "vidiq-alternative" and "tubebuddy-alternative"). It does not mention TubeLab, NexLev or 1of10, and it lacks their core features: channel-baseline outliers, large historical databases, and RPM/revenue estimates. If the user meant the paid "Tube Atlas" product, that is a different, non-AI, one-time-purchase tool.

### Cited Findings
- **Commercial Tube Atlas (per a review blog).** Named tools: Keyword Generator, Trends Generator, Video Analyzer, Channel Analyzer, Comment Analyzer, Video-to-Text Converter, Browser Extractor, Tag Analyzer, hashtag generation and a content spinner. It claims "12 tools", costs "$67" one-time with "Lifetime updates for version 1", and the review does not describe AI. This is an affiliate-style review blog, so treat it as low-reliability. — [Revuuit review (Sep 2025)](https://revuuit.blogspot.com/2025/09/tube-atlas-review.html)
- **Other commercial Tube Atlas write-ups** exist, for example "12 tools", a June 2026 TubeAtlas article. They were not read. — [differ.blog](https://differ.blog/p/honest-tube-atlas-review-12-tools-that-changed-everything-8ed24c), [blogspot 2026-06](https://directcontentmarketingstrategy.blogspot.com/2026/06/how-tubeatlas-helps-new-youtubers-find.html)
- **OSS v1.0 tool list:** Keyword Generator, Trends Generator, Video Analyzer, Channel Analyzer, Title Generator, Video → Text, Content Spinner, Browser Extractor, Comment Analyzer, Shorts Analyzer. Its README notes "6/10 tools hoạt động ngay mà không cần API key". — [README at e0161c8](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/e0161c8/README.md)
- **VidIQ references:**
  - Code comments: "VidIQ-style" gauges, `keyword_score` "VidIQ-style: 0.7×Volume + 0.3×(100−Competition)".
  - UI disclaimer: "not VidIQ".
  - — [core/keywords.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/keywords.py), [core/i18n.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/i18n.py)
  - PR #1 is titled "VidIQ-parity features (Outlier, Audit, Best Time …)". — [PR #1](https://github.com/quyenmanhnguyen/tube-atlas-oss/pull/1)
- **No TubeLab/NexLev/1of10 mentions.** A grep of master for `tubelab|nexlev|1of10` found nothing in code or docs. — [repo](https://github.com/quyenmanhnguyen/tube-atlas-oss)
- **Other borrowed code:**
  - Producer code is adapted from AIDC-AI Pixelle-Video (Apache-2.0). — [core/pixelle/NOTICE](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/NOTICE)
  - The Grok client mirrors the "AutoGrok" Electron app. — [core/pixelle/grok_web_client.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/core/pixelle/grok_web_client.py)

### Inferences
- **Feature comparison (INFERRED; competitor details not verified in this session):**
  - Outlier Finder ≈ a lightweight subs-based version of the "outlier" idea popularised by 1of10/TubeLab. It runs live per query and uses no historical database.
  - Research/niche ≈ a VidIQ-like keyword panel plus a pytrends chart.
  - There is no channel-level niche discovery across thousands of channels, no RPM/CPM/revenue estimate, no saved searches or alerts, and no faceless-channel database.
- The repo uses the commercial product's name. The README does not say whether it is affiliated with the commercial Tube Atlas vendor; presumably it is not.

### Gaps
- How TubeLab, NexLev and 1of10 compute their outlier scores and RPM estimates was not researched here (out of scope and no sources fetched).
- The commercial Tube Atlas vendor and its exact 12-tool list are unconfirmed.

---

## 8. How a faceless YouTube studio would use it, step by step

### Takeaway
The most useful, low-risk parts are:
- Research tab A (free autocomplete and question buckets),
- Outlier Finder (102 units/run, CSV export),
- Research tab B (≈500 units/run, used sparingly).

Put their CSVs through CineFactory's own median and outlier stats. Do not use the Cloner script output or the Producer/Grok features for production.

### Cited Findings
- The pipeline the repo intends: Research or Outlier → "Send to Studio" / "🎯 Clone" → Studio's 5 steps → Producer. — [README.md](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/README.md), [pages/03_Outlier_Finder.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/03_Outlier_Finder.py)
- Exports available: keyword CSV (Research tab A), outlier CSV (Outlier Finder), clone script `.md`, and long-form scene breakdown `.md`/`.json`. — [pages/01_Research.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/01_Research.py), [pages/03_Outlier_Finder.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/03_Outlier_Finder.py), [pages/05_Producer.py](https://github.com/quyenmanhnguyen/tube-atlas-oss/blob/master/pages/05_Producer.py)

### Inferences
This step-by-step is INFERRED, based on the code and on the CineFactory rules in `/home/claude/cine/CLAUDE.md`.

1. **Setup.** Use a separate folder and venv. Create a dedicated Google Cloud project and API key restricted to YouTube Data API v3, so you can watch quota in the console. Add a DeepSeek key only if the owner approves the metered LLM spend. Run locally; do not deploy publicly.
2. **Seed brainstorming (free).** Research, tab A, without KGR: enter a broad seed such as "slow english listening", "bedtime history", or "3d animals slide". Set `gl`/`hl` to the target market, for example US/en. Export the CSV. Open the question buckets for long-tail informational angles.
3. **Shortlist keywords (quota).** Turn KGR on only for a shortlist, because it costs up to 2,500 units. Treat easy/medium as a hint, since only `totalResults` drives it.
4. **Niche check per finalist seed (~500 units each).** Read Trend Pulse, the Trends rising queries and the top channels. Treat the Opportunity score and AI verdict as soft signals. Save the breakouts table and the top-channel URLs.
5. **Outlier hunt (~102 units each).** Outlier Finder settings:
   - window 7 → 14 → 30 days,
   - max subs 10k–100k for "small channels proving a format",
   - min ratio 3–5×.
   Run it per seed and region, and export the CSV. Repeat across 5–10 seeds; that is roughly 1,000 units total.
6. **Normalise and judge in CineFactory.** Load the CSVs into `tools/cf_research_stats.py` to get medians and views/day. Rank by views/day relative to the niche median, not by subs-ratio alone, per the CLAUDE.md research policy ("benchmark is the niche MEDIAN"). Log the chosen niche with `tools/cf_decision.py add`.
7. **Format study (structure only).** For 2–3 top outliers, Video Cloner's fingerprint and hook analysis can describe pacing and beats. Do not use its title clones or script clone as our content. Any "we learned X from competitor Y" claim still needs the competitor-complete-study gate.
8. **Scripting.** Studio's 5-step flow (topics → titles → 8-part outline → script → humanize) is generic DeepSeek prompting. CineFactory already has its own Script Factory and master skill for Bell & Leaf / Slow English A2, so Studio adds little and would create a parallel script factory, which CLAUDE.md forbids.
9. **Production.** Skip Producer. Edge-TTS shorts with gradient backgrounds are low quality, and its Grok provider breaks third-party terms. The CineFactory render/edit/QC loop is the production path.

### Gaps
- Not measured: none of these steps were run, so result quality for VN- or EN-language faceless niches is unknown.
- No case studies of creators using this repo were found. The repo has 0 stars and 0 forks.
