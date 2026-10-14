---
name: nightly-research
description: Nightly (or on-demand) research run for one channel/niche - pull competitor and outlier videos read-only, compute honest medians/outliers with tools/cf_research_stats.py, and write ONE dated report with 3 proposals for the showrunner. Use for "research tonight", "what is working in <niche>", or the nightly factory.
---
# Nightly research (one report, labeled numbers, no rabbit holes)

Inputs: NICHE (e.g. "kids long slide animals"), CHANNEL (our channel id), up to 30 competitor channels from `config/research/<CHANNEL>_watchlist.txt` (create it on the first run from the vidIQ results and ask the owner to confirm it).
Budget: about 45 minutes and only read-only tools. Never spend credits (the guard hook blocks paid tools; vidIQ `video_watch`, generation and upload tools are NOT part of this skill).

1. **Pull (read-only).** With vidIQ when connected: `vidiq_outliers`, `vidiq_trending_videos`, `vidiq_channel_videos` (watchlist), `vidiq_keyword_research`. Save the rows you got, unchanged, to `data/research/raw/<YYYY-MM-DD>_<CHANNEL>.json` as a list of videos with channel, title, views, published, duration, url. No vidIQ? Use what the owner exported (CSV) - never scrape or download videos.
2. **Measure.** `python tools/cf_research_stats.py data/research/raw/<date>_<CHANNEL>.json --niche "<NICHE>" --out reports/research/<date>_<CHANNEL>.md --json reports/research/<date>_<CHANNEL>.json`
   Use the MEDIAN as the benchmark, never the best video. Outliers (>= 3x their own channel median) are the formulas worth studying.
3. **Compare with last week.** Read the previous report in `reports/research/`. What is new, what faded, which channels are growing.
4. **Read the audience.** For the top 3 outliers, read comments when a read-only tool returns them (`vidiq_video_comments`). Write down what viewers ask for, in their words.
5. **Write the report** - append to the stats markdown a section `## Proposals` with exactly 3 items, each: idea (original, our characters/world only), the outlier evidence it comes from (link), why it fits our pipeline, cheapest test. Label every claim OBSERVED (in the data file) / INFERRED (your reasoning) / UNKNOWN.
6. **Log.** `python tools/cf_decision.py add --kind topic --label INFERRED --by claude --decision "Proposals ready: <one line>" --why "<top evidence>" --evidence reports/research/<date>_<CHANNEL>.md`
   The showrunner and the owner decide; this skill never starts production by itself.

Rules: public metadata and comments only; titles/thumbnails are not "watched videos"; never copy competitor characters, names, scripts, music or footage; one report per run, no new code modules.
