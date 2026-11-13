# Algrow Channel Trends "minecraft": lọc tuổi kênh 30 → 1 ngày, sắp theo view 24h, kiểm lại bằng API (13/11/2026)

## Cách làm (OBSERVED)

**Nguồn:** trang `algrow.online/trends?q=minecraft&adv_max_age=N`, chạy với N = 30, 29, … 1.
- Sắp xếp theo **Views (24h)**, ngôn ngữ English.
- Mỗi mốc lấy hết các trang, mỗi trang 20 kênh, qua chính API mà trang Algrow dùng trong phiên đăng nhập của owner.
- Mỗi kênh có các trường: view 24h/48h, sub 24h, trung bình view mỗi video, outlier tốt nhất trong 30 ngày, số outlier, có bật kiếm tiền hay không, ngách con và video gần đây.

**Số kênh theo mốc tuổi:**

| Mốc (ngày) | 30 | 29 | 28 | 27 | 26 | 25 | 24 | 23 | 22 | 21 | 20 | 19 | 18 | 17 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Số kênh | 207 | 200 | 195 | 171 | 153 | 146 | 139 | 132 | 123 | 117 | 109 | 99 | 92 | 83 | 78 |

| Mốc (ngày) | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Số kênh | 70 | 63 | 60 | 53 | 41 | 35 | 30 | 23 | 21 | 16 | 8 | 4 | 1 | 0 | 0 |

**Lưu ý về định nghĩa:** trong bộ lọc nâng cao, Algrow ghi rõ **"Channel age = Time since their first upload"**, tức là thời gian tính từ video đầu tiên hiện còn trên kênh.

**Kiểm lại bằng YouTube API:** lấy ngày tạo tài khoản (`channels.list` → `snippet.publishedAt`) của 205/207 kênh, file `algrow_trends_channel_ages.json`.
- **Chỉ 70 kênh thật sự được tạo trong 30 ngày qua.** 21 kênh ≤15 ngày, 4 kênh ≤7 ngày.
- 135 kênh còn lại là tài khoản cũ mới đăng video lại. Ví dụ: Manhoryn tạo 7.310 ngày trước, SmartyCraft 1.008 ngày, V4NITY 1.763 ngày.

## Bảng 1: kênh mới thật (tạo ≤30 ngày theo API), xếp theo view 24h

