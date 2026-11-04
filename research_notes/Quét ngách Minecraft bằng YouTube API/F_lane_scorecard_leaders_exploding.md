# F — Minecraft lanes: 5-criteria scorecard, lane leaders' outliers (ĐỐI THỦ 1), exploding videos (ĐỐI THỦ 3)

Snapshot: targeted lane scan, YouTube Data API v3, **2026-11-04 12:00–12:05 UTC** (`data/2026-11-04/`). Context comes from the broad scan of **2026-11-03 19:00–19:05 UTC** (`data/`) and from the 16.8 h re-snapshot `resnapshot_24h.csv` (s2 2026-11-03 ~19:16Z → s3 2026-11-04 ~12:05Z).

No API calls were made for this note; quota is spent. The analysis uses only files that already exist.

Labels follow CLAUDE.md:
- **OBSERVED** = counted from those files, with the snapshot date.
- **INFERRED** = my reasoning, including every 1–5 score.
- **OWNER** = the owner said so.

Helper CSVs are `data/2026-11-04/derived_F_*.csv`. The code that produced them is in `data/2026-11-04/derived_F_code/` (run order in `README.txt`).

**Bottom line (INFERRED from OBSERVED 2026-11-04 data).** No lane wins on all five criteria. Under the explicit scoring rules in §2.2 the ranking is:

| rank | lane | score /25 (format lanes) | score /25 (query-lane check) |
|---|---|---|---|
| 1 | scripted survival / "movie" | **20** | 21 |
| 2 | lore/facts | 17 | 17 |
| 3 | mob/army battle sims | 16 | 19 |
| 4 | mystery/horror | 15 | 15 |
| 4 | AI in Minecraft | 15 | 15 |
| 4 | "Minecraft but" | 15 | 15 |
| 7 | family/emotional animation | 13 | 14 |
| 8 | interactive Shorts | 11 | 14 |

For an original-IP studio I recommend three lanes:
1. **Long-form scripted survival with a mystery/threat hook** as the main lane.
2. **Command-driven mob/physics battle sims** as the Shorts funnel, with tournament long-forms.
3. **AI-in-Minecraft (local-LLM bots) long-form** as a test lane, with own-universe mechanics/lore Shorts.

This agrees with the OWNER's three lanes: horror-mystery universe (main), Day 1→100 survival (secondary), experiment/fact Shorts (test). The data argues for one change: make the **survival "movie" the main vehicle and use mystery as its hook**. Pure mystery/horror long-form has fewer newcomer hits (§5).

---

## 1. Method & filters

**Pool (OBSERVED, lane scan 2026-11-04).** The scan returned 1,814 unique videos. Filters removed them in this order:
- 455 failed the English rule.
- 207 failed the Minecraft rule.
- 23 were off-topic (all from *ohnepixel raw*, a DE CS2 channel).
- 38 were found **only** by the creator-name expansion queries `minecraft verity` / `minecraft maizen`. Those queries select third-party IP by construction.

That leaves a **pool of 1,091 videos (605 Shorts, 486 long-form)**. 226 of them match none of the eight lane rules (mostly memes and builds).

