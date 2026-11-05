# Nghiên cứu ngách Minecraft hằng ngày – vòng 3 (2026-11-05)

> **Đường API KHÔNG chạy được hôm nay.** Máy PC online nhưng Blender MCP đóng (`localhost:9876` từ chối kết nối; chế độ CLI báo không tìm thấy `blender`). Vì vậy không gọi YouTube Data API, không dùng quota, không đụng tới file `.env`.
> **Đường dự phòng:** đọc metadata công khai bằng Claude in Chrome trong tab riêng, 75 lượt tải trang (giới hạn 80), không đăng nhập, không like/comment/tải video. Chụp lúc ~11:55–12:20 UTC.

**Giới hạn của dữ liệu hôm nay (đọc trước khi so sánh):**
- 23 truy vấn tìm kiếm (lọc "tuần này"/"tháng này", sắp theo lượt xem) → 342 video duy nhất; 209 video ≥100K, 68 video ≥1M (OBSERVED 2026-11-05).
- 38/38 kênh trong danh sách theo dõi + 8 kênh ứng viên được đọc trang kênh.
- Không có số sub chính xác (trang kênh làm tròn 2–3 chữ số), không có ngôn ngữ âm thanh, không có ngày tạo kênh chính xác cho mọi kênh, và tab Shorts không ghi tuổi video. Tuổi video lấy từ chữ "x ngày/tuần trước" nên sai số ±3 ngày (INFERRED).
- Số "+/24 h" dưới đây = số OBSERVED hôm nay trừ số OBSERVED 2026-11-04 ~12:00Z (khoảng 24 h).
- Dữ liệu: `research_notes/Quét ngách Minecraft bằng YouTube API/data/2026-11-05/browser_fallback_snapshot.csv` (48 video chính).

## 1. Thay đổi so với hôm qua

### Làn chính "Zombie Outbreak / bộ đếm ngày" (S7): vẫn nóng nhưng đang **chín** (INFERRED)
| Video | Hôm qua | Hôm nay (OBSERVED 2026-11-05) | +24 h | Xu hướng |
|---|---|---|---|---|
| Kit vs The End – Zombie Cruise Ship | 715K | 763K | +~48K | giảm tốc (hôm qua ~59K/ngày) |
| Day Zero – DEADLY OUTBREAK (video dài thứ 2) | 376K | 383K | +~7K | gần như dừng |
| Nobody Gets In – Locked Inside a School | 1,86M | 1,885M | +~25K | giảm tốc |
| Nobody Gets In – Locked Inside a Supermarket | 3,28M | 3,35M | +~70K | ổn định |
| Maizen – Zombie Outbreak / SURVIVING in BUS | 5,00M | 5,20M | +~199K | ổn định |

- Định dạng đang lan: Beanie Survives làm thành series đánh số ("Zombie Outbreak Ep. 5" 525K); Nobody Gets In chuyển sang thảm họa khác ("Quarantined at Sea", "Every Passenger on Flight 212…"); xuất hiện bản tiếng Thổ Nhĩ Kỳ (1,12M trên kênh 5,89K sub ≈ 190× sub) và tiếng Bồ Đào Nha (OBSERVED 2026-11-05).
- Maizen hiện tiêu đề khác nhau cho cùng video (trang tìm kiếm "Zombie Outbreak", trang kênh "SURVIVING in BUS During ZOMBIE APOCALYPSE") → INFERRED: đang A/B test tiêu đề.
- **Kết luận (INFERRED):** nhu cầu còn lớn, nhưng tiêu đề trơn "Zombie Outbreak: N Days in <nơi>" đã đông. Lợi thế của ta phải là **twist dàn nhân vật** (zombie chính là em út Zu) và hình Minecraft thật, không phải công thức tiêu đề.

