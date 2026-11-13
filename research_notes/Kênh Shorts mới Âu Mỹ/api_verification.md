# API verification of tracker / case-study candidates (OBSERVED, 2026-11-13 ~19:00 VN)

**How:** `channels.list` with `forHandle`, plus `playlistItems` (latest 50 uploads) and `videos.list`, using the official API on the owner's PC.

- Raw data: `reports/research/new_channel_hunt_2026-11-13/tracker_candidates_verify.json`.
- "Median" = median views over the latest 50 uploads.
- "Like" = total likes ÷ total views over those uploads.

## Verified channels

| Handle | Created (API) | Age on 11-13 | Country setting | Subs | Total views | Videos | Median / upload | Like | Top uploads |
|---|---|---|---|---|---|---|---|---|---|
| @gta6-罪恶都市 | 2026-10-14 | 30 d | US | 544K | **1,077,063,775** | 115 | 1.18M | 0.88% | 17.2M "#gta #gta6 #shorts" (46 s); 8.1M; 7.7M. GTA6 gameplay clips, no spoken language |
| @gta6-w7m (GTA6) | 2026-10-14 | 30 d | US | 506K | **462,850,321** | 123 | 645K | 1.5% | 57.5M "小狗该如何选择？#GTA #GTA6" (29 s). Chinese titles |
| @glowstrikeshop (GlowStrike) | 2026-10-08 | 36 d | CA | 117K | **253,151,259** | 54 | 129K | 0.38% | 176.6M "Link in bio! ⚡️🤩" (15 s). Product/dropship; one video holds ~70% of views; low like rate suggests possible paid promotion |
| @tecuentoblox (Te Cuento Blox) | 2026-10-10 | 34 d | ES | 205K | **191,635,563** | 97 | **1.73M** | 1.85% | 9.5M "En este pueblo, solo puedes decir 'NO' UNA vez en la vida…" (1:53, es-419); 8.4M "En este pueblo, todos tienen un SUPERPODER…"; 8.3M "En este pueblo, si dices '¡ME LO PIDO!'…". Roblox-style "town with one strange rule" stories |
| @lumarein (LumaRein) | 2026-10-17 | 27 d | CA | 128K | **180,517,905** | 72 | 178K | 0.67% | 25.9M "Comment 'Horse' if you need these for your horse" (14 s). Affiliate/product |
| @sashashowbro (SASHA SHOW) | **2022-03-23** | old | TR | 17.7M | 1.74B | 184 | 5.4M | 2.59% | 162.8M "Кто украдет БОЛЬШЕ ВСЕГО КОНФЕТ у САМОЙ ЗЛОЙ БАБУШКИ" (1:10, ru). Old channel that pivoted (latest 50 uploads all since 2026-09-03) |
| @LucanPevidor | **2021-10-27** | old | BR | 49.5M | 18.5B | 2,540 | 12.5M | 2.88% | Portuguese family challenge Shorts. Old channel |

`@USAbaby-e5v` was not found via `forHandle`.

## Conclusion of verification

1. **No channel created ≤15 days ago (on or after 2026-10-29) with ≥100M views was found**, by trackers or by our own API pools. The largest ≤15-day channels in our pools: Rô Tới Chơi (VN) 117.7M and CuddlePop (IN/en AI baby) 116.9M; in the US/EU set, Copycat Cuties at 76M.
2. **At ≤30–36 days old there are US/EU-flagged channels with hundreds of millions to 1B views:**
   - GTA6 gameplay Shorts with Chinese titles, country set to US: 1.08B and 463M.
   - Affiliate/product channels (CA): GlowStrike 253M (possibly paid), LumaRein 181M.
   - Spanish "En este pueblo…" Roblox-style rule stories (ES): 191.6M.
3. **Cross-language trend (INFERRED):** "a town with one strange rule" story Shorts appear in Spanish (Te Cuento Blox, median 1.73M/upload) and Vietnamese (Rô Tới Chơi: "Thị trấn mỗi ngày chỉ được nói mười từ", 117.7M in 14 days). An English, original-IP version is a candidate format to test.
