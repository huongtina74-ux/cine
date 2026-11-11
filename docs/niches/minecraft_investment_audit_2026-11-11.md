# Independent audit: which Minecraft-adjacent long-form niche for a NEW English channel (2026-11-11)

Evidence labels: VERIFIED (re-computed from official API data in this audit) · OBSERVED (seen in a file/page today) ·
INFERRED (reasoning) · ESTIMATED (heuristic) · INSUFFICIENT_EVIDENCE. Data, scripts and per-video classification:
`reports/research/minecraft_audit_2026-11-11/` (classify.py, metrics.py, z_sample.py, classified_videos.csv, metrics.md,
breakouts.json, z_sample.json). Raw data stays on the owner PC (read-only, not modified):
`C:\Users\ADMIN\Downloads\cine_niche_survey\out\2026-11-11_niche_compare` and `...\2026-11-11_audit_z`.

---

## A. Tóm tắt điều hành (Vietnamese)

**Kết luận đảo chiều một phần so với báo cáo trước (D-4127cce8):** con số "Realistic Apocalypse có 14 kênh mới bứt phá" **bị lẫn**.
Phần lớn các kênh đó là **hoạt hình người que 2D kể chuyện sinh tồn (không phải Minecraft)** – Nobody Gets In, Beanie Survives,
DoodleSurvivals, Kit vs The End, StickFallout… Khi tách ra:

| Định dạng (≥ 8 phút, kênh < 100K sub) | Trung vị view | ≥ 1M | Bằng chứng kênh mới |
|---|---|---|---|
| Minecraft gameplay sinh tồn/tận thế thật (A1) | **18K** | 0% | chỉ Day Zero (1 video 2,07M) |
| Minecraft horror mod (A5) | 67K | 2% | có, nhưng là gameplay có người dẫn |
| Minecraft cinematic/machinima (A2) | 80K | 17% | gần như toàn kênh fan Maizen (IP người khác) |
| **Hoạt hình kể chuyện sinh tồn 2D độc lập (A3)** | **500K** | **36%** | **mạnh nhất**: Nobody Gets In 2 video ≥1M trong 30 ngày đầu |
| Mystery/ARG (A6) / Lore (A8) | 8K / 1K | 3% / 4% | yếu |

**Trả lời thẳng câu hỏi mâu thuẫn chiến lược:** Đúng – dữ liệu cho thấy ta đang **ép CineFactory vào Minecraft gameplay**,
trong khi thứ kênh mới thật sự bứt lên được là **câu chuyện sinh tồn có kịch bản** (Day 1 → Day 30, bị kẹt ở một địa điểm,
giải từng vấn đề). Gameplay Minecraft thật còn cần người chơi hàng chục giờ mỗi tập – CineFactory không làm được.
Nhưng làn 2D người que đang là **"cơn sốt vàng"**: ≥ 20 kênh mới ra đời trong 60 ngày, có cả video dạy "làm stickman survival bằng AI
miễn phí" (579K view) → bão hòa nhanh và **rủi ro chính sách nội dung rập khuôn (YouTube, 16/7/2026)**; trung vị mỗi kênh mới chỉ ~18K/video.

**Quyết định đề xuất (chờ OWNER duyệt):**
- **CHỌN CHÍNH:** *Phim hoạt hình kể chuyện sinh tồn có kịch bản, định dạng "Day-N bị kẹt ở một nơi"*, dựng bằng **thế giới khối 3D
  của CineFactory** (phong cách Minecraft nhưng tài sản gốc, không dùng gameplay), dàn nhân vật cố định – lấy **công thức đã chứng minh
  của làn 2D** nhưng **khác biệt bằng chất lượng hình ảnh, quy mô đám đông, nhân vật lặp lại**. 10–14 phút/tập + "Full Movie" 40–60 phút ghép lại.
- **DỰ PHÒNG:** cùng công thức nhưng **minh họa 2D** (rẻ hơn, bằng chứng kênh mới mạnh nhất) – chỉ dùng nếu pilot 3D quá chậm/đắt.
- **LOẠI:** Minecraft gameplay thật (cần chơi hàng chục giờ, kênh nhỏ trung vị 18K), horror mod (cần người dẫn/facecam),
  Mystery/ARG, Lore, Engineering (kênh mới gần như không chen được), fan Maizen (IP).