| Kênh | Tuổi thật | Sub | Tổng view | Số video | View 24h | Outlier tốt nhất 30 ngày | Ngách (Algrow) | Video lớn nhất | Dùng được cho CINE? |
|---|---|---|---|---|---|---|---|---|---|
| Christopher Norton | 22,6 ngày | 9,4K | 3,36M | 11 | **1,21M** | 44,7× | (bình luận drama) | "The Dream Files Just Dropped" 3,17M, 61 phút | ✗ Drama về creator thật (Dream) |
| จันจิรา | 5,4 ngày | 0,5K | 288K | 5 | 172K | 2,4× | action animations | "Guess The DAD \| CreeperBoy" 165K | ✗ Khuôn JJ/Maizen |
| Mix Funny (VN) | 18,6 ngày | 1,3K | 1,08M | 18 | 84K | 6,2× | dance animations | Meme trollface 250K | ✗ IP Maizen |
| Old Stories From JJ And Mikey | 11,4 ngày | 0,6K | 180K | 9 | 59K | 3,8× | roleplay | 72K | ✗ IP |
| Mikey Chilly | 12,1 ngày | 0,3K | 108K | 6 | 40K | 4,1× | roleplay | 67K | ✗ IP |
| Odar | 29,1 ngày | 0,8K | 380K | 7 | 36K | 5,2× | SMP battles | "Unstable SMP: The 5th Protagonist" 180K | △ Kể lore SMP của creator khác |
| Banazen Craft | 19,4 ngày | 10,3K | 1,41M | 6 | 30K | 2,9× | survival | JJ & Mikey 754K | ✗ IP |
| **Soup Theory** | 17,2 ngày | 0,5K | 225K | 12 | 29K | **9,1×** | — | **"We Put 8 Historic Warriors in One Arena. It Wasn't Fair."** 170K, 12 phút | ✓✓ Mô phỏng trận đấu lịch sử |
| Ash Plus | 22,7 ngày | 2,5K | 552K | 21 | 26K | 2,3× | roleplay POV | "YOUR HEART is BROKEN!" 119 phút | △ Truyện POV dài |
| UmangRon | 7,5 ngày | 0,6K | 228K | 4 | 19K | 3,9× | survival | Tralalelo (meme brainrot) 232K | ✗ IP meme |
| **eskrr** | 24,3 ngày | 0,3K | 59K | 18 | 13K | **9,1×** | horror mods | "this minecraft horror mod got worse every minute" 37K | ✓ (nếu dùng thực thể gốc) |
| NICHE Minecraft | 27,3 ngày | 0,6K | 171K | 33 | 9,6K | 6,1× | roleplay | "YANDERE CAT wants YOU" 44K | △ |
| **The Games Professor** | 23 ngày | 0,3K | 118K | 16 | 8K | **9,3×** | lore & theories | "Who Created the Sculk (And Steve)?" 49K, 17 phút | ✓✓ |
| Novorions | 9,2 ngày | 0,2K | 47K | 5 | 6K | 5,6× | horror mods | Parallel Stalker update 38K | △ Mod của người khác |
| DirtyKitty | 28,9 ngày | 0,2K | 87K | 6 | 4,9K | 5,6× | mob battles | "10000 Zombie VS Secure House With Machine Gun Cats" 53K | ✓ |
| Ethan's Adventures | 27 ngày | 0,3K | 61K | 4 | 2,7K | 2,9× | survival storytelling | "I Raced to the Last Evacuation in a Zombie Apocalypse" 59K | ✓✓ Khớp L2 |
| MinePhysics | 28,9 ngày | 0,1K | 71K | 17 | 2,6K | 4,8× | factory building | "How Steve's Brain Is Crafted [Oddly Satisfying]" 18K | ✓ Khớp S2 |
| **History in Minecraft** | 20,1 ngày | 2,7K | 46K | 14 | 1K | **8,7×** | Roman history | "The History of Roman Empire: Every Year (in Minecraft)" 29K, 21 phút | ✓✓ |
| **Mr. Aftermath** | 28 ngày | 0,2K | 32K | 8 | 1K | **10,1×** | zombie survival | "I Survived 100 Days in the Zombie Apocalypse \| Full Movie" 21K, 52 phút | ✓✓ Khớp L2 |
| QuiClips | 24,1 ngày | 0,2K | 35K | 11 | 1K | 9,8× | battles & builds | "Minecraft Mobs VS Minecraft Cats House" 21K | ✓ |
| Fazy | 28,9 ngày | 0,2K | 40K | 6 | 0,6K | 3,5× | survival builds | "How to Build the ULTIMATE Survival Base" 22K | ✓ |
| Hxppys | 11,6 ngày | 0,1K | 22K | 3 | 1,7K | 1,9× | roleplay | "I Got Hunted by a Minecraft Empire" 215 phút | △ |
| comtaigratme1984 / Rin Manhwa | 9–25 ngày | — | 14–19K | — | 2,7–4,9K | — | manhwa recap (2–3 giờ) | — | ✗ Tóm tắt truyện của người khác |

## Bảng 2: tài khoản cũ được Algrow coi là "mới" (tuổi thật >30 ngày), tham khảo định dạng

| Kênh | Tuổi thật | View 24h | Định dạng | Video lớn nhất |
|---|---|---|---|---|
| TheLittleFoxYT | 366 ngày | 72K | Nhân vật Sonic chơi Minecraft (IP) | 270K |
| GurkaRoblox | 39 ngày | 61K | "Roblox vs Minecraft vs Garry's Mod – Chase Test" | 137K, outlier 13,3× |
| SmartyCraft | 1.008 ngày | 56K | Roleplay "Smarty vs Daddy" | 41K |
| RazeCrafter | 171 ngày | 56K | "LORD VERITY Vs All New Minecraft Bosses" | 198K |
| Kouzly | 928 ngày | 42K | Clip khoảnh khắc creator | 458K |
| Meep 2 | 71 ngày | 42K | "40 Minecraft Secrets You Didn't Know!" | 333K |
| Ivan Kuria | 192 ngày | 33K | "Minecraft is Secretly Chemistry" | 428K |
| _slicee | 52 ngày | 31K | PvP Bedrock | 734K |
| V4NITY | 1.763 ngày | 27K | "How to Get Stacked Fast" | 593K |
| Kan | 1.182 ngày | 24K | "How the Herobrine Seed Was Finally Found" (bí ẩn) | 129K |
| ClipProviders | 118 ngày | 20K | Clip streamer | 331K |
| Manhoryn | 7.310 ngày | 18K | "I Built a Modern Underground City After Being Exiled…", 88 phút | 86K |
| Em Again and BLOX | 84 ngày | 14K | "Minecraft, But the Chunk Changes Every Minute" | 409K |

