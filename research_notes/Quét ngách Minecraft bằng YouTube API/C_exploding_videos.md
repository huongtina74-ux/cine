# (C) Exploding Minecraft videos, 0–15 days old: ranked list, growth between two API snapshots, and trend patterns

Labels follow CLAUDE.md. **OBSERVED** means counted from the files named in the citation. **INFERRED** means my reasoning from those counts. **OWNER** means the brief said so. All `data/…` links are relative to this note.

## How was growth measured, and which videos count as "English/US Minecraft"?

### Takeaway
Snapshot 1 is the existing dataset (2026-11-03 19:00:33–19:05:26 UTC). Snapshot 2 is one `videos.list part=statistics` pass over 795 selected ids at 19:16:54–19:16:58 UTC, using 16 quota units, with 0 errors and 0 missing ids. The gap is therefore only **11.5–16.4 minutes (median 15.9)**. Δviews and views/hour are a short "speed right now" reading, not a multi-hour trend. After the language and Minecraft filters, **547 of the 953 videos aged ≤15 days with ≥1M views remain: 496 Shorts and 51 long-form** (OBSERVED).

### Cited Findings
- **Snapshot 2 run (OBSERVED, [derived_C_snapshot2_growth.csv](data/derived_C_snapshot2_growth.csv); raw [derived_C_snapshot2_raw_stats.csv](data/derived_C_snapshot2_raw_stats.csv); code in `data/derived_C_code/`).**
  - The code ran on the owner's PC through the Blender MCP with stdlib urllib. It read the key from `.env` inside the process and set it to `None` after the loop. The key was not returned, printed or written.
  - It made 16 calls of 50 ids each (16 units). 795 ids were requested and 795 returned. There were no errors.
  - The PC copy of the output is `C:\Users\ADMIN\Downloads\cine_niche_survey\out\2026-11-03_api_dataset\snapshot2_videos_statistics.csv` (video_id, views, likes, comments, fetched_at; no key). It was staged back to `/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-03_api_dataset/`.
  - No search.list call was made. Remaining quota is about 888 − 16 ≈ 872 units (INFERRED from the earlier counter in [api_dataset.md](api_dataset.md)).
- **Which 795 ids (OBSERVED).**
  - (a) All 590 search videos aged ≤15 days with ≥1M views.
  - (b) 73 more search videos aged ≥4.5 days, >180 s, from channels <100K subs, at ≥5K views/day.
  - (c) 79 upload-sample videos aged ≤15 days with ≥1M views from channels <100K subs.
  - (d) 53 upload-sample long-form videos aged 4.5–15 days from channels <100K subs at ≥5K views/day.
  - Excluded: 284 upload-sample ≥1M videos from channels ≥100K subs (mostly the back catalogues of Shorts factories such as BlobbyClips). They are listed with "–" for growth because a full pass would have needed ~6 more units. Their snapshot-1 numbers are still in the CSVs.
- **Growth metrics, per video (OBSERVED definitions; computed in the derived CSVs).**
  - `d_views` = S2 − S1.
  - `vph_between` = d_views ÷ gap in hours.
  - `vph_lifetime` = S1 views ÷ hours since publish.
  - `accel_ratio` = vph_between ÷ vph_lifetime.
  - `accelerating` = accel_ratio ≥1.25 with d_views > 0.
  - `views_per_day` = views ÷ max(age_days, 1), as in videos.csv.
- **Counter noise (OBSERVED).** 19 of 795 videos showed d_views = 0 ("frozen", e.g. MineBraintor live replays) and 12 showed a small negative Δ. INFERRED: YouTube's public counter updates in batches and sometimes corrects downward, so a ~15-minute Δ under ~1K views is noise.
- **The English/US rule (OBSERVED code, [derived_C_1m_le15d_all.csv](data/derived_C_1m_le15d_all.csv) column `lang_rule`).** A video is kept as English only if all of these hold:
  1. `defaultAudioLanguage` is blank, `zxx` or `en*`.
  2. When the audio language is blank or zxx, `defaultLanguage` is blank or `en*`.
  3. The title has no letters from a non-Latin script (stylised "mathematical" Latin fonts are allowed).
  4. The title has no Spanish/Portuguese/Turkish diacritics (ñ ã õ ç ğ ş ı İ ¿ ¡).
  5. The title has fewer than 2 hits from a Spanish/Portuguese/Indonesian/German/Turkish stop-word list.
  - Of the 953 videos aged ≤15 days with ≥1M views (590 search + 363 upload-sample), 321 fail the rule. Most are Spanish (`es`, `es-MX`, `es-419`), then Hindi, Portuguese, Vietnamese and Indonesian.
  - Indian-run channels with English titles and English or blank audio stay in (e.g. Karry Kraft). Channel country is not used, because 504 channels have a blank country ([api_dataset.md](api_dataset.md)).
