# Nghiên cứu ngách Minecraft hằng ngày – vòng 5 (2026-11-11)

> **Nguồn dữ liệu:** YouTube Data API chính thức, chạy `cf_mc_api_dataset.py` trên PC của owner (desktop-hje6a6d, Blender 5.2.3 MCP), lúc 11:19–11:25Z. Một phiên trước trong ngày đã chạy lượt này. 84 lượt search (7 và 15 ngày), 2.886 video, 1.938 kênh, uploads của 320 kênh. **Quota: 9.130 unit (OBSERVED, `run_meta.json`)**, vượt ngân sách 9.000 khoảng 130 unit. Vì vậy phiên này **không gọi thêm API** (0 unit) và chỉ phân tích lại dữ liệu đã có ngay trên PC. Key chỉ đọc trong tiến trình trên PC, không in ra, không ghi log.
> **Khoảng trống:** không có vòng nào từ 2026-11-07 đến 2026-11-10. Vì vậy "thay đổi" dưới đây so với vòng 4 (2026-11-06, đường trình duyệt) và với snapshot API 2026-11-04. Không có số 24 h. Thay vào đó là **tăng trưởng ~7 ngày**: lấy cùng một video, so số view hôm nay với snapshot 2026-11-04 (cách nhau 6,97–7,68 ngày).
> **Kết quả phân tích nằm trên PC:** `Downloads\cine_niche_survey\out\2026-11-11_api_dataset\analysis\` (gồm `A_lanes_15d.csv`, `A_outliers_3x_median.csv`, `B_new_channels_0_30d.csv`, `C_exploding_le15d_1m.csv`, `C_small_channel_vs_subs.csv`, `C_growth_vs_prev.csv`, `watchlist_status.csv`, `videos_en_tagged.csv`). **Chưa stage được** về repo vì phiên này không có thư mục nào được kết nối (`connectedFolders` rỗng). JSON thô vẫn để trên PC.
> **Bộ lọc:** chỉ giữ video tiếng Anh, tức audio trống/zxx/en*, tiêu đề chữ Latin và không có ≥2 từ chức năng ngoại ngữ. Còn 1.989/2.886. Shorts = ≤180 s. Gán cờ IP bên thứ ba bằng regex trên tiêu đề. Làn (lane) được gán bằng regex tiêu đề đơn giản, thô hơn bộ 20 mã trong file A (INFERRED). Có 762 video ≤15 ngày rơi vào "OTHER".

## 1. Tín hiệu mạnh nhất: truyện ngắn với mob Mojang làm nhân vật chính, trên kênh mới tinh

Các kênh dưới đây làm Shorts với nhân vật IP gốc hoặc mob Mojang. Kênh mới hoặc rất nhỏ, nhưng view lên gấp hàng trăm lần số sub (OBSERVED 2026-11-11):

| Kênh (tuổi kênh) | Sub | Video | View | Tuổi video | View ÷ sub |
|---|---|---|---|---|---|
| **CreeperStory** (14 ngày) | 1,04K | [The Creeper Who Protected a Kitten😭](https://www.youtube.com/watch?v=ETjsctzkrQw) (32 s) | 379K | 4,2 ngày | ~364× |
| **Mochi & Pals** (27 ngày) | 3,88K | [Who can build the best house?](https://www.youtube.com/watch?v=qLDngfY1d3o) | 2,21M | 5,6 ngày | 569× |
| **Mega Cascade** (46 ngày) | 4,89K | [Emerald City! Does the Giant Villager Keep His Emerald?](https://www.youtube.com/watch?v=qfL1sxlYqHE) | 2,67M | 7,3 ngày | 545× |
| **Cube Clash** (6 ngày) | 9,44K | [NOOB vs PRO: Who Survives the FLOOD? 🌊](https://www.youtube.com/watch?v=hq2I-CuJMUM) | 225K | 4,6 ngày | 24× |

- **CreeperStory:** 10 video. Cả series đều theo khuôn "Why X protected/raised Y 😭".
- **Mochi & Pals:** sub tăng gấp ~2 so với 1,91K ngày 2026-11-06. Median Shorts của kênh là 302K. Video "Who can dig down the fastest?" giờ đạt 2,80M.
- **Cube Clash:** cả 8 video đều là thảm họa NOOB vs PRO, mỗi video từ 76K đến 225K.

**Kết luận (INFERRED):**
- Mô hình Logetor (đã ghi ở note L ngày 2026-11-11) đang được lặp lại hằng tuần trên những kênh mới hơn nữa: một mob quen mặt + một hành động cảm xúc + 15–45 giây + emoji 😭 trong tiêu đề.
- Baby zombie Zu hợp đúng khuôn này. Đây là cửa vào rẻ nhất cho kênh của ta.

## 2. Làn Zombie Outbreak (S7) tiếp tục suy giảm

**Số liệu làn hôm nay** (OBSERVED 2026-11-11, video ≤15 ngày, tiếng Anh):
- 21 video.
- **0 video đạt ≥1M.**
- Chỉ 4 video đạt ≥100K.
- Median video dài 50K.

**So sánh:** ngày 2026-11-04 làn này có 5 video dài ≥1M (OBSERVED).

**Một ca kênh nhỏ đi ngược xu hướng:** Stickvival, 1,26K sub, video [I Built a Treehouse to Survive a Zombie Apocalypse!](https://www.youtube.com/watch?v=tqfg1i6rR40):
- 105K view sau 3,1 ngày, gấp 83 lần số sub.
- Dài 53 phút.
- Góc khai thác là xây/gia cố căn cứ. Góc này hôm 2026-11-06 cũng đã thấy ở Zombie Days Diaries.

**Kết luận (INFERRED):**
- S7 chuyển từ "bão hòa" sang **"đang giảm"**.
- Chỉ vào làn này khi có cả hai yếu tố: twist "Zu là zombie" và mục tiêu xây nhà cây. Bộ set nhà cây của pilot đã có sẵn (commit fac5eb2).

## 3. Thay đổi so với vòng trước

Số view là OBSERVED 2026-11-11. Tốc độ "gần đây" = (view hôm nay − view 2026-11-04) ÷ số ngày giữa hai lần đo. Tỉ lệ = tốc độ gần đây ÷ tốc độ trung bình cả đời video (INFERRED).

| Video | View hôm nay | Gần đây/ngày | Tỉ lệ | Đánh giá |
|---|---|---|---|---|
| Parrot "10,000 Player War: Nether VS Overworld" | 21,51M | 1,76M | 0,80 | vẫn lớn nhất |
| MSToons "YOU Trolled JJ and Mikey with Infinite Hearts!" | 6,23M | 690K | 0,98 | giữ tốc |
| Maizen "NOOB vs PRO: SAFEST GOLD SAFE BUILD" | 2,25M | 315K | 0,98 | giữ tốc |
| Sticks "If Technoblade's Life Was a Movie…" | 5,41M | 283K | 0,57 | giảm tốc |
| Carry Depie "Hiding in a SECRET BASE INSIDE the TOILET" | 2,87M | 281K | 0,78 | |
| ProBoiz 95 "Testing Trending Minecraft Scary Myths…" | 8,06M | 229K | 0,39 | giảm mạnh |
| MSToons "JJ BUS EATER was Buried Under The Water" | 2,55M | 149K | 0,63 | S2 nguội dần |
| Carry Depie "Minecraft, But Your Hearts = Realism…" | 3,77M | 141K | 0,45 | |

**Đang tăng tốc (tỉ lệ ≥1):**
- Milo and Chip (4,86M sub):
  - "PARENTS vs KIDS Speedrunners in Minecraft" 1,27M, tỉ lệ 1,23.
  - "NOOB vs PRO: VERITY Safest Security House Build Challenge to Protect My Family" 1,31M, tỉ lệ 1,29. Video này có Verity, nên chỉ học công thức.
- SLUURP "A MINECRAFT MOVIE 2: SQUARED… 5 Mob Pitches" 815K, tỉ lệ 1,22.
- ZZILCO "Delicious Verity COMPLETE EDITION" 1,16M.
- Ligabka "MAIZEN - JJ and Love JJ SISTER" 2,63M, tỉ lệ 1,2 dù video đã 67 ngày tuổi.

**Kết luận (INFERRED):** các video "gia đình chơi cùng nhau" (bố mẹ vs con, bảo vệ gia đình) đang tăng tốc, trong khi hầu hết mega-hit khác đều giảm tốc.

**Watchlist (OBSERVED 2026-11-11):**
- Erzxck: 30,8K sub (17,7K ngày 2026-11-04). Short Verity 14,04M.
- Verity Verifies MC: 2,78K sub. Short 3,24M, gấp 116 lần median của kênh.
- Bench Animation: 258K sub. "No One Helped Dark JJ…" 2,37M.
- Wablo: 287K sub. "Creator just wanted to do his job" 5,16M.
- Ziggy Blox: 80,9K sub.
- **Lượt API hôm nay chỉ kéo được uploads của 19/40 kênh trong watchlist.** Lượt này không có nhóm "toàn bộ watchlist". Các kênh Marrow, Zombie Days Diaries, Day Zero, Nobody Gets In, Beanie Survives, SirCloaked, Kit vs The End… không được đo lại hôm nay.

## 4. Đối thủ mới 0–30 ngày (ngày tạo kênh lấy từ `channels.list publishedAt`, OBSERVED)

- 89 kênh mới 0–30 ngày trong mẫu. **0 kênh đạt chuẩn khắt khe** (≥2 video dài >3 phút ≥1M). Đây là vòng thứ 5 liên tiếp không có kênh nào đạt.
- Hai kênh gần chuẩn nhất đều không hợp làn của ta:
  - **Christopher Norton** (tạo 2026-10-22, 4,16K sub): 10 video dài, 5 video ≥100K. Video tốt nhất "The Dream Files Just Dropped" 904K, dài 61 phút. Đây là drama về creator có thật (Dream), nên không hợp kênh.
  - **UmangRon** (tạo 2026-11-06, 412 sub): "i FOUND the SCARIEST TRALALELO TRALOLA 😱 in Minecraft!" 179K, dài 22 phút, gấp 435 lần số sub. IP brainrot của bên thứ ba.
- **Thêm vào watchlist 4 dòng mới**, trạng thái "new":
  - CreeperStory: IP gốc, mob Mojang.
  - Cube Clash: IP gốc, NOOB vs PRO thảm họa.
  - Christopher Norton: chỉ theo dõi, bên thứ ba.
  - UmangRon: chỉ theo dõi, bên thứ ba.
- Hai dòng "new" từ ngày 2026-11-06 (Marrow, Zombie Days Diaries) chuyển sang "leader".

**Công thức của kênh mới (INFERRED, chỉ từ tiêu đề và độ dài, chưa xem video):**
- CreeperStory: "The <mob> Who <hành động che chở> <con vật nhỏ>😭", dài 30–32 s, không lời (đoán).
- Cube Clash: "NOOB vs PRO: Who Survives the <thảm họa>? <emoji>", dài 45 s, đăng 8 video trong 6 ngày, đổi thảm họa mỗi tập.

## 5. Video bùng nổ 0–15 ngày (OBSERVED 2026-11-11)

**Tổng quan:** 384 video tiếng Anh ≥1M view. Trong đó 66 video dài, còn lại là Shorts.

**Video dài nhanh nhất:**

| Video | View | Tuổi | Ghi chú |
|---|---|---|---|
| ProBoiz 95 "I Can Turn Any BLOCK into GUN" | 3,95M | 2,9 ngày | |
| Maizen "Dinosaur Horror Mod" | 2,51M | 3,4 ngày | |
| Junkeyy "I OPENED A FIRECRACKER SHOP" | 1,48M | 2,9 ngày | |
| LazarLazar "I Tricked My Wife Into Playing Minecraft Horror" | 1,38M | 3,2 ngày | |
| Karry Kraft "We Found Horrifying Cat in the Hat…" | 1,19M | 3,0 ngày | IP bên thứ ba |
| Clooless Gaming "Beating Minecraft With The Phobia Mod" | 1,51M | 13,5 ngày | 3,1× median kênh |

**Kênh nhỏ có video dài gấp nhiều lần số sub:**
- MineQuest Tales: Steve nấu ăn kiểu ASMR, 257K trên 776 sub, gấp 332 lần.
- TwoBelow: "Manhunt, But I Can't See My Hunger Bar" 201K, gấp 343 lần.
- KnightMC: "Surviving 500 Days LOST AT SEA", dài 3,6 giờ, 192K, gấp 48 lần.

**Trend mới, IP meme bên thứ ba:** "Polar Bear 2026 / Elephant 2028 / Bird 2027".
- 36 video, tổng 37,4M view, 21 kênh, 13 video ≥1M.
- Ví dụ: Alexa - Minecraft có 5 Shorts "Lava Maze" từ 2,7M đến 5,9M; Mr Muscle 1,69M trên 27,6K sub.

## 6. Trend bắt đầu / kết thúc

**Bắt đầu:**
- **S15 – Meme "Polar Bear 2026 / Elephant 2028":** đang nóng, không hợp kênh (meme bên thứ ba).
- **S16 – Bản cập nhật mùa đông 26.4 (zombie Frostbite, Ice Caves, băng giòn):**
  - Bằng chứng: Vivilly "Minecraft, But the World is Brittle Ice…" 1,46M; Mogswamp "Ice Caves in superflat?!" 818K.
  - Trạng thái: theo dõi. Dùng được, vì đều là mob và block của Mojang.
- **S17 – Truyện cảm xúc ngắn với mob Mojang ("The Creeper Who…😭"):** đang nóng, dùng được. Đây là khuôn mẫu trực tiếp cho Zu.

**Đổi trạng thái:**
- S7 chuyển sang **đang giảm**.
- S8 ("Who can…" và NOOB vs PRO dạng Shorts) nâng từ "theo dõi" lên **đang nóng**:
  - Làn KIDS_CHOICE có median 534K.
  - 69% số hit ≥100K đến từ kênh dưới 100K sub.
  - Có thêm Cube Clash.
- S13 (gia đình) có thêm bằng chứng: các video gia đình của Milo and Chip đang tăng tốc.

**Không có trend nào hết hạn.** S6 (Halloween) đã hết hạn từ trước. Các trend S1–S5 và S9–S14 đều thấy lại hôm nay.

**Chưa nâng trend nào thành nguyên tắc dài hạn.** S7 đã 5 tuần nhưng đang giảm. Các trend khác mới 1–2 tuần.

## 7. Top 10 video nên nghiên cứu (chỉ học công thức, không sao chép)

| # | Video | Kênh | Số liệu | Vì sao |
|---|---|---|---|---|
| 1 | [The Creeper Who Protected a Kitten😭](https://www.youtube.com/watch?v=ETjsctzkrQw) | CreeperStory | 379K, 32 s | Khuôn S17 |
| 2 | [Who can build the best house?](https://www.youtube.com/watch?v=qLDngfY1d3o) | Mochi & Pals | 2,21M | Khuôn S8, IP gốc |
| 3 | [Emerald City! Does the Giant Villager Keep His Emerald?](https://www.youtube.com/watch?v=qfL1sxlYqHE) | Mega Cascade | 2,67M, 545× sub | Mob Mojang làm nhân vật chính |
| 4 | [I Built a Treehouse to Survive a Zombie Apocalypse!](https://www.youtube.com/watch?v=tqfg1i6rR40) | Stickvival | 105K, 83× sub, 53 phút | Cùng set nhà cây với ta |
| 5 | [NOOB vs PRO: Who Survives the FLOOD?](https://www.youtube.com/watch?v=hq2I-CuJMUM) | Cube Clash | 225K | Kênh mới 6 ngày |
| 6 | [Hiding in a SECRET BASE INSIDE the TOILET](https://www.youtube.com/watch?v=ex6bMmddjSs) | Carry Depie | 2,87M | S1, nơi chật hẹp |
| 7 | [PARENTS vs KIDS Speedrunners in Minecraft](https://www.youtube.com/watch?v=HZAi5SS3QoA) | Milo and Chip | 1,27M | Đang tăng tốc, tỉ lệ 1,23 |
| 8 | [Minecraft but you Can Equip Anything!](https://www.youtube.com/watch?v=45cS67nDAmk) | Karry Kraft | 1,59M | S14 |
| 9 | [Beating Minecraft With The Phobia Mod](https://www.youtube.com/watch?v=fHGRgKgIbAU) | Clooless Gaming | 1,51M, 3,1× median | Video dài high-concept |
| 10 | [STEVE OPENS A MYSTERY CHEST… THEN COOKS…](https://www.youtube.com/watch?v=o_L6iVrhvDA) | MineQuest Tales | 257K, 332× sub | S5, ấm áp |

Mọi nhận định về nhịp, diễn xuất và âm thanh vẫn là giả thuyết cho tới khi qua cổng `competitor-complete-study`.

## 8. Ý tưởng cho Bin/Bo/Zu (INFERRED; OWNER quyết)

1. **Video dài, sinh tồn có mối đe dọa (S7 + S1, có twist):** "We Built a Treehouse to Survive the Zombie Apocalypse… But Our Little Brother IS a Zombie"
   - Hook ở 0:00–0:20: đàn zombie kéo tới lúc đêm đầu tiên. Zu đứng *bên ngoài* hàng rào và đàn zombie coi Zu là đồng loại.
   - Dài 20–30 phút, dùng set nhà cây của pilot.
   - Sau 3 phần thì làm bản "Day 1 To Day 100 (Full Story)".
2. **Shorts funnel, nhân vật gốc (S17):** series "The Baby Zombie Who Protected a Kitten 😭"
   - 30–45 giây, gần như không lời. Zu che chở một mob con.
   - Các tập sau đổi con vật/mob: "Why the Iron Golem Let Zu Stay 😭", "Zu Was Raised by Chickens 😭".
   - 3 Short mỗi tuần, chỉ dùng mob Mojang.
3. **"Minecraft, But…" với dàn nhân vật của ta (S14 + S16):** "Minecraft, But Zu Turned Into a FROSTBITE Zombie…"
   - Bin và Bo phải giữ ấm cho Zu trong Ice Caves.
   - Dài 10–14 phút. Nên ra trước khi bản 26.4 phát hành (Beebom đoán ~giữa tháng 12, chưa xác nhận).
   - Short đi kèm (S8): "Who can build the warmest igloo? Bin vs Bo vs Zu".

## 9. Việc còn chặn
- **Quota:** lượt chạy sáng nay đã dùng 9.130 unit, vượt ngân sách 9.000. Vì vậy hôm nay không có re-snapshot 24 h và không quét riêng 21 kênh watchlist còn thiếu. Ngày mai cần thêm nhóm "toàn bộ watchlist" vào `cf_mc_api_dataset.py`, khoảng 80 unit.
- **Không stage được CSV** về `research_notes/.../data/2026-11-11/`, vì phiên chưa được nối thư mục `Downloads\cine_niche_survey` (`connectedFolders` rỗng). Owner cần cấp quyền thư mục này trong app desktop để vòng sau stage được.
- Khoảng trống 2026-11-07 đến 11-10 không có vòng nào, nên chuỗi so sánh ngày-qua-ngày bị đứt.
- Chưa xem video nào ở dạng chuyển động. Cổng `competitor-complete-study` vẫn mở.
