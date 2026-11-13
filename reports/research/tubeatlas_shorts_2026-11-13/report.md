# Tube Atlas Shorts scan: 19 keywords, Minecraft + other niches (2026-11-13)

## Method
- **Tool:** Tube Atlas v1.0.6.7 on the owner's Windows PC, driven by Claude via computer use.
- **Search setup:** Videos → Search, YouTube first page only. Google and Bing were OFF. Sort = Relevance. Each phrase had `#shorts` appended.
- **Volume:** 19 phrases, 810 rows exported, 765 unique videos, 438 flagged `Is Shorts = YES`.
- **Files:**
  - Export: `raw_tubeatlas_export.csv`
  - Analysis code: `analyze.py`
  - Full numbers: `analysis.json`
- **Limits:**
  - About 20–30 results per phrase, chosen by YouTube relevance. The sample therefore leans towards winners and tells us nothing about failure rates.
  - This is one snapshot, so "views/day" is lifetime views ÷ age.
  - There is no channel age column. Breakout channels still need a channel-age check (Channels tab or API).
  - Views use the post-2026-08-24 definition.
  - The "Est. Earnings" column (a flat $1.85 per 1K views) is ignored.

## Shorts by keyword (OBSERVED from the export; ratios INFERRED)

| Keyword | n | Median views | Channels with ≥1M | Of which <100K subs | Recent ≤30 d | Recent median views/day | Like rate | Comments hidden | IP in title/tags |
|---|---|---|---|---|---|---|---|---|---|
| science experiment | 37 | 3.31M | 17 | 12 | 13 | 4.5K | 0.93% | 14% | 3% |
| ai animals | 25 | 639K | 12 | 8 | 2 | 34K | 0.77% | 4% | 0% |
| satisfying 3d animation | 25 | 566K | 10 | 6 | 9 | 35K | 0.43% | 16% | 12% |
| minecraft satisfying | 24 | 535K | 9 | 3 | 9 | 13K | 1.23% | 12% | 0% |
| soft body simulation | 29 | 441K | 11 | 8 | 10 | 12K | 0.79% | 7% | 0% |
| history facts | 18 | 440K | 6 | 2 | 8 | 6.5K | 2.18% | 11% | 0% |
| minecraft parkour | 25 | 392K | 7 | 4 | 10 | 10.6K | 1.88% | 4% | 0% |
| minecraft tnt experiment | 28 | 356K | 11 | 8 | 14 | 5.2K | 1.31% | 18% | 0% |
| did you know facts | 24 | 185K | 7 | 6 | 4 | 3.0K | 1.46% | 8% | 0% |
| minecraft noob vs pro | 23 | 170K | 6 | 4 | 13 | 11K | 1.14% | 9% | 22% |
| minecraft horror | 23 | 67K | 4 | 1 | 17 | 14.6K | 1.24% | 13% | 4% |
| minecraft facts | 20 | 47K | 7 | 6 | 5 | 7.9K | 2.84% | 5% | 0% |
| minecraft animation | 22 | 38K | 5 | 4 | 18 | 36K | 1.37% | 27% | **59%** |
| beamng crash | 23 | 38K | 4 | 2 | 18 | 12.5K | 0.63% | 35% | 0% |
| minecraft redstone | 20 | 27K | 3 | 1 | 15 | 8.7K | 1.48% | 5% | 0% |
| minecraft physics experiment | 25 | 22K | 3 | 2 | 17 | 4.5K | 0.98% | 40% | 0% |
| minecraft build hacks | 28 | 9.5K | 2 | 2 | 15 | 1.2K | 1.45% | 36% | 4% |
| marble race | 17 | 3.4K | 0 | 0 | 17 | 3.4K | 0.57% | 71% | 0% |

The `animated story` keyword returned only 2 Shorts and is left out.

## Breakouts and evidence of durability (OBSERVED)

