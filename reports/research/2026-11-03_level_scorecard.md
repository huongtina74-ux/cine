# Bin & Bo đang ở mức nào so với đối thủ? (2026-11-03)

**Nguồn dữ liệu**
- Số đo hình ảnh: `tools/mineimator/benchmark_frames.py` và `benchmark_sampler.js`, cùng một cách đo cho mọi bên.
- Số đo âm thanh: cửa sổ 100 ms, đo RMS và tỉ lệ năng lượng 300–3400 Hz / dưới 150 Hz. Đối thủ đo trong trình duyệt, của ta đo bằng numpy theo đúng công thức đó.
- Tốc độ sản xuất: lấy từ `data/research/raw/2026-11-03_minecraft_story.json` (ngày đăng quy đổi từ "x weeks ago", nên là số xấp xỉ).
- **OBSERVED** = số đo được. **INFERRED** = đánh giá hoặc ước tính.

## 1. Tốc độ sản xuất (OBSERVED, video dài đăng trong ≤30 ngày)

| Kênh | Video dài / 30 ngày | Phút / 30 ngày | Độ dài trung vị | View trung vị |
|---|---|---|---|---|
| Maizen | 21 | 466 | 19.3' | 1.6M |
| GameToons | 25 | 488 | 8.3' | 881K |
| MyMy toon | 29 | 359 | 10.3' | 403K |
| MSToons | 21 | 242 | 11.2' | 1.6M |
| ZomBo | 12 | 161 | 10.2' | 64K |
| Морфиз | 8 | 105 | 13.0' | 258K |
| Mine Block | 4 | 98 | 10.1' | 1.1M |
| Class Monster School | 7 | 98 | 11.2' | 146K |
| Cubeee Animations | 3 | 72 | 8.4' | 1.93M |
| BigSchool | 0 | 0 | 11.4' | 1.7M |
| **Bin & Bo (ta)** | 0 tập (3 cảnh thử) | **0.83** (17 s + 17 s + 16 s) | 16 s | — |

**Thời gian render của ta** (OBSERVED, theo mốc thời gian file):
- 16 s phim mất 8'38"–8'51" (1080p, 48 samples, RTX 3060), khoảng 1.35 s/khung.
- Quy ra: khoảng 33 phút render cho 1 phút phim (INFERRED).

## 2. Hình ảnh (OBSERVED, khung 160×90 lấy mẫu mỗi 0.2 s)

| Chỉ số | Ta thu03 v2 | BigSchool | MSToons | Maizen |
|---|---|---|---|---|
| Độ phân giải | 1080p | 1080p | **2160p** | 1080p |
| Cắt cảnh / phút | 15 | **39–45** | 12–13 | 7–13 |
| Chuyển động | **10.4** | 5.1–5.4 | 13–20 | 2.9–10.6 |
| Độ sáng | 138 | 116–133 | 73–95 | 81–113 |
| Độ bão hòa | 0.46 | 0.43–0.45 | 0.38–0.64 | 0.15–0.31 |

## 3. Âm thanh (OBSERVED, 30 s mỗi video; YouTube có chuẩn hóa âm lượng nên chỉ so tương đối)

| Chỉ số | Ta thu03 v2 | Ta thu02 | BigSchool 2:00–2:30 | MSToons 3:20–3:50 |
|---|---|---|---|---|
| RMS dBFS | −15.8 | −13.7 | −19.2 | −17.6 |
| Đáy (p10) | **−39.7** (có khoảng gần im lặng) | −25.7 | −33.6 | −21.3 (nền nhạc liên tục) |
| Thời lượng có tiếng | 94% | 99% | 98% | 100% |
| Dải giọng nói chiếm ưu thế | 42% | 42% | 67% | 3% (đoạn này toàn nhạc + SFX) |
| Tỉ lệ năng lượng trầm (<150 Hz) | **0.11** | 0.07 | 0.17 | **0.57** |

**Nhận xét (INFERRED)**
- Nhạc tự tổng hợp của ta rất mỏng, gần như không có âm trầm.
- thu03 không có lời thoại và có những đoạn hụt tiếng.
- Đối thủ luôn có một lớp nhạc nền dày và liên tục.
- Chất lượng giọng lồng tiếng của đối thủ chưa đo được, vì YouTube không mở bản chép lời.

## 4. Bảng điểm (INFERRED, thang 10, so trong cùng ngách)

| Hạng mục | Ta | BigSchool | MSToons | Ghi chú |
|---|---|---|---|---|
| Kỹ thuật hình (độ nét, màu, ánh sáng) | 6 | 6 | 8 | Màu ngang BigSchool; MSToons có 4K và đổi tông màu theo cảnh |
| Bối cảnh | 3 | 6 | 9 | Ta mới có 1 phòng nhỏ |
| Biểu cảm khuôn mặt | 6 | 5 | 8 | Mắt tim, "><", lồi, má hồng, mồ hôi; còn thiếu má phồng 3D và miệng dính đồ ăn |
| Diễn xuất cơ thể | 5 | 7 | 8 | Thiếu tư thế cực đoan (té lộn ngược) và gag đổi kích thước |
| Góc máy | 6 | 6 | 8 | Đã đủ loại góc; còn thiếu camera bám theo dài và góc POV |
| Nhịp dựng | 5 | 8 | 8 | BigSchool cắt cảnh nhanh gấp 3 lần ta |
| Âm thanh | 3 | 6 | 8 | Nhạc mỏng, có khoảng hụt tiếng, chưa có giọng thật trong thu03 |
| Nội dung / câu chuyện | 2 | 7 | 8 | Ta chỉ có các gag 16 s, chưa có tập 8–12 phút |
| Tốc độ sản xuất | 1 | — | 9 | Ta chưa ra 1 phút phim/tuần; MSToons khoảng 56 phút/tuần |
| IP gốc / an toàn kênh | **9** | 9 | 4 | Phần lớn kênh dẫn đầu dùng nhân vật Maizen (rủi ro bản quyền); ta là nhân vật gốc |

**Tổng (INFERRED):**
- Từng khung hình riêng lẻ đã gần mức BigSchool.
- Nội dung, âm thanh và tốc độ thì còn ở mức "phòng thí nghiệm".
- Ước chừng ta đạt khoảng 35–40% chất lượng tổng thể của BigSchool, và khoảng 1% sản lượng của MSToons.

## 5. Khoảng cách theo thứ tự ưu tiên (INFERRED)

1. **Nội dung:** làm tập đầu dài 8–10 phút, có cốt truyện và lời thoại (L1–L7 trong `minecraft_story_principles.md`).
2. **Tốc độ:** tập hợp các cảnh thành một tập, render bản nháp 24 samples để soát lỗi, render đêm, chỉ render lại cảnh có sửa, và đóng các bản Mine-imator thừa. Mục tiêu là 1 tập/tuần trước, sau đó 2 tập/tuần.
3. **Âm thanh:**
   - Nền nhạc liên tục, có bè trầm (nhạc có giấy phép rõ ràng, ví dụ Incompetech có ghi công).
   - Thêm lớp hiệu ứng tiếng.
   - Giọng nhân vật có giấy phép thương mại.
   - Không để khoảng lặng dưới −35 dBFS.
4. **Bối cảnh:** xây thư viện set (nhà, bếp, rừng, khe núi) từ block; về sau import world bằng Minecraft Java.
5. **Nhịp dựng:** cắt cảnh nhanh hơn trong đoạn thoại (shot 1.5–2.5 s, mục tiêu 25–30 cắt/phút).
