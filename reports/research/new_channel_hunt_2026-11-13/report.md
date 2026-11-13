# Channels created ≤15 days ago that already broke out (2026-11-13)

## Method (OBSERVED)
- **Video pool.** Video IDs came from two places:
  - Tube Atlas v1.0.6.7 exports: the 19-keyword Shorts scan, plus the **Trending Videos** button (99 rows, mostly music).
  - YouTube Data API `search.list` with `publishedAfter=2026-10-29`, `order=viewCount`, `relevanceLanguage=en`. There were 24 queries, each run as Shorts and as any length (48 calls).
- **Enrichment.** `videos.list` and `channels.list` added each channel's **creation date** (`snippet.publishedAt`), subscribers and total views.
- **Scale and cost.** About 4,877 units were used. The pool was 2,259 videos from 1,504 channels.
- **Code and data.** The script is `cf_new_channel_hunt.py`; it reads the key from `.env` and never prints it. Raw data is in `hunt_15d.json`; the analysis is `analyze.py`, and its output is `channels.json`.
- **Limits.**
  - Search was ordered by views, so this list shows winners, not the failure rate.
  - Channel age is the account creation date.
  - Views are lifetime totals from one snapshot.
  - Under the new 2026-08-24 view definition, public views ≈ 1.6× engaged views (INFERRED from the Agentio ratio).

## Result
- In the pool, **30 channels were ≤15 days old and 22 of them already had ≥100K channel views.**
- For ≤30 days: 63 channels, of which 50 had ≥100K.

### Relevant to CINE (original, faceless, Blender/3D or Minecraft) — channels ≤15 days old

| Channel | Age | Channel views | Videos | Subs | Format | Top video |
|---|---|---|---|---|---|---|
| 3d Loop Layer | 13 d | 4.83M | 14 | 1.1K | 6-second 3D satisfying loops | "Infinite Dice Waves 2", 3.48M |
| Robots Taught Me | 15 d | 4.82M | 17 | 1.5K | 3D reconstruction explainers | Learjet crash debris, 4.75M |
| Cube Clash | 8 d | 1.36M | 10 | 15.4K | Minecraft-style noob vs pro disaster | "Who survives the FLOOD?", 341K |
| MMirazzX | 15 d | 1.21M | 20 | 0.4K | Soft body "0% vs 100%" | 1.0M |
| AMP Digitals | 10 d | 1.11M | 49 | 0.6K | Blender marble plinko | 395K |
| Squishy 3D | 14 d | 601K | 21 | 0.5K | "Minecraft vs Real Life" Blender sims | 76K |
| Mob Problems | 9 d | 402K | 18 | 0.5K | Minecraft noob vs pro from the zombie's POV | 23K |
| GridLoopifyX | 12 d | 383K | 10 | 0.1K | 3D satisfying loops | 35K |

### Relevant — channels 16–30 days old

| Channel | Age | Channel views | Videos | Format |
|---|---|---|---|---|
| SatisfyingShortly | 21 d | 12.4M | 78 | 3D satisfying |
| Mochi & Pals | 29 d | 9.79M | 17 | Cute Minecraft-style "who builds the best house?" |
| Endform TV | 22 d | 6.33M | 41 | "Which Block Reaches Final Form? ⛏️" Minecraft 3D |
| Enbi Loop | 27 d | 3.96M | 32 | 3D satisfying loops |
| Stumblework Studios | 19 d | 3.09M | 8 | "You Just Invented the Sewing Machine", an invention series |
| Bureau of Odd Things | 19 d | 2.45M | 12 | 3D "how a tractor becomes a tank" |
| Melt Everything 3D | 23 d | 665K | 20 | Soft body |

### Not for CINE
- **Hindi "bhoot wala" horror cartoons:** Tudicore Darr TV, DAARNOX, BhootWalaCartoonHorror and others. Wrong language and market.
- **Emotional AI animal stories** (Moral Puppy Story, Edit Ingrid). Policy risk: emotionally manipulative content.
- **Maizen/JJ IP** (DiaxGold Crafts).
- **"Real or fake?" filmed experiments** (Shivalex). Misleading-content risk, and they need live filming.
- **Movie-detail trivia using film footage** (Detective Pasini). Reused-content risk.

