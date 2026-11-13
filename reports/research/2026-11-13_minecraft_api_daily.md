# Nghiên cứu ngách Minecraft hằng ngày – vòng 6 (2026-11-13)

> **Nguồn dữ liệu.** Đường API chính thức chạy được: PC owner (desktop-hje6a6d) có Blender 5.2.3 MCP, key chỉ đọc trong tiến trình con trên PC, không in, không ghi.
> - **Quota hôm nay gần như đã hết trước khi vòng này chạy.** Một phiên khác hôm nay (sau 08:00Z, tức đầu ngày quota Pacific) đã chạy `cf_new_channel_hunt.py` (~4.877 unit), `cf_mega_new_channel_hunt.py` (~3.845), `cf_us_eu_new_channel_deep.py` (~997), `cf_mostpopular_us_eu.py` (90). Tổng ≈ 9.809 unit (OBSERVED từ các file meta, 2026-11-13). Vì vậy vòng này **không gọi search.list** (0 lượt) để không vượt trần 10.000/ngày.
> - Vòng này chỉ chạy `cf_mc_daily_lite.py` (bản rút gọn, đặt trên PC và chép vào `reports/research/mc_daily_2026-11-13/`): **113 unit**, 0 lỗi, 11:51–11:52Z. Gồm (1) chụp lại 655 video trong các danh sách 1M+/outlier/bùng nổ/kênh nhỏ của vòng 2026-11-11 (14 unit), (2) `channels.list` + 50 upload mới nhất của **toàn bộ 44 kênh watchlist + 5 kênh ứng viên** (99 unit). Lần đầu tiên đo đủ cả watchlist.
> - **Tập tìm kiếm của ngày** = kho video mà phiên kia đã kéo hôm nay (`reports/research/new_channel_hunt_2026-11-13/hunt_15d.json` + `mega_15d.json`, publishedAfter 2026-10-29). Lọc chủ đề Minecraft + tiếng Anh còn **865 video, 629 video ≤15 ngày** (OBSERVED). Bộ từ khoá của kho này **khác** bộ 84 từ khoá hôm 11-11 (không có "zombie apocalypse", "100 days"…), nên số theo làn **không so được 1:1** với vòng trước.
> - **So sánh ngày-qua-ngày:** vòng trước là 2026-11-11 (không có vòng 11-12). Tăng trưởng đo trên cùng video, khoảng cách trung vị **2,02 ngày** (OBSERVED), không phải 24 h.
> - **CSV đã đưa vào repo** (`research_notes/Quét ngách Minecraft bằng YouTube API/data/2026-11-13/`): `resnapshot_growth_vs_2026-11-11.csv` (81 dòng: top 60 theo tốc độ + mọi video đang tăng tốc), `watchlist_channels_2026-11-13.csv` (49 kênh), `derived_mc_en_le15d_pool.csv` (629 video). CSV thô (`resnapshot.csv`, `watch_uploads.csv`) vẫn trên PC tại `Downloads\cine_niche_survey\out\2026-11-13_mc_daily_lite\` vì quyền thư mục cho phiên này **đang chờ owner bấm Allow** trên máy tính.
> - Bộ lọc: audio trống/zxx/en*, tiêu đề chữ Latin, <2 từ chức năng ngoại ngữ; Shorts = ≤180 s; cờ IP bên thứ ba bằng regex tiêu đề. Chưa xem video nào ở dạng chuyển động: cổng `competitor-complete-study` vẫn mở.

## 1. Tín hiệu mạnh nhất

**Truyện cảm xúc ngắn với mob Mojang (S17) là nhóm Shorts IP gốc đang *tăng tốc*, trong khi phần lớn mega-hit đang giảm.** Trung vị tỉ lệ "tốc độ 2 ngày qua ÷ tốc độ cả đời" là **0,20 với Shorts và 0,32 với video dài** (655 video, OBSERVED 2026-11-13). Chỉ 29 video vừa tăng tốc (≥1,0) vừa thêm >50K view. Trong số đó có:

| Video | Kênh | View 11-11 → 11-13 | Tốc độ gần đây/ngày | Tỉ lệ |
|---|---|---|---|---|
| [Baby Creeper's Last Second 💔](https://www.youtube.com/watch?v=6A_ooG234aA) (25 s) | CrafToons | 702K → 1,06M | 178K | **1,23** |
| [The Creeper Who Protected a Kitten😭](https://www.youtube.com/watch?v=ETjsctzkrQw) (32 s) | CreeperStory (16 ngày, 1,40K sub) | 379K → 436K | ~28K | — (311× sub, 7,3× median Shorts kênh) |
| [Monster school is coming](https://www.youtube.com/watch?v=u8cUwTg9bxA) (59 s) | OBITOᴳᴼᴬᵀ | 654K → 1,19M | 263K | 1,37 |
| [Herobrine is back](https://www.youtube.com/watch?v=drsSTOW7320) (83 s) | OBITOᴳᴼᴬᵀ | 301K → 587K | 142K | 1,98 |

Cùng chiều: CreeperStory đăng thêm 4 Short trong 2 ngày (tốt nhất 32K), sub 1,04K → 1,40K (+35%, OBSERVED). **Kết luận (INFERRED):** khuôn "mob Mojang + một hành động che chở/hy sinh + 15–45 s + 😭/💔" vẫn sống sau ≥1 tuần, là cửa vào rẻ nhất cho Zu.

## 2. Thay đổi so với vòng 2026-11-11 (OBSERVED, cùng video, cách ~2,02 ngày)

**Nhanh nhất tuyệt đối:**
- Sir Potato "Which One Is the FUNNIEST? 1, 2 or 3? 😂 - Maizen…" 12,5M → **25,2M** (6,26M/ngày, tỉ lệ 0,69). IP Maizen: chỉ học công thức "1, 2 or 3?".
- Joeysaf "Minecraft But Every Advancement Makes Blocks Bigger" 4,00M → **6,22M** (1,09M/ngày). Kênh này có 3 Short "Minecraft But…" 3,5–6,2M trong 15 ngày → S14 mạnh nhất hôm nay.
- Aquish "What If You Fell Overboard? 😱" 1,53M → **3,79M**, tỉ lệ **1,34** (đang tăng tốc, 61 s, IP gốc).
- JohnnyXD "How Is This Even Possible? #scary" 1,54M → **3,48M**, tỉ lệ 1,28 (kênh 9,87K sub, 350×).
- Parrot "10,000 Player Minecraft War" 21,5M → 22,8M (634K/ngày, tỉ lệ 0,33; giảm tốc mạnh từ 1,76M/ngày tuần trước).

**Đang tăng tốc đáng chú ý (tỉ lệ ≥1,15):** KRIZZIT "Daylight Edition" 4,02M (1,24); Catkin Craft "Being Left-Handed Is Overpowered" 3,52M (1,17); Cheesy Animation "No One Come to Evil JJ Birthday… 😭" 2,46M (1,31, IP JJ); HamsterWorker "PIZZA BUILD BATTLE - Noob vs Pro vs Hacker vs God" 871K (1,34); XuroBy "0$ vs 50$ vs 100000$ Rich vs Poor Civilization" 672K (1,51).

**Watchlist (đo đủ 49 kênh lần đầu, OBSERVED 2026-11-13):**
- **Kit vs The End** "I Survived 100 Days On A Zombie Cruise Ship…" đã **vượt 1M (1,06M)** ở ngày 19,7; 73,6× sub (14,4K). Kênh vẫn chỉ 1 video dài ≥1M; video mới chỉ ~19K (median video dài kênh 18,7K).
- **Marrow** "Zombie Outbreak: The Last Soldier on the Bridge, Day 1 To Day 100 (Full Story)" **402K** (275K ngày 11-06), 63× median kênh, 120× sub. Tạo kênh API ghi 2024-09-24 (cũ hơn ước tính trước; kênh tái sử dụng – INFERRED).
- **Mochi & Pals** 4,50K sub (3,88K ngày 11-11); 3 Short mới trong 2 ngày, tốt nhất 351K; "Who can dig down the fastest?" 2,92M.
- **Cube Clash** 15,8K sub (9,44K ngày 11-11, +67%); median Shorts 154K, 2 Short mới, tốt nhất 168K.
- **Ziggy Blox** 86,3K sub; 8 Short mới trong 2 ngày, tốt nhất 960K; "I Taught the Shark King to Surf 🏄" 1,85M = 37× median → POV cải trang vẫn chạy.
- **Erzxck** 36,3K sub; Short mới 1,95M (Verity, bên thứ ba).
- **Manic Craft** 12 Short mới trong 2 ngày; "grox fights against froggy…" 792K ở 3 ngày (R1+R2+R3) – nhân vật của creator thật (Grox/Froggy) → bên thứ ba.
- **Christopher Norton** (tạo 2026-10-22): "The Dream Files Just Dropped" **3,07M ở 2,8 ngày**, 61 phút, 328× sub – drama về creator thật (Dream), không hợp kênh.
- Day Zero, DL Minecraft, Zombie Days Diaries, SirCloaked, BigSchool, Cubeee, Морфиз: không có upload mới trong 2 ngày.

## 3. Đối thủ mới 0–30 ngày

- **0 kênh đạt chuẩn khắt khe** (≥2 video dài >3 phút ≥1M). Vòng thứ 6 liên tiếp. Gần nhất: Christopher Norton (22 ngày, 1 video dài ≥1M, IP creator thật).
- Kho hôm nay: video ≥1M Shorts có 3/141 từ kênh ≤30 ngày; video dài ≥1M (đã loại "TNT Village Live", xem mục 4) **36 video, chỉ 2 từ kênh ≤365 ngày, 0 từ kênh ≤90 ngày** (OBSERVED). Video dài vẫn là sân của kênh lâu năm.
- **Thêm vào watchlist (status `new`)**, ngày tạo theo `channels.list`:
  - **BlockKahani** (tạo 2026-10-24, 4,34K sub, 16 video): Short-dài 2:22 [🌕 Never Stay Awake After 9 PM… 😨 | Minecraft Horror Story](https://www.youtube.com/watch?v=a4YGrxjCvb0) **552K = 127× sub, 199× median**; [When the Bell Rings 3 Times, NEVER Stay Outside😨](https://www.youtube.com/watch?v=5h8BUpXk3EU) 350K. IP gốc. Công thức tiêu đề: "<giờ/âm thanh> + NEVER + luật sống còn + 😨".
  - **Endform TV** (tạo 2026-10-22, 7,47K sub, 41 video, đa chủ đề): [Which Block Reaches Final Form? ⛏️👑](https://www.youtube.com/watch?v=o1HxKGwLPw8) **1,16M**, 49× median, 155× sub; cùng khuôn với xe hơi 1,54M. IP gốc, Blender 3D.
- **Ứng viên chưa thêm:** Mob Problems (tạo 2026-11-04, 464 sub) "Noob vs Pro… From the Zombie's Point of View 🤣" – ý tưởng rất gần Zu nhưng tốt nhất chỉ 60K; Squishy 3D (539 sub, "Minecraft vs Real Life", tốt nhất 76K); Blokz (159 sub). Theo dõi từ dữ liệu ngày mai.
- Status `new` hôm 11-11 (CreeperStory, Cube Clash, Christopher Norton, UmangRon) → chuyển `leader`.

## 4. Video bùng nổ 0–15 ngày và trend

**Kho hôm nay (OBSERVED, tiếng Anh, Minecraft, ≤15 ngày):** 208 video ≥1M (141 Shorts, 67 dài). Shorts ≥1M: 43/141 từ kênh ≤12 tháng, 49/141 từ kênh <100K sub, 99/141 không có IP bên thứ ba trong tiêu đề. Video dài ≥100K: 15/117 từ kênh ≤12 tháng.

**Trend bắt đầu:**
- **T-new-1 "Minecraft TNT (Blast) Village Live"** – 31 video dài 45–85 phút, 5 kênh (Arytro, SILENCE GOD, BOW MC, Levi Robux, Milo), tổng 73,8M view, tất cả ≥1M. Cùng khuôn với MineBraintor – kênh đã bị xác nhận "đóng băng bộ đếm" ngày 11-04. **Nghi là bất thường bề mặt live, loại khỏi mọi trung vị** (INFERRED). Không hợp kênh.
- **T-new-2 "Night rules" horror-story Shorts** (BlockKahani 552K/350K) – gộp vào S12 làm bằng chứng IP gốc dạng Short.
- **T-new-3 "Which X Reaches Final Form?"** (Endform TV 1,16M) – tiến hoá khối/mob theo bậc, Blender 3D. Theo dõi; hợp với "thí nghiệm dị thường" (INFERRED).
- **T-new-4 Grox/Froggy** (FroggyDude VS Grox MANHUNT 2,73M; Manic Craft 792K) – nhân vật của creator thật → vào S9, chỉ học công thức.

**Trend kết thúc / đổi trạng thái:**
- **Không trend nào hết hạn** (chưa trend nào vắng 3 vòng).
- S10 (chiến tranh 10.000 người) giảm tốc rõ: Parrot tỉ lệ 0,33.
- S16 (cập nhật mùa đông 26.4) yếu: chỉ thấy video chính chủ Minecraft "Frostbite Invitational" và 1 build tuyết 388K → giữ "theo dõi".
- S7 (Zombie Outbreak): kho hôm nay không có từ khoá làn này nên **không đo được làn**; watchlist cho thấy đuôi dài vẫn tăng (Kit vs The End vượt 1M, Marrow Full Story 402K) nhưng video mới của kênh làn này vẫn thấp → giữ "đang giảm".

## 5. Top 10 video nên nghiên cứu (chỉ học công thức)

| # | Video | Kênh | Số liệu (OBSERVED 2026-11-13) | Vì sao |
|---|---|---|---|---|
| 1 | [Baby Creeper's Last Second 💔](https://www.youtube.com/watch?v=6A_ooG234aA) | CrafToons | 1,06M, tăng tốc 1,23 | S17, đang tăng |
| 2 | [The Creeper Who Protected a Kitten😭](https://www.youtube.com/watch?v=ETjsctzkrQw) | CreeperStory | 436K, 311× sub | S17, kênh 16 ngày |
| 3 | [Never Stay Awake After 9 PM… 😨](https://www.youtube.com/watch?v=a4YGrxjCvb0) | BlockKahani | 552K, 127× sub, 2:22 | Luật sống còn + đe doạ, IP gốc |
| 4 | [Minecraft But Every Advancement Makes Blocks Bigger](https://www.youtube.com/watch?v=Wy68KUz6S3s) | Joeysaf | 6,22M, +1,09M/ngày | S14 dạng Short |
| 5 | [What If You Fell Overboard? 😱](https://www.youtube.com/watch?v=FpxVsDJpuhI) | Aquish | 3,79M, tăng tốc 1,34 | "What if" + đe doạ, 61 s |
| 6 | [Which Block Reaches Final Form? ⛏️👑](https://www.youtube.com/watch?v=o1HxKGwLPw8) | Endform TV | 1,16M, 155× sub | Kênh 22 ngày, Blender |
| 7 | [I Survived 100 Days On A Zombie Cruise Ship…](https://www.youtube.com/watch?v=xdj5PL0t61k) | Kit vs The End | 1,06M, 73 phút | Video dài sinh tồn vượt 1M ở ngày 20 |
| 8 | [Zombie Outbreak: The Last Soldier on the Bridge… (Full Story)](https://www.youtube.com/watch?v=YD6g0b6WLFg) | Marrow | 402K, 63× median | Full Story thắng từng phần |
| 9 | [Who can build the best house?](https://www.youtube.com/watch?v=qLDngfY1d3o) | Mochi & Pals | 2,76M, 614× sub | S8, dàn nhân vật gốc cố định |
| 10 | [I Taught the Shark King to Surf 🏄](https://www.youtube.com/watch?v=o5W8h559S48) | Ziggy Blox | 1,85M, 37× median | POV cải trang, series ổn định |

## 6. Ý tưởng cho Bin/Bo/Zu (INFERRED; OWNER quyết)

1. **Video dài – sinh tồn có mối đe doạ + luật chơi:** "We Survived 30 Nights in a Zombie Town… The Only Rule: NEVER Wake Baby Zombie Zu"
   - Hook 0:00–0:20: chuông làng vang 3 lần, đàn zombie tràn vào; Bin và Bo phát hiện Zu ngủ say giữa đàn zombie là thứ duy nhất khiến chúng không tấn công.
   - 20–25 phút, set nhà cây có sẵn; mỗi "đêm" một luật mới (S12 + S7 có twist). Sau 3 phần ghép "Night 1 To Night 30 (Full Story)" như Marrow/Kit.
2. **Shorts phễu – S17:** series "The Baby Zombie Who… 😭" (25–40 s, gần như không lời)
   - Tập 1: "The Baby Zombie Who Gave the Creeper His Last Cookie 😭"; tập 2: "Baby Zombie Zu's Last Sunrise 💔" (Zu tránh nắng để che cho mèo con, kết ấm). 3 Short/tuần, chỉ mob Mojang + dàn của ta.
3. **"Minecraft But…" với dàn nhân vật (S14):** Short đánh số kiểu Joeysaf
   - "Minecraft But Every Time Zu Laughs, the Blocks Get BIGGER (Part 1)" – 60–150 s; Bin và Bo phải giữ Zu không cười. Nếu một tập ≥2× median 7 ngày đầu thì làm Part 2 ngay (L5).

## 7. Việc còn chặn
- **Quyết định đã ghi:** `D-cfdd4e56` (kind topic) qua `tools/cf_decision.py`. `data/` bị `.gitignore` nên file `data/decisions.jsonl` của bản clone cloud không được commit; cần ghi lại trên PC nếu muốn log thống nhất. Ba CSV ngày hôm nay được commit bằng `git add -f` vì thư mục `data/` của research_notes cũng nằm trong `.gitignore`.
- **Quota:** ngày quota 2026-11-13 đã bị phiên săn kênh mới dùng ~9,8K unit trước vòng này → không có search Minecraft riêng hôm nay. Cần thống nhất lịch: vòng Minecraft hằng ngày và các lượt săn khác không chạy cùng một ngày quota, hoặc owner xin tăng quota.
- **Quyền thư mục:** yêu cầu cấp `Downloads\cine_niche_survey\out\2026-11-13_mc_daily_lite` **đang chờ owner bấm Allow** trên máy tính (còn ~2 giờ). Khi được cấp, các vòng sau stage CSV thô trực tiếp.
- Chưa xem video nào dạng chuyển động; cổng `competitor-complete-study` vẫn mở.