## Bảng 3: tổng hợp theo ngách cho kênh mới (INFERRED, dựa trên Bảng 1–2 và báo cáo video ngày 13/11)

| Hạng | Ngách | Kênh mới thật đang thắng (tuổi, outlier) | Tín hiệu bền | Rủi ro / ghi chú | Khớp kế hoạch CINE |
|---|---|---|---|---|---|
| **1** | **Lịch sử & khoa học bằng Minecraft hoặc mô phỏng**: "History of X in Minecraft", "8 Historic Warriors in One Arena", "Minecraft is Secretly Chemistry" | Soup Theory (17 ngày, 9,1×, 170K); History in Minecraft (20 ngày, 8,7×); Ivan Kuria (tài khoản cũ, 428K) | Mỗi tập một chủ đề mới; người xem tìm kiếm lại về sau; ít IP | Cần nghiên cứu kịch bản thật; RPM có thể cao hơn gaming (chưa đo) | Kênh "3D history & engineering" + Minecraft/Blender |
| **2** | **Lore, bí ẩn, giả thuyết Minecraft** | The Games Professor (23 ngày, 9,3×); Kan "Herobrine Seed" (cũ, 129K) | Lore phong phú, chủ đề vô tận | Herobrine và lore Mojang dùng được theo hướng dẫn của Mojang; không dùng IP creator khác | Lời dẫn + Blender |
| **3** | **"100 Days" / phim sinh tồn zombie hoặc thảm họa** (Full Movie 50+ phút) | Mr. Aftermath (28 ngày, **10,1×**); Ethan's Adventures (27 ngày, 59K) | Video dài nên giờ xem lớn; làm được series nhiều mùa | Cạnh tranh cao; cần dựng kịch bản bài bản | Chính là **L2** đã chọn |
| **4** | **Kinh dị với thực thể hoặc mod do mình làm** | eskrr (24 ngày, 9,1×); Novorions (9 ngày, 5,6×) | Hai kênh mới thật đều lên được | Không dùng mod hoặc thực thể của người khác (Parallel Stalker) | **L1** |
| **5** | **Thí nghiệm, đối đầu mob, "X vs Y"** | DirtyKitty (29 ngày, 5,6×); QuiClips (24 ngày, 9,8×); GurkaRoblox "Chase Test" (13,3×) | Dễ làm series, hợp cả Shorts lẫn video dài | Dễ thành lặp khuôn, cần thay đổi luật chơi mỗi tập | S2/S3 |
| **6** | **Xây dựng gây thỏa mãn / hướng dẫn xây** | MinePhysics (29 ngày, 4,8×); Fazy (29 ngày, 22K) | Nội dung hướng dẫn được tìm kiếm lâu dài | View mỗi video thấp hơn các ngách trên | S2/S3 |
| ✗ | JJ & Mikey / Maizen, Sonic, Verity, brainrot (Tralalelo), Dream drama, tóm tắt manhwa | Chiếm phần lớn view 24h của kênh mới thật | — | Dùng IP người khác hoặc drama về người thật; vi phạm luật studio | Không làm |

## Hạn chế
- Đây là một lần chụp trong cơ sở dữ liệu Algrow (13/11), chỉ gồm kênh tiếng Anh có từ khóa "minecraft".
- Cách Algrow tính outlier và view 24h không được công bố.
- Ngách con là nhãn do AI của Algrow gán.
- Algrow không cung cấp RPM cho tài khoản dùng thử (rpm_by_id trống).
- Tuổi thật lấy từ YouTube API, khớp với dòng "Đã tham gia" trên trang kênh YouTube. Đã đối chiếu 5 kênh trong phiên 23:13.