- **ĐỘ TIN CẬY: THẤP–TRUNG BÌNH.** Nhu cầu và công thức đã có bằng chứng; việc *chuyển công thức sang hình khối 3D* và *sản xuất video
  20+ phút* thì **chưa chứng minh** (video dài nhất CineFactory đã hoàn thành: 57 giây).
- **3 video thử nghiệm** (mục I) kiểm tra 3 giả thuyết khác nhau trước khi làm hàng loạt.

---

## B. Dataset integrity audit

| Check | Result | Label |
|---|---|---|
| Unique video ids | 954 (1,070 niche-assignments) | VERIFIED |
| Channels | 705 | VERIFIED |
| Channels created <= 365 d | 142 (uploads fetched for all 142) | VERIFIED |
| API units | 319 (enrich_meta.json) | OBSERVED |
| Collection date | search 2026-11-11 ~15:20Z, API 15:31Z | OBSERVED |
| Publish window | 2026-10-11 .. 2026-11-11 (all inside "this month") | VERIFIED |
| Videos in > 1 search niche | 87 (A+G 17, A+C 6, B+D 6 ...); previous report counted them in every niche | VERIFIED - **error** |
| Live streams | 0 flagged | VERIFIED |
| Shorts/short videos | 98 videos < 4 min (excluded from long-form) | VERIFIED |
| Language | API audio tag present on all rows; 765 of 954 judged English (tag + accent/word filter). A few English titles with accents (e.g. "Pokémon") are wrongly excluded | ESTIMATED |
| Channel creation dates | official channels.list `publishedAt`, not first upload | VERIFIED |
| Non-Minecraft content | ~75 videos (Roblox, GTA, Peppa, ZAMination, AI tutorials, news) were inside the 7 "Minecraft" niches | VERIFIED - **error** |
| Independent 2D animation counted as Minecraft | yes - the biggest error (see C) | VERIFIED - **error** |
| Established-creator spin-offs counted as "new" | SSundeePlus (2026-09-18, 582K subs; SSundee spin-off) has 10 long videos >= 1M in its first 30 days - not a beginner | VERIFIED (dates) / INFERRED (spin-off) |
| Percentiles | previous: nearest-rank on sorted list; now linear interpolation. Differences small | VERIFIED |
| Sampling bias | top-of-search sample (by views and relevance); medians describe *visible winners*, not the niche | known limitation |
| Day Zero 2.07M video | published 2026-10-07 - **outside** the search window; found only through uploads | VERIFIED |
| Another agent's scripts | `audit_summary_local.py`, `audit_deep_clean.py` appeared in the dataset folder at 15:45Z (not written by this session); reviewed as data only, not run | OBSERVED |

