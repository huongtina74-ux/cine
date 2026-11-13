# Algrow: Minecraft, kênh "≤30 ngày" quét từ 30 về 1 ngày, đối chiếu tuổi kênh bằng YouTube API (13/11/2026)

## Cách làm (OBSERVED)

### Bộ lọc
Giữ đúng bộ lọc owner đã đặt trên Algrow (`/viral`):
- type = longform
- search = MINECRAFT
- min_video_views = 10.000
- max_upload_date = 21 ngày
- languages = English
- sort = similarity

### Quét theo tuổi kênh
- Lần lượt đặt `max_channel_age` = 30, 29, … 1.
- Mỗi mốc lấy hết các trang, mỗi trang 24 video, qua chính API mà trang Algrow dùng trong phiên đăng nhập của owner.
- Từ đó gán mỗi video vào **mốc tuổi nhỏ nhất** mà nó còn xuất hiện.

**Số video theo mốc (Algrow):**

| ≤30 | ≤25 | ≤20 | ≤15 | ≤12 | ≤10 | ≤7 | ≤5 | ≤3 | ≤2 | ≤1 |
|---|---|---|---|---|---|---|---|---|---|---|
| 120 | 107 | 89 | 44 | 34 | 16 | 10 | 4 | 1 | 0 | 0 |

### Quét thêm Shorts
- Cùng bộ lọc nhưng đổi type sang Shorts, ở mốc ≤30 ngày.
- Lấy 605 video từ 117 kênh. Mốc 30 và 29 đều chạm trần 25 trang, nên con số thật có thể còn cao hơn.

### Đối chiếu tuổi kênh
- Dùng YouTube Data API `channels.list` lấy `snippet.publishedAt` (ngày tạo kênh), tốn 3 unit.
- File kết quả: `algrow_longform_channel_ages.json` và `algrow_shorts_channel_ages.json`.

## Phát hiện số 1: "Channel age" của Algrow không phải ngày tạo kênh (OBSERVED)

**Video dài (Longform):**
- Có 57 kênh Algrow xếp là "≤30 ngày". Theo API, chỉ **31 kênh thật sự ≤30 ngày**.
- 26 kênh còn lại là tài khoản cũ:

  | Kênh | Algrow xếp vào | Tuổi thật (API) |
  |---|---|---|
  | SmartyCraft | ≤12 ngày | 1.008 ngày |
  | V4NITY | — | 1.763 ngày |
  | Waffy | — | 885 ngày |
  | Ivan Kuria | — | 192 ngày |
  | Bingis | — | 3.568 ngày |
  | TwoBelow | — | 2.742 ngày |
  | RedMinecraft | — | 1.261 ngày |

**Shorts:**
- 115 kênh Algrow ghi "≤30 ngày" thì **chỉ 12 kênh thật sự ≤30 ngày**, và 5 kênh ≤15 ngày.

**Suy luận (INFERRED):** Algrow tính ngày từ lúc kênh "bắt đầu" (có lẽ là video công khai đầu tiên hiện còn), không phải ngày tạo tài khoản. Vì vậy danh sách "kênh mới" của Algrow lẫn nhiều tài khoản cũ đã xóa video, đổi tên hoặc mua lại. **Muốn biết kênh nào mới thật thì phải kiểm lại bằng API.**

## Video dài: chỉ giữ kênh mới thật (≤30 ngày theo API) — 68 video, 30 kênh

### Theo ngách con của Algrow

