# Algrow Channel Trends "minecraft" — SHORTS: lọc tuổi kênh 30 → 1 ngày, kiểm lại bằng API (13/11/2026)

## Cách làm (OBSERVED)
- Trang Algrow Channel Trends, tab Shorts, `q=minecraft`, ngôn ngữ English, sort view 24h. Đây là phiên Algrow chủ kênh đã đăng nhập, chỉ đọc.
- Đọc JSON `/channels?...&adv_max_age=N` (20 kênh/trang, lật đến khi trang <20) cho N = 30, 29, … , 1. Gộp lại được **398 kênh khác nhau**.
- Lấy tuổi thật bằng YouTube Data API `channels.list` (`snippet.publishedAt`): **383/398 kênh** có ngày tạo (15 kênh không trả về). File: `algrow_shorts_trends_channel_ages.json`.
- **Giới hạn:**
  - Trường `view_increase_24h` / `views_24h_cached` của Algrow **rỗng với 397/398 kênh** (chỉ JataZ có: 87,5K). Vì vậy KHÔNG xếp được theo view 24h như bản longform; tôi xếp theo **view/ngày = tổng view ÷ tuổi thật** (INFERRED, một lần chụp; kênh tạo trước rồi mới đăng thì con số này bị thấp đi).
  - Ngách được tôi phân loại bằng tiêu đề video gần đây (INFERRED), không phải nhãn của Algrow.
  - Chỉ là kênh Algrow đã lập chỉ mục cho từ "minecraft"; các kênh 3D loop không gắn chữ minecraft không có ở đây.

## Số kênh theo bộ lọc tuổi của Algrow (OBSERVED)

| Mốc ≤ (ngày) | 30 | 29 | 28 | 27 | 26 | 25 | 24 | 23 | 22 | 21 | 20 | 19 | 18 | 17 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Số kênh | 398 | 390 | 373 | 355 | 339 | 318 | 302 | 287 | 271 | 256 | 237 | 219 | 198 | 179 | 152 |

| Mốc ≤ (ngày) | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Số kênh | 138 | 127 | 106 | 85 | 80 | 65 | 50 | 41 | 26 | 16 | 9 | 5 | 0 | 0 | 0 |

## Kiểm tuổi thật bằng API (OBSERVED)

| Tuổi thật | ≤7 ngày | 8–15 | 16–30 | 31–90 | 91–365 | >365 |
|---|---|---|---|---|---|---|
| Số kênh (trong 383) | 13 | 44 | 122 | 44 | 44 | 116 |

- **Chỉ 179/383 kênh (47%) thật sự tạo ≤30 ngày.** 204 kênh là tài khoản cũ, cũ nhất 6.750 ngày (~18 năm).
- Algrow đo "Channel age = từ video đầu tiên", nên tài khoản cũ đổi hướng sang Shorts Minecraft cũng hiện là "mới". Giống kết luận ở `report.md` và `channel_trends_report.md`.

## Bảng 1: kênh mới thật (≤30 ngày) theo ngách

Cột "View/ngày" và "TB/video" là trung vị trong ngách (INFERRED từ số OBSERVED).

| Ngách | Kênh mới thật | Trong đó ≤15 ngày | Tổng view cả ngách | View/ngày (trung vị) | TB view/video (trung vị) | Outlier tốt nhất (trung vị) | Kênh dẫn đầu |
|---|---|---|---|---|---|---|---|
| Truyện / POV / cảm xúc | 47 | 19 | 7,1M | 5,7K | 6K | 2,5× | arminol 0,6M · nostalgia.archive 0,5M · Minecraft Tales 0,5M |
| Build / mẹo / hướng dẫn | 58 | 16 | 6,8M | 3,6K | 4K | 2,1× | RugeRyse 0,8M · Blockalation 0,5M · MR PIXEL 0,4M |
| IP khác / brainrot (Sonic, Roblox, Tom & Jerry, Sprunki…) | 35 | 10 | 4,6M | 4,4K | 7K | 2,8× | FUNYUN CRAFT GUESS 0,7M · Cube Rivals 0,5M |
| Kinh dị | 19 | 5 | 1,7M | 2,8K | 3K | 1,7× | DD Pro Clips 0,4M · Mezzy 0,3M |
| Satisfying / vật lý / mô phỏng | 8 | 2 | 1,4M | 4,8K | 7K | 1,4× | LoopCraft 3D 0,6M |
| IP JJ / Mikey / Maizen | 5 | 2 | 0,7M | 8,4K | **19K** | 2,4× | Hoxami 0,3M |
| Thử thách / đấu | 3 | 1 | 0,4M | 1,9K | 1K | 1,5× | Zakpg Blox 0,4M |
| Khác (SMP clip, meme…) | 4 | 2 | 0,6M | — | — | — | sniffer 0,2M |

