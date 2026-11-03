# Minecraft YouTube sub-niches (US/English, 0–7 and 0–15 days): demand, newcomer share, third-party IP, leaders and outliers

Snapshot: YouTube Data API v3 run of 2026-11-03 19:00–19:05 UTC. Analysis only uses files already in `data/`. No API calls and no scraping were made for this note. Labels follow CLAUDE.md: **OBSERVED** means counted from the dataset files (or the derived CSVs built from them). **INFERRED** means my reasoning. **OWNER** means the owner or brief said so. Every derived table is in `data/derived_A_*.csv`. The scripts that produced them are in `data/derived_A_code/` (run order: `run.py → metrics.py → leaders.py → rank.py → tables.py`).

## Q1. How the dataset was cleaned and classified (language filter, taxonomy, manual review)

### Takeaway
2,827 videos went in and 1,858 passed the English filter. After off-topic removal, the main 0–7-day analysis set is **1,486 English Minecraft videos (1,068 Shorts ≤180 s, 418 long-form)**. Each video was tagged into one of 20 sub-niches with ordered rules, per-channel overrides for mono-format channels, and a title-only third-party-IP flag. I hand-checked **717 unique videos**. They carry 78.5% of 7-day English views and 59.6% of the 7-day ≥100K hits (OBSERVED).

### Cited Findings
- **Language rule (OBSERVED, [derived_A_videos_tagged.csv](data/derived_A_videos_tagged.csv), column `lang_drop`).** A video is dropped in any of three cases:
  - (a) `default_audio_language` is set and is not `en*` or `zxx`. This dropped 728 videos.
  - (b) The audio language is blank or `zxx`, and `default_language` is set and is not `en*`. This dropped 226.
  - (c) The title is foreign. This dropped 15. A title is foreign when non-Latin letters (Devanagari, Arabic, Thai, Cyrillic, CJK, Hangul…) make up ≥15% of its letters, or when it contains ≥2 non-English function words. The lists cover Spanish, Portuguese, Indonesian, Turkish, German, French, Vietnamese and Hinglish (e.g. "Gareeb Alex Ko Gaon Walo Ne Rulaya", "Jangan mencuri ayam tetangga!").
  - Result: 1,858 kept of 2,827. Kept videos include English-titled uploads from India and other non-US countries with `en-IN`/blank audio (e.g. ProBoiz 95, Karry Kraft, Junkeyy). The data cannot show US audience share.
- **Off-topic removal (OBSERVED).** Two groups are excluded from every niche metric.
  - **`OFF` (33 videos).** The title says Roblox, GTA, Skyrim, Mario or similar without "minecraft", or there is no Minecraft word in title, tags or description but there is a Roblox/GTA-type word. Examples: Vua roblox 11.9M, Stay Wild "Surviving HOT vs COLD For 24 Hours!" 12.7M, The Spiffing Brit "Skyrims Greatest Challenge", NotGamerFleet "…| ROBLOX".
  - **`UNCLEAR` (33 videos).** No Minecraft word anywhere and an empty description. Example: VoidCast "If You Lose Hide And Seek, A Monster Takes You" 4.8M.
- **Taxonomy (OBSERVED codes; rules in [aclass.py](data/derived_A_code/aclass.py)).**

| Code | Sub-niche / format |
| --- | --- |
| HOR_FIC | Horror fiction: found footage, analog horror, ARG, creepypasta, Broken Script, lost worlds |
| HOR_PLAY | Horror mods, scary myths and seeds, haunted roleplay, horror let's-plays |
| SURV100 | Scripted survival: "100 days", "I survived", hardcore series, "THE MOVIE"/[FULL MOVIE] |
| SIM_WAR | Player simulations and wars ("1,000/10,000 players", civilization) |
| MANHUNT_PVP | Manhunt, speedrunner vs hunters, PvP, hide-and-seek |
| CHALL_BUT | "Minecraft but…", challenges, lucky block, one block/chunk, "beating Minecraft with X mod" |
| SMP | SMP series and streamer clips (Unstable SMP, Donut SMP, 2b2t, Lifesteal, Final Life, Forever World) |
| RP_STORY_GAMEPLAY | Gameplay roleplay, pranks, trolls, "noob vs pro", "poor to rich", "I became…" (Cash, Aphmau, Maizen long-form, Karry Kraft) |
| KIDS_ANIM_STORY | Kids character-animation stories (JJ/Mikey fan animation, "No one helped…", sad story, Monster School, baby/family) |
| KIDS_CHOICE_PUZZLE | Interactive choice and puzzle ("1 or 2", guess, choose the door, bridge/head/maze challenge, "who will win", "help X") |
| SKIT_COMEDY | Animated comedy skits not explicitly kids-coded (BlobbyClips, PumpBrine, Wablo) |
| MEMES_CLIPS | Gameplay memes, clips, edits, "X the SOUND", try-not-to-laugh |
| BUILD | Build tutorials, hacks and ideas, farms, redstone builds |
| FACTS_TIPS_NEWS | Mechanics and tips, "why do…", update news |
| DOC_LORE | Long documentaries and drama ("Dream cheated…") |
| SATISFY_REAL | Satisfying or semi-realistic renders, IRL crossovers |
| FOOD_FIRST | Food, "first time", eating |
| MUSIC_DANCE | Dance, music, parody songs |
| ART_DRAW | Drawing and pixel art |
| LP_GENERAL | Other long-form let's-plays and modded survival |

- **How each tag was assigned in the 7-day set (OBSERVED, `niche_how`).** ordered title rule 1,042; per-channel override 153; manual-review fixes coded as rules 57 + 42 + 21; tag-keyword rule 42; fallback 129 (115 Shorts→MEMES_CLIPS, 14 long→LP_GENERAL).
  - Per-channel overrides were set only after reading that channel's titles. Examples: Stonecraft Studios→KIDS_CHOICE_PUZZLE, PumpBrine/BlobbyClips→SKIT_COMEDY, camman18→FACTS, Joeysaf→CHALL_BUT, wykull/WhiteDot→BUILD, CaseOh→HOR_PLAY, Maizen (official)→RP_STORY_GAMEPLAY.
- **Manual review (OBSERVED).** 717 unique videos were read title by title, alongside channel, duration and assigned tag. The set is:
  - the top 320 English videos by views
  - the top 230 long-form videos
  - the top 10 of every niche × format cell in the 7-day window
  - the top 40 OFF/UNCLEAR
  - every 7-day ≥100K no-IP video from a channel ≤12 months old
  - every long-form ≥100K video from a channel <100K subs or ≤12 months old
  - Review led to five rounds of rule changes. Examples: Herobrine-only Shorts were moved out of horror, "Monster School" was routed to kids animation, Roblox titles were moved to OFF, and own-channel IP was exempted.
- **Third-party-IP flag (OBSERVED, column `ip3p`).** Title-only regex families:
  - `maizen_jj_mikey` (Maizen, JJ, Mikey)
  - `verity` (Verity, Lovety, Falsity, Twixxel)
  - `sprunki`
  - `poppy_playtime` (Huggy, Catnap, Banban)
  - `kpop_demon_hunters` (Rumi, Jinu, "Kpop head")
  - `skibidi_toilet`
  - `mrbeast`
  - `creators_dream_smp_etc`: Dream, Technoblade, Spoke, Wemmbu, Unstable/Donut SMP, Grox, iShowSpeed, CaseOh, Aphmau, Dr Donut…
  - `italian_brainrot`
  - `other_franchise`: Sonic, Numberblocks, Paw Patrol, Ben 10, Saitama/JJK/Gojo, Smurf Cat, TADC, Labubu, Talking Tom, Spider-Man/Venom, SCP, FNAF, Interstellar, Breaking Bad…
  - A creator's own name on their own channel is not counted as third-party (e.g. Maizen on Maizen, Dream on Dream).
  - Mojang-native characters (Steve, Alex, Herobrine, mobs) are **not** flagged.
  - A tag-inclusive variant is kept in `ip3p_incl_tags`. Tags are heavily SEO-stuffed, so the title version is the one reported.
- **Format split (OBSERVED).** Shorts = `duration_s` ≤180 s, as in the dataset's `is_short_candidate`. 1 upcoming live with no duration is excluded.
- **Window (OBSERVED).** All niche metrics use videos aged ≤7 days. The 7–15-day band exists only for 18 core keywords, so it is under-sampled ([api_dataset.md](api_dataset.md) caveat). 15-day counts are in [derived_A_niche_counts_15d.csv](data/derived_A_niche_counts_15d.csv).

### Inferences
- About 21% of 7-day ≥100K hits (100% − 59.6% hand-checked − remaining long-tail share) rest on regex only. Expect some cross-bucket leakage between MEMES_CLIPS, SKIT_COMEDY and KIDS_ANIM_STORY, which differ by tone more than by title words. Niche totals are robust to this because the hand-checked set covers 78.5% of views. Medians of small niches are less robust.
- English-titled South-Asian uploads with `en-IN` audio pass the filter. "US/English" here means English-language, not a US audience.

### Gaps
- Classification error rate was **not measured**. That would need a blind second labeller on a random sample.
- Audio language is blank for about 36% of videos (1,009 of 2,827 in the raw file), so the title heuristic carries those. A few English-titled dubbed videos are probably still inside.

## Q2. Sub-niche demand in the last 7 days, Shorts vs long-form

### Takeaway
Seven-day demand is **87% Shorts by raw views (583.8M Shorts vs 88.7M long, OBSERVED)**. Four Shorts sub-niches each pull roughly 88–131M: memes/clips, interactive choice/puzzle, kids JJ-style animation and animated comedy skits. Long-form demand concentrates in gameplay roleplay (17.6M), player simulations/wars (15.3M, 10 videos), horror mods and myths (14.2M), "Minecraft but" challenges (8.2M) and scripted 100-days survival (7.7M). Horror *fiction* (found footage/ARG) is tiny: 1.5M total, 2.8K median long-form. Weighted by the OWNER/AIR Shorts RPM ratio (3–14% of long-form), long-form is still **52–84% of revenue-equivalent demand** (INFERRED).