| Ngách con | Video | Kênh | Trung vị view | Trung vị outlier | Tổng view 24h | % dùng IP người khác | Kênh tiêu biểu |
|---|---|---|---|---|---|---|---|
| minecraft roleplay | 15 | 8 | 38K | 1,89× | 210K | **87%** | Banazen Craft, Mikey Chilly, Old Stories From JJ And Mikey |
| minecraft animation(s) | 24 | 4 | ~44–52K | 1,1–1,7× | 187K | **60–78%** | VODCRAFT, Mix Funny (VN), จันจิรา |
| minecraft battles | 3 | 3 | 17K | 0,9× | 11K | 100% | Maikey Friends, Mikey Chilly |
| minecraft lore / theories | 4 | 1 | 19K | **7,5×** | 2,9K | 0% | The Games Professor (23 ngày, 307 sub) |
| ancient rome (lịch sử dựng trong Minecraft) | 1 | 1 | 29K | **8,7×** | 0,3K | 0% | History in Minecraft (20 ngày, 2,6K sub) |
| minecraft mods (horror mod) | 3 | 3 | 22K | 2,1× (eskrr 9,1×) | 12K | 33% | eskrr, Kageborne, Zarbenix |
| minecraft updates | 1 | 1 | 36K | **12×** | 36K | 0% | Novorions (9 ngày): "Parallel Stalker… UPDATE" |
| minecraft builds (satisfying) | 1 | 1 | 18K | 4,9× | 0,7K | 0% | MinePhysics (29 ngày): "How Steve's Brain Is Crafted [Oddly Satisfying]" |
| minecraft survival / hardcore | 4 | 4 | 14–19K | 1–3,6× | 40K | 33% | UmangRon, NotCraftOP, FlixMCraft |
| minecraft stories (POV dài 2 giờ) | 2 | 1 | 25K | 1× | 1,9K | 0% | Ash Plus (23 ngày): video 2 giờ |
| what-if / so sánh | 2 | 2 | 17–21K | 2–9,8× | 4K | 0% | LegendBro, QuiClips |

Kênh mới thật nhiều view nhất đều dùng IP Maizen (JJ & Mikey):
- Banazen Craft: 20 ngày, 1,52M view trên 6 video, video cao nhất 754K.
- Mix Funny: Việt Nam, 1,11M.
- VODCRAFT: 396K.

### Định dạng ở các tài khoản cũ vừa "khởi động lại" (Algrow coi là mới)
Các kênh này không chứng minh "kênh mới thắng", nhưng cho thấy định dạng nào đang ăn với kênh nhỏ (OBSERVED):
- **Ivan Kuria** (8,9K sub): "Minecraft is Secretly Chemistry" 428K view (outlier 4,6×); "Can You Run Every Line of Code in Minecraft?" 166K. Dạng khoa học trong Minecraft.
- **Em Again and BLOX**: "Minecraft, But the Chunk Changes Every Minute…" 409K. **rat lolz**: "Can You Beat Minecraft Using ONLY Chest Loot?" 168K. Dạng thử thách.
- **Meep 2**: "40 Minecraft Secrets You Didn't Know!" 333K. **V4NITY**: "How to Get Stacked Fast" 593K.
- **Bingis**: "Fall Asleep While I Rebuild the World in Modded Minecraft", 2,6 giờ, outlier **30×**. Dạng video dài để ngủ.

## Shorts: 12 kênh mới thật (≤30 ngày theo API)

| Kênh | Tuổi | Tổng view kênh | Sub | Dạng |
|---|---|---|---|---|
| ArcticRanks88 | 24,8 ngày | 9,61M | 7,5K | "Ranking Minecraft Jumpscare Moments": xếp hạng, ghép clip (rủi ro nội dung tái sử dụng) |
| HoHoSchool | 24,1 ngày | 7,05M | 39K | Truyện JJ/Mikey dạy con (IP Maizen) |
| PoReact (NP) | 17,5 ngày | 5,41M | 6K | Reaction |
| Evil Spector | 13 ngày | 2,52M | 19,7K | Maizen |
| Mini Bummkinn | 24,4 ngày | 2,19M | 15K | Hoạt hình rap Minecraft vs Roblox |
| 匚尺ㄖ乙 | 24,2 ngày | 1,78M | 4K | "Ara Ara" Minecraft animation |
| Dexisgod | 20,2 ngày | 1,28M | 3K | — |
| Rizox | 19,6 ngày | 0,74M | 2K | Thử thách mê cung lava noob/pro |
| **NotEvanavE** | 14,7 ngày | 0,72M | 0,9K | **Hướng dẫn xây công trình gốc ("Making a Working Elevator")** |
| Mikey&JJ | 14,2 ngày | 0,48M | 2K | Maizen |
| Mine Table (TR) | 8 ngày | 0,37M | 0,2K | — |
| BigMineCraft | 4 ngày | 0,24M | 1K | — |