The rules behind each filter:
- **English (same rule as notes A/C, `derived_A_code/alang.py`).** `default_audio_language` must be blank, `zxx` or `en*`. If audio is blank or `zxx`, `default_language` must be blank or `en*`. The title must not be foreign: ≥15% non-Latin letters, or ≥2 non-English function words, fails it.
- **Minecraft.** The video passes if any of these holds:
  - "minecraft"/"mcyt"/"mc" appears in the title, tags or channel name (1,087 videos).
  - The 2026-11-03 raw description mentions it (11 videos; descriptions exist only for ids in yesterday's pull).
  - The channel is a Minecraft channel (31 videos). That means ≥10% of the channel's known uploads name Minecraft, or >0% and the title uses Minecraft vocabulary, and the title names no other game.
  - **Sensitivity:** 63 videos match Minecraft vocabulary only (21 of them ≥1M). They are *excluded*. The biggest are not Minecraft: *Nobody Gets In* and *Beanie Survives* are stickman-animation zombie-survival channels, per their tags (§4.4).
- **Shorts** = duration ≤180 s.
- **Third-party IP flag (title only; tags are SEO-stuffed).** Families flagged:
  - Maizen JJ/Mikey
  - Verity/Lovity/Falsity/Cruelty
  - Sprunki
  - Poppy Playtime/Huggy
  - K-pop Demon Hunters (Rumi/Jinu)
  - Skibidi/cameraman
  - Dr Donut
  - Jerry the dog/wolf
  - MrBeast
  - Dream/SMP creators
  - Italian brainrot
  - other franchises (Sonic, Peppa, Undertale/Deltarune, Godzilla, FNAF, Death Note, Alan Becker AVM, Sadako, Miku…)

  A creator's own characters on their own channel are not third-party (e.g. Maizen, Dr Donut Clips). **Herobrine (and Entity 303/Null) is Mojang lore**, so it is flagged separately and not counted as third-party.
- **Mega-personality channels** are excluded from "room for new channels" denominators. A fixed list of 39 names: MrBeast Gaming, Dream, Maizen, Joeysaf, dayta, Cayce, Spoke, Parrot, Forge Labs, CaseOh, Cash, Jazzghost, PrestonPlayz, Aphmau and others (`common.py: MEGA`).
- **Lanes = title-format rules, multi-label** (`lanes.py`), applied the same way to:
  - every pool video, whichever query found it;
  - yesterday's broad scan;
  - every upload sample.

  The search-query lanes are noisy: only 40–84% of a query lane's pool results match its format (AI 40%, lore 55%, interactive 61%, "but" 69%, mystery 72%, battle 73%, family 77%, survival 84%; OBSERVED). Examples: "who will win minecraft" returned MrBeast Gaming, and "minecraft AI" returned Dream. As a robustness check, the whole scorecard is recomputed with query-lane membership (`derived_F_lane_*_querylanes.csv`). Animated comedy skits (BlobbyClips type) belong to none of the 8 lanes, so they get an extra row.
- **Kid tone** = a title lexicon (baby/family/sad/mom/noob/choose/who will win/💔🥺…). It is a proxy, not audience data. Only 4 pool videos carry `made_for_kids=true`.
- **Newcomer** = channel ≤365 d old **or** <100K subs. "Newcomer-original" also requires the video to have no third-party flag.
- **Leader outlier rules.** Channel medians are recomputed the same way for both pulls: same-format uploads aged ≥3 d (if there are ≥3), otherwise all.
  - *Outlier ≤30 d* = views ≥3× the same-format median, **or** views ≥ subs.
  - *Explosive ≤5 d* = views/day ≥2× the channel's median views/day of same-format uploads aged 3–30 d, **or** already ≥1× the channel's same-format median.
- **Growth labels (re-snapshot).** `decel_ratio` = views/h over the 16.8 h gap ÷ lifetime average views/h.
  - accelerating ≥1.0
  - steady 0.4–1.0
  - decaying <0.4
  - frozen = 0 new views

  A video naturally slows with age, so "steady" at 5–10 days is already strong (INFERRED).

## 2. Lane scorecard

### 2.1 Metrics

| lane | fmt | n (ch) | median | p90 | ≥1M | non-mega ≥100K hits | of those: ch ≤12 mo / ≤90 d / ≤30 d / <100K subs | non-mega ≥1M hits: ≤12 mo / ≤90 d / ≤30 d / <100K | orig-IP share of ≥100K | median views÷subs | MFK flag / kid-tone | long-form share of lane views |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| survival/movie | short | 9 (9) | 1K | 1.46M | 3 | 4 | 25% / 0% / 0% / 25% | 3: 33% / 0% / 0% / 0% | 100% | 14.55 | 0 / 11% | 97% |
| survival/movie | long | 109 (87) | 363K | 1.62M | 23 | 76 | 16% / 4% / 4% / 26% | 19: 11% / 5% / 5% / 16% | 86% | 1.19 | 0 / 4% |  |
| mystery/horror | short | 67 (62) | 32K | 983K | 7 | 24 | 33% / 4% / 0% / 54% | 7: 29% / 14% / 0% / 43% | 58% | 6.93 | 1 / 9% | 73% |
| mystery/horror | long | 81 (59) | 356K | 2.09M | 23 | 49 | 10% / 2% / 0% / 10% | 17: 12% / 0% / 0% / 6% | 82% | 0.71 | 1 / 4% |  |
| family/emotional anim | short | 221 (117) | 422K | 2.55M | 72 | 160 | 42% / 20% / 2% / 52% | 72: 46% / 21% / 0% / 50% | 34% | 5.52 | 1 / 72% | 21% |
| family/emotional anim | long | 62 (42) | 359K | 2.91M | 19 | 48 | 6% / 0% / 0% / 25% | 16: 0% / 0% / 0% / 19% | 45% | 0.72 | 1 / 69% |  |
| interactive Shorts | short | 127 (86) | 107K | 1.97M | 24 | 65 | 43% / 15% / 5% / 57% | 23: 57% / 13% / 4% / 48% | 44% | 2.63 | 0 / 83% | 9% |
| interactive Shorts | long | 19 (18) | 108K | 1.31M | 3 | 8 | 0% / 0% / 0% / 12% | 1: 0% / 0% / 0% / 0% | 70% | 0.72 | 0 / 53% |  |
| mob/army battle sim | short | 44 (26) | 143K | 2.09M | 10 | 22 | 59% / 50% / 45% / 82% | 6: 67% / 33% / 17% / 83% | 69% | 10.31 | 0 / 9% | 68% |
| mob/army battle sim | long | 118 (81) | 110K | 920K | 12 | 56 | 5% / 2% / 0% / 30% | 8: 0% / 0% / 0% / 12% | 63% | 0.99 | 1 / 13% |  |
| AI in Minecraft | short | 18 (16) | 47K | 1.39M | 4 | 8 | 38% / 12% / 0% / 62% | 4: 25% / 0% / 0% / 25% | 88% | 4.49 | 0 / 17% | 53% |
| AI in Minecraft | long | 23 (20) | 68K | 1.25M | 3 | 10 | 10% / 10% / 0% / 30% | 3: 0% / 0% / 0% / 0% | 90% | 1.33 | 0 / 0% |  |
| lore/facts | short | 50 (42) | 181K | 1.42M | 6 | 31 | 32% / 16% / 0% / 58% | 6: 67% / 17% / 0% / 50% | 90% | 5.52 | 0 / 12% | 9% |
| lore/facts | long | 24 (19) | 8K | 402K | 1 | 3 | 0% / 0% / 0% / 67% | 1: 0% / 0% / 0% / 0% | 100% | 2.73 | 0 / 0% |  |
| "Minecraft but"/roleplay | short | 68 (32) | 2.19M | 5.95M | 48 | 28 | 46% / 7% / 4% / 64% | 14: 36% / 0% / 0% / 43% | 85% | 6.02 | 0 / 35% | 27% |
| "Minecraft but"/roleplay | long | 77 (50) | 427K | 2.01M | 22 | 59 | 10% / 3% / 0% / 19% | 14: 7% / 0% / 0% / 0% | 76% | 0.52 | 0 / 40% |  |
| skit/comedy (extra) | short | 11 (7) | 2.96M | 16.47M | 7 | 9 | 22% / 0% / 0% / 22% | 7: 14% / 0% / 0% / 14% | 67% | 17.77 | 0 / 0% | 0% |
| skit/comedy (extra) | long | 0 | | | | | | | | | | |

### 2.2 Scoring rules (explicit; every score is INFERRED from the OBSERVED inputs in T2)

- **RPM (higher = better)** = 1 + a + b + c, clipped to 1–5.
  - a = long-form share of lane views: ≥80% → 3, 60–80% → 2, 30–60% → 1, else 0.
  - b = kid-tone share: ≥50% → −1, ≤15% → +1, else 0.
  - c = +1 for lore only. This is the background prior from `reports/Ngách Minecraft RPM cao bền vững.md`: lore/storytelling $3–6, a weak estimate. The same report gives gaming long-form ~$2–3.4, Kids/MFK ~$0.33–0.49 and Shorts 3–14% of long-form.
- **Low risk** = 5 minus three penalties, clipped to 1–5.
  - Third-party share of ≥100K hits: ≥40% → −2, 15–40% → −1.
  - Kid tone ≥50% or any MFK flag → −1 (MFK/COPPA risk).
  - "Templated" share of ≥100K hits ≥30% → −1. Templated means "Part N/Ep N" titles, or titles whose normalised first 3 words are shared by ≥3 hits; this approximates the repetitive/inauthentic-content risk.
- **Sustainable** = 1 + b1 + b2 + b3, clipped to 1–5.
  - b1 = +1 if the lane has ≥3 videos ≥1M both today and in yesterday's ≤15-day set.
  - b2 = format age: ≥5 channels with an on-format ≥1M upload older than 180 d in the upload samples → +2; ≥3 → +1.
  - b3 = +1 if the third-party share is <15% (not riding someone else's IP wave).
- **Huge views** = score from the median of on-format videos: ≥500K → 4, ≥250K → 3, ≥100K → 2, else 1. Plus 1 if p90 ≥2.5M.
- **Newcomer room** = share of non-mega ≥100K hits that are original-IP **and** from a newcomer channel: ≥40% → 5, 30–40% → 4, 20–30% → 3, 10–20% → 2, else 1. Minus 1 when there are <25 non-mega ≥100K hits or <5 such newcomer channels (thin evidence).

### 2.3 Scores

| lane | long share of views | kid-tone | 3P-IP share of ≥100K | templated share of ≥100K | ≥1M both days (today / 03-Nov ≤15 d) | channels with a ≥1M on-format upload >180 d old | median all | p90 all | newcomer-original share of non-mega ≥100K (videos / channels) | RPM | Low risk | Sustainable | Huge views | Newcomer room | **Total /25** | total with query-lane membership |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| survival/movie | 97% | 4% | 13% | 35% | 26 / 16 | 5 (oldest 2023-12-02) | 334K | 1.63M | 29% (23/21) | 5 | 4 | 5 | 3 | 3 | **20** | 21 |
| mystery/horror | 73% | 6% | 25% | 16% | 30 / 18 | 4 (oldest 2023-06-17) | 133K | 1.41M | 25% (18/15) | 4 | 3 | 3 | 2 | 3 | **15** | 15 |
| family/emotional anim | 21% | 71% | 64% | 17% | 91 / 100 | 8 (oldest 2025-01-08) | 405K | 2.87M | 17% (36/29) | 1 | 2 | 4 | 4 | 2 | **13** | 14 |
| interactive Shorts | 9% | 79% | 53% | 21% | 27 / 42 | 4 (oldest 2023-06-17) | 108K | 1.78M | 23% (17/15) | 1 | 2 | 3 | 2 | 3 | **11** | 14 |
| mob/army battle sim | 68% | 12% | 35% | 28% | 22 / 19 | 6 (oldest 2023-12-09) | 113K | 1.46M | 28% (22/18) | 4 | 3 | 4 | 2 | 3 | **16** | 19 |
| AI in Minecraft | 53% | 7% | 11% | 0% | 7 / 0 | 1 (oldest 2025-11-28) | 55K | 1.38M | 44% (8/8) | 3 | 5 | 2 | 1 | 4 | **15** | 15 |
| lore/facts | 9% | 8% | 9% | 9% | 7 / 4 | 2 (oldest 2025-01-08) | 72K | 871K | 56% (19/15) | 3 | 5 | 3 | 1 | 5 | **17** | 17 |
| "Minecraft but"/roleplay | 27% | 38% | 19% | 43% | 70 / 40 | 4 (oldest 2024-01-02) | 867K | 3.80M | 28% (24/19) | 1 | 3 | 3 | 5 | 3 | **15** | 15 |
| skit/comedy (extra) | 0% | 0% | 33% | 0% | 7 / 27 | 1 (oldest 2025-08-05) | 2.96M | 16.47M | 22% (2/2) | 2 | 4 | 2 | 5 | 2 | **15** |  |

### 2.4 What the scorecard says (INFERRED unless a number is quoted)

**1. Scripted survival / "movie" is the only lane that is long-form, original and old at the same time (all OBSERVED 2026-11-04).**
- 97% of lane views are long-form.
- 87% of ≥100K hits are original IP; kid tone is 4%.
- ≥1M hits: 26 today and 16 in yesterday's ≤15-day set.
- 5 channels have ≥1M on-format uploads older than 180 d (Forge Labs' 100-day outbreak films: 14.8–26.0M at 2.3–2.7 years).
- Its weak point is room: only 16% of non-mega ≥100K long-form hits come from channels ≤12 months old, and the median views÷subs is 1.19.

**2. Mystery/horror long-form performs like survival, but newcomers rarely break in.**
- Long-form median is 356K (OBSERVED).
- Only 10% of non-mega ≥100K long hits come from channels ≤12 months old, and 6% of ≥1M hits come from <100K-subs channels (OBSERVED).
- The lane's Shorts side is horror-clip compilations (Rank it Laughs).

**3. Family/emotional animation and interactive Shorts have the most demand and the most newcomers, but are the worst fit for the studio.**
- Family: 91 ≥1M hits today and 100 yesterday (OBSERVED).
- About 46–57% of ≥1M Shorts come from ≤12-month channels (OBSERVED).
- Both lanes are 53–64% third-party IP and 71–79% kid tone (OBSERVED), so RPM is low and COPPA/MFK risk is high. This matches BigSchool's history in note D.

**4. Mob/army battle sims split in two.**
- *Player-simulation wars* (Spoke, Parrot, FlameFrags, SpeedSilver: 2.5–13.7M, 2.5–4 h) need thousands of real players, so they cannot be reproduced.
- *Command mob-vs-mob / physics sims* have the **most newcomer-friendly Shorts of any lane**:
  - 82% of non-mega ≥100K battle Shorts come from <100K-subs channels, and 45% from channels ≤30 d old (OBSERVED).
  - These come from only 6 newcomer channels, and the top one, Brawl Lab, has 40% of them.
  - Long-form command battles have a median of only 71K, with one ≥1M among 70 videos (OBSERVED). Long-form RPM in this sub-lane is unproven.
- With query-lane membership the lane scores 19/25.

**5. "Minecraft but" has the biggest Shorts numbers, but mega channels own them.**
- Median Short is 2.19M (OBSERVED).
- 34 of 68 Shorts are from mega channels (Joeysaf, dayta, Cayce).
- 43% of ≥100K hits are templated (OBSERVED).
- As a premise device inside survival episodes it is free; as a lane it is crowded.

**6. AI in Minecraft and lore/facts are the most open lanes, on thin evidence.**
- AI: 89–91% original and 44–56% newcomer-original among ≥100K hits (OBSERVED).
- Both are small: AI has 41 on-format videos and 0 ≥1M in yesterday's ≤15-day set; lore long-form has a median of 8K (OBSERVED).
- They are cheap tests, not proven lanes.

**Robustness.** With query-lane membership the top three are survival 21, battle 19 and lore 17. Mystery, AI and "but" stay at 15. Family rises to 14 and interactive to 14 (OBSERVED). The ranking of the top lanes holds.

## 3. ĐỐI THỦ 1 — lane leaders, their outliers, and what the outliers share

**How leaders were chosen.**
- Top 5 channels per lane by summed on-format 30-day views in the pool ("top").
- Top 4 non-mega channels whose on-format hits carry no third-party flag and whose upload sample is <30% third-party ("orig-IP").
- If a leader has no upload sample, the next channel with one (rank ≤15) is analysed instead.

**Upload samples.** Today's pull (`lane_uploads.csv`, 2026-11-04 ~12:01Z) is used first; otherwise yesterday's (`uploads.csv`, 2026-11-03 ~19:03Z). Each holds ≤50 uploads per channel, so a Shorts-heavy channel's sample can cover under 2 weeks.

Every row in the tables is OBSERVED with the snapshot date shown. Outlier tables list **on-format** uploads only. The "What the outliers share" paragraphs are INFERRED from the listed titles and lengths; nothing was watched (see §6).

### 3.1 Leaders: survival/movie

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | MrBeast Gaming (mega) | 61.10M | 2402 | 72.73M (1) | [h8VE9_aHd94](https://www.youtube.com/watch?v=h8VE9_aHd94) $10,000 Every Day You Survive In Minecraft — 72.73M, 24.8 d, long | 2026-11-04, n=50 | 56.94M / 55.41M / 68.91M | 4 | 0% | 20 min | 1 / 0 |
| top | 2 | Forge Labs (mega) | 6.28M | 7094 | 8.46M (1) | [jccqEa0Qd40](https://www.youtube.com/watch?v=jccqEa0Qd40) 1 Year in Alaska in ULTRA REALISTIC Minecraft — 8.46M, 24.7 d, long | 2026-11-04, n=50 | 2.84M / 3.21M / 151K | 1 | 2% | 180 min | 1 / 0 |
| top | 3 | Maizen (mega) | 17.90M | 2138 | 5.00M (1) | [UH1HSIN4L20](https://www.youtube.com/watch?v=UH1HSIN4L20) Zombie Outbreak — 5.00M, 10.5 d, long | 2026-11-04, n=50 | 510K / 2.02M / 442K | 36 | 2% | 24 min | 0 / 1 |
| top | 4 | aCookieGod | 8.18M | 3627 | 3.90M (1) | [NvoKphWCXXk](https://www.youtube.com/watch?v=NvoKphWCXXk) I Survived 100 Days on ONE CHEST in Minecraft Hardcore — 3.90M, 25.0 d, long | none | – | – | – | – | – |
| top | 5 | EYstreem | 13.90M | 5346 | 3.75M (2) | [1y0fQKWFzEI](https://www.youtube.com/watch?v=1y0fQKWFzEI) I Survived 100 Days as VERITY in Minecraft — 2.17M, 12.5 d, long | 2026-11-04, n=50 | 1.98M / 2.36M / 444K | 10 | 12% | 26 min | 0 / 0 |
| top | 10 | Day Zero | 14K | 30 | 2.29M (2) | [crnpqkov3ps](https://www.youtube.com/watch?v=crnpqkov3ps) I Survived 100 Days in a REALISTIC APOCALYPSE in Minec… — 1.91M, 27.7 d, long | 2026-11-04, n=4 | 193K / 1.14M / 9K | 4 | 0% | 46 min | 2 / 0 |
| orig-IP | 1 | aCookieGod | 8.18M | 3627 | 3.90M (1) | [NvoKphWCXXk](https://www.youtube.com/watch?v=NvoKphWCXXk) I Survived 100 Days on ONE CHEST in Minecraft Hardcore — 3.90M, 25.0 d, long | none | – | – | – | – | – |
| orig-IP | 2 | Jynxzi | 7.09M | 2480 | 3.65M (2) | [5RnuKa0iPqw](https://www.youtube.com/watch?v=5RnuKa0iPqw) PLAYING HARDCORE MINECRAFT UNTIL WE BEAT IT DAY 4 — 1.89M, 26.5 d, long | none | – | – | – | – | – |
| orig-IP | 3 | MineLand | 5.19M | 1506 | 2.49M (1) | [GtxjQRWV5E0](https://www.youtube.com/watch?v=GtxjQRWV5E0) Minecraft Survival Bamboo House....🤔 (Training Season)… — 2.49M, 23.2 d, short | none | – | – | – | – | – |
| orig-IP | 4 | Day Zero | 14K | 30 | 2.29M (2) | [crnpqkov3ps](https://www.youtube.com/watch?v=crnpqkov3ps) I Survived 100 Days in a REALISTIC APOCALYPSE in Minec… — 1.91M, 27.7 d, long | 2026-11-04, n=4 | 193K / 1.14M / 9K | 4 | 0% | 46 min | 2 / 0 |
| orig-IP | 11 | Clooless Gaming | 319K | 348 | 1.40M (2) | [n06Hx1wLgfY](https://www.youtube.com/watch?v=n06Hx1wLgfY) Trying To Survive A Modded Minecraft Zombie Apocalypse — 892K, 23.6 d, long | 2026-11-04, n=50 | 485K / 485K / – | 8 | 10% | 50 min | 8 / 1 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [frYFifKDofo](https://www.youtube.com/watch?v=frYFifKDofo) | Forge Labs | I Spent 100 Days in an Evolved Parasite Outbreak in Hardcore Minecraf… | 983.9 | 25.97M | 232 min | 8.1× | 0.1× | 6.28M |  |
| [vRJtFetkA1Q](https://www.youtube.com/watch?v=vRJtFetkA1Q) | Forge Labs | I Spent 100 Days in a Flood Apocalypse in Hardcore Minecraft... Here'… | 948.9 | 17.66M | 240 min | 5.5× | 0.1× | 6.28M |  |
| [I3odKRhgPnQ](https://www.youtube.com/watch?v=I3odKRhgPnQ) | Forge Labs | I Spent 100 Days in a Fungal Outbreak in Hardcore Minecraft... Here's… | 822.0 | 14.81M | 222 min | 4.6× | 0.1× | 6.28M |  |
| [hjEljGsdD8U](https://www.youtube.com/watch?v=hjEljGsdD8U) | EYstreem | I Survived 100 Days as HOUSE HEAD in Minecraft | 117.4 | 9.94M | 28 min | 4.2× | 1.1× | 13.90M |  |
| [wFggR039O24](https://www.youtube.com/watch?v=wFggR039O24) | EYstreem | I Survived 100 Days as INFECTED SKY in Minecraft | 151.4 | 8.43M | 23 min | 3.6× | 0.8× | 13.90M |  |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [jccqEa0Qd40](https://www.youtube.com/watch?v=jccqEa0Qd40) | Forge Labs | 1 Year in Alaska in ULTRA REALISTIC Minecraft | 24.7 | 8.46M | 180 min | 2.6× | 1.0× | 6.28M |  |
| [n06Hx1wLgfY](https://www.youtube.com/watch?v=n06Hx1wLgfY) | Clooless Gaming | Trying To Survive A Modded Minecraft Zombie Apocalypse | 23.6 | 892K | 56 min | 1.8× | 1.0× | 319K |  |
| [crnpqkov3ps](https://www.youtube.com/watch?v=crnpqkov3ps) | Day Zero | I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft | 27.7 | 1.91M | 52 min | 1.7× | 1.4× | 14K |  |
| [h8VE9_aHd94](https://www.youtube.com/watch?v=h8VE9_aHd94) | MrBeast Gaming | $10,000 Every Day You Survive In Minecraft | 24.8 | 72.73M | 58 min | 1.3× | 0.9× | 61.10M |  |
| [RTVtQOfe2oU](https://www.youtube.com/watch?v=RTVtQOfe2oU) | Clooless Gaming | 4 Idiots Try To Survive Slenderman! | 9.6 | 586K | 41 min | 1.2× | 1.6× | 319K |  |
| [Du3-onARPlg](https://www.youtube.com/watch?v=Du3-onARPlg) | Clooless Gaming | THE MINECRAFT ZOMBIE APOCALYPSE GOT OUT OF CONTROL | 20.6 | 508K | 47 min | 1.0× | 0.7× | 319K |  |
| [eAqPRLb9JQg](https://www.youtube.com/watch?v=eAqPRLb9JQg) | Day Zero | I Survived 100 Days in a DEADLY OUTBREAK in Minecraft | 11.8 | 376K | 40 min | 0.3× | 0.6× | 14K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median): none in the samples.*

**What the survival outliers share (INFERRED from the titles above):**
- **Long runtime.** The ≤30-day outliers are 40–60 min; Forge Labs runs 3–4 h. Same-channel non-outliers are about 25 min.
- **Title formula.** "I Survived/Spent **100 Days** in a [ADJ] [THREAT] (in Hardcore) Minecraft" — threats like Apocalypse, Outbreak, Flood or Parasite. Variants: "Trying To Survive A Modded Minecraft Zombie Apocalypse" and "[N] Idiots Try To Survive X".
- **Premise.** An escalating environmental threat plus a visible timer (Day 1 → 100, 1 Year).
- **Cast.** A solo narrator or a small friend group.
- **Hook word.** "REALISTIC" / "ULTRA REALISTIC" appears in the two strongest recent outliers: Forge Labs 8.46M and Day Zero 1.91M.
- **IP.** No third-party characters apart from EYstreem's "as VERITY", which was not an outlier.
- **Newcomer case.** Day Zero has 4 uploads and 2 long videos at 0.38M and 1.91M on a 30-day-old channel, so the formula plus a long runtime works with no audience at all.

### 3.2 Leaders: mystery/horror

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | CaseOh (mega) | 11.30M | 5511 | 11.90M (5) | [GF4RGA8daaE](https://www.youtube.com/watch?v=GF4RGA8daaE) This Might Be The Scariest Minecraft Horror Mod…ep 1 — 4.71M, 25.6 d, long | none | – | – | – | – | – |
| top | 2 | Mayamystic | 12.70M | 4319 | 8.46M (1) | [dJE_fhBkc7s](https://www.youtube.com/watch?v=dJE_fhBkc7s) Do you know Jerry the dog ? #minecraft #cosplay #minec… — 8.46M, 29.8 d, short | none | – | – | – | – | – |
| top | 3 | ProBoiz 95 | 9.41M | 2391 | 6.46M (1) | [ls0FQdzVxko](https://www.youtube.com/watch?v=ls0FQdzVxko) Testing Trending Minecraft Scary Myths To See If They … — 6.46M, 6.9 d, long | 2026-11-04, n=50 | 8.99M / 8.94M / 10.33M | 2 | 6% | 29 min | 0 / 0 |
| top | 4 | AlphaExtra | 1.06M | 1887 | 5.46M (3) | [i2o9XJctd0I](https://www.youtube.com/watch?v=i2o9XJctd0I) Alpha vs Tikawar: Scary Verity's Maze Statue Battle In… — 2.84M, 21.0 d, long | none | – | – | – | – | – |
| top | 5 | Karry Kraft | 1.77M | 1572 | 4.16M (2) | [s8ZEQ4fZhkM](https://www.youtube.com/watch?v=s8ZEQ4fZhkM) Busting Hidden SCARY MYTHS in Minecraft.. — 2.16M, 18.0 d, long | none | – | – | – | – | – |
| top | 6 | Maizen (mega) | 17.90M | 2138 | 3.93M (1) | [BCIEA_QMWmc](https://www.youtube.com/watch?v=BCIEA_QMWmc) I BUILT A ZOO FOR EVERY HORROR MOB In Minecraft — 3.93M, 14.0 d, long | 2026-11-04, n=50 | 510K / 2.02M / 442K | 36 | 2% | 24 min | 0 / 1 |
| top | 9 | imKaiL00L | 241K | 205 | 2.44M (2) | [1ncAcHzjW1c](https://www.youtube.com/watch?v=1ncAcHzjW1c) Horror One Block, But Drops are Guns — 1.95M, 22.9 d, long | 2026-11-04, n=50 | 177K / 560K / 38K | 9 | 0% | 24 min | 5 / 1 |
| top | 12 | SirCloaked | 141K | 347 | 2.18M (2) | [EYyB2uwb9o0](https://www.youtube.com/watch?v=EYyB2uwb9o0) Something Is Wrong With My Farm... — 1.21M, 23.0 d, long | 2026-11-04, n=50 | 271K / 467K / 149K | 5 | 4% | 18 min | 2 / 0 |
| orig-IP | 1 | ProBoiz 95 | 9.41M | 2391 | 6.46M (1) | [ls0FQdzVxko](https://www.youtube.com/watch?v=ls0FQdzVxko) Testing Trending Minecraft Scary Myths To See If They … — 6.46M, 6.9 d, long | 2026-11-04, n=50 | 8.99M / 8.94M / 10.33M | 2 | 6% | 29 min | 0 / 0 |
| orig-IP | 2 | Karry Kraft | 1.77M | 1572 | 4.16M (2) | [s8ZEQ4fZhkM](https://www.youtube.com/watch?v=s8ZEQ4fZhkM) Busting Hidden SCARY MYTHS in Minecraft.. — 2.16M, 18.0 d, long | none | – | – | – | – | – |
| orig-IP | 3 | Zachobuilds | 866K | 3166 | 3.23M (1) | [P1Nk0VJLU9A](https://www.youtube.com/watch?v=P1Nk0VJLU9A) Finding The End Of The Skin Caves — 3.23M, 24.8 d, long | none | – | – | – | – | – |
| orig-IP | 4 | imKaiL00L | 241K | 205 | 2.44M (2) | [1ncAcHzjW1c](https://www.youtube.com/watch?v=1ncAcHzjW1c) Horror One Block, But Drops are Guns — 1.95M, 22.9 d, long | 2026-11-04, n=50 | 177K / 560K / 38K | 9 | 0% | 24 min | 5 / 1 |
| orig-IP | 7 | SirCloaked | 141K | 347 | 2.18M (2) | [EYyB2uwb9o0](https://www.youtube.com/watch?v=EYyB2uwb9o0) Something Is Wrong With My Farm... — 1.21M, 23.0 d, long | 2026-11-04, n=50 | 271K / 467K / 149K | 5 | 4% | 18 min | 2 / 0 |
| orig-IP | 15 | Rank it Laughs | 263K | 253 | 1.12M (1) | [9ULv8twx2ac](https://www.youtube.com/watch?v=9ULv8twx2ac) Top 3 Funniest Minecraft Horror Mod Moments 😂 (Bro has… — 1.12M, 6.8 d, short | 2026-11-04, n=50 | 205K / – / 205K | 18 | 12% | – | 3 / 3 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [jAORyZRoBPo](https://www.youtube.com/watch?v=jAORyZRoBPo) | Rank it Laughs | These Minecraft Horror Mods Had Me Screaming 💀😭 #minecraft #horrorgam… | 36.8 | 10.06M | 59 s | 49.2× | 36.0× | 263K |  |
| [Zwic7sO3uQo](https://www.youtube.com/watch?v=Zwic7sO3uQo) | Rank it Laughs | Minecraft Horror Mods Were NOT Ready for This 😭 #minecraft #horrorgam… | 62.8 | 8.41M | 55 s | 41.1× | 17.6× | 263K |  |
| [xCjyZHA___E](https://www.youtube.com/watch?v=xCjyZHA___E) | Rank it Laughs | Top 3 Minecraft Horror Mod Moments That Sent Me To Heaven 💀 #minecraf… | 48.8 | 8.05M | 67 s | 39.3× | 21.7× | 263K |  |
| [BCIEA_QMWmc](https://www.youtube.com/watch?v=BCIEA_QMWmc) | Maizen | I BUILT A ZOO FOR EVERY HORROR MOB In Minecraft | 14.0 | 3.93M | 56 min | 2.0× | 2.0× | 17.90M |  |
| [H6yj4XbkHhk](https://www.youtube.com/watch?v=H6yj4XbkHhk) | imKaiL00L | Horror Minecraft, but Drops are Guns | 92.9 | 2.96M | 23 min | 5.3× | 1.1× | 241K |  |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [5psl2aC8b10](https://www.youtube.com/watch?v=5psl2aC8b10) | Rank it Laughs | Top 3 Horror Moments That Completely Broke Me 😂 #horrorgaming #shorts | 26.8 | 1.31M | 58 s | 6.4× | 6.4× | 263K |  |
| [9ULv8twx2ac](https://www.youtube.com/watch?v=9ULv8twx2ac) | Rank it Laughs | Top 3 Funniest Minecraft Horror Mod Moments 😂 (Bro has 0 survival ins… | 6.8 | 1.12M | 68 s | 5.5× | 21.5× | 263K |  |
| [M2ONo7feQbM](https://www.youtube.com/watch?v=M2ONo7feQbM) | Rank it Laughs | Top 3 Times Horror Games Made Players FORGET HOW TO BREATHE 😭 #horror… | 13.8 | 998K | 43 s | 4.9× | 9.5× | 263K |  |
| [1ncAcHzjW1c](https://www.youtube.com/watch?v=1ncAcHzjW1c) | imKaiL00L | Horror One Block, But Drops are Guns | 22.9 | 1.95M | 30 min | 3.5× | 3.0× | 241K |  |
| [EYyB2uwb9o0](https://www.youtube.com/watch?v=EYyB2uwb9o0) | SirCloaked | Something Is Wrong With My Farm... | 23.0 | 1.21M | 16 min | 2.6× | 0.7× | 141K |  |
| [VYFy1FN7-tk](https://www.youtube.com/watch?v=VYFy1FN7-tk) | SirCloaked | Something On My Farm Wants Me Dead... | 9.0 | 970K | 19 min | 2.1× | 1.3× | 141K |  |
| [YrHfnPh4Yw8](https://www.youtube.com/watch?v=YrHfnPh4Yw8) | imKaiL00L | Gun Minecraft, but Horror Mobs Evolve | 8.9 | 487K | 25 min | 0.9× | 1.9× | 241K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [Eff-hsDLJbM](https://www.youtube.com/watch?v=Eff-hsDLJbM) | Rank it Laughs | Top 3 Funniest FNAF Moments (Freddy Gave Me a Heart Attack 😭🥀) #fnaf … | 2.8 | 69K | 70 s | 0.3× | 3.2× | 263K | other_franchise |
| [KDPNupc0EQI](https://www.youtube.com/watch?v=KDPNupc0EQI) | Rank it Laughs | 💀 Top 3 Funniest Horror Game Moments (Bro Got DEVOURED 😭) #horrorgami… | 0.8 | 24K | 65 s | 0.1× | 3.2× | 263K |  |
| [dlqusksD9ng](https://www.youtube.com/watch?v=dlqusksD9ng) | Rank it Laughs | Top 3 Funniest Horror Game Moments (Bro's soul left through his mouth… | 4.8 | 105K | 33 s | 0.5× | 2.9× | 263K |  |

**What the mystery/horror outliers share (INFERRED):**
- **Mundane-place-gone-wrong titles** in first person with an ellipsis: SirCloaked's "Something Is Wrong With My Farm..." and "Something On My Farm Wants Me Dead...", at 16–19 min.
- **Mashups of "horror" with a rule twist:** imKaiL00L's "Horror One Block, But Drops are Guns", 30 min, 3.5×.
- **Myth-testing** from big channels: ProBoiz "Testing Trending Minecraft Scary Myths…", 40 min.
- **Exploration mystery:** Zachobuilds "Finding The End Of The Skin Caves", 3.23M at 866K subs.
- **Episodic horror-mod series with a personality:** CaseOh "…ep N", which is mega.
- **Shorts side:** "Top 3 Funniest Minecraft Horror Mod Moments 😂" compilations (Rank it Laughs, up to 49× median). These are probably clips of other people's gameplay, so reused-content risk (INFERRED, not watched).
- **IP.** Almost no third-party IP in long-form (89% original).

### 3.3 Leaders: family/emotional anim

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | MSToons | 1.77M | 3273 | 22.97M (7) | [qtWfSIqNfdU](https://www.youtube.com/watch?v=qtWfSIqNfdU) JJ's Girl EAT JJ CAKE - Maizen Minecraft Animation — 7.03M, 29.9 d, long | 2026-11-04, n=50 | 1.86M / 1.86M / – | 11 | 100% | 11 min | 6 / 2 |
| top | 2 | Manic Craft | 66K | 40 | 20.29M (8) | [vmIQJJXOaFU](https://www.youtube.com/watch?v=vmIQJJXOaFU) Dog Jerry And Tom Sing Together Minecraft Animation #m… — 5.67M, 29.0 d, short | 2026-11-04, n=50 | 25K / – / 25K | 50 | 68% | – | 9 / 14 |
| top | 3 | FoxiLu | 74K | 690 | 15.40M (7) | [JIqeCzFHnJM](https://www.youtube.com/watch?v=JIqeCzFHnJM) JJ made the wrong choice in Minecraft 😱🥺 #minecraft #s… — 3.41M, 14.7 d, short | 2026-11-04, n=32 | 236K / – / 236K | 32 | 100% | – | 23 / 4 |
| top | 4 | The Albo | 93K | 192 | 12.67M (3) | [ygr5ZjLOIXM](https://www.youtube.com/watch?v=ygr5ZjLOIXM) Perfect World Trend (Minecraft Animation) — 6.52M, 16.9 d, short | 2026-11-04, n=50 | 168K / – / 168K | 29 | 18% | – | 26 / 3 |
| top | 5 | Alex Drawly | 1.45M | 1572 | 12.32M (3) | [VL7IThMS1Bs](https://www.youtube.com/watch?v=VL7IThMS1Bs) Why Did Falsity Let Papa Verity WIN the Race? 🥹🏁 Minec… — 6.18M, 16.9 d, short | 2026-11-04, n=50 | 62K / 56K / 64K | 50 | 86% | 9 min | 10 / 12 |
| orig-IP | 1 | The Albo | 93K | 192 | 6.52M (1) | [ygr5ZjLOIXM](https://www.youtube.com/watch?v=ygr5ZjLOIXM) Perfect World Trend (Minecraft Animation) — 6.52M, 16.9 d, short | 2026-11-04, n=50 | 168K / – / 168K | 29 | 18% | – | 26 / 3 |
| orig-IP | 2 | Butter Penguin | 431K | 950 | 6.14M (1) | [vyzWa7jz9Kc](https://www.youtube.com/watch?v=vyzWa7jz9Kc) Mud Slime Treatment! 🩹 - Minecraft Animation — 6.14M, 25.1 d, short | none | – | – | – | – | – |
| orig-IP | 3 | BabyCrab | 639K | 607 | 5.57M (8) | [7BZG05gIoQs](https://www.youtube.com/watch?v=7BZG05gIoQs) Baby Steve vs. Baby Zombie — which character do you pr… — 1.14M, 27.0 d, short | none | – | – | – | – | – |
| orig-IP | 4 | TeardownTown | 66K | 1030 | 4.24M (1) | [qz8T9dFbFSQ](https://www.youtube.com/watch?v=qz8T9dFbFSQ) How Many Baby Zombies will Destroy Giant Steve? #minec… — 4.24M, 20.7 d, short | none | – | – | – | – | – |
| orig-IP | 6 | Brineycraft | 817K | 341 | 2.82M (2) | [UwvYtsG409I](https://www.youtube.com/watch?v=UwvYtsG409I) Herobrine Vs Steve, Push Challenge - Minecraft Animati… — 2.22M, 19.1 d, short | 2026-11-04, n=50 | 2.30M / – / 2.30M | 15 | 18% | – | 6 / 1 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [EMpBSspZGG4](https://www.youtube.com/watch?v=EMpBSspZGG4) | Brineycraft | Herobrine & Strong Steve Vs Spider Sister - Minecraft Animation | 64.2 | 40.52M | 15 s | 17.6× | 12.3× | 817K |  |
| [NMzB_oX_6a4](https://www.youtube.com/watch?v=NMzB_oX_6a4) | Brineycraft | Herobrine Vs Strong Steve, High Level Punch Machine - Minecraft Anima… | 36.2 | 38.14M | 15 s | 16.6× | 20.5× | 817K |  |
| [iT4JGguG8VA](https://www.youtube.com/watch?v=iT4JGguG8VA) | Brineycraft | Herobrine Vs Super Steve, New Spider Zombie - Minecraft Animation | 81.1 | 33.46M | 18 s | 14.5× | 8.0× | 817K |  |
| [WHpNapdjfoQ](https://www.youtube.com/watch?v=WHpNapdjfoQ) | MSToons | JJ was Buried Under The Water - Maizen Minecraft Animation | 62.8 | 8.23M | 11 min | 4.4× | 0.9× | 1.77M | maizen_jj_mikey |
| [W7R8k10Kjfk](https://www.youtube.com/watch?v=W7R8k10Kjfk) | MSToons | JJ VERITY vs Mikey CURIOSITY! - Maizen Minecraft Animation | 31.9 | 7.87M | 14 min | 4.2× | 1.6× | 1.77M | maizen_jj_mikey|verity_cruelty |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [ygr5ZjLOIXM](https://www.youtube.com/watch?v=ygr5ZjLOIXM) | The Albo | Perfect World Trend (Minecraft Animation) | 16.9 | 6.52M | 15 s | 38.8× | 16.1× | 93K |  |
| [5pfZXSWVWes](https://www.youtube.com/watch?v=5pfZXSWVWes) | The Albo | Jerry and Tom (Minecraft Animation) | 25.9 | 4.33M | 17 s | 25.8× | 7.0× | 93K | jerry_wolf_dog |
| [5WY9jUfLhmo](https://www.youtube.com/watch?v=5WY9jUfLhmo) | The Albo | Jerry and Tom Original vs My Version (Minecraft Animation) | 25.0 | 3.31M | 17 s | 19.7× | 5.5× | 93K | jerry_wolf_dog |
| [zxNzFLFlc9M](https://www.youtube.com/watch?v=zxNzFLFlc9M) | Alex Drawly | Verity Choose School or Home 🤔😱 / Minecraft Animation #shorts | 9.9 | 1.09M | 6 s | 17.2× | 11.7× | 1.45M | verity_cruelty |
| [mnZuRCVAPbo](https://www.youtube.com/watch?v=mnZuRCVAPbo) | The Albo | Jerry and Lookout3d Red Line Trend (Minecraft Animation) | 24.0 | 2.84M | 8 s | 16.9× | 5.0× | 93K | jerry_wolf_dog|other_franchise |
| [k4H74ZDHAF8](https://www.youtube.com/watch?v=k4H74ZDHAF8) | FoxiLu | Bunny Girl picked JJ else over Mikey 😭🏠 #minecraft #sadstory #maizen … | 11.7 | 3.76M | 29 s | 15.9× | 17.6× | 74K | maizen_jj_mikey |
| [JIqeCzFHnJM](https://www.youtube.com/watch?v=JIqeCzFHnJM) | FoxiLu | JJ made the wrong choice in Minecraft 😱🥺 #minecraft #sadstory #maizen… | 14.7 | 3.41M | 44 s | 14.4× | 12.7× | 74K | maizen_jj_mikey |
| [13-EI5573Bg](https://www.youtube.com/watch?v=13-EI5573Bg) | FoxiLu | Which JJ is Real? Dark JJ tricked! 🤔💔 #minecraft #sadstory #maizen #j… | 15.7 | 3.38M | 46 s | 14.3× | 11.8× | 74K | maizen_jj_mikey |
| [TtmmFOu8CzU](https://www.youtube.com/watch?v=TtmmFOu8CzU) | Alex Drawly | How Many CLAPPING CATS Can You Find? 🐱 #cat #funny #minecraft #minecr… | 7.5 | 834K | 7 s | 13.1× | 11.8× | 1.45M | other_franchise |
| [8RLm_8McObo](https://www.youtube.com/watch?v=8RLm_8McObo) | The Albo | Angry calm trend (Minecraft Animation) | 20.0 | 1.95M | 13 s | 11.6× | 4.1× | 93K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [8iDpNWjxhs8](https://www.youtube.com/watch?v=8iDpNWjxhs8) | Manic Craft | Verity And Thatmob Argue In Minecraft New Update Animation #minecraft… | 1.0 | 51K | 17 s | 2.0× | 11.4× | 66K | verity_cruelty |
| [zeAbe5ieeFU](https://www.youtube.com/watch?v=zeAbe5ieeFU) | Manic Craft | We Are Eggchan In A Perfect World In Minecraft New Update Animation #… | 3.7 | 185K | 8 s | 7.3× | 11.3× | 66K |  |
| [uuzK-XW9GGc](https://www.youtube.com/watch?v=uuzK-XW9GGc) | Manic Craft | Teto And Miku Dance In Minecraft New Update Animation #minecraftshort… | 0.7 | 50K | 8 s | 2.0× | 11.2× | 66K | other_franchise |
| [KluGoov5yoQ](https://www.youtube.com/watch?v=KluGoov5yoQ) | Brineycraft | Herobrine, I scared my Girlfriend and Bros - Minecraft Animation | 4.1 | 2.14M | 14 s | 0.9× | 10.1× | 817K |  |
| [B3k9u6eUVG0](https://www.youtube.com/watch?v=B3k9u6eUVG0) | Manic Craft | Eggchan And Wemmbu Unstable SMP In Minecraft New Update Animation #mi… | 1.9 | 84K | 13 s | 3.3× | 10.0× | 66K | dream_smp_creators |

**What the family/emotional outliers share (INFERRED):**
- **Very short Shorts:** 6–50 s.
- **Mostly third-party casts:** JJ/Mikey ("Why JJ Couldn't Impress [Animal] Girl 💔" is a numbered-variation series by FoxiLu at 7–16×), Verity/Lovity, Jerry & Tom/Lookout3D.
- **Original-IP outliers fall into three types:**
  - *Trend-audio remakes:* The Albo "Perfect World Trend (Minecraft Animation)", 6.52M, 39× median; "Angry calm trend My Version vs Original".
  - *Mojang-cast power or challenge escalations:* Brineycraft "Herobrine Vs Strong Steve, High Level Punch Machine", 38–41M at 817K subs.
  - *Mojang cast plus a horror figure:* CHAnimationsClips "Herobrine vs Sadako & Alex". Sadako is third-party.
- **Common devices:** a Steve/Alex/Herobrine cast, a power ladder or trend audio, an emoji-loaded title, a kid tone.
- **Long-form:** 11-min Maizen fan stories from MSToons, where 100% of uploads are third-party.

### 3.4 Leaders: interactive Shorts

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | FoxiLu | 74K | 690 | 8.84M (3) | [JIqeCzFHnJM](https://www.youtube.com/watch?v=JIqeCzFHnJM) JJ made the wrong choice in Minecraft 😱🥺 #minecraft #s… — 3.41M, 14.7 d, short | 2026-11-04, n=32 | 236K / – / 236K | 32 | 100% | – | 23 / 4 |
| top | 2 | Tg Jamal Shorts 44 | 24K | 315 | 6.39M (2) | [uTjxhkO1_SE](https://www.youtube.com/watch?v=uTjxhkO1_SE) Which One Would You Guys Choose? — 4.44M, 8.2 d, short | 2026-11-04, n=50 | 49K / – / 49K | 50 | 2% | – | 42 / 7 |
| top | 3 | Cayce (mega) | 278K | 1351 | 6.23M (1) | [nLHOu9MC6ZQ](https://www.youtube.com/watch?v=nLHOu9MC6ZQ) Minecraft But I GUESS COLORS — 6.23M, 10.5 d, short | 2026-11-04, n=50 | 1.72M / – / 1.72M | 13 | 0% | – | 12 / 1 |
| top | 4 | Peppa Up | 532K | 292 | 6.05M (1) | [M1jxa2gfjkU](https://www.youtube.com/watch?v=M1jxa2gfjkU) Who Can Get Their Body Back, Peppa or Suzy? #peppapig … — 6.05M, 26.0 d, short | 2026-11-04, n=50 | 220K / – / 220K | 11 | 100% | – | 3 / 2 |
| top | 5 | Stonecraft Studios | 5.92M | 1399 | 5.26M (3) | [qa75FG2IzhY](https://www.youtube.com/watch?v=qa75FG2IzhY) JJ Sister Choose the Right Outfit Final Reaction🕸️🤯😍 -… — 3.70M, 18.2 d, short | 2026-11-03, n=50 | 1.66M / – / 1.66M | 50 | 92% | – | 1 / 10 |
| orig-IP | 1 | Tg Jamal Shorts 44 | 24K | 315 | 6.39M (2) | [uTjxhkO1_SE](https://www.youtube.com/watch?v=uTjxhkO1_SE) Which One Would You Guys Choose? — 4.44M, 8.2 d, short | 2026-11-04, n=50 | 49K / – / 49K | 50 | 2% | – | 42 / 7 |
| orig-IP | 2 | Lou and Cray | 173K | 170 | 2.65M (1) | [CerrENqCCOg](https://www.youtube.com/watch?v=CerrENqCCOg) Pick A Door 7! 1v2 ✅🌌 #minecraft #funny — 2.65M, 17.2 d, short | 2026-11-04, n=50 | 358K / 956 / 377K | 6 | 2% | 13 min | 2 / 1 |
| orig-IP | 3 | Eeel | 102K | 2253 | 2.16M (1) | [5cIZnn-7odI](https://www.youtube.com/watch?v=5cIZnn-7odI) Can you guess which build is built by me? (ft. Mogswam… — 2.16M, 17.0 d, short | none | – | – | – | – | – |
| orig-IP | 4 | BabyCrab | 639K | 607 | 1.93M (2) | [wsC7Qc3pOGo](https://www.youtube.com/watch?v=wsC7Qc3pOGo) Baby Steve😇 and Baby Zombie😈 — which one will you choo… — 1.13M, 5.0 d, short | none | – | – | – | – | – |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [8ClaQIkUrTU](https://www.youtube.com/watch?v=8ClaQIkUrTU) | Peppa Up | Help Peppa Find Her Body! #peppapig #peppa | 22.1 | 9.08M | 28 s | 41.3× | 48.2× | 532K | other_franchise |
| [M1jxa2gfjkU](https://www.youtube.com/watch?v=M1jxa2gfjkU) | Peppa Up | Who Can Get Their Body Back, Peppa or Suzy? #peppapig #peppa #minecra… | 26.0 | 6.05M | 35 s | 27.5× | 27.3× | 532K | other_franchise |
| [q_N23LHqAnE](https://www.youtube.com/watch?v=q_N23LHqAnE) | Stonecraft Studios | 1 or 2:Wall-Playing Jj sister Reaction🏥🕸️🥰-Minecraft Short Animation … | 5.8 | 5.51M | 8 s | 3.3× | 5.6× | 5.92M | maizen_jj_mikey |
| [EgGF9iLClms](https://www.youtube.com/watch?v=EgGF9iLClms) | Stonecraft Studios | 1 or 2: Sleeping Police Jj's Dream Reaction Reveal🛌😮🚨-Minecraft Short… | 2.3 | 4.45M | 6 s | 2.7× | 11.4× | 5.92M | maizen_jj_mikey|dream_smp_creators |
| [uTjxhkO1_SE](https://www.youtube.com/watch?v=uTjxhkO1_SE) | Tg Jamal Shorts 44 | Which One Would You Guys Choose? | 8.2 | 4.44M | 6 s | 90.6× | 132.7× | 24K |  |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [uTjxhkO1_SE](https://www.youtube.com/watch?v=uTjxhkO1_SE) | Tg Jamal Shorts 44 | Which One Would You Guys Choose? | 8.2 | 4.44M | 6 s | 90.6× | 132.7× | 24K |  |
| [8ClaQIkUrTU](https://www.youtube.com/watch?v=8ClaQIkUrTU) | Peppa Up | Help Peppa Find Her Body! #peppapig #peppa | 22.1 | 9.08M | 28 s | 41.3× | 48.2× | 532K | other_franchise |
| [NXCnMP6Em1g](https://www.youtube.com/watch?v=NXCnMP6Em1g) | Tg Jamal Shorts 44 | What Do You Guys Think Who Will Win | 4.2 | 1.95M | 6 s | 39.8× | 114.0× | 24K |  |
| [5ESvZbZ9R7c](https://www.youtube.com/watch?v=5ESvZbZ9R7c) | Tg Jamal Shorts 44 | Which One of These Is Your Favorite Gear? | 13.2 | 1.77M | 6 s | 36.1× | 32.8× | 24K |  |
| [M1jxa2gfjkU](https://www.youtube.com/watch?v=M1jxa2gfjkU) | Peppa Up | Who Can Get Their Body Back, Peppa or Suzy? #peppapig #peppa #minecra… | 26.0 | 6.05M | 35 s | 27.5× | 27.3× | 532K | other_franchise |
| [JIqeCzFHnJM](https://www.youtube.com/watch?v=JIqeCzFHnJM) | FoxiLu | JJ made the wrong choice in Minecraft 😱🥺 #minecraft #sadstory #maizen… | 14.7 | 3.41M | 44 s | 14.4× | 12.7× | 74K | maizen_jj_mikey |
| [13-EI5573Bg](https://www.youtube.com/watch?v=13-EI5573Bg) | FoxiLu | Which JJ is Real? Dark JJ tricked! 🤔💔 #minecraft #sadstory #maizen #j… | 15.7 | 3.38M | 46 s | 14.3× | 11.8× | 74K | maizen_jj_mikey |
| [9klofxQUqQ0](https://www.youtube.com/watch?v=9klofxQUqQ0) | FoxiLu | Why didn't the girl believe JJ? Which JJ is Real? 😨💔 #minecraft #sads… | 10.7 | 2.05M | 47 s | 8.7× | 10.5× | 74K | maizen_jj_mikey |
| [CerrENqCCOg](https://www.youtube.com/watch?v=CerrENqCCOg) | Lou and Cray | Pick A Door 7! 1v2 ✅🌌 #minecraft #funny | 17.2 | 2.65M | 155 s | 7.0× | 6.5× | 173K |  |
| [nLHOu9MC6ZQ](https://www.youtube.com/watch?v=nLHOu9MC6ZQ) | Cayce | Minecraft But I GUESS COLORS | 10.5 | 6.23M | 159 s | 3.6× | 9.0× | 278K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [NXCnMP6Em1g](https://www.youtube.com/watch?v=NXCnMP6Em1g) | Tg Jamal Shorts 44 | What Do You Guys Think Who Will Win | 4.2 | 1.95M | 6 s | 39.8× | 114.0× | 24K |  |
| [7ixUnE5FK60](https://www.youtube.com/watch?v=7ixUnE5FK60) | Stonecraft Studios | 1 or 2:Wall-Playing Spidervenom Jj sister Reaction🖤🥰🕷️-Minecraft Shor… | 1.5 | 3.53M | 8 s | 2.1× | 14.2× | 5.92M | maizen_jj_mikey|other_franchise |
| [EgGF9iLClms](https://www.youtube.com/watch?v=EgGF9iLClms) | Stonecraft Studios | 1 or 2: Sleeping Police Jj's Dream Reaction Reveal🛌😮🚨-Minecraft Short… | 2.3 | 4.45M | 6 s | 2.7× | 11.4× | 5.92M | maizen_jj_mikey|dream_smp_creators |
| [BrT1ChD9z5c](https://www.youtube.com/watch?v=BrT1ChD9z5c) | Stonecraft Studios | 1 or 2:Awkward Jj Reaction Reveal Mirror Dancing🦊🚨🤣-Minecraft Short A… | 2.8 | 2.50M | 12 s | 1.5× | 5.3× | 5.92M | maizen_jj_mikey |
| [huqSwg0jeI8](https://www.youtube.com/watch?v=huqSwg0jeI8) | Stonecraft Studios | 1 or 2: Sleeping Gohjo and Jj's Dream Reaction Reveal🚓🛌🤣-Minecraft Sh… | 3.3 | 2.68M | 6 s | 1.6× | 4.8× | 5.92M | maizen_jj_mikey|dream_smp_creators |

**What the interactive outliers share (INFERRED):**
- **A 6–46 s Short that asks the viewer one binary question:**
  - "Which One Would You Guys Choose?" — Tg Jamal, 24K subs, 4.44M, 90× median, 6 s.
  - "Pick A Door! 1v2 ✅" — Lou and Cray.
  - "1 or 2: … Reaction Reveal" — Stonecraft, JJ.
  - "Baby Steve vs Baby Zombie — which one will you choose to help?" — BabyCrab, Mojang cast.
- **Payoff in the comments.** Little or no story.
- **Mostly third-party** (Peppa, JJ, Verity) **and 83% kid tone.**
- **Mass-produced:** Tg Jamal posts 50 uploads in 30 d, and 42 of them are outliers.

### 3.5 Leaders: mob/army battle sim

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | Joeysaf (mega) | 491K | 3766 | 13.78M (4) | [O9sLjjxenr0](https://www.youtube.com/watch?v=O9sLjjxenr0) Minecraft But Every Mob Changes When I Kill One / #sho… — 4.64M, 20.6 d, short | 2026-11-04, n=50 | 2.36M / 106K / 2.58M | 34 | 0% | 15 min | 30 / 4 |
| top | 2 | Spoke (mega) | 2.91M | 4124 | 13.73M (1) | [y5IdSoHdkgg](https://www.youtube.com/watch?v=y5IdSoHdkgg) 10,000 Players Simulate COLD WAR in Minecraft — 13.73M, 12.5 d, long | 2026-11-04, n=50 | 3.43M / 3.50M / 3.23M | 1 | 0% | 67 min | 1 / 0 |
| top | 3 | Parrot (mega) | 4.45M | 2260 | 7.24M (1) | [9-j9GWjyWpY](https://www.youtube.com/watch?v=9-j9GWjyWpY) 1000 Players Simulate End Prison in Minecraft — 7.24M, 19.6 d, long | none | – | – | – | – | – |
| top | 4 | FlameFrags | 3.08M | 3255 | 5.02M (1) | [ZT-k42SC7L0](https://www.youtube.com/watch?v=ZT-k42SC7L0) 10,000 VS 10,000 Player Minecraft War — 5.02M, 3.8 d, long | 2026-11-04, n=50 | 4.53M / 4.53M / – | 2 | 6% | 55 min | 2 / 1 |
| top | 5 | AlphaExtra | 1.06M | 1887 | 4.30M (2) | [i2o9XJctd0I](https://www.youtube.com/watch?v=i2o9XJctd0I) Alpha vs Tikawar: Scary Verity's Maze Statue Battle In… — 2.84M, 21.0 d, long | none | – | – | – | – | – |
| top | 6 | Mikey Crazy | 91K | 144 | 3.56M (2) | [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft — 2.14M, 3.8 d, short | 2026-11-04, n=50 | 29K / 5K / 238K | 22 | 50% | 8 min | 18 / 5 |
| top | 7 | Brawl Lab | 9K | 23 | 3.50M (11) | [dvKQhdDwbnU](https://www.youtube.com/watch?v=dvKQhdDwbnU) Sans Has 1 HP vs EVERY Minecraft Mob #minecraft #shorts — 1.56M, 18.0 d, short | 2026-11-04, n=49 | 52K / 4K / 53K | 49 | 80% | 7 min | 44 / 8 |
| orig-IP | 1 | FlameFrags | 3.08M | 3255 | 5.02M (1) | [ZT-k42SC7L0](https://www.youtube.com/watch?v=ZT-k42SC7L0) 10,000 VS 10,000 Player Minecraft War — 5.02M, 3.8 d, long | 2026-11-04, n=50 | 4.53M / 4.53M / – | 2 | 6% | 55 min | 2 / 1 |
| orig-IP | 2 | SpeedSilver | 4.00M | 2149 | 2.53M (1) | [KnlAF_djhdc](https://www.youtube.com/watch?v=KnlAF_djhdc) 1000 Players Simulate Minecraft's Deadliest Containmen… — 2.53M, 4.6 d, long | none | – | – | – | – | – |
| orig-IP | 3 | Gorf | 292K | 750 | 2.09M (1) | [49YPsBjaEGg](https://www.youtube.com/watch?v=49YPsBjaEGg) Minecraft, But I Join Size Civilization... — 2.09M, 22.9 d, long | none | – | – | – | – | – |
| orig-IP | 4 | Hoodie Steve | 5K | 39 | 1.97M (1) | [xpsiRQd7ssg](https://www.youtube.com/watch?v=xpsiRQd7ssg) Minecraft Tug of War: Villagers vs Mobs — 1.97M, 16.7 d, short | 2026-11-04, n=14 | 40K / – / 40K | 9 | 0% | – | 8 / 0 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [y5IdSoHdkgg](https://www.youtube.com/watch?v=y5IdSoHdkgg) | Spoke | 10,000 Players Simulate COLD WAR in Minecraft | 12.5 | 13.73M | 240 min | 3.9× | 1.0× | 2.91M |  |
| [xpsiRQd7ssg](https://www.youtube.com/watch?v=xpsiRQd7ssg) | Hoodie Steve | Minecraft Tug of War: Villagers vs Mobs | 16.7 | 1.97M | 70 s | 49.5× | 22.3× | 5K |  |
| [udhWREKY2h0](https://www.youtube.com/watch?v=udhWREKY2h0) | Brawl Lab | Last Breath Sans vs EVERY Minecraft Mob #undertale #shorts | 10.1 | 409K | 106 s | 7.7× | 6.1× | 9K | other_franchise |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [xpsiRQd7ssg](https://www.youtube.com/watch?v=xpsiRQd7ssg) | Hoodie Steve | Minecraft Tug of War: Villagers vs Mobs | 16.7 | 1.97M | 70 s | 49.5× | 22.3× | 5K |  |
| [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) | Mikey Crazy | All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft | 3.8 | 2.14M | 58 s | 9.0× | 23.6× | 91K | maizen_jj_mikey |
| [udhWREKY2h0](https://www.youtube.com/watch?v=udhWREKY2h0) | Brawl Lab | Last Breath Sans vs EVERY Minecraft Mob #undertale #shorts | 10.1 | 409K | 106 s | 7.7× | 6.1× | 9K | other_franchise |
| [wKUybajlHMg](https://www.youtube.com/watch?v=wKUybajlHMg) | Mikey Crazy | JJ Golem SAVES All Mobs From a HUGE VERITY TSUNAMI! 🌊😱 #minecraft | 1.9 | 1.42M | 58 s | 6.0× | 32.0× | 91K | maizen_jj_mikey|verity_cruelty |
| [y5IdSoHdkgg](https://www.youtube.com/watch?v=y5IdSoHdkgg) | Spoke | 10,000 Players Simulate COLD WAR in Minecraft | 12.5 | 13.73M | 240 min | 3.9× | 1.0× | 2.91M |  |
| [ROFxrv-1gAg](https://www.youtube.com/watch?v=ROFxrv-1gAg) | Brawl Lab | Chara vs EVERY Minecraft Mob #minecraft #shorts | 15.8 | 186K | 104 s | 3.5× | 1.8× | 9K | other_franchise |
| [rstXhQfgxDs](https://www.youtube.com/watch?v=rstXhQfgxDs) | Brawl Lab | Gargantuar vs EVERY Minecraft Mob — One Smash Kills Anything #pvz #mi… | 8.6 | 174K | 52 s | 3.3× | 3.1× | 9K | other_franchise |
| [TIMJ4hgxZV4](https://www.youtube.com/watch?v=TIMJ4hgxZV4) | Brawl Lab | Last Breath Sans vs EVERY Deltarune Boss #undertale #deltarune #shorts | 4.2 | 128K | 62 s | 2.4× | 4.7× | 9K | other_franchise |
| [O9sLjjxenr0](https://www.youtube.com/watch?v=O9sLjjxenr0) | Joeysaf | Minecraft But Every Mob Changes When I Kill One / #shorts | 20.6 | 4.64M | 140 s | 1.8× | 1.1× | 491K |  |
| [7wbF_IKUDW8](https://www.youtube.com/watch?v=7wbF_IKUDW8) | Brawl Lab | Tenna vs EVERY Minecraft Mob #minecraft #shorts | 11.6 | 93K | 59 s | 1.8× | 1.2× | 9K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [wKUybajlHMg](https://www.youtube.com/watch?v=wKUybajlHMg) | Mikey Crazy | JJ Golem SAVES All Mobs From a HUGE VERITY TSUNAMI! 🌊😱 #minecraft | 1.9 | 1.42M | 58 s | 6.0× | 32.0× | 91K | maizen_jj_mikey|verity_cruelty |
| [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) | Mikey Crazy | All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft | 3.8 | 2.14M | 58 s | 9.0× | 23.6× | 91K | maizen_jj_mikey |
| [UsAJx2lp1RA](https://www.youtube.com/watch?v=UsAJx2lp1RA) | Brawl Lab | Snowgrave Noelle vs EVERY Minecraft Mob #deltarune #noelle #snowgrave… | 2.0 | 61K | 94 s | 1.2× | 4.7× | 9K | other_franchise |
| [TIMJ4hgxZV4](https://www.youtube.com/watch?v=TIMJ4hgxZV4) | Brawl Lab | Last Breath Sans vs EVERY Deltarune Boss #undertale #deltarune #shorts | 4.2 | 128K | 62 s | 2.4× | 4.7× | 9K | other_franchise |
| [k_BIMDELwL0](https://www.youtube.com/watch?v=k_BIMDELwL0) | Joeysaf | Minecraft But I Have to Reveal Every Mob / #shorts | 0.6 | 795K | 155 s | 0.3× | 3.9× | 491K |  |

**What the battle outliers share (INFERRED):**
- **Two different products under one lane:**
  - *(a) Player-simulation wars:* "10,000 Players Simulate COLD WAR", "10,000 VS 10,000 Player Minecraft War". These are 2.5–4 h, made by the Unstable SMP crew, and need real players.
  - *(b) Short contests with a clear winner question:* "[A] vs EVERY Minecraft Mob", "[Team] vs [Team] — Which Team Wins?" (Brawl Lab, 60–120 s), and physics experiments like "Minecraft Tug of War: Villagers vs Mobs" and "I Dropped Minecraft Blocks on an Iron Golem" (Hoodie Steve, 25–70 s, 39–50×).
- **Where third-party IP enters.** Undertale/Deltarune heroes (Sans, Susie, Noelle) and JJ Golem (Mikey Crazy). The no-IP physics experiments do just as well.
- **Long-form command battles** (Peteson Craft, ZoraCrafter, Gasbo, MakoShi): "X vs ALL Minecraft Bosses / World War of Mobs", 10–20 min, mostly 100–500K.

### 3.6 Leaders: AI in Minecraft

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | GameToons | 12.80M | 2422 | 2.87M (1) | [297i_hQ7k3Q](https://www.youtube.com/watch?v=297i_hQ7k3Q) LORD VERITY: MASTER of AI! (Cartoon Animation) — 2.87M, 28.5 d, long | 2026-11-04, n=50 | 1.43M / 1.43M / – | 13 | 70% | 8 min | 0 / 1 |
| top | 2 | Kiply | 3.28M | 2638 | 2.15M (1) | [jQbvEV68dPc](https://www.youtube.com/watch?v=jQbvEV68dPc) I Added Talking Villagers to Minecraft — 2.15M, 25.6 d, long | none | – | – | – | – | – |
| top | 3 | CaptainNate | 35K | 1744 | 1.78M (2) | [CWdRj2u_BSQ](https://www.youtube.com/watch?v=CWdRj2u_BSQ) This Minecraft World is AI Generated... — 1.74M, 25.9 d, short | none | – | – | – | – | – |
| top | 4 | Catkin Craft | 125K | 184 | 1.55M (1) | [n05c_dhqfKE](https://www.youtube.com/watch?v=n05c_dhqfKE) What Happens When AI Runs a Minecraft Village? 😲 — 1.55M, 26.8 d, short | 2026-11-04, n=50 | 573K / – / 573K | 30 | 2% | – | 20 / 1 |
| top | 5 | Swayle | 1.37M | 1189 | 1.38M (1) | [_CAmsCrqSug](https://www.youtube.com/watch?v=_CAmsCrqSug) I Created a Horror Mod That is Smarter Than You... — 1.38M, 17.9 d, long | none | – | – | – | – | – |
| top | 10 | JakeInABox | 57K | 39 | 444K (1) | [Kix0iuunTrY](https://www.youtube.com/watch?v=Kix0iuunTrY) My Mom Loves The AI Robot More Than Me?! 🤖❓ #minecraft… — 444K, 15.8 d, short | 2026-11-04, n=50 | 48K / 7K / 49K | 50 | 0% | 3 min | 20 / 5 |
| top | 12 | DrDonutShorts | 58K | 353 | 318K (1) | [lFPzp3UiMIo](https://www.youtube.com/watch?v=lFPzp3UiMIo) DRDONUT WATCHES AI OR BAD PLAYER? #shorts #minecraft #… — 318K, 10.1 d, short | 2026-11-04, n=50 | 153K / – / 153K | 33 | 100% | – | 24 / 0 |
| orig-IP | 1 | Kiply | 3.28M | 2638 | 2.15M (1) | [jQbvEV68dPc](https://www.youtube.com/watch?v=jQbvEV68dPc) I Added Talking Villagers to Minecraft — 2.15M, 25.6 d, long | none | – | – | – | – | – |
| orig-IP | 2 | CaptainNate | 35K | 1744 | 1.78M (2) | [CWdRj2u_BSQ](https://www.youtube.com/watch?v=CWdRj2u_BSQ) This Minecraft World is AI Generated... — 1.74M, 25.9 d, short | none | – | – | – | – | – |
| orig-IP | 3 | Catkin Craft | 125K | 184 | 1.55M (1) | [n05c_dhqfKE](https://www.youtube.com/watch?v=n05c_dhqfKE) What Happens When AI Runs a Minecraft Village? 😲 — 1.55M, 26.8 d, short | 2026-11-04, n=50 | 573K / – / 573K | 30 | 2% | – | 20 / 1 |
| orig-IP | 4 | Swayle | 1.37M | 1189 | 1.38M (1) | [_CAmsCrqSug](https://www.youtube.com/watch?v=_CAmsCrqSug) I Created a Horror Mod That is Smarter Than You... — 1.38M, 17.9 d, long | none | – | – | – | – | – |
| orig-IP | 9 | JakeInABox | 57K | 39 | 444K (1) | [Kix0iuunTrY](https://www.youtube.com/watch?v=Kix0iuunTrY) My Mom Loves The AI Robot More Than Me?! 🤖❓ #minecraft… — 444K, 15.8 d, short | 2026-11-04, n=50 | 48K / 7K / 49K | 50 | 0% | 3 min | 20 / 5 |
| orig-IP | 14 | CollinCC 3 | 2K | 83 | 148K (2) | [NXO0UbmEbsE](https://www.youtube.com/watch?v=NXO0UbmEbsE) I Took Over Minecraft’s Largest AI Server — 121K, 19.7 d, long | 2026-11-04, n=2 | 74K / 74K / – | 2 | 0% | 61 min | 2 / 0 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [NXO0UbmEbsE](https://www.youtube.com/watch?v=NXO0UbmEbsE) | CollinCC 3 | I Took Over Minecraft’s Largest AI Server | 19.7 | 121K | 57 min | 1.6× | 1.2× | 2K |  |
| [q1nHfJTbUfg](https://www.youtube.com/watch?v=q1nHfJTbUfg) | CollinCC 3 | I Got Hunted by 3,000 AI Players | 6.6 | 27K | 64 min | 0.4× | 0.8× | 2K |  |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [n05c_dhqfKE](https://www.youtube.com/watch?v=n05c_dhqfKE) | Catkin Craft | What Happens When AI Runs a Minecraft Village? 😲 | 26.8 | 1.55M | 53 s | 2.7× | 1.8× | 125K |  |
| [ebrudXT_-rc](https://www.youtube.com/watch?v=ebrudXT_-rc) | JakeInABox | Why Is The AI Robot BACK?! 🤖💐 #minecraft #animation | 13.5 | 120K | 31 s | 2.5× | 1.2× | 57K |  |
| [lFPzp3UiMIo](https://www.youtube.com/watch?v=lFPzp3UiMIo) | DrDonutShorts | DRDONUT WATCHES AI OR BAD PLAYER? #shorts #minecraft #drdonutt | 10.1 | 318K | 36 s | 2.1× | 4.6× | 58K | dr_donut |
| [NXO0UbmEbsE](https://www.youtube.com/watch?v=NXO0UbmEbsE) | CollinCC 3 | I Took Over Minecraft’s Largest AI Server | 19.7 | 121K | 57 min | 1.6× | 1.2× | 2K |  |
| [q1nHfJTbUfg](https://www.youtube.com/watch?v=q1nHfJTbUfg) | CollinCC 3 | I Got Hunted by 3,000 AI Players | 6.6 | 27K | 64 min | 0.4× | 0.8× | 2K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median): none in the samples.*

**What the AI outliers share (INFERRED):**
- **First-person "I added / I created / I took over" builds** around AI agents with emergent behaviour:
  - "I Added Talking Villagers to Minecraft" — Kiply, 2.15M.
  - "I Created a Horror Mod That is Smarter Than You..." — Swayle, 1.38M.
  - "I Took Over Minecraft's Largest AI Server" — CollinCC 3, 61 min.
- **Short "what happens when AI runs X" experiments:** Catkin Craft, CaptainNate "This Minecraft World is AI Generated...".
- **Kid skits that only name-drop AI:** JakeInABox "My Mom Loves The AI Robot More Than Me?!".
- **Concrete-model titles** ("Claude Opus 5.5", "Claude AI") appear on small-channel long-forms at 114–132K (§5.3).
- **IP.** Third-party appears only via GameToons "LORD VERITY: MASTER of AI!".

### 3.7 Leaders: lore/facts

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | KeyroNN | 43K | 210 | 11.23M (1) | [S61-yhDHdog](https://www.youtube.com/watch?v=S61-yhDHdog) You Can Be IMMORTAL using a PICKAXE... — 11.23M, 29.2 d, short | 2026-11-04, n=16 | 6.83M / – / 6.83M | 2 | 0% | – | 2 / 0 |
| top | 2 | TeardownTown | 66K | 1030 | 4.24M (1) | [qz8T9dFbFSQ](https://www.youtube.com/watch?v=qz8T9dFbFSQ) How Many Baby Zombies will Destroy Giant Steve? #minec… — 4.24M, 20.7 d, short | none | – | – | – | – | – |
| top | 3 | DikoEng | 725K | 440 | 2.21M (2) | [bqRN8bq0sO8](https://www.youtube.com/watch?v=bqRN8bq0sO8) Who Is Alex? And Why Steve Almost Wasn’t There #minecr… — 1.92M, 24.9 d, short | none | – | – | – | – | – |
| top | 4 | Henreee | 82K | 85 | 2.00M (2) | [MMWDMuQ9HOo](https://www.youtube.com/watch?v=MMWDMuQ9HOo) What Happens If You Name a Rabbit Toast in Minecraft? 😳 — 1.58M, 17.9 d, short | 2026-11-04, n=50 | 369K / 10K / 377K | 50 | 66% | 55 min | 42 / 11 |
| top | 5 | Catkin Craft | 125K | 184 | 1.55M (1) | [n05c_dhqfKE](https://www.youtube.com/watch?v=n05c_dhqfKE) What Happens When AI Runs a Minecraft Village? 😲 — 1.55M, 26.8 d, short | 2026-11-04, n=50 | 573K / – / 573K | 30 | 2% | – | 20 / 1 |
| top | 6 | MythSector | 351K | 176 | 1.40M (1) | [_V2dESJmTgA](https://www.youtube.com/watch?v=_V2dESJmTgA) The Jerry Dog Backstory Will Break You… — 1.40M, 28.0 d, short | 2026-11-04, n=50 | 131K / – / 131K | 28 | 40% | – | 5 / 2 |
| top | 8 | wykull | 255K | 3333 | 908K (1) | [a4Jl4ZgehKQ](https://www.youtube.com/watch?v=a4Jl4ZgehKQ) This Redstone Door is SUPER Secret in Minecraft — 908K, 7.0 d, short | 2026-11-03, n=50 | 622K / 48K / 628K | 31 | 0% | 16 min | 26 / 4 |
| orig-IP | 1 | KeyroNN | 43K | 210 | 11.23M (1) | [S61-yhDHdog](https://www.youtube.com/watch?v=S61-yhDHdog) You Can Be IMMORTAL using a PICKAXE... — 11.23M, 29.2 d, short | 2026-11-04, n=16 | 6.83M / – / 6.83M | 2 | 0% | – | 2 / 0 |
| orig-IP | 2 | TeardownTown | 66K | 1030 | 4.24M (1) | [qz8T9dFbFSQ](https://www.youtube.com/watch?v=qz8T9dFbFSQ) How Many Baby Zombies will Destroy Giant Steve? #minec… — 4.24M, 20.7 d, short | none | – | – | – | – | – |
| orig-IP | 3 | DikoEng | 725K | 440 | 2.21M (2) | [bqRN8bq0sO8](https://www.youtube.com/watch?v=bqRN8bq0sO8) Who Is Alex? And Why Steve Almost Wasn’t There #minecr… — 1.92M, 24.9 d, short | none | – | – | – | – | – |
| orig-IP | 4 | Catkin Craft | 125K | 184 | 1.55M (1) | [n05c_dhqfKE](https://www.youtube.com/watch?v=n05c_dhqfKE) What Happens When AI Runs a Minecraft Village? 😲 — 1.55M, 26.8 d, short | 2026-11-04, n=50 | 573K / – / 573K | 30 | 2% | – | 20 / 1 |
| orig-IP | 6 | wykull | 255K | 3333 | 908K (1) | [a4Jl4ZgehKQ](https://www.youtube.com/watch?v=a4Jl4ZgehKQ) This Redstone Door is SUPER Secret in Minecraft — 908K, 7.0 d, short | 2026-11-03, n=50 | 622K / 48K / 628K | 31 | 0% | 16 min | 26 / 4 |
| orig-IP | 8 | Explained Using Minecraft | 17K | 64 | 862K (2) | [2ug97dmUTH8](https://www.youtube.com/watch?v=2ug97dmUTH8) guerrilla warfare explained using minecraft — 523K, 27.0 d, short | 2026-11-04, n=50 | 166K / – / 166K | 46 | 0% | – | 46 / 4 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [_V2dESJmTgA](https://www.youtube.com/watch?v=_V2dESJmTgA) | MythSector | The Jerry Dog Backstory Will Break You… | 28.0 | 1.40M | 60 s | 10.7× | 4.5× | 351K | jerry_wolf_dog |
| [iVNUbwDrEKM](https://www.youtube.com/watch?v=iVNUbwDrEKM) | Henreee | What Happens If You Never Unlock Anyone in Sonic Advance 3? 🔒 | 4.5 | 991K | 45 s | 2.6× | 2.9× | 82K | other_franchise |
| [iBZkAynpc-I](https://www.youtube.com/watch?v=iBZkAynpc-I) | Henreee | What Happens If You Come Back Without the Crystal in Crash Bandicoot … | 6.8 | 908K | 45 s | 2.4× | 1.7× | 82K | other_franchise |
| [EHMvdCGgHlU](https://www.youtube.com/watch?v=EHMvdCGgHlU) | Henreee | Why Does Cuphead Have a Cup for a Head? ☕ | 5.7 | 884K | 35 s | 2.3× | 2.0× | 82K | other_franchise |
| [CERSa9ZOCyQ](https://www.youtube.com/watch?v=CERSa9ZOCyQ) | Explained Using Minecraft | democracy explained using minecraft | 22.0 | 640K | 72 s | 3.9× | 3.2× | 17K |  |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [_V2dESJmTgA](https://www.youtube.com/watch?v=_V2dESJmTgA) | MythSector | The Jerry Dog Backstory Will Break You… | 28.0 | 1.40M | 60 s | 10.7× | 4.5× | 351K | jerry_wolf_dog |
| [ar6VI865seE](https://www.youtube.com/watch?v=ar6VI865seE) | MythSector | This Bear’s Backstory Will Break You… | 8.8 | 697K | 71 s | 5.3× | 7.1× | 351K |  |
| [CERSa9ZOCyQ](https://www.youtube.com/watch?v=CERSa9ZOCyQ) | Explained Using Minecraft | democracy explained using minecraft | 22.0 | 640K | 72 s | 3.9× | 3.2× | 17K |  |
| [2ug97dmUTH8](https://www.youtube.com/watch?v=2ug97dmUTH8) | Explained Using Minecraft | guerrilla warfare explained using minecraft | 27.0 | 523K | 79 s | 3.2× | 2.1× | 17K |  |
| [SA3t6jAQFSE](https://www.youtube.com/watch?v=SA3t6jAQFSE) | Explained Using Minecraft | feudalism explained using minecraft #shorts | 29.4 | 466K | 77 s | 2.8× | 1.7× | 17K |  |
| [n05c_dhqfKE](https://www.youtube.com/watch?v=n05c_dhqfKE) | Catkin Craft | What Happens When AI Runs a Minecraft Village? 😲 | 26.8 | 1.55M | 53 s | 2.7× | 1.8× | 125K |  |
| [iVNUbwDrEKM](https://www.youtube.com/watch?v=iVNUbwDrEKM) | Henreee | What Happens If You Never Unlock Anyone in Sonic Advance 3? 🔒 | 4.5 | 991K | 45 s | 2.6× | 2.9× | 82K | other_franchise |
| [iBZkAynpc-I](https://www.youtube.com/watch?v=iBZkAynpc-I) | Henreee | What Happens If You Come Back Without the Crystal in Crash Bandicoot … | 6.8 | 908K | 45 s | 2.4× | 1.7× | 82K | other_franchise |
| [EHMvdCGgHlU](https://www.youtube.com/watch?v=EHMvdCGgHlU) | Henreee | Why Does Cuphead Have a Cup for a Head? ☕ | 5.7 | 884K | 35 s | 2.3× | 2.0× | 82K | other_franchise |
| [ve8lUQI94QI](https://www.youtube.com/watch?v=ve8lUQI94QI) | Henreee | What Happens If You Let a Yellow Koopa Back Into a Shell in Super Mar… | 6.1 | 773K | 39 s | 2.1× | 1.7× | 82K | other_franchise |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [IJP9uflWYro](https://www.youtube.com/watch?v=IJP9uflWYro) | Explained Using Minecraft | tax havens explained using minecraft | 1.4 | 46K | 93 s | 0.3× | 3.5× | 17K |  |
| [9CEWqXPTzec](https://www.youtube.com/watch?v=9CEWqXPTzec) | Explained Using Minecraft | who pays for healthcare explained using minecraft | 3.4 | 103K | 73 s | 0.6× | 3.3× | 17K |  |
| [MQ5IYJDkDJI](https://www.youtube.com/watch?v=MQ5IYJDkDJI) | Explained Using Minecraft | world war 1 explained using minecraft | 2.4 | 66K | 83 s | 0.4× | 3.0× | 17K |  |
| [ztktkAjra04](https://www.youtube.com/watch?v=ztktkAjra04) | Henreee | What Happens If You Get All 180 Emblems in Sonic Adventure 2? 🏅 | 1.0 | 235K | 44 s | 0.6× | 3.0× | 82K | other_franchise |
| [iVNUbwDrEKM](https://www.youtube.com/watch?v=iVNUbwDrEKM) | Henreee | What Happens If You Never Unlock Anyone in Sonic Advance 3? 🔒 | 4.5 | 991K | 45 s | 2.6× | 2.9× | 82K | other_franchise |

**What the lore/facts outliers share (INFERRED):**
- **Mechanic-secret Shorts** with "You/Can" plus an ellipsis: KeyroNN "You Can Be IMMORTAL using a PICKAXE..." (11.2M) and "A BEE NEST Can EXPOSE Your Base..." (22.9M, 57 d), at 43–52 s, from a 43K-subs channel.
- **"Who is / why" origin questions:** DikoEng "Who Is Alex? And Why Steve Almost Wasn't There".
- **Real-world concepts "explained using minecraft":** a 17K-subs, 64-day channel at 0.47–0.64M, 2.8–3.9×.
- **Build-hack Shorts** (wykull "The BEST way to build Doors…", 11.6M) sit next to this lane.
- **Fan-lore of third-party characters** (MythSector "The Jerry Dog Backstory Will Break You…") is third-party.
- **Long-form lore** has almost no recent hits in this scan. Game Theory's 1.37M is the exception.

### 3.8 Leaders: "Minecraft but"/roleplay

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | Joeysaf (mega) | 491K | 3766 | 78.95M (25) | [gNosQvKuGLA](https://www.youtube.com/watch?v=gNosQvKuGLA) Minecraft But Every Basic Rule Is Reversed / #shorts — 6.95M, 27.6 d, short | 2026-11-04, n=50 | 2.36M / 106K / 2.58M | 34 | 0% | 15 min | 30 / 4 |
| top | 2 | dayta (mega) | 12.30M | 2325 | 24.48M (4) | [g3d9JWBNduo](https://www.youtube.com/watch?v=g3d9JWBNduo) Minecraft, But anything you TOUCH you BECOME... — 10.37M, 21.4 d, short | 2026-11-04, n=50 | 2.21M / 29K / 3.26M | 13 | 2% | 16 min | 2 / 1 |
| top | 3 | Cayce (mega) | 278K | 1351 | 15.90M (5) | [nLHOu9MC6ZQ](https://www.youtube.com/watch?v=nLHOu9MC6ZQ) Minecraft But I GUESS COLORS — 6.23M, 10.5 d, short | 2026-11-04, n=50 | 1.72M / – / 1.72M | 13 | 0% | – | 12 / 1 |
| top | 4 | Air Run | 3.86M | 4852 | 12.25M (1) | [QvDX0Gttz_c](https://www.youtube.com/watch?v=QvDX0Gttz_c) Minecraft But Every Landing Gets Harder! 💥 — 12.25M, 27.2 d, short | none | – | – | – | – | – |
| top | 5 | HydroMC | 42K | 1841 | 7.38M (1) | [-f_kwRmKep4](https://www.youtube.com/watch?v=-f_kwRmKep4) I Added Cracking To Minecraft — 7.38M, 28.3 d, short | none | – | – | – | – | – |
| top | 6 | ProBoiz 95 | 9.41M | 2391 | 6.91M (1) | [NmxoC89w1-A](https://www.youtube.com/watch?v=NmxoC89w1-A) Minecraft, But You Can Combine Any Mobs! — 6.91M, 21.9 d, long | 2026-11-04, n=50 | 8.99M / 8.94M / 10.33M | 2 | 6% | 29 min | 0 / 0 |
| top | 8 | camman18 | 11.40M | 2040 | 5.28M (1) | [1l2LHE9URyM](https://www.youtube.com/watch?v=1l2LHE9URyM) i meant to say caption but said subtitle but i didnt f… — 5.28M, 9.9 d, short | 2026-11-03, n=50 | 4.41M / – / 4.41M | 30 | 0% | – | 1 / 2 |
| orig-IP | 1 | Air Run | 3.86M | 4852 | 12.25M (1) | [QvDX0Gttz_c](https://www.youtube.com/watch?v=QvDX0Gttz_c) Minecraft But Every Landing Gets Harder! 💥 — 12.25M, 27.2 d, short | none | – | – | – | – | – |
| orig-IP | 2 | HydroMC | 42K | 1841 | 7.38M (1) | [-f_kwRmKep4](https://www.youtube.com/watch?v=-f_kwRmKep4) I Added Cracking To Minecraft — 7.38M, 28.3 d, short | none | – | – | – | – | – |
| orig-IP | 3 | ProBoiz 95 | 9.41M | 2391 | 6.91M (1) | [NmxoC89w1-A](https://www.youtube.com/watch?v=NmxoC89w1-A) Minecraft, But You Can Combine Any Mobs! — 6.91M, 21.9 d, long | 2026-11-04, n=50 | 8.99M / 8.94M / 10.33M | 2 | 6% | 29 min | 0 / 0 |
| orig-IP | 4 | camman18 | 11.40M | 2040 | 5.28M (1) | [1l2LHE9URyM](https://www.youtube.com/watch?v=1l2LHE9URyM) i meant to say caption but said subtitle but i didnt f… — 5.28M, 9.9 d, short | 2026-11-03, n=50 | 4.41M / – / 4.41M | 30 | 0% | – | 1 / 2 |
| orig-IP | 9 | imKaiL00L | 241K | 205 | 2.44M (2) | [1ncAcHzjW1c](https://www.youtube.com/watch?v=1ncAcHzjW1c) Horror One Block, But Drops are Guns — 1.95M, 22.9 d, long | 2026-11-04, n=50 | 177K / 560K / 38K | 9 | 0% | 24 min | 5 / 1 |
| orig-IP | 15 | EYstreem | 13.90M | 5346 | 1.93M (1) | [ONdXW2oIsdc](https://www.youtube.com/watch?v=ONdXW2oIsdc) Minecraft, But There's SQUISHY DUMPLING Hearts — 1.93M, 26.5 d, long | 2026-11-04, n=50 | 1.98M / 2.36M / 444K | 10 | 12% | 26 min | 0 / 0 |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [foV20Sn50jg](https://www.youtube.com/watch?v=foV20Sn50jg) | dayta | Minecraft, But if you LEAVE the BORDER YOU LOSE... | 90.3 | 19.60M | 65 s | 6.0× | 0.9× | 12.30M |  |
| [lxKoCx8pB5c](https://www.youtube.com/watch?v=lxKoCx8pB5c) | ProBoiz 95 | Minecraft But Every Drop is a Gun! | 287.9 | 15.38M | 25 min | 1.7× | 0.1× | 9.41M |  |
| [FckHPKMQIls](https://www.youtube.com/watch?v=FckHPKMQIls) | dayta | Minecraft, But anything you ABSORB you BECOME... | 73.3 | 13.48M | 62 s | 4.1× | 0.8× | 12.30M |  |
| [g3d9JWBNduo](https://www.youtube.com/watch?v=g3d9JWBNduo) | dayta | Minecraft, But anything you TOUCH you BECOME... | 21.4 | 10.37M | 66 s | 3.2× | 2.1× | 12.30M |  |
| [YYM8CDH1ghE](https://www.youtube.com/watch?v=YYM8CDH1ghE) | Cayce | Minecraft But Drawing DELETES BLOCKS | 79.1 | 9.73M | 145 s | 5.7× | 1.9× | 278K |  |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [nLHOu9MC6ZQ](https://www.youtube.com/watch?v=nLHOu9MC6ZQ) | Cayce | Minecraft But I GUESS COLORS | 10.5 | 6.23M | 159 s | 3.6× | 9.0× | 278K |  |
| [1ncAcHzjW1c](https://www.youtube.com/watch?v=1ncAcHzjW1c) | imKaiL00L | Horror One Block, But Drops are Guns | 22.9 | 1.95M | 30 min | 3.5× | 3.0× | 241K |  |
| [g3d9JWBNduo](https://www.youtube.com/watch?v=g3d9JWBNduo) | dayta | Minecraft, But anything you TOUCH you BECOME... | 21.4 | 10.37M | 66 s | 3.2× | 2.1× | 12.30M |  |
| [gNosQvKuGLA](https://www.youtube.com/watch?v=gNosQvKuGLA) | Joeysaf | Minecraft But Every Basic Rule Is Reversed / #shorts | 27.6 | 6.95M | 154 s | 2.7× | 1.2× | 491K |  |
| [M6W6qQQJZ_4](https://www.youtube.com/watch?v=M6W6qQQJZ_4) | Joeysaf | Minecraft But the Government Makes a New Law Every 30 Seconds / #shor… | 26.6 | 6.34M | 148 s | 2.5× | 1.2× | 491K |  |
| [hlbEaOiM3_o](https://www.youtube.com/watch?v=hlbEaOiM3_o) | Joeysaf | Minecraft But the Overworld and Nether Swapped / #shorts | 13.6 | 5.83M | 157 s | 2.3× | 2.1× | 491K |  |
| [cNf0GfhQuWM](https://www.youtube.com/watch?v=cNf0GfhQuWM) | Cayce | Minecraft But Villagers Fight Back | 17.3 | 3.30M | 160 s | 1.9× | 2.9× | 278K |  |
| [O9sLjjxenr0](https://www.youtube.com/watch?v=O9sLjjxenr0) | Joeysaf | Minecraft But Every Mob Changes When I Kill One / #shorts | 20.6 | 4.64M | 140 s | 1.8× | 1.1× | 491K |  |
| [2ls5d4wG0CM](https://www.youtube.com/watch?v=2ls5d4wG0CM) | Cayce | Minecraft But I'm Just A Head | 15.3 | 2.78M | 143 s | 1.6× | 2.8× | 278K |  |
| [VYURL1KS0q0](https://www.youtube.com/watch?v=VYURL1KS0q0) | Joeysaf | Minecraft But My Health Drains Every 5 Seconds / #shorts | 25.6 | 4.03M | 160 s | 1.6× | 0.8× | 491K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [t75SLaZKWSA](https://www.youtube.com/watch?v=t75SLaZKWSA) | Joeysaf | Minecraft But Breaking One Block Changes Them All / #shorts | 2.6 | 3.10M | 146 s | 1.2× | 5.9× | 491K |  |
| [0QxH2wcSV0I](https://www.youtube.com/watch?v=0QxH2wcSV0I) | Joeysaf | Minecraft But Everything Moves 10x Faster When I Look Away / #shorts | 1.5 | 1.62M | 152 s | 0.6× | 5.2× | 491K |  |
| [k_BIMDELwL0](https://www.youtube.com/watch?v=k_BIMDELwL0) | Joeysaf | Minecraft But I Have to Reveal Every Mob / #shorts | 0.6 | 795K | 155 s | 0.3× | 3.9× | 491K |  |
| [_GT2x0tl2uE](https://www.youtube.com/watch?v=_GT2x0tl2uE) | Cayce | Minecraft But There's A BLACK HOLE | 1.2 | 257K | 157 s | 0.1× | 3.2× | 278K |  |
| [lAm9-YnK7tw](https://www.youtube.com/watch?v=lAm9-YnK7tw) | imKaiL00L | Minecraft but Dying is Secretly OP | 1.9 | 121K | 33 min | 0.2× | 2.3× | 241K |  |

**What the "Minecraft but" outliers share (INFERRED):**
- **One rule change stated in the title:** "Minecraft, But [anything you TOUCH you BECOME / Every Basic Rule Is Reversed / the Overworld and Nether Swapped]".
- **Lengths:** 60–160 s Shorts (Joeysaf 140–160 s, dayta 60–66 s) or 23–30 min long-forms (ProBoiz, imKaiL00L).
- **Nearly no third-party IP.**
- **Personality-driven and highly serial:** Joeysaf has 25 on-format hits in 30 d.
- **Roleplay** ("POOR to RICH", Cash) is mega-owned.

### 3.9 Leaders: command mob-vs-mob sims (sub-lane of battle)

| group | # | channel | subs | ch. age d | on-format 30-d views (videos) | top on-format video | uploads sample | median all / long / Shorts | uploads ≤30 d | 3P-IP share of uploads | median long length | outliers ≤30 d / explosive ≤5 d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top | 1 | Joeysaf (mega) | 491K | 3766 | 13.78M (4) | [O9sLjjxenr0](https://www.youtube.com/watch?v=O9sLjjxenr0) Minecraft But Every Mob Changes When I Kill One / #sho… — 4.64M, 20.6 d, short | 2026-11-04, n=50 | 2.36M / 106K / 2.58M | 34 | 0% | 15 min | 30 / 4 |
| top | 2 | Mikey Crazy | 91K | 144 | 3.56M (2) | [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft — 2.14M, 3.8 d, short | 2026-11-04, n=50 | 29K / 5K / 238K | 22 | 50% | 8 min | 18 / 5 |
| top | 3 | Brawl Lab | 9K | 23 | 3.50M (11) | [dvKQhdDwbnU](https://www.youtube.com/watch?v=dvKQhdDwbnU) Sans Has 1 HP vs EVERY Minecraft Mob #minecraft #shorts — 1.56M, 18.0 d, short | 2026-11-04, n=49 | 52K / 4K / 53K | 49 | 80% | 7 min | 44 / 8 |
| top | 4 | MSToons | 1.77M | 3273 | 1.86M (1) | [HsYArr0UEQ4](https://www.youtube.com/watch?v=HsYArr0UEQ4) JJ BUFF Chicken and 1000 ARMY?! - Maizen Minecraft Ani… — 1.86M, 24.9 d, long | 2026-11-04, n=50 | 1.86M / 1.86M / – | 11 | 100% | 11 min | 6 / 2 |
| top | 5 | Witherion | 298K | 3670 | 1.62M (1) | [BWpJTo7nLAs](https://www.youtube.com/watch?v=BWpJTo7nLAs) Escaping the horror mob army #minecraft #shorts — 1.62M, 24.5 d, short | none | – | – | – | – | – |
| orig-IP | 1 | Witherion | 298K | 3670 | 1.62M (1) | [BWpJTo7nLAs](https://www.youtube.com/watch?v=BWpJTo7nLAs) Escaping the horror mob army #minecraft #shorts — 1.62M, 24.5 d, short | none | – | – | – | – | – |
| orig-IP | 2 | Superoid Man | 42K | 1535 | 1.45M (1) | [LSPVi1PzIXM](https://www.youtube.com/watch?v=LSPVi1PzIXM) MINECRAFT BUT MOBS JOIN MY ARMY — 1.45M, 14.0 d, short | none | – | – | – | – | – |
| orig-IP | 3 | Peteson Craft | 3.42M | 2280 | 1.38M (12) | [ENEhwW1Qby0](https://www.youtube.com/watch?v=ENEhwW1Qby0) World War of Mobs / Minecraft Mob Battle — 240K, 22.2 d, long | none | – | – | – | – | – |
| orig-IP | 4 | Sunrat | 9K | 3788 | 870K (1) | [Wv06iq8RfzA](https://www.youtube.com/watch?v=Wv06iq8RfzA) Minecraft, But Every Mob Is Hunting Me At The Same Time — 870K, 9.6 d, long | none | – | – | – | – | – |

*Most popular on-format uploads in the samples (any age):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [udhWREKY2h0](https://www.youtube.com/watch?v=udhWREKY2h0) | Brawl Lab | Last Breath Sans vs EVERY Minecraft Mob #undertale #shorts | 10.1 | 409K | 106 s | 7.7× | 6.1× | 9K | other_franchise |

*On-format outliers ≤30 d (≥3× same-format channel median or views ≥ subs):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) | Mikey Crazy | All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft | 3.8 | 2.14M | 58 s | 9.0× | 23.6× | 91K | maizen_jj_mikey |
| [udhWREKY2h0](https://www.youtube.com/watch?v=udhWREKY2h0) | Brawl Lab | Last Breath Sans vs EVERY Minecraft Mob #undertale #shorts | 10.1 | 409K | 106 s | 7.7× | 6.1× | 9K | other_franchise |
| [wKUybajlHMg](https://www.youtube.com/watch?v=wKUybajlHMg) | Mikey Crazy | JJ Golem SAVES All Mobs From a HUGE VERITY TSUNAMI! 🌊😱 #minecraft | 1.9 | 1.42M | 58 s | 6.0× | 32.0× | 91K | maizen_jj_mikey|verity_cruelty |
| [ROFxrv-1gAg](https://www.youtube.com/watch?v=ROFxrv-1gAg) | Brawl Lab | Chara vs EVERY Minecraft Mob #minecraft #shorts | 15.8 | 186K | 104 s | 3.5× | 1.8× | 9K | other_franchise |
| [rstXhQfgxDs](https://www.youtube.com/watch?v=rstXhQfgxDs) | Brawl Lab | Gargantuar vs EVERY Minecraft Mob — One Smash Kills Anything #pvz #mi… | 8.6 | 174K | 52 s | 3.3× | 3.1× | 9K | other_franchise |
| [TIMJ4hgxZV4](https://www.youtube.com/watch?v=TIMJ4hgxZV4) | Brawl Lab | Last Breath Sans vs EVERY Deltarune Boss #undertale #deltarune #shorts | 4.2 | 128K | 62 s | 2.4× | 4.7× | 9K | other_franchise |
| [O9sLjjxenr0](https://www.youtube.com/watch?v=O9sLjjxenr0) | Joeysaf | Minecraft But Every Mob Changes When I Kill One / #shorts | 20.6 | 4.64M | 140 s | 1.8× | 1.1× | 491K |  |
| [7wbF_IKUDW8](https://www.youtube.com/watch?v=7wbF_IKUDW8) | Brawl Lab | Tenna vs EVERY Minecraft Mob #minecraft #shorts | 11.6 | 93K | 59 s | 1.8× | 1.2× | 9K |  |
| [3e6nNat41Wc](https://www.youtube.com/watch?v=3e6nNat41Wc) | Brawl Lab | Kaizo Knight vs EVERY Minecraft Mob #deltarune #minecraft #shorts | 5.2 | 90K | 81 s | 1.7× | 2.6× | 9K | other_franchise |
| [MtpFq2fFI-c](https://www.youtube.com/watch?v=MtpFq2fFI-c) | Brawl Lab | Pink vs EVERY Minecraft Mob #minecraft #shorts | 13.0 | 87K | 53 s | 1.6× | 1.0× | 9K |  |

*On-format explosive ≤5 d (views/day ≥2× channel’s same-format 3–30 d median views/day, or already ≥1× channel median):*

| video | channel | title | age d | views | len | × same-fmt median | views/day ÷ channel norm | subs | 3P IP |
|---|---|---|---|---|---|---|---|---|---|
| [wKUybajlHMg](https://www.youtube.com/watch?v=wKUybajlHMg) | Mikey Crazy | JJ Golem SAVES All Mobs From a HUGE VERITY TSUNAMI! 🌊😱 #minecraft | 1.9 | 1.42M | 58 s | 6.0× | 32.0× | 91K | maizen_jj_mikey|verity_cruelty |
| [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) | Mikey Crazy | All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft | 3.8 | 2.14M | 58 s | 9.0× | 23.6× | 91K | maizen_jj_mikey |
| [UsAJx2lp1RA](https://www.youtube.com/watch?v=UsAJx2lp1RA) | Brawl Lab | Snowgrave Noelle vs EVERY Minecraft Mob #deltarune #noelle #snowgrave… | 2.0 | 61K | 94 s | 1.2× | 4.7× | 9K | other_franchise |
| [TIMJ4hgxZV4](https://www.youtube.com/watch?v=TIMJ4hgxZV4) | Brawl Lab | Last Breath Sans vs EVERY Deltarune Boss #undertale #deltarune #shorts | 4.2 | 128K | 62 s | 2.4× | 4.7× | 9K | other_franchise |
| [k_BIMDELwL0](https://www.youtube.com/watch?v=k_BIMDELwL0) | Joeysaf | Minecraft But I Have to Reveal Every Mob / #shorts | 0.6 | 795K | 155 s | 0.3× | 3.9× | 491K |  |

**Sub-lane reading (INFERRED).** This is the subset of battle titles naming mob armies, "vs every/all" or N mobs, minus player-simulation titles. Its counts in the pool (OBSERVED):
- **Shorts:** 31 videos, median 181K, 9 ≥1M, 64% original among ≥100K.
- **Long-form:** 70 videos, median 71K, 1 ≥1M, 59% original among ≥100K.

The leaders are a mix of mega (Joeysaf), JJ-IP (Mikey Crazy, MSToons) and Undertale-IP (Brawl Lab) channels. The no-IP winners are smaller: Witherion "Escaping the horror mob army" 1.62M, Superoid Man "MINECRAFT BUT MOBS JOIN MY ARMY" 1.45M (42K subs), and Sunrat "…Every Mob Is Hunting Me" 870K (9K subs).


**Title features of on-format outliers vs the same channels' other on-format uploads** (OBSERVED, `derived_F_outlier_title_features.csv`, uploads ≤60 d). Samples are small and dominated by a few channels, so read these as hints only:
- **Survival:** 8 outliers, all long-form, median 49 min vs 25 min for the rest.
- **Mystery:** 19% of outliers use "…" vs 0% of the rest. Threat words appear in 95% of outliers and 100% of the rest, so they do not separate the two.
- **Battle:** 79% of outliers contain "vs" vs 50% of the rest.
- **Lore:** a question in the title 35% vs 18%.
- **Interactive:** fewer numbers in outlier titles (39% vs 71%); short direct questions win.

## 4. ĐỐI THỦ 3 — exploding videos (0–15 days) and real growth over 16.8 h

### 4.1 Set and growth summary (OBSERVED, s2 2026-11-03 19:16Z → s3 2026-11-04 12:05Z)

**Eligible set.** From the 795 re-snapshotted ids:
- English (2026-11-03 rule) and Minecraft (text or channel level).
- Age ≤15 d at s3.
- Shorts ≥1M or long-form ≥300K.
- Not *ohnepixel raw*.

That leaves **420 videos: 356 Shorts and 64 long-form**.

**Growth labels.**

| format | accelerating | steady | decaying | frozen | median decel_ratio |
|---|---|---|---|---|---|
| Shorts | 12 | 75 | 269 | – | 0.14 |
| Long-form | 1 | 24 | 38 | 1 | 0.29 |

**IP and channel size.**
- 182 of 420 (43%) carry a third-party flag; 5 more are Herobrine-only.
- 235 (56%) are from "small" channels: <100K subs **or** views ≥10× subs. The ≥10× rule also admits BlobbyClips (2.83M subs), whose Shorts reach 16×.
- Among non-mega small-channel exploders, original and third-party are split evenly: 115 vs 114. Their median real speed is the same: 2.3K vs 2.2K views/h.

### 4.2 Top exploding videos

#### T5. Top 20 exploding videos by real views/hour over the 16.8 h gap (OBSERVED, snapshots 2026-11-03 19:16Z → 2026-11-04 12:05Z)

| # | video | channel | subs | title | age d | len | views (s3) | +views in 16.8 h | real views/h | ÷ lifetime views/h | label | views÷subs | IP | template |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [glwTiwUdhJo](https://www.youtube.com/watch?v=glwTiwUdhJo) | XOXU MINECRAFT | 35K | Who Will ADOPT JJ Kitten?! 🥺🐱 #minecraft | 1.2 | 46 s | 3.55M | 2.21M | 132K | 1.03 | accelerating | 101.4 | maizen_jj_mikey | jj_mikey_story |
| 2 | [bHxLy6Qza3M](https://www.youtube.com/watch?v=bHxLy6Qza3M) | Parrot (mega) | 4.45M | 10,000 Player Minecraft War: Nether VS Overworld | 2.8 | 240 min | 9.24M | 1.99M | 118K | 0.86 | steady | 2.1 | original | player_sim_war |
| 3 | [ChumXJor8EA](https://www.youtube.com/watch?v=ChumXJor8EA) | PumpBrine | 100K | Smartest Player VS Dr Donut Part 29 #minecraft #deathnote #… | 1.9 | 54 s | 4.87M | 1.33M | 79K | 0.76 | steady | 48.7 | dr_donut|other_franchise | dr_donut_smartest_player |
| 4 | [4w22UAHpwhE](https://www.youtube.com/watch?v=4w22UAHpwhE) | PumpBrine | 100K | Smartest Player VS Dr Donut #minecraft #deathnote #skit #fu… | 6.9 | 53 s | 13.48M | 920K | 55K | 0.67 | steady | 134.8 | dr_donut|other_franchise | dr_donut_smartest_player |
| 5 | [Jl-KVNhnMjo](https://www.youtube.com/watch?v=Jl-KVNhnMjo) | lowkiMC | 98K | This feels like a scene from interstellar 🥹 | 3.5 | 20 s | 19.79M | 914K | 54K | 0.23 | decaying | 202.2 | other_franchise | other |
| 6 | [xxa_Jpt0l_M](https://www.youtube.com/watch?v=xxa_Jpt0l_M) | PumpBrine | 100K | Smartest Player VS Dr Donut Part 32 #minecraft #deathnote #… | 1.3 | 54 s | 1.97M | 855K | 51K | 0.82 | steady | 19.7 | dr_donut|other_franchise | dr_donut_smartest_player |
| 7 | [Ep9sV6gEdgo](https://www.youtube.com/watch?v=Ep9sV6gEdgo) | DrDonut Clips | 2.35M | ive seen this prank | 6.3 | 17 s | 3.29M | 805K | 48K | 2.20 | accelerating | 1.4 | original | other |
| 8 | [IGiveq3olJU](https://www.youtube.com/watch?v=IGiveq3olJU) | CheezyChez | 1.08M | Cushion in water | 2.0 | 32 s | 3.29M | 798K | 48K | 0.71 | steady | 3.0 | original | other |
| 9 | [TKv74nlJCXs](https://www.youtube.com/watch?v=TKv74nlJCXs) | BlobbyClips | 2.83M | Crafting Circles in Minecraft! 😂😂 | 12.8 | 25 s | 46.32M | 770K | 46K | 0.30 | decaying | 16.4 | original | emoji_reaction_meme |
| 10 | [uiLAXLyBwlY](https://www.youtube.com/watch?v=uiLAXLyBwlY) | Craft Lab3D | 196K | Minecraft Steve vs Death Factory 💀 | 5.2 | 17 s | 7.17M | 680K | 40K | 0.70 | steady | 36.6 | original | emoji_reaction_meme |
| 11 | [Cxpnf26tWqs](https://www.youtube.com/watch?v=Cxpnf26tWqs) | Mikey Crazy | 91K | DARK JJ GAVE His BODY PARTS to His FRIENDS! 😱 #minecraft | 4.9 | 51 s | 1.66M | 648K | 39K | 2.73 | accelerating | 18.3 | maizen_jj_mikey | jj_mikey_story |
| 12 | [H1_V9gxhQfg](https://www.youtube.com/watch?v=H1_V9gxhQfg) | 1997studio | 24K | JJ & Mikey, Who win ?! #minecraft #shorts | 3.0 | 19 s | 2.45M | 614K | 37K | 1.09 | accelerating | 102.2 | maizen_jj_mikey | jj_mikey_story |
| 13 | [dpB7vy8n1x8](https://www.youtube.com/watch?v=dpB7vy8n1x8) | JojoCraft | 378K | Mikey Dont Want Corn 🌽 #minecraftshorts | 4.5 | 11 s | 3.90M | 591K | 35K | 0.98 | steady | 10.3 | maizen_jj_mikey | jj_mikey_story |
| 14 | [D6br6Dam-rA](https://www.youtube.com/watch?v=D6br6Dam-rA) | Floog | 2K | larp / #animation #alanbecker #avm #minecraft | 2.7 | 18 s | 2.16M | 562K | 33K | 0.99 | steady | 1213.7 | other_franchise | other |
| 15 | [Rwx6b2ngh5w](https://www.youtube.com/watch?v=Rwx6b2ngh5w) | Cheesy Animation | 197K | No One Helped Evil JJ… 😱 #minecraft #shorts | 6.9 | 79 s | 10.78M | 543K | 32K | 0.49 | steady | 54.7 | maizen_jj_mikey | jj_mikey_story |
| 16 | [LKdjKUER3aY](https://www.youtube.com/watch?v=LKdjKUER3aY) | zedarGG | 232K | DUMB the SOUND 🤦‍♂️ | 6.9 | 64 s | 3.94M | 532K | 32K | 1.33 | accelerating | 17.0 | original | the_sound_meme |
| 17 | [7wJa_TnXdwU](https://www.youtube.com/watch?v=7wJa_TnXdwU) | BlobbyClips | 2.83M | Minecraft Mods Then vs Now! 🤣🤣 | 4.8 | 22 s | 12.08M | 529K | 31K | 0.30 | decaying | 4.3 | original | emoji_reaction_meme |
| 18 | [y-IFKuhBqBE](https://www.youtube.com/watch?v=y-IFKuhBqBE) | Oren Shorts | 4.70M | Masha and Bear X Kpop Head Noob Pro Jump Challenge (Part 1)… | 2.8 | 33 s | 1.70M | 491K | 29K | 1.16 | accelerating | 0.4 | kpop_demon_hunters|other_franchise | kpop_demon_hunters |
| 19 | [y-fSEQ00Idw](https://www.youtube.com/watch?v=y-fSEQ00Idw) | flexy31z | 12K | HELP Herobrine To Power Up And Split The Bedrock #friendshi… | 7.0 | 56 s | 1.54M | 479K | 28K | 3.10 | accelerating | 127.3 | Herobrine | help_herobrine_family |
| 20 | [xjokcIXG28k](https://www.youtube.com/watch?v=xjokcIXG28k) | NoobySquad | 81K | Can We Survive the BIGGEST Sponge TNT? 💣🧽 | 6.1 | 44 s | 1.74M | 451K | 27K | 2.25 | accelerating | 21.4 | original | other |

#### T6. Top 20 from SMALL channels (<100K subs or views ≥10× subs), same ranking

| # | video | channel | subs | title | age d | len | views (s3) | +views in 16.8 h | real views/h | ÷ lifetime views/h | label | views÷subs | IP | template |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [glwTiwUdhJo](https://www.youtube.com/watch?v=glwTiwUdhJo) | XOXU MINECRAFT | 35K | Who Will ADOPT JJ Kitten?! 🥺🐱 #minecraft | 1.2 | 46 s | 3.55M | 2.21M | 132K | 1.03 | accelerating | 101.4 | maizen_jj_mikey | jj_mikey_story |
| 2 | [ChumXJor8EA](https://www.youtube.com/watch?v=ChumXJor8EA) | PumpBrine | 100K | Smartest Player VS Dr Donut Part 29 #minecraft #deathnote #… | 1.9 | 54 s | 4.87M | 1.33M | 79K | 0.76 | steady | 48.7 | dr_donut|other_franchise | dr_donut_smartest_player |
| 3 | [4w22UAHpwhE](https://www.youtube.com/watch?v=4w22UAHpwhE) | PumpBrine | 100K | Smartest Player VS Dr Donut #minecraft #deathnote #skit #fu… | 6.9 | 53 s | 13.48M | 920K | 55K | 0.67 | steady | 134.8 | dr_donut|other_franchise | dr_donut_smartest_player |
| 4 | [Jl-KVNhnMjo](https://www.youtube.com/watch?v=Jl-KVNhnMjo) | lowkiMC | 98K | This feels like a scene from interstellar 🥹 | 3.5 | 20 s | 19.79M | 914K | 54K | 0.23 | decaying | 202.2 | other_franchise | other |
| 5 | [xxa_Jpt0l_M](https://www.youtube.com/watch?v=xxa_Jpt0l_M) | PumpBrine | 100K | Smartest Player VS Dr Donut Part 32 #minecraft #deathnote #… | 1.3 | 54 s | 1.97M | 855K | 51K | 0.82 | steady | 19.7 | dr_donut|other_franchise | dr_donut_smartest_player |
| 6 | [TKv74nlJCXs](https://www.youtube.com/watch?v=TKv74nlJCXs) | BlobbyClips | 2.83M | Crafting Circles in Minecraft! 😂😂 | 12.8 | 25 s | 46.32M | 770K | 46K | 0.30 | decaying | 16.4 | original | emoji_reaction_meme |
| 7 | [uiLAXLyBwlY](https://www.youtube.com/watch?v=uiLAXLyBwlY) | Craft Lab3D | 196K | Minecraft Steve vs Death Factory 💀 | 5.2 | 17 s | 7.17M | 680K | 40K | 0.70 | steady | 36.6 | original | emoji_reaction_meme |
| 8 | [Cxpnf26tWqs](https://www.youtube.com/watch?v=Cxpnf26tWqs) | Mikey Crazy | 91K | DARK JJ GAVE His BODY PARTS to His FRIENDS! 😱 #minecraft | 4.9 | 51 s | 1.66M | 648K | 39K | 2.73 | accelerating | 18.3 | maizen_jj_mikey | jj_mikey_story |
| 9 | [H1_V9gxhQfg](https://www.youtube.com/watch?v=H1_V9gxhQfg) | 1997studio | 24K | JJ & Mikey, Who win ?! #minecraft #shorts | 3.0 | 19 s | 2.45M | 614K | 37K | 1.09 | accelerating | 102.2 | maizen_jj_mikey | jj_mikey_story |
| 10 | [dpB7vy8n1x8](https://www.youtube.com/watch?v=dpB7vy8n1x8) | JojoCraft | 378K | Mikey Dont Want Corn 🌽 #minecraftshorts | 4.5 | 11 s | 3.90M | 591K | 35K | 0.98 | steady | 10.3 | maizen_jj_mikey | jj_mikey_story |
| 11 | [D6br6Dam-rA](https://www.youtube.com/watch?v=D6br6Dam-rA) | Floog | 2K | larp / #animation #alanbecker #avm #minecraft | 2.7 | 18 s | 2.16M | 562K | 33K | 0.99 | steady | 1213.7 | other_franchise | other |
| 12 | [Rwx6b2ngh5w](https://www.youtube.com/watch?v=Rwx6b2ngh5w) | Cheesy Animation | 197K | No One Helped Evil JJ… 😱 #minecraft #shorts | 6.9 | 79 s | 10.78M | 543K | 32K | 0.49 | steady | 54.7 | maizen_jj_mikey | jj_mikey_story |
| 13 | [LKdjKUER3aY](https://www.youtube.com/watch?v=LKdjKUER3aY) | zedarGG | 232K | DUMB the SOUND 🤦‍♂️ | 6.9 | 64 s | 3.94M | 532K | 32K | 1.33 | accelerating | 17.0 | original | the_sound_meme |
| 14 | [y-fSEQ00Idw](https://www.youtube.com/watch?v=y-fSEQ00Idw) | flexy31z | 12K | HELP Herobrine To Power Up And Split The Bedrock #friendshi… | 7.0 | 56 s | 1.54M | 479K | 28K | 3.10 | accelerating | 127.3 | Herobrine | help_herobrine_family |
| 15 | [xjokcIXG28k](https://www.youtube.com/watch?v=xjokcIXG28k) | NoobySquad | 81K | Can We Survive the BIGGEST Sponge TNT? 💣🧽 | 6.1 | 44 s | 1.74M | 451K | 27K | 2.25 | accelerating | 21.4 | original | other |
| 16 | [UiRv3wqFuIs](https://www.youtube.com/watch?v=UiRv3wqFuIs) | Mrjunaid Short | 14K | Minecraft game play with animation #minecraft #minecraftbui… | 4.0 | 85 s | 2.85M | 451K | 27K | 0.91 | steady | 204.9 | original | other |
| 17 | [h69NvBvgPj8](https://www.youtube.com/watch?v=h69NvBvgPj8) | Minecraft Sea | 249K | Dancing Like Different Animals Backstage 🦖🦍🐶- Minecraft Ani… | 3.5 | 19 s | 4.65M | 392K | 23K | 0.42 | steady | 18.7 | original | other |
| 18 | [EkNgf9DDtwM](https://www.youtube.com/watch?v=EkNgf9DDtwM) | MaizCr | 35K | During the Day vs At Night 🚒🚛🚂🚜#minecraft  #animation #funny | 3.1 | 17 s | 2.00M | 370K | 22K | 0.82 | steady | 57.4 | original | other |
| 19 | [9RV1BTPFoCw](https://www.youtube.com/watch?v=9RV1BTPFoCw) | Headfilter67CookieGuy | 460K | which one did you get ft. Jerry in Minecraft #dog | 6.8 | 8 s | 6.18M | 317K | 19K | 0.50 | steady | 13.4 | jerry_wolf_dog | jerry_dog_lookout |
| 20 | [wKUybajlHMg](https://www.youtube.com/watch?v=wKUybajlHMg) | Mikey Crazy | 91K | JJ Golem SAVES All Mobs From a HUGE VERITY TSUNAMI! 🌊😱 #min… | 1.9 | 58 s | 1.42M | 280K | 17K | 0.52 | steady | 15.7 | maizen_jj_mikey|verity_cruelty | verity_family |

#### T7. Long-form (>180 s, ≥300K) by real views/hour

| # | video | channel | subs | title | age d | len | views (s3) | +views in 16.8 h | real views/h | ÷ lifetime views/h | label | views÷subs | IP | template |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [bHxLy6Qza3M](https://www.youtube.com/watch?v=bHxLy6Qza3M) | Parrot (mega) | 4.45M | 10,000 Player Minecraft War: Nether VS Overworld | 2.8 | 240 min | 9.24M | 1.99M | 118K | 0.86 | steady | 2.1 | original | player_sim_war |
| 2 | [FSCGy0YaUaE](https://www.youtube.com/watch?v=FSCGy0YaUaE) | MSToons | 1.77M | YOU Trolled JJ and Mikey with Infinite Hearts! - Maizen Min… | 1.8 | 10 min | 1.42M | 390K | 23K | 0.72 | steady | 0.8 | maizen_jj_mikey | jj_mikey_story |
| 3 | [y5IdSoHdkgg](https://www.youtube.com/watch?v=y5IdSoHdkgg) | Spoke (mega) | 2.91M | 10,000 Players Simulate COLD WAR in Minecraft | 12.5 | 240 min | 13.73M | 354K | 21K | 0.46 | steady | 4.7 | original | player_sim_war |
| 4 | [ZGYi_JjKhfE](https://www.youtube.com/watch?v=ZGYi_JjKhfE) | Sticks | 1.16M | If Technoblade's Life Was a Movie... | 3.9 | 14 min | 3.43M | 307K | 18K | 0.49 | steady | 3.0 | dream_smp_creators | other |
| 5 | [ZT-k42SC7L0](https://www.youtube.com/watch?v=ZT-k42SC7L0) | FlameFrags | 3.08M | 10,000 VS 10,000 Player Minecraft War | 3.8 | 147 min | 5.02M | 235K | 14K | 0.26 | decaying | 1.6 | original | player_sim_war |
| 6 | [KnlAF_djhdc](https://www.youtube.com/watch?v=KnlAF_djhdc) | SpeedSilver | 4.00M | 1000 Players Simulate Minecraft's Deadliest Containment Zon… | 4.6 | 150 min | 2.53M | 195K | 12K | 0.51 | steady | 0.6 | original | player_sim_war |
| 7 | [ls0FQdzVxko](https://www.youtube.com/watch?v=ls0FQdzVxko) | ProBoiz 95 | 9.41M | Testing Trending Minecraft Scary Myths To See If They Are R… | 6.9 | 40 min | 6.47M | 179K | 11K | 0.27 | decaying | 0.7 | original | horror_mod_myth |
| 8 | [g-GgM-kVnNs](https://www.youtube.com/watch?v=g-GgM-kVnNs) | Cubeee Animations | 51K | MAIZEN : ALL EPISODE JJ Sister LOVES JJ - Minecraft Animati… | 7.8 | 54 min | 2.37M | 174K | 10K | 0.81 | steady | 46.8 | maizen_jj_mikey | jj_mikey_story |
| 9 | [QBzI4ENJw5g](https://www.youtube.com/watch?v=QBzI4ENJw5g) | FroggyDude Gaming | 593K | FroggyDude VS Grox MANHUNT | 2.9 | 22 min | 1.34M | 171K | 10K | 0.53 | steady | 2.3 | original | other |
| 10 | [Ed74ounoOhc](https://www.youtube.com/watch?v=Ed74ounoOhc) | LookOut2DD | 1.16M | Jerry The Dog [FULL MOVIE] | 9.8 | 119 min | 2.88M | 149K | 9K | 0.73 | steady | 2.5 | jerry_wolf_dog | jerry_dog_lookout |
| 11 | [Sv78gB7zi_E](https://www.youtube.com/watch?v=Sv78gB7zi_E) | Beppo | 2.37M | Achievement = 1 Block | 7.4 | 66 min | 3.67M | 149K | 9K | 0.43 | steady | 1.6 | original | other |
| 12 | [Lnl-4FT77Ws](https://www.youtube.com/watch?v=Lnl-4FT77Ws) | MSToons | 1.77M | JJ BUS EATER was Buried Under The Water - Maizen Minecraft … | 3.8 | 13 min | 1.51M | 142K | 8K | 0.51 | steady | 0.9 | maizen_jj_mikey | jj_mikey_story |

#### T8. Original-IP (no third-party flag) exploders from small channels

| # | video | channel | subs | title | age d | len | views (s3) | +views in 16.8 h | real views/h | ÷ lifetime views/h | label | views÷subs | IP | template |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [TKv74nlJCXs](https://www.youtube.com/watch?v=TKv74nlJCXs) | BlobbyClips | 2.83M | Crafting Circles in Minecraft! 😂😂 | 12.8 | 25 s | 46.32M | 770K | 46K | 0.30 | decaying | 16.4 | original | emoji_reaction_meme |
| 2 | [uiLAXLyBwlY](https://www.youtube.com/watch?v=uiLAXLyBwlY) | Craft Lab3D | 196K | Minecraft Steve vs Death Factory 💀 | 5.2 | 17 s | 7.17M | 680K | 40K | 0.70 | steady | 36.6 | original | emoji_reaction_meme |
| 3 | [LKdjKUER3aY](https://www.youtube.com/watch?v=LKdjKUER3aY) | zedarGG | 232K | DUMB the SOUND 🤦‍♂️ | 6.9 | 64 s | 3.94M | 532K | 32K | 1.33 | accelerating | 17.0 | original | the_sound_meme |
| 4 | [y-fSEQ00Idw](https://www.youtube.com/watch?v=y-fSEQ00Idw) | flexy31z | 12K | HELP Herobrine To Power Up And Split The Bedrock #friendshi… | 7.0 | 56 s | 1.54M | 479K | 28K | 3.10 | accelerating | 127.3 | Herobrine | help_herobrine_family |
| 5 | [xjokcIXG28k](https://www.youtube.com/watch?v=xjokcIXG28k) | NoobySquad | 81K | Can We Survive the BIGGEST Sponge TNT? 💣🧽 | 6.1 | 44 s | 1.74M | 451K | 27K | 2.25 | accelerating | 21.4 | original | other |
| 6 | [UiRv3wqFuIs](https://www.youtube.com/watch?v=UiRv3wqFuIs) | Mrjunaid Short | 14K | Minecraft game play with animation #minecraft #minecraftbui… | 4.0 | 85 s | 2.85M | 451K | 27K | 0.91 | steady | 204.9 | original | other |
| 7 | [h69NvBvgPj8](https://www.youtube.com/watch?v=h69NvBvgPj8) | Minecraft Sea | 249K | Dancing Like Different Animals Backstage 🦖🦍🐶- Minecraft Ani… | 3.5 | 19 s | 4.65M | 392K | 23K | 0.42 | steady | 18.7 | original | other |
| 8 | [EkNgf9DDtwM](https://www.youtube.com/watch?v=EkNgf9DDtwM) | MaizCr | 35K | During the Day vs At Night 🚒🚛🚂🚜#minecraft  #animation #funny | 3.1 | 17 s | 2.00M | 370K | 22K | 0.82 | steady | 57.4 | original | other |
| 9 | [3is1ebirAXQ](https://www.youtube.com/watch?v=3is1ebirAXQ) | nixil | 33K | Jesus in 2b2t’s spawn update | 6.6 | 61 s | 3.22M | 279K | 17K | 0.82 | steady | 96.4 | original | other |
| 10 | [OPMBE8pgPdQ](https://www.youtube.com/watch?v=OPMBE8pgPdQ) | Drdonutt Official Clip | 32K | POV When Nostalgia Starts Hitting Hard | 11.8 | 25 s | 4.74M | 267K | 16K | 0.94 | steady | 150.4 | original | other |
| 11 | [PrqXRtXSPfg](https://www.youtube.com/watch?v=PrqXRtXSPfg) | Pixel Lume | 192K | Minecraft whole room projector 📽️ | 8.1 | 19 s | 7.09M | 242K | 14K | 0.39 | decaying | 36.9 | original | other |
| 12 | [je8PaFFsTwU](https://www.youtube.com/watch?v=je8PaFFsTwU) | CraftLore | 61K | Finding The Impossible Seed | 3.7 | 50 s | 1.27M | 240K | 14K | 0.99 | steady | 20.6 | original | other |
| 13 | [Af43UFHita0](https://www.youtube.com/watch?v=Af43UFHita0) | lowkiMC | 98K | They’re still figuring out the job 😭 | 2.7 | 18 s | 2.26M | 220K | 13K | 0.38 | decaying | 23.1 | original | emoji_reaction_meme |
| 14 | [ow9qGwMrSTk](https://www.youtube.com/watch?v=ow9qGwMrSTk) | Mine Mythos | 16K | Bro Crafted Netherite Armor 💀 | 7.7 | 13 s | 3.47M | 207K | 12K | 0.66 | steady | 218.0 | original | emoji_reaction_meme |
| 15 | [K7xFyRmxoB0](https://www.youtube.com/watch?v=K7xFyRmxoB0) | Verity Verifies MC | 2K | How To Breed Horses Perfectly... #shorts | 5.2 | 53 s | 1.85M | 176K | 10K | 0.70 | steady | 1033.5 | original | other |

#### T9. ≤15-day videos ≥1M (long ≥300K) found only in today’s lane scan (no growth measure; ranked by lifetime views/day)

| video | channel | subs | title | age d | fmt | views | views/day | views÷subs | IP | template |
|---|---|---|---|---|---|---|---|---|---|---|
| [0QxH2wcSV0I](https://www.youtube.com/watch?v=0QxH2wcSV0I) | Joeysaf (mega) | 491K | Minecraft But Everything Moves 10x Faster When I Look Away … | 1.5 | short | 1.62M | 1.06M | 3.3 | original | minecraft_but |
| [9rXD7tIzPC8](https://www.youtube.com/watch?v=9rXD7tIzPC8) | Xanner | 72K | Will JJ be able to HIDE from VERITY Phone x Moon x Truck? #… | 7.8 | short | 6.54M | 838K | 91.3 | maizen_jj_mikey|verity_cruelty | verity_family |
| [pw8KekF78uM](https://www.youtube.com/watch?v=pw8KekF78uM) | camman18 | 11.40M | name the mobs | 2.8 | short | 1.47M | 520K | 0.1 | original | other |
| [rd1-03tTTgs](https://www.youtube.com/watch?v=rd1-03tTTgs) | ROBLOXICO | 346K | Minecraft Mobs vs GIANT Bosses! ⛏️👹 | 12.8 | short | 4.33M | 338K | 12.5 | original | other |
| [wq01bCUjGrc](https://www.youtube.com/watch?v=wq01bCUjGrc) | Cash (mega) | 11.80M | From POOR to RICH Cliff House in Minecraft! | 4.9 | long | 1.36M | 280K | 0.1 | original | other |
| [CfbO_D_LT74](https://www.youtube.com/watch?v=CfbO_D_LT74) | Cash (mega) | 11.80M | We Trapped EVERY MONSTER in Minecraft.. | 5.9 | long | 1.56M | 266K | 0.1 | original | other |
| [wsC7Qc3pOGo](https://www.youtube.com/watch?v=wsC7Qc3pOGo) | BabyCrab | 639K | Baby Steve😇 and Baby Zombie😈 — which one will you choose to… | 5.0 | short | 1.13M | 227K | 1.8 | original | who_will_win_choose |
| [9klofxQUqQ0](https://www.youtube.com/watch?v=9klofxQUqQ0) | FoxiLu | 74K | Why didn't the girl believe JJ? Which JJ is Real? 😨💔 #minec… | 10.7 | short | 2.05M | 192K | 27.9 | maizen_jj_mikey | jj_mikey_story |
| [csqOUnEbpOc](https://www.youtube.com/watch?v=csqOUnEbpOc) | TechyCraft | 1.32M | Dirt vs MONEY Skyblock Battle in Minecraft... | 4.0 | long | 700K | 175K | 0.5 | original | other |
| [--0KP-bA0p4](https://www.youtube.com/watch?v=--0KP-bA0p4) | Ryguyrocky | 3.93M | I Survived 100 Days as a Necromancer in Minecraft | 4.0 | long | 684K | 172K | 0.2 | original | survived_n_days |
| [hvQ45N6SpWo](https://www.youtube.com/watch?v=hvQ45N6SpWo) | Vivilly | 1.90M | most complicated redstone door | 10.8 | short | 1.83M | 170K | 1.0 | original | other |
| [y3LxjHNTGz4](https://www.youtube.com/watch?v=y3LxjHNTGz4) | MartianMC | 325K | how to make a insane rabbit cage #minecraft @brizinhueng | 6.3 | short | 1.04M | 166K | 3.2 | original | other |
| [9ULv8twx2ac](https://www.youtube.com/watch?v=9ULv8twx2ac) | Rank it Laughs | 263K | Top 3 Funniest Minecraft Horror Mod Moments 😂 (Bro has 0 su… | 6.8 | short | 1.12M | 163K | 4.2 | original | horror_mod_myth |
| [UZfAbp3nlVQ](https://www.youtube.com/watch?v=UZfAbp3nlVQ) | Cash (mega) | 11.80M | Boys vs Girls: POOR to RICH Chunk Battle! | 9.9 | long | 1.60M | 162K | 0.1 | original | other |
| [oVwGOpG7r2w](https://www.youtube.com/watch?v=oVwGOpG7r2w) | GameToons + | 1.86M | REVENGE of LORD VERITY... (Minecraft Animation) | 4.6 | long | 751K | 162K | 0.4 | verity_cruelty | verity_family |

### 4.3 Trend templates

| template | exploding (re-snap / new today) | Shorts / long | from small ch. | 3P share | median real views/h | accel / steady / decay | sample uploads (channels) | ≥1M in sample | first seen in sample | first ≥1M | uploads (channels) since 20 Oct | 3P share in sample |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| jj_mikey_story | 82 / 17 | 76 / 6 | 57 | 100% | 2K | 5 / 18 / 59 | 2026 (176) | 473 | 2025-07-30 | 2025-12-06 | 789 (152) | 98% |
| emoji_reaction_meme | 31 / 1 | 31 / 0 | 24 | 23% | 3K | 0 / 7 / 24 | 1937 (369) | 265 | 2026-01-21 | 2026-03-08 | 1011 (290) | 13% |
| verity_family | 25 / 6 | 21 / 4 | 16 | 100% | 958 | 0 / 4 / 21 | 1085 (172) | 267 | 2026-06-21 | 2026-06-21 | 379 (116) | 100% |
| minecraft_but | 23 / 3 | 21 / 2 | 6 | 0% | 800 | 0 / 5 / 18 | 484 (160) | 159 | 2025-05-14 | 2025-05-14 | 190 (126) | 6% |
| 1or2_reaction_reveal | 16 / 0 | 16 / 0 | 1 | 100% | 1K | 0 / 2 / 14 | 48 (6) | 28 | 2026-09-29 | 2026-10-17 | 40 (4) | 90% |
| kpop_demon_hunters | 12 / 0 | 12 / 0 | 7 | 100% | 4K | 1 / 2 / 9 | 313 (39) | 39 | 2026-02-25 | 2026-07-14 | 151 (29) | 100% |
| dr_donut_smartest_player | 12 / 0 | 12 / 0 | 12 | 100% | 11K | 0 / 7 / 5 | 169 (28) | 22 | 2026-09-23 | 2026-10-02 | 130 (25) | 99% |
| horror_mod_myth | 8 / 7 | 2 / 6 | 2 | 0% | 3K | 0 / 1 / 7 | 556 (251) | 58 | 2023-12-17 | 2023-12-17 | 287 (179) | 5% |
| player_sim_war | 6 / 2 | 0 / 6 | 1 | 0% | 13K | 1 / 3 / 2 | 117 (71) | 33 | 2023-12-09 | 2023-12-09 | 55 (39) | 11% |
| who_will_win_choose | 6 / 1 | 6 / 0 | 3 | 17% | 1K | 0 / 1 / 5 | 265 (115) | 47 | 2023-06-17 | 2023-06-17 | 144 (84) | 25% |
| help_herobrine_family | 6 / 0 | 6 / 0 | 3 | 17% | 5K | 1 / 3 / 2 | 436 (124) | 64 | 2026-01-10 | 2026-01-10 | 190 (88) | 13% |
| the_sound_meme | 4 / 0 | 4 / 0 | 1 | 0% | 13K | 1 / 2 / 1 | 84 (7) | 24 | 2026-09-19 | 2026-09-20 | 38 (7) | 0% |
| jerry_dog_lookout | 4 / 2 | 2 / 2 | 2 | 100% | 6K | 0 / 2 / 2 | 113 (38) | 37 | 2026-08-31 | 2026-09-26 | 44 (27) | 100% |
| noob_pro_hacker | 3 / 1 | 2 / 1 | 1 | 0% | 586 | 0 / 1 / 2 | 502 (128) | 68 | 2025-08-01 | 2025-08-01 | 205 (85) | 12% |
| survived_n_days | 3 / 6 | 0 / 3 | 2 | 0% | 1K | 0 / 1 / 2 | 190 (86) | 39 | 2024-02-24 | 2024-02-24 | 81 (61) | 6% |
| zombie_outbreak_apocalypse | 3 / 1 | 1 / 2 | 0 | 33% | 817 | 0 / 1 / 2 | 215 (54) | 15 | 2023-12-15 | 2023-12-15 | 133 (35) | 0% |
| perfect_world_trend | 1 / 0 | 1 / 0 | 1 | 0% | 5K | 0 / 0 / 1 | 20 (8) | 11 | 2026-09-01 | 2026-09-01 | 12 (7) | 0% |
| physics_tug_drop | 1 / 0 | 1 / 0 | 0 | 0% | 764 | 0 / 0 / 1 | 59 (32) | 27 | 2025-04-04 | 2025-04-04 | 25 (18) | 7% |
| full_movie_compilation | 0 / 1 | 0 / 0 | 0 | – | – | 0 / 0 / 0 | 53 (37) | 6 | 2026-04-26 | 2026-05-23 | 37 (32) | 4% |

First-seen dates are the earliest matching upload in any sample. Samples hold ≤50 uploads per channel, so a 2023–2024 date only shows that the template is at least that old (bounded by sample depth). Reading of T10 (INFERRED from the OBSERVED counts):

**Short-lived third-party waves (avoid; also a policy risk).** All are 99–100% third-party, almost all Shorts, and mostly decaying:

| wave | first seen | first ≥1M | in last 15 days |
|---|---|---|---|
| Smartest Player VS Dr Donut / Death Note skits | 2026-09-23 | 2026-10-02 | 130 uploads from 25 channels |
| "1 or 2 … Reaction Reveal" (Stonecraft JJ) | 2026-09-29 | 2026-10-17 | 4 channels |
| Jerry the dog / Lookout | 2026-08-31 | – | – |
| Verity family | 2026-06-21 | – | 379 uploads from 116 channels |
| K-pop Demon Hunters heads | 2026-02-25 | – | – |
| JJ/Mikey stories (the base layer) | – | – | 789 uploads from 152 channels |

**Durable original templates.** All have ≤11% third-party share:
- horror mod/myth testing (in samples since 2023-12)
- player-simulation wars (2023-12)
- "I survived N days" (2024-02)
- zombie outbreak/apocalypse (2023-12)
- "Minecraft, but" (2025-05)

Their exploding entries are mostly long-form and mostly from established channels, apart from Day Zero, Clooless and BowlerCraft in §3/T6.

**Original Shorts templates that small channels are exploding with now.** These are cheap to make and own:
- **Physics/destruction experiments:**
  - Craft Lab3D "Steve vs Death Factory" 7.17M, 196K subs.
  - NoobySquad "Can We Survive the BIGGEST Sponge TNT?" 1.74M, 81K subs, accelerating 2.25.
  - Pixel Lume projector 7.09M.
  - Hoodie Steve "Tug of War: Villagers vs Mobs" 1.97M, 4,970 subs (§3).
- **"[ADJ] the SOUND":** zedarGG, accelerating 1.33. Seven channels in the samples; it is a meme format.
- **Herobrine "HELP … / family" interactive Shorts:** flexy31z, 12K subs, 1.54M, accelerating 3.10. Herobrine is Mojang lore, but these sit in the kid-tone interactive lane.
- **Mechanic "secret/trick" Shorts:**
  - CraftLore "Finding The Impossible Seed", 61K subs.
  - Verity Verifies MC "How To Breed Horses Perfectly", 2K subs, 1.85M. The channel name contains "Verity" but the content is not the Verity IP.

### 4.4 Adjacent signal outside Minecraft (excluded from all lane numbers)

The Minecraft filter excluded *Nobody Gets In*: created 2026-10-01, 58.1K subs. Its tags say "stickman animation", so it is not Minecraft. OBSERVED 2026-11-04:
- "Zombie Outbreak: 30 Days Locked Inside a Supermarket" — 3.28M, 11 min ([oXj7bWgRX_I](https://www.youtube.com/watch?v=oXj7bWgRX_I)).
- "…Inside a School" — 1.86M, 9 min ([2XYr2AEHDGI](https://www.youtube.com/watch?v=2XYr2AEHDGI)).
- 5 long videos ≥300K at 34 days old.

Two *Beanie Survives* channels, 107K and 9.6K subs, run the same "Zombie Outbreak: 30 Days Trapped On The 30th Floor" / "Ep. 3: Leaving The Tower On Day 90" template:
- 2.85M ([1AF04-V4Yao](https://www.youtube.com/watch?v=1AF04-V4Yao))
- 869K ([LmM7TLWBWok](https://www.youtube.com/watch?v=LmM7TLWBWok))

**INFERRED:** the *story template* — a confined place, a day counter and resource scarcity, at 8–11 min — is exploding for brand-new animated channels regardless of the game skin. It is the strongest newcomer evidence for the survival lane.

Under the OWNER's competitor rule B (channels created 0–30 d ago with ≥2 long videos ≥1M), Nobody Gets In qualifies at 34 d except for the "Minecraft" tag. Day Zero (29.9 d, 1 long ≥1M plus a second at 376K) is the closest Minecraft candidate. Both are worth adding to the watchlist (INFERRED; the owner decides).

## 5. Recommendation (INFERRED; the owner decides — please log the choice with `python tools/cf_decision.py add …`)

The studio has an original cast (Bin, Bo, baby zombie Zu), Blender/Mine-imator animation, Minecraft Java, command-driven mob sims, and local-LLM bots. Weighing all five criteria:

### 5.1 Main lane: long-form scripted survival "movie" with a mystery/threat hook (score 20/25; 21 by query lanes)

**Format:** "Day 1 → Day 100" (or "30 Days Trapped in …") with Bin/Bo/Zu, 40–60 min, plus 3–4-episode compilations. The mystery universe is the threat engine ("Something is wrong with our farm…"), so the OWNER's main and secondary lanes become one show.

**Evidence (OBSERVED 2026-11-04 unless noted):**
- 97% of lane views are long-form; 87% original IP; 4% kid tone.
- ≥1M hits: 26 today and 16 in the 2026-11-03 ≤15-day set.
- Durable since at least 2023-12: Forge Labs has 14.8–26.0M at 2.3–2.7 years.
- Newcomer proof:
  - **Day Zero** (14K subs, 29.9 d old, 4 uploads): "I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft", 1.91M at 27.7 d, 52 min — 136× subs.
  - **Clooless Gaming** (319K, 348 d): 8 on-format outliers ≤30 d, 41–56 min.
- Mystery-hook proof: **SirCloaked** (141K, 347 d), "Something Is Wrong With My Farm..." 1.21M and "Something On My Farm Wants Me Dead..." 970K, at 16–19 min.
- Adjacent: the stickman "Zombie Outbreak: 30 Days" channels in §4.4.
- On-format outliers' long videos run a median of 49 min vs 25 min for the same channels' other uploads (OBSERVED, small n).

**Main risks:**
1. **Cost per finished minute.** Competitors mostly *record modded gameplay*. 40–60 animated minutes per episode in Blender/Mine-imator on one RTX 3060 has not been measured. Benchmark scripted **machinima on Java** (scripted acting plus Replay-mod cameras) against Mine-imator before committing; check `data/production_ledger.jsonl` (INFERRED).
2. **A cute cast reads as Made-for-Kids.** Zu as a "baby zombie" pulls toward kid tone (the family lane is 71% kid tone). Keep the tone teen (suspense, no gore) and the metadata Not-MFK to protect gaming-level RPM (~$2–3.4 vs ~$0.33–0.49; report).
3. **Formula saturation.** 35% of ≥100K survival hits are templated "I Survived 100 Days as/in X". Every episode needs a real new premise to stay clear of the repetitive-content policy.

### 5.2 Shorts funnel and second lane: command-driven mob/physics battle sims (score 16/25; 19 by query lanes)

**Format:** Java command/datapack fights and physics experiments with an ownable frame, e.g. "Zu's Zombie Army vs EVERY Mob" or "Tug of War: Villagers vs Mobs", 60–120 s. Add 10–20 min "tournament/bracket" long-forms with commentary from Bin and Bo.

**Evidence (OBSERVED 2026-11-04):**
- Battle Shorts: 82% of non-mega ≥100K hits come from <100K-subs channels and 45% from channels ≤30 d old.
- Third-party share of battle Shorts ≥100K hits is 31%.
- **Hoodie Steve** (4,970 subs, 39 d): "Minecraft Tug of War: Villagers vs Mobs" 1.97M (49.5× median); "I Dropped Minecraft Blocks on an Iron Golem" 1.54M.
- **Brawl Lab** (9K subs, 23 d): 44 outliers ≤30 d. The format works, but 80% of its uploads carry a third-party flag (Undertale/Deltarune characters) — the trap to avoid.
- Re-snapshot: NoobySquad "Can We Survive the BIGGEST Sponge TNT?" accelerating (2.25); Craft Lab3D 7.17M steady.
- Studio fit: mob AI, commands and replays are cheap compared with character animation (INFERRED).

**Main risks:**
1. Long-form demand is modest. Command mob battles have a median of 71K and one ≥1M among 70 videos, and 41% of their ≥100K hits lean on third-party characters (Godzilla, Jerry, Sans, Cat in the Hat). Shorts RPM is 3–14% of long-form, so revenue depends on converting viewers to the survival long-forms.
2. Matchup-of-the-day uploads are exactly what the inauthentic/repetitive policy targets. Each video needs a narrative frame and a cast payoff, not just a new matchup.
3. Newcomer success is concentrated: 6 channels, the top with 40%.

### 5.3 Test lane: AI-in-Minecraft long-form with local-LLM bots (score 15/25), with own-universe mechanics/lore Shorts as filler (lore 17/25)

**Format:** "We gave Bin, Bo and Zu AI brains and left them for 100 days" — LLM-driven villagers or bots on a Java server. Fold the finds into lore Shorts ("Why Zu can't …", "secret mechanic" style).

**Evidence (OBSERVED 2026-11-04):**
- AI lane: 89% original; 44% of non-mega ≥100K hits are newcomer-original.
- Small creators with LLM-server long-forms:
  - CollinCC 3 (1,920 subs, 83 d): "I Took Over Minecraft's Largest AI Server", 121K (63× subs).
  - Viral Echoes (7.3K): "I Tried Making a VIRAL Minecraft Server With Claude Opus 5.5", 132K.
  - HighwayTrooper (40K): "I Asked Claude AI to Make a Fully Custom Minecraft Server", 114K.
  - VoxelMind (4K): "My AI Villagers Thought I Was Dead / Ep. 2", 76K.
- Larger: Kiply "I Added Talking Villagers to Minecraft" 2.15M; Catkin Craft "What Happens When AI Runs a Minecraft Village?" 1.55M (Short, 184-d channel).
- Lore Shorts: 56% newcomer-original, e.g. KeyroNN (43K subs) "You Can Be IMMORTAL using a PICKAXE..." 11.2M.

**Main risk:** thin and young evidence. The AI lane has n=41, 0 videos ≥1M in yesterday's ≤15-day set, and its oldest ≥1M upload in the samples dates from 2025-11. It may be a novelty wave. Lore long-form shows a median of only 8K here, so the $3–6 lore RPM prior is unproven for this channel type. Run it as a 4–6-week test, not a pillar.

### 5.4 Do not build on (INFERRED from OBSERVED shares)

- **Family/emotional animation:** 64% third-party at ≥100K, 71% kid tone, 21% long-form share. RPM and MFK trap, as in note D.
- **Interactive Shorts:** 79% kid tone, 9% long-form share, 53% third-party.
- **"Minecraft but" Shorts as a lane:** mega-owned and 43% templated. Use the premise inside survival episodes instead.
- **Player-simulation wars:** need thousands of real players.
- **Every third-party wave in §4.3**, Herobrine-family interactive Shorts included (kid tone, mass-produced).

## 6. Gaps

1. **Search ≠ market.** Each query returns ≤50 results ordered by viewCount, so lane medians are medians of top search results. They overstate the true niche median that CLAUDE.md asks us to benchmark against. Lanes with 3–4 queries (AI, lore, but, interactive) are under-sampled.
2. **Lane rules are title regexes.** Thumbnails and content were not seen. Kid tone is lexical. `made_for_kids` is the uploader's declaration: 4 true in the pool. Some lane overlap is intended (multi-label).
3. **The Minecraft rule is strict.** 63 vocabulary-only videos (21 ≥1M) are excluded and listed in the sensitivity check. Descriptions exist only for ids from yesterday's raw pull.
4. **Leaders without upload samples get no outlier analysis.** These include CaseOh, aCookieGod, Parrot, AlphaExtra, Karry Kraft, Zachobuilds, Kiply, Swayle, Air Run, HydroMC, Peteson Craft, Witherion, Butter Penguin, BabyCrab and TeardownTown. Each costs 1–2 playlistItems units on the next quota day.
5. **Growth covers only yesterday's 795 ids.** The 82 ≤15-day ≥1M videos first seen today (T9) have lifetime views/day only. The gap is 16.8 h, not 24 h, and `views_per_day_24h_equiv` assumes a linear rate.
6. **RPM is not in the API.** Every RPM statement is inference from the RPM report plus long-form/tone shares. Only the owner's own analytics will measure it.
7. **No video was watched.** Per CLAUDE.md, outlier "commonalities" here are title/length/metadata patterns only. They are not "we learned X from competitor Y" statements; those still need the competitor full-viewing gate.
8. **Channel age ≠ creator experience.** Second channels and rebrands exist (MSToons Shorts, PrestonPlayz Top Videos, two Beanie Survives channels). Newcomer shares may overstate how open a lane is to true beginners.
9. **The IP regex is title-only.** It misses IP shown only in thumbnails or video, and it has false positives (e.g. "interstellar" as a song reference). The mega-channel list is manual.
10. **Template first-seen dates are bounded by sample depth** (≤50 uploads per channel).
11. **Owner decisions needed:**
    - confirm or adjust the lane order (survival as main vs the stored "horror-mystery main");
    - choose machinima vs full animation for 40–60 min episodes;
    - set the tone/MFK policy for Zu;
    - decide whether Nobody Gets In and Day Zero join the watchlist.