### Cited Findings
- **Per-niche demand, 7 days, English (OBSERVED, [derived_A_niche_metrics_7d.csv](data/derived_A_niche_metrics_7d.csv)).**
  - Columns: n; total and median views; count ≥100K / ≥1M; then share of ≥100K hits from channels ≤12 months / ≤90 days / ≤30 days old / <100K subs; share of ≥1M hits from channels ≤12 months / <100K subs; median views÷subs; share of ≥100K hits with third-party IP; number of ≥100K hits without IP → share of those from channels ≤12 months.
  - Rows are ordered by the INFERRED rank in Q6.

| Sub-niche | Format | n | Total views | Median | ≥100K | ≥1M | ≥100K hits from ch ≤12 mo / ≤90 d / ≤30 d / <100K subs | ≥1M hits from ch ≤12 mo / <100K subs | Median views÷subs | ≥100K hits with 3rd-party IP | ≥100K no-IP hits (n) → share from ch ≤12 mo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | short | 1068 | 583.8M | 76K | 498 | 182 | 34% / 10% / 2% / 43% | 32% / 32% | 3.28 | 50% | 247 → 33% |
| ALL | long | 418 | 88.7M | 40K | 148 | 15 | 11% / 2% / 1% / 22% | 7% / 0% | 0.49 | 31% | 102 → 7% |
| CHALL_BUT | short | 83 | 34.4M | 32K | 27 | 13 | 7% / 4% / 0% / 26% | 0% / 23% | 2.29 | 11% | 24 → 4% |
| CHALL_BUT | long | 55 | 8.2M | 18K | 14 | 1 | 21% / 0% / 0% / 7% | 0% / 0% | 0.37 | 14% | 12 → 25% |
| HOR_PLAY | short | 45 | 5.1M | 27K | 13 | 0 | 46% / 8% / 0% / 46% | – / – | 2.96 | 8% | 12 → 50% |
| HOR_PLAY | long | 57 | 14.2M | 41K | 20 | 2 | 5% / 0% / 0% / 10% | 50% / 0% | 0.38 | 10% | 18 → 6% |
| KIDS_ANIM_STORY | short | 132 | 97.8M | 282K | 81 | 36 | 56% / 18% / 0% / 44% | 56% / 44% | 4.65 | 85% | 12 → 92% |
| KIDS_ANIM_STORY | long | 9 | 4.7M | 362K | 7 | 2 | 29% / 0% / 0% / 43% | 0% / 0% | 0.64 | 100% | 0 → – |
| SIM_WAR | long | 10 | 15.3M | 170K | 6 | 3 | 17% / 0% / 0% / 17% | 0% / 0% | 1.16 | 0% | 6 → 17% |
| RP_STORY_GAMEPLAY | short | 22 | 8.6M | 49K | 9 | 4 | 11% / 0% / 0% / 33% | 0% / 0% | 2.49 | 22% | 7 → 14% |
| RP_STORY_GAMEPLAY | long | 53 | 17.6M | 149K | 33 | 4 | 6% / 6% / 3% / 21% | 0% / 0% | 0.23 | 39% | 20 → 0% |
| SURV100 | short | 10 | 1.1M | 25K | 4 | 0 | 50% / 0% / 0% / 50% | – / – | 2.07 | 25% | 3 → 33% |
| SURV100 | long | 64 | 7.7M | 47K | 23 | 0 | 0% / 0% / 0% / 17% | – / – | 0.53 | 39% | 14 → 0% |
| BUILD | short | 116 | 33.5M | 32K | 35 | 9 | 26% / 14% / 6% / 40% | 11% / 33% | 1.56 | 3% | 34 → 26% |
| BUILD | long | 20 | 2.5M | 44K | 7 | 0 | 43% / 0% / 0% / 43% | – / – | 0.31 | 43% | 4 → 0% |
| SATISFY_REAL | short | 7 | 8.9M | 3K | 3 | 2 | 33% / 0% / 0% / 67% | 0% / 50% | 12.46 | 0% | 3 → 33% |
| MANHUNT_PVP | short | 45 | 3.6M | 56K | 9 | 0 | 44% / 11% / 11% / 56% | – / – | 10.90 | 11% | 8 → 50% |
| MANHUNT_PVP | long | 36 | 4.9M | 8K | 10 | 1 | 20% / 10% / 0% / 30% | 0% / 0% | 0.89 | 20% | 8 → 12% |
| SKIT_COMEDY | short | 102 | 87.3M | 195K | 59 | 22 | 27% / 7% / 3% / 19% | 32% / 18% | 3.13 | 54% | 27 → 41% |
| SKIT_COMEDY | long | 8 | 1.4M | 86K | 4 | 0 | 25% / 0% / 0% / 50% | – / – | 0.22 | 50% | 2 → 0% |
| SMP | short | 55 | 21.0M | 117K | 28 | 7 | 43% / 14% / 4% / 82% | 43% / 71% | 10.26 | 75% | 7 → 43% |
| SMP | long | 30 | 5.1M | 51K | 13 | 1 | 0% / 0% / 0% / 54% | 0% / 0% | 0.54 | 23% | 10 → 0% |
| HOR_FIC | short | 20 | 169K | 2K | 0 | 0 | – | – | 3.34 | – | 0 → – |
| HOR_FIC | long | 35 | 1.5M | 3K | 4 | 0 | 0% / 0% / 0% / 0% | – / – | 0.98 | 0% | 4 → 0% |
| FACTS_TIPS_NEWS | short | 39 | 12.4M | 29K | 13 | 4 | 31% / 31% / 15% / 46% | 50% / 25% | 1.72 | 0% | 13 → 31% |
| FACTS_TIPS_NEWS | long | 5 | 425K | 3K | 1 | 0 | 0% | – | 0.15 | 0% | 1 → 0% |
| MEMES_CLIPS | short | 239 | 130.8M | 80K | 110 | 32 | 28% / 3% / 1% / 52% | 12% / 31% | 3.37 | 26% | 82 → 26% |
| KIDS_CHOICE_PUZZLE | short | 100 | 109.5M | 475K | 89 | 41 | 33% / 10% / 3% / 40% | 32% / 27% | 2.50 | 88% | 11 → 54% |
| KIDS_CHOICE_PUZZLE | long | 2 | 352K | 176K | 1 | 0 | 100% / 0% / 0% / 0% | – | 1.37 | 0% | 1 → 100% |
| MUSIC_DANCE | short | 40 | 21.3M | 27K | 14 | 9 | 57% / 21% / 0% / 36% | 78% / 33% | 1.51 | 79% | 3 → 67% |
| MUSIC_DANCE | long | 10 | 10K | 78 | 0 | 0 | – | – | 0.35 | – | 0 → – |
| DOC_LORE | long | 5 | 3.4M | 59K | 2 | 1 | 0% | 0% | 0.67 | 50% | 1 → 0% |
| FOOD_FIRST | short | 3 | 3.4M | 83K | 1 | 1 | 0% | 0% | 0.94 | 0% | 1 → 0% |
| FOOD_FIRST | long | 1 | 516K | 516K | 1 | 0 | 0% | – | 0.26 | 100% | 0 → – |
| LP_GENERAL | long | 14 | 923K | 22K | 2 | 0 | 0% | – | 0.69 | 50% | 1 → 0% |
| ART_DRAW | short | 7 | 4.7M | 44K | 3 | 2 | 67% / 0% / 0% / 67% | 100% / 50% | 7.93 | 100% | 0 → – |

- **Format totals (OBSERVED).**
  - Shorts: 1,068 videos, 583.8M views, median 76K.
  - Long-form: 418 videos, 88.7M views, median 40K.
  - ≥100K hits: 498 Shorts and 148 long. ≥1M hits: 182 Shorts and 15 long.
- **RPM-weighted demand (INFERRED from OBSERVED views × OWNER ratio).** Shorts pay about 3–14% of long-form RPM. The OWNER brief says so, citing AIR Media-Tech via [the 2026-11-03 RPM report](../../reports/Ngách%20Minecraft%20RPM%20cao%20bền%20vững.md).
  - Long-equivalent demand = long views + Shorts views × 0.03–0.14 = **106–170M**. Long-form is 83% of that at the low ratio and 52% at the high ratio.
  - By niche (midpoint ratio 0.085, [derived_A_rpm_weighted_demand.csv](data/derived_A_rpm_weighted_demand.csv)): RP_STORY_GAMEPLAY 18.3M, SIM_WAR 15.3M, HOR_PLAY 14.7M, KIDS_ANIM_STORY 13.0M, CHALL_BUT 11.2M, MEMES_CLIPS 11.1M, KIDS_CHOICE_PUZZLE 9.7M, SKIT_COMEDY 8.8M, SURV100 7.7M, SMP 6.8M, BUILD 5.4M, MANHUNT_PVP 5.2M, HOR_FIC 1.5M.