**Định dạng Shorts đang chạy ở các kênh lớn hơn** (tài khoản cũ) **(OBSERVED):**
- "Tiny to Colossal Steve VS Earths #teardown" (CuBerry Gaming, 13M)
- "X vs EVERY Minecraft Mob" (Brawl Lab)
- "War Profiteering Explained in Minecraft" (cleverchuck, 128K sub)
- "Baby Creeper's Last Second 💔" (CrafToons)
- Pixel art / linocut in tranh Minecraft (WhiteCraft, MagicalTulips)
- "Minecraft, But…" (skiv)
- Hướng dẫn xây (MartianMC, NotEvanavE)

## Bảng tổng hợp: ngách nên làm cho kênh mới và có thể phát triển bền thành kênh lớn (INFERRED)

| Hạng | Ngách / định dạng | Bằng chứng (OBSERVED) | Vì sao bền | Hợp CINE | Rủi ro |
|---|---|---|---|---|---|
| **1** | **Giải thích khoa học / lịch sử / lore bằng Minecraft** (video dài 8–20 phút, kèm Shorts cắt ra) | History in Minecraft (20 ngày) outlier 8,7×; The Games Professor (23 ngày) 7,5–9,3×; Ivan Kuria 428K/166K; cleverchuck (Shorts giải thích kinh tế) | Chủ đề không lỗi thời, người xem tìm kiếm lại về sau; RPM có thể nghiêng về nhóm Education; mỗi tập một chủ đề mới nên không lặp khuôn | ✓✓ Lời dẫn + Blender/ghi hình Minecraft; khớp hướng "3D history & engineering" | Phải nghiên cứu nội dung kỹ, không chép kịch bản người khác |
| **2** | **Thử thách "Minecraft, But…" / "Can You Beat Minecraft Using ONLY…"** (video dài) | Em Again 409K; rat lolz 168K; QuiClips (24 ngày) 9,8×; skiv và Viks (Shorts) | Mỗi luật là một tập mới, tạo được series; kênh lớn như Dream và Kipz đi lên bằng dạng này | ✓ Cần quay gameplay (Fabric/Flashback) và người chơi góc nhìn POV | Cạnh tranh cao; phải có góc riêng |
| **3** | **Kinh dị: thực thể / mod gốc** (video dài sinh tồn + Shorts) | eskrr (24 ngày) 9,1×; Novorions (9 ngày) 12×; ArcticRanks88 9,6M (Shorts); BlockKahani (vòng hằng ngày) | Có một vũ trụ thực thể riêng để phát triển nhiều series (kế hoạch L1/L2) | ✓ Đã có kế hoạch | Không dùng thực thể hoặc mod của người khác (Parallel Stalker, Jerry, Nextbot) |
| **4** | **Xây dựng gây thỏa mãn / "How X is Crafted" / hướng dẫn xây** (Shorts + video dài) | MinePhysics (29 ngày) 4,9×; NotEvanavE (14,7 ngày) 0,72M; MartianMC | Nội dung hướng dẫn được tìm lại lâu dài; làm thành series được | ✓ Blender + template công trình (S2/S3) | Lượt thích thấp nếu chỉ là vòng lặp |
| **5** | **Video dài để ngủ / thư giãn trong Minecraft** (2–3 giờ) | Bingis 2,6 giờ, outlier 30×; Ash Plus 2 giờ | Giờ xem lớn, dễ đạt 4.000 giờ cho YPP | △ Làm được bằng ghi hình kèm lời dẫn nhẹ | Phải có lời dẫn hoặc chỉnh sửa thật, tránh nội dung tái sử dụng |
| ✗ | **JJ & Mikey / Maizen roleplay và hoạt hình** | Chiếm phần lớn view của kênh mới thật (Banazen 1,52M; HoHoSchool 7M Shorts) | — | ✗ Vi phạm luật Original IP | IP Maizen, khán giả nhỏ tuổi (Made for Kids) |
| ✗ | Ghép Sonic / Peppa / brainrot / Verity / Roblox | Snow Mine, Peppa Up, Erzxck… | — | ✗ | IP người khác |

## Hạn chế
- Mẫu chỉ là những gì Algrow đã thu thập, xếp theo độ giống từ khóa (similarity), và mới chụp một lần (13/11).
- Phần Shorts chạm trần 600 video ở mốc ≤30 ngày.
- Algrow không công bố cách tính outlier. "Tổng view 24h" lấy từ Algrow.
- Bộ lọc IP chỉ dựa trên tiêu đề nên là ước lượng.
- Chưa đo RPM thật của ngách Minecraft giáo dục.