### Kênh khác trong danh sách (OBSERVED 2026-11-05, +24 h là INFERRED từ hai lần đọc)
- **SirCloaked:** "Something On My Farm Wants Me Dead..." 994K (+~24K) → sẽ qua 1M trong ~1 ngày → kênh có 3 video dài ≥1M.
- **MSToons:** "YOU Trolled JJ and Mikey with Infinite Hearts!" 1,97M (+~546K, giữ tốc độ); "JJ BUS EATER was Buried…" 1,72M (+~207K). IP Maizen → chỉ học công thức.
- **Spoke COLD WAR:** 14,10M (+~366K, giảm từ ~505K/ngày).
- **Ligabka LOVE QUEEN:** 908K (+~95K). **Cody Toon** LOVE STORY PIT 705K (+~34K). **Cubeee** bản tổng hợp ~2,5M.
- **Banazen Craft:** 5,71K sub (hôm qua 4,69K); video mới nhất 513K ở ~3 ngày, chưa có video ≥1M.
- **DL Minecraft** (gần Zu nhất): baby zombie + pizza 221K (+~17K); video mới "Baby Piglin Thought He Had Lost Everything" 58K ở ~5 ngày; 2,81K sub.
- **Mochi & Pals** (IP gốc, Shorts thi đấu): 1,35K sub (hôm qua 1,15K); 3 Shorts mới nhất 84K/56K/261K.
- **Wablo:** 3 Shorts mới nhất 916K/1,2M/1,7M (Verity/"demon in my house" – IP người khác).
- BigSchool, Class Monster School, ZomBo: không có outlier ≤15 ngày.

## 2. Đối thủ mới 0–30 ngày
- **Không kênh nào đạt chuẩn khắt khe** (≥2 video dài >3 phút ≥1M) – ngày thứ 3 liên tiếp.
- Ứng viên gần nhất trong làn sinh tồn: **Stick It Out** – 304 sub, 5 video, video cũ nhất ~11 ngày (INFERRED tuổi kênh ≤~11 ngày), "Zombie Outbreak: 100 Days Trapped…" 54K, 61 phút (OBSERVED 2026-11-05). Chưa đủ "mạnh" để thêm vào danh sách; theo dõi lại ngày mai.
- Các kênh lớn mới thấy trong top tuần (Sticks, Omenasito, Karry Kraft, Damn Seconds, Rumble Ron) đều tạo từ 2016–2025 → không phải đối thủ mới (OBSERVED ngày tham gia trên trang About).
- Danh sách theo dõi: 38 kênh, 6 kênh "new" hôm qua đã chuyển thành "leader".

## 3. Video bùng nổ 0–15 ngày (OBSERVED 2026-11-05)
- 47 video ≥1M trong ≤15 ngày ở các truy vấn của ta. Phần lớn là kênh lớn (Parrot, Dream, Spoke, Maizen, MSToons).
- Mạnh nhất theo tốc độ: Parrot "10,000 Player Minecraft War" 12,07M ở ~3 ngày (~4M/ngày, INFERRED); FlameFrags 5,28M ở ~4 ngày; Sticks "If Technoblade's Life Was a Movie..." 3,76M ở ~4 ngày; Dagar "I Became the DARK WOLF KING" 3,25M ở ~3 ngày.
- Kênh nhỏ có lượt xem gấp nhiều lần sub: Başına Gelse (Thổ Nhĩ Kỳ) 1,12M / 5,89K sub ≈ 190×; Banazen 513K / 5,71K ≈ 90×; DL Minecraft 221K / 2,81K ≈ 79×.

