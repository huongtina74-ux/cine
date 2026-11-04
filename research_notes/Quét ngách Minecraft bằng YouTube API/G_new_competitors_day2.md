# G. New Minecraft competitors — day 2 (2026-11-03 → 2026-11-04), outliers on the watchlist, and the updated watchlist

Scope: existing data only. **No YouTube API call, no scraping, no download was made for this note** (the day's quota was spent by the 12:00 UTC lane scan). Analysis was done with Python in the sandbox on 2026-11-04.
Snapshots used: **S-11-03** = `data/channels.csv` / `uploads.csv` / `videos.csv` (fetched 2026-11-03 19:00–19:05 UTC); **S-11-04** = `data/2026-11-04/lane_channels.csv` / `lane_uploads.csv` / `lane_videos.csv` (fetched 2026-11-04 12:00–12:05 UTC); `resnapshot_24h.csv` (795 ids, gap 16.8 h from the 19:16 UTC re-snapshot). The video-level gap between S-11-03 and S-11-04 is **17.0 h** (median, OBSERVED), not 24 h; "/day (24 h-equiv.)" scales that 17 h delta linearly (INFERRED: assumes a constant rate).
Labels: **OBSERVED** = counted from the files above (the snapshot date is given in each table header or line). **INFERRED** = my reasoning or arithmetic projection. **OWNER** = owner rules (`config/research/minecraft_story_rules.md` and the task brief).

Method notes (apply to every table):
- Video pool per channel = S-11-04 uploads (≤50 latest) ∪ S-11-04 search results, deduplicated by video id. Long = duration >180 s; Short = ≤180 s (dataset rule; the API has no Shorts flag).
- **English filter (OWNER):** a video passes if `default_audio_language` is blank, `zxx` or `en*` AND its title has no non-Latin script. Channel country is not used.
- **Created date:** channel `publishedAt` from channels.list (OBSERVED, S-11-04). The About-page "Joined" date was not opened (no browsing today), so where the owner rule asks for "Joined" the date is the API value and an About-page check is still open.
- Subscriber counts from the API are rounded to 3 significant figures, so a change of ±100 on a 14K channel or ±1,000 on a 62.8K channel is inside the rounding step.
- Outlier rules (OWNER rules operationalised the same way as in B §7, plus one new velocity test that needs two snapshots):
  - **R1** views ≥10× subs and ≥500K.
  - **R2** age ≤15 d, ≥3× the channel's same-format median (median ≥1,000) and ≥300K.
  - **R3** age ≤5 d and (≥100K views/day lifetime with ≥2× median, or ≥5× median with ≥100K).
  - **R3v (new today)** age ≤5 d and ≥100K views/day *measured between S-11-03 and S-11-04*. It separates videos that are still accelerating from ones that already peaked.

## 1. Day-over-day: yesterday's 8 'new' channels and the key candidates

### Takeaway
**Still no channel meets the strict rule** (created ≤30 d AND ≥2 long >3 min with ≥1M) on S-11-04. **Day Zero cannot qualify any more.** It turns 30 days old at 2026-11-04 13:35 UTC, and its second long video gained only +5.9K in 17 h (376K). The only long-form channel that has the strict-rule numbers is **Nobody Gets In** (2 long ≥1M: 3.28M and 1.86M), but it was created on 2026-10-01, so it is 33.7 d old and outside the window. It was not in yesterday's dataset at all.

### Cited Findings — channel level (OBSERVED, S-11-03 → S-11-04)
| Channel | age d (11-04) | subs 11-03 → 11-04 | Δ subs | videos 11-03 → 11-04 | new uploads since 11-03 19:00Z | views gained by tracked videos (≈17 h) | long ≥1M / long ≥300K / Short ≥1M (11-04) | strict rule |
|---|---|---|---|---|---|---|---|---|
| [Day Zero](https://www.youtube.com/channel/UCU9XwWmgsDdGRHXjrE0ewmQ) | 29.9 | 13,900 → 14,000 | +100 (+0.7%) | 4 → 4 | 0 | 22,413 on 4 videos (gap 17.0 h) | 1 / 2 / 0 | no |
| [Banazen Craft](https://www.youtube.com/channel/UCK0DXOEQLQ_YkP2x1jddjsw) | 10.2 | 4,290 → 4,690 | +400 (+9.3%) | 3 → 3 | 0 | 62,052 on 3 videos (gap 17.0 h) | 0 / 1 / 0 | no |
| [Ziggy Blox](https://www.youtube.com/channel/UCVFgxz89Ond56851oZHAcrg) | 24.7 | 61,100 → 62,800 | +1,700 (+2.8%) | 84 → 87 | 3: [A Million Copper Golems Followed Me 💀](https://www.youtube.com/watch?v=ns-CNbBXl6Q) 2,101 at 1 h; [A Glow Squid Ate My Town’s Christmas Li…](https://www.youtube.com/watch?v=beuh7k0LMTo) 10,095 at 5 h; [I Owed the Tooth Fairy 1000 Teeth 😳](https://www.youtube.com/watch?v=zygXkQfL-S8) 249,856 at 16 h | 1,836,242 on 48 videos (gap 17.0 h) + 262,052 on new uploads | 0 / 0 / 9 | no |
| [Erzxck](https://www.youtube.com/channel/UCDCDdtu2ldfNCJJfrLEqRWw) | 22.5 | 17,300 → 17,700 | +400 (+2.3%) | 22 → 23 | 1: [Minecraft Verity Match The Dumpling Squ…](https://www.youtube.com/watch?v=WYyrLNe4eD8) 156,666 at 12 h | 439,781 on 22 videos (gap 17.0 h) + 156,666 on new uploads | 0 / 0 / 4 | no |
| [CHIRAG FACTO](https://www.youtube.com/channel/UC8Cp4n7CJBoY4sMOWdTSAGA) | 12.0 | 26,000 → 26,200 | +200 (+0.8%) | 10 → 10 | 0 | 166,216 on 10 videos (gap 17.0 h) | 0 / 0 / 3 | no |
| [Verity Verifies MC](https://www.youtube.com/channel/UCCQaqq9L_IaPw3FyLW1Rn5A) | 9.7 | 1,790 → 1,890 | +100 (+5.6%) | 19 → 19 | 0 | 283,496 on 19 videos (gap 17.0 h) | 0 / 0 / 2 | no |
| [Mochi & Pals](https://www.youtube.com/channel/UC8BAM9FulzAucO3ENpk-yqA) | 20.5 | 1,060 → 1,150 | +90 (+8.5%) | 6 → 8 | 2: [Who wins the Minecraft swim race?](https://www.youtube.com/watch?v=iaS65SNrx3g) 39,035 at 14 h; [Who Wins the Minecraft Games?](https://www.youtube.com/watch?v=Aw0Nb1oX4kM) 228 at 15 h | 131,883 on 6 videos (gap 17.0 h) + 39,263 on new uploads | 0 / 0 / 1 | no |
| [SlivaCraft](https://www.youtube.com/channel/UC9rNiDYJAsDRbYuQO2wvihQ) | 30.2 | 1,780 → 1,830 | +50 (+2.8%) | 9 → 9 | 0 | 90,991 on 9 videos (gap 17.0 h) | 0 / 0 / 1 | no (age 30.2 d > 30) |
| [Kit vs The End](https://www.youtube.com/channel/UCND-rtZrbxwcyz4qA5Bppkg) | 38.0 | 9,730 → 10,200 | +470 (+4.8%) | 23 → 23 | 0 | 62,628 on 23 videos (gap 17.0 h) | 0 / 1 / 0 | no (age 38.0 d > 30) |
| [SirCloaked](https://www.youtube.com/channel/UC6KHf_WmgxTGKBAGckDUHHw) | 346.7 | 141,000 → 141,000 | +0 (+0.0%) | 169 → 169 | 0 | 27,347 on 50 videos (gap 17.0 h) | 2 / 12 / 1 | no (age 346.7 d > 30) |
| [Nobody Gets In](https://www.youtube.com/channel/UCZDmrAO-bnBxU4_LiH40CjA) | 33.7 | not in 11-03 data → 58,100 | not measured | — → 26 | n/a | not measured (first seen 11-04) | 2 / 5 / 0 | no (age 33.7 d > 30) |
| [Manic Craft](https://www.youtube.com/channel/UCCqUgUPWNhUzrmGE1r4p2kA) | 39.8 | not in 11-03 data → 66,100 | not measured | — → 101 | n/a | not measured (first seen 11-04) | 0 / 0 / 7 | no (age 39.8 d > 30) |
| [Henreee](https://www.youtube.com/channel/UCIYo_L-ZTXTMYUGe3Id9sGw) | 84.6 | not in 11-03 data → 82,000 | not measured | — → 218 | n/a | not measured (first seen 11-04) | 0 / 0 / 3 | no (age 84.6 d > 30) |

### Cited Findings — key videos (OBSERVED, S-11-03 19:0x UTC → S-11-04 12:0x UTC, gap 17.0 h)
| Channel | Video | Dur | Views 11-03 19:0xZ | Views 11-04 12:0xZ | Δ | Δ/day (24 h-equiv.) | lifetime views/day | note |
|---|---|---|---|---|---|---|---|---|
| Day Zero | [I Survived 100 Days in a REALISTIC APOCALYPSE in …](https://www.youtube.com/watch?v=crnpqkov3ps) | 52:00 | 1,894,197 | 1,910,705 | +16,508 | 23,325 | 69,069 | long |
| Day Zero | [I Survived 100 Days in a DEADLY OUTBREAK in Minec…](https://www.youtube.com/watch?v=eAqPRLb9JQg) | 40:30 | 370,330 | 376,184 | +5,854 | 8,266 | 31,960 | long |
| Day Zero | [Finding A Pistol in a Minecraft Apocalypse](https://www.youtube.com/watch?v=OKubhdelP8w) | 0:29 | 9,527 | 9,552 | +25 | 35 | 435 | Short |
| Banazen Craft | [JJ and Mikey Grow SECRET VERITY from Seeds in Min…](https://www.youtube.com/watch?v=uah6ikSydJ8) | 15:15 | 394,077 | 440,554 | +46,477 | 65,550 | 148,877 | long |
| Banazen Craft | [Only JJ Can SAVE His Friends from the GRAVE in Mi…](https://www.youtube.com/watch?v=IB4kSXJ1FrY) | 11:52 | 110,367 | 121,489 | +11,122 | 15,703 | 20,387 | long |
| Banazen Craft | [JJ and Mikey Survive as CHICKENS on ONE BLOCK in …](https://www.youtube.com/watch?v=zDBK1FX65jM) | 12:15 | 59,946 | 64,399 | +4,453 | 6,287 | 7,206 | long |
| Ziggy Blox | [I Fooled a Million Zombies 😱](https://www.youtube.com/watch?v=vH0pd4SomN8) | 2:21 | 9,357,584 | 9,370,852 | +13,268 | 18,734 | 669,301 | Short |
| Ziggy Blox | [I Pretended to Be a Mummy in a Real Pyramid 😳🐪](https://www.youtube.com/watch?v=1K1oIJp0yEg) | 2:15 | 3,236,484 | 3,255,014 | +18,530 | 26,164 | 234,051 | Short |
| Ziggy Blox | [I Crashed the Biggest Skeleton Party Ever 🦴](https://www.youtube.com/watch?v=VU6eTOdYz1w) | 2:29 | 2,437,392 | 2,526,246 | +88,854 | 125,459 | 315,325 | Short |
| Ziggy Blox | [I Fooled Herobrine’s Whole Army 😈](https://www.youtube.com/watch?v=bbj2gv4ZN4s) | 2:24 | 2,415,112 | 2,501,388 | +86,276 | 121,819 | 181,084 | Short |
| Erzxck | [Minecraft Verity Match The Block Game 🟡#minecraft…](https://www.youtube.com/watch?v=31tzZ_Y3n4c) | 1:15 | 12,072,020 | 12,310,439 | +238,419 | 336,559 | 984,230 | Short |
| Erzxck | [Minecraft Verity Plays Match The Block #minecraft…](https://www.youtube.com/watch?v=c4KIHOaQaOY) | 1:41 | 2,561,686 | 2,567,380 | +5,694 | 8,039 | 176,443 | Short |
| Erzxck | [Minecraft Verity Match The Block With Friends 🟢 #…](https://www.youtube.com/watch?v=967RWA-E0m4) | 1:26 | 1,059,760 | 1,063,704 | +3,944 | 5,568 | 112,287 | Short |
| CHIRAG FACTO | [Slither Run with Steve - Funny Animation](https://www.youtube.com/watch?v=xel-UZ5bf1s) | 0:35 | 2,623,353 | 2,659,488 | +36,135 | 50,957 | 915,610 | Short |
| CHIRAG FACTO | [Can Steve Win Memory Competition?!- Funny Animati…](https://www.youtube.com/watch?v=ckXQhXq8OPA) | 1:00 | 2,352,888 | 2,355,356 | +2,468 | 3,484 | 199,488 | Short |
| CHIRAG FACTO | [Double Slither Run with Steve and Alex - Funny An…](https://www.youtube.com/watch?v=-tXgpPl45B4) | 0:32 | 1,751,593 | 1,813,383 | +61,790 | 87,237 | 163,236 | Short |
| Verity Verifies MC | [How To Breed Horses Perfectly... #shorts](https://www.youtube.com/watch?v=K7xFyRmxoB0) | 0:53 | 1,669,935 | 1,849,189 | +179,254 | 253,077 | 357,852 | Short |
| Verity Verifies MC | [How To Use Copper Golems Perfectly... #shorts](https://www.youtube.com/watch?v=3U2_rB7SrZ0) | 0:49 | 1,350,457 | 1,417,644 | +67,187 | 94,755 | 230,676 | Short |
| Verity Verifies MC | [How To Store XP Perfectly... #shorts](https://www.youtube.com/watch?v=wFdwngDvbTQ) | 0:46 | 275,592 | 284,840 | +9,248 | 13,057 | 58,416 | Short |
| Mochi & Pals | [Who can dig down the fastest?](https://www.youtube.com/watch?v=nf9oZPSqhjE) | 0:16 | 1,424,438 | 1,474,014 | +49,576 | 69,912 | 497,194 | Short |
| Mochi & Pals | [Never let Bubbles build the bridge!](https://www.youtube.com/watch?v=AA7D_Imey0U) | 0:15 | 287,442 | 339,102 | +51,660 | 72,934 | 60,304 | Short |
| Mochi & Pals | [Who can build the tallest tower?](https://www.youtube.com/watch?v=F5tAxrMJAb8) | 0:17 | 223,441 | 245,303 | +21,862 | 30,865 | 153,409 | Short |
| SlivaCraft | [Minecraft Mystery Transformation part 4 #minecraf…](https://www.youtube.com/watch?v=Men-1Ggv3ms) | 0:41 | 1,331,193 | 1,410,841 | +79,648 | 112,461 | 76,776 | Short |
| SlivaCraft | [Minecraft Mystery Transformation part 5 #minecraf…](https://www.youtube.com/watch?v=xsA6WWceY5E) | 0:28 | 279,269 | 282,646 | +3,377 | 4,768 | 18,382 | Short |
| SlivaCraft | [Minecraft Mystery Transformation part 7 #minecraf…](https://www.youtube.com/watch?v=x5vnHO7Uay0) | 0:29 | 150,394 | 151,424 | +1,030 | 1,454 | 16,150 | Short |
| Kit vs The End | [Zombie Outbreak: 100 Days Trapped On A Zombie Cru…](https://www.youtube.com/watch?v=xdj5PL0t61k) | 1:13:02 | 672,849 | 714,784 | +41,935 | 59,211 | 66,662 | long |
| Kit vs The End | [Zombie Outbreak: Hundreds Of Zombies Pull The Anc…](https://www.youtube.com/watch?v=AmhWM6Gdmow) | 10:42 | 72,759 | 77,222 | +4,463 | 6,314 | 6,548 | long |
| Kit vs The End | [Zombie Outbreak: Ep. 1 [Day 14/100] Surviving A Z…](https://www.youtube.com/watch?v=6ftMiYTz5Bs) | 9:15 | 45,799 | 46,006 | +207 | 293 | 2,230 | long |
| SirCloaked | [Minecraft's NEW Verity Mod VS Falsity...](https://www.youtube.com/watch?v=QB8avpNjq4Y) | 10:21 | 2,469,780 | 2,469,979 | +199 | 281 | 18,571 | long |
| SirCloaked | [Something Is Wrong With My Farm...](https://www.youtube.com/watch?v=EYyB2uwb9o0) | 16:18 | 1,205,547 | 1,207,508 | +1,961 | 2,776 | 52,595 | long |
| SirCloaked | [Full video 😳⬇️](https://www.youtube.com/watch?v=pMwHgAWL12s) | 0:16 | 1,019,282 | 1,019,490 | +208 | 294 | 11,208 | Short |

- **Day Zero**: no new upload since 2026-10-23 (4 videos). Created 2026-10-05T13:35:17Z, so it reaches 30.0 d at 2026-11-04T13:35Z, about 1.5 h after S-11-04 (OBSERVED created date, arithmetic). The second long video "I Survived 100 Days in a DEADLY OUTBREAK in Minecraft" needs +623,816 views for 1M. At the measured 8.3K/day that would take about 75 days (INFERRED, constant rate; real decay is slower to reach). **Final 0–30 d result: 1 long ≥1M + 1 long 376K. It does not qualify.**
- **Banazen Craft**: best long 440,554 at 3.0 d. Its current pace is 65.6K/day, against 148.9K/day lifetime, so it is decelerating (OBSERVED). Its window closes 2026-11-24T06:56Z (created 2026-10-25T06:56Z). At the current rate the best video would reach 1M in about 8.5 d (INFERRED, constant rate, optimistic given the deceleration). It also needs a *second* long ≥1M, and its other long videos are at 121K and 64K. So it qualifies only if a new upload breaks out (INFERRED: possible but unlikely). Its 3-day upload slot (13:00 UTC) on 11-04 falls after S-11-04, so no upload has been seen since 11-01.
- **Ziggy Blox**: 9 videos ≥1M now (6 on S-11-03). The three new ones are "I Wore a Crocodile Costume Into a Real Croc River" (752K → 1.07M), "I Got Locked in the World's Biggest Mall" (985K → 1.02M) and "I Pretended to Be a Monster at Monster School" (1.68M, seen only today through search). Every upload is 1:45–2:39 long, so **0 count as long under the >3 min rule**: Ziggy Blox structurally cannot meet the strict rule with this format (OBSERVED durations).
- **Erzxck**: 4 Shorts ≥1M. "Minecraft Verity Matches The Squishy With Freddy" crossed 1M (994K → 1.05M). The 12.31M Short still gained +238K in 17 h (OBSERVED).
- **CHIRAG FACTO**: the fastest new-channel Short of 11-03 ("Slither Run with Steve", 916K/day lifetime) is now growing at only 51K/day, a 0.05 deceleration ratio in `resnapshot_24h.csv`. No upload since 11-02 (OBSERVED).
- **Mochi & Pals**: subs 1,060 → 1,150, with 2 new uploads. Its 2-day-old Short "Never let Bubbles build the bridge!" grew +51.7K, *faster* than its lifetime average (72.9K/day vs 60.3K/day) (OBSERVED).
- **SlivaCraft**: it is now 30.2 d old, so it has left the window. Its part-4 Short is re-accelerating at 18 d: +79.6K in 17 h = 112K/day against a 77K/day lifetime average (OBSERVED).
- **Kit vs The End** (38 d): its "Full Movie" holds 89% of its lifetime pace (59K/day). At that pace it passes 1M in about 4.8 d (INFERRED), but the channel is 38 d old.
- **SirCloaked** (346.7 d): it already has 2 long ≥1M. A third, "Something On My Farm Wants Me Dead..." (970,149 at 9.0 d), is gaining about 20K/day, so it should pass 1M in about 1.5 d (INFERRED).
- **Nobody Gets In / Manic Craft / Henreee**: first seen in S-11-04, so day-over-day change is **not measured**. Nobody Gets In's two 1M videos average 151.9K/day and 98.3K/day over their lifetimes. Each would probably have passed 1M while the channel was still ≤30 d old (around 2026-10-20 and 2026-10-27) (INFERRED from lifetime averages only, with no earlier snapshot). The 11-03 search simply did not surface the channel, which is a **search-coverage gap** (see §6).

### Inferences
- Among new channels, the long-form 1M+ path in this sample now runs mostly through **non-Minecraft stickman "Zombie Outbreak" survival stories** (Nobody Gets In, Beanie Survives, Kit vs The End) and Day Zero's Minecraft 100-days. The Minecraft-rendered new breakouts remain Shorts (INFERRED from the tags in §2).
- Several 11-03 "explosions" were short-lived (CHIRAG at 0.05× lifetime pace; Ziggy's 9.37M at 0.03×). Owner rule A's "exploding in the first 5 days" should be confirmed with a second snapshot (R3v) before a format is copied (INFERRED).

## 2. New 0–30-day channels found today (not on the 11-04 watchlist)

### Takeaway
45 channels ≤30 d not on the 11-04 watchlist; 15 with a ≥100K video (OBSERVED, S-11-04). **No strict qualifier.** None of these new channels has a long ≥1M or ≥2 long ≥300K. Two are **Shorts-only 1M+**: **Vexora Plays** (2.11M, third-party Poppy Playtime) and **Brawl Lab** (1.85M Mojang-only mob battle; 1.56M Sans). Below them, a cluster of 20–30-day **stickman zombie/apocalypse long-form** channels reached 211K–564K on 1.5K–9.6K subs (DoodleSurvivals 564K = 102× subs).

### Cited Findings (OBSERVED, S-11-04; views÷subs uses S-11-04 subs; views/day = views ÷ age)
| Channel | Created (API publishedAt) | Age d | Subs | Videos | Best videos (views · dur · ÷subs · views/day · age d) | IP / notes | seen 11-03? |
|---|---|---|---|---|---|---|---|
| [Vexora Plays](https://www.youtube.com/channel/UCZikV3UKwZZKoE0hG9YquPQ) | 2026-10-15 | 20.0 | 3,540 | 19 | [Correct Jump Challenge😱/ Poppy Playtime Chap…](https://www.youtube.com/watch?v=rYHwXTBGXfw) 2,112,670 · 0:23 · 597× · 125,963/d · 16.8<br>[Poppy Playtime Chapter 5 VS Kpop Demon Hunte…](https://www.youtube.com/watch?v=H61C-P3U-js) 907,037 · 0:23 · 256× · 51,037/d · 17.8<br>[Poppy Playtime Insane Challenge😱🌈 #minecraft…](https://www.youtube.com/watch?v=1U9IHzGMLTs) 719,803 · 0:20 · 203× · 48,727/d · 14.8 | third-party (Poppy Playtime, KPop Demon Hunters, GuguGaga, Squid Game) | no |
| [Brawl Lab](https://www.youtube.com/channel/UCoetJ6BMwV4gpCnW88fIEyw) | 2026-10-12 | 22.6 | 9,040 | 76 | [6 Overworld Mobs vs 6 Nether Mobs — Who Wins…](https://www.youtube.com/watch?v=tshtU9_yED8) 1,853,527 · 1:11 · 205× · 104,464/d · 17.7<br>[Sans Has 1 HP vs EVERY Minecraft Mob #minecr…](https://www.youtube.com/watch?v=dvKQhdDwbnU) 1,564,531 · 1:34 · 173× · 86,819/d · 18.0<br>[Undertale vs Deltarune — Which Team Wins? #u…](https://www.youtube.com/watch?v=5NRYR2elwEo) 577,899 · 2:03 · 64× · 42,214/d · 13.7 | third-party (Undertale/Deltarune: Sans, Asriel) + Mojang mobs | no |
| [Krowz](https://www.youtube.com/channel/UCHpY5_ZNDHNRb9B7oNOXk3A) | 2026-10-05 | 29.7 | 2,850 | 8 | [Jerry and Tom [LookOut3D] #animation #tom #j…](https://www.youtube.com/watch?v=LURUMIZvS3c) 657,729 · 0:18 · 231× · 28,878/d · 22.8 | third-party ("Jerry and Tom [LookOut3D]" dog characters; creator OCs) | no |
| [DoodleSurvivals](https://www.youtube.com/channel/UCXMvwFJxTp-fLF1k6qABrxg) | 2026-10-14 | 20.8 | 5,500 | 7 | [Zombie Outbreak Survival: Trapped In a Farm …](https://www.youtube.com/watch?v=9LVdlATk5Zw) 563,738 · 1:07:18 · 102× · 63,816/d · 8.8 | original story; likely not Minecraft-rendered (INFERRED: 1 of 7 videos tagged minecraft) | no |
| [Beanie Survives](https://www.youtube.com/channel/UCjp_7goy334-kGzkNsPT0TA) | 2026-10-05 | 30.0 | 9,590 | 11 | [Zombie Apartment Survival 1 Year](https://www.youtube.com/watch?v=TsADgaT6ucE) 513,056 · 17:29 · 53× · 21,545/d · 23.8<br>[Zombie Apartment Survival: Year 2 (Day 730)](https://www.youtube.com/watch?v=yQ54sjpgz4E) 123,524 · 18:33 · 13× · 5,701/d · 21.7 | original story, stickman (not Minecraft-rendered; tags); same name as the older Beanie Survives channel | no |
| [KiroByte09](https://www.youtube.com/channel/UC__B1flCFe1cGQsAei65TyA) | 2026-10-14 | 20.9 | 3,580 | 23 | [Baby Zombie Vs Bruce Lee 😂 #minecraft​ #shor…](https://www.youtube.com/watch?v=AQuHVYem2qo) 374,588 · 1:00 · 105× · 22,992/d · 16.3 | third-party (Hulk, Venom, Bruce Lee, Kaiju No. 8, KPop Demon Hunters) + baby zombie | no |
| [Stick Through Collapse](https://www.youtube.com/channel/UCX3TcmmJl1F5dWquW1-jVVQ) | 2026-10-10 | 25.1 | 6,020 | 6 | [Nuclear Apocalypse Survival: Day 1 to Day 30](https://www.youtube.com/watch?v=R88aTtJDDTs) 334,920 · 13:11 · 56× · 24,056/d · 13.9<br>[Every Man on Earth Disappeared Except You](https://www.youtube.com/watch?v=ty4NUYXz_7Y) 128,240 · 32:40 · 21× · 8,524/d · 15.0 | original, stickman/2D (INFERRED from name; no tags) | no |
| [Day by Day Stick](https://www.youtube.com/channel/UCy7Ke_F2ZANZpSwar-9ZGjw) | 2026-10-14 | 20.8 | 3,340 | 27 | [Zombie Apocalypse Survival: Day 1 to Day 365](https://www.youtube.com/watch?v=aAtF3xpttJA) 270,332 · 26:46 · 81× · 15,088/d · 17.9 | original, stickman (tags) | no |
| [BlockKahani](https://www.youtube.com/channel/UC4TX3h4QQgsCzndbYag6new) | 2026-10-24 | 11.2 | 2,280 | 13 | [🌕 Never Stay Awake After 9 PM… 😨 / Minecraft…](https://www.youtube.com/watch?v=a4YGrxjCvb0) 242,355 · 2:22 · 106× · 61,723/d · 3.9<br>[When the Bell Rings 3 Times, NEVER Stay Outs…](https://www.youtube.com/watch?v=5h8BUpXk3EU) 181,110 · 2:35 · 79× · 61,843/d · 2.9 | original horror stories, HINDI audio (excluded by English rule) | yes (in 11-03 dataset, not listed) |
| [DiaxGold Crafts](https://www.youtube.com/channel/UCoSfmCWZylAigXHdxEx_8Nw) | 2026-10-31 | 4.4 | 509 | 2 | [JJ & Zombie JJ Sister Guess what JJ reaction…](https://www.youtube.com/watch?v=zPOAXM3h9ZI) 221,288 · 0:16 · 435× · 98,295/d · 2.3<br>[JJ & Zombie JJ Sister Guess the reaction of …](https://www.youtube.com/watch?v=1zCAtiKQ1ys) 218,707 · 0:09 · 430× · 154,307/d · 1.4<br>[JJ & JJ Sister Change Outfits what is the Be…](https://www.youtube.com/watch?v=sgfIemKjUT4) 171,066 · 0:11 · 336× · 48,856/d · 3.5 | third-party (Maizen JJ & JJ Sister) | yes (in 11-03 dataset, not listed) |
| [HatchLog](https://www.youtube.com/channel/UCBEY78pD2v6cSR-goxjOxrQ) | 2026-10-07 | 27.9 | 1,490 | 13 | [Zombie Bunker Survival 1 Year](https://www.youtube.com/watch?v=EmBb2kPsvRM) 211,335 · 15:08 · 142× · 9,241/d · 22.9 | original bunker-survival story; not Minecraft-tagged | no |
| [BlaBlaEnding](https://www.youtube.com/channel/UC_XJZ649yTN6d3EOFXlw5Tw) | 2026-10-23 | 11.8 | 255 | 7 | [Gugugaga Penguin Build Battle Jump Challenge…](https://www.youtube.com/watch?v=M5yzWexdVtA) 143,493 · 0:46 · 563× · 17,954/d · 8.0 | third-party (Gugugaga, Mommy Long Legs, Verity, other mascots) | yes (in 11-03 dataset, not listed) |
| [Clent](https://www.youtube.com/channel/UC-VXED8sa0IM8jGAUndHo2g) | 2026-10-14 | 20.9 | 386 | 9 | [He Ran Through a Desert to Save This Snowbal…](https://www.youtube.com/watch?v=kBi0qF4-AY4) 135,231 · 0:11 · 350× · 7,448/d · 18.2 | original / Mojang-only (golems, Steve), wordless | yes (in 11-03 dataset, not listed) |
| [Huda Plaze](https://www.youtube.com/channel/UCmboscEb8DjnofADu0cUQHg) | 2026-10-05 | 29.9 | 6,050 | 224 | [My Friend Knows Exactly How to Handle It!😎🔥 …](https://www.youtube.com/watch?v=Cyf-Sl2g9qo) 116,365 · 0:28 · 19× · 64,952/d · 1.8<br>[#minecraft #minecraftanimation  #youtubeshor…](https://www.youtube.com/watch?v=gCyDTr9WDt4) 106,487 · 0:20 · 18× · 39,536/d · 2.7 | mixed (emotional family Shorts + JJ vs Mikey) | yes (in 11-03 dataset, not listed) |
| [mochi64](https://www.youtube.com/channel/UCsPUKvWnyv3uOrFVtI353tA) | 2026-10-08 | 26.7 | 5,900 | 261 | [I Tested 2 BLJ Myths in Mario 64 😳 #shorts #…](https://www.youtube.com/watch?v=efPRxz0uq0U) 108,476 · 0:10 · 18× · 5,912/d · 18.3 | off-niche (Super Mario 64 myths; Nintendo IP) | no |

- Closest-candidate tests (OWNER) applied to these 45 channels: ≥1 long 1M → 0; ≥2 long 300K+ → 0; Shorts-only 1M+ → 2 (Vexora Plays, Brawl Lab) (OBSERVED).
- 7 other ≤30 d channels in S-11-04 are already on the watchlist (Day Zero, Banazen Craft, Ziggy Blox, Erzxck, CHIRAG FACTO, Verity Verifies MC, Mochi & Pals). SlivaCraft (30.2 d) has just aged out (OBSERVED).
- **Two channels are both named "Beanie Survives".** UCjp_7goy334-kGzkNsPT0TA (@beaniesurvives1, created 2026-10-05, 9.59K subs) and the older UCGj5HppBXUUFZ7CoyNUNu2Q (@beaniesurvives, 107K subs, below). Kit vs The End tags 7 of its videos "beanie survives" (OBSERVED tags). INFERRED: a copycat/name-borrowing ecosystem around one breakout.

### Wider net — key candidates older than 30 d (OBSERVED, S-11-04)
| Channel | Created | Age d | Subs | Videos | First upload in sample | Best videos (views · dur · ÷subs · views/day · age d) |
|---|---|---|---|---|---|---|
| [Nobody Gets In](https://www.youtube.com/channel/UCZDmrAO-bnBxU4_LiH40CjA) | 2026-10-01 | 33.7 | 58,100 | 26 | 2026-10-13 (n=26) | [Zombie Outbreak: 30 Days Locked Inside a Sup…](https://www.youtube.com/watch?v=oXj7bWgRX_I) 3,279,978 · 10:41 · 56× · 151,885/d · 21.6<br>[Zombie Outbreak: 30 Days Locked Inside a Sch…](https://www.youtube.com/watch?v=2XYr2AEHDGI) 1,855,441 · 8:57 · 32× · 98,264/d · 18.9<br>[Zombie Outbreak: 60 Days Locked Inside a Sup…](https://www.youtube.com/watch?v=3N7ScfT7hn0) 527,572 · 8:11 · 9.1× · 35,311/d · 14.9 |
| [Beanie Survives (@beaniesurvives)](https://www.youtube.com/channel/UCGj5HppBXUUFZ7CoyNUNu2Q) | 2026-02-16 | 260.5 | 107,000 | 24 | 2026-10-11 (n=24) | [Zombie Outbreak: 30 Days Trapped On The 30th…](https://www.youtube.com/watch?v=1AF04-V4Yao) 2,853,150 · 8:12 · 27× · 118,879/d · 24.0<br>[Trapped On The Roof Until Day 60 / Zombie Ou…](https://www.youtube.com/watch?v=p9iPPGrn86o) 1,102,313 · 7:41 · 10× · 48,009/d · 23.0<br>[Zombie Outbreak Ep. 3: Leaving The Tower On …](https://www.youtube.com/watch?v=LmM7TLWBWok) 869,388 · 10:03 · 8.1× · 40,048/d · 21.7 |
| [SirCloaked](https://www.youtube.com/channel/UC6KHf_WmgxTGKBAGckDUHHw) | 2025-11-22 | 346.7 | 141,000 | 169 | 2026-06-21 (n=50) | [Minecraft's NEW Verity Mod VS Falsity...](https://www.youtube.com/watch?v=QB8avpNjq4Y) 2,469,979 · 10:21 · 18× · 18,571/d · 133.0<br>[Something Is Wrong With My Farm...](https://www.youtube.com/watch?v=EYyB2uwb9o0) 1,207,508 · 16:18 · 8.6× · 52,595/d · 23.0<br>[Full video 😳⬇️](https://www.youtube.com/watch?v=pMwHgAWL12s) 1,019,490 · 0:16 · 7.2× · 11,208/d · 91.0 |
| [Manic Craft](https://www.youtube.com/channel/UCCqUgUPWNhUzrmGE1r4p2kA) | 2026-09-25 | 39.8 | 66,100 | 101 | 2026-10-06 (n=58) | [Dog Jerry And Tom Sing Together Minecraft An…](https://www.youtube.com/watch?v=vmIQJJXOaFU) 5,667,266 · 0:18 · 86× · 195,420/d · 29.0<br>[Jerry Dog And Tom Dog Hug Each Other Minecra…](https://www.youtube.com/watch?v=3NrPPD_IEdg) 5,292,214 · 0:17 · 80× · 203,544/d · 26.0<br>[Jerry Dog Sneaks Up On Tom Dog Minecraft Ani…](https://www.youtube.com/watch?v=pEYE9hGLFlM) 2,552,421 · 0:14 · 39× · 94,532/d · 27.0 |
| [Henreee](https://www.youtube.com/channel/UCIYo_L-ZTXTMYUGe3Id9sGw) | 2026-08-11 | 84.6 | 82,000 | 218 | 2026-10-17 (n=59) | [Who Would Win? Sonic or Steve?](https://www.youtube.com/watch?v=WwFWcg4n-E4) 2,001,307 · 1:00 · 24× · 115,271/d · 17.4<br>[What Happens If You Name a Rabbit Toast in M…](https://www.youtube.com/watch?v=MMWDMuQ9HOo) 1,579,069 · 0:39 · 19× · 87,982/d · 17.9<br>[Who Would Win? Sonic or Pac-Man?](https://www.youtube.com/watch?v=rI4GYSgb9Ig) 1,246,414 · 0:55 · 15× · 81,396/d · 15.3 |

### Study of the million-view videos (metadata only: titles, durations, tags, publish times)
- **Nobody Gets In** (stickman 2D, 96% of videos tagged stickman; 0 Minecraft tags):
  - Title formula: "Zombie Outbreak: [30] Days Locked Inside a [everyday place]". The 1M+ places were Supermarket (3.28M) and School (1.86M). Prison, Mega Mall, Hospital, Treehouse, Zoo and Cruise Ship drew 65K–301K.
  - Length: 8:57–10:41.
  - Premise and cast: second-person "you" survival (tags "what would you do", "second person story", "survival scenario"). No named characters.
  - Rhythm: one long video a day, mostly 13:00–16:00 UTC. The two hits got escalating sequels (30 → 60 → 90 → 120 → 150 days, "Part N"), which decayed per part: Supermarket 3.28M → 528K → 238K → 144K → 91K; School 1.86M → 495K → 278K → 154K. Its first day also had 2-min "Part 1/2/3" cut-downs (6K–13K).
  - Engagement on the 3.28M video: 0.66% likes, 1.8 comments per 10K views.
- **Beanie Survives (@beaniesurvives)** (stickman; created 2026-02-16 but first upload 2026-10-11):
  - Its first long video is its biggest: "Zombie Outbreak: 30 Days Trapped On The 30th Floor" (8:12, 2.85M).
  - Then come episodes with a day stamp: "Trapped On The Roof Until Day 60 | Zombie Outbreak Ep. 2" (7:41, 1.10M), "Ep. 3: Leaving The Tower On Day 90" (869K), "Ep. 5: You Got Them Out (Day 121)" (523K).
  - The 2–2.5 min vertical "Part 2–6" cut-downs got 21K–70K, so they did not carry the views.
  - Rhythm: 7 uploads on 10-12, then about 1 long a day at 13:00–18:00 UTC.
- **SirCloaked** (Minecraft horror ARG/mod stories):
  - Ellipsis titles: "Minecraft's NEW Verity Mod VS Falsity..." (10:21, 2.47M, 2026-06-24, third-party mod entity). Then a farm arc with escalating sequels: "Something Is Wrong With My Farm..." (16:18, 1.21M) → "Something On My Farm Wants Me Dead..." (18:34, 970K at 9 d).
  - "(FULL MOVIE)" recuts run 48–62 min (426K–829K).
  - Each long video goes up at 13:00 UTC with a "Full video 😳⬇️" teaser Short a few minutes apart.
  - Engagement on the long videos: 590–1,190 comments (6.6 per 10K views on the top video).
- **Vexora Plays**: "Correct Jump Challenge😱| Poppy Playtime Chapter 5🏆 #poppyplaytime #minecraft." (0:23, 2.11M). Mascot obstacle-challenge Shorts, 1 a day at 17:30 UTC. Engagement is low (0.57% likes, 16 comments).
- **Brawl Lab**: "6 Overworld Mobs vs 6 Nether Mobs — Who Wins?" (1:11, 1.85M, Mojang-only) and "Sans Has 1 HP vs EVERY Minecraft Mob" (1:34, 1.56M). The formula is "X vs EVERY Minecraft Mob" or "Team vs Team — Who Wins?", at about 3 Shorts a day, with 1.6% likes and 202–528 comments. Its 4 long compilations/tournaments (3.5–10 min) got ≤8.3K (OBSERVED).
- **Manic Craft** (39.8 d): every 1M+ Short (7–28 s, up to 5.67M) stars "Jerry Dog / Tom Dog / Lookout" (#lookout3d), which is third-party IP. Titles end "#minecraft #lookout3d #usa". It now posts 6 Shorts a day.

### Inferences
- The long-form 1M+ "new channel" signal this week is a **cross-platform story format** rather than a Minecraft format: day-counter survival in one confined, everyday place, told to "you", 8–11 min, one per day. The *first* episode decides the channel's ceiling, and sequels decay about 2–6× per part (INFERRED from the two channels above).
- Brawl Lab shows that the "who wins vs every mob" Short reaches 1.85M **without** borrowed characters (INFERRED: the Mojang-only video beat the Sans one).

### Gaps
- No descriptions or thumbnails are in the CSVs (the raw JSON stays on the PC), so hooks are inferred from titles only. Visual style (stickman vs Minecraft) is inferred from tags.
- Under CLAUDE.md, any "we learned acting/editing/visual X from competitor Y" claim still needs the competitor full-viewing gate. This note covers metadata only.

## 3. Old-competitor outliers today (all 32 watchlist channels; yesterday's 'new' now 'old')

### Takeaway
1046 videos on 32 watchlist channels; 144 English videos meet ≥1 rule (96 of them ≤30 d old; 21 long); channels with a hit: 25 (OBSERVED, S-11-04).
- **Strongest long-form outliers ≤30 d:**
  - Spoke "COLD WAR" (13.73M, 3.9× median, still +505K/day).
  - Kit vs The End "Full Movie" (715K, 34× median, 70× subs).
  - Mine Block "JJ Became Spider-Man" (3.52M, 31× subs).
  - Cubeee's 54-min compilation (2.37M, 47× subs, +248K/day).
  - Day Zero (1.91M, 136× subs).
  - DL Minecraft "Steve and Alex rescuing a Baby Villager … Pizza" (511K = 190× subs, 75× median). This is the closest original-style analog to baby zombie Zu.
- **New velocity outliers caught only by R3v:**
  - MSToons "YOU Trolled JJ and Mikey with Infinite Hearts!" (1.42M at 1.8 d, +394K in 17 h).
  - Wablo "There is an imposter in my house" (1.31M at 1.5 d, +472K in 17 h).
  - Bench Animation's "Evil JJ" arc.
- **Watchlist channels with no rule hit today:** BigSchool, Maizen, GameToons, MyMy toon, ZomBo, Class Monster School, JJ Cartoons.

### Cited Findings — long-form (>3 min) videos ≤30 d meeting ≥1 rule (OBSERVED, S-11-04; "last ≈17 h" = S-11-03 → S-11-04 delta scaled to 24 h)
| Channel (subs 11-04) | Video | Age d | Dur | Views 11-04 | ÷subs | × same-format median | lifetime views/day | last ≈17 h (24 h-equiv./day) | Rules |
|---|---|---|---|---|---|---|---|---|---|
| Spoke (2,910,000) | [10,000 Players Simulate COLD WAR in Minecraft](https://www.youtube.com/watch?v=y5IdSoHdkgg) | 12.5 | 3:59:41 | 13,731,436 | 4.7× | 3.9× | 1,098,679 | 505,064 | R2 |
| Mine Block (115,000) | [JJ Became Spider-Man, JJ Sister Spider-Girl?!- Mi…](https://www.youtube.com/watch?v=RjyeHZ5hSaE) | 26.1 | 26:01 | 3,517,540 | 31× | 3.1× | 134,856 | no 11-03 value | R1 |
| Cubeee Animations (50,700) | [MAIZEN : ALL EPISODE JJ Sister LOVES JJ - Minecra…](https://www.youtube.com/watch?v=g-GgM-kVnNs) | 7.8 | 54:29 | 2,371,984 | 47× | 1.1× | 305,228 | 248,269 | R1 |
| Day Zero (14,000) | [I Survived 100 Days in a REALISTIC APOCALYPSE in …](https://www.youtube.com/watch?v=crnpqkov3ps) | 27.7 | 52:00 | 1,910,705 | 136× | 1.7× | 69,069 | 23,325 | R1 |
| Морфиз (73,900) | [MAIZEN: JJ and Love JJ Sister POLICE Love Story -…](https://www.youtube.com/watch?v=ekwQBMtUNPM) | 21.1 | 12:57 | 1,619,860 | 22× | 6.4× | 76,677 | no 11-03 value | R1 |
| MSToons (1,770,000) | [JJ BUS EATER was Buried Under The Water - Maizen …](https://www.youtube.com/watch?v=Lnl-4FT77Ws) | 3.8 | 13:10 | 1,513,667 | 0.9× | 0.8× | 394,808 | 201,703 | R3v |
| MSToons (1,770,000) | [YOU Trolled JJ and Mikey with Infinite Hearts! - …](https://www.youtube.com/watch?v=FSCGy0YaUaE) | 1.8 | 10:16 | 1,417,158 | 0.8× | 0.8× | 772,795 | 555,877 | R3v |
| Cody Toon (43,800) | [JJ and Mikey survival in DOUBLE PITS WITH ALL VER…](https://www.youtube.com/watch?v=IYaWLDQnyZ4) | 25.0 | 10:33 | 1,272,861 | 29× | 4.3× | 50,998 | 14,058 | R1 |
| MineBraintor ⚠suspect (1,860) | [Minecraft TNT Blast IN VILLAGE](https://www.youtube.com/watch?v=IdwH1fbtOkc) | 6.6 | 1:24:34 | 982,326 | 528× | 814× | 148,685 | 4 | R1 R2 |
| Chase Liminal (16,700) | [Poolrooms - Mini Golf (Backrooms)](https://www.youtube.com/watch?v=4UgGJkBi6UM) | 27.0 | 5:16 | 930,127 | 56× | 1.6× | 34,448 | 12,453 | R1 |
| Морфиз (73,900) | [MAIZEN: JJ Got a GIRLFRIEND - Minecraft Animation…](https://www.youtube.com/watch?v=79egDYFvxtY) | 28.1 | 12:50 | 860,337 | 12× | 3.4× | 30,589 | no 11-03 value | R1 |
| Ligabka (69,400) | [MAIZEN - JJ and LOVE QUEEN - ❤️ LOVE STORY !? 💕 -…](https://www.youtube.com/watch?v=10vzXGySExY) | 5.0 | 8:06 | 812,876 | 12× | 1.7× | 161,209 | 122,584 | R1 |
| Cody Toon (43,800) | [JJ and Mikey inside PITS WITH JERRY DOG & ALL VER…](https://www.youtube.com/watch?v=QcKXl5iYuTY) | 18.0 | 9:54 | 736,354 | 17× | 2.5× | 41,002 | 27,763 | R1 |
| Kit vs The End (10,200) | [Zombie Outbreak: 100 Days Trapped On A Zombie Cru…](https://www.youtube.com/watch?v=xdj5PL0t61k) | 10.7 | 1:13:02 | 714,784 | 70× | 34× | 66,662 | 59,211 | R1 R2 |
| Cody Toon (43,800) | [JJ and Mikey in ALL LOVE STORY PIT LORD VERITY & …](https://www.youtube.com/watch?v=8zrl4YNyPA4) | 7.0 | 11:08 | 670,653 | 15× | 2.3× | 96,370 | 41,530 | R1 |
| Cody Toon (43,800) | [JJ and Mikey survival in ALL DOORS WITH ALL VERIT…](https://www.youtube.com/watch?v=lj50e066xB4) | 11.0 | 10:08 | 633,776 | 14× | 2.2× | 57,830 | 25,126 | R1 |
| MineBraintor ⚠suspect (1,860) | [Minecraft TNT  Live](https://www.youtube.com/watch?v=E2Hf1pKCBMY) | 5.7 | 56:52 | 604,584 | 325× | 501× | 106,794 | 4 | R1 R2 |
| MineBraintor ⚠suspect (1,860) | [Minecraft TNT Blast Village Live 0004](https://www.youtube.com/watch?v=-pl0Xmo26Ik) | 6.2 | 1:22:16 | 547,647 | 294× | 454× | 87,648 | 0 | R1 R2 |
| MineBraintor ⚠suspect (1,860) | [Minecraft TNT Brainrots PVP Live 01](https://www.youtube.com/watch?v=Ol3mgOtNQww) | 3.1 | 38:51 | 516,013 | 277× | 427× | 166,341 | 6 | R1 R2 R3 |
| DL Minecraft (2,690) | [Steve and Alex rescuing a Baby Villager and Givin…](https://www.youtube.com/watch?v=tRXWDQFJ1Do) | 27.1 | 10:23 | 511,232 | 190× | 75× | 18,876 | no 11-03 value | R1 |
| Banazen Craft (4,690) | [JJ and Mikey Grow SECRET VERITY from Seeds in Min…](https://www.youtube.com/watch?v=uah6ikSydJ8) | 3.0 | 15:15 | 440,554 | 94× | 3.6× | 148,877 | 65,550 | R2 R3 |

### Cited Findings — Shorts ≤15 d meeting R2/R3/R3v with ≥1M views or ≥200K/day now (suspect channels excluded) (OBSERVED, S-11-04)
| Channel (subs 11-04) | Video | Age d | Dur | Views 11-04 | ÷subs | × same-format median | lifetime views/day | last ≈17 h (24 h-equiv./day) | Rules |
|---|---|---|---|---|---|---|---|---|---|
| Erzxck (17,700) | [Minecraft Verity Match The Block Game 🟡#minecraft…](https://www.youtube.com/watch?v=31tzZ_Y3n4c) | 12.5 | 1:15 | 12,310,439 | 696× | 250× | 984,230 | 336,559 | R1 R2 |
| Ziggy Blox (62,800) | [I Fooled a Million Zombies 😱](https://www.youtube.com/watch?v=vH0pd4SomN8) | 14.0 | 2:21 | 9,370,852 | 149× | 87× | 669,301 | 18,734 | R1 R2 |
| Wablo (257,000) | [There is an imposter outside my house](https://www.youtube.com/watch?v=d5lFbb4xDYk) | 13.5 | 0:36 | 6,798,673 | 26× | 3.5× | 502,027 | 151,850 | R1 R2 |
| Bench Animation (239,000) | [JJ Almost Lost His Little Sister… 😭 Minecraft Ani…](https://www.youtube.com/watch?v=9URFvxHG4Eo) | 13.7 | 1:25 | 5,060,668 | 21× | 7.0× | 370,424 | 23,352 | R1 R2 |
| Ziggy Blox (62,800) | [I Pretended to Be a Mummy in a Real Pyramid 😳🐪](https://www.youtube.com/watch?v=1K1oIJp0yEg) | 13.9 | 2:15 | 3,255,014 | 52× | 30× | 234,051 | 26,164 | R1 R2 |
| CHIRAG FACTO (26,200) | [Slither Run with Steve - Funny Animation](https://www.youtube.com/watch?v=xel-UZ5bf1s) | 2.9 | 0:35 | 2,659,488 | 102× | 13× | 915,610 | 50,957 | R1 R2 R3 |
| Erzxck (17,700) | [Minecraft Verity Plays Match The Block #minecraft…](https://www.youtube.com/watch?v=c4KIHOaQaOY) | 14.6 | 1:41 | 2,567,380 | 145× | 52× | 176,443 | 8,039 | R1 R2 |
| Ziggy Blox (62,800) | [I Crashed the Biggest Skeleton Party Ever 🦴](https://www.youtube.com/watch?v=VU6eTOdYz1w) | 8.0 | 2:29 | 2,526,246 | 40× | 23× | 315,325 | 125,459 | R1 R2 |
| Ziggy Blox (62,800) | [I Fooled Herobrine’s Whole Army 😈](https://www.youtube.com/watch?v=bbj2gv4ZN4s) | 13.8 | 2:24 | 2,501,388 | 40× | 23× | 181,084 | 121,819 | R1 R2 |
| CHIRAG FACTO (26,200) | [Can Steve Win Memory Competition?!- Funny Animati…](https://www.youtube.com/watch?v=ckXQhXq8OPA) | 11.8 | 1:00 | 2,355,356 | 90× | 11× | 199,488 | 3,484 | R1 R2 |
| Ziggy Blox (62,800) | [I Crashed a Vampire Wedding💀](https://www.youtube.com/watch?v=H2a_oD4SK58) | 10.0 | 2:23 | 2,097,490 | 33× | 19× | 209,952 | 2,293 | R1 R2 |
| Verity Verifies MC (1,890) | [How To Breed Horses Perfectly... #shorts](https://www.youtube.com/watch?v=K7xFyRmxoB0) | 5.2 | 0:53 | 1,849,189 | 978× | 74× | 357,852 | 253,077 | R1 R2 |
| CHIRAG FACTO (26,200) | [Double Slither Run with Steve and Alex - Funny An…](https://www.youtube.com/watch?v=-tXgpPl45B4) | 11.1 | 0:32 | 1,813,383 | 69× | 8.6× | 163,236 | 87,237 | R1 R2 |
| Gamity (1,580) | [Minecraft Moments That Got WORSE Every Second 💀😂 …](https://www.youtube.com/watch?v=lLy9Oiocb_c) | 9.9 | 1:33 | 1,783,689 | 1,129× | 87× | 180,609 | 77,091 | R1 R2 |
| Mochi & Pals (1,150) | [Who can dig down the fastest?](https://www.youtube.com/watch?v=nf9oZPSqhjE) | 3.0 | 0:16 | 1,474,014 | 1,282× | 27× | 497,194 | 69,912 | R1 R2 R3 |
| Verity Verifies MC (1,890) | [How To Use Copper Golems Perfectly... #shorts](https://www.youtube.com/watch?v=3U2_rB7SrZ0) | 6.1 | 0:49 | 1,417,644 | 750× | 57× | 230,676 | 94,755 | R1 R2 |
| Bench Animation (239,000) | [Evil JJ Could Only Save One… 😱 Minecraft Animatio…](https://www.youtube.com/watch?v=LE52kyfNQf4) | 3.7 | 1:14 | 1,385,012 | 5.8× | 1.9× | 375,187 | 161,531 | R3v |
| Wablo (257,000) | [There is an imposter in my house](https://www.youtube.com/watch?v=A7LCtpxbA-s) | 1.5 | 0:35 | 1,307,185 | 5.1× | 0.7× | 847,318 | 666,255 | R3v |
| Bench Animation (239,000) | [No One Celebrated Evil JJ… 😭 Minecraft Animation …](https://www.youtube.com/watch?v=bP56zLxtTns) | 4.7 | 1:22 | 1,253,369 | 5.2× | 1.7× | 267,595 | 157,377 | R3v |
| Ziggy Blox (62,800) | [I Snuck Into a World of Real Endermen 😳](https://www.youtube.com/watch?v=9mqoXWhu3oo) | 4.0 | 2:14 | 1,107,681 | 18× | 10× | 274,006 | 87,991 | R1 R2 R3 |
| Ziggy Blox (62,800) | [I Wore a Crocodile Costume Into a Real Croc River…](https://www.youtube.com/watch?v=ClQeDnXZPnQ) | 2.9 | 2:10 | 1,070,992 | 17× | 9.9× | 365,788 | 450,343 | R1 R2 R3 R3v |
| Erzxck (17,700) | [Minecraft Verity Match The Block With Friends 🟢 #…](https://www.youtube.com/watch?v=967RWA-E0m4) | 9.5 | 1:26 | 1,063,704 | 60× | 22× | 112,287 | 5,568 | R1 R2 |
| Erzxck (17,700) | [Minecraft Verity Matches The Squishy With Freddy …](https://www.youtube.com/watch?v=KUkGfN8btZk) | 5.6 | 1:14 | 1,050,102 | 59× | 21× | 188,313 | 78,629 | R1 R2 |
| Ziggy Blox (62,800) | [I Got Locked in the World’s Biggest Mall 😱](https://www.youtube.com/watch?v=PDmVNu7mjmE) | 6.0 | 1:45 | 1,023,658 | 16× | 9.5× | 169,988 | 54,783 | R1 R2 |
| Ziggy Blox (62,800) | [I Invited the Wither to My Birthday 💀](https://www.youtube.com/watch?v=bubLIQDm-MY) | 2.0 | 2:12 | 738,783 | 12× | 6.8× | 363,520 | 236,066 | R1 R2 R3 R3v |
| Ziggy Blox (62,800) | [I Worked in Santa's Workshop With a Million Elves…](https://www.youtube.com/watch?v=VBKEfmyQgeQ) | 1.9 | 2:16 | 580,464 | 9.2× | 5.4× | 301,091 | 267,446 | R2 R3 R3v |
| Ziggy Blox (62,800) | [I Hatched the Ender Dragon Egg 🥚](https://www.youtube.com/watch?v=PlgOyBdPZoc) | 2.2 | 2:15 | 391,838 | 6.2× | 3.6× | 179,062 | 247,404 | R2 R3 R3v |
| Ziggy Blox (62,800) | [I Snuck Into a School of Real Ninjas](https://www.youtube.com/watch?v=SXcg2as0C-8) | 1.2 | 2:08 | 385,062 | 6.1× | 3.6× | 321,176 | 274,322 | R2 R3 R3v |

- Full list (144 rows, incl. older R1 hits and suspect channels): `data/2026-11-04/derived_G_watchlist_outliers.csv`.
- Older (>30 d) R1-only hits by channel: Mine Block 11; Wablo 9; Cubeee Animations 6; EvanavE 6; Ligabka 5; Морфиз 4; Chase Liminal 3; imKaiL00L 3; Mikey & JJ Verse 1 (OBSERVED).
- **Near misses** (≤15 d, ≥3× same-format median, but <300K, so they miss R2 only on the floor) (OBSERVED, S-11-04):
- MineBraintor (⚠suspect): [Minecraft TNT Live BOOOM](https://www.youtube.com/watch?v=X9kgfK_sQTY) 100,634 at 5.5 d, 1:01:49, 83× same-format median, 54× subs
- MineBraintor (⚠suspect): [Minecraft TNT Zombie VS Villager PVP Live 02](https://www.youtube.com/watch?v=gwhW0gfk_Po) 91,598 at 2.2 d, 40:19, 76× same-format median, 49× subs
- DL Minecraft: [Baby Zombie Couldn’t Believe This Giant Pizza & Fried …](https://www.youtube.com/watch?v=xLlYCcahMPE) 204,365 at 8.1 d, 10:44, 30× same-format median, 76× subs
- Verity Verifies MC: [How To Store XP Perfectly... #shorts](https://www.youtube.com/watch?v=wFdwngDvbTQ) 284,840 at 4.9 d, 0:46, 11× same-format median, 151× subs
- DL Minecraft: [Baby Piglin Thought He Had Lost Everything… Until Stev…](https://www.youtube.com/watch?v=JVcApKT2YT4) 52,856 at 4.1 d, 8:46, 7.7× same-format median, 20× subs
- Chase Liminal: [Whispering Wyrm chases me in the Poolrooms](https://www.youtube.com/watch?v=wtQ8eBcD9PM) 177,339 at 11.8 d, 1:03, 6.5× same-format median, 11× subs
- Erzxck: [Minecraft Verity Match The Spooky Block 🎃 #minecraft #…](https://www.youtube.com/watch?v=Oob5CywvZPw) 297,719 at 4.5 d, 1:14, 6.0× same-format median, 17× subs
- Mochi & Pals: [Who can build the tallest tower?](https://www.youtube.com/watch?v=F5tAxrMJAb8) 245,303 at 1.6 d, 0:17, 4.5× same-format median, 213× subs
- Ligabka: [Bro Thinks He Strong ☠️](https://www.youtube.com/watch?v=wQErXdYQFDk) 190,145 at 11.9 d, 0:11, 3.9× same-format median, 2.7× subs
- Kit vs The End: [Zombie Outbreak: Hundreds Of Zombies Pull The Anchor O…](https://www.youtube.com/watch?v=AmhWM6Gdmow) 77,222 at 11.8 d, 10:42, 3.7× same-format median, 7.6× subs
- Verity Verifies MC: [Never Kill A Ghast With Your Bow #shorts](https://www.youtube.com/watch?v=d-YQcLAA1Gk) 90,337 at 7.5 d, 0:41, 3.6× same-format median, 48× subs
- JJ Cartoons: [Mikey & JJ Friends From POOR to RICH in Minecraft…Maiz…](https://www.youtube.com/watch?v=JqwECK8JIJU) 286,850 at 13.1 d, 22:40, 3.5× same-format median, 79× subs
- Ligabka: [Bro Thinks He Strong ☠️](https://www.youtube.com/watch?v=CgZ3GijQQdg) 165,094 at 9.9 d, 0:12, 3.4× same-format median, 2.4× subs
- Erzxck: [Minecraft Verity Match The Dumpling Squishy Block Game…](https://www.youtube.com/watch?v=WYyrLNe4eD8) 156,666 at 0.5 d, 1:18, 3.2× same-format median, 8.9× subs
- **Leaders just under the rules:**
  - Maizen "Zombie Outbreak" (28:30): 4,996,282 at 10.5 d = 2.48× long median (2.02M), +136K in 17 h. It also uses the "Zombie Outbreak" phrase (see §6).
  - Maizen "JJ Pretended to Be a BABY CAT on an OP One Chunk!": 2.12M at 4.3 d.
  - MSToons "JJ BUS EATER was Buried Under The Water": 1.51M at 3.8 d.
  - (OBSERVED)
- **Suspect channels confirmed** (OBSERVED, 17 h):
  - MineBraintor's 4 "live" long videos (516K–982K) gained **0–6 views each**, and its subs fell 1,870 → 1,860.
  - EvanavE's two 1.14M long VODs gained **0 views**, while its Shorts kept moving.
  - Treat both channels' long-form numbers as non-organic or frozen counters, not as a benchmark (INFERRED).
- **Corrections to the 11-03 watchlist** (OBSERVED, S-11-04 titles and language fields):
  - Морфиз has English/Latin titles and `en` audio on 22/22 videos (only its channel name is Cyrillic), so it **passes** the English rule. Its titles are Maizen fan IP.
  - Mine Block's titles are "MAIZEN: JJ … JJ Sister & Mikey" (audio `zxx`), so it is **third-party Maizen fan IP**, not "original-style".
  - MyMy toon now uses the Verity mod entity.
  - All of these are corrected in the CSV.

### Inferences
- Lifetime views/day overstates many 11-03 "explosions". Ranking by the 17 h delta puts **Wablo, MSToons, Ziggy Blox, Bench Animation and Spoke** on top as the channels still accelerating now. CHIRAG FACTO and the older Ziggy hits have flattened (INFERRED from the R3v column).
- Long-form outliers on small channels are again **compilations or Full Movies** (Cubeee 54 min, Kit 73 min) and **day-counter survival** (Day Zero, Kit). That matches yesterday's B §7 inference (INFERRED).

### Gaps
- Same-format medians use the last ≤50 uploads, which for Shorts-heavy channels can be under 2 weeks of history. For Mine Block, Морфиз, Cubeee and DL Minecraft there is no S-11-03 value, so their 17 h velocity is not measured.

## 4. Watchlist update

### Takeaway
The watchlist grows from 32 to **38 channels**. All 32 existing rows are now `old` (OWNER rule: once listed, a channel is an old competitor). The **6 additions** are `new` with first_seen 2026-11-04: Nobody Gets In, Beanie Survives (@beaniesurvives), SirCloaked, Manic Craft, Vexora Plays, Brawl Lab.

### Cited Findings
- `data/watchlist_2026-11-05.csv`: same 12 columns as `watchlist_2026-11-04.csv`, plus `last_checked` = 2026-11-04 and `subs_2026-11-04` (API, S-11-04). For old rows, `notes` = "[2026-11-04] today's finding || [2026-11-03] yesterday's note". For new rows, `age_days_at_2026-11-03` is computed from the created date (INFERRED arithmetic). The `ip_type` corrections for Mine Block, Морфиз and MyMy toon are applied (OBSERVED).
- `data/2026-11-04/watchlist_txt_proposed.txt`: 38 rows in the repo's 8-field `|` format. `config/research/minecraft_story_watchlist.txt` was **not** modified. Header lines state that `role` = `new` for rows added on that date and `leader` for rows already listed (tracked with the old-competitor rules), so yesterday's `new` rows now read `leader`. Handles and joined dates of the 13 original rows are kept from the current txt; the others use the API `customUrl` and `publishedAt`.
- Why each addition qualifies (OBSERVED, S-11-04):
  - Nobody Gets In: 2 long ≥1M, 33.7 d.
  - Beanie Survives: 2 long ≥1M within 24 d of its first upload.
  - SirCloaked: 2 long ≥1M, plus a third near 1M; it is the owner-flagged key candidate.
  - Manic Craft: 7 Shorts ≥1M at 39.8 d (flagged third-party).
  - Vexora Plays and Brawl Lab: ≤30 d, Shorts-only 1M+.
- **Considered, not added:**
  - Henreee (82K subs, 84.6 d): only 5 of 59 sampled titles are Minecraft. The rest are Sonic/Mario/Crash trivia Shorts, so it is off-niche. Its 2.00M "Who Would Win? Sonic or Steve?" is a format reference only.
  - DoodleSurvivals, Beanie Survives (@beaniesurvives1), Stick Through Collapse, Day by Day Stick, HatchLog: young long-form, but they do not meet the owner's closest-candidate tests. Watch them in the next scan.
  - Krowz, KiroByte09, DiaxGold Crafts, BlaBlaEnding: third-party IP, below 1M.
  - BlockKahani: Hindi.

### Inferences
- Three of the 6 additions are stickman non-Minecraft channels or third-party-IP Shorts. If the owner wants the list to stay Minecraft-rendered only, the stickman pair (Nobody Gets In, Beanie Survives) could move to a separate "adjacent format" list. That is the owner's call, not decided here (INFERRED / ask OWNER).

## 5. What Bin, Bo and baby zombie Zu can learn from each new competitor (formula only — no names, characters, skins, scripts or footage)

### Takeaway
The transferable formulas are:
- a day-counter survival episode set in **one confined, everyday place**, told in second person;
- the **sequel-title escalation** of a hit ("Something Is Wrong With …" → "… Wants Me Dead");
- the **same-minute teaser Short** pointing to the long video;
- the periodic **FULL MOVIE recut**;
- the Mojang-only **"vs every mob — who wins?"** Short.

All of these can be done with our own cast. The full-movie recut also raises approved finished minutes per week without new animation.

### Cited Findings (formula observed → our original adaptation, INFERRED; these are proposals for the showrunner, not decisions)
- **Nobody Gets In**. Observed: "Zombie Outbreak: 30 Days Locked Inside a Supermarket" (3.28M) / "… a School" (1.86M); 8–11 min, 1 a day, sequels decay from 3.28M to 91K by Part 5.
  - Adaptation: a Minecraft-rendered "30 Days Locked Inside a [supermarket / school]" in which Bin and Bo hide baby zombie Zu from a horde.
  - Lessons: pick the most *relatable* place first, since everyday places beat exotic ones in its data. Cap sequels at 1–2, then compile them into a full movie.
- **Beanie Survives**. Observed: the episode title carries the day stamp ("Ep. 2 … Until Day 60", "Ep. 5 … (Day 121)"). Its vertical cut-downs did not carry the views (21–70K vs 2.85M).
  - Adaptation: put the day number in the title of our survival lane.
  - Lessons: do not spend production time on chopped Parts as Shorts; make purpose-built Shorts instead (OBSERVED gap, INFERRED lesson).
- **SirCloaked**. Observed: ellipsis mystery titles, a sequel that escalates the threat, a "Full video ⬇️" teaser Short published within minutes of the long video, and 48–62 min FULL MOVIE recuts.
  - Adaptation: a kids-safe mystery arc ("Something Is Wrong With Zu…" → "Something Is Following Zu…"), each long video with a same-minute teaser Short, and a monthly full-movie recut.
  - This matches the owner's main lane (original horror-mystery universe) and second lane (Day 1 → Day 100 survival), as stated in their saved channel plan (OWNER, from memory).
- **Brawl Lab**. Observed: "6 Overworld Mobs vs 6 Nether Mobs — Who Wins?" (1.85M, Mojang-only).
  - Adaptation: Shorts in the style "Baby Zombie Zu vs Every Mob — Who Wins?" or "Bin's team vs Bo's team — Who Wins?" for the owner's Shorts test lane.
  - Lessons: its long compilations failed (≤8.3K), so keep this format as Shorts.
- **Vexora Plays**. Observed: a 20–30 s single-obstacle challenge with a visible pass/fail.
  - Adaptation: "Can Zu make the jump?" micro-challenges.
  - Lessons: do **not** use mascot IP (Poppy Playtime / KPop Demon Hunters) in titles or tags.
- **Manic Craft**. Observed: 7–28 s wordless emotional micro-moments between two pet characters (hug, sing, sneak up), with 1.8% likes on the top video.
  - Adaptation: Zu-and-a-pet-mob micro-moments. Do **not** use the Jerry/Tom "LookOut3D" dogs.
  - Its "#usa" title tag and 6 uploads a day are packaging tactics our policy-check would need to judge.
- **Wider stickman cluster** (DoodleSurvivals 67-min "Day 1 To Day 100 (Full Movie!)" 564K on 5.5K subs; Kit vs The End 73-min Full Movie 715K): even 20–40-day-old channels get their biggest long-form numbers from a **season compiled into one 60–75 min movie** (OBSERVED). For the KPI this is the cheapest source of approved minutes (INFERRED).

### Gaps
- None of this proves the formulas work in Minecraft rendering with our cast. The stickman channels' audience may differ (not measured). The first test should be one 8–11 min "30 Days Locked Inside …" Bin & Bo & Zu episode against the niche *median*, not the 3.28M best (CLAUDE.md research policy).

## 6. Short-term trend to log (for `reports/research/minecraft_story_principles.md`, not edited here)

- **"Zombie Outbreak:" day-counter survival titles** (short-term).
  - Start: earliest in today's pool 2026-10-06 (StickFallout). Breakouts: 2026-10-11 (Beanie Survives, 2.85M) and 2026-10-13 (Nobody Gets In, 3.28M). The leader **Maizen** used the same phrase on 2026-10-25 (5.00M).
  - Evidence: 100 English videos in S-11-04 titled "Zombie Outbreak", from 12 channels, 77 of them long. 5 are ≥1M, all long (Maizen 1, Nobody Gets In 2, Beanie Survives 2).
  - Last seen: 2026-11-04 (Nobody Gets In still posting daily; Kit's Full Movie +59K/day).
  - Labels: all OBSERVED, except that "trend" is INFERRED. Search-biased: the lane queries included survival-movie keywords.
- Coverage note: Nobody Gets In (58.1K subs, 2 long ≥1M) was **absent from the 11-03 dataset**. The 11-03 keyword set did not surface the stickman survival cluster (OBSERVED absence; INFERRED cause). Next quota day: add a "zombie outbreak 30 days" / "day 1 to day 100 full movie" query, and re-pull the uploads of the 6 additions.

## 7. Files written
- `research_notes/Quét ngách Minecraft bằng YouTube API/G_new_competitors_day2.md` (this note)
- `research_notes/Quét ngách Minecraft bằng YouTube API/data/watchlist_2026-11-05.csv` (38 rows)
- `research_notes/Quét ngách Minecraft bằng YouTube API/data/2026-11-04/watchlist_txt_proposed.txt` (proposal for `config/research/minecraft_story_watchlist.txt`; config not overwritten)
- `research_notes/Quét ngách Minecraft bằng YouTube API/data/2026-11-04/derived_G_watchlist_outliers.csv` (144 scored outlier rows behind §3)