- **Trong danh sách Algrow này**, không có kênh Shorts mới thật nào đạt 1M tổng view. Lớn nhất: RugeRyse 830K (29 ngày). Danh sách Algrow lại **bỏ sót** các kênh mới đã có Short triệu view mà API tìm được; xem mục "Đính chính" cuối file.
- Tổng cả 179 kênh mới thật ≈ 23M view. 40/179 (22%) dựa vào IP người khác.

## Bảng 2: top kênh mới thật theo view/ngày (OBSERVED, view/ngày INFERRED)

| Kênh | Tuổi thật | Sub | Tổng view | Video | View/ngày | TB/video | Ngách | Short lớn nhất | Dùng được cho CINE? |
|---|---|---|---|---|---|---|---|---|---|
| **Blockalation** | 7 | 789 | 499K | 11 | **71K** | 45K | Build bí mật | "How to build a base NOBODY can find" 110K, 60 s | ✓ nhưng cần quay trong game |
| Hoxami | 5 | 942 | 252K | 6 | 50K | 42K | JJ/Maizen | "JJ & Sister Save Mikey from LAVA!" 99K | ✗ IP |
| **Mob Problems** | 9 | 469 | 402K | 19 | **45K** | 21K | POV của mob | "Minecraft Mobs When the Player Puts Torches EVERYWHERE" 48K | ✓✓ Nhân vật gốc được |
| Diep Diep 2 | 5 | 92 | 214K | 8 | 43K | 27K | Tom & Jerry/FNF | 77K | ✗ IP |
| Steve & Noob Show | 9 | 352 | 285K | 17 | 32K | 17K | Noob vs pro | "Never let a Noob dig straight down" 30K | △ Khuôn quen, trẻ em |
| RugeRyse | 29 | 1,8K | 830K | 29 | 29K | 29K | Meme build | 35K | △ |
| arminol | 21 | 162 | 572K | 22 | 27K | 26K | Clip 5 s emoji | 69K | △ Không có danh tính |
| **LoopCraft 3D** | 26 | 133 | 640K | 28 | 25K | 23K | 3D loop | "Watch This Minecraft Loop Until It Resets" 27K, 7 s | ✓ Blender, nhưng sub rất thấp |
| nostalgia.archive | 20 | 240 | 488K | 21 | 24K | 23K | Hoài niệm game | "Hill Climb Racing is a core memory" 38K | ✗ Game người khác |
| FUNYUN CRAFT GUESS | 29 | 476 | 662K | 64 | 23K | 10K | Đoán nhân vật Sonic | 35K | ✗ IP |
| Cube Rivals | 25 | 688 | 469K | 25 | 19K | 19K | Roblox vs Minecraft | 35K | ✗ IP Roblox |
| Snoof | 12 | 1,1K | 220K | 9 | 18K | 24K | "In This World…" | "Liars Glow Red…" 34K, 90 s | ✓ Khuôn premise |
| DD Pro Clips | 23 | 200 | 416K | 24 | 18K | 17K | Ảo giác / kinh dị nhẹ | "This Minecraft Illusion Broke My Brain" 28K | ✓ |
| Minecraft Tales | 27 | 1,7K | 457K | 27 | 17K | 17K | Truyện kịch tính | "Prisoners did the UNTHINKABLE…" 34K | △ |
| AnyAnimations | 14 | 269 | 224K | 8 | 16K | 28K | Animation POV | Animal Crossing 52K | △ Game khác |
| Respawn Crew | 18 | 317 | 283K | 24 | 16K | 12K | Hội bạn relatable | "Every Friend Group When ONE Guy Won't Sleep" 32K | ✓✓ |
| Doomy Animation | 4 | 412 | 63K | 5 | 16K | 13K | Animation cảm xúc | "They LET Dex Sink…" 29K, 58 s | ✓ Nhân vật gốc |
| ZekoCraftz | 13 | 520 | 163K | 11 | 13K | 15K | "In This Village…" | "Your Name Is Your Power…" 27K | ✓✓ |
| Mr Burger \| Gaming | 29 | 3,6K | 386K | 37 | 13K | 10K | Build theo yêu cầu | 147K, outlier **14×** | △ Có mặt người/giọng thật |
| CubbyEra | 5 | 259 | 56K | 5 | 11K | 12K | "In This World…" | "You Become the LAST Thing You Touched…" 54K, 106 s | ✓✓ |
| Parablock | 15 | 227 | 107K | 11 | 7K | 8K | Truyện mẹo | "Make the King Say 'That's a Lie'…" 38K | ✓ |

