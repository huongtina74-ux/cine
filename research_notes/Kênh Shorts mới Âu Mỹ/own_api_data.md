# Own YouTube Data API measurements, 2026-11-13 (OBSERVED, CineFactory scripts on the owner's PC)

All of these runs used the official YouTube Data API v3. The key was read from `.env` and never printed. Channel age is `channels.list snippet.publishedAt`.

## Runs

1. **`cf_new_channel_hunt.py`**
   - Inputs: 24 English keywords × {short, any}; `search.list` with `order=viewCount`, `publishedAfter=2026-10-29`; plus Tube Atlas exports.
   - Pool: 2,259 videos, 1,504 channels. Cost about 4,877 units.
2. **`cf_mega_new_channel_hunt.py`**
   - Inputs: region feeds with no query for US, IN, BR, ID, MX, PH, GB, DE, JP, KR, VN, TH, EG, PK (US/IN/BR/ID got 2 pages), plus 20 generic queries.
   - Pool: 1,250 videos, 967 channels. Cost about 3,845 units.
3. **`cf_us_eu_new_channel_deep.py`**
   - Inputs: region feeds for CA, AU, FR, ES, IT, NL, PL, SE, BE.
   - Selected channels created ≤30 days ago with ≥1M views and US/EU signals, then pulled the latest 50 uploads for the top 45. Cost about 997 units.
4. **`cf_mostpopular_us_eu.py`**
   - Inputs: `videos.list chart=mostPopular` for US, GB, CA, AU, DE, FR, ES, IT, NL, PL, SE, IE, BE, AT (up to 200 results each).
   - Result: 1,792 videos, 1,657 channels, 295 of the videos ≤180 s. Cost 90 units.

Total across runs 1–3: **2,360 unique channels**.

Daily quota is now about spent: roughly 9,800 of 10,000 units, and the `search.list` limit of about 100 calls/day is close to used. Both reset at 15:00 Vietnam time.

## Findings

**Channels created ≤15 days ago (any country): 51.**
- 18 have ≥10M channel views, 2 have ≥100M, and **0 have ≥1B**.
- **≥100M:**
  - Rô Tới Chơi (VN, Vietnamese, 117.7M, 33 videos).
  - CuddlePop (country IN, English AI baby clips, 116.9M, 6 videos; one Short has 120M).
- **Excluded:** GOPLUS (VN ad, 254M views, 0% likes, 24 days old) as paid promotion.

**US/EU channels ≤15 days old.** The largest are AI toddler/baby clips and affiliate funnels:

| Channel | Age | Channel views | Videos | Subs | Format |
|---|---|---|---|---|---|
| Copycat Cuties | 12 d | 76.0M | 80 | 21.7K | AI toddler/baby |
| Baby Bo | 15 d | 52.9M | 20 | 50.7K | AI toddler/baby |
| WonderSnapp | 13 d | 39.8M | 7 | — | AI toddler/baby |
| Old Guy Energy | 11 d | 29.2M | 7 | — | median 1.85M per upload |
| Rycroft Willians | 14 d | 28.9M | — | — | AI toddler/baby |
| Baby Bloom | 7 d | 24.4M | — | — | AI toddler/baby |
| Casper Cat | 10 d | 21.5M | — | — | AI cat drama |
| Ghibli Tales | 9 d | 21.6M | — | — | AI garden stories |
| Tekto Explains | 13 d | 16.7M | — | — | country CY, US feed; 3D "How To Build a Nuclear Bunker" |
| VEXOMORPH | 11 d | 15.3M | — | — | transforming vehicles |
| Pawspike | 6 d | 13.7M | — | — | affiliate |

**US/EU channels 16–30 days old:**

| Channel | Age | Channel views | Subs | Format |
|---|---|---|---|---|
| traineronevolleyball | 18 d | 56.1M | — | affiliate "comment for link" |
| Baby Elecyent | 29 d | 48.6M | — | AI baby/toddler |
| lulu fah stories | 27 d | 46M | 319K | horror micro-stories |
| Crazyfunnybloxx | 24 d | 43M | 439K | Roblox animated stories |
| Pawly | 24 d | 40.6M | — | affiliate |
| ¿Qué hacer si…? | 15 d | 27.1M | — | Spanish survival explainer |

**mostPopular charts (14 US/EU regions):** no brand-new Shorts megachannel. The youngest non-"Topic" channels were:
- FrabyESP: 15 d, ES, 33.3M, 26 videos.
- LumeXx Spielt: 13 d, DE, 459K.
- Dillymingo: 11 d, US, 135K.

The charts are dominated by music "Topic" auto-channels and established creators.

## Caveats

- `search.list` ordered by viewCount returns at most about 500 results per query and is biased towards winners.
- `regionCode` means "viewable in", not the creator's country. `snippet.country` is self-declared and often blank.
- Every figure is a single snapshot taken on 2026-11-13.