Classification evidence levels (954 videos): THUMBNAIL_VERIFIED 54 (39 priority channels' top long video), METADATA_ONLY 900;
confidence high 45 / medium ~270 / low ~640 (keyword rule). Storyboard frames (YouTube's public scrub-preview sprites, viewed
not downloaded) were sampled for 4 videos: STORYBOARD_SAMPLED. No video was watched with audio; transcripts could not be fetched
(caption endpoint returned empty) -> no TRANSCRIPT_VERIFIED claims.

## C. Cleaned niche comparison (mutually exclusive primary_format, English, >= 8 min = PRIMARY)

Full tables (>= 4 / >= 8 / >= 15 min, sensitivity runs): `reports/research/minecraft_audit_2026-11-11/metrics.md`.

| Format (>= 8 min) | Videos | Ch | Median | P75 | P90 | >=100K | >=1M | New ch (<=365 d) with >=100K | with >=1M | 2x >=1M | repeat (>=3 x 100K) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 Minecraft real gameplay | 179 | 132 | 90K | 519K | 1.52M | 47% | 16% | 14 | 6 | 3 | 7 |
| A1s of which apocalypse/survival-tagged | 103 | 73 | 88K | 326K | 934K | 46% | 9% | 8 | 4 | 2 | 4 |
| A2 Minecraft cinematic / machinima | 93 | 56 | 442K | 1.63M | 3.77M | 72% | 42% | 6 | 2 | 1 | 5 |
| **A3 Independent 2D survival animation** | 17 | 13 | **533K** | 1.14M | 2.45M | **94%** | 35% | **10** | **5** | 1 | 5 |
| A4 Independent 3D survival animation | 0 | - | INSUFFICIENT_EVIDENCE | | | | | | | | |
| A5 Minecraft horror mod gameplay | 131 | 76 | 371K | 1.06M | 1.64M | 69% | 26% | 11 | 4 | 2 | 10 |
| A6 Minecraft mystery / ARG | 44 | 42 | 17K | 128K | 684K | 30% | 7% | 2 | 1 | 1 | 2 |
| A7 Minecraft engineering / redstone | 46 | 43 | 157K | 477K | 1.95M | 57% | 17% | 3 | 1 | 1 | 3 |
| A8 Minecraft lore / history | 58 | 50 | 3K | 127K | 671K | 26% | 7% | 0 | 0 | 0 | 0 |

Sensitivity (>= 8 min, median views): excluding channels > 1M subs -> A3 551K, A2 161K, A5 121K, A1 60K, A7 98K, A6 15K, A8 2K;
excluding channels > 100K subs -> **A3 500K, A2 80K, A5 67K, A7 34K, A1 14K (A1s 18K), A6 8K, A8 1K**. Ranking of A3 is stable;
A2 and A5 collapse once big creators are removed (their medians are carried by Maizen, ProBoiz, CaseOh-size channels).

**A3 dedicated sample** (7 survival-animation queries, 99 videos, 68 channels, 82 units; `z_sample.py`): 41 survival-story channels;
21 created in the last 60 days; 15 of those 21 have a >= 100K long video, 2 have >= 1M; **but the median of each channel's long-video
median is only 18K** - hit-driven, most uploads do not perform. The lane is being flooded: channels of 23-34 days with 6-36 uploads,
and AI tutorials ("How to Create Stickman Animation with AI 100% FREE" 579K; "How to Make Zombie Stickman Survival Videos With Claude Code").

Limits: A3 n is small (17 + 41 channels); every number is a single reading; search ranking over-represents winners; RPM UNKNOWN for all.

## D. New-channel breakout report (official dates; >= 8 min)

Strict Tier-A (age <= 30 d, two >= 1M long videos both published in the last 14 d): **0 channels** (VERIFIED).
Historical early breakouts (>= 8-min video now >= 1M, published <= 30 d after channel creation; date it crossed 1M = UNKNOWN):

| Channel (ID) | Format | Created | Subs | Videos | Qualifying videos (published, channel age at publish, length, views now) | Notes |
|---|---|---|---|---|---|---|
| Nobody Gets In (UCZDmrAO-bnBxU4_LiH40CjA) | A3 | 2026-10-01 | 66.3K | 30 | [Zombie Outbreak: 30 Days Locked Inside a Supermarket](https://youtu.be/oXj7bWgRX_I) (10-13, d12, 11 m, 3.89M); [... Inside a School](https://youtu.be/2XYr2AEHDGI) (10-16, d14, 9 m, 2.13M) | **2x >= 1M within 3 days, in first 30 days** - strongest new-channel evidence. Country EG. 24 long uploads in 40 d; channel long median 174K. Creator background UNKNOWN |
| DoodleSurvivals (UCXMvwFJxTp-fLF1k6qABrxg) | A3 | 2026-10-14 | 11.8K | 7 | [Zombie Outbreak Survival: Trapped In a Farm Day 1 To Day 100 (Full Movie)](https://youtu.be/9LVdlATk5Zw) (10-26, d11, 67 m, 1.28M) | one hit; channel median 29K |
| Kit vs The End (UCND-rtZrbxwcyz4qA5Bppkg) | A3 | 2026-09-27 | 13.9K | 25 | [I Survived 100 Days On A Zombie Cruise Ship...](https://youtu.be/xdj5PL0t61k) (10-24, d27, 73 m, 1.01M) | one hit; median 18K |
| Day Zero (UCU9XwWmgsDdGRHXjrE0ewmQ) | A1 | 2026-10-05 | 14.9K | 4 | [I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft](https://youtu.be/crnpqkov3ps) (10-07, d2, 52 m, 2.07M) | second video 432K; real modded gameplay + downloaded maps; country TR |
| SSundeePlus (UCXsIAx0Zcf2ObW-Lerv9Sbw) | A1 | 2026-09-18 | 582K | 17 | 10 videos >= 1M in first 30 d | **established creator spin-off - excluded as evidence for beginners** |

Priority channels without an early >= 1M (age, best long, channel long median): Beanie Survives 268 d / 2.93M / 152K (second
channel "Beanie Survives" 37 d / 533K / 9K - same brand, CA); StickFallout 343 d / 898K / 31K; Stick Through Collapse 32 d / 468K / 44K;
WhyThat 106 d / 219K / 170K; Clooless Gaming 356 d / 1.52M / 495K (facecam modded gameplay); BlakeCraft 198 d / 325K / 25K;
imKaiL00L 212 d / 2.11M / 519K (facecam multiplayer gameplay); SirCloaked 354 d / 1.23M / 473K; Smellzzy+ 161 d / 407K / 76K.
Whether any of these is backed by an existing creator: INSUFFICIENT_EVIDENCE except SSundeePlus (name) and Beanie Survives (two
channels, same brand).

## E. Content format analysis (evidence-linked)

| Video | Evidence | What is on screen | Type |
|---|---|---|---|
| Nobody Gets In - Supermarket (oXj7bWgRX_I) | STORYBOARD_SAMPLED (4 of 15 sprite sheets, 5 s/frame) | one red-cap stick survivor in illustrated, muted locations; one-word burned-in captions synced to narration; full-screen info cards ("FOOD SAFETY, POWER OFF", "4 TONS OF MEAT, MILK AND FISH", "NEW STORE POLICY: Nobody opens this. Ever.", "PROBLEM 4: THE LIVING"); crowd of stick zombies; end card "ZOMBIE OUTBREAK - THE EXPERIMENT" | **concept + story-led**: survival logic solved problem by problem; minimal animation |
| Kit vs The End - Cruise Ship (xdj5PL0t61k) | STORYBOARD_SAMPLED (4 of 49 sheets) | stick hero + dog + a cast of survivors over detailed painterly backgrounds (look AI-generated - INFERRED); DAY counter cards (0, 34...); "SKILL INFO" tip cards ("SEVEN SHORT, ONE LONG", "REACH OR THROW", "BOTTLE LENS", "Stay dark. A fire is a light."); horde set pieces | story-led with practical survival tips |
| Day Zero - Realistic Apocalypse (crnpqkov3ps) | STORYBOARD_SAMPLED (4 of 35 sheets) + description | first-person modded Minecraft with HUD, inventory screens, guns, vehicles, realistic town map; description: planned events, real gameplay, mods The Hordes/TaCZ/Immersive Vehicles | **gameplay-led** with narrated story |
| imKaiL00L - Horror One Block, Guns (1ncAcHzjW1c) | STORYBOARD_SAMPLED | facecam + multiplayer Minecraft, one-block + gun drops + horror entities | **gameplay/personality-led, concept title** |

INFERRED pattern: the new-channel winners in A3 sell a **curiosity premise ("Could you survive 30 days locked in X?") + a survival
puzzle solved step by step + a Day counter**, with cheap visuals. The appeal is the premise and the logic, not the rendering.
That premise does **not** need Minecraft gameplay. Maizen's "Zombie Outbreak" (6.49M, Minecraft animation) shows the same premise
also works in a block world - but for an 18M-sub channel (INSUFFICIENT_EVIDENCE for a new block-world channel).
Not analysed (no access): narration delivery, music, cut rhythm, comments, retention.

## F. CineFactory production feasibility

| Capability | Status | Evidence |
|---|---|---|
| Block-world 3D episodes rendered from code (three.js), Piper TTS, procedural music/SFX, captions, thumbnail | **Demonstrated, short only** | 3 finished videos 49-57 s (`tools/blockfilm/*/out/*.mp4`, OBSERVED) |
| Minecraft Java sets via datapacks (city, arena, treehouse, crowds of NoAI mobs), cinematic grade | Demonstrated as **stills**; no in-game video recorded | sheets in `tools/blockfilm/ep03_zombie_outbreak/out/` |
| Long Slide (Blender) producer, Director Cut, auto-edit, QC, policy tools | Implemented; validated for another niche, not for this one | CLAUDE.md tools table |
| Polished video > 20 min | **Missing (never done)** | longest output 57 s |
| Emotional English voice acting | Not validated (Piper voices are flat; ElevenLabs needs owner approval/credits) | - |
| 2D illustrated stick-figure pipeline | Missing (no tooling) | - |
| Real Minecraft gameplay for 100 in-game days (~33 h play) + mods | **Not possible for CineFactory**; needs a human player and owner-approved mod installs | - |
| Character consistency across episodes | Achievable in code (same rig/skins) - INFERRED | blockfilm rigs |
| Render bottleneck | not measured for long form; headless Chromium per segment, parallel | INSUFFICIENT_EVIDENCE |

Format fit: A3/A2 scripted stories = **scripted, no gameplay expectation, reusable sets, consistent characters** -> best fit.
A1/A5 = viewers expect real play and a host's reactions -> poor fit. A6/A8 = cheap but weak demand.

## G. Monetization and policy risk matrix

| Risk | A1 gameplay | A2 block-world story | A3 2D stick story | A5 horror mod | Mitigation |
|---|---|---|---|---|---|
| Mojang usage guidelines (gameplay may be monetized; "Minecraft" not the dominant name; disclaimer) | low | low-medium (original assets; avoid Mojang textures/logo) | n/a | low | own assets; disclaimer; channel name without "Minecraft" |
| Third-party maps/mods licences | **high** (Day Zero uses "All Rights Reserved" maps) | none | none | high | own sets only |
| Maizen/Verity fan IP | - | high if copied | - | medium | original cast only |
| Inauthentic / mass-produced content (YPP clarification 2026-07-16: template-based, easy-to-make-with-AI, little variation) | low | medium | **high** (lane flooded by AI tutorial clones) | low | real authorship: original scripts, varied premises, hand-directed scenes; no bulk uploads |
| Made for Kids classification (MFK lowers ad revenue) | low | **medium-high** (block-world characters read as kids) | medium | low | teen/adult survival themes, no kid-directed titles; owner sets audience honestly |
| Violence / ad suitability | medium (guns) | medium (zombie violence) | medium | medium-high | no gore in thumbnail/first 7 s; non-graphic |
| Synthetic/altered disclosure | realistic-looking alteration only (ESTIMATED from YouTube rules; not re-fetched today) | animation normally not affected | same | - | disclose AI voice if realistic |
| Copyrighted music (C418 etc.) | medium | low (procedural music) | low | medium | original music |
| Impersonation / misleading | "I survived" must be true | do not title as gameplay | do not copy Nobody Gets In branding | - | honest titles ("Zombie Outbreak: 30 Days...") |
| RPM | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | measure on own channel |

Sources: Minecraft Usage Guidelines (minecraft.net, read 2026-11-11); TechCrunch 2026-07-20 on YouTube's 2026-07-16 inauthentic-content
clarification; YouTube YPP 2027-02-01 threshold from earlier research.

## H. Investment decision

Weighted scores (0-1 per factor, INFERRED from sections C-G; evidence quality shown separately):

| Candidate | Breakout 25 | Demand 20 | Feasibility 20 | Repeatability 15 | Monetization 10 | Policy 10 | Score | Evidence quality |
|---|---|---|---|---|---|---|---|---|
| A3 2D stick survival story | 1.0 | 0.8 | 0.6 | 0.4 | 0.6 | 0.4 | **69** | medium (small n, single reading) |
| **A2/A3 hybrid: scripted survival story in CineFactory block-world 3D** | 0.5* | 0.8 | 0.6 | 0.7 | 0.5 | 0.6 | **62** | **low** (*borrowed from A3; style transfer untested) |
| A2 block-world animation (kid/family comedy) | 0.3 | 0.8 | 0.6 | 0.6 | 0.4 | 0.6 | 55 | low |
| A5 horror mod gameplay | 0.5 | 0.9 | 0.15 | 0.7 | 0.5 | 0.6 | 55 | medium |
| A1 Minecraft realistic apocalypse gameplay | 0.4 | 0.6 | 0.2 | 0.6 | 0.7 | 0.6 | 48 | medium |
| A7 engineering | 0.2 | 0.6 | 0.2 | 0.6 | 0.7 | 0.9 | 46 | low |
| A6 mystery/ARG | 0.2 | 0.3 | 0.5 | 0.4 | 0.6 | 0.7 | 40 | low |
| A8 lore | 0.0 | 0.2 | 0.7 | 0.4 | 0.6 | 0.8 | 38 | medium |

**Quyết định (Vietnamese):**
- **CHỌN CHÍNH:** Phim kể chuyện sinh tồn có kịch bản, công thức "Day-N bị kẹt ở một nơi + giải từng vấn đề", dựng bằng thế giới khối 3D
  gốc của CineFactory, dàn nhân vật cố định, tiêu đề trung thực (không ghi "I survived" như gameplay). A3 điểm cao hơn trên giấy,
  nhưng tôi **không chọn sao chép làn 2D** vì nó đang bị nhân bản bằng AI hàng loạt (rủi ro chính sách + không có lợi thế riêng);
  khối 3D + đám đông + bối cảnh lớn là thứ ta đã có và đối thủ 2D không có.
- **DỰ PHÒNG:** cùng công thức, minh họa 2D có chủ đích (không phải template AI) – nếu pilot 3D không đạt chi phí/tốc độ.
- **LOẠI:** gameplay Minecraft thật (không sản xuất được, kênh nhỏ trung vị 18K), horror mod (cần người dẫn), Mystery/ARG, Lore,
  Engineering, fan IP.
- **ĐỘ TIN CẬY: thấp–trung bình.** Công thức có bằng chứng; phong cách khối 3D cho kênh mới và năng lực làm video 20+ phút chưa chứng minh.
- **RỦI RO CHÍNH:** (1) khán giả làn này thích sự đơn giản/logic, hình khối 3D có thể không tăng CTR; (2) bị xếp "dành cho trẻ em";
  (3) làn bão hòa trước khi ta ra mắt; (4) chi phí render/giọng đọc cho 20+ phút; (5) số liệu là một lần đọc, mẫu nghiêng về video thắng.
- **ĐIỀU KIỆN TRƯỚC KHI MỞ RỘNG:** 3 pilot (mục I) phải đạt ngưỡng ở mục I; sản xuất được 1 video 12 phút trong ≤ 3 ngày công;
  QC độc lập đạt; owner duyệt đối tượng khán giả (13+).

## I. Three pilot concepts (development briefs; each tests a different hypothesis)

| | P1 - Concept-led | P2 - Character-led | P3 - Spectacle-led |
|---|---|---|---|
| Title | *Frozen Outbreak: 30 Days Locked Inside a Ski Lodge* | *Our Little Brother Is One of Them (100 Days Hiding Zu)* | *10,000 Zombies vs One Treehouse: 100 Nights* |
| Hypothesis | the proven Day-N survival-logic format works in block-world 3D | a recurring family with a secret raises retention/subs | our unique scale (sets + crowds) is the hook |
| Promise | how you would really survive 30 days in a frozen lodge as the Frostbite dead arrive | will Bin & Bo keep Zu hidden from the survivors and the cure-hunters | can one treehouse town hold against a growing horde |
| Audience | 13+ survival-curious, English | 13+ story viewers | 13+ spectacle/siege viewers |
| Length | 12 min | 25-30 min | 15-18 min |
| Structure | cold open on Day 21 crisis -> Day 0 -> 6 numbered problems (heat, food, light, noise, the living, the breach) -> Day 30 twist | 3 acts; secret, discovery, sacrifice; Day counter as spine | escalation ladder: 10 -> 100 -> 1,000 -> 10,000; each night a new defence |
| Hook (first 15 s) | "Day 21. The generator stopped. Rule 1: never open the kitchen door." | Zu's hand turns grey; Bin hides it before the survivors see | aerial of the horde reaching the palisade, counter "10,000" |
| Characters | one narrator-survivor (no recurring cast needed) | Bin, Bo, Zu (+2 survivors) | Bin, Bo, Zu as defenders |
| Visuals/sets | new lodge interior + snow arena exterior | treehouse town + city v2 | treehouse set (exists) + crowd tech |
| Sound | narration, wind bed, original music | dialogue, emotional score | battle SFX, drums |
| Thumbnail | split DAY 1 / DAY 30, lodge in blizzard, dead at the glass | Zu grey-eyed, Bin's finger to lips | treehouse vs sea of zombies, "10,000" |
| Originality | own premise/sets/cast; no Mojang assets; no copying of Nobody Gets In layout/branding | same | same |
| Complexity | medium (mostly narration + info cards + few animated beats) | high (acting, dialogue, 30 min) | high (crowd animation, many shots) |
| CineFactory readiness | closest (blockfilm short pipeline + cards) | lowest (voice acting, length) | medium (sets exist; crowd motion unproven) |
| Shorts | 2 x 45 s "Rule #N" clips | 1 x 50 s secret reveal | 2 x 40 s horde waves |
| Metrics (7 / 28 days) | CTR, average % viewed, views per impression vs our own other pilots; subs per 1K views | same + returning viewers | same |
| Continue if (proposed, owner to confirm) | >= 40% average viewed at 12 min AND top-2 CTR of the three | >= 35% average viewed at 25 min | >= 40% viewed |
| Stop if | < 25% viewed and lowest CTR after 28 days | idem | idem |

No hundreds of episodes before these three are measured. Upload only by the owner, as private drafts first.

## J. Red-team review

| Critic | Objection | Effect on decision |
|---|---|---|
| Growth analyst | A3 "winners" are what search surfaced; 21 new A3 channels in 60 days with median ~18K/video means most fail | accepted: do not expect Nobody Gets In results; pilots measure our own median |
| Minecraft specialist | a block-world look will be judged "Minecraft animation for kids" and compete with Maizen clones, not with A3 | partly accepted: P1 tests exactly this; titles/thumbnails must signal teen survival, not kids |
| Animation director | CineFactory has never finished > 57 s; 12-30 min is 15-30x more | accepted: readiness = low; P1 first, P2 last |
| Policy specialist | the A3 lane is the textbook "template, easy with AI, little variation" case | accepted: reason we don't clone 2D; every episode needs a distinct premise and real direction |
| Data auditor | 640 videos classified by keyword only; A3 n = 17 + 41 channels; single reading; RPM unknown | accepted: confidence kept low-medium |
| Investment analyst | revenue unknown; YPP needs 8,000 watch hours from 2027-02-01; long videos help watch hours | neutral: favours long-form compilations ("Full Movie") once pilots work |
| Unresolved conflict | A3 2D scores higher than the hybrid on evidence; the hybrid wins only on defensibility and policy | kept visible: if P1 underperforms 2D benchmarks, switch to the backup |

## K. Evidence and provenance

- Search: owner PC built-in browser, logged out, VN IP, YouTube results pages filtered "this month" by view count (`sp=CAMSBAgEEAE%3D`)
  and relevance (`sp=EgIIBA%3D%3D`); 49 + 14 queries; 2026-11-11 15:20-16:00Z.
- API: YouTube Data API v3 via `Downloads\cine_niche_survey\cf_mc_niche_enrich.py` (videos.list, channels.list, playlistItems.list);
  319 + 82 units; key read in-process only, never printed.
- Thumbnails: `i.ytimg.com/vi/<id>/mqdefault.jpg`; storyboards: YouTube player storyboard sprites (viewed, not saved).
- Policy: minecraft.net/en-us/usage-guidelines (2026-11-11); techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/.
- Reproduce: `python3 classify.py && python3 metrics.py && python3 z_sample.py` in `reports/research/minecraft_audit_2026-11-11/`
  with the staged copies of the PC data folders as arguments.
- Known gaps: no audio/transcripts; no retention/CTR/RPM; no historical view snapshots (1M-crossing dates UNKNOWN); creator
  backgrounds mostly unknown; A4 (independent 3D) not sampled.
