# B. New Minecraft YouTube competitors (0–30 d, wider net 31–180 d) and updated watchlist — from the 2026-11-03 API snapshot

Scope: existing dataset only (snapshot 2026-11-03 19:00–19:05 UTC, YouTube Data API v3, US/en search). No API calls or scraping were made for this note.
Labels: **OBSERVED** = counted from files in `data/` (analysis run in Python in the sandbox, 2026-11-04). **INFERRED** = my reasoning. **OWNER** = owner rules in `config/research/minecraft_story_rules.md`.
Video pool used per channel = `uploads.csv` (≤50 latest uploads) ∪ `videos.csv` (search hits), deduplicated by video_id (13,622 videos). Long = duration > 180 s; Short = ≤ 180 s (same rule as the dataset; the API has no Shorts flag). views÷subs bands: <10× "several×", 10–99× "tens×", 100–999× "hundreds×", ≥1,000× "thousands×". Ages are as of fetch time (2026-11-03 ≈19:01 UTC).

**English rule (stated, applied to every video then to the channel):** a video is English if its declared `defaultAudioLanguage`/`defaultLanguage` starts with `en` and its title has no non-Latin script; it is non-English if it declares another real language (not `zxx`/blank); if undeclared, the title decides (non-Latin script, or more Spanish/Portuguese/Turkish/Indonesian/German/French function words + accented letters than English function words → non-English). A channel is English if ≥60% of its sampled videos are English. Channel `country` is NOT used (several English-language channels are registered TR, SE, KW, PK, IN).

## 1. How many channels are 0–30 days old, which have 100K+/1M+ videos, long vs Shorts, English vs non-English

### Takeaway
77 sampled channels were 0–30 days old (59 English by the rule). 20 have a ≥100K video (16 English), 7 have a ≥1M video (6 English) — and the breakouts are overwhelmingly Shorts: only 1 channel aged ≤30 d has a long-form video ≥1M (Day Zero, 1.89M) and only 2 have any long-form ≥100K.

### Cited Findings
- 77 channels with `age_days` ≤ 30; all 77 had uploads fetched (group `new_le_30d`) — OBSERVED, [channels.csv](data/channels.csv).
- English rule result: 59 English, 18 non-English (e.g. animacraft = Portuguese, BlockKahani = Hindi, Thanh = Russian, SlivaCraft = Polish-declared metadata with English titles, en share 0.44) — OBSERVED, [raw_uploads.json](data/raw_uploads.json) language fields + titles.
- 0–30 d, all / English: channels with any ≥100K video 20 / 16; with a long ≥100K 2 / 2; with a Short ≥100K 18 / 14; with any ≥1M 7 / 6; with a long ≥1M 1 / 1; with a Short ≥1M 6 / 5; with ≥2 long ≥1M 0 / 0; with ≥2 long ≥300K 1 / 1 (Day Zero) — OBSERVED, [uploads.csv](data/uploads.csv) ∪ [videos.csv](data/videos.csv).
- Video level for those 77 channels: 1,189 videos, 90 long; 79 videos ≥100K, of which 4 long; 17 videos ≥1M, of which 1 long — OBSERVED, same files.
- Note vs `api_dataset.md`: that note listed "15 channels ≤30 d with a ≥100K result" (search results only) and Day Zero's top as 370K; adding the uploads pull raises it to 20 channels and reveals Day Zero's older 1.89M long video, which no search query returned — OBSERVED, [api_dataset.md](api_dataset.md) vs [uploads.csv](data/uploads.csv).
- 31–180 d (wider net), all / English: 263 / 197 channels, but uploads were fetched only for the 97 / 75 with a ≥100K search result; any ≥1M 72 / 53; long ≥1M 5 / 4; ≥2 long ≥1M 2 / 1 (EvanavE — see §3 caveat; the other is RazoGames, Spanish); ≥2 long ≥300K 6 / 5 — OBSERVED, [channels.csv](data/channels.csv), [uploads.csv](data/uploads.csv).
- For context, 0–365 d English: 113 channels have a Short ≥1M but only 17 a long ≥1M and 8 have ≥2 long ≥1M — OBSERVED, same files.

### Inferences
- New-channel breakouts in this niche (Oct 2026) are a Shorts phenomenon; long-form breakouts at ≤30 d are rare (1 of 59 English channels) — INFERRED from the counts above. This sample is search-biased: a brand-new long-form channel that no 7/15-day query surfaced is invisible unless it also has a search hit (INFERRED).

### Gaps
- 166 of the 263 channels aged 31–180 d had no uploads pull, so their long-form history is unknown (OBSERVED gap in [channels.csv](data/channels.csv) `uploads_fetched`).
- Creation date = channel `publishedAt`, not first upload; About-page "Joined" was not checked (no scraping) — renamed/repurposed channels can look old or new.

## 2. Strict rule (created ≤30 d AND ≥2 long >3 min with ≥1M) — result and closest candidates