## Bảng 3: tài khoản cũ Algrow ghi là "mới" (tham khảo định dạng, không phải bằng chứng kênh mới thắng)

| Kênh | Tuổi Algrow | Tuổi thật | Tổng view | TB/video | Định dạng |
|---|---|---|---|---|---|
| JataZ | 29 | 56 | 2,9M | 109K | Map art animation (snowman × Loki = IP) |
| Blocky JJ & Mikey | 13 | 52 | 2,1M | 42K | IP JJ/Mikey |
| Fleeki_Gamer | 29 | 41 | 1,7M | 45K | Meme dân làng ("Villager issue" 272K) |
| Bear Adventure_World | 24 | 164 | 1,2M | 21K | Super Bear Adventure vs Minecraft (IP) |
| Trolld Media | 29 | 2.074 | 1M | 30K | Meme giọng narrator |
| analog | 19 | 41 | 0,7M | 36K | Mẹo PvP |
| Gatoli Explains | 19 | 36 | 0,6M | 27K | Giải thích "The Far Lands" |
| Vessendor | 30 | 915 | 0,6M | 26K | Drama DonutSMP (creator thật) |

## Đọc số liệu (INFERRED, chủ kênh quyết)

**1. Shorts Minecraft cho kênh mới: lên nhanh nhưng nhỏ.**
- Trung vị kênh mới thật chỉ khoảng 3–6K view/ngày; kênh tốt nhất khoảng 71K/ngày.
- Từ 1/2/2027, kênh mới cần 20M view Shorts trong 90 ngày (≈222K/ngày) để vào YPP. **0/179 kênh đạt mức đó.**
- Tiền Shorts ≈ $0,03–0,10/1K view (ESTIMATED). 5,7K view/ngày ≈ 171K/tháng ≈ $5–17/tháng sau khi đã vào YPP.
- Chuyển đổi sub rất thấp: Blockalation 789 sub trên 499K view, LoopCraft 3D 133 sub trên 640K view.
- **Shorts Minecraft dùng để kéo khán giả về longform, không phải nguồn tiền chính.** Khớp với `channel_trends_report.md`, nơi các kênh longform mới (Soup Theory, History in Minecraft, Mr. Aftermath) có outlier 9–10×.

**2. Xếp hạng ngách Shorts cho kênh mới muốn bền và lớn lên:**

| Hạng | Ngách / định dạng | Bằng chứng (OBSERVED) | Vì sao bền | CINE làm được bây giờ? |
|---|---|---|---|---|
| 1 | **"In This World / In This Village…" — Shorts premise thế giới kỳ lạ** (60–110 s) | CubbyEra 54K ở 5 ngày; Snoof 24K TB/video; ZekoCraftz 15K TB; Parablock 38K | Mỗi tập một luật thế giới mới nên không vi phạm "same situation same outcome". Dễ nối thành tập dài / lore kênh. | ✓ Blender + nhân vật gốc + voice |
| 2 | **POV mob / hội bạn relatable** (20–60 s) | Mob Problems 45K/ngày ở 9 ngày; Respawn Crew 16K/ngày | Dàn nhân vật cố định (mob gốc) tạo danh tính → sub. Hài, không cần IP. | ✓ Blender, cần dàn nhân vật |
| 3 | **Animation cảm xúc nhân vật gốc** (≤60 s) | Doomy Animation 16K/ngày ở 4 ngày; AnyAnimations 28K TB/video | Cảm xúc + nhân vật quen → follow theo series | ✓ Nhưng tránh cảm xúc ép buộc |
| 4 | **Ảo giác / kinh dị nhẹ** (10–20 s) | DD Pro Clips 18K/ngày; ngách kinh dị 19 kênh mới | Phễu sang horror longform (L1/L2) | ✓ |
| 5 | **Base bí mật / build mẹo** (≤60 s) | Blockalation 71K/ngày, TB 45K ở 7 ngày | Mẹo có ích → lưu, chia sẻ | ✗ Chưa: cần quay trong game (Fabric/Flashback/WorldEdit chưa cài) |
| 6 | **3D loop / satisfying theme Minecraft** (5–10 s) | LoopCraft 3D 640K/26 ngày | View nhanh, nhưng 133 sub → không có danh tính | ✓ Blender, chỉ làm phụ |

**3. Tránh:**
- JJ / Mikey / Maizen (Hoxami TB 42K, cao nhất, nhưng là IP người khác).
- Brainrot / Sonic / Roblox vs Minecraft / Tom & Jerry / Sprunki (MR PIXEL "Stick War", Moxira "Oren x Wenda x Vineria"): 22% kênh mới dựa vào IP.
- Hoài niệm game khác (Hill Climb Racing, Animal Crossing): dùng hình game người khác.
- Spam "Duel now vs then" (Elshod: 69 video, TB 4K) và mồi "Don't say aww".
- Drama về creator thật (DonutSMP, Dream).