- **Long-form top examples, 7 days (OBSERVED).**
  - Parrot, [10,000 Player Minecraft War: Nether VS Overworld](https://www.youtube.com/watch?v=bHxLy6Qza3M): 7.2M, 2.1 d, 4.45M subs.
  - ProBoiz 95, [Testing Trending Minecraft Scary Myths To See If They Are Real!](https://www.youtube.com/watch?v=ls0FQdzVxko): 6.3M, 6.2 d, 9.41M subs.
  - Beppo, [Achievement = 1 Block](https://www.youtube.com/watch?v=Sv78gB7zi_E): 3.5M, 6.7 d.
  - Sticks, [If Technoblade's Life Was a Movie...](https://www.youtube.com/watch?v=ZGYi_JjKhfE): 3.1M, 3.2 d.
  - Karry Kraft, [This Scary Tree Monster Destroyed Our World in Minecraft..](https://www.youtube.com/watch?v=TFHP1mPdKrY): 1.6M, 5.3 d.
- **The 15-day top long-form videos sit mostly outside the 7-day window (OBSERVED).**
  - Spoke, [10,000 Players Simulate COLD WAR in Minecraft](https://www.youtube.com/watch?v=y5IdSoHdkgg): 13.4M at 11.8 d.
  - Dream, [Minecraft Speedrunner VS 6 Hunters FINALE](https://www.youtube.com/watch?v=g22Z__ShvVY): 13.1M at 14.0 d.
  - Maizen, [SURVIVING in BUS During ZOMBIE APOCALYPSE](https://www.youtube.com/watch?v=UH1HSIN4L20): 4.9M at 9.8 d.
- **Shorts top examples, 7 days (OBSERVED).**
  - lowkiMC, [This feels like a scene from interstellar](https://www.youtube.com/watch?v=Jl-KVNhnMjo): 18.9M, 2.8 d, 97.9K subs.
  - PumpBrine, [Smartest Player VS Dr Donut](https://www.youtube.com/watch?v=4w22UAHpwhE): 12.5M.
  - BlobbyClips, [Minecraft Mods Then vs Now!](https://www.youtube.com/watch?v=7wJa_TnXdwU): 11.5M.
  - Cheesy Animation, [No One Helped Evil JJ…](https://www.youtube.com/watch?v=Rwx6b2ngh5w): 10.2M.
  - darix, [Kpop Head Noob Pro Trap Challenge Part 12](https://www.youtube.com/watch?v=uYhJbAYatv8): 8.0M.

### Inferences
- The search sample is ranked by viewCount, top 50 per keyword. "n" and "≥100K counts" describe what YouTube surfaces at the top, not the whole niche. The niche *median* is the fairer benchmark (CLAUDE.md research policy, OWNER).
- Kids-coded Shorts have very high medians. KIDS_CHOICE_PUZZLE has a 475K median and KIDS_ANIM_STORY 282K, about 6× and 4× the all-Shorts median of 76K. Most of that comes from Maizen/Verity/K-pop-IP fan channels (see Q4).
- Horror demand lives in *gameplay framing* (mods, myths, "something is on my farm"), not in found-footage/ARG fiction labels. HOR_PLAY long-form has a 41K median and 20 videos ≥100K. HOR_FIC long-form has a 2.8K median and 4 videos ≥100K, all from established channels (Bionic 8.9M subs, BeckBroJack 5.5M, Dialko, Vivilly). This qualifies yesterday's report, which ranked "original-IP mystery/horror 15–30 min" first ([RPM report](../../reports/Ngách%20Minecraft%20RPM%20cao%20bền%20vững.md)). The format may still work, but titles and packaging should look like scary survival or gameplay, not "ARG/found footage".

### Gaps
- 7-day views of videos aged <2 days are still climbing. Comparing by age bucket would need a second snapshot. Researcher C appears to have one (`derived_C_snapshot2_growth.csv`), but it was not used here.

## Q3. How much demand goes to new and small channels

### Takeaway
New channels get real Shorts demand but very little long-form demand.
- **Shorts:** 34% of 7-day ≥100K Shorts and 32% of ≥1M Shorts come from channels created ≤12 months ago, and 43% of ≥100K Shorts come from channels with <100K subs.
- **Long-form:** only 11% of ≥100K and 1 of 15 ≥1M videos come from channels ≤12 months old. Only 2% of ≥100K long-form videos come from channels ≤90 days old.
- **Most newcomer-friendly sub-niches:** kids JJ-style animation (56% of ≥100K Shorts from ≤12-month channels), music/dance (57%), SMP clips (43%), horror Shorts (46%), manhunt Shorts (44%) and facts/tips Shorts (31% from ≤90-day channels).
- **Long-form exceptions:** the only original-IP long-form breakouts from young channels are Clooless Gaming (347 d), SirCloaked (346 d), Kit vs The End (37 d), Day Zero (29 d) and Cobweb (267 d) (OBSERVED).

### Cited Findings
- **Aggregate newcomer share (OBSERVED, [derived_A_niche_metrics_7d.csv](data/derived_A_niche_metrics_7d.csv)).** Among the 646 7-day ≥100K hits:
  - Channel ≤12 months old: 29.1%. Shorts 34.5%, long 10.8%.
  - Channel ≤90 days old: 8.2%. Shorts 10.0%, long 2.0%.
  - Channel ≤30 days old: 2.0%. Shorts 2.4%, long 0.7%, i.e. 1 video (MineBraintor's livestream replay).
  - Channel <100K subs: 38.4%. Shorts 43.2%, long 22.3%.
  - Among ≥1M hits, ≤12 months: Shorts 32.4%, long 6.7% (1 of 15). <100K subs: Shorts 31.9%, long 0%.
- **Median views÷subs (OBSERVED).** All Shorts 3.28 and all long-form 0.49. The highest are MANHUNT_PVP Shorts 10.9, SMP Shorts 10.3 and SATISFY_REAL Shorts 12.5 (n=7). Long-form niches all sit at 0.2–1.2, except tiny samples.
- **No-IP newcomer hits, 7 days (OBSERVED, top 30 of 88).** Columns: channel, niche, format, video, age, views, subs, channel age, views÷subs, views÷channel same-format median. "–" means the channel has no upload sample.

| Channel | Niche | Fmt | Video | Age | Views | Subs | Ch age | Views÷subs | Views÷ch median |
|---|---|---|---|---|---|---|---|---|---|
| Headfilter67CookieGuy | KIDS_CHOICE_PUZZLE | short | [which one did you get ft. Jerry in Minecraft #dog](https://www.youtube.com/watch?v=9RV1BTPFoCw) | 6.1 d | 5.9M | 458K | 265 d | 12.8 | 3.0 |
| Wablo | SKIT_COMEDY | short | [Creator just wanted to do his job](https://www.youtube.com/watch?v=BJ1XeW9_6rE) | 4.9 d | 4.3M | 254K | 114 d | 17.0 | 2.3 |
| melZerry | BUILD | short | [Water can build PRESSURE in minecraft??](https://www.youtube.com/watch?v=5dwJxih_if8) | 4.7 d | 4.3M | 26K | 319 d | 164.6 | 31.7 |
| zedarGG | MEMES_CLIPS | short | [DUMB the SOUND](https://www.youtube.com/watch?v=LKdjKUER3aY) | 6.2 d | 3.4M | 232K | 305 d | 14.6 | 66.3 |
| Mine Mythos | MEMES_CLIPS | short | [Bro Crafted Netherite Armor](https://www.youtube.com/watch?v=ow9qGwMrSTk) | 7.0 d | 3.2M | 16K | 169 d | 204.4 | 39.7 |
| CHIRAG FACTO | SKIT_COMEDY | short | [Slither Run with Steve - Funny Animation](https://www.youtube.com/watch?v=xel-UZ5bf1s) | 2.2 d | 2.6M | 26K | 11 d | 100.9 | 13.5 |
| Whitye | FACTS_TIPS_NEWS | short | [Minecraft Mobs Weaknesses !](https://www.youtube.com/watch?v=7D8-j8lFu2s) | 4.0 d | 2.5M | 138K | 88 d | 18.5 | 33.5 |
| Brineycraft | KIDS_ANIM_STORY | short | [Herobrine, I scared my Girlfriend and Bros - Minecraft Animation](https://www.youtube.com/watch?v=KluGoov5yoQ) | 3.4 d | 2.0M | 817K | 340 d | 2.5 | 0.9 |
| Tg Jamal Shorts 44 | KIDS_CHOICE_PUZZLE | short | [What Do You Guys Think Who Will Win](https://www.youtube.com/watch?v=NXCnMP6Em1g) | 3.5 d | 1.8M | 24K | 314 d | 77.0 | 37.2 |
| MaizCr | SKIT_COMEDY | short | [During the Day vs At Night #animation](https://www.youtube.com/watch?v=EkNgf9DDtwM) | 2.4 d | 1.6M | 34K | 162 d | 47.3 | 15.3 |
| Floog | SKIT_COMEDY | short | [larp / #animation #alanbecker](https://www.youtube.com/watch?v=D6br6Dam-rA) | 2.0 d | 1.6M | 1.8K | 324 d | 894.3 | 917.0 |
| MaizCr | KIDS_ANIM_STORY | short | [MaizCR Don't Cross Until the Monster Cars Pass!](https://www.youtube.com/watch?v=Oocx5mNdz0E) | 1.4 d | 1.5M | 34K | 162 d | 44.4 | 14.3 |
| Mochi & Pals | KIDS_CHOICE_PUZZLE | short | [Who can dig down the fastest?](https://www.youtube.com/watch?v=nf9oZPSqhjE) | 2.3 d | 1.4M | 1.1K | 19 d | 1343.8 | 28.2 |
| Verity Verifies MC | FACTS_TIPS_NEWS | short | [How To Use Copper Golems Perfectly...](https://www.youtube.com/watch?v=3U2_rB7SrZ0) | 5.4 d | 1.4M | 1.8K | 9 d | 754.4 | 55.5 |
| Catkin Craft | SMP | short | [How Long Can a Base Survive on 2b2t?](https://www.youtube.com/watch?v=0Cs0T81YOkI) | 7.0 d | 1.3M | 125K | 183 d | 10.6 | 2.5 |
| Clooless Gaming | HOR_PLAY | **long** | [Beating Minecraft With The Phobia Mod](https://www.youtube.com/watch?v=fHGRgKgIbAU) | 5.9 d | 1.2M | 318K | 347 d | 3.8 | 2.5 |
| Rank it Laughs | HOR_PLAY | short | [Top 3 Funniest Minecraft Horror Mod Moments](https://www.youtube.com/watch?v=9ULv8twx2ac) | 6.1 d | 973K | 262K | 252 d | 3.7 | 4.8 |
| CHAnimationsClips | CHALL_BUT | short | [NOOB vs SADAKO&ALEX in Never Give Up Mining Challenge](https://www.youtube.com/watch?v=C22VTFwwexo) | 5.3 d | 834K | 92K | 60 d | 9.0 | 5.6 |
| parsamehrj | BUILD | short | [I Built a Farm in Minecraft That Automatically Collects…](https://www.youtube.com/watch?v=njGzqtWPgAk) | 6.0 d | 828K | 1.1K | 30 d | 767.1 | 44.6 |
| Clooless Gaming | CHALL_BUT | **long** | [Beating Minecraft With The Disabilities Mod](https://www.youtube.com/watch?v=QZ-cOjajyYg) | 1.9 d | 821K | 318K | 347 d | 2.6 | 1.7 |
| Cobweb | MANHUNT_PVP | **long** | [Beating Players with PvP kits only I know how to use](https://www.youtube.com/watch?v=X9ZXFM5a6jg) | 6.0 d | 579K | 42K | 267 d | 13.8 | 3.8 |
| Mob Academy | KIDS_ANIM_STORY | short | [Monster School: Trick or Treat (Halloween Minecraft Logic)](https://www.youtube.com/watch?v=RhoKbtVwLXc) | 4.7 d | 114K | 369 | 33 d | 309.0 | 43.1 |
| Spoon Gaming YT | KIDS_ANIM_STORY | short | [STEVE & ALEX HAVE A BABY?! / MINECRAFT FAMILY STORY!](https://www.youtube.com/watch?v=DePOj2iQlM4) | 1.3 d | 276K | 469 | 318 d | 587.7 | 196.0 |
| SohilXCraft | SKIT_COMEDY | short | [Minecraft Villagers vs Pillagers](https://www.youtube.com/watch?v=B_xrdABjn48) | 4.2 d | 254K | 347 | 33 d | 731.5 | 206.4 |
| MineZox | MANHUNT_PVP | short | [HE THOUGHT HE FOUND ME! (Minecraft Hide and Seek)](https://www.youtube.com/watch?v=O-J9Tmi50m4) | 2.2 d | 311K | 208 | 3 d | 1495.8 | 1994.4 |

- **Long-form original-IP breakouts from ≤12-month channels, 0–15 days (OBSERVED, `E.pkl` query in `rank.py` logic). 11 videos.**
  - Clooless Gaming (347 d), "Beating Minecraft With The Phobia Mod": 1.21M, 59 min, ×3.8 subs, ×2.5 median.
  - SirCloaked (346 d, 141K subs), [Something On My Farm Wants Me Dead...](https://www.youtube.com/watch?v=VYFy1FN7-tk): 956K, 8.2 d, 18 min, ×6.8 subs, ×2.2 median.
  - Kit vs The End (37 d, 9.7K subs), [Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship… (Full Movie)](https://www.youtube.com/watch?v=xdj5PL0t61k): 673K, 10.0 d, 73 min, **×69 subs, ×34 channel median**.
  - Day Zero (29 d, 13.9K subs), [I Survived 100 Days in a DEADLY OUTBREAK in Minecraft](https://www.youtube.com/watch?v=eAqPRLb9JQg): 370K, 11.1 d, 40 min, ×26.6 subs.
  - Cobweb (267 d), "Beating Players with PvP kits only I know how to use": 579K, 9 min.
  - Niz unseen (254 d), [Find the Mistake in These Minecraft Builds!](https://www.youtube.com/watch?v=WmfqzjWBKjg): 289K, 20 min.
  - CashMovies (83 d), [NOOB vs PRO TREEHOUSE in Minecraft…](https://www.youtube.com/watch?v=avr9MoPaq-s): 171K, 182 min.
  - Also on the list: Ding & Doge (300 d), BionicTV (258 d), imKaiL00L (203 d). All are 144–156K and below their channel median.
- **Long-form 7-day hits from <100K-sub channels are mostly Maizen fan channels (OBSERVED).** Examples:
  - Ligabka, "MAIZEN - JJ and LOVE QUEEN": 726K, 69K subs.
  - Cody Toon (63 d), "JJ and Mikey in ALL LOVE STORY PIT LORD VERITY & JERRY DOG & LIGHTING MCQUEEN": 641K.
  - Banazen Craft (9 d, 4.3K subs), [JJ and Mikey Grow SECRET VERITY from Seeds](https://www.youtube.com/watch?v=uah6ikSydJ8): 394K.
  - Original-IP exceptions:
    - GupMC (78K subs), [Minecraft Mob Slayers: THE MOVIE](https://www.youtube.com/watch?v=AA4tn0Ts9_k): 592K, 78 min.
    - Jaiz (35K), [I Designed a Mod to Torture Speedrunners](https://www.youtube.com/watch?v=FqvK2EWQC00): 567K.
    - Iron Studio Minecraft Animation (20.5K), [The Poor Axolotl's Road to Success](https://www.youtube.com/watch?v=PwYF6Nv8uIk): 154K, 8.6 min.
    - Shulker Cat (23K), [Minecraft 100 Days Deserted Island But It's Cats (Full Episode)](https://www.youtube.com/watch?v=Uk5MK7RzCtI): 119K.

### Inferences
- "Channel ≤12 months" over-counts true newcomers. Several apparent newcomers are second channels of established creators: CashMovies (Cash), Niz unseen (Niz), BionicTV (Bionic), YGG EXTRAS, zedarextra, Joeysaf Clips. Their success is not evidence that a cold-start channel can win (INFERRED; the API does not expose owner identity).
- For a cold-start original-IP studio, the strongest evidence is **Kit vs The End** (37 d, ×34 median, 73-min zombie-outbreak "Full Movie") and **Day Zero** (29 d, 40-min "100 Days DEADLY OUTBREAK"). Both are scripted-survival long-form with an outbreak/horror hook. Together with SirCloaked and Clooless Gaming they suggest "survival + threat" long-form is the one long-form lane where young channels broke 300K–1.2M in under 2 weeks. That is 4 cases, so treat it as an existence proof, not a rate.
- In Shorts, tiny accounts reached 100K–1.4M on original premises: Mochi & Pals, Mob Academy, SohilXCraft, parsamehrj, Verity Verifies MC, MineZox. So Shorts are a realistic discovery engine for Bin/Bo/Zu.

### Gaps
- Retention, CTR, traffic source and audience age are not in the public API. Why newcomer long-form worked cannot be measured here.
- Second-channel status needs a manual "About"/links check (not done; no browsing allowed in this task).

## Q4. How much of each sub-niche depends on third-party characters (we can only use original IP)

### Takeaway
**46% of all 7-day ≥100K hits use third-party characters in the title** (Shorts 50%, long 31%) (OBSERVED). By family, the hit counts are Maizen JJ/Mikey 126, creators/Dream/SMP 81, other franchises 57, Verity 57 and K-pop Demon Hunters 18.
- **IP-heavy niches.** In the kids-coded cells, third-party IP is in **85% of KIDS_ANIM_STORY Shorts hits, 88% of KIDS_CHOICE_PUZZLE Shorts hits, 79% of MUSIC_DANCE, 100% of ART_DRAW and 75% of SMP Shorts**.
- **Largely original niches.** Original IP dominates horror mods (91% no-IP), challenges (88%), build (90%), player simulations (100%), facts/tips (100%) and horror fiction (100%).
- **Kids animation without IP.** After removing IP videos, kids animation keeps only 12 ≥100K hits in 7 days, but 11 of those 12 are from ≤12-month channels.

### Cited Findings
- **IP family counts among 646 7-day ≥100K hits (OBSERVED, `ip3p` title flag).** maizen_jj_mikey 126, creators_dream_smp_etc 81, other_franchise 57, verity 57, kpop_demon_hunters 18, poppy_playtime 5, sprunki 1, italian_brainrot 1, skibidi_toilet 1. One video can carry several flags.
- **Share of each niche's ≥100K hits with third-party IP, all formats (OBSERVED).**
  - Mostly third-party: ART_DRAW 100%, KIDS_CHOICE_PUZZLE 87%, KIDS_ANIM_STORY 86%, MUSIC_DANCE 79%, SMP 59%, SKIT_COMEDY 54%.
  - Middle: SURV100 37%, RP_STORY_GAMEPLAY 36%, MEMES_CLIPS 25%, MANHUNT_PVP 16%.
  - Mostly original: CHALL_BUT 12%, BUILD 10%, HOR_PLAY 9%, SIM_WAR / FACTS / HOR_FIC / SATISFY_REAL 0%.
- **Newcomer share with and without IP (OBSERVED; "no-IP" = ≥100K hits with no title flag).**

| Cell | All ≥100K hits (n) → share from ≤12-mo channels | No-IP ≥100K hits (n) → share from ≤12-mo channels |
| --- | --- | --- |
| ALL Shorts | 498 → 34% | 247 → 33% |
| ALL long | 148 → 11% | 102 → 7% |
| KIDS_ANIM_STORY Shorts | 81 → 56% | 12 → 92% |
| KIDS_CHOICE_PUZZLE Shorts | 89 → 33% | 11 → 54% |
| SKIT_COMEDY Shorts | 59 → 27% | 27 → 41% |
| MEMES_CLIPS Shorts | 110 → 28% | 82 → 26% |
| BUILD Shorts | 35 → 26% | 34 → 26% |
| HOR_PLAY Shorts | 13 → 46% | 12 → 50% |
| HOR_PLAY long | 20 → 5% | 18 → 6% |
| SURV100 long | 23 → 0% | 14 → 0% (7 d window) |
| RP_STORY_GAMEPLAY long | 33 → 6% | 20 → 0% |

- **Original-IP kids/animation examples, 7 days (OBSERVED).**
  - Mob Academy (33 d, 369 subs), "Monster School: Trick or Treat": 114K.
  - Spoon Gaming YT, "STEVE & ALEX HAVE A BABY?!": 276K on 469 subs.
  - MaizCr (162 d), "MaizCR Don't Cross Until the Monster Cars Pass!": 1.53M. The channel name echoes Maizen, but the title has no JJ/Mikey.
  - Rk_offical_cartoon, [Shortest Sad Story... (Minecraft Animation)](https://www.youtube.com/watch?v=HE_iXfy7uVI): 387K.
  - ZomCraft Animation (56 d, 8.3K subs), [Monster School: Will You Try This Formula?](https://www.youtube.com/watch?v=DnoLULhbqX0): 167K at 0.8 d. Its other Monster School episodes mix JJ in.
  - Mochi & Pals (19 d), "Who can dig down the fastest?": 1.42M.
- **IP-dependent hits that look newcomer-friendly but are off-limits for us (OBSERVED).**
  - Cheesy Animation (131 d), "No One Helped Evil JJ…": 10.2M.
  - Sleepy Mikey! (158 d), "No One Helped Dark JJ…": 13.8M at 14.1 d.
  - darix "Kpop Head Noob Pro Trap Challenge" series: 8.0M / 6.7M / 4.2M.
  - BH_Toon (209 d), "NEW Verity's Bridge Challenge: Sonic vs Sonic EXE": 13.8M.
  - ClayBoom (31 d, 7.9K subs), "JJ, Mikey & Steve Funny Dance": 4.26M.
  - Banazen Craft (9 d), "JJ and Mikey Grow SECRET VERITY": 394K long-form.

### Inferences
- The "kids animation is where newcomers break in" signal is mostly a **Maizen fan-animation signal**. Remove JJ/Mikey/Verity/K-pop titles and the cell shrinks from 81 to 12 ≥100K Shorts in 7 days. The newcomer share of that remainder is very high (92%), though. INFERRED: original-IP kids animation is under-supplied rather than undemanded, and 12 hits/week is the realistic ceiling signal, not 81.
- Herobrine, Steve, Alex, villagers and mobs are Mojang game characters, not competitor IP. Several original-IP breakouts lean on them: Brineycraft, Spoon Gaming, OLD Legends, Mob Academy. Usage terms are a separate legal question (not assessed here).

### Gaps
- The regex will miss lesser-known third-party characters (e.g. "Jerry Dog", "Lord Obesity", "emojicatgirl67", "Dr Donut"), whose origin is unclear. It may also flag a creator's own character on a fan-named channel. Shares are lower bounds for IP dependence.
- Thumbnails were not inspected. A video can feature JJ/Mikey visually with a neutral title.

## Q5. Leaders per sub-niche, their outliers, and first-5-day explosions

### Takeaway
Most sub-niches are led by one or two channels that take 25–50% of the niche's 7-day views. Examples: Stonecraft Studios 38% of choice/puzzle, PumpBrine 47% of skits, Joeysaf 28% of challenges, ProBoiz 95 32% of horror mods, Parrot 47% of simulations. Only 15 of the 116 leader slots are channels created ≤12 months ago, and outside the kids/IP cells they are Shorts formats: Wablo, melZerry, Whitye, HeldIsHere, Headfilter67CookieGuy, Clooless Gaming. The upload sample shows leaders routinely post 30-day outliers at **10–100× their own median**. The strongest **first-5-day explosions** all come from tiny or young accounts: lowkiMC ×565 median, ClayBoom ×161, Mob Academy ×43, SohilXCraft ×206, MineBraintor's TNT livestreams ×565–1,075, JJ AND MILKY long-form ×41–82 (OBSERVED).

### Cited Findings
- **Top 3 leaders per sub-niche by 7-day views in that niche (OBSERVED, [derived_A_leaders_by_niche.csv](data/derived_A_leaders_by_niche.csv), top 6 per niche in file).** Columns: niche, rank, channel, 7-day views in the niche (share of niche), subs, channel age, channel median from uploads.csv, top video in the window.

| Niche | # | Channel | 7-d views in niche (share) | Subs | Ch age | Channel median (uploads.csv) | Top video in window |
|---|---|---|---|---|---|---|---|
| CHALL_BUT | 1 | Joeysaf | 12.0M (28%) | 489K | 3765 d | Shorts 2.6M / long 102K | [Minecraft But Breaking One Block Changes Them All](https://www.youtube.com/watch?v=t75SLaZKWSA) — 2.8M, 1.9 d, short |
| CHALL_BUT | 2 | Joeysaf Clips | 3.5M (8%) | 40K | 1515 d | no upload sample | [The Biggest Bucket In Minecraft](https://www.youtube.com/watch?v=c4hlCcskZcY) — 3.5M, 6.2 d, short |
| CHALL_BUT | 3 | Beppo | 3.5M (8%) | 2.4M | 3767 d | no upload sample | [Achievement = 1 Block](https://www.youtube.com/watch?v=Sv78gB7zi_E) — 3.5M, 6.7 d, long |
| HOR_PLAY | 1 | ProBoiz 95 | 6.3M (32%) | 9.4M | 2390 d | no upload sample | [Testing Trending Minecraft Scary Myths…](https://www.youtube.com/watch?v=ls0FQdzVxko) — 6.3M, 6.2 d, long |
| HOR_PLAY | 2 | Clooless Gaming | 1.2M (6%) | 318K | 348 d | long 484K | [Beating Minecraft With The Phobia Mod](https://www.youtube.com/watch?v=fHGRgKgIbAU) — 1.2M, 5.9 d, long |
| HOR_PLAY | 3 | Rank it Laughs | 973K (5%) | 262K | 253 d | Shorts 204K | [Top 3 Funniest Minecraft Horror Mod Moments](https://www.youtube.com/watch?v=9ULv8twx2ac) — 973K, 6.1 d, short |
| KIDS_ANIM_STORY | 1 | Cheesy Animation | 10.2M (10%) | 189K | 131 d | Shorts 499K | [No One Helped Evil JJ…](https://www.youtube.com/watch?v=Rwx6b2ngh5w) — 10.2M, 6.2 d, short (IP) |
| KIDS_ANIM_STORY | 2 | Minoku Animation | 7.2M (7%) | 295K | 517 d | no upload sample | [Baby JJ's New Friends!](https://www.youtube.com/watch?v=YZnOpFPE-gQ) — 3.1M, 3.8 d, short (IP) |
| KIDS_ANIM_STORY | 3 | Mikey Crazy | 6.9M (7%) | 85K | 143 d | Shorts 234K / long 5K | [Dark JJ Dog STOLE Their BODY PARTS!](https://www.youtube.com/watch?v=e9H1xdYXOhU) — 2.7M, 6.0 d, short (IP) |
| SIM_WAR | 1 | Parrot | 7.2M (47%) | 4.5M | 2260 d | no upload sample | [10,000 Player Minecraft War: Nether VS Overworld](https://www.youtube.com/watch?v=bHxLy6Qza3M) — 7.2M, 2.1 d, long |
| SIM_WAR | 2 | FlameFrags | 4.8M (31%) | 3.1M | 3255 d | no upload sample | [10,000 VS 10,000 Player Minecraft War](https://www.youtube.com/watch?v=ZT-k42SC7L0) — 4.8M, 3.1 d, long |
| SIM_WAR | 3 | SpeedSilver | 2.3M (15%) | 4.0M | 2148 d | no upload sample | [1000 Players Simulate Minecraft's Deadliest Containment Zone...](https://www.youtube.com/watch?v=KnlAF_djhdc) — 2.3M, 3.9 d, long |
| RP_STORY_GAMEPLAY | 1 | Cash | 3.9M (15%) | 11.8M | 1494 d | no upload sample | [Help Cash's Dog!](https://www.youtube.com/watch?v=TpqDLa28e78) — 2.0M, 6.2 d, short |
| RP_STORY_GAMEPLAY | 2 | Karry Kraft | 2.7M (10%) | 1.8M | 1571 d | no upload sample | [This Scary Tree Monster Destroyed Our World in Minecraft..](https://www.youtube.com/watch?v=TFHP1mPdKrY) — 1.6M, 5.3 d, long |
| RP_STORY_GAMEPLAY | 3 | Aphmau | 2.5M (9%) | 25.4M | 5195 d | no upload sample | [The VAMPIRE LORD KIDNAPPED Me: The MOVIE!](https://www.youtube.com/watch?v=81tl9y0wt7w) — 901K, 2.9 d, long |
| SURV100 | 1 | Ryguyrocky | 621K (7%) | 3.9M | 6407 d | no upload sample | [I Survived 100 Days as a Necromancer in Minecraft](https://www.youtube.com/watch?v=--0KP-bA0p4) — 621K, 3.3 d, long |
| SURV100 | 2 | Luke TheNotable | 614K (7%) | 4.9M | 6575 d | no upload sample | [100 Days - [SCARY MINECRAFT]](https://www.youtube.com/watch?v=ZlfSeR0v-lo) — 614K, 4.0 d, long |
| SURV100 | 3 | ohnepixel raw | 603K (7%) | 1.4M | 1915 d | no upload sample | [Can I Beat Minecraft Hardcore with VERITY](https://www.youtube.com/watch?v=rX5cppOVzyE) — 603K, 0.6 d, long (IP) |
| BUILD | 1 | wykull | 4.8M (13%) | 253K | 3333 d | Shorts 628K / long 48K | [Building a REALISTIC Soccer Goal in Minecraft](https://www.youtube.com/watch?v=IM9pZSeOwOw) — 2.0M, 5.3 d, short |
| BUILD | 2 | melZerry | 4.3M (12%) | 26K | 319 d | Shorts 135K | [Water can build PRESSURE in minecraft??](https://www.youtube.com/watch?v=5dwJxih_if8) — 4.3M, 4.7 d, short |
| BUILD | 3 | Midmysticx | 3.3M (9%) | 2.2M | 2390 d | no upload sample | [NEVER build FULLY out of COPPER...](https://www.youtube.com/watch?v=_EDGsXxTqIA) — 3.3M, 3.2 d, short |
| MANHUNT_PVP | 1 | FroggyDude Gaming | 1.2M (14%) | 593K | 1401 d | no upload sample | [FroggyDude VS Grox MANHUNT](https://www.youtube.com/watch?v=QBzI4ENJw5g) — 1.2M, 2.2 d, long |
| MANHUNT_PVP | 2 | Feinberg Sucks | 744K (9%) | 162K | 1755 d | no upload sample | [8 pro speedrunners VS Minecraft's worst seeds](https://www.youtube.com/watch?v=2FCncSg7cR4) — 744K, 6.7 d, long |
| MANHUNT_PVP | 3 | Cobweb | 579K (7%) | 42K | 268 d | Shorts 9K / long 153K | [Beating Players with PvP kits only I know how to use](https://www.youtube.com/watch?v=X9ZXFM5a6jg) — 579K, 6.0 d, long |
| SKIT_COMEDY | 1 | PumpBrine | 41.3M (47%) | 100K | 449 d | Shorts 313K | [Smartest Player VS Dr Donut](https://www.youtube.com/watch?v=4w22UAHpwhE) — 12.5M, 6.1 d, short |
| SKIT_COMEDY | 2 | BlobbyClips | 11.5M (13%) | 2.8M | 3286 d | Shorts 11.5M | [Minecraft Mods Then vs Now!](https://www.youtube.com/watch?v=7wJa_TnXdwU) — 11.5M, 4.1 d, short |
| SKIT_COMEDY | 3 | Wablo | 9.0M (10%) | 254K | 115 d | Shorts 1.9M / long 2.4M | [Creator just wanted to do his job](https://www.youtube.com/watch?v=BJ1XeW9_6rE) — 4.3M, 4.9 d, short |
| SMP | 1 | Audio Mansion | 3.0M (11%) | 48K | 991 d | no upload sample | [Technoblade core part 4](https://www.youtube.com/watch?v=FEXoI1HfYI8) — 3.0M, 5.7 d, short (IP) |
| SMP | 2 | nixil | 2.9M (11%) | 33K | 686 d | no upload sample | [Jesus in 2b2t's spawn update](https://www.youtube.com/watch?v=3is1ebirAXQ) — 2.9M, 5.9 d, short |
| SMP | 3 | HeldIsHere | 1.5M (6%) | 2.7K | 46 d | Shorts 60K | [Spoke Is Cooked / Unstable SMP](https://www.youtube.com/watch?v=q9BzhyI0IfQ) — 1.5M, 6.2 d, short (IP) |
| HOR_FIC | 1 | Bionic | 633K (39%) | 8.9M | 4381 d | no upload sample | [3 idiots vs The Broken Script](https://www.youtube.com/watch?v=25tihyuEO6g) — 633K, 4.8 d, long |
| HOR_FIC | 2 | BeckBroJack | 229K (14%) | 5.5M | 5398 d | no upload sample | ["BROKEN SCRIPT" (zalgo title)](https://www.youtube.com/watch?v=Ug_5r3cKIRY) — 229K, 4.0 d, long |
| HOR_FIC | 3 | Dialko | 193K (12%) | 119K | 1905 d | no upload sample | [The Creepypastas of Old Minecraft](https://www.youtube.com/watch?v=uvXEwWQgMRY) — 193K, 4.0 d, long |
| FACTS_TIPS_NEWS | 1 | Whitye | 2.6M (20%) | 138K | 88 d | Shorts 76K | [Minecraft Mobs Weaknesses !](https://www.youtube.com/watch?v=7D8-j8lFu2s) — 2.5M, 4.0 d, short |
| FACTS_TIPS_NEWS | 2 | TuxeBro (TBroz15) | 2.4M (19%) | 100K | 774 d | no upload sample | [Secret Underground Bases in Minecraft Create Mod be like:](https://www.youtube.com/watch?v=nqW_RgAXNEM) — 2.4M, 6.1 d, short |
| FACTS_TIPS_NEWS | 3 | camman18 | 2.2M (17%) | 11.4M | 2040 d | Shorts 4.4M | [SNOW BRICKS HAVE BEEN ADDED TO MINECRAFT!](https://www.youtube.com/watch?v=wuMmOolFhqA) — 2.2M, 6.2 d, short |
| MEMES_CLIPS | 1 | lowkiMC | 18.9M (14%) | 98K | 683 d | Shorts 33K | [This feels like a scene from interstellar](https://www.youtube.com/watch?v=Jl-KVNhnMjo) — 18.9M, 2.8 d, short |
| MEMES_CLIPS | 2 | BlockerLocker | 6.6M (5%) | 293K | 1736 d | no upload sample | [The Perfect Pearl Throw (totally first try)](https://www.youtube.com/watch?v=G79qPgG8NvI) — 4.6M, 6.5 d, short |
| MEMES_CLIPS | 3 | Sticky Spawn | 6.5M (5%) | 97K | 1987 d | no upload sample | [Happy little fellas](https://www.youtube.com/watch?v=JQCrn203IdM) — 6.5M, 6.2 d, short |
| KIDS_CHOICE_PUZZLE | 1 | Stonecraft Studios | 42.2M (38%) | 5.9M | 1398 d | Shorts 1.7M | [1 or 2: Wall-Playing Jj sister Reaction](https://www.youtube.com/watch?v=q_N23LHqAnE) — 5.5M, 5.8 d, short (IP) |
| KIDS_CHOICE_PUZZLE | 2 | darix | 9.9M (9%) | 25K | 3919 d | Shorts 152K | [Kpop Head Noob Pro Trap Challenge Part 12](https://www.youtube.com/watch?v=uYhJbAYatv8) — 8.0M, 7.0 d, short (IP) |
| KIDS_CHOICE_PUZZLE | 3 | Headfilter67CookieGuy | 5.9M (5%) | 458K | 266 d | Shorts 1.9M / long 276K | [which one did you get ft. Jerry in Minecraft #dog](https://www.youtube.com/watch?v=9RV1BTPFoCw) — 5.9M, 6.1 d, short |
| MUSIC_DANCE | 1 | Minecraft Sea | 8.1M (38%) | 249K | 302 d | Shorts 652K | [Dancing Like Different Animals Backstage](https://www.youtube.com/watch?v=h69NvBvgPj8) — 4.2M, 2.8 d, short |
| MUSIC_DANCE | 2 | ClayBoom | 4.3M (20%) | 7.9K | 31 d | Shorts 26K | [JJ, Mikey & Steve Funny Dance in Minecraft](https://www.youtube.com/watch?v=pDvFg4rsWoU) — 4.3M, 2.0 d, short (IP) |
| MUSIC_DANCE | 3 | Ender Frame | 3.2M (15%) | 106K | 134 d | Shorts 641K | [Musical Instrumental Battle - MAIZEN Minecraft Animation](https://www.youtube.com/watch?v=0q0lg_IyLNk) — 1.6M, 1.8 d, short (IP) |
| DOC_LORE | 1 | Sticks | 3.1M (92%) | 1.2M | 3733 d | no upload sample | [If Technoblade's Life Was a Movie...](https://www.youtube.com/watch?v=ZGYi_JjKhfE) — 3.1M, 3.2 d, long (IP) |
| FOOD_FIRST | 1 | Nolan | 3.3M (85%) | 3.5M | 1758 d | no upload sample | [I Tried Every Minecraft Food!](https://www.youtube.com/watch?v=41cbKN_LHXA) — 3.3M, 6.1 d, short |
| SATISFY_REAL | 1 | Craft Lab3D | 6.5M (73%) | 196K | 1050 d | no upload sample | [Minecraft Steve vs Death Factory](https://www.youtube.com/watch?v=uiLAXLyBwlY) — 6.5M, 4.4 d, short |
| ART_DRAW | 1 | AnimeMine TKM | 2.6M (54%) | 221K | 294 d | Shorts 205K | [Help JJ Draw Verity](https://www.youtube.com/watch?v=i11zk9qSheY) — 2.6M, 6.2 d, short (IP) |

- **Coverage of the upload sample (OBSERVED).** Only 38 of the 116 leader slots have an upload sample in `uploads.csv`. The collector sampled the top-30 by search views plus new channels, not per-niche leaders. Big long-form leaders (Parrot, ProBoiz 95, Cash, Aphmau, Ryguyrocky…) have **no channel median** in this dataset.
- **Leader outliers in the last 30 days (OBSERVED, [derived_A_leader_outliers_30d.csv](data/derived_A_leader_outliers_30d.csv), 587 rows; rule: age ≤30 d and views ≥3× channel same-format median or ≥ subs). Two strongest per channel.** Columns: channel, niche, video, age, format, views, subs, views÷subs, channel same-format median, views÷median, IP.

| Channel | Niche | Video | Age | Fmt | Views | Subs | ÷subs | Ch median | ÷median | IP |
|---|---|---|---|---|---|---|---|---|---|---|
| MineBraintor | MANHUNT_PVP | [Minecraft TNT Blast IN VILLAGE](https://www.youtube.com/watch?v=IdwH1fbtOkc) | 5.9 d | long (live) | 982K | 1.9K | 525 | 914 | 1075 | brainrot channel |
| lowkiMC | MEMES_CLIPS | [Redstone is more useful than ever](https://www.youtube.com/watch?v=Dg8Zp56TgSY) | 7.1 d | short | 3.4M | 98K | 35 | 33K | 103 | none |
| ClayBoom | MUSIC_DANCE | [The Security Guard Be Laughing at My Ugly Face](https://www.youtube.com/watch?v=xuj0XTcp9ac) | 18.3 d | short | 4.1M | 7.9K | 517 | 26K | 153 | none |
| Verity Verifies MC | FACTS_TIPS_NEWS | [How To Breed Horses Perfectly...](https://www.youtube.com/watch?v=K7xFyRmxoB0) | 4.5 d | short | 1.7M | 1.8K | 933 | 24K | 69 | none (name only) |
| darix | KIDS_CHOICE_PUZZLE | [Kpop Head Noob Pro Trap Challenge Part 3](https://www.youtube.com/watch?v=sbEISEco27M) | 12.2 d | short | 6.7M | 25K | 267 | 152K | 44 | kpop |
| PumpBrine | SKIT_COMEDY | [Smartest Player VS Smartest Liar](https://www.youtube.com/watch?v=hAWQudxJvFU) | 9.6 d | short | 4.0M | 100K | 40 | 313K | 12.7 | none |
| melZerry | BUILD | [If you try to fly to the other side of the RING WORLD.](https://www.youtube.com/watch?v=1BZ9WsSCVUs) | 11.1 d | short | 4.9M | 26K | 187 | 135K | 36 | none |
| Whitye | FACTS_TIPS_NEWS | [What happens if we sleep on a BED and a STRAW BED at the EXACT same time](https://www.youtube.com/watch?v=NSnW6uoocuI) | 12.0 d | short | 1.9M | 138K | 13.8 | 76K | 24.9 | none |
| BH_Toon | KIDS_CHOICE_PUZZLE | [NEW Verity's Bridge Challenge: Sonic vs Sonic EXE](https://www.youtube.com/watch?v=bXL7f2c_rYw) | 21.6 d | short | 13.8M | 352K | 39 | 433K | 32 | verity, Sonic |
| Sticki Crew | SATISFY_REAL | [Can I Bake a Minecraft Cake IRL?](https://www.youtube.com/watch?v=FsEeUvaHkQ4) | 19.2 d | short | 3.3M | 66K | 50 | 115K | 29 | none |
| Mikey Crazy | KIDS_ANIM_STORY | [JJ SAVES Animals from a TSUNAMI!](https://www.youtube.com/watch?v=MithTcX-Mb8) | 12.9 d | short | 6.7M | 85K | 79 | 234K | 29 | maizen |
| wykull | BUILD | [Making a REALISTIC Basketball Hoop in Minecraft](https://www.youtube.com/watch?v=L5U1hAWXUDs) | 7.3 d | short | 14.3M | 253K | 56 | 628K | 22.8 | none |
| wykull | BUILD | [The BEST way to build Doors in Minecraft](https://www.youtube.com/watch?v=FYjzXdEA_94) | 22.3 d | short | 11.6M | 253K | 46 | 628K | 18.4 | none |
| Cheesy Animation | KIDS_ANIM_STORY | [No One Helped Evil JJ…](https://www.youtube.com/watch?v=Rwx6b2ngh5w) | 6.2 d | short | 10.2M | 189K | 54 | 499K | 20.5 | maizen |
| Wablo | SKIT_COMEDY | [I found verity's weakness](https://www.youtube.com/watch?v=4rxNsYwsfmQ) | 15.8 d | short | 20.3M | 254K | 80 | 1.9M | 10.7 | verity |
| Wablo | SKIT_COMEDY | [There is an imposter in my house](https://www.youtube.com/watch?v=BIp5kzK-axs) | 22.9 d | short | 16.1M | 254K | 63 | 1.9M | 8.5 | none |
| アシュch | SKIT_COMEDY | [Minecraft's Most Satisfying Moments (Compilation)](https://www.youtube.com/watch?v=rNbHC6BalS4) | 11.2 d | **long** | 1.1M | 455K | 2.3 | 112K | 9.4 | none |
| Sleepy Mikey! | KIDS_ANIM_STORY | [No One Helped Dark JJ…](https://www.youtube.com/watch?v=9Klhof7JJIw) | 14.1 d | short | 13.8M | 756K | 18.2 | 2.5M | 5.5 | maizen |
| BlobbyClips | SKIT_COMEDY | [When Mobs Get Smart!](https://www.youtube.com/watch?v=4O-1iZb1Wz4) | 18.0 d | short | 50.1M | 2.8M | 17.7 | 11.5M | 4.3 | none |
| Joeysaf | CHALL_BUT | [Minecraft But Every Basic Rule Is Reversed](https://www.youtube.com/watch?v=gNosQvKuGLA) | 26.9 d | short | 6.9M | 489K | 14.2 | 2.6M | 2.7 | none |
| Clooless Gaming | HOR_PLAY | [Trying To Survive A Modded Minecraft Zombie Apocalypse](https://www.youtube.com/watch?v=n06Hx1wLgfY) | 22.9 d | **long** | 883K | 318K | 2.8 | 484K | 1.8 | none |
| Cobweb | MANHUNT_PVP | [Beating Players with PvP kits only I know how to use](https://www.youtube.com/watch?v=X9ZXFM5a6jg) | 6.0 d | **long** | 579K | 42K | 13.8 | 153K | 3.8 | none |
| camman18 | FACTS_TIPS_NEWS | [i before e except after c…](https://www.youtube.com/watch?v=acvo9GuIU1c) | 23.2 d | short | 12.4M | 11.4M | 1.1 | 4.4M | 2.8 | none |

- **First-5-day explosions (OBSERVED, [derived_A_explosive_first5d.csv](data/derived_A_explosive_first5d.csv)).**
  - Rule: an upload aged 0.5–5 d with ≥50K views qualifies if either (a) views ≥2× the channel's same-format median, or (b) views/day ≥3× the channel's median views/day for same-format uploads aged 3–30 d.
  - Restricted to channels whose search videos are mostly English: 398 rows (364 Shorts, 34 long). Off-topic rows are excluded below.
  - Columns: channel, niche, video, age, format, views, views/day vs channel norm (×ratio), views÷median, subs, channel age, IP.

| Channel | Niche | Video | Age | Fmt | Views | Views/day vs ch norm | ÷median | Subs | Ch age | IP |
|---|---|---|---|---|---|---|---|---|---|---|
| lowkiMC | MEMES_CLIPS | [This feels like a scene from interstellar](https://www.youtube.com/watch?v=Jl-KVNhnMjo) | 2.8 d | short | 18.9M | 6.8M vs 2.2K (×3107) | 565 | 98K | 683 d | Interstellar ref |
| ClayBoom | MUSIC_DANCE | [JJ, Mikey & Steve Funny Dance](https://www.youtube.com/watch?v=pDvFg4rsWoU) | 2.0 d | short | 4.3M | 2.1M vs 1.4K (×1547) | 161 | 7.9K | 31 d | maizen |
| Mob Academy | KIDS_ANIM_STORY | [Monster School: Trick or Treat](https://www.youtube.com/watch?v=RhoKbtVwLXc) | 4.7 d | short | 114K | 24K vs 25 (×952) | 43 | 369 | 33 d | none |
| OLD Legends 360 | KIDS_ANIM_STORY | [Herobrine Sir's Death / Monster School Sad Story](https://www.youtube.com/watch?v=lBgA2rtLaug) | 2.6 d | short | 264K | 102K vs 112 (×907) | 192 | 2.2K | 69 d | none |
| SohilXCraft | SKIT_COMEDY | [Minecraft Villagers vs Pillagers](https://www.youtube.com/watch?v=B_xrdABjn48) | 4.2 d | short | 254K | 60K vs 89 (×680) | 206 | 347 | 33 d | none |
| Beazle | MEMES_CLIPS | [Newest oldest trick in the book](https://www.youtube.com/watch?v=hDoxpvKPwCA) | 2.1 d | short | 2.2M | 1.1M vs 2.3K (×474) | 246 | 8.4K | 737 d | none |
| Mrjunaid Short | BUILD | [Minecraft game play with animation](https://www.youtube.com/watch?v=UiRv3wqFuIs) | 3.3 d | short | 2.4M | 724K vs 2.0K (×355) | 286 | 13.9K | 40 d | none |
| MiniSchool89 | MEMES_CLIPS | [Herobrine and the mysterious elevator!](https://www.youtube.com/watch?v=3qY5RR23wUE) | 0.9 d | short | 451K | 451K vs 2.4K (×186) | 10 | 36K | 82 d | none |
| Short Gamerzz | BUILD | [House for My Dog](https://www.youtube.com/watch?v=CYoR2MB4KvY) | 4.7 d | short | 237K | 50K vs 333 (×150) | 60 | 4.2K | 66 d | none |
| zedarGG | MEMES_CLIPS | [NOT the SOUND](https://www.youtube.com/watch?v=sDPUHcASUjM) | 3.2 d | short | 1.7M | 540K vs 3.7K (×145) | 33 | 232K | 305 d | none |
| Blockified | KIDS_ANIM_STORY | [JJ and Pig Swap Brains…](https://www.youtube.com/watch?v=QTLtqJriKgM) | 4.2 d | short | 2.1M | 493K vs 4.7K (×105) | 39 | 19.6K | 275 d | maizen |
| Whitye | FACTS_TIPS_NEWS | [Minecraft Mobs Weaknesses !](https://www.youtube.com/watch?v=7D8-j8lFu2s) | 4.0 d | short | 2.5M | 630K vs 6.1K (×103) | 33 | 138K | 88 d | none |
| Mr MushMoo Animation | KIDS_ANIM_STORY | [JJ and JJ Sister Wall-Playing 1](https://www.youtube.com/watch?v=IYZEPN-PQmQ) | 2.3 d | short | 1.4M | 607K vs 6.6K (×92) | 14 | 6.1K | 43 d | maizen |
| MineBraintor | MANHUNT_PVP | [Minecraft TNT Brainrots PVP Live 01](https://www.youtube.com/watch?v=Ol3mgOtNQww) | 2.4 d | **long (live)** | 516K | 216K vs 165 (×1310) | 565 | 1.9K | 30 d | brainrot |
| AlphaOGPlayz | FACTS_TIPS_NEWS* | [MINECRAFT LIVE! Creating Massive Emperor](https://www.youtube.com/watch?v=CTc3Dy0Mb-Q) | 1.0 d | **long (live)** | 138K | 134K vs 200 (×670) | 39 | 13.5K | 272 d | none |
| JJ AND MILKY ANIMATION STORYS | KIDS_ANIM_STORY | [JJ AND MILKY ANIMATION STORY](https://www.youtube.com/watch?v=Kx7mBPPUKhw) | 2.4 d | **long** | 162K | 69K vs 396 (×173) | 82 | 23.5K | 210 d | maizen |
| JJ AND MILKY ANIMATION STORYS | KIDS_ANIM_STORY | [JJ Found a GIRL SUBMARINE Underwater?!](https://www.youtube.com/watch?v=zuW2BlvTpCc) | 4.2 d | **long** (3 min+) | 136K | 32K vs 396 (×82) | 69 | 23.5K | 210 d | maizen |
| BacTi | SKIT_COMEDY | [Animation Battles / Verity Mod Minecraft Characters #13](https://www.youtube.com/watch?v=T9ik9Tj_r9I) | 4.2 d | **long** | 341K | 80K vs 4.1K (×20) | 38 | 2.7K | 300 d | verity |
| Banazen Craft | RP_STORY_GAMEPLAY | [JJ and Mikey Grow SECRET VERITY from Seeds](https://www.youtube.com/watch?v=uah6ikSydJ8) | 2.2 d | **long** | 394K | 175K vs 14K (×12) | 3.6 | 4.3K | 9 d | maizen, verity |
| Clooless Gaming | CHALL_BUT | [Beating Minecraft With The Disabilities Mod](https://www.youtube.com/watch?v=QZ-cOjajyYg) | 1.9 d | **long** | 821K | 438K vs 34K (×13) | 1.7 | 318K | 347 d | none |
| my MONSTER SCHOOL | BUILD | [CATS VS LORD VERITY and Lord Obesity in Verity CITY…](https://www.youtube.com/watch?v=peLEUxpFLEk) | 1.1 d | **long** | 203K | 191K vs 15K (×12.5) | 1.7 | 11.4K | 325 d | verity |
| BionicTV | RP_STORY_GAMEPLAY | [I Secretly Duped Everything in Minecraft](https://www.youtube.com/watch?v=FCLgTANcobk) | 1.8 d | **long** | 151K | 84K vs 9K (×9.4) | 0.4 | 151K | 258 d | none |

  `*` AlphaOGPlayz's "MINECRAFT LIVE!" is a livestream, mis-bucketed by the word "live". MineBraintor's "TNT … Live" items are livestream replays.
- **Explosions by niche (OBSERVED).** Of the 398, the top niches were MEMES_CLIPS 74 (60 without IP), KIDS_ANIM_STORY 70 (only 10 without IP), KIDS_CHOICE_PUZZLE 45 (10 without IP) and SKIT_COMEDY 40 (19 without IP). Only 34 of 398 were long-form.

### Inferences
- The views/day-vs-norm ratio inflates for tiny channels: a norm of 25–165 views/day turns any 100K video into ×500+. For decisions, use the ÷median and ÷subs columns together, with absolute views. By that reading, the most decision-relevant original-IP explosions are three: Mob Academy (33 d, 369 subs, 114K), SohilXCraft (33 d, 347 subs, 254K) and Mrjunaid Short (40 d, 2.4M). All three are Shorts made by young animation accounts.
- Livestream replays (MineBraintor, AlphaOGPlayz) show up as "long-form explosions". They are a different product, 24/7 or interactive live, and should not be read as evidence for edited long-form animation (INFERRED).
- Leaders' 30-day outliers repeat a *series* formula rather than standalone ideas. PumpBrine runs "Smartest Player VS …" Part 2–38. darix runs "Kpop Head … Part 3/10/12". Joeysaf runs "Minecraft But …". Sleepy Mikey/Cheesy run "No One Helped …". Wablo runs "There is an imposter in my house" (×2 variants). wykull runs "REALISTIC … in Minecraft". INFERRED: a numbered, repeatable premise is the common trait of the leaders' breakouts.

### Gaps
- No channel medians exist for most long-form leaders (78 of 116 leader slots lack uploads). Long-form outlier claims for Parrot, ProBoiz 95, Cash, Aphmau, Ryguyrocky, Luke TheNotable, Karry Kraft, Junkeyy and similar channels are **not measured**. Getting them needs about 1 playlistItems unit + 1 videos.list unit per channel on a future quota day.
- First-5-day explosions are relative to a 3–30-day norm built from at most 50 uploads. For Shorts-heavy channels that window can be only days long.

## Q6. Which sub-niches a new original-IP channel (Bin, Bo, baby zombie Zu; Blender/Mine-imator; Minecraft Java) should target

### Takeaway
No sub-niche scores well on everything. On the INFERRED composite (demand, long-form demand, newcomer share, original-IP share, Made-for-Kids risk, production fit), the best-supported plan is:
- **(1) Long-form: scripted survival with a threat hook.** This means 100 Days / outbreak / "something is hunting us", packaged like HOR_PLAY/SURV100 titles, Not-Made-for-Kids tone, 20–70 min. Evidence: 7-day long-form demand of 7.7M (SURV100) + 14.2M (HOR_PLAY); 63–91% of hits are original IP; four young-channel breakouts (Kit vs The End ×34 median, Day Zero, SirCloaked, Clooless Gaming).
- **(2) Shorts as the discovery funnel: original-IP animated comedy skits and Monster-School-style character Shorts.** In 7 days, 27 no-IP ≥100K skit Shorts (41% from newcomers) plus 12 no-IP kids-animation Shorts (92% from newcomers).
- **(3) Optional: "Minecraft but…" premises staged with our characters.** 88% original; long-form newcomer share 21–25%.
- **Avoid as a main lane:** interactive choice/puzzle, music/dance, drawing and SMP clips (75–100% third-party IP); player-simulation wars and manhunt/PvP (need real multiplayer servers or personalities); found-footage/ARG labels (7-day long-form median 2.8K).

### Cited Findings
- **Composite ranking (component values OBSERVED; weights, MFK risk and fit INFERRED; [derived_A_niche_ranking.csv](data/derived_A_niche_ranking.csv)).**
  - Score = 0.15·pct-rank(log total views) + 0.25·pct-rank(log long-form views) + 0.20·pct-rank(newcomer share of ≥100K) + 0.15·pct-rank(original-IP share) − 0.10·MFK-risk/3 + 0.15·production-fit/3.
  - MFK risk (0–3) is my judgment from how kids-coded the format and characters are. Production fit (0–3) is my judgment of how well it suits scripted Blender/Mine-imator character animation with original characters.
  - Columns: rank, niche, 7-day views, long-form (share / median / count ≥100K), newcomer share of ≥100K, original-IP share of ≥100K, MFK risk, production fit, score.

| # | Niche | 7-d views | Long-form: views (share) / median / ≥100K | ≥100K from ch ≤12 mo (no-IP newcomer hits) | Original-IP share of ≥100K | MFK risk | Prod. fit | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | CHALL_BUT | 42.7M | 8.2M (19%) / 18K / 14 | 12% (4) | 88% | 1 | 2 | 0.57 |
| 2 | HOR_PLAY | 19.3M | 14.2M (74%) / 41K / 20 | 21% (7) | 91% | 0 | 1 | 0.57 |
| 3 | KIDS_ANIM_STORY | 102.5M | 4.7M (5%) / 362K / 7 | 53% (11) | 14% | 3 | 3 | 0.55 |
| 4 | SIM_WAR | 15.4M | 15.3M (99%) / 170K / 6 | 17% (1) | 100% | 0 | 0 | 0.53 (thin, n=13) |
| 5 | RP_STORY_GAMEPLAY | 26.2M | 17.6M (67%) / 149K / 33 | 7% (1) | 64% | 2 | 2 | 0.52 |
| 6 | SURV100 | 8.7M | 7.7M (88%) / 47K / 23 | 7% (1) | 63% | 1 | 3 | 0.50 |
| 7 | BUILD | 36.0M | 2.5M (7%) / 44K / 7 | 29% (9) | 90% | 1 | 1 | 0.50 |
| 8 | SATISFY_REAL | 8.9M | 50K (1%) / 25K / 0 | 33% (1) | 100% | 1 | 2 | 0.48 (thin, n=9) |
| 9 | MANHUNT_PVP | 8.5M | 4.9M (58%) / 8K / 10 | 32% (5) | 84% | 0 | 0 | 0.47 |
| 10 | SKIT_COMEDY | 88.7M | 1.4M (2%) / 86K / 4 | 27% (11) | 46% | 2 | 3 | 0.47 |
| 11 | SMP | 26.1M | 5.1M (19%) / 51K / 13 | 29% (3) | 42% | 0 | 0 | 0.46 |
| 12 | HOR_FIC | 1.6M | 1.5M (90%) / 3K / 4 | 0% (0) | 100% | 0 | 3 | 0.45 |
| 13 | FACTS_TIPS_NEWS | 12.8M | 425K (3%) / 3K / 1 | 29% (4) | 100% | 1 | 1 | 0.42 |
| 14 | MEMES_CLIPS | 130.8M | 24K (0%) / 12K / 0 | 28% (21) | 74% | 1 | 1 | 0.40 |
| 15 | KIDS_CHOICE_PUZZLE | 109.9M | 352K (0%) / 176K / 1 | 33% (7) | 13% | 3 | 2 | 0.39 |
| 16 | MUSIC_DANCE | 21.4M | 10K (0%) / 78 / 0 | 57% (2) | 21% | 3 | 2 | 0.34 |
| 17 | DOC_LORE | 3.4M | 3.4M (100%) / 59K / 2 | 0% (0) | 50% | 0 | 1 | 0.31 (thin) |
| 18 | FOOD_FIRST | 3.9M | 516K (13%) / 516K / 1 | 0% (0) | 50% | 2 | 3 | 0.29 (thin, n=4) |
| 19 | LP_GENERAL | 923K | 923K (100%) / 22K / 2 | 0% (0) | 50% | 0 | 1 | 0.24 (thin) |
| 20 | ART_DRAW | 4.7M | 0 / – / 0 | 67% (0) | 0% | 3 | 1 | 0.21 (thin) |

- **RPM context (OWNER brief + earlier report).** Shorts earn about 3–14% of long-form RPM. Made-for-Kids classification cuts RPM by about 80–85% (INFERRED in the [2026-11-03 RPM report](../../reports/Ngách%20Minecraft%20RPM%20cao%20bền%20vững.md), from AIR Media-Tech medians). `made_for_kids` was True for **0** videos in the 7-day English set (OBSERVED), so uploader self-declaration says nothing about audience age.
- **"Baby zombie tries food for the first time" (OWNER seed keyword) has almost no 7-day demand in this sample (OBSERVED).** FOOD_FIRST has 4 videos in 7 days; the leader is Nolan "I Tried Every Minecraft Food!" (3.3M, 3.55M subs, live-action-style creator).

### Inferences
- **Why the composite is not the final order (INFERRED).** CHALL_BUT and HOR_PLAY score highest mostly because they are long-form-heavy and original-IP. As *formats* they are gameplay let's-plays, not character animation (fit 1–2). The actionable combination for Bin/Bo/Zu is SURV100's story structure (fit 3) inside HOR_PLAY's packaging ("Something Is Hunting Us…", "Zombie Outbreak: 100 Days…"). The two 15-day cold-start breakouts, Kit vs The End and Day Zero, are exactly that hybrid.
- **Kids animation is the volume trap (INFERRED).** KIDS_ANIM_STORY has the highest newcomer share and the best production fit. But 86% of its hits use Maizen IP, 95% of its views are Shorts, and Bin/Bo/baby-Zu designs carry high MFK risk. Use it only as a Shorts funnel with teen-leaning comedy/creepy-cute tone, and do not make it the revenue lane. This agrees with the 2026-11-03 report.
- **Animated comedy skits are the best Shorts lane for our tools (INFERRED).** Original-IP examples reached millions from small or young channels: CHIRAG FACTO (11 d, 2.6M), Floog (1.8K subs, 1.6M), Wablo (114 d, 254K subs, multi-million), MaizCr (34K subs, 1.6M), SohilXCraft (347 subs, 254K). PumpBrine's numbered-series pattern (Part 2→38) can be copied with original characters.
- **Horror fiction packaging (INFERRED).** HOR_FIC's 7-day long-form median of 2.8K and 0% newcomer share argue against "ARG / found footage / analog horror" as the *label*. The mystery can stay in the story and should not lead the title.
- **What not to chase (INFERRED).** SIM_WAR needs thousands of real players and a big creator (Parrot 4.45M subs, Spoke). SMP needs streamer personalities. MANHUNT needs live players. Our Blender pipeline can fake neither credibly at speed.

### Gaps
- No RPM, retention or audience-age data exist for any of these channels in the public API. The ranking rests on views and the OWNER RPM ratio.
- The four young long-form survival/horror breakouts are too few to estimate a success *rate*. A larger sample of ≤12-month long-form channels needs another quota day: search.list costs 100 units per query.
- The weights, MFK-risk scores and fit scores are my judgment. The owner may weight long-form RPM or production capacity differently. The table keeps every component so the order can be recomputed.