## 4. Trend bắt đầu / kết thúc
- **Mới – S10** "10,000 Players Simulate… / War" (Parrot, FlameFrags, SpeedSilver, Spoke): nóng nhưng **không hợp kênh** (cần hàng trăm người chơi thật). Chỉ mượn khung "phe vs phe" cho Shorts đánh mob (S8).
- **Mới – S11** "If X's Life Was a Movie…": theo dõi; dùng được dạng công thức với nhân vật của ta.
- **Đang chín – S7** Zombie Outbreak (xem bảng trên).
- **Vẫn nóng nhưng không hợp kênh:** S2 X EATER, S3 Verity, S4 truyện tình "bị bắt", S9 làn sóng IP người khác (thêm Cat in the Hat, Talking Tom).
- **Hết hạn:** S6 Halloween (giữ nguyên). Chưa trend nào đủ 4 tuần để nâng thành nguyên tắc dài hạn.

## 5. Top 10 video nên nghiên cứu (công thức, không sao chép)
1. [Zombie Outbreak: 30 Days Locked Inside a School – Nobody Gets In](https://www.youtube.com/watch?v=2XYr2AEHDGI) – 1,885M, 9 phút
2. [Zombie Outbreak / SURVIVING in BUS – Maizen](https://www.youtube.com/watch?v=UH1HSIN4L20) – 5,20M, 29 phút (A/B tiêu đề)
3. [Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship – Kit vs The End](https://www.youtube.com/watch?v=xdj5PL0t61k) – 763K
4. [Something On My Farm Wants Me Dead... – SirCloaked](https://www.youtube.com/watch?v=VYFy1FN7-tk) – 994K
5. [If Technoblade's Life Was a Movie... – Sticks](https://www.youtube.com/watch?v=ZGYi_JjKhfE) – 3,76M, 14 phút (S11)
6. [I Became the DARK WOLF KING in Minecraft! – Dagar](https://www.youtube.com/watch?v=S8jwJk66Q7w) – 3,25M ở ~3 ngày
7. [Minecraft, But Your Hearts = Realism... – Carry Depie](https://www.youtube.com/watch?v=1G3RbNd2ZJA) – 2,95M ("Minecraft but…")
8. [10,000 Player Minecraft War: Nether VS Overworld – Parrot](https://www.youtube.com/watch?v=bHxLy6Qza3M) – 12,07M (chỉ khung "phe vs phe")
9. [Baby Zombie Couldn't Believe This Giant Pizza – DL Minecraft](https://www.youtube.com/watch?v=xLlYCcahMPE) – 221K, ~79× sub
10. [Zombie Outbreak Ep. 5 – Beanie Survives](https://www.youtube.com/watch?v=pLskOS1GddU) – 525K (mẫu series đánh số)

Lưu ý: các nhận định về nhịp, diễn xuất, âm thanh của những video này vẫn là **giả thuyết** cho tới khi qua cổng `competitor-complete-study`.

## 6. Ý tưởng cho Bin/Bo/Zu (INFERRED; OWNER quyết)
1. **Video dài (làn sinh tồn có mối đe dọa):** "Zombie Outbreak: 30 Days in a Frozen Mall… But Our Little Brother IS a Zombie". Twist: Bin & Bo phải giấu Zu khỏi những người sống sót khác, và Zu là người duy nhất đi qua đám zombie được. 10–12 phút; đánh số "Ep. 1" ngay từ đầu (học Beanie Survives), gộp Full Movie sau 4 tập.
2. **Video dài/Shorts (S11 + L1):** "If Baby Zombie Zu's Life Was a Movie…" – sinh ra, bị bỏ lại, được Bin & Bo tìm thấy, cứu cả nhà ở cuối. 8–10 phút, đoạn cắt 50 giây làm Shorts dẫn người xem.
3. **Shorts "Minecraft but…" với dàn của ta:** "Minecraft, But Zu's Hearts = Real Food…" – mỗi lần Zu ăn, tim đổi; Bin & Bo chạy đua tìm món. Chỉ dùng mob/đồ vật Mojang.

## 7. Việc còn chặn
- Mở Blender 5.2 + bật MCP addon trên PC để vòng ngày mai chạy lại đường API (≤9.000 đơn vị), có ngày tạo kênh, ngôn ngữ âm thanh và số sub chính xác.