- **The Minecraft rule (OBSERVED, column `mc_status`).**
  - `mc_text`: a Minecraft term appears in the title, tags, description or channel name, and the title does not say Roblox without Minecraft.
  - `mc_channel_level`: no term in the video's own text, but ≥30% of the channel's dataset videos are Minecraft (e.g. BlobbyClips' "X Be Like!" animations).
  - Everything else is dropped: the 89 `not_minecraft` (Zack D. Films 0% Minecraft, Vua roblox, Headfilter67CookieGuy, and the Skyrim video from The Spiffing Brit, removed manually) and 24 `unverified_search_hit_only`.
  - The 14 English unverified videos include CaseOh "It's Outside My Window…ep 9" (1.37M), Stay Wild "Surviving HOT vs COLD For 24 Hours!" (12.7M), Doron's World "Technoblade KNEW Dream Was Cheating…" (8.3M) and Hayzits "Don't click the sound" (3.15M).
- **IP rule (OBSERVED, columns `ip_hits`, `ip_class`; title only, because tags are often stuffed).**
  - `3P franchise IP`: Death Note, Sonic, KPop/KPop Demon Hunters, Masha and the Bear, Blippi, Cars, Paw Patrol, Alan Becker AvM, Interstellar, iShowSpeed, etc.
  - `3P creator characters`: Maizen's JJ & Mikey; Verity; Jerry the Wolf; DrDonut. Each counts only when the channel is not the owner.
  - `real-creator reference`: Dream, Technoblade, Grox, Wemmbu, Unstable SMP, FroggyDude, when the channel is not that creator.
  - `own IP`, or otherwise `original/generic-Minecraft`.
  - Vanilla Minecraft (Mojang) is the baseline game for every video, so it is not counted as third-party here.
- **Background on the creator characters (web sources).**
  - Verity is a horror web series/ARG by YouTuber ThatMob that began at the end of May 2026. A fan song "gained over 14 million views in just over a month" after July 2026 — [Know Your Meme](https://trending.knowyourmeme.com/editorials/guides/what-is-verity-the-viral-minecraft-horror-arg-web-series-and-its-me-its-verity-memes-explained).
  - Jerry the Wolf comes from LookOut3D's "Something Is Wrong With My Dog…", uploaded on second channel LookOut2DD on 2026-09-10 — [Know Your Meme](https://knowyourmeme.com/memes/jerry-the-wolf).
  - DrDonut is Nate Filson, an American streamer best known for creating DonutSMP, with 1.9M subscribers as of April 2026 — [Donutpedia](https://donutsmp-wiki.pages.dev/w/DrDonut).

### Inferences
- A 15-minute window is enough to separate videos still being pushed hard (tens of thousands of views per hour) from ones that are coasting. It cannot show a day-over-day curve. A second, cheap pass of the same 795 ids 24 h later (16 units) would give a proper daily growth rate.
- The English rule is conservative. A few English-language videos from channels that set a Spanish `defaultLanguage` are lost. Hindi-audio videos with English titles are correctly excluded.

### Gaps
- No snapshot later than 19:16 UTC exists. Δ over 24 h was not measured.
- Channel country is blank for about a quarter of channels, so "US" cannot be verified per channel. "US-relevant" here means English-language and returned for regionCode=US queries.

## Which videos aged ≤15 days have ≥1M views, how fast are they growing, and are they original or third-party IP?

### Takeaway
The 547 English Minecraft videos split very unevenly.
- **Shorts (496, from 209 channels).** Median 2.13M views and 333K views/day. 280 (56%) are original/generic Minecraft, 148 (30%) use other creators' characters (135 of them Maizen-style JJ & Mikey), and 60 (12%) use franchise IP.
- **Long-form (51, from 36 channels).** Median 1.74M views and 203K views/day. They come almost entirely from established channels (49 of 51 have ≥100K subs; only 1 channel is ≤365 days old), and 38 of 51 are original/generic Minecraft.

Growth between the snapshots is mostly decay. The median Short ran at **0.16×** its lifetime-average speed and the median long-form at **0.37×**. 19 Shorts and 3 long videos were still accelerating (OBSERVED, [derived_C_1m_le15d_en_minecraft.csv](data/derived_C_1m_le15d_en_minecraft.csv)).

### Cited Findings
- **Full list.** All 547 rows are in [derived_C_1m_le15d_en_minecraft.csv](data/derived_C_1m_le15d_en_minecraft.csv), with every field requested: URL, title, channel, channel age, subs, views, views÷subs and bucket, duration, views/day, S1/S2, Δ, views/h, accel ratio and IP class. All 953 rows, before the language and Minecraft filters, are in [derived_C_1m_le15d_all.csv](data/derived_C_1m_le15d_all.csv).
- **Views÷subs buckets (OBSERVED).**
  - Shorts: <1×: 83, 1–10×: 166, 10–100×: 187, 100×+: 60.
  - Long-form: <1×: 25, 1–10×: 24, 10–100×: 1, 100×+: 1.
- **Decay by age (OBSERVED, accel_ratio median by age band; Shorts / long).**
  - 1–2 d: 0.44 / 0.80.
  - 2–3 d: 0.23 / 0.58.
  - 3–5 d: 0.24 / 0.46.
  - 5–7 d: 0.37 / 0.46.
  - 7–10 d: 0.10 / 0.31.
  - 10–15 d: 0.08 / 0.35.
  - Shorts lose most of their speed within about 2 days. Long-form decays about half as fast.
- **Long-form ≥1M aged ≤15 days, all 51, ranked by views/day (OBSERVED; S1 = 19:00–19:05Z, S2 = 19:16:5xZ). The Skyrim video is excluded as not Minecraft.**

| # | ID | Title | Channel | Ch age d | Subs | Views (S1) | Views÷subs | Dur s | Age d | Views/day | Δ S1→S2 (views/h, ×lifetime avg) | IP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [bHxLy6Qza3M](https://www.youtube.com/watch?v=bHxLy6Qza3M) | 10,000 Player Minecraft War: Nether VS Overworld | Parrot | 2260 | 4.45M | 7.22M | 1.6× (1-10x) | 14399 | 2.1 | 3.44M | +28,013 in 16 min = 103K/h (×0.71) | orig |
| 2 | [ZT-k42SC7L0](https://www.youtube.com/watch?v=ZT-k42SC7L0) | 10,000 VS 10,000 Player Minecraft War | FlameFrags | 3255 | 3.08M | 4.78M | 1.6× (1-10x) | 8804 | 3.1 | 1.54M | +5,452 in 16 min = 20K/h (×0.31) | orig |
| 3 | [y5IdSoHdkgg](https://www.youtube.com/watch?v=y5IdSoHdkgg) | 10,000 Players Simulate COLD WAR in Minecraft | Spoke | 4124 | 2.91M | 13.37M | 4.6× (1-10x) | 14381 | 11.8 | 1.13M | +4,918 in 16 min = 19K/h (×0.39) | orig |
| 4 | [ls0FQdzVxko](https://www.youtube.com/watch?v=ls0FQdzVxko) | Testing Trending Minecraft Scary Myths To See If They Are Real! | ProBoiz 95 | 2390 | 9.41M | 6.28M | 0.7× (<1x) | 2380 | 6.2 | 1.02M | +5,342 in 16 min = 20K/h (×0.46) | orig |
| 5 | [ZGYi_JjKhfE](https://www.youtube.com/watch?v=ZGYi_JjKhfE) | If Technoblade's Life Was a Movie... | Sticks | 3733 | 1.16M | 3.12M | 2.7× (1-10x) | 817 | 3.2 | 984K | +10,131 in 16 min = 37K/h (×0.91) | real-creator: Technoblade |
| 6 | [g22Z__ShvVY](https://www.youtube.com/watch?v=g22Z__ShvVY) | Minecraft Speedrunner VS 6 Hunters FINALE | Dream | 4651 | 34.80M | 13.12M | 0.4× (<1x) | 2989 | 14.0 | 939K | +3,582 in 16 min = 14K/h (×0.35) | orig |
| 7 | [FSCGy0YaUaE](https://www.youtube.com/watch?v=FSCGy0YaUaE) | YOU Trolled JJ and Mikey with Infinite Hearts! - Maizen Minecraft Anim | MSToons | 3272 | 1.77M | 1.02M | 0.6× (<1x) | 616 | 1.1 | 909K | +8,244 in 16 min = 30K/h (×0.80) | 3P-creator-char: Maizen JJ&Mikey |
| 8 | [KnlAF_djhdc](https://www.youtube.com/watch?v=KnlAF_djhdc) | 1000 Players Simulate Minecraft's Deadliest Containment Zone... | SpeedSilver | 2148 | 4.00M | 2.33M | 0.6× (<1x) | 9002 | 3.9 | 602K | +4,626 in 16 min = 17K/h (×0.68) | orig |
| 9 | [QBzI4ENJw5g](https://www.youtube.com/watch?v=QBzI4ENJw5g) | FroggyDude VS Grox MANHUNT | FroggyDude Gaming | 1401 | 593K | 1.17M | 2.0× (1-10x) | 1343 | 2.2 | 535K | +3,109 in 16 min = 11K/h (×0.51) | real-creator: Grox|FroggyDude |
| 10 | [Sv78gB7zi_E](https://www.youtube.com/watch?v=Sv78gB7zi_E) | Achievement = 1 Block | Beppo | 3767 | 2.37M | 3.52M | 1.5× (1-10x) | 3962 | 6.7 | 524K | +3,962 in 16 min = 15K/h (×0.66) | orig |
| 11 | [UH1HSIN4L20](https://www.youtube.com/watch?v=UH1HSIN4L20) | SURVIVING in BUS During ZOMBIE APOCALYPSE | Maizen | 2138 | 17.90M | 4.86M | 0.3× (<1x) | 1710 | 9.8 | 496K | +1,974 in 16 min = 7K/h (×0.36) | orig |
| 12 | [PbyK9R4de_o](https://www.youtube.com/watch?v=PbyK9R4de_o) | How I Saved The SIFT DIMENSION in This Minecraft SMP | SenpaiExtras | 1493 | 2.46M | 1.22M | 0.5× (<1x) | 3411 | 2.5 | 490K | +3,234 in 16 min = 12K/h (×0.58) | orig |
| 13 | [Lnl-4FT77Ws](https://www.youtube.com/watch?v=Lnl-4FT77Ws) | JJ BUS EATER was Buried Under The Water - Maizen Minecraft Animation | MSToons | 3272 | 1.77M | 1.37M | 0.8× (<1x) | 790 | 3.1 | 439K | +2,320 in 16 min = 9K/h (×0.47) | 3P-creator-char: Maizen JJ&Mikey |
| 14 | [CoNyot0UsSY](https://www.youtube.com/watch?v=CoNyot0UsSY) | DON'T ENTER THIS HAUNTED SUPERMARKET AT 3AM! | Karry Kraft | 1571 | 1.77M | 1.10M | 0.6× (<1x) | 735 | 3.3 | 333K | +766 in 16 min = 3K/h (×0.20) | orig |
| 15 | [Z3eizu2xYTE](https://www.youtube.com/watch?v=Z3eizu2xYTE) | I Installed MINECRAFT STEVE in Every Game! | ProBoii | 1810 | 2.94M | 2.31M | 0.8× (<1x) | 1286 | 7.2 | 318K | +1,216 in 16 min = 5K/h (×0.35) | orig |
| 16 | [g-GgM-kVnNs](https://www.youtube.com/watch?v=g-GgM-kVnNs) | MAIZEN : ALL EPISODE JJ Sister LOVES JJ - Minecraft Animation JJ & Mik | Cubeee Animations | 590 | 50K | 2.20M | 43.8× (10-100x) | 3269 | 7.1 | 311K | +3,628 in 16 min = 14K/h (×1.06) | 3P-creator-char: Maizen JJ&Mikey |
| 17 | [2lkxXfMFu2Y](https://www.youtube.com/watch?v=2lkxXfMFu2Y) | Dream Cheated Every World Record | MrMangoHands | 4460 | 3K | 3.34M | 1325.4× (100x+) | 1732 | 11.1 | 302K | +611 in 16 min = 2K/h (×0.18) | real-creator: Dream |
| 18 | [Ed74ounoOhc](https://www.youtube.com/watch?v=Ed74ounoOhc) | Jerry The Dog [FULL MOVIE] | LookOut2DD | 639 | 1.16M | 2.73M | 2.4× (1-10x) | 7141 | 9.1 | 299K | +2,598 in 16 min = 10K/h (×0.79) | own: Jerry the Wolf (LookOut3D) |
| 19 | [TFHP1mPdKrY](https://www.youtube.com/watch?v=TFHP1mPdKrY) | This Scary Tree Monster Destroyed Our World in Minecraft.. | Karry Kraft | 1571 | 1.77M | 1.57M | 0.9× (<1x) | 588 | 5.3 | 296K | +974 in 16 min = 4K/h (×0.29) | orig |
| 20 | [BCIEA_QMWmc](https://www.youtube.com/watch?v=BCIEA_QMWmc) | I BUILT A ZOO FOR EVERY HORROR MOB In Minecraft | Maizen | 2138 | 17.90M | 3.87M | 0.2× (<1x) | 3332 | 13.3 | 290K | +1,269 in 16 min = 5K/h (×0.40) | orig |
| 21 | [DbuA1Qd4tIg](https://www.youtube.com/watch?v=DbuA1Qd4tIg) | Upgrading Gun Shop From DIRT to DIAMOND in Minecraft! | Junkeyy | 1771 | 3.64M | 2.24M | 0.6× (<1x) | 1862 | 9.2 | 245K | +711 in 16 min = 3K/h (×0.26) | orig |
| 22 | [_Q-QoRuLYCw](https://www.youtube.com/watch?v=_Q-QoRuLYCw) | when the trapper learns how to PVP... | JudeHigh | 683 | 367K | 2.15M | 5.9× (1-10x) | 2796 | 9.1 | 235K | +427 in 16 min = 2K/h (×0.17) | orig |
| 23 | [4gdIdEStUSY](https://www.youtube.com/watch?v=4gdIdEStUSY) | I Became Minecraft's Deadliest Assassin | TheobaldTheBird | 4488 | 893K | 1.37M | 1.5× (1-10x) | 1493 | 6.2 | 221K | +2,404 in 16 min = 9K/h (×0.96) | orig |
| 24 | [NMqcAa5Di7I](https://www.youtube.com/watch?v=NMqcAa5Di7I) | JJ and Mikey FUSED into TRAIN EATER?! - Maizen Minecraft Animation | MSToons | 3272 | 1.77M | 2.87M | 1.6× (1-10x) | 706 | 13.2 | 218K | +768 in 16 min = 3K/h (×0.32) | 3P-creator-char: Maizen JJ&Mikey |
| 25 | [fHGRgKgIbAU](https://www.youtube.com/watch?v=fHGRgKgIbAU) | Beating Minecraft With The Phobia Mod | Clooless Gaming | 348 | 318K | 1.21M | 3.8× (1-10x) | 3577 | 5.9 | 206K | +1,066 in 16 min = 4K/h (×0.46) | orig |
| 26 | [xHLoAiadBk8](https://www.youtube.com/watch?v=xHLoAiadBk8) | We Found Scary Verity City in Minecraft.. | Karry Kraft | 1571 | 1.77M | 1.48M | 0.8× (<1x) | 730 | 7.3 | 203K | +330 in 16 min = 1K/h (×0.15) | 3P-creator-char: Verity (ThatMob ARG) |
| 27 | [eSWni1Ze2eQ](https://www.youtube.com/watch?v=eSWni1Ze2eQ) | Unstable SMP Speedruns Minecraft! | Wemmbu: The Sequel | 948 | 564K | 2.81M | 5.0× (1-10x) | 1641 | 14.2 | 198K | +231 in 16 min = 874/h (×0.11) | real-creator: Unstable SMP |
| 28 | [3nv6sVj2nm8](https://www.youtube.com/watch?v=3nv6sVj2nm8) | KIDNAPPED By a CAT GIRL in Minecraft! | Karry Kraft | 1571 | 1.77M | 1.79M | 1.0× (1-10x) | 854 | 9.3 | 193K | +529 in 16 min = 2K/h (×0.25) | orig |
| 29 | [C--BdEHsQ3w](https://www.youtube.com/watch?v=C--BdEHsQ3w) | From POOR to RICH BABY in Minecraft! | Cash | 1494 | 11.80M | 1.18M | 0.1× (<1x) | 1396 | 6.2 | 191K | +711 in 16 min = 3K/h (×0.33) | orig |
| 30 | [1y0fQKWFzEI](https://www.youtube.com/watch?v=1y0fQKWFzEI) | I Survived 100 Days as VERITY in Minecraft | EYstreem | 5346 | 13.90M | 2.13M | 0.2× (<1x) | 1701 | 11.8 | 182K | +976 in 16 min = 4K/h (×0.49) | 3P-creator-char: Verity (ThatMob ARG) |
| 31 | [r1EUU26jrTM](https://www.youtube.com/watch?v=r1EUU26jrTM) | We Found GIANT SCARY FOOTPRINTS in Minecraft… | Karry Kraft | 1571 | 1.77M | 1.98M | 1.1× (1-10x) | 831 | 11.2 | 177K | +333 in 16 min = 1K/h (×0.17) | orig |
| 32 | [xxvzkQvsJyg](https://www.youtube.com/watch?v=xxvzkQvsJyg) | We Created BUNKER to Survive SCARY LUNAR MOON in Minecraft... | Junkeyy | 1771 | 3.64M | 2.07M | 0.6× (<1x) | 1227 | 12.2 | 170K | +691 in 16 min = 3K/h (×0.37) | orig |
| 33 | [mCLCxkg9-WE](https://www.youtube.com/watch?v=mCLCxkg9-WE) | I Became King of My Brother's SMP | Freshlol | 2141 | 1.07M | 1.20M | 1.1× (1-10x) | 2197 | 7.3 | 166K | +499 in 16 min = 2K/h (×0.27) | orig |
| 34 | [WrD9HDGEDkc](https://www.youtube.com/watch?v=WrD9HDGEDkc) | Minecraft One Chunk, But It's RANDOM Layers | Farzy | 3958 | 3.30M | 1.46M | 0.4× (<1x) | 2033 | 9.2 | 159K | +2,362 in 16 min = 9K/h (×1.35) ACCEL | orig |
| 35 | [hZONbRYdn5Y](https://www.youtube.com/watch?v=hZONbRYdn5Y) | Minecraft NOOB vs PRO: CREEPER FACTORY BUILD CHALLENGE | Maizen | 2138 | 17.90M | 1.12M | 0.1× (<1x) | 1450 | 7.3 | 152K | +319 in 16 min = 1K/h (×0.19) | orig |
| 36 | [JAYJgDv1pdQ](https://www.youtube.com/watch?v=JAYJgDv1pdQ) | I Joined a Spear Mace Only Minecraft SMP | Freshlol | 2141 | 1.07M | 2.16M | 2.0× (1-10x) | 2870 | 14.3 | 151K | +627 in 16 min = 2K/h (×0.38) | orig |
| 37 | [OnBjF79u3vI](https://www.youtube.com/watch?v=OnBjF79u3vI) | Upgrading into Ben 10 in Minecraft.. | Karry Kraft | 1571 | 1.77M | 2.00M | 1.1× (1-10x) | 700 | 13.3 | 151K | +298 in 16 min = 1K/h (×0.18) | 3P-franchise: Ben 10 |
| 38 | [xdGMMA8kOUU](https://www.youtube.com/watch?v=xdGMMA8kOUU) | We Thought It Was a Mountain | al1 | 979 | 1.67M | 1.34M | 0.8× (<1x) | 1423 | 9.3 | 145K | +663 in 16 min = 3K/h (×0.41) | orig |
| 39 | [RUUdY1aAO5I](https://www.youtube.com/watch?v=RUUdY1aAO5I) | Minecraft: ELEMENTAL ACADEMY | Salt | 1394 | 179K | 1.38M | 7.7× (1-10x) | 5862 | 10.0 | 138K | +854 in 16 min = 3K/h (×0.56) | orig |
| 40 | [dUshzXnUZ6E](https://www.youtube.com/watch?v=dUshzXnUZ6E) | COPS vs ROBBERS: One Chunk Battle! (Minecraft) | Cash | 1494 | 11.80M | 1.13M | 0.1× (<1x) | 1115 | 8.2 | 138K | +337 in 16 min = 1K/h (×0.22) | orig |
| 41 | [db09phDpur4](https://www.youtube.com/watch?v=db09phDpur4) | How I Almost GOT BANNED in This Minecraft SMP | SenpaiExtras | 1493 | 2.46M | 1.96M | 0.8× (<1x) | 4355 | 14.5 | 135K | +241 in 16 min = 911/h (×0.16) | orig |
| 42 | [9kvJoDKvXIg](https://www.youtube.com/watch?v=9kvJoDKvXIg) | SPIN THE BOTTLE = KISS in Minecraft.. | Cash | 1494 | 11.80M | 1.63M | 0.1× (<1x) | 1270 | 12.2 | 134K | +646 in 16 min = 2K/h (×0.44) | orig |
| 43 | [c1rzc-7-Puo](https://www.youtube.com/watch?v=c1rzc-7-Puo) | I Survived a Minecraft Civilization War | Jaden-MAN | 2430 | 451K | 1.43M | 3.2× (1-10x) | 3180 | 11.2 | 128K | +225 in 16 min = 852/h (×0.16) | orig |
| 44 | [RCfATYAsuA0](https://www.youtube.com/watch?v=RCfATYAsuA0) | Industrializing Minecraft with Create | RagePlaysGames | 5398 | 586K | 1.74M | 3.0× (1-10x) | 4193 | 15.0 | 116K | +344 in 16 min = 1K/h (×0.27) | orig |
| 45 | [uAKJRX3FKA0](https://www.youtube.com/watch?v=uAKJRX3FKA0) | I Survived 100 Days as DEATH in Minecraft! | Ryguy v2 | 442 | 180K | 1.24M | 6.9× (1-10x) | 5897 | 11.3 | 110K | +476 in 16 min = 2K/h (×0.39) | orig |
| 46 | [l6z2fg58t9w](https://www.youtube.com/watch?v=l6z2fg58t9w) | POOR Vs RICH Scary Talking Tom Apocalypse Bunker Battle In Minecraft | AlphaExtra | 1887 | 1.06M | 1.44M | 1.4× (1-10x) | 2183 | 13.5 | 107K | +273 in 16 min = 1K/h (×0.23) | orig |
| 47 | [Z6Utg5a7Gew](https://www.youtube.com/watch?v=Z6Utg5a7Gew) | From POOR to RICH School in Minecraft! | Cash | 1494 | 11.80M | 1.14M | 0.1× (<1x) | 1163 | 11.2 | 102K | +261 in 16 min = 990/h (×0.23) | orig |
| 48 | [rNbHC6BalS4](https://www.youtube.com/watch?v=rNbHC6BalS4) | Minecraft's Most Satisfying Moments (Compilation) | アシュch | 419 | 455K | 1.06M | 2.3× (1-10x) | 817 | 11.2 | 95K | – | orig |
| 49 | [xSQSYFGCPLI](https://www.youtube.com/watch?v=xSQSYFGCPLI) | You CHEAT in Manhunt... like dream | Friend | 5301 | 1.95M | 1.07M | 0.5× (<1x) | 1472 | 12.0 | 89K | +385 in 16 min = 1K/h (×0.39) | real-creator: Dream |
| 50 | [cDsFJ8njLmM](https://www.youtube.com/watch?v=cDsFJ8njLmM) | 4 Idiots Have a Sleepover in VR Minecraft with Horror Mods | Vrumpo | 2013 | 524K | 1.12M | 2.1× (1-10x) | 2194 | 13.0 | 86K | +1,199 in 16 min = 5K/h (×1.26) ACCEL | orig |
| 51 | [dslHroagdTo](https://www.youtube.com/watch?v=dslHroagdTo) | WATER vs FIRE: Power PICKAXE BATTLE in Minecraft | Milo and Chip | 1315 | 4.83M | 1.14M | 0.2× (<1x) | 2185 | 14.9 | 77K | +1,079 in 16 min = 4K/h (×1.27) ACCEL | orig |

- **Shorts ≥1M aged ≤15 days: top 30 of 496 by views/day (OBSERVED).** "–" means not re-snapshotted: an upload-sample video from a channel with ≥100K subs.

| # | ID | Title | Channel | Ch age d | Subs | Views (S1) | Views÷subs | Dur s | Age d | Views/day | Δ S1→S2 (views/h, ×lifetime avg) | IP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Jl-KVNhnMjo](https://www.youtube.com/watch?v=Jl-KVNhnMjo) | This feels like a scene from interstellar 🥹 | lowkiMC | 683 | 98K | 18.86M | 192.6× (100x+) | 20 | 2.8 | 6.77M | +21,891 in 16 min = 81K/h (×0.29) | 3P-franchise: Interstellar |
| 2 | [gAJRyICpLe8](https://www.youtube.com/watch?v=gAJRyICpLe8) | Gaming Memories in 50 Years! 🥹🥹 | BlobbyClips | 3286 | 2.83M | 19.64M | 6.9× (1-10x) | 30 | 3.0 | 6.46M | – | orig |
| 3 | [pbeAARuUKsQ](https://www.youtube.com/watch?v=pbeAARuUKsQ) | Fixing Creeper Holes Be Like! 🤣🤣 | BlobbyClips | 3286 | 2.83M | 5.55M | 2.0× (1-10x) | 22 | 1.0 | 5.32M | – | orig |
| 4 | [WtIysmgchPw](https://www.youtube.com/watch?v=WtIysmgchPw) | The Wifi at 3am Be Like! 😆😆 | BlobbyClips | 3286 | 2.83M | 8.56M | 3.0× (1-10x) | 27 | 2.0 | 4.19M | – | orig |
| 5 | [wJ_PY3MWDv0](https://www.youtube.com/watch?v=wJ_PY3MWDv0) | Aliens and Minecraft Secrets! 🤣🤣 | BlobbyClips | 3286 | 2.83M | 4.11M | 1.5× (1-10x) | 27 | 1.0 | 4.11M | – | orig |
| 6 | [MCvsKZr7b_k](https://www.youtube.com/watch?v=MCvsKZr7b_k) | When Your Items Despawn! 😭😭 | BlobbyClips | 3286 | 2.83M | 20.24M | 7.2× (1-10x) | 26 | 5.0 | 4.01M | – | orig |
| 7 | [TKv74nlJCXs](https://www.youtube.com/watch?v=TKv74nlJCXs) | Crafting Circles in Minecraft! 😂😂 | BlobbyClips | 3286 | 2.83M | 45.54M | 16.1× (10-100x) | 25 | 12.0 | 3.78M | +17,358 in 16 min = 66K/h (×0.42) | orig |
| 8 | [tP97dVmvDOY](https://www.youtube.com/watch?v=tP97dVmvDOY) | How Mobs See Render Distance! 😧😧 | BlobbyClips | 3286 | 2.83M | 10.45M | 3.7× (1-10x) | 20 | 3.1 | 3.34M | – | orig |
| 9 | [9BFe_dhmpw0](https://www.youtube.com/watch?v=9BFe_dhmpw0) | block bottoms you've never seen | camman18 | 2040 | 11.40M | 3.33M | 0.3× (<1x) | 26 | 1.1 | 2.96M | – | orig |
| 10 | [ChumXJor8EA](https://www.youtube.com/watch?v=ChumXJor8EA) | Smartest Player VS Dr Donut Part 29 #minecraft #deathnote #skit #funny | PumpBrine | 449 | 100K | 3.51M | 35.1× (10-100x) | 54 | 1.2 | 2.85M | +38,120 in 16 min = 140K/h (×1.18) | 3P-franchise: Death Note|DrDonut |
| 11 | [7wJa_TnXdwU](https://www.youtube.com/watch?v=7wJa_TnXdwU) | Minecraft Mods Then vs Now! 🤣🤣 | BlobbyClips | 3286 | 2.83M | 11.54M | 4.1× (1-10x) | 22 | 4.1 | 2.82M | +13,541 in 16 min = 50K/h (×0.42) | orig |
| 12 | [7ixUnE5FK60](https://www.youtube.com/watch?v=7ixUnE5FK60) | 1 or 2:Wall-Playing Spidervenom Jj sister Reaction🖤🥰🕷️-Minecraft Short | Stonecraft Studios | 1398 | 5.92M | 3.53M | 0.6× (<1x) | 8 | 1.5 | 2.42M | +1,773 in 16 min = 7K/h (×0.07) | 3P-franchise: Spider-Man|Maizen JJ&Mikey |
| 13 | [IK_44LFEOnc](https://www.youtube.com/watch?v=IK_44LFEOnc) | Customizing Characters Gone Wrong! 🤣🤣 | BlobbyClips | 3286 | 2.83M | 8.75M | 3.1× (1-10x) | 25 | 4.1 | 2.12M | – | orig |
| 14 | [pDvFg4rsWoU](https://www.youtube.com/watch?v=pDvFg4rsWoU) | 📹 JJ, Mikey & Steve Funny Dance in Minecraft 😂🥰 - Minecraft Animation  |     ClayBoom 💣 | 31 | 8K | 4.26M | 541.4× (100x+) | 16 | 2.0 | 2.09M | +3,792 in 16 min = 14K/h (×0.16) | 3P-creator-char: Maizen JJ&Mikey |
| 15 | [4w22UAHpwhE](https://www.youtube.com/watch?v=4w22UAHpwhE) | Smartest Player VS Dr Donut #minecraft #deathnote #skit #funny | PumpBrine | 449 | 100K | 12.53M | 125.3× (100x+) | 53 | 6.1 | 2.04M | +24,126 in 16 min = 89K/h (×1.04) | 3P-franchise: Death Note|DrDonut |
| 16 | [L5U1hAWXUDs](https://www.youtube.com/watch?v=L5U1hAWXUDs) | Making a REALISTIC Basketball Hoop in Minecraft | wykull | 3333 | 253K | 14.29M | 56.5× (10-100x) | 161 | 7.3 | 1.96M | +1,623 in 16 min = 6K/h (×0.07) | orig |
| 17 | [EgGF9iLClms](https://www.youtube.com/watch?v=EgGF9iLClms) | 1 or 2: Sleeping Police Jj's Dream Reaction Reveal🛌😮🚨-Minecraft Short  | Stonecraft Studios | 1398 | 5.92M | 4.45M | 0.8× (<1x) | 6 | 2.3 | 1.94M | +895 in 16 min = 3K/h (×0.04) | 3P-creator-char: Maizen JJ&Mikey |
| 18 | [nN_99gCppCg](https://www.youtube.com/watch?v=nN_99gCppCg) | JJ STOLE an Egg 🥚 | MSToons Shorts | 748 | 396K | 5.94M | 15.0× (10-100x) | 18 | 3.1 | 1.90M | – | 3P-creator-char: Maizen JJ&Mikey |
| 19 | [CNX-zw2HaWc](https://www.youtube.com/watch?v=CNX-zw2HaWc) | Green or Yellow? 🐢💚💛 Guess Mikey's Color! 🤔 #shorts | GOLDCRAFT STUDIOS | 1168 | 11.60M | 3.12M | 0.3× (<1x) | 8 | 1.6 | 1.89M | +7,556 in 16 min = 29K/h (×0.36) | 3P-creator-char: Maizen JJ&Mikey |
| 20 | [c6DuztIJ9SQ](https://www.youtube.com/watch?v=c6DuztIJ9SQ) | The Types of Farmers 😭😭 | BlobbyClips | 3286 | 2.83M | 24.54M | 8.7× (1-10x) | 19 | 13.0 | 1.88M | – | orig |
| 21 | [IGiveq3olJU](https://www.youtube.com/watch?v=IGiveq3olJU) | Cushion in water | CheezyChez | 3922 | 1.08M | 2.47M | 2.3× (1-10x) | 32 | 1.3 | 1.85M | +24,095 in 16 min = 89K/h (×1.15) | orig |
| 22 | [dioY__ADDno](https://www.youtube.com/watch?v=dioY__ADDno) | Why Nobody Plays Anymore! 🤔🤔 | BlobbyClips | 3286 | 2.83M | 23.67M | 8.4× (1-10x) | 25 | 13.1 | 1.81M | – | orig |
| 23 | [BknZymlKR_E](https://www.youtube.com/watch?v=BknZymlKR_E) | JJ and Mikey Guess the MONSTER.EXE Inside 📦💀 | MSToons Shorts | 748 | 396K | 22.75M | 57.5× (10-100x) | 63 | 13.1 | 1.73M | +2,290 in 16 min = 9K/h (×0.12) | 3P-creator-char: Maizen JJ&Mikey |
| 24 | [D3djB8bexpM](https://www.youtube.com/watch?v=D3djB8bexpM) | Why Can't You Pause? 🤔🤔 | BlobbyClips | 3286 | 2.83M | 20.83M | 7.4× (1-10x) | 21 | 12.1 | 1.72M | – | orig |
| 25 | [CiphPUTHaJ0](https://www.youtube.com/watch?v=CiphPUTHaJ0) | Crafting Tables Get Jealous! 🤣🤣 | BlobbyClips | 3286 | 2.83M | 15.20M | 5.4× (1-10x) | 23 | 9.1 | 1.67M | – | orig |
| 26 | [Rwx6b2ngh5w](https://www.youtube.com/watch?v=Rwx6b2ngh5w) | No One Helped Evil JJ… 😱 #minecraft #shorts | Cheesy Animation | 131 | 189K | 10.23M | 54.1× (10-100x) | 79 | 6.2 | 1.66M | +7,318 in 16 min = 27K/h (×0.39) | 3P-creator-char: Maizen JJ&Mikey |
| 27 | [rcIOiVn21FE](https://www.youtube.com/watch?v=rcIOiVn21FE) | My hardcore world is nothing without him… | Ayvex | 236 | 576K | 1.93M | 3.3× (1-10x) | 60 | 1.2 | 1.59M | – | orig |
| 28 | [h69NvBvgPj8](https://www.youtube.com/watch?v=h69NvBvgPj8) | Dancing Like Different Animals Backstage 🦖🦍🐶- Minecraft Animation#shor | Minecraft Sea | 302 | 249K | 4.24M | 17.0× (10-100x) | 19 | 2.8 | 1.51M | +10,881 in 16 min = 40K/h (×0.63) | orig |
| 29 | [IQ1h20t2wMc](https://www.youtube.com/watch?v=IQ1h20t2wMc) | Woodland Mansion vs. Flint and Steel! 😂😂 | BlobbyClips | 3286 | 2.83M | 2.99M | 1.1× (1-10x) | 21 | 2.0 | 1.50M | – | orig |
| 30 | [t75SLaZKWSA](https://www.youtube.com/watch?v=t75SLaZKWSA) | Minecraft But Breaking One Block Changes Them All / #shorts | Joeysaf | 3765 | 489K | 2.77M | 5.7× (1-10x) | 146 | 1.9 | 1.48M | +9,279 in 16 min = 34K/h (×0.55) | orig |

- **Top 25 by absolute speed between snapshots (views/hour), with accel ratio (OBSERVED).** This is the best "exploding right now" list:

| # | ID | Title | Channel | Ch age d | Subs | Views (S1) | Views÷subs | Dur s | Age d | Views/day | Δ S1→S2 (views/h, ×lifetime avg) | IP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [glwTiwUdhJo](https://www.youtube.com/watch?v=glwTiwUdhJo) | Who Will ADOPT JJ Kitten?! 🥺🐱 #minecraft | XOXU MINECRAFT | 276 | 14K | 1.29M | 89.8× (10-100x) | 46 | 0.5 | 1.29M | +46,389 in 16 min = 175K/h (×1.46) ACCEL | 3P-creator-char: Maizen JJ&Mikey |
| 2 | [ChumXJor8EA](https://www.youtube.com/watch?v=ChumXJor8EA) | Smartest Player VS Dr Donut Part 29 #minecraft #deathnote #skit #funny | PumpBrine | 449 | 100K | 3.51M | 35.1× (10-100x) | 54 | 1.2 | 2.85M | +38,120 in 16 min = 140K/h (×1.18) | 3P-franchise: Death Note|DrDonut |
| 3 | [Ep9sV6gEdgo](https://www.youtube.com/watch?v=Ep9sV6gEdgo) | ive seen this prank | DrDonut Clips | 1711 | 2.35M | 2.46M | 1.0× (1-10x) | 17 | 5.6 | 440K | +33,208 in 16 min = 122K/h (×6.68) ACCEL | orig |
| 4 | [bHxLy6Qza3M](https://www.youtube.com/watch?v=bHxLy6Qza3M) | 10,000 Player Minecraft War: Nether VS Overworld | Parrot | 2260 | 4.45M | 7.22M | 1.6× (1-10x) | 14399 | 2.1 | 3.44M | +28,013 in 16 min = 103K/h (×0.71) | orig |
| 5 | [xxa_Jpt0l_M](https://www.youtube.com/watch?v=xxa_Jpt0l_M) | Smartest Player VS Dr Donut Part 32 #minecraft #deathnote #skit #funny | PumpBrine | 449 | 100K | 1.09M | 10.9× (10-100x) | 54 | 0.6 | 1.09M | +23,760 in 16 min = 89K/h (×1.19) | 3P-franchise: Death Note|DrDonut |
| 6 | [IGiveq3olJU](https://www.youtube.com/watch?v=IGiveq3olJU) | Cushion in water | CheezyChez | 3922 | 1.08M | 2.47M | 2.3× (1-10x) | 32 | 1.3 | 1.85M | +24,095 in 16 min = 89K/h (×1.15) | orig |
| 7 | [4w22UAHpwhE](https://www.youtube.com/watch?v=4w22UAHpwhE) | Smartest Player VS Dr Donut #minecraft #deathnote #skit #funny | PumpBrine | 449 | 100K | 12.53M | 125.3× (100x+) | 53 | 6.1 | 2.04M | +24,126 in 16 min = 89K/h (×1.04) | 3P-franchise: Death Note|DrDonut |
| 8 | [Jl-KVNhnMjo](https://www.youtube.com/watch?v=Jl-KVNhnMjo) | This feels like a scene from interstellar 🥹 | lowkiMC | 683 | 98K | 18.86M | 192.6× (100x+) | 20 | 2.8 | 6.77M | +21,891 in 16 min = 81K/h (×0.29) | 3P-franchise: Interstellar |
| 9 | [TKv74nlJCXs](https://www.youtube.com/watch?v=TKv74nlJCXs) | Crafting Circles in Minecraft! 😂😂 | BlobbyClips | 3286 | 2.83M | 45.54M | 16.1× (10-100x) | 25 | 12.0 | 3.78M | +17,358 in 16 min = 66K/h (×0.42) | orig |
| 10 | [y-IFKuhBqBE](https://www.youtube.com/watch?v=y-IFKuhBqBE) | Masha and Bear X Kpop Head Noob Pro Jump Challenge (Part 1)😱 #minecraf | Oren Shorts | 2070 | 4.70M | 1.19M | 0.3× (<1x) | 33 | 2.1 | 567K | +16,564 in 16 min = 62K/h (×2.64) ACCEL | 3P-franchise: Masha and the Bear|KPop (generic/KDH) |
| 11 | [H1_V9gxhQfg](https://www.youtube.com/watch?v=H1_V9gxhQfg) | JJ & Mikey, Who win ?! #minecraft #shorts | 1997studio | 1624 | 23K | 1.82M | 79.3× (10-100x) | 19 | 2.3 | 782K | +15,199 in 16 min = 57K/h (×1.76) ACCEL | 3P-creator-char: Maizen JJ&Mikey |
| 12 | [LKdjKUER3aY](https://www.youtube.com/watch?v=LKdjKUER3aY) | DUMB the SOUND 🤦‍♂️ | zedarGG | 306 | 232K | 3.39M | 14.6× (10-100x) | 64 | 6.2 | 550K | +15,631 in 16 min = 57K/h (×2.50) ACCEL | orig |
| 13 | [7wJa_TnXdwU](https://www.youtube.com/watch?v=7wJa_TnXdwU) | Minecraft Mods Then vs Now! 🤣🤣 | BlobbyClips | 3286 | 2.83M | 11.54M | 4.1× (1-10x) | 22 | 4.1 | 2.82M | +13,541 in 16 min = 50K/h (×0.42) | orig |
| 14 | [dpB7vy8n1x8](https://www.youtube.com/watch?v=dpB7vy8n1x8) | Mikey Dont Want Corn 🌽 #minecraftshorts | JojoCraft | 254 | 378K | 3.29M | 8.7× (1-10x) | 11 | 3.8 | 868K | +13,522 in 16 min = 50K/h (×1.37) ACCEL | 3P-creator-char: Maizen JJ&Mikey |
| 15 | [q_N23LHqAnE](https://www.youtube.com/watch?v=q_N23LHqAnE) | 1 or 2:Wall-Playing Jj sister Reaction🏥🕸️🥰-Minecraft Short Animation # | Stonecraft Studios | 1398 | 5.92M | 5.51M | 0.9× (<1x) | 8 | 5.8 | 952K | +13,337 in 16 min = 49K/h (×1.23) | 3P-creator-char: Maizen JJ&Mikey |
| 16 | [uiLAXLyBwlY](https://www.youtube.com/watch?v=uiLAXLyBwlY) | Minecraft Steve vs Death Factory 💀 | Craft Lab3D | 1050 | 196K | 6.48M | 33.0× (10-100x) | 17 | 4.4 | 1.46M | +13,288 in 16 min = 49K/h (×0.80) | orig |
| 17 | [UiRv3wqFuIs](https://www.youtube.com/watch?v=UiRv3wqFuIs) | Minecraft game play with animation #minecraft #minecraftbuilding #mine | Mrjunaid Short | 41 | 14K | 2.39M | 171.8× (100x+) | 85 | 3.3 | 724K | +9,225 in 12 min = 47K/h (×1.57) ACCEL | orig |
| 18 | [h69NvBvgPj8](https://www.youtube.com/watch?v=h69NvBvgPj8) | Dancing Like Different Animals Backstage 🦖🦍🐶- Minecraft Animation#shor | Minecraft Sea | 302 | 249K | 4.24M | 17.0× (10-100x) | 19 | 2.8 | 1.51M | +10,881 in 16 min = 40K/h (×0.63) | orig |
| 19 | [ZGYi_JjKhfE](https://www.youtube.com/watch?v=ZGYi_JjKhfE) | If Technoblade's Life Was a Movie... | Sticks | 3733 | 1.16M | 3.12M | 2.7× (1-10x) | 817 | 3.2 | 984K | +10,131 in 16 min = 37K/h (×0.91) | real-creator: Technoblade |
| 20 | [ow9qGwMrSTk](https://www.youtube.com/watch?v=ow9qGwMrSTk) | Bro Crafted Netherite Armor 💀 | Mine Mythos | 170 | 16K | 3.25M | 204.4× (100x+) | 13 | 7.0 | 467K | +9,331 in 16 min = 34K/h (×1.76) ACCEL | orig |
| 21 | [t75SLaZKWSA](https://www.youtube.com/watch?v=t75SLaZKWSA) | Minecraft But Breaking One Block Changes Them All / #shorts | Joeysaf | 3765 | 489K | 2.77M | 5.7× (1-10x) | 146 | 1.9 | 1.48M | +9,279 in 16 min = 34K/h (×0.55) | orig |
| 22 | [41cbKN_LHXA](https://www.youtube.com/watch?v=41cbKN_LHXA) | I Tried Every Minecraft Food! | Nolan | 1758 | 3.55M | 3.33M | 0.9× (<1x) | 132 | 6.1 | 550K | +8,358 in 16 min = 31K/h (×1.34) ACCEL | orig |
| 23 | [FSCGy0YaUaE](https://www.youtube.com/watch?v=FSCGy0YaUaE) | YOU Trolled JJ and Mikey with Infinite Hearts! - Maizen Minecraft Anim | MSToons | 3272 | 1.77M | 1.02M | 0.6× (<1x) | 616 | 1.1 | 909K | +8,244 in 16 min = 30K/h (×0.80) | 3P-creator-char: Maizen JJ&Mikey |
| 24 | [3HGsNwJQ8v8](https://www.youtube.com/watch?v=3HGsNwJQ8v8) | Smartest Player VS Dr Donut Part 14 #minecraft #deathnote #skit #funny | PumpBrine | 449 | 100K | 2.80M | 28.0× (10-100x) | 51 | 3.5 | 798K | +8,105 in 16 min = 30K/h (×0.90) | 3P-franchise: Death Note|DrDonut |
| 25 | [CNX-zw2HaWc](https://www.youtube.com/watch?v=CNX-zw2HaWc) | Green or Yellow? 🐢💚💛 Guess Mikey's Color! 🤔 #shorts | GOLDCRAFT STUDIOS | 1168 | 11.60M | 3.12M | 0.3× (<1x) | 8 | 1.6 | 1.89M | +7,556 in 16 min = 29K/h (×0.36) | 3P-creator-char: Maizen JJ&Mikey |

### Inferences
- **"Exploding right now" (INFERRED from the speed table).** Four groups are being pushed hardest in the 19:00–19:17 UTC window.
  - PumpBrine's "Smartest Player VS Dr Donut Part N". Parts 1, 14, 29 and 32 each gained 8K–38K views in about 16 minutes, and three of the four run at ≥1× their lifetime average (1.04–1.19).
  - Brand-new JJ-kitten/JJ-vs-Mikey Shorts from tiny channels: XOXU MINECRAFT 175K/h at 14K subs, and 1997studio 57K/h at 23K subs.
  - The Unstable-SMP 10,000-player war (Parrot, 103K/h).
  - A DrDonut Clips Short at 6.7× its lifetime speed.
- Third-party characters do not get more views per day than original Shorts. The medians are 307K/day (creator characters) and 332K/day (franchise) against 355K/day (original) (OBSERVED). For CineFactory this means the original-IP rule costs nothing measurable at the median (INFERRED).

### Gaps
- Retention, CTR and traffic source are not in the public API. Whether a Short's views come from the Shorts feed or from search cannot be told.

## Which ≥1M videos come from small channels (<100K subs), and at what multiples?

### Takeaway
**157 of the 496 English Shorts with ≥1M views come from 89 channels under 100K subs.** All 157 are at ≥10× their subscriber count: 98 at 10–100× and 59 at 100×+, with a median of 76.7×. Only **2 long-form** videos with ≥1M views come from small channels: a Maizen JJ & Mikey compilation (43.8×) and the Dream commentary "Dream Cheated Every World Record" (1,325×). So a small channel reaching 1M in 15 days is overwhelmingly a Shorts event (OBSERVED, [derived_C_1m_le15d_en_minecraft.csv](data/derived_C_1m_le15d_en_minecraft.csv)).

### Cited Findings
- **Small-channel Shorts by IP (OBSERVED).** 87 original/generic, 44 third-party creator characters (mostly JJ & Mikey and Verity), 19 franchise IP, 7 real-creator references.
- **Channel age (OBSERVED).** 48 of the 496 English Shorts come from channels ≤90 days old, and 15 from channels ≤30 days old. Examples:
  - ClayBoom (31 d, 8K subs): 4.26M on "JJ, Mikey & Steve Funny Dance".
  - CHIRAG FACTO (11 d, 26K): 2.62M.
  - Erzxck (22 d, 17K): 12.07M "Minecraft Verity Match The Block Game".
  - Mochi & Pals (20 d, 1K): 1.42M "Who can dig down the fastest?".
  - Mrjunaid Short (41 d, 14K): 2.39M.
  - Ziggy Blox (24 d, 61K): 9.36M "I Fooled a Million Zombies".
- **Repeat hitters among small channels (OBSERVED; number of ≥1M Shorts).** Mikey Crazy 6, Ziggy Blox 6, Mine Mythos 5, MaizCr 5, melZerry 4, Joeysaf Clips 4, AAYUUSPEED 4. Beazle, CHIRAG FACTO, darix, JPAUL, SAM_TOON, SWEETY BLOCK, Tg Jamal Shorts 44, Superoid Man, Sticki Crew, Snow Mine, NoobySquad, Mine HM, Erzxck and lowkiMC have 3 each.
- **Top 45 small-channel (<100K subs) Shorts by views/day (OBSERVED).** All 157 are in the CSV (filter `channel_subs < 100000`).

| # | ID | Title | Channel | Ch age d | Subs | Views (S1) | Views÷subs | Dur s | Age d | Views/day | Δ S1→S2 (views/h, ×lifetime avg) | IP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Jl-KVNhnMjo](https://www.youtube.com/watch?v=Jl-KVNhnMjo) | This feels like a scene from interstellar 🥹 | lowkiMC | 683 | 98K | 18.86M | 192.6× (100x+) | 20 | 2.8 | 6.77M | +21,891 in 16 min = 81K/h (×0.29) | 3P-franchise: Interstellar |
| 2 | [pDvFg4rsWoU](https://www.youtube.com/watch?v=pDvFg4rsWoU) | 📹 JJ, Mikey & Steve Funny Dance in Minecraft 😂🥰 - Minecraft Animation  |     ClayBoom 💣 | 31 | 8K | 4.26M | 541.4× (100x+) | 16 | 2.0 | 2.09M | +3,792 in 16 min = 14K/h (×0.16) | 3P-creator-char: Maizen JJ&Mikey |
| 3 | [glwTiwUdhJo](https://www.youtube.com/watch?v=glwTiwUdhJo) | Who Will ADOPT JJ Kitten?! 🥺🐱 #minecraft | XOXU MINECRAFT | 276 | 14K | 1.29M | 89.8× (10-100x) | 46 | 0.5 | 1.29M | +46,389 in 16 min = 175K/h (×1.46) ACCEL | 3P-creator-char: Maizen JJ&Mikey |
| 4 | [xel-UZ5bf1s](https://www.youtube.com/watch?v=xel-UZ5bf1s) | Slither Run with Steve - Funny Animation | CHIRAG FACTO | 11 | 26K | 2.62M | 100.9× (100x+) | 35 | 2.2 | 1.20M | +2,377 in 16 min = 9K/h (×0.17) | orig |
| 5 | [uYhJbAYatv8](https://www.youtube.com/watch?v=uYhJbAYatv8) | Kpop Head Noob Pro Trap Challenge Part 12/ #minecraft #shorts | darix | 3919 | 25K | 8.02M | 319.4× (100x+) | 43 | 7.0 | 1.15M | +4,196 in 16 min = 15K/h (×0.32) | 3P-franchise: KPop (generic/KDH) |
| 6 | [Oocx5mNdz0E](https://www.youtube.com/watch?v=Oocx5mNdz0E) | MaizCR Don’t Cross Until the Monster Cars Pass! 🚗😱 #minecraft #animati | MaizCr | 162 | 34K | 1.53M | 44.4× (10-100x) | 17 | 1.4 | 1.08M | +1,208 in 16 min = 4K/h (×0.10) | orig |
| 7 | [hDoxpvKPwCA](https://www.youtube.com/watch?v=hDoxpvKPwCA) | Newest oldest trick in the book 😭✌️ #minecraftsurvival  #minecraftshor | Beazle | 737 | 8K | 2.22M | 265.4× (100x+) | 17 | 2.1 | 1.07M | +4,990 in 16 min = 18K/h (×0.41) | orig |
| 8 | [KBPyFBc73oI](https://www.youtube.com/watch?v=KBPyFBc73oI) | Come on bro😭✌️#minecraftshorts #minecraft #minecraftmemes #minecraftsu | Beazle | 737 | 8K | 10.69M | 1279.3× (100x+) | 19 | 10.1 | 1.06M | +2,447 in 16 min = 9K/h (×0.21) | orig |
| 9 | [JQCrn203IdM](https://www.youtube.com/watch?v=JQCrn203IdM) | Happy little fellas | Sticky Spawn | 1987 | 97K | 6.47M | 66.5× (10-100x) | 16 | 6.2 | 1.04M | +305 in 16 min = 1K/h (×0.03) | orig |
| 10 | [Af43UFHita0](https://www.youtube.com/watch?v=Af43UFHita0) | They’re still figuring out the job 😭 | lowkiMC | 683 | 98K | 2.04M | 20.8× (10-100x) | 18 | 2.0 | 1.02M | +5,055 in 15 min = 20K/h (×0.46) | orig |
| 11 | [31tzZ_Y3n4c](https://www.youtube.com/watch?v=31tzZ_Y3n4c) | Minecraft Verity Match The Block Game 🟡#minecraft #minecraftshorts #sh | Erzxck | 22 | 17K | 12.07M | 697.8× (100x+) | 75 | 11.8 | 1.02M | +6,401 in 16 min = 24K/h (×0.57) | 3P-creator-char: Verity (ThatMob ARG) |
| 12 | [hg1KSeUva34](https://www.youtube.com/watch?v=hg1KSeUva34) | Dark JJ Cars DESTROYED JJ's Race! 😱🚗 #minecraft | Mikey Crazy | 143 | 85K | 2.15M | 25.4× (10-100x) | 53 | 2.1 | 1.01M | +1,568 in 15 min = 6K/h (×0.15) | 3P-creator-char: Maizen JJ&Mikey |
| 13 | [wKUybajlHMg](https://www.youtube.com/watch?v=wKUybajlHMg) | JJ Golem SAVES All Mobs From a HUGE VERITY TSUNAMI! 🌊😱 #minecraft | Mikey Crazy | 143 | 85K | 1.14M | 13.4× (10-100x) | 58 | 1.1 | 997K | +4,805 in 16 min = 18K/h (×0.44) | 3P-creator-char: Maizen JJ&Mikey|Verity (ThatMob ARG) |
| 14 | [BE2Chg5AaEk](https://www.youtube.com/watch?v=BE2Chg5AaEk) | Melt the ICE Challenge! ROBLOX VS BARRY! #youtubeshorts #roblox #carto | PatchShi | 1364 | 11K | 1.67M | 146.7× (100x+) | 29 | 1.8 | 950K | +366 in 16 min = 1K/h (×0.03) | orig |
| 15 | [5dwJxih_if8](https://www.youtube.com/watch?v=5dwJxih_if8) | Water can build PRESSURE in minecraft?? | melZerry | 319 | 26K | 4.30M | 164.6× (100x+) | 30 | 4.7 | 907K | +1,607 in 16 min = 6K/h (×0.16) | orig |
| 16 | [U5gk5iDSJAk](https://www.youtube.com/watch?v=U5gk5iDSJAk) | Small To Giant Steve VS Planets ! #minecraft #teardown | TeardownTown | 1029 | 66K | 1.83M | 27.6× (10-100x) | 38 | 2.1 | 890K | +1,748 in 16 min = 6K/h (×0.17) | orig |
| 17 | [D6br6Dam-rA](https://www.youtube.com/watch?v=D6br6Dam-rA) | larp / #animation #alanbecker #avm #minecraft | Floog | 325 | 2K | 1.59M | 894.3× (100x+) | 18 | 2.0 | 809K | +6,448 in 16 min = 24K/h (×0.70) | 3P-franchise: Alan Becker AvM |
| 18 | [H1_V9gxhQfg](https://www.youtube.com/watch?v=H1_V9gxhQfg) | JJ & Mikey, Who win ?! #minecraft #shorts | 1997studio | 1624 | 23K | 1.82M | 79.3× (10-100x) | 19 | 2.3 | 782K | +15,199 in 16 min = 57K/h (×1.76) ACCEL | 3P-creator-char: Maizen JJ&Mikey |
| 19 | [loykFiwzUpY](https://www.youtube.com/watch?v=loykFiwzUpY) | Chainmail Craft 💀 | Mine Mythos | 170 | 16K | 9.52M | 598.5× (100x+) | 13 | 12.8 | 744K | +971 in 14 min = 4K/h (×0.13) | orig |
| 20 | [UiRv3wqFuIs](https://www.youtube.com/watch?v=UiRv3wqFuIs) | Minecraft game play with animation #minecraft #minecraftbuilding #mine | Mrjunaid Short | 41 | 14K | 2.39M | 171.8× (100x+) | 85 | 3.3 | 724K | +9,225 in 12 min = 47K/h (×1.57) ACCEL | orig |
| 21 | [vH0pd4SomN8](https://www.youtube.com/watch?v=vH0pd4SomN8) | I Fooled a Million Zombies 😱 | Ziggy Blox | 24 | 61K | 9.36M | 153.2× (100x+) | 141 | 13.3 | 704K | +203 in 15 min = 806/h (×0.03) | orig |
| 22 | [EkNgf9DDtwM](https://www.youtube.com/watch?v=EkNgf9DDtwM) | During the Day vs At Night 🚒🚛🚂🚜#minecraft  #animation #funny | MaizCr | 162 | 34K | 1.63M | 47.3× (10-100x) | 17 | 2.4 | 675K | +3,439 in 16 min = 13K/h (×0.45) | orig |
| 23 | [hhK1dOPDo1E](https://www.youtube.com/watch?v=hhK1dOPDo1E) | All Mobs STOLE JJ Golem's BODY PARTS! 😱 #minecraft | Mikey Crazy | 143 | 85K | 2.04M | 24.1× (10-100x) | 58 | 3.1 | 669K | +2,252 in 16 min = 8K/h (×0.30) | 3P-creator-char: Maizen JJ&Mikey |
| 24 | [05jFksgGiLY](https://www.youtube.com/watch?v=05jFksgGiLY) | Verity’s Bridge Challenge! SONIC vs SHADOW – Only One Can Cross! 🌉😱 Wh | SAM_TOON | 46 | 15K | 3.73M | 255.8× (100x+) | 10 | 5.6 | 669K | +19 in 16 min = 70/h (×0.00) | 3P-franchise: Sonic|Verity (ThatMob ARG) |
| 25 | [cyM7B7sxJ5w](https://www.youtube.com/watch?v=cyM7B7sxJ5w) | finger licking chicken😭 #minecraftshorts #minecraftmemes #minecraft #m | Beazle | 737 | 8K | 1.27M | 152.3× (100x+) | 18 | 2.0 | 635K | +417 in 16 min = 2K/h (×0.06) | orig |
| 26 | [nf9oZPSqhjE](https://www.youtube.com/watch?v=nf9oZPSqhjE) | Who can dig down the fastest? | Mochi & Pals | 20 | 1K | 1.42M | 1343.8× (100x+) | 16 | 2.3 | 631K | +1,476 in 16 min = 5K/h (×0.21) | orig |
| 27 | [Q6aH51XXylY](https://www.youtube.com/watch?v=Q6aH51XXylY) | Paw Patrol in Minecraft : Chase vs Rubble , Come Here . #pawpatrol #mi | King Animation Team | 6014 | 58K | 4.86M | 83.4× (10-100x) | 13 | 7.7 | 630K | +736 in 16 min = 3K/h (×0.11) | 3P-franchise: Paw Patrol |
| 28 | [IYZEPN-PQmQ](https://www.youtube.com/watch?v=IYZEPN-PQmQ) | JJ and JJ Sister Wall-Playing 1 😱 / Minecraft Animation #minecraft #ma | Mr MushMoo Animations | 43 | 6K | 1.38M | 228.4× (100x+) | 8 | 2.3 | 607K | +1,122 in 16 min = 4K/h (×0.17) | 3P-creator-char: Maizen JJ&Mikey |
| 29 | [uTjxhkO1_SE](https://www.youtube.com/watch?v=uTjxhkO1_SE) | Which One Would You Guys Choose? | Tg Jamal Shorts 44 | 314 | 24K | 4.43M | 187.6× (100x+) | 6 | 7.5 | 592K | +417 in 14 min = 2K/h (×0.07) | orig |
| 30 | [c4hlCcskZcY](https://www.youtube.com/watch?v=c4hlCcskZcY) | The Biggest Bucket In Minecraft | Joeysaf Clips | 1515 | 40K | 3.54M | 88.3× (10-100x) | 36 | 6.2 | 574K | +1,622 in 16 min = 6K/h (×0.25) | orig |
| 31 | [sbEISEco27M](https://www.youtube.com/watch?v=sbEISEco27M) | Kpop Head Noob Pro Trap Challenge Part 3/ #minecraft  #shorts | darix | 3919 | 25K | 6.71M | 267.1× (100x+) | 48 | 12.2 | 548K | +1,334 in 16 min = 5K/h (×0.22) | 3P-franchise: KPop (generic/KDH) |
| 32 | [VPpYNzsYCPg](https://www.youtube.com/watch?v=VPpYNzsYCPg) | Minecraft Before Google 💀 | Mine Mythos | 170 | 16K | 8.20M | 516.0× (100x+) | 13 | 15.0 | 548K | +175 in 14 min = 746/h (×0.03) | orig |
| 33 | [a27xegKDv6o](https://www.youtube.com/watch?v=a27xegKDv6o) | Amy saved us! #minecraft | Snow Mine | 100 | 78K | 7.27M | 93.8× (10-100x) | 49 | 13.6 | 535K | +4,085 in 14 min = 17K/h (×0.77) | orig |
| 34 | [jUXeCrkxo_E](https://www.youtube.com/watch?v=jUXeCrkxo_E) | Kpop Head Noob Pro Trap Challenge Part 10/ #minecraft #shorts | darix | 3919 | 25K | 4.15M | 165.5× (100x+) | 48 | 7.9 | 525K | +1,815 in 16 min = 7K/h (×0.31) | 3P-franchise: KPop (generic/KDH) |
| 35 | [MithTcX-Mb8](https://www.youtube.com/watch?v=MithTcX-Mb8) | JJ SAVES Animals from a TSUNAMI! 🌊🐱 #minecraft | Mikey Crazy | 143 | 85K | 6.74M | 79.5× (10-100x) | 58 | 12.9 | 523K | +502 in 16 min = 2K/h (×0.09) | 3P-creator-char: Maizen JJ&Mikey |
| 36 | [NXCnMP6Em1g](https://www.youtube.com/watch?v=NXCnMP6Em1g) | What Do You Guys Think Who Will Win | Tg Jamal Shorts 44 | 314 | 24K | 1.82M | 77.0× (10-100x) | 6 | 3.5 | 523K | +2,020 in 16 min = 7K/h (×0.34) | orig |
| 37 | [FEXoI1HfYI8](https://www.youtube.com/watch?v=FEXoI1HfYI8) | Technoblade core part 4 / #technoblade #minecraft | Audio Mansion | 991 | 48K | 2.98M | 62.0× (10-100x) | 55 | 5.7 | 520K | +3,403 in 16 min = 13K/h (×0.58) | real-creator: Technoblade |
| 38 | [b--CG4XUtSg](https://www.youtube.com/watch?v=b--CG4XUtSg) | Who Stole JJ's Halloween Candy?? #minecraft | Blanco Craft | 125 | 15K | 2.65M | 173.0× (100x+) | 46 | 5.2 | 508K | +1 in 16 min = 4/h (×0.00) | 3P-creator-char: Maizen JJ&Mikey |
| 39 | [3is1ebirAXQ](https://www.youtube.com/watch?v=3is1ebirAXQ) | Jesus in 2b2t’s spawn update | nixil | 686 | 33K | 2.93M | 87.8× (10-100x) | 61 | 5.9 | 497K | +5,209 in 16 min = 19K/h (×0.92) | orig |
| 40 | [QTLtqJriKgM](https://www.youtube.com/watch?v=QTLtqJriKgM) | JJ and Pig Swap Brains, But What Happens Next Shocks The Pig 🐷😂 #short | Blockified  | 276 | 20K | 2.05M | 104.8× (100x+) | 9 | 4.2 | 493K | +9 in 16 min = 33/h (×0.00) | 3P-creator-char: Maizen JJ&Mikey |
| 41 | [Dg8Zp56TgSY](https://www.youtube.com/watch?v=Dg8Zp56TgSY) | Redstone is more useful than ever 😭 | lowkiMC | 683 | 98K | 3.44M | 35.2× (10-100x) | 9 | 7.1 | 487K | +3,335 in 15 min = 13K/h (×0.64) | orig |
| 42 | [ow9qGwMrSTk](https://www.youtube.com/watch?v=ow9qGwMrSTk) | Bro Crafted Netherite Armor 💀 | Mine Mythos | 170 | 16K | 3.25M | 204.4× (100x+) | 13 | 7.0 | 467K | +9,331 in 16 min = 34K/h (×1.76) ACCEL | orig |
| 43 | [-z7CRoxTRcY](https://www.youtube.com/watch?v=-z7CRoxTRcY) | This mod adds hmmmmmmmmm….. | MishimaShock | 808 | 3K | 3.29M | 1093.2× (100x+) | 20 | 7.1 | 463K | +904 in 16 min = 3K/h (×0.18) | orig |
| 44 | [e9H1xdYXOhU](https://www.youtube.com/watch?v=e9H1xdYXOhU) | Dark JJ Dog STOLE Their BODY PARTS! 😱💀 #minecraft | Mikey Crazy | 143 | 85K | 2.75M | 32.4× (10-100x) | 55 | 6.0 | 459K | +4,216 in 16 min = 15K/h (×0.81) | 3P-creator-char: Maizen JJ&Mikey |
| 45 | [rbfO_HXSg4E](https://www.youtube.com/watch?v=rbfO_HXSg4E) | More Realistic Tatami Mats for Minecraft Interiors | Nightfxll | 351 | 27K | 5.94M | 218.5× (100x+) | 17 | 13.1 | 455K | +221 in 16 min = 835/h (×0.04) | orig |

### Inferences
- Original-IP small-channel breakouts cluster into a few repeatable shapes (INFERRED from the titles above):
  - Relatable "Minecraft memes": Beazle "Come on bro😭✌️" (1,279×), Mine Mythos "Chainmail Craft 💀" (599×) and "Minecraft Before Google 💀" (516×).
  - Mechanics/physics curiosities: melZerry "Water can build PRESSURE in minecraft??" (165×) and "…RING WORLD" (187×).
  - Satisfying micro-builds: Nightfxll "More Realistic Tatami Mats" (219×).
  - Tiny-cast competitions: Mochi & Pals "Who can dig down the fastest?" (1,344×), Tg Jamal "Which One Would You Guys Choose?" (188×), darix "Noob Pro Trap Challenge Part N" (165–319×).
  - Short emotional animations: Floog "larp" (894×), Snow Mine "Amy saved us!" (94×).
  - All of these are under ~60 s and need no third-party character.
- The 100×+ bucket is where tiny channels live. A 1M Short on a 1–10K channel is common enough (59 cases) that a single viral Short says little about a channel's repeatability. Repeat hitters (≥3 hits in 15 days) are the better trend evidence.

### Gaps
- Subscriber counts are rounded to 3 significant figures ([api_dataset.md](api_dataset.md)), so 1K–3K-sub multiples are coarse.
- Network or second-channel status (e.g. "Joeysaf Clips" from Joeysaf, "DrDonut Clips", "Drdonutt Official Clip") is not in the API. Some "small" channels are clip channels of big creators.

## What trend patterns cluster, which are original vs third-party, and which are short-lived vs repeatable?

### Takeaway
- **Shorts.** Volume concentrates in four title shapes:
  - Emoji-reaction memes: 155 hits.
  - "X vs Y / who will win" duels: 51.
  - Family/sad JJ stories: 48.
  - "Survive/challenge": 39.
- **Hottest new meme templates (OBSERVED first appearance in the upload sample).** All appeared in September–October 2026:
  - "Smartest Player VS Dr Donut Part N", first seen 2026-09-15.
  - "[ADJ] the SOUND", first seen 2026-09-19.
  - "1 or 2: JJ … Reaction", first seen 2026-10-18.
  - "Kpop Head Noob Pro Trap Challenge Part N", first seen 2026-10-17.
  - "Dark/Evil JJ", first seen 2026-09-15.
  - Verity (since 2026-06-21) and Jerry the dog (since 2026-08-31) are the two creator-character waves.
- **Long-form.** The ≥1M formats are big-channel staples: 1,000–10,000-player war simulations (median 1.13M views/day), manhunts, myth-testing horror, "100 days", one-chunk/random-layers, poor-to-rich roleplay and "[FULL MOVIE]" compilations (OBSERVED, [derived_C_pattern_summary.csv](data/derived_C_pattern_summary.csv), [derived_C_pattern_history_uploads.csv](data/derived_C_pattern_history_uploads.csv)).

### Cited Findings
- **Pattern counts in the 547 English Minecraft videos with ≥1M views (OBSERVED, [derived_C_pattern_summary.csv](data/derived_C_pattern_summary.csv); a title can match several patterns; regexes are in `data/derived_C_code/analyze_c.py`).**

| Pattern | Shorts n (small ch) | Shorts median views/day | Shorts median views÷subs | Shorts share 3P (franchise + creator chars) | Long n | Long median views/day |
|---|---|---|---|---|---|---|
| emoji reaction (😭💀🤣…) | 155 (47) | 355K | 5.8× | 55% | – | – |
| X vs Y / versus | 51 (12) | 344K | 14.6× | 67% | 8 | 344K |
| family / love / sad / bully | 48 (11) | 331K | 8.4× | 60% | 5 | 166K |
| build / house / base / trap / design | 43 (11) | 307K | 10.5× | 21% | 1 | 152K |
| survive / challenge / hardcore | 39 (18) | 312K | 12.0× | 64% | 6 | 161K |
| "Minecraft but…" | 26 (5) | 297K | 5.7× | 8% | 1 | 159K |
| choose / guess / who can / which one / match the block | 26 (9) | 210K | 9.7× | 62% | – | – |
| horror / .EXE / myth / 3 AM / zombie / monster | 21 (7) | 441K | 11.9× | 48% | 12 | 256K |
| donut / smartest player / deathnote / skit | 20 (0) | 461K | 16.2× | 100% | – | – |
| noob vs pro / hacker | 10 (4) | 358K | 13.1× | 80% | 1 | 152K |
| first time / food / eat / cake | 9 (4) | 255K | 11.7× | 44% | – | – |
| mod / mace / axe / kit / OP | 9 (4) | 305K | 24.1× | 11% | 4 | 119K |
| POV | 3 (2) | 206K | 90.3× | 0% | – | – |
| then vs now / update | 3 (2) | 497K | 34.4× | 0% | – | – |
| poor vs rich | 2 (1) | 275K | 84.2× | 100% | 3 | 107K |
| something is … / in my house/world | 1 (1) | 111K | 39.4× | 0% | – | – |
| players simulate / war / civilization | – | – | – | – | 5 | 1,134K |
| manhunt / speedrun / hunters | 2 | 193K | 13.9× | 100% | 4 | 366K |
| 100 days | – | – | – | – | 2 | 146K |
| full movie / all episodes | 1 | 373K | 15.5× | 0% | 3 | 311K |

- **Ad-hoc templates (OBSERVED; Shorts with ≥1M / small channels / channels; first appearance in the 11,408-row upload sample).**
  - "Smartest Player VS Dr Donut Part N", all PumpBrine: 19 hits on one 100K channel, first seen 2026-09-15. 103 donut-pattern uploads exist across 12 channels, 86% of them from the last 15 days.
  - "[ADJ] the SOUND" (AGE/DUMB/UNFAIR/LUCKY/NOT/AFRAID the SOUND, "CLICK THE SOUND"): 10 / 0 / 5 channels (zedarGG, zedarextra, Zedar Short, Corgi MC, Ingot MC). First seen 2026-09-19.
  - "1 or 2: … JJ … Reaction", almost all Stonecraft Studios (5.92M subs): 20 / 1 / 2. First seen 2026-10-18.
  - "Dark/Evil JJ …": 27 / 3 / 12 channels. First seen 2026-09-15.
  - "No One Helped [Evil/Dark] JJ…": 3 hits with a median of 975K views/day. First seen 2026-09-18.
  - "Kpop Head Noob Pro … Challenge Part N": 5 / 3 / 3. First seen 2026-10-17.
  - "Part N" serial Shorts in general: 17 / 5 / 6 channels, median 555K views/day.
  - Verity in the title: 25 videos (23 Shorts, 10 small channels, 21 channels). 703 Verity uploads exist in the sample, first seen 2026-06-21.
  - Jerry: 4 / 0 / 4, first seen 2026-08-31. The original is LookOut2DD "Jerry The Dog [FULL MOVIE]": 2.73M in 9.1 days at 1.16M subs.
  - Nostalgia/"Before Google"/"Beta players": 5 / 4 / 4, first seen 2026-09-12.
  - Physics/mechanics curiosity (melZerry, camman18 "block bottoms you've never seen"): 7 / 4 / 5.
  - "Something is wrong with…": 0 videos with ≥1M in English Minecraft. Ayvex "Something is wrong with me…" has 1.12M but sits in the all-rows file. 12 uploads, first seen 2026-09-05.
- **Duration (OBSERVED).**
  - English Shorts with ≥1M: median 37 s, interquartile range 18–60 s. By band: 97 at ≤15 s, 110 at 16–30 s, 158 at 31–60 s, 38 at 61–90 s, 79 at 91–180 s.
  - Long-form with ≥1M: 1 at 3–10 min, 10 at 10–20 min, 13 at 20–30 min, 14 at 30–60 min, 10 over 60 min (the 2–4 h player-war simulations).
- **Concentration (OBSERVED).** BlobbyClips (32), Stonecraft Studios (31), PumpBrine (19), camman18 (14) and Joeysaf (14) account for 110 of the 496 English Shorts with ≥1M (22%).

### Inferences
- **Short-lived (meme or series), INFERRED from first-seen dates within the last ~7 weeks and concentration in 1–5 channels:**
  - Dr Donut/Death Note skits: third-party franchise plus a real creator. Avoid.
  - "[ADJ] the SOUND".
  - "1 or 2" JJ reactions: third-party.
  - Kpop-Head trap challenges: franchise-adjacent.
  - Dark/Evil JJ and "No One Helped JJ": third-party.
  - The Verity and Jerry waves: third-party creator characters. Verity has lasted ~5 months, which is long for a meme but still someone else's IP.
  - Halloween-tagged titles will decay after 2026-10-31.
- **Repeatable formats that work with original IP, INFERRED from ≥3 independent channels, first-seen dates in 2023–2025, and low third-party share:**
  - Shorts:
    - Relatable gameplay memes ("X Be Like", "When your items despawn", nostalgia).
    - Mechanics/physics curiosities ("…??", "what happens if…").
    - Satisfying realistic builds and interiors (wykull, Nightfxll; build pattern 21% third-party).
    - "Minecraft but…" rule-change Shorts (8% third-party; Joeysaf, BlobbyClips).
    - Mod/item-power Shorts (11% third-party, highest median multiple at 24×).
    - Tiny-cast contests ("Who can dig the fastest?", "Which one would you choose?").
  - Long-form:
    - Myth/horror testing (12 hits, 8% third-party).
    - "100 Days in [disaster]" and "[FULL MOVIE]" survival stories.
    - Mass-player simulations. These need large casts and servers, so INFERRED they are not reachable for a new channel.
- **Original vs third-party split, by format (OBSERVED counts above).** Shorts: 56% original/generic, 42% third-party (franchise or creator characters). Long-form: 75% original/generic.
- **Characters (OBSERVED from titles).** The recurring "characters" are Steve, Herobrine, JJ/Mikey and their "sister", Verity, Jerry the wolf, Dr Donut, Grox, Technoblade and Dream. Only Steve/Herobrine and generic mobs are not owned by another creator. INFERRED: this is a gap an original recurring duo or family could fill. The JJ & Mikey clones show demand for a two-character kid-friendly duo with a sibling.

### Gaps
- The `first_seen` dates come from the last ≤50 uploads of 308 channels. For Shorts-heavy channels, those 50 uploads cover only weeks, so a template may be older than shown. The dates are a lower bound on age, not proof of novelty.
- Pattern tagging is regex on titles. It does not include what happens on screen (no video viewing, per the brief).

## Which 5–15-day-old long-form videos (>3 min) from small channels show high views/day, even below 1M?

### Takeaway
86 English Minecraft long-form videos aged 5–15 days from channels under 100K subs run at ≥5K views/day. The best are a JJ & Mikey "all episodes" compilation (311K/day) and a Dream commentary (302K/day). Among original IP, the leaders are:
- Cobweb "Beating Players with PvP kits only I know how to use" (97K/day, 13.8×).
- Jaiz "I Designed a Mod to Torture Speedrunners" (85K/day).
- JoeyShmoovin "Minecraft HORROR, But We CANT Break Character…" (84K/day).
- WoodsyZ "I Got The Mace Axe" (74K/day).
- Kit vs The End "Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship… (Full Movie)" (67K/day, 69×, channel 37 days old) (OBSERVED, [derived_C_longform_5to15d_small_signals.csv](data/derived_C_longform_5to15d_small_signals.csv)).

### Cited Findings
- **Top 30 by views/day (OBSERVED).**

| # | ID | Title | Channel | Ch age d | Subs | Views (S1) | Views÷subs | Dur s | Age d | Views/day | Δ S1→S2 (views/h, ×lifetime avg) | IP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [g-GgM-kVnNs](https://www.youtube.com/watch?v=g-GgM-kVnNs) | MAIZEN : ALL EPISODE JJ Sister LOVES JJ - Minecraft Animation JJ & Mik | Cubeee Animations | 590 | 50K | 2.20M | 43.8× (10-100x) | 3269 | 7.1 | 311K | +3,628 in 16 min = 14K/h (×1.06) | 3P-creator-char: Maizen JJ&Mikey |
| 2 | [2lkxXfMFu2Y](https://www.youtube.com/watch?v=2lkxXfMFu2Y) | Dream Cheated Every World Record | MrMangoHands | 4460 | 3K | 3.34M | 1325.4× (100x+) | 1732 | 11.1 | 302K | +611 in 16 min = 2K/h (×0.18) | real-creator: Dream |
| 3 | [IdwH1fbtOkc](https://www.youtube.com/watch?v=IdwH1fbtOkc) | Minecraft TNT Blast IN VILLAGE | MineBraintor | 31 | 2K | 982K | 525.3× (100x+) | 5074 | 5.9 | 166K | +0 in 13 min = 0/h (×0.00) frozen | orig |
| 4 | [8zrl4YNyPA4](https://www.youtube.com/watch?v=8zrl4YNyPA4) | JJ and Mikey in ALL LOVE STORY PIT LORD VERITY & JERRY DOG & LIGHTING  | Cody Toon | 63 | 43K | 641K | 14.8× (10-100x) | 668 | 6.2 | 103K | +831 in 16 min = 3K/h (×0.74) | 3P-franchise: Cars/McQueen|Maizen JJ&Mikey|Verity (ThatMob ARG)|Jerry the Wolf (LookOut3D) |
| 5 | [-pl0Xmo26Ik](https://www.youtube.com/watch?v=-pl0Xmo26Ik) | Minecraft TNT Blast Village Live 0004 | MineBraintor | 31 | 2K | 548K | 292.9× (100x+) | 4936 | 5.5 | 99K | +0 in 13 min = 0/h (×0.00) frozen | orig |
| 6 | [X9ZXFM5a6jg](https://www.youtube.com/watch?v=X9ZXFM5a6jg) | Beating Players with PvP kits only I know how to use | Cobweb | 268 | 42K | 579K | 13.8× (10-100x) | 579 | 6.0 | 97K | +807 in 16 min = 3K/h (×0.74) | orig |
| 7 | [FqvK2EWQC00](https://www.youtube.com/watch?v=FqvK2EWQC00) | I Designed a Mod to Torture Speedrunners | Jaiz | 1740 | 35K | 567K | 16.2× (10-100x) | 922 | 6.7 | 85K | +534 in 16 min = 2K/h (×0.56) | orig |
| 8 | [hh_jy89yTvo](https://www.youtube.com/watch?v=hh_jy89yTvo) | Minecraft HORROR, But We CANT Break Character... | JoeyShmoovin | 2326 | 29K | 812K | 28.2× (10-100x) | 5666 | 9.7 | 84K | +409 in 16 min = 2K/h (×0.44) | orig |
| 9 | [0uz1VrBg8gE](https://www.youtube.com/watch?v=0uz1VrBg8gE) | I Got The Mace Axe | WoodsyZ | 2239 | 32K | 676K | 21.2× (10-100x) | 3218 | 9.1 | 74K | +313 in 16 min = 1K/h (×0.38) | orig |
| 10 | [xdj5PL0t61k](https://www.youtube.com/watch?v=xdj5PL0t61k) | Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship. One Sound A | Kit vs The End | 37 | 10K | 673K | 69.2× (10-100x) | 4382 | 10.0 | 67K | +666 in 16 min = 3K/h (×0.90) | orig |
| 11 | [g0yIHLLAlnQ](https://www.youtube.com/watch?v=g0yIHLLAlnQ) | DONT CALL 3 AM SECRET JJ SISTER SCARY HALLOWEEN - Maizen JJ & Mikey An | Морфиз | 546 | 74K | 420K | 5.7× (1-10x) | 769 | 6.4 | 65K | +1,458 in 16 min = 6K/h (×2.02) ACCEL | 3P-creator-char: Maizen JJ&Mikey |
| 12 | [lj50e066xB4](https://www.youtube.com/watch?v=lj50e066xB4) | JJ and Mikey survival in ALL DOORS WITH ALL VERITY VERSIONS & SAKADUNG | Cody Toon | 63 | 43K | 616K | 14.2× (10-100x) | 608 | 10.3 | 60K | +267 in 13 min = 1K/h (×0.50) | 3P-creator-char: Maizen JJ&Mikey|Verity (ThatMob ARG) |
| 13 | [R7yDCbR5lwQ](https://www.youtube.com/watch?v=R7yDCbR5lwQ) | This Mace Turns You Into Wemmbu | Wellou | 402 | 21K | 462K | 22.2× (10-100x) | 1477 | 8.0 | 58K | +283 in 16 min = 1K/h (×0.45) | real-creator: Wemmbu |
| 14 | [pesa4keKrMc](https://www.youtube.com/watch?v=pesa4keKrMc) | Mikey and JJ Friends: NOOB vs PRO STAIRS Battle in Minecraft - Maizen | Blomzy - Mikey & JJ Minecraft | 7378 | 86K | 328K | 3.8× (1-10x) | 1331 | 6.5 | 50K | +124 in 16 min = 458/h (×0.22) | 3P-creator-char: Maizen JJ&Mikey |
| 15 | [80X7icVjFxY](https://www.youtube.com/watch?v=80X7icVjFxY) | JJ and Mikey: Built SECRET BASES Inside Their Girlfriends' Backpacks.. | Mikey & JJ Verse | 179 | 71K | 259K | 3.7× (1-10x) | 1023 | 5.4 | 48K | +23 in 12 min = 115/h (×0.06) | 3P-creator-char: Maizen JJ&Mikey |
| 16 | [DBt-Jc6DK04](https://www.youtube.com/watch?v=DBt-Jc6DK04) | JJ and Mikey Found a SECRET BASE BLIPPI.EXE in Minecraft - Maizen | Super Maizen | 1329 | 79K | 267K | 3.4× (1-10x) | 1006 | 6.8 | 39K | +364 in 16 min = 1K/h (×0.82) | 3P-franchise: Blippi|Maizen JJ&Mikey |
| 17 | [Z8VHxBP6CII](https://www.youtube.com/watch?v=Z8VHxBP6CII) | There’s an Angel Hiding in My World... | CloudyDreamzs | 2722 | 23K | 552K | 24.2× (10-100x) | 3438 | 14.6 | 38K | +107 in 16 min = 405/h (×0.26) | orig |
| 18 | [AYkLerdq_2I](https://www.youtube.com/watch?v=AYkLerdq_2I) | 🔥MINECRAFT LIVE! Creating Massive Emperor💎 #Minecraft #minecraftlive | AlphaOGPlayz | 272 | 14K | 255K | 18.9× (10-100x) | 25663 | 6.9 | 37K | +1 in 12 min = 5/h (×0.00) | orig |
| 19 | [c47f1Gojteg](https://www.youtube.com/watch?v=c47f1Gojteg) | I destroyed BULLIES on my School's SMP... | RedishPlays | 859 | 8K | 175K | 23.0× (10-100x) | 1837 | 5.1 | 35K | +1,279 in 16 min = 5K/h (×3.26) ACCEL | orig |
| 20 | [eAqPRLb9JQg](https://www.youtube.com/watch?v=eAqPRLb9JQg) | I Survived 100 Days in a DEADLY OUTBREAK in Minecraft | Day Zero | 29 | 14K | 370K | 26.6× (10-100x) | 2430 | 11.1 | 33K | +103 in 16 min = 389/h (×0.28) | orig |
| 21 | [vi0AMe5kiEg](https://www.youtube.com/watch?v=vi0AMe5kiEg) | Rich Axolotl’s Downfall Minecraft Animation | Iron Studio Minecraft Animation | 607 | 20K | 424K | 20.7× (10-100x) | 287 | 12.9 | 33K | +67 in 16 min = 254/h (×0.18) | orig |
| 22 | [Ow7L7VZoY74](https://www.youtube.com/watch?v=Ow7L7VZoY74) | Minecraft, But I Join a Pirate Civilization [FULL MOVIE] | Boof and Bung | 734 | 78K | 185K | 2.4× (1-10x) | 3298 | 6.2 | 30K | +208 in 16 min = 764/h (×0.62) | orig |
| 23 | [FFcKUJfYWqk](https://www.youtube.com/watch?v=FFcKUJfYWqk) | 1,000,000 Villagers Simulate RICH vs POOR in Minecraft | BowlerCraft | 1802 | 11K | 332K | 30.8× (10-100x) | 1204 | 11.9 | 28K | +632 in 16 min = 2K/h (×2.06) ACCEL | orig |
| 24 | [51OemhUogXk](https://www.youtube.com/watch?v=51OemhUogXk) | 🔥MINECRAFT LIVE! Creating Massive Emperor💎 #Minecraft #minecraftlive | AlphaOGPlayz | 272 | 14K | 215K | 15.9× (10-100x) | 29318 | 7.8 | 27K | +0 in 12 min = 0/h (×0.00) frozen | orig |
| 25 | [a-smKMDN3no](https://www.youtube.com/watch?v=a-smKMDN3no) | Minecraft Shorts Coldest Moments Ever / best compilation video that br | 𝕮𝖗𝖆𝖋𝖙𝖎𝖈𝖔 | 951 | 28K | 374K | 13.6× (10-100x) | 633 | 14.6 | 26K | +554 in 16 min = 2K/h (×1.96) ACCEL | orig |
| 26 | [kVc4yVAH1Fs](https://www.youtube.com/watch?v=kVc4yVAH1Fs) | WHAT IS GOING ON IN RADIANT SMP ? / RAWKNEE | The RawKnee Live | 545 | 73K | 146K | 2.0× (1-10x) | 16757 | 6.0 | 24K | +11 in 16 min = 40/h (×0.04) | orig |
| 27 | [JqwECK8JIJU](https://www.youtube.com/watch?v=JqwECK8JIJU) | Mikey & JJ Friends From POOR to RICH in Minecraft…Maizen | JJ Cartoons | 45 | 4K | 284K | 79.3× (10-100x) | 1360 | 12.4 | 23K | +79 in 16 min = 299/h (×0.31) | 3P-creator-char: Maizen JJ&Mikey |
| 28 | [JWKUEtrEkzA](https://www.youtube.com/watch?v=JWKUEtrEkzA) | 20000 Zombie & Lord Verity VS Secure House With Cats In Minecraft | my MONSTER SCHOOL | 325 | 11K | 254K | 22.2× (10-100x) | 632 | 11.1 | 23K | +27 in 12 min = 131/h (×0.14) | 3P-creator-char: Verity (ThatMob ARG) |
| 29 | [4-HK_OKoxQo](https://www.youtube.com/watch?v=4-HK_OKoxQo) | JJ and Mikey survival in MAZE WITH ALL JERRY DOG VERSIONS in Minecraft | Cody Toon | 63 | 43K | 299K | 6.9× (1-10x) | 606 | 13.3 | 23K | +48 in 13 min = 224/h (×0.24) | 3P-creator-char: Maizen JJ&Mikey|Jerry the Wolf (LookOut3D) |
| 30 | [m7t_EhVzBGg](https://www.youtube.com/watch?v=m7t_EhVzBGg) | How a Happy Ghast shows Dream staged a Manhunt | BjorkMinecraft | 1702 | 19K | 212K | 11.0× (10-100x) | 667 | 9.7 | 22K | +245 in 16 min = 926/h (×1.02) | real-creator: Dream |

- **Accelerating long-form from small channels (OBSERVED, accel ≥1.25).**
  - RedishPlays "I destroyed BULLIES on my School's SMP…" (8K subs, ×3.26).
  - True Mario "SONIC, MARIO & LUIGI vs HEROBRINE!" (×2.73, franchise IP).
  - BowlerCraft "1,000,000 Villagers Simulate RICH vs POOR" (11K subs, ×2.06).
  - Banazen Craft "Only JJ Can SAVE His Friends from the GRAVE" (10-day-old channel, ×2.02).
  - Морфиз JJ sister Halloween (×2.02).
  - Craftico compilation (×1.96).
- **Live replays (OBSERVED).** MineBraintor "Minecraft TNT Blast IN VILLAGE" (982K, 5,074 s, channel 31 days old, 2K subs) and AlphaOGPlayz "MINECRAFT LIVE!" are live-stream replays with frozen counters between snapshots.

### Inferences
- The original-IP long-form signals from small channels are personality-led gameplay (PvP kits, mods, maces) and narrative horror/survival "movies". The "100 Days / FULL MOVIE / One Sound And They Find You" stack from Kit vs The End (37-day-old channel, 69×) and Day Zero (29 days, 26.6×) is the closest match to a scripted, animatable original format (INFERRED).
- The live-replay rows and the JJ & Mikey compilations should not count as signals for CineFactory: the first are not a production format, and the second use third-party IP (INFERRED).

### Gaps
- Sixteen of the top 30 are below 50K views/day, and long-form views keep accruing for weeks. A 24 h re-snapshot is needed to tell sustained risers from one-day spikes.
