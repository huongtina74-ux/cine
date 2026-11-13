# US/EU: channels ≤30 days old with ≥1M views — what they make and whether it repeats (2026-11-13)

## Method (OBSERVED)
- **Pool.** The pool came from three sources:
  - Earlier scans: Tube Atlas exports, 24 English keywords, and region feeds for US, GB and DE.
  - New Shorts region feeds (`order=viewCount`, published after 2026-10-29) for CA, AU, FR, ES, IT, NL, PL, SE and BE.
- **Selection.** Channels created ≤30 days ago with ≥1M channel views, where either the channel country is US/EU or the country is blank and the region feed or audio language is US/EU.
- **Depth.** For the top 45 channels, the latest 50 uploads came from `playlistItems`, with stats from `videos.list`.
  - "Median" is the median views per upload.
  - "Top share" is the biggest video's share of the channel's sampled views. A low share means the channel wins repeatedly.
- **Cost.** This step used about 997 units. Today's total was about 9,700 of 10,000, so the next run is after 15:00 VN tomorrow.
- **Files.** Code: `cf_us_eu_new_channel_deep.py`, `analyze_us_eu.py`. Data: `us_eu_deep.json`, `us_eu_channels.json`.
- **Limits.**
  - Search is ordered by views, so this sample shows winners only.
  - A channel's country is self-declared and often blank.
  - Views are lifetime totals from one snapshot.

## What new US/EU channels are doing

| Group | Channels (age, channel views, median per upload, top share, like rate) | CINE fit |
|---|---|---|
| **AI toddler/baby family comedy** | Copycat Cuties (12 d, 76M, 56K, 41%, 0.42%); Baby Bo (15 d, 52.9M, 71K, 51%); Baby Elecyent (29 d, 48.6M); WonderSnapp (13 d, 39.8M, 251K); **Old Guy Energy (11 d, 29.2M, median 1.85M/upload)**; Rycroft Willians; Baby Bloom; GoofBit | ✗ Realistic AI minors, AI disclosure, inauthentic-content and kids-safety risk; passive likes 0.4–0.6% |
| **Affiliate "comment X to get the link"** | traineronevolleyball (18 d, 56.1M); Pawly (24 d, 40.6M, median 210K); Joy Ride; BuggyBlaze; Pawspike; Pov Of Animal | ✗ Product/affiliate business, not AdSense; likely ManyChat funnels |
| **Roblox animated stories** | Crazyfunnybloxx (24 d, 43M, **439K subs**, median 165K, top share 16%, like 3.8%); Hun blox (24 d, 16.8M, median 653K) | ✗ Roblox IP. Proves "short animated drama with a recurring cast" converts to subscribers |
| **Horror micro-stories** | lulu fah stories (27 d, 46M, 319K subs, median 94K, top share 22%, like 2.8%): "The Snowman MOVED Closer Every NIGHT" | ✓ Format fits S1 Minecraft horror with original characters |
| **AI animal soap opera** | Casper Cat (10 d, 21.5M, median 4.1M/upload, like 1.6%): "She Chose Money 💔" | △ Emotional-manipulation and AI risk |
| **"What to do if…" survival explainer (Spanish)** | ¿Qué hacer si…? (15 d, 27.1M, median 382K, top share 19%, 99 s, like 1.5%) | ✓ An English 3D/animated version is CINE-compatible and evergreen |
| **"Which X reaches Final Form?" / merge evolution** | Endform TV (DE, 22 d, 6.3M; Block/Car/GTA/Chess); Memeland (23 d, 31.6M; "Football Club Merge… Final Form"); Super Balls 3000 (FR, 21 d, 5.5M; "Merging until the MULTIVERSE") | ✓ Blender/Minecraft-block merge sequences; repeats across topics |
| **Cute blocky cast competitions** | Mochi & Pals (29 d, 9.8M, median 204K, top share 29%): "Who can build the best house?", "Who can dig down the fastest?" | ✓ Original Minecraft-style cast in Blender. Watch the Made-for-Kids risk |
| **3D satisfying / sim loops** | SatisfyingShortly (SE, 21 d, 12.4M, 78 uploads, median 60K); Enbi Loop (27 d, 4.0M); VEXOMORPH (transforming vehicles, 11 d, 15.3M, median 205K); Mini lab ASMR (miniature bikes, 15.3M, median 981K) | ✓ Fast views, but weak subscriber conversion (like 0.3%) |
| **Education series** | **Stumblework Studios (19 d, 3.1M, 18.6K subs, like 4.06%, 164 s): "You Just Invented the Sewing Machine \| Invention Series Ep #007"**; yourbuildingnow (24 d, 18.2M, like 2.9%) | ✓✓ Highest engagement and durable; matches the 3D history/engineering long-form plan |
| Spanish Minecraft "¿REAL o FALSO?" myth tests | ElChipaX MIN (29 d, 4.8M, 104K subs) | ✓ English myth-test version = S3 |

Also notable outside the US/EU filter (country CY, found in the US feed): **Tekto Explains**, 13 d, 16.7M, "How To Build a Nuclear Bunker", like 2.16%, 2,630 comments.

## Reading (INFERRED)
1. **The biggest US/EU new-channel numbers come from AI realistic babies and affiliate funnels.** Both are off-limits or off-model for CINE.
2. **The CINE-compatible winners repeat, with low top share and 2–4% likes:**
   - (a) education series with a fixed hook: "You Just Invented…", "What to do if…", "How to build…";
   - (b) evolution/merge "Final Form" sequences;
   - (c) a recurring blocky cast in competitions;
   - (d) horror micro-stories with a ticking threat ("moved closer every night").
3. **Money:** a US-heavy audience pays roughly $100–200 per 1M Shorts views once monetized (ESTIMATED; see `reports/Tiền Shorts Minecraft 1 triệu view.md`). Durable money still comes from long-form, so pick Shorts formats that feed a long-form series (invention / how-to-build / survival explainers → 10–20 min 3D documentaries).

## Next checks
- After 15:00 VN tomorrow:
  - Re-pull these channels to measure 24-hour velocity and which keep growing.
  - Run English keyword searches for "you just invented", "what to do if", "final form", "who can build", "moved closer every night".
- In Tube Atlas: Channels → Analyze videos for Stumblework Studios, Tekto Explains, Endform TV, Mochi & Pals and lulu fah stories (titles and lengths); then Comments on their top videos.
