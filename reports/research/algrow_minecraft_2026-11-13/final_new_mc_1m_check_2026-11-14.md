# Quét lần cuối: kênh Minecraft tạo ≤1 tháng có video ≥1M view (14/11/2026)

## Cách làm (OBSERVED)
1. **Algrow Viral Videos** (phiên của chủ kênh, chỉ đọc)
   - Bộ lọc: Shorts + Longform, `min_video_views=1.000.000`, `max_upload_date=31`, `max_channel_age=30`.
   - 30 từ khoá: minecraft, minecraft animation/horror/noob vs pro/build/but/satisfying/blender/story/challenge/mobs/funny/pvp/parkour/tnt/redstone/maizen, steve, creeper, herobrine, villager, enderman, zombie minecraft, warden, who can build, blocky animation, block world animation, jj and mikey, minecraft roblox.
   - Kết quả: **643 video từ 269 kênh** (Longform: 0). Lọc theo tiêu đề liên quan Minecraft còn 92 kênh. Ngày tạo của 92 kênh lấy từ dòng "Đã tham gia" trên trang About.
2. **Kho dữ liệu YouTube Data API đã quét 03–13/11**
   - Gồm api_dataset, lane_scan, wide_scan, targeted_minecraft, niche_compare, mc_shorts, mc_daily, new_channel_hunt và audit.
   - Tổng 44.333 video; 12.567 kênh có ngày tạo thật.
   - Lọc kênh tạo từ 14/10 trở đi có video ≥1M.
3. **Kiểm nội dung từng ứng viên:** xem thumbnail và 10–14 Shorts mới nhất của kênh.

**Giới hạn:**
- Không chạy được `search.list` mới hôm nay: Blender MCP trên PC đang tắt, quota search ngày 13/11 gần hết.
- Kênh nào chưa từng lọt vào kho API và Algrow cũng không lập chỉ mục thì vẫn có thể bị sót.

## Kết quả

### A. Đúng Minecraft, không dựa IP bên thứ ba ngoài Minecraft, tạo ≤30 ngày

| Kênh | Ngày tạo (tuổi) | Video ≥1M | Dạng | Ngôn ngữ |
|---|---|---|---|---|
| **Verity Verifies MC** | 25/10 (≈20 ngày) | "How To Breed Horses Perfectly..." **3,44M**; "How To Use Copper Golems Perfectly..." 1,61M | Short mẹo / "perfectly" + lore server 2b2t, gameplay thật | Anh |
| **Mochi & Pals** | 15/10 (30 ngày) | "Who can dig down the fastest?" **2,92M**; "Who can build the best house?" 2,76M | Hoạt hình 3D, dàn nhân vật gốc, thi đấu "Who can…?" | Anh (gần như không lời) |
| ElChipaX MIN | 15/10 (30 ngày) | "Minecraft, pero comprobé si este truco de los aldeanos es REAL o FALSO" **2,1M** | Thử mẹo "thật hay giả", gameplay | Tây Ban Nha. 104K sub sau 29 ngày → có thể là kênh phụ của creator ElChipaX (INFERRED) |
| MineZox | 31/10 (14 ngày) | "HE THOUGHT HE FOUND ME! (Minecraft Hide and Seek)" **1,29M** | Gameplay trốn tìm + avatar hoạt hình | Anh. Có 1 video "Mikey Turned EVIL" (dính tên Maizen) |

### B. Có Minecraft nhưng vướng vấn đề

| Kênh | Tuổi | Video ≥1M | Vấn đề |
|---|---|---|---|
| CHIRAG FACTO | 22 ngày | "Slither Run with Steve" 3,09M; Memory Competition 2,36M; Double Slither Run 1,96M | Steve/Alex chạy trong game runner kiểu mobile, không phải thế giới Minecraft. Kênh "facts" tiếng Hindi. |
| Maikeyxx | 6 ngày | 5,60M | IP JJ/Maizen |
| Maddyshorts07 | 13 ngày | 2,17M | IP JJ/Maizen |
| DiaxGold Crafts | 14 ngày | 2,15M | IP JJ/Maizen |
| HoHoSchool | 25 ngày | 1,38M | IP JJ/Maizen |
| ArcticRanks88 | 25 ngày | "Ranking Minecraft Jumpscare Moments" 9,28M | Ghép clip TikTok của người khác (nội dung tái sử dụng) |

### C. Vừa quá 1 tháng (31–33 ngày)
- Erzxck (32 ngày): 14,5M, IP Verity/Fortnite/FNAF.
- unstxblesmpedits (31 ngày): 5,64M, edit clip Unstable SMP.
- Dime Minecraft Bits (33 ngày): 1,17M, clip Mumbo/Grian.

### D. Đã loại vì KHÔNG phải kênh Minecraft
Endform TV (đa chủ đề), Brawl Lab (Undertale/PvZ crossover), Cube Clash (blocky, chưa có video 1M), Hopkin (Roblox), DoodleSurvivals (hoạt hình 2D), BTS KING (Ronaldo/IShowSpeed maze), cùng rất nhiều kênh Roblox, "Steal an Egg" và Maizen do Algrow trả về theo độ giống từ khoá.

## Kết luận (INFERRED)
- **Có, nhưng rất ít.** Trong khoảng 12.800 kênh đã quét, chỉ có **4 kênh đúng Minecraft, nội dung gốc, tạo ≤30 ngày, có video ≥1M**. Chỉ 2 trong số đó là tiếng Anh và có ≥2 video triệu view: Verity Verifies MC và Mochi & Pals.
- Hai cách thắng khác nhau:
  - **Verity Verifies MC:** quay gameplay thật, Short mẹo "How To X Perfectly…" + lore 2b2t. Rẻ, nhưng cần quay trong game.
  - **Mochi & Pals:** hoạt hình 3D với dàn nhân vật gốc, thi đấu "Who can…?". Hợp với Blender của CINE.
- Số kênh mới đạt triệu view nhờ IP Maizen (4 kênh trong ≤30 ngày) **ngang bằng** số kênh gốc. Đây là lý do ngách trông "dễ" hơn thực tế.