## Việc tiếp theo
- Chụp lại cùng danh sách sau 3–7 ngày để có view/ngày thật (Algrow không trả về view 24h cho Shorts).
- Nếu chủ kênh chọn hạng 1 hoặc 2: showrunner làm 5 Shorts pilot nhân vật gốc, mỗi Short một luật thế giới khác nhau, đo view 48 giờ và sub/1K view.

## Đính chính 13/11 (OBSERVED): kênh Minecraft mới có Short triệu view, Algrow bỏ sót

Kiểm lại dữ liệu API cùng ngày (`new_channel_hunt_2026-11-13/channels_merged.json`, 2.360 kênh có ngày tạo thật; các báo cáo `2026-11-1x_minecraft_api_daily.md`). Không kênh nào dưới đây có trong 398 kênh Shorts của Algrow (đã tra trong phiên trình duyệt).

**Kênh tạo ≤30 ngày, có Short ≥1M hoặc tổng view ≥1M:**

| Kênh | Ngày tạo (tuổi) | Sub | Tổng view kênh | Video | Short lớn nhất | IP |
|---|---|---|---|---|---|---|
| **Mochi & Pals** | 15/10 (29 ngày) | 4,5K | 9,79M | 17 | "Who can dig down the fastest?" 2,92M; "Who can build the best house?" 2,76M | ✓ Dàn nhân vật gốc |
| **Endform TV** | 22/10 (22 ngày) | 7,4K | 6,33M | 41 | "Which Block Reaches Final Form? ⛏️👑" 1,16M | ✓ Khối Mojang, kênh đa chủ đề |
| DiaxGold Crafts | 31/10 (13 ngày) | 6,3K | 3,65M | 6 | JJ & JJ Sister… 2,15M | ✗ IP JJ/Maizen |
| Brawl Lab | ~12/10 (23 ngày khi đo 04/11) | — | — | — | "6 Overworld Mobs vs 6 Nether Mobs — Who Wins?" 1,85M | ✓ Mob Mojang |
| **Cube Clash** | 05/11 (8 ngày) | 15,4K → 15,8K | 1,36M | 10 | "NOOB vs PRO: Who Survives the FLOOD?" 341K (chưa có Short 1M) | ✓ Gốc |
| BlockKahani | 24/10 (20 ngày) | 4,3K | 0,94M | 16 | "Never Stay Awake After 9 PM… 😨" 552K | ✓ Kinh dị luật đêm |

**31–60 ngày:** Gargamel Land (56 ngày, 28M, "Dropping Minecraft Cake on Alex" Blender 3,28M); Mrjunaid Short (51 ngày, 26,4M, 4,62M); Erzxck (32 ngày, 38,7M, 2,44M, nhân vật "Verity", cần kiểm IP); Mr MushMoo và Bench Animation (IP JJ/Maizen).

**Bị tưởng là kênh mới nhưng tài khoản cũ:** JohnnyXD (tạo 2021, Short 3,48M); VOXCRASH (224 ngày, 7,86M); UnVoidMC (572 ngày); ArtikAnimates (1.092 ngày); Blendverse 3D (88 ngày, 8,68M).

**Sửa lại kết luận (INFERRED):**
- Kênh Minecraft mới **có thể** có Short triệu view trong 2–4 tuần. Mochi & Pals có 2 Short gần 3M sau 29 ngày.
- Điểm chung của các kênh thắng: **dàn nhân vật gốc + câu hỏi thi đấu / tiến hoá** ("Who can…?", "Which X reaches Final Form?", "Mobs vs Mobs — Who Wins?", "NOOB vs PRO: Who Survives…?"), làm bằng 3D.
- Câu "Shorts Minecraft lên nhanh nhưng nhỏ" chỉ đúng với **trung vị** kênh mới. Phần đuôi trên thì lớn hơn nhiều.
- Tiền vẫn nhỏ: chưa kênh mới nào đạt mức YPP 2027 (20M/90 ngày). Mochi & Pals 9,79M sau 29 ngày là gần nhất, ≈ nửa đường.
- **Bài học về công cụ:** chỉ dùng Algrow Channel Trends để quét ngách là thiếu. Cần quét `search.list` theo view, rồi kiểm tuổi bằng `channels.list`.

## File
- `algrow_shorts_trends_channel_ages.json`: tuổi thật (ngày) của 383 kênh, khóa là channel ID.
- Dữ liệu từng kênh (398 dòng) nằm trong phiên trình duyệt; các bảng trên là bản trích.
