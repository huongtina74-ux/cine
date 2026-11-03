# Lộ trình đưa Bin & Bo lên ngang MSToons (lập 2026-11-03, INFERRED)

Điểm xuất phát lấy từ `2026-11-03_level_scorecard.md`.
- Hình ảnh: khoảng 6/10, gần BigSchool.
- Yếu nhất: nội dung 2, âm thanh 3, tốc độ 1.
- MSToons (OBSERVED): khoảng 21 video dài và 242 phút mỗi 30 ngày, 4K, tập 11 phút.

## Nguyên tắc
1. **Chất lượng trước, sản lượng sau.** Tập 1 phải đạt chuẩn rồi mới nhân số lượng.
2. **Biến kịch bản thành dự án bằng máy.** Kịch bản → shot list JSON → keyframe, bằng thư viện bối cảnh, tư thế, biểu cảm, góc máy và hiệu ứng tiếng. Không chỉnh tay từng tập.
3. **Mọi tiêu chí đều có số đo**, dùng `benchmark_frames.py`, máy đo âm thanh, contact sheet dày và bảng điểm.

## Theo từng hạng mục

| Hạng mục | Hiện tại | Mục tiêu MSToons | Cách làm |
|---|---|---|---|
| Nội dung | gag 16 s | tập 8–12', có nối tiếp và phần tiếp theo | Series bible Bin/Bo/Zu; khung tập: hook ≤30 s, leo thang mỗi 60–90 s, 3 hồi, cliffhanger; bám L1–L7; mỗi 4–5 tập có một bản compilation 30–45' |
| Bối cảnh | 1 phòng | 10+ set lớn | Thư viện set bằng block (nhà, bếp, phòng ngủ, rừng, làng, khe núi, hang, biển, trường, công viên); sau khi mua Minecraft Java thì import world hoặc dùng MCprep |
| Diễn xuất | squash/stretch, nhảy | tư thế cực đoan, gag vật lý | Thư viện 50 tư thế và 20 gag (té lộn ngược, bị nhốt, phóng to/thu nhỏ, bay); đà lấy trước và quá đà; chuyển động phụ; nhép môi theo thoại |
| Biểu cảm | 13 kiểu mắt, 18 kiểu miệng, hiệu ứng | phong phú hơn, có khối 3D | Miệng dính đồ ăn, mắt xoáy, mắt sao, nước mắt chảy dòng, mặt đỏ giận; má phồng thật thì làm ở Blender |
| Góc máy | đủ loại, phần lớn đứng yên | camera luôn chuyển động | 20 preset (POV, bám theo, quay quanh, crash zoom, khung trong khung); shot list chọn preset theo cảm xúc |
| Dựng | 15 cắt/phút | 25–30 cắt/phút khi thoại | Cận mặt phản ứng sau mỗi câu; flash chuyển cảnh; chữ trên màn hình; cắt khớp với hiệu ứng tiếng |
| Âm thanh | nhạc mỏng (trầm 0.07–0.11), có khoảng lặng | nền dày (trầm ≈0.5), không lặng | Thư viện nhạc có giấy phép (YouTube Audio Library, Incompetech CC-BY), mỗi cảm xúc một bài; SFX CC0 cùng sfxkit; foley tự gắn theo hành động; giọng nhân vật; ducking; −14 LUFS; sàn tiếng ≥ −35 dBFS |
| Độ phân giải | 1080p | 2160p | Trước mắt giữ 1080p; lên 1440p/4K khi đã có render đêm hoặc GPU thứ hai |
| Tốc độ | 50 s / 2 ngày | 56'/tuần | Tự động hóa cùng render đêm; cân nhắc Blender headless vì không cần bấm giao diện (xem dưới) |
| Đóng gói | — | thumbnail mặt to, màu rực | Thumbnail render tư thế hero + hiệu ứng 2D; tiêu đề theo L2; YouTube Test & Compare |

## Nút thắt cổ chai thật sự: render và điều khiển giao diện
- Mine-imator không có dòng lệnh. Mỗi lần render đều phải bấm giao diện, và đã nhiều lần bị kẹt cửa sổ, mất focus.
- CineFactory đã có worker **Blender headless** (blender-td).
- Cần làm benchmark một ngày cho cùng một cảnh, giữa Mine-imator và Blender EEVEE + MCprep. So 4 thứ: điểm hình, thời gian render, mức tự động hóa, độ khó dựng nhân vật. Kết quả quyết định đường chính cho sản xuất hàng loạt.

## Mốc kiểm tra
- **Tuần 2:** tập 1 dài 8–10'. Không còn lỗi QC (khối, chèn mặt). Nội dung ≥5, âm thanh ≥5, ≥25 cắt/phút khi thoại.
- **Tuần 6:** 2 tập/tuần. 8 set. Tỉ lệ âm trầm ≥0.3. Hình ≥7.
- **Tuần 12:** 3 tập/tuần cộng 1 compilation. Mọi hạng mục ≥7. Thử 1440p/4K.

## Quyết định của chủ kênh (cần anh trả lời)
1. Mua Minecraft Java để import world (đã duyệt, chưa xác nhận đã mua).
2. Giọng nhân vật: TTS miễn phí, thuê diễn viên lồng tiếng, hay giọng của anh.
3. Có làm benchmark Blender headless song song không.
4. Có tính đến GPU thứ hai hoặc render cloud (tốn tiền) để lên 3+ tập/tuần và 4K không.
