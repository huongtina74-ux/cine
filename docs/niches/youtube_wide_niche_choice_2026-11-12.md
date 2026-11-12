# Quét toàn YouTube: chọn ngách faceless kiếm tiền (2026-11-12)

Owner hỏi: "nếu được chọn bạn sẽ chọn những ngách nào để làm, hãy nghiên cứu toàn bộ YouTube".
Trạng thái: **PROPOSED**, chờ owner duyệt.

Nhãn bằng chứng:
- **OBSERVED**: số đo một lần qua API.
- **MEASURED**: RPM do AIR Media-Tech đo trên 300 kênh.
- **AGG-EST / practitioner**: số creator tự báo hoặc trang tổng hợp ước tính.
- **INFERRED**: suy luận.

## Cách đo
- Chỉ dùng YouTube Data API v3 chính thức: 8.955 unit, chạy lúc 2026-11-12 08:18Z. Script: `cine_niche_survey/cf_youtube_wide_scan.py`.
- 22 ngách, mỗi ngách 4 lượt tìm kiếm:
  - 2 lượt "xem nhiều nhất 30 ngày", một cho video dài >20 phút và một cho video 4–20 phút → đo nhu cầu và kênh thắng.
  - 2 lượt "mới đăng 48 giờ" → **mọi kênh đang đăng, gồm cả kênh thất bại**.
- Lấy chi tiết toàn bộ 4.206 video và 3.475 kênh.
- Chỉ giữ video tiếng Anh, dài từ 8 phút, không phải livestream.
- Phân tích: `reports/research/wide_scan_2026-11-12/wide_scan.py`, kết quả ở `wide_scan.md` và `wide_scan.json`.
- Giới hạn của cách đo:
  - Thứ tự "theo view" của API search có sai lệch.
  - Một số ngách lẫn đài TV hoặc phim truyện: Nollywood, Har Pal Geo, Nat Geo, DW.
  - Mỗi ô có ít kênh; số view chỉ đo một lần.
  - Lọc tiếng Anh dựa trên tag/tiêu đề nên là ước lượng.
  - RPM theo ngách con không đo được, chỉ có RPM nhóm lớn hoặc số creator tự báo.

## Kênh mới (tạo ≤365 ngày) đang đăng trong 48 giờ: bao nhiêu sống được (OBSERVED)

| Ngách | Kênh đăng trong 48h | Trong đó <1K sub | Kênh mới: số kênh / ≥1K sub / ≥10K sub | Kênh mới có video ≥100K / ≥1M trong 30 ngày | RPM |
|---|---|---|---|---|---|
| History documentary | 75 | 59 | 49 / 5 / 4 | 5 / 0 | Education $10,22 (MEASURED class) |
| Western / faith heartwarming (người lớn tuổi) | 68 | 54 | 48 / 7 / 2 | 2 / 0 (còn nhiều kênh 37–120 ngày có 72K–119K view mỗi video) | $16–28 (practitioner) |
| Disaster documentary / 3D | 66 | 50 | 42 / 7 / 3 | **19 / 7** | ~$2–10 (News/Education, INFERRED) |
| WW2 / military | 89 | 68 | 64 / 7 / 3 | 15 / 1 | ~$4–15 (INFERRED) |
| Senior family drama / revenge | 28 | 13 | 19 / **9** / 3 | 8 / 4 (phần lớn là phim drama) | $3–13 (AGG-EST) |
| Slow English | 54 | 39 | 41 / 7 / 3 | 10 / 2 | ~$0,5–3 (INFERRED theo nước người xem) |
| Nature / wildlife | 62 | 41 | 37 / 6 / 2 | 22 / 3 (nhiều cảnh động vật dạng AI) | ~$3–10 |
| Bible stories | 53 | 39 | 34 / 4 / 1 | 5 / 0 | $4–18 (AGG-EST); 16% video là nội dung trẻ em |
| Minecraft horror | 65 | 45 | 14 / 2 / 0 | 5 / 2 | Gaming $2,05 (MEASURED) |
| **History for sleep** | 81 | **79** | 64 / **1** / 0 | 6 / 0 | $8–35, nhưng **gần như tất cả kênh mới thất bại** |
| **Sleep stories (fiction)** | 65 | **61** | 48 / **1** / 0 | 1 / 0 | Bão hòa |
| Kids animation | 35 | 16 | 17 / 4 / 3 | 8 / 6 | $0,33; **89% video là nội dung trẻ em** |

Đủ 22 ngách và mô hình tiền ở `wide_scan.md`.

## Kết luận (PROPOSED)

**Kênh A: tài liệu lịch sử 30–60 phút, có dựng 3D**
- Chủ đề: thảm họa lịch sử, kỹ thuật, WW2, "how people lived".
- Lý do chọn:
  - RPM thuộc nhóm Education, nhóm duy nhất có RPM cao được đo thật ($10,22).
  - Có kênh mới thắng: Arthur Revives the Past (tạo 2026-01, 880K view/video 57 phút), Landfall (tạo 2026-10, 601K).
  - Disaster 3D có nhiều kênh mới bứt phá nhất: TALEYE 4,4M, Fault Lines 1,9M, reci 2,8M, đều dưới 40 ngày tuổi.
- Hợp năng lực: CineFactory có Blender 3D, Afanta lo kịch bản và TTS.
- Bản sleep (3–5 giờ) chỉ là bản ghép thêm, **không mở kênh riêng**, vì 79/81 kênh sleep history đăng gần đây có dưới 1K sub.

**Kênh B: truyện miền Tây / đức tin / ấm lòng cho người Mỹ lớn tuổi, 30–40 phút**
- Đây là ngách con đang lên. Các kênh 37–120 ngày tuổi đã có 72K–119K view mỗi video: Western Faith Tales, Brave Wild West, Tales of Western Faith, Faithful Western Stories.
- RPM do creator tự báo $16–28.
- Đúng thế mạnh của Afanta.
- Rủi ro: tiêu đề kiểu "She said… He said…" đang bị làm theo khuôn. Cần truyện gốc, cấu trúc đa dạng, hình minh họa có đầu tư.

**Không chọn**
- History-for-sleep và sleep fiction làm kênh riêng: bão hòa.
- Revenge drama: rủi ro chính sách "emotionally manipulative".
- Slow English: RPM thấp, nội dung lệch về trẻ em.
- Nature dùng AI: vướng mục "animals in distress" trong chính sách 7/2026.
- Kids: phần lớn video là nội dung trẻ em.
- Minecraft horror: RPM $2, kênh mới 2/14 đạt 1K sub. Giữ làm dự án thương hiệu sau.
- Personal finance và true crime (bodycam): rủi ro chính sách và nội dung tái sử dụng.

**Cổng thử nghiệm**
- Mỗi kênh làm 6 video.
- Đạt nếu có ít nhất 1 video ≥10K view trong 28 ngày và trung vị ≥1K.
- Đo RPM thật ngay khi kênh được bật kiếm tiền.