### Takeaway
**No channel qualifies** on the 2026-11-03 snapshot. Closest: **Day Zero** (29.2 d, original IP, 1 long at 1.89M + 1 long at 370K). Next long-form candidate: **Banazen Craft** (9.5 d, Maizen fan IP, 394K long in 2.25 d). Shorts-only 1M+ new channels: Ziggy Blox, Erzxck, CHIRAG FACTO, Verity Verifies MC, Mochi & Pals (+ SlivaCraft, non-English metadata).

### Cited Findings
All rows OBSERVED from [channels.csv](data/channels.csv) and [uploads.csv](data/uploads.csv); views/day = views ÷ max(age, 1 d).

**A. ≥1 long 1M+ (and ≥2 long 300K+): Day Zero** — https://www.youtube.com/channel/UCU9XwWmgsDdGRHXjrE0ewmQ — created 2026-10-05 (29.2 d), country TR but en-US audio, 13,900 subs, 4 videos, 2,253,707 total views.

| Video | Published | Dur | Views | ÷subs | Views/day |
|---|---|---|---|---|---|
| [I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft](https://www.youtube.com/watch?v=crnpqkov3ps) | 2026-10-07 | 52:00 | 1,894,197 | 136× (hundreds×) | 70,270 |
| [I Survived 100 Days in a DEADLY OUTBREAK in Minecraft](https://www.youtube.com/watch?v=eAqPRLb9JQg) | 2026-10-23 | 40:30 | 370,330 | 27× | 33,477 |

- Engagement on the 1.89M video: 23,734 likes (1.25%), 766 comments — OBSERVED. Description credits a Planet Minecraft map, lists a custom modpack, and says "focuses on cinematic story-telling ... may contain planned events"; cites ForgeLabs/OkRobert-style 100-day creators as inspiration — OBSERVED, [raw_uploads.json](data/raw_uploads.json).
- Rhythm: 2 long videos 16 days apart + two ~30–40 s Shorts on 2026-10-13 — OBSERVED.

**B. Long-form rising: Banazen Craft** — https://www.youtube.com/channel/UCK0DXOEQLQ_YkP2x1jddjsw — created 2026-10-25 (9.5 d), US, 4,290 subs, 3 videos (all long, 12–15 min), uploads every 3 days at 13:00 UTC.

| Video | Published | Dur | Views | ÷subs | Views/day |
|---|---|---|---|---|---|
| [JJ and Mikey Grow SECRET VERITY from Seeds in Minecraft!](https://www.youtube.com/watch?v=uah6ikSydJ8) | 2026-11-01 | 15:15 | 394,077 | 92× | 175,134 |
| [Only JJ Can SAVE His Friends from the GRAVE in Minecraft!](https://www.youtube.com/watch?v=IB4kSXJ1FrY) | 2026-10-29 | 11:52 | 110,367 | 26× | 21,018 |
| [JJ and Mikey Survive as CHICKENS on ONE BLOCK in Minecraft!](https://www.youtube.com/watch?v=zDBK1FX65jM) | 2026-10-26 | 12:15 | 59,946 | 14× | 7,285 |

- Description: "Independent fan-made Minecraft content inspired by Maizen" — OBSERVED. Third-party IP (JJ & Mikey + Verity mod entity).

**C. Shorts-only 1M+ channels created ≤30 d (English)**

| Channel (created, age, subs, videos) | 1M+ video (published, duration) | Views | ÷subs | Views/day |
|---|---|---|---|---|
| **Ziggy Blox** https://www.youtube.com/channel/UCVFgxz89Ond56851oZHAcrg (2026-10-10, 24.0 d, 61,100, 84) | [I Fooled a Million Zombies 😱](https://www.youtube.com/watch?v=vH0pd4SomN8) (10-21, 2:21) | 9,357,584 | 153× | 703,963 |
| | [I Pretended to Be a Mummy in a Real Pyramid](https://www.youtube.com/watch?v=1K1oIJp0yEg) (10-21, 2:15) | 3,236,484 | 53× | 245,206 |
| | [I Crashed the Biggest Skeleton Party Ever](https://www.youtube.com/watch?v=VU6eTOdYz1w) (10-27, 2:29) | 2,437,392 | 40× | 333,737 |
| | [I Fooled Herobrine's Whole Army](https://www.youtube.com/watch?v=bbj2gv4ZN4s) (10-21, 2:24) | 2,415,112 | 40× | 184,287 |
| | [I Crashed a Vampire Wedding](https://www.youtube.com/watch?v=H2a_oD4SK58) (10-25, 2:23) | 2,095,866 | 34× | 225,797 |
| | [I Snuck Into a World of Real Endermen](https://www.youtube.com/watch?v=9mqoXWhu3oo) (10-31, 2:14) | 1,045,363 | 17× | 313,516 |
| **Erzxck** https://www.youtube.com/channel/UCDCDdtu2ldfNCJJfrLEqRWw (2026-10-12, 21.8 d, 17,300, 22) | [Minecraft Verity Match The Block Game](https://www.youtube.com/watch?v=31tzZ_Y3n4c) (10-22, 1:15) | 12,072,020 | 698× | 1,023,115 |
| | [Minecraft Verity Plays Match The Block](https://www.youtube.com/watch?v=c4KIHOaQaOY) (10-20, 1:41) | 2,561,686 | 148× | 185,060 |
| | [Minecraft Verity Match The Block With Friends](https://www.youtube.com/watch?v=967RWA-E0m4) (10-26, 1:26) | 1,059,760 | 61× | 120,912 |
| **CHIRAG FACTO** https://www.youtube.com/channel/UC8Cp4n7CJBoY4sMOWdTSAGA (2026-10-23, 11.3 d, 26,000, 10) | [Slither Run with Steve - Funny Animation](https://www.youtube.com/watch?v=xel-UZ5bf1s) (11-01, 0:35) | 2,623,353 | 101× | 1,194,885 |
| | [Can Steve Win Memory Competition?!](https://www.youtube.com/watch?v=ckXQhXq8OPA) (10-23, 1:00) | 2,352,888 | 90× | 211,996 |
| | [Double Slither Run with Steve and Alex](https://www.youtube.com/watch?v=-tXgpPl45B4) (10-24, 0:32) | 1,751,593 | 67× | 168,412 |
| **Verity Verifies MC** https://www.youtube.com/channel/UCCQaqq9L_IaPw3FyLW1Rn5A (2026-10-25, 9.0 d, 1,790, 19; country SE) | [How To Breed Horses Perfectly...](https://www.youtube.com/watch?v=K7xFyRmxoB0) (10-30, 0:53) | 1,669,935 | 933× | 374,495 |
| | [How To Use Copper Golems Perfectly...](https://www.youtube.com/watch?v=3U2_rB7SrZ0) (10-29, 0:49) | 1,350,457 | 754× | 248,404 |
| **Mochi & Pals** https://www.youtube.com/channel/UC8BAM9FulzAucO3ENpk-yqA (2026-10-15, 19.7 d, 1,060, 6) | [Who can dig down the fastest?](https://www.youtube.com/watch?v=nf9oZPSqhjE) (11-01, 0:16) | 1,424,438 | 1,344× (thousands×) | 631,528 |
| *SlivaCraft* (non-English by rule) https://www.youtube.com/channel/UC9rNiDYJAsDRbYuQO2wvihQ (2026-10-05, 29.4 d, 1,780, 9; PL) | [Minecraft Mystery Transformation part 4](https://www.youtube.com/watch?v=Men-1Ggv3ms) (10-17, 0:41) | 1,331,193 | 748× | 75,346 |

- Erzxck's views jumped when its game Shorts switched from "Squishy" to the Verity character on 2026-10-20 (prior 7 Shorts 8K–40K; Verity Shorts 300K–12.07M) — OBSERVED, [uploads.csv](data/uploads.csv).
- CHIRAG FACTO descriptions carry "This video education propose only" and dozens of unrelated rap/XXXTentacion tags; comments 0–6 per video even at 2.6M views — OBSERVED, [raw_uploads.json](data/raw_uploads.json).
- Below 1M but notable ≤30 d English: parsamehrj (30.0 d) 828,473 Short "I Built a Farm ... Automatically Collects and Replants Items!" (767×); Ryu (16.9 d) 578,965 Death-Note-skit Short (274×); MineZox (3.6 d) 311,133 JJ-vs-Mikey hide-and-seek Short (1,496× on 208 subs); Clent (20.2 d, original wordless golem stories) 135,231 — OBSERVED.

### Inferences
- Day Zero is the only new channel whose long-form result is both large and plausibly organic (normal like/comment ratios) — INFERRED. With 1.89M on its 1st long video it needs one more long ≥1M; at 33K/day its 2nd video would need ~19 more days at constant pace (INFERRED, simple extrapolation; real decay is usually faster).
- Banazen Craft is the likeliest next strict-rule qualifier on raw velocity (175K/day at day 2), but it is Maizen fan content (INFERRED).

### Gaps
- Thumbnails were dropped from the raw JSON, so thumbnail hooks cannot be studied from this data; titles/descriptions/tags only.
- Whether Ziggy Blox's 2–2.5 min uploads are vertical Shorts or horizontal long-form ≤3 min cannot be told from the API fields stored.

## 3. Wider net (31–180 days): long-form 1M+ channels and caveats

### Takeaway
Four English channels aged 31–180 d have a long-form ≥1M video; three are third-party-IP (two Maizen fan channels, one Verity/Stalker-mod compilation) and one (EvanavE) has long-form numbers with near-zero engagement. The cleanest original-IP long-form signal in the wider net is **Kit vs The End** (37 d, 673K "Full Movie", 69× subs), not yet 1M.

### Cited Findings
All OBSERVED, [uploads.csv](data/uploads.csv) + [channels.csv](data/channels.csv):

| Channel (created, age, subs, videos) | Best long video | Published | Dur | Views | ÷subs | Views/day | Note |
|---|---|---|---|---|---|---|---|
| Mikey & JJ Verse https://www.youtube.com/channel/UCI4jqHZzPqg5aQEJSC4zn1g (2026-05-09, 178.7 d, 70,600, 51) | [JJ and Mikey: From POOR to RICH Chunk in Minecraft! (Maizen)](https://www.youtube.com/watch?v=6AGAgrvL77k) | 2026-07-24 | 20:52 | 2,504,006 | 35× | 24,463 | 13.9× its long median (180K) |
| Wablo https://www.youtube.com/channel/UCXwHTTvZxWXmoiXsitx8iog (2026-07-11, 114.9 d, 254,000, 101) | [torturing The stalker for 4 minutes and 19 seconds](https://www.youtube.com/watch?v=P4HsUyqCKg0) | 2026-10-07 | 4:19 | 2,392,986 | 9.4× | 88,691 | compilation of its Shorts; Short max 20,259,368 |
| Cody Toon https://www.youtube.com/channel/UC55HQXkPybptGkfRfniM77g (2026-09-01, 63.4 d, 43,400, 14) | [JJ and Mikey survival in DOUBLE PITS WITH ALL VERITY VERSIONS & LORD VERITY (Maizen)](https://www.youtube.com/watch?v=IYaWLDQnyZ4) | 2026-10-10 | 10:33 | 1,262,926 | 29× | 52,074 | 4 more long 600K–717K |
| EvanavE https://www.youtube.com/channel/UC6KDePyRnTj5EIUcJvCXVmQ (2026-05-31, 156.5 d, 39,200, 170) | [Trying to Beat Minecraft by Only Gambling](https://www.youtube.com/watch?v=uxS8Q7qknvg) / [Minecraft But Chunks are Random](https://www.youtube.com/watch?v=slA9oXtvFGo) | 10-03 / 09-28 | 2:59:09 / 4:01:13 | 1,143,625 / 1,141,803 | 29× | ~36K | 552 / 475 likes (0.05%), 2 / 0 comments |
| Kit vs The End https://www.youtube.com/channel/UCND-rtZrbxwcyz4qA5Bppkg (2026-09-27, 37.3 d, 9,730, 23; KW) | [Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship. One Sound And They Find You. (Full Movie)](https://www.youtube.com/watch?v=xdj5PL0t61k) | 2026-10-24 | 1:13:02 | 672,849 | 69× | 67,189 | 34× its median; 516 comments |
| MineBraintor https://www.youtube.com/channel/UCfrE3ETIQO906PeaUZoDC_w (2026-10-04, 30.6 d, 1,870, 29) | [Minecraft TNT Blast IN VILLAGE](https://www.youtube.com/watch?v=IdwH1fbtOkc) | 2026-10-28 | 1:24:34 | 982,323 | 525× | 166,491 | 4 "live" uploads 516K–982K; likes hidden, 0 comments, `#shortslive #verticallive` |

- Kit vs The End tags/description: "stickman", "zombie survival story, day by day", second-person narration ("You lock your cabin door ... they follow the light"), "all of Season 1 in one video" — OBSERVED, [raw_uploads.json](data/raw_uploads.json).
- Older (181–365 d) English channels with ≥2 long ≥1M, for reference: imKaiL00L (204 d, 5; "Horror Minecraft, but Drops are Guns" 2.96M), Ding & Doge (300 d, 4), BionicTV (258 d, 4), Clooless Gaming (348 d, 2), SirCloaked (346 d, 2; "Minecraft's NEW Verity Mod VS Falsity" 2.47M), Chase Liminal (240 d, 2; "Poolrooms - The Snake Lady (Backrooms)" 2.05M on 16.6K subs = 123×), TechyClips (253 d, 2) — OBSERVED.
- RazoGames (MX, 169 d, 5.5M subs, 18 long ≥1M) is Spanish-language and excluded by the English rule — OBSERVED.

### Inferences
- EvanavE and MineBraintor long-form "1M" are distribution anomalies (live/vertical-live surfaces, 3–6 h VODs, ≤0.1% likes or hidden likes, ~0 comments) rather than a format to copy — INFERRED from engagement ratios; I would exclude them from any "long-form benchmark" median.
- Kit vs The End's tags say "stickman", so it may not be Minecraft-rendered at all even though Minecraft queries surfaced it (INFERRED). Its format (survival structure) still transfers.

### Gaps
- No retention/CTR; cannot verify whether anomalous views are bot-driven or genuine live-surface traffic.

## 4. Third-party IP vs original characters

### Takeaway
Among the 16 English ≤30 d channels with a ≥100K video, 8 lean on third-party IP (JJ & Mikey/Maizen, Verity mod entity, Poppy Playtime/Guga, Death-Note skit meme, Radiant SMP creators) and 8 use original or Mojang-only characters. But of the 6 English ≤30 d channels with a 1M+ video, 5 are original/Mojang-only (Day Zero, Ziggy Blox, CHIRAG FACTO, Verity Verifies MC [name only], Mochi & Pals); only Erzxck relies on a third-party character (Verity). In the 31–180 d long-form 1M+ set, 3 of 4 are third-party IP.

### Cited Findings
- Manual classification from titles/tags/descriptions (OBSERVED text, classification INFERRED), [uploads.csv](data/uploads.csv), [raw_uploads.json](data/raw_uploads.json):
  - Third-party: Banazen Craft (JJ & Mikey + Verity; "fan-made ... inspired by Maizen"), Erzxck (Verity), MineZox (description "Can JJ outsmart Mikey"), DiaxGold Crafts (JJ & JJ Sister), ZynBlocks (JJ Sister), BlaBlaEnding (Gugugaga, Mommy Long Legs, CatNap, Verity), Ryu (#deathnote skit format, PumpBrine-style "Smartest player vs"), RL Secondary7 (Radiant SMP / Yes Smarty Pie clips).
  - Original or Mojang-only: Day Zero (own story, modpack, credited maps), Ziggy Blox (first-person hero + zombies/Herobrine/Endermen), CHIRAG FACTO (Steve & Alex), Verity Verifies MC (gameplay tips; borrows the name "Verity" only), Mochi & Pals (Mochi, Pickles, Bubbles), parsamehrj (farm tutorials), Clent (snow golem/iron golem wordless stories), BlockyFacts (facts).
- "Verity" is a Minecraft horror-mod entity, not a game character from Mojang: descriptions say "#veritymod", "credit ... LCrandom the owner of entitys", "inspired by @ThatMob ... FALSITY is from @xqree's video" — OBSERVED, Wablo / SirCloaked descriptions in [raw_uploads.json](data/raw_uploads.json).
- 31–180 d long ≥1M: Mikey & JJ Verse and Cody Toon both credit "Original Maizen channel: @maizenofficial"; Wablo credits LCrandom's Stalker entity; EvanavE is mod gameplay — OBSERVED.
- Existing watchlist correction: Ligabka's long-form hits are Maizen fan IP ("MAIZEN - JJ and Love JJ SISTER - ❤️ Love Story !?" 2,255,130; "MAIZEN - JJ and LOVE QUEEN" 725,965), while its Shorts use its own persona "LIGABKA" vs "POWERSTUDIOS"/"NULL" — OBSERVED, [uploads.csv](data/uploads.csv).

### Inferences
- For a studio bound to original IP (Bin, Bo, baby zombie Zu), the encouraging signal is that the biggest ≤30 d breakouts did not need borrowed characters; what they borrowed was **format** (100 days, disguise/infiltration POV, "who can X fastest", tip ellipsis) — INFERRED.
- Maizen fan channels show the JJ & Mikey sub-niche still converts new channels to long-form 300K–2.5M; that demand can be addressed with an original duo + kid sibling + monster friend dynamic without names/skins — INFERRED; legal/policy risk of fan IP is a separate question not studied here.

### Gaps
- Visual similarity (skins, character designs) cannot be judged from metadata; a channel classed "original" by text may still use look-alike skins.

## 5. Study of the million-view videos (title, length, IP, format, hooks, rhythm)

### Takeaway
Million-view new-channel videos cluster into five repeatable formats: (1) **100-days cinematic survival** (40–52 min, "I Survived 100 Days in a [ADJ] [threat]"), (2) **first-person disguise/infiltration mini-stories** (2–2.5 min, "I Fooled/Pretended/Crashed/Snuck ..."), (3) **character game-show Shorts** ("Match the Block", "Who can X fastest?", 15–100 s), (4) **"How To X Perfectly..." tip Shorts** (~50 s), (5) **Maizen-style duo adventures** (10–21 min, "JJ and Mikey [verb] SECRET/POOR to RICH ..."). Long-form winners stack a concrete threat + a numeric frame (100 days, a million zombies) + a rule.

### Cited Findings
- Title patterns (OBSERVED, titles in [uploads.csv](data/uploads.csv)):
  - 100-days: "I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft" (1.89M), "... DEADLY OUTBREAK ..." (370K); wider net "Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship. One Sound And They Find You. (Full Movie)" (673K) — caps on the threat adjective; a survival rule in the title.
  - First-person transgression + absurd scale + emoji: Ziggy Blox "I Fooled a Million Zombies 😱", "I Pretended to Be a Mummy in a Real Pyramid 😳🐪", "I Crashed a Vampire Wedding💀", "I Got Locked in the World's Biggest Mall 😱" (984,859). Description = stakes + rule: "any human found before sunrise becomes the Zombie King's butler forever."
  - Game-show/competition: "Minecraft Verity Match The Block Game 🟡", "Who can dig down the fastest?", "Who can build the tallest tower?" (223,441 at 0.9 d), "Slither Run with Steve", "Can Steve Win Memory Competition?!".
  - Tip with ellipsis: "How To Breed Horses Perfectly...", "How To Use Copper Golems Perfectly..." (Copper Golem = recent vanilla mob).
  - Duo adventure: "JJ and Mikey Grow SECRET VERITY from Seeds", "From POOR to RICH Chunk", "survival in DOUBLE PITS WITH ALL VERITY VERSIONS & LORD VERITY" — CAPS nouns, "SECRET", "ALL ... VERSIONS".
- Lengths (OBSERVED): Day Zero long median 46 min; Banazen 12–15 min; Cody Toon median 10:18; Mikey & JJ Verse median 19 min; Kit vs The End movie 73 min (channel median long 10:45); Ziggy Blox median 2:14; Erzxck Shorts median 1:15; Mochi & Pals 13–17 s; Verity Verifies MC ~47 s.
- Upload rhythm (OBSERVED, published_at): Day Zero 1 long / ~16 d; Banazen Craft 1 long / 3 d at 13:00 UTC; Cody Toon ~2 long / week at 13:00 UTC; Mikey & JJ Verse ~2 long / week at 10:30 UTC; Ziggy Blox ~3.5 uploads / day (84 videos in 24 d); Erzxck 1 Short / day ~23:00 UTC; Verity Verifies MC ~2 / day; CHIRAG FACTO ~1 / day; Mochi & Pals ~1 / day since 2026-10-25.
- Speed (OBSERVED): the fastest new-channel 1M+ videos hit ≥600K/day in their first 2–3 days (CHIRAG 1.19M/day at 2.2 d; Mochi & Pals 632K/day at 2.3 d; Erzxck 1.02M/day averaged over 11.8 d).
- Engagement (OBSERVED): Day Zero 1.25% likes / 4.0 comments per 10K views; Kit vs The End 0.99% / 7.7; Cody Toon 1.7–2.9% / 0.7–2.9; Ziggy Blox 1.1–1.9% / 0.1–0.6; Mochi & Pals 0.48% / 0.2.

### Inferences
- The long-form format with an original-IP path to 1M at a new channel is **story-driven survival with a day counter** (Day Zero, Kit vs The End): explicit rule ("one sound and they find you"), escalating set pieces, cinematic framing, 40–75 min — INFERRED.
- The ~2-minute first-person "I [did a forbidden disguise] among [huge crowd of monsters]" format (Ziggy Blox) is a strong seed for long-form episode premises (each title is a 10-minute story logline) — INFERRED.
- Ultra-short character competitions (Mochi & Pals) are the cheapest way to test original-character appeal before long-form — INFERRED.

### Gaps
- No thumbnails, no retention curves, no audio/visual review: under CLAUDE.md research policy, any "we learned X from competitor Y" claim about acting, editing or visuals still needs the competitor full-viewing gate; this note covers metadata only.

## 6. Existing watchlist and the updated file `data/watchlist_2026-11-04.csv`

### Takeaway
The updated watchlist has 32 channels: the 13 existing ones (all status `old`), 8 new ≤30 d channels (status `new`), and 11 older/wider-net channels added as `old` because they currently have outliers. Only 8 of the 13 existing watchlist channels appear in this API sample, and only 2 (Ligabka, JJ Cartoons) have upload histories.

### Cited Findings
- Existing watchlist read: [config/research/minecraft_story_watchlist.txt](../../config/research/minecraft_story_watchlist.txt) (13 channels; it already states that none met the 0–30 d + 2×1M rule on 2026-11-03) — OBSERVED.
- In this sample: Maizen (4 search videos), MSToons (4), Cubeee Animations (1), Ligabka (50 uploads), MyMy toon (1), Морфиз (1), JJ Cartoons (14 uploads), ZomBo (1). Not in sample: BigSchool, GameToons, Mine Block, Class Monster School, DL Minecraft — OBSERVED, [channels.csv](data/channels.csv). For those 5, the CSV keeps the subs/joined values from the old watchlist (labelled so in `notes`).
- No separate "PC-side watchlist summary" exists in the data notes folder; the only watchlist sources are the `.txt` above and its rules file — OBSERVED (directory listing of `research_notes/` and `config/research/`).
- Status rule used in the CSV: `new` = created ≤30 d at first_seen (2026-11-03) and added today; everything else `old`. Per OWNER rules (B), every listed channel is tracked from now on with the old-competitor rules — OWNER, [minecraft_story_rules.md](../../config/research/minecraft_story_rules.md).
- New (`new`): Day Zero, Banazen Craft, Ziggy Blox, Erzxck, CHIRAG FACTO (policy red flags noted), Verity Verifies MC, Mochi & Pals, SlivaCraft. Added `old`: Mikey & JJ Verse, Cody Toon, Wablo, MineBraintor (flagged suspect), EvanavE (flagged suspect), Kit vs The End, Chase Liminal, imKaiL00L, Spoke, Bench Animation (43 d, 237K subs, 13 Shorts ≥1M, max 8.50M), Gamity (49 d, 1.73M Short = 1,108×) — OBSERVED, [watchlist_2026-11-04.csv](data/watchlist_2026-11-04.csv).

### Inferences
- The old `.txt` watchlist should be refreshed from the CSV by the main session (I did not modify `config/`); subs in the CSV come from the API where available, which differ slightly from the old file (e.g. Ligabka 68.8K → 69,000; Cubeee 49.7K → 50,100) — INFERRED that growth/rounding explains it.

### Gaps
- BigSchool, GameToons, Mine Block, Class Monster School, DL Minecraft have no fresh numbers today; next quota day should pull their uploads (≈1 unit each via playlistItems + videos.list).

## 7. Old/leader channels with outlier videos right now (owner rules: views ≫ subs; ≤15 d and far above the channel's other videos; explosive first 5 days)

### Takeaway
Operationalised as R1 = views ≥10× subs and ≥500K; R2 = age ≤15 d, ≥3× the channel's same-format median (median ≥1,000) and ≥300K; R3 = age ≤5 d and (≥100K views/day with ≥2× median, or ≥5× median with ≥100K). 45 English long-form videos on channels >30 d old meet at least one rule. The strongest current long-form outliers relevant to story/animation are Cubeee's 54-min compilation (2.20M at 7 d, 44×), Ligabka's 8-min love story (726K at 4.3 d, 167K/day), Kit vs The End (673K, 34× median), Spoke (13.37M, 3.8× median), and Chase Liminal / imKaiL00L for horror.

### Cited Findings
All OBSERVED, [uploads.csv](data/uploads.csv) (same-format medians as computed by the collector) and [videos.csv](data/videos.csv):

| Channel (subs) | Video | Age d | Dur | Views | ÷subs | ×median | Views/day | Rule |
|---|---|---|---|---|---|---|---|---|
| Spoke (2.91M) | [10,000 Players Simulate COLD WAR in Minecraft](https://www.youtube.com/watch?v=y5IdSoHdkgg) | 11.8 | 4:00 h | 13,373,694 | 4.6× | 3.8× | 1,134,342 | R2 |
| Cubeee Animations (50.1K; watchlist) | [MAIZEN : ALL EPISODE JJ Sister LOVES JJ](https://www.youtube.com/watch?v=g-GgM-kVnNs) | 7.1 | 54:29 | 2,196,144 | 44× | n/a (search-only) | 310,940 | R1 |
| Ligabka (69K; watchlist) | [MAIZEN - JJ and LOVE QUEEN - ❤️ LOVE STORY !?](https://www.youtube.com/watch?v=10vzXGySExY) | 4.3 | 8:06 | 725,965 | 10.5× | 1.6× | 167,528 | R1 + fast first 5 d |
| Kit vs The End (9.7K) | [Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship ... (Full Movie)](https://www.youtube.com/watch?v=xdj5PL0t61k) | 10.0 | 1:13 h | 672,849 | 69× | 34× | 67,189 | R1 R2 |
| imKaiL00L (241K) | [Horror Minecraft, but Drops are Guns](https://www.youtube.com/watch?v=H6yj4XbkHhk) | 92 | 23:18 | 2,958,110 | 12× | 5.3× | 32,080 | R1 |
| Chase Liminal (16.6K) | [Poolrooms - The Snake Lady (Backrooms)](https://www.youtube.com/watch?v=VRrWXv1S1M4) | 94 | 10:11 | 2,049,362 | 123× | 3.5× | 21,743 | R1 |
| Chase Liminal | [Poolrooms - Mini Golf (Backrooms)](https://www.youtube.com/watch?v=4UgGJkBi6UM) | 26 | 5:16 | 921,334 | 56× | 1.6× | 35,038 | R1 |
| アシュch (455K) | [Minecraft's Most Satisfying Moments (Compilation)](https://www.youtube.com/watch?v=rNbHC6BalS4) | 11.2 | 13:37 | 1,057,976 | 2.3× | 9.5× | 94,665 | R2 |
| Cobweb (42.1K) | [Beating Players with PvP kits only I know how to use](https://www.youtube.com/watch?v=X9ZXFM5a6jg) | 6.0 | 9:39 | 579,221 | 14× | 3.8× | 96,572 | R1 R2 |
| Niz unseen (118K) | [1 Pro Builder vs 3 Creative Noobs](https://www.youtube.com/watch?v=3TfB6zDs9Jg) | 1.4 | 19:46 | 321,577 | 2.7× | 2.3× | 232,785 | R3 |
| BacTi (2.69K) | [Animation Battles - Verity Mod Minecraft Characters #13](https://www.youtube.com/watch?v=T9ik9Tj_r9I) | 4.2 | 8:49 | 340,652 | 127× | 38× | 80,354 | R2 R3 |
| noblevox (9.9K) | [Interrogating Parrot (found footage)](https://www.youtube.com/watch?v=TprsWvdq7Zs) | 3.9 | 4:48 | 219,370 | 22× | 501× | 55,727 | R3 |
| Mikey & JJ Verse (70.6K) | [JJ and Mikey: From POOR to RICH Chunk](https://www.youtube.com/watch?v=6AGAgrvL77k) | 102 | 20:52 | 2,504,006 | 35× | 13.9× | 24,463 | R1 |
| Cody Toon (43.4K) | [... DOUBLE PITS WITH ALL VERITY VERSIONS ...](https://www.youtube.com/watch?v=IYaWLDQnyZ4) | 24 | 10:33 | 1,262,926 | 29× | 4.4× | 52,074 | R1 |

- Shorts outliers on leaders (R2/R3, English): lowkiMC "This feels like a scene from interstellar 🥹" 18,855,299 at 2.8 d (565× its median, 6.76M/day); Beazle 2,219,048 at 2.1 d on 8,360 subs (245× median); MSToons Shorts "JJ and Mikey Guess the MONSTER.EXE Inside" 22,754,579 at 13.1 d (30× median); PumpBrine "Smartest Player VS Dr Donut" 12,534,983 at 6.1 d (40× median); darix "Kpop Head Noob Pro Trap Challenge Part 12" 8,018,131 at 7.0 d (53× median, 319× subs) — OBSERVED.
- Other high views÷subs Shorts on young-but->30 d channels: JPAUL "JINU When RUMI is Calling" 17,747,707 on 12K subs (1,479×, K-pop Demon Hunters IP); ClayBoom (31 d) 4,255,039 at 2.0 d (541×); SWEETY BLOCK (34 d) 1,943,971 (525×) — OBSERVED.
- Counting: 231 channels >30 d old have upload histories; 205 of them have ≥1 video meeting R1/R2/R3 (1,305 videos, 48 long) — OBSERVED. R1 alone is loose on small channels.

### Inferences
- Compilations/"Full Movie"/"ALL EPISODE" re-cuts are a recurring long-form outlier mechanism (Cubeee 54 min, Kit 73 min, アシュch compilation, Wablo 4:19) — INFERRED: cheap minutes from existing material; directly relevant to the KPI "approved finished minutes per week".
- Horror-liminal (Backrooms/Poolrooms, found footage) gives the highest views÷subs on small long-form channels outside the Maizen-verse — INFERRED.

### Gaps
- Same-format median includes the video itself and, for Shorts-heavy channels, may rest on few long uploads; long ×median values on channels with <5 long uploads are weak.

## 8. What Bin, Bo and baby zombie Zu can legitimately learn (no characters, names, skins, scripts or footage copied)

### Takeaway
Learn structure, titles and packaging mechanics, not characters: the 100-day cinematic survival arc (Day Zero / Kit vs The End), the first-person disguise logline (Ziggy Blox), the character mini-competition test (Mochi & Pals), the season-to-"Full Movie" compilation, and the duo-plus-sibling relationship engine that powers the Maizen-verse — all re-expressed with Bin, Bo and Zu.

### Cited Findings
- Day Zero — structure: day counter, realistic modpack, credited third-party maps, "planned events ... gameplay itself is real" disclosure; we can use an original story with an explicit day counter and disclosed staging — OBSERVED description, [raw_uploads.json](data/raw_uploads.json).
- Kit vs The End — hook: one survival rule in the title ("One Sound And They Find You"), second-person stakes, Season 1 compiled into a 73-min movie — OBSERVED.
- Ziggy Blox — logline template "[POV] disguised among [huge number of monsters]; if caught before [deadline], [funny penalty]" — OBSERVED description of "I Fooled a Million Zombies".
- Mochi & Pals — 3 original characters, each with a distinct method ("Bubbles has another way..."), 13–17 s, one question title — OBSERVED.
- Erzxck — the same game format lifted from ~30K to 12M when a recognisable character was swapped in (2026-10-20) — OBSERVED; lesson: character recognisability drives Shorts, so our cast needs a consistent look and repetition, not borrowed IP.
- Policy cautions: CHIRAG FACTO's irrelevant tag stuffing and "education purpose only" text; MineBraintor's hidden likes/looping "live" — OBSERVED; these conflict with our policy-check (tag stuffing, misleading metadata) rules in CLAUDE.md — OWNER.

### Inferences
- Concrete original adaptations (INFERRED, for the showrunner, not decisions): "Bin & Bo Survive 100 Days Hiding Baby Zombie Zu in a Zombie City" (day-counter arc + secret-friend stakes); "Bo Pretends to Be a Zombie to Rescue Zu — If the Horde Finds Out, ..." (disguise logline); Shorts "Who can dig the fastest? Bin vs Bo vs Zu" to test which character the audience prefers; monthly "Full Movie" compilation of the season.
- Avoid: any JJ/Mikey/Verity/Sprunki/Poppy/Rumi names in titles or tags (even as tags), since several third-party-IP channels self-label as fan-made and their long-term risk is unmeasured — INFERRED.

### Gaps
- Not measured: whether original-IP channels sustain views after the first breakout (only 4–29 days of history for the new ones). Re-check Day Zero, Mochi & Pals, Ziggy Blox and Banazen Craft on the next quota day (≈1–2 units per channel).