## Reading (INFERRED)
- Yes — brand-new channels can reach millions of Shorts views within 2 weeks. The repeated pattern is **Blender 3D satisfying loops, soft-body or Minecraft-themed physics, and 3D "how it works/reconstruction" explainers**. That matches the studio's S2 lane and its Blender capability.
- **The money is small and not immediate:**
  - Even at 4.8M views a channel earns $0 until it is in YPP (1K subs + 10M Shorts views in 90 days).
  - After that, Shorts pay roughly $0.03–0.10 per 1K engaged views (ESTIMATED).
  - Subscriber conversion of loop channels is very low: 3d Loop Layer has 1.1K subs on 4.8M views.
- **Durable picks** are formats with a series and identity, such as Stumblework's invention series (18.6K subs on 3.1M views) and Mochi & Pals characters. Pure loops are the opposite.

## Next steps
- Re-run the same pool in 3–7 days. That gives real velocity and shows which new channels keep growing.

## Addendum: mega hunt, any niche and any country (OBSERVED, 18:30 VN)
- **Method.** `cf_mega_new_channel_hunt.py` ran `search.list` with `order=viewCount`, `publishedAfter=2026-10-29` and Shorts only.
  - Region feeds with no query: US, IN, BR, ID, MX, PH, GB, DE, JP, KR, VN, TH, EG, PK.
  - 20 generic queries: baby, cat, ai, story, car, and others.
  - About 3,845 units. Merged with the earlier pool, that gives **2,360 channels**.
- **Channels created ≤15 days ago: 51.** 18 have ≥10M channel views, 2 have ≥100M, and **none is near 1 billion**.

| Channel | Age | Channel views | Videos | Subs | Format | Note |
|---|---|---|---|---|---|---|
| Rô Tới Chơi (VN) | 14 d | 117.7M | 33 | 152K | Vietnamese 2–3 min story Shorts ("Thị trấn mỗi ngày chỉ được nói mười từ") | Vietnamese audience, so low RPM |
| CuddlePop (IN) | 10 d | 116.9M | 6 | 39K | Realistic AI baby clips; one Short has 120M views | Policy risk |
| Copycat Cuties | 12 d | 76.0M | 80 | 22K | AI baby "copies" | Policy risk |
| Baby Bo | 15 d | 52.9M | 20 | 51K | AI baby | Policy risk |
| WonderSnapp, Old Guy Energy, Rycroft Willians, Baby Bloom | 7–14 d | 24–40M each | 5–25 | 7–17K | AI baby/family | Policy risk |
| Ghibli Tales | 9 d | 21.6M | 8 | 37K | "Ghibli"-style AI garden stories | Uses another studio's style and name |
| Casper Cat, Pawspike, tooniverse, Pov Of Animal | 6–12 d | 10–22M each | 4–22 | 3–57K | AI cats | Policy risk |
| **Tekto Explains** | 13 d | 16.7M | 13 | 30.5K | **3D explainer "How To Build a Nuclear Bunker"** | Like rate 2.16% and 2,630 comments: real engagement, CINE-compatible |
| VEXOMORPH | 11 d | 15.3M | 19 | 11.9K | "Luxury car that turns into a flower cabinet" | AI/3D transform |
| Pizza Hub (VN) | 10 d | 12.6M | 5 | 31.6K | Vietnamese story Shorts | |

- **Excluded as paid ads.** GOPLUS (24 d) has 254M views with 0.00% likes and 7 comments on an 87M-view ad.
- **For context, ≤30 days:** Baby Elecyent 48.6M, lulu fah stories 46M, Crazyfunnybloxx 43M (Roblox IP), Memeland 31.6M ("Football Club Merge … Final Form").
- **Reading (INFERRED).**
  - Channels that reached hundreds of millions of views within 15 days exist, but they are AI realistic baby/animal clips or Vietnamese story Shorts.
  - **AI realistic babies are high-risk.** They carry YouTube's realistic-AI disclosure duty and the July 2026 inauthentic-content rule ("same situation, same outcome"). Depicting minors realistically is also sensitive. Low like rates (0.4–0.6%) show passive views, and the money is small: Shorts RPM is about $0.03–0.10 per 1K.
  - **The CINE-compatible breakout is Tekto Explains,** a 3D "how to build X" explainer: 16.7M views in 13 days with genuine engagement. It fits the studio's 3D history/engineering explainer direction (`docs/niches/capability_niche_matrix_2026-11-12.md`).