**Blender soft-body / "0% vs 100%"**
- 11 channels have a Short with ≥1M views. 8 of those channels have under 100K subscribers.
- New breakouts:
  - ArtikAnimates: 9.46M views in 24 days, 11.6K subs.
  - Blendverse 3D: 8.68M in 23 days, 29.2K subs.
- Older Shorts still above 1M: RenderZen 10.3M (419 days), Foxsplash 3D 18.7M (244 days), Digital 3D Pixel 10.2M (400 days), sentix 3d 8.2M (506 days).
- Repeat winners: Windie 3D, 3D 4FUN.

**Minecraft satisfying in 3D (Blender sims with Minecraft themes)**
- VOXCRASH: "Creeper → Steve | Minecraft Factory | Satisfying Loop", 7.86M views in 32 days, 30.7K subs.
- Craft Lab3D: 6.9M (117 days) and 1.33M (402 days).
- Render X: hair simulation, 10.1M (726 days).
- Windie 3D: "Steve vs Realistic Fluid", 1.15M and 4.84M.
- 3D Smoothie Spot: "Hero Iron Golem … Satisfying Fluid", 676K on day 1.

**Minecraft horror**
- JohnnyXD: "How Is This Even Possible?", 3.45M views in 5 days on a 9.8K-sub channel, i.e. 351× its subscriber count.
- Galinha Dangola: 9.63M (79 days) and 1.9M (47 days).
- 17 of the 23 results were ≤30 days old.

**Minecraft parkour TAS**
- UnVoidMC: 2.09M views in 12 days, 6.6K subs.

**Minecraft animation**
- Dominated by Maizen/JJ IP, e.g. Sir Potato 25.1M in 3 days.
- **Not usable: copies another creator's IP.**

## Reading (INFERRED, for the owner to decide)
1. **Best fit for the studio's Shorts (fast + durable): Blender physics with Minecraft themes plus original characters.** This is S2 refined.
   - It sits where two strong niches meet: soft body / 3D satisfying, and Minecraft satisfying.
   - Many independent small channels win, old videos keep earning views, and the studio already has Blender + GPU.
   - **Risk:** "0% vs 100%" is a template. YouTube's July 2026 inauthentic-content wording ("same situation, same outcome") means each Short needs a different idea.
   - Low like rate (0.4–1.2%) suggests passive viewers and weaker subscriber conversion.
2. **Minecraft horror Shorts (S1):** the freshest momentum among the Minecraft keywords (17/23 recent, median 14.6K views/day) and the JohnnyXD small-channel breakout. It feeds long-form L1/L2, so durability comes from the long-form universe.
3. **Parkour/TAS and TNT experiments:** good medians, but need in-game production (Fabric/Flashback not yet installed).
4. **Avoid:**
   - Minecraft animation (59% Maizen/JJ IP).
   - Noob vs pro (22% IP, kids).
   - Build hacks and physics-experiment Shorts in this sample: low medians and 36–40% hidden comments, a likely sign of Made for Kids.
   - Marble race (median 3.4K).
   - AI animals: policy risk around inauthentic/AI-slop content and animals in distress.
   - BeamNG: game-footage / reused-content risk.
   - Real-life "science experiment" Shorts need filming, and the "real or fake?" style risks being misleading.
5. **Money (ESTIMATED):** Shorts RPM is roughly $0.03–0.10 per 1K engaged views, so a 9M-view Short brings in about $160–540. From 2027-02-01 Shorts earn only at ≥10M qualified views per 90 days. Shorts are the fast traffic and subscriber engine; long-form is the money.

## Next checks
- **Channel ages:** use the API `channels.list` (about 1 unit) for the breakout channels: ArtikAnimates, Blendverse 3D, VOXCRASH, JohnnyXD, UnVoidMC, 3D Smoothie Spot, QUANASIUS_STUDIO.
- **Second snapshot in 3–7 days:** re-import the same video links into Tube Atlas to measure real velocity.
