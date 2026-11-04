# Nghiên cứu ngách Minecraft bằng YouTube API – vòng 2 (2026-11-04)

**Dữ liệu:** quét theo 8 làn, chụp lúc 12:00–12:05 UTC, dùng 5.788 đơn vị quota.
- 52 truy vấn tìm kiếm trong 30 và 15 ngày gần nhất, thị trường Mỹ, tiếng Anh.
- Thu được 1.814 video và 1.192 kênh. Kéo thêm upload của 256 kênh.
- Chụp lại số view của 795 video sau 16,8 giờ.

**Chi tiết:** `research_notes/Quét ngách Minecraft bằng YouTube API/` gồm E (bộ dữ liệu), F (chấm điểm làn, kênh dẫn đầu, video bùng nổ), G (đối thủ mới). Số liệu đi kèm nằm trong `data/2026-11-04/`.

## Chấm 8 làn theo 5 tiêu chí (INFERRED theo luật trong F §2.2, tính trên số OBSERVED)

| Làn | RPM | Ít rủi ro | Bền vững | View lớn | Chỗ cho kênh mới | Tổng /25 |
|---|---|---|---|---|---|---|
| **Phim sinh tồn có kịch bản ("Full Movie", bộ đếm ngày)** | 5 | 4 | 5 | 3 | 3 | **20** |
| Lore / sự thật | 3 | 5 | 3 | 1 | 5 | 17 |
| Mô phỏng trận đánh mob | 4 | 3 | 4 | 2 | 3 | 16 |
| Bí ẩn / kinh dị dạng gameplay | 4 | 3 | 3 | 2 | 3 | 15 |
| AI trong Minecraft | 3 | 5 | 2 | 1 | 4 | 15 |
| "Minecraft but" / roleplay | 1 | 3 | 3 | 5 | 3 | 15 |
| Hoạt hình gia đình / cảm xúc | 1 | 2 | 4 | 4 | 2 | 13 |
| Shorts tương tác | 1 | 2 | 3 | 2 | 3 | 11 |

Làn sinh tồn có 97% lượt xem đến từ video dài. 87% số video ≥100K của làn này dùng IP gốc, và chỉ 4% có giọng trẻ em (OBSERVED).

Hai làn gia đình và tương tác có nhiều lượt xem và nhiều kênh mới, nhưng 53–64% dùng IP của người khác và 71–79% có giọng trẻ em (OBSERVED). Vì vậy rủi ro bị xếp vào nội dung trẻ em (MFK) cao và RPM thấp.

## Đối thủ dẫn đầu và video vượt trội (OBSERVED)

- **Day Zero** (kênh 30 ngày, 14K sub): [I Survived 100 Days in a REALISTIC APOCALYPSE](https://www.youtube.com/watch?v=crnpqkov3ps) 1,91M view, gấp 136 lần số sub.
- **Kit vs The End** (38 ngày): [Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship](https://www.youtube.com/watch?v=xdj5PL0t61k) 715K view, gấp 34 lần trung vị của kênh, đang tăng khoảng 59K/ngày.
- **SirCloaked** (347 ngày): có 2 video dài trên 1M. Video "Something On My Farm Wants Me Dead..." đạt 970K và sắp vượt 1M.
- **Hoodie Steve** (4.970 sub): [Minecraft Tug of War: Villagers vs Mobs](https://www.youtube.com/watch?v=xpsiRQd7ssg) 1,97M view, gấp 49,5 lần trung vị.
- **Spoke**: "COLD WAR" 13,73M view, gấp 3,9 lần trung vị, tăng khoảng 505K/ngày.
- **Cubeee**: bản compilation 54 phút đạt 2,37M view, tăng khoảng 248K/ngày. Đây là IP fan Maizen, chỉ học công thức.

## Đối thủ mới 0–30 ngày (OBSERVED)

Không kênh nào đạt chuẩn khắt khe là có ít nhất 2 video dài trên 1M. Có 45 kênh mới lập 0–30 ngày, 15 kênh trong số đó có video vượt 100K.

- Day Zero đã ra khỏi cửa sổ 30 ngày. Video dài thứ hai của kênh mới 376K, tăng khoảng 8,3K/ngày.
- **Nobody Gets In** (người que, không phải Minecraft) có 2 video trên 1M: 3,28M và 1,86M. Nhưng kênh này đã 33,7 ngày tuổi.

Danh sách theo dõi tăng từ 32 lên 38 kênh (`config/research/minecraft_story_watchlist.txt`). Kênh mới thêm vào: Nobody Gets In, Beanie Survives, SirCloaked, Manic Craft, Vexora Plays, Brawl Lab.

## Video đang bùng nổ (OBSERVED, khoảng cách 16,8 giờ)

Có 420 video đủ điều kiện xét.
- Shorts: 12 tăng tốc, 75 ổn định, 269 giảm tốc.
- Video dài: 1 tăng tốc, 24 ổn định, 38 giảm tốc.

43% số video này dùng IP của người khác. Ở kênh nhỏ, video IP gốc và video IP người khác gần ngang nhau (115 so với 114) và tăng cùng tốc độ, khoảng 2,2–2,3K view/giờ.

Video tăng nhanh nhất là [Who Will ADOPT JJ Kitten?!](https://www.youtube.com/watch?v=glwTiwUdhJo), khoảng 132K view/giờ. Video này dùng IP fan nên chỉ học công thức.

## Cập nhật nguyên tắc

Đã ghi vào `minecraft_story_principles.md`:
- Thêm **S7 "Zombie Outbreak + bộ đếm ngày"**: thấy lần đầu 2026-10-06, đang nóng, dùng được.
- Thêm S8: mô phỏng trận đánh mob.
- Thêm S9: các làn sóng IP của người khác, gồm Dr Donut, Jerry the Wolf và Verity.
- Hạ S5 (đồ ăn "lần đầu tiên") xuống mức theo dõi.
- Đánh dấu S6 (Halloween) là hết hạn.

## Khuyến nghị (INFERRED; OWNER quyết)

1. **Làn chính:** phim sinh tồn có mối đe dọa hoặc bí ẩn, với Bin, Bo và Zu. Ví dụ: "Zombie Outbreak: 30 Days Locked in a Supermarket… But Our Little Brother IS a Zombie". Mỗi tập 10–15 phút, gộp lại thành Full Movie 40–60 phút.
2. **Shorts kéo người xem:** mô phỏng trận đánh chỉ dùng mob của Mojang, dựng bằng lệnh. Ví dụ: "Zu vs Every Mob — Who Wins?".
3. **Làn thử nghiệm:** AI trong Minecraft, dùng bot LLM chạy trên máy. Kèm theo là Shorts lore về chính vũ trụ của kênh.

**Nên tránh làm trụ:** hoạt hình gia đình và Shorts tương tác (rủi ro MFK, nhiều IP người khác), cùng mọi làn sóng IP của người khác.
