---
name: minecraft-trend-watch
description: Weekly Minecraft trend check before planning episodes - what skins/outfits players wear now (NameMC, Skindex, Planet Minecraft, observed by hand) plus which Minecraft videos are breaking out (nightly-research), turned into an IP-safe brief for our ORIGINAL cast. Use for "bắt trend Minecraft", "skin nào đang hot", weekly Minecraft planning, or before a new Minecraft series/costume episode.
---
# Minecraft trend watch (weekly, ~45 min, one brief)

Goal: every Minecraft plan starts from this week's evidence, not from memory. Skins tell us what the
audience finds cool to BE (looks, costumes, colours, season); videos tell us what they WATCH. We need both,
and only video numbers predict views. Nothing here guarantees a hit: the benchmark is the niche median.

## 0. Before you start
- `python tools/cf_decision.py list` - read Minecraft decisions (free-tools-only, original IP, routes).
- Find the newest snapshot in `config/niches/minecraft/skin_trends/` (the baseline is `2026-11-01.json`).

## 1. Skin boards - observe by hand, never scrape (~20 min)
Open in a browser (the owner, or Claude in an interactive session the owner asked for):
- NameMC: `https://namemc.com/minecraft-skins/trending/weekly`, `/trending/monthly`, `https://namemc.com/minecraft-skins/tag`
- Skindex: `https://www.minecraftskins.com/` (Top, page 1)
- Planet Minecraft skins (popular, last 7 days) - only if it opens normally.

Hard rules (do not relax them):
- Skindex terms forbid automated access/copying/monitoring and keep ownership with uploaders. So: no scraper,
  no scheduled/unattended browsing, no bulk page fetches, no image downloads, no skin PNG files in the repo.
- A security check (Cloudflare, CAPTCHA) = skip that site this week. Never bypass it.
- Record observations only. Copy `2026-11-01.json` to `config/niches/minecraft/skin_trends/<YYYY-MM-DD>.json`
  and fill, per skin: `source, board, board_size, rank, favorites, age_days` (OBSERVED on the page) and
  `archetype, palette[], features[], season, third_party_ip` (your coding, INFERRED). Reuse last week's
  archetype names so weeks compare. `third_party_ip: true` for any known character (films, games, anime,
  superheroes, real people) - it still counts as a trend signal but never enters the brief.
- Tags: copy the NameMC tag list with its counts (growth between weeks shows what is rising).

## 2. Measure
```
python tools/cf_research_stats.py config/niches/minecraft/skin_trends/<date>.json --kind skins \
    --previous config/niches/minecraft/skin_trends/<last-date>.json \
    --out reports/research/<date>_minecraft_skins.md --json reports/research/<date>_minecraft_skins.json
```
Read: archetype shares (rank-weighted), rising/fading (>= 5 points), tag growth, momentum (favorites/day),
the IP-safe design brief, and the seasonal share (seasons move fast: Halloween -> Christmas -> New Year -> Tết -> summer).

## 3. Videos - what actually gets views
Run the `nightly-research` skill for niche "minecraft animation" (watchlist `config/research/<CHANNEL>_watchlist.txt`,
read-only vidIQ: outliers, trending, keyword research). Save and measure with `tools/cf_research_stats.py`
(video mode). Note which outliers use costumes/seasons/archetypes that also rise on the skin boards -
that overlap is the strongest signal. Public metadata only; a thumbnail is not a watched video.

## 4. Write the brief (append to the skins report, section `## Trend brief`)
Exactly 3 proposals, each with: the trend (skin evidence + video evidence, links), the ORIGINAL angle for our
cast (e.g. Bin & Bo get duck onesies for one episode - new design, our colours, never a traced skin), title and
thumbnail angle, which route renders it (R1 Blender+MCprep / R2 Mine-imator), cheapest test. Label every claim
OBSERVED / INFERRED / UNKNOWN. Mention the next seasonal window and how many days remain to it.

## 5. Hand-off and log
- Showrunner plans; owner approves. This skill never starts production.
- New outfits for the cast go through character design (64x64 original skin, NovaSkin/SkinMC/Blockbench,
  free tools only) and the originality check (`s13-originality-and-kids-safety` rules: no third-party IP).
- `python tools/cf_decision.py add --kind topic --label INFERRED --by claude --project minecraft --decision "Trend brief <date>: <one line>" --why "<top evidence>" --evidence reports/research/<date>_minecraft_skins.md`

Rules: one snapshot + one report per week; observations, not files, from other people's work; free tools only;
Minecraft name is never the main title of our series, and video descriptions carry
"NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT."
