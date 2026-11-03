# Biểu cảm và góc máy của đối thủ: xem từng khung (2026-11-03)

**Owner request (OWNER, 2026-11-03 20:00):** "TÔI THẤY BIỂU CẢM, GÓC MÁY... HỌ LÀM RẤT NGỘ NGHĨNH CHI TIẾT CHỨ KHÔNG ĐƠN GIẢN NHƯ CÁCH CHÚNG TA LÀM". In English: "I see their expressions, camera angles... are very playful and detailed, not simple like the way we do it."

**Method**
- Watched in my own Chrome tab, muted.
- Paused frames by seeking: every 3–4 s across selected stretches of 2 videos.
- These are paused frames, not full viewing, so the competitor-complete-study gate is not met. Conclusions about acting rhythm and sound are hypotheses.
- Timestamps are OBSERVED; the "what we learn" column is INFERRED.
- We learn techniques only. We do not copy characters, names, sets or scripts.

## Video đã xem

- [JJ's Girl EAT JJ CAKE](https://www.youtube.com/watch?v=qtWfSIqNfdU), MSToons, 7.01M views. Frames at 0:04–0:39, 3:21–3:33, 5:00–5:08 and 7:32–7:36.
- [Baby Steve Becomes Thor](https://www.youtube.com/watch?v=twcBG93WBQE), BigSchool, 7.40M views. Frames at 2:04–2:21.
- From the earlier benchmark pass: [JJ BUS EATER was Buried Under The Water](https://www.youtube.com/watch?v=Lnl-4FT77Ws), at 6:00–7:00.

## Danh mục (OBSERVED → INFERRED)

| Nhóm | Thấy ở đâu | Họ làm gì | Ta học gì (kỹ thuật, không chép nội dung) |
|---|---|---|---|
| Mắt | MSToons 0:19 | Mắt trái tim hồng có chấm sáng trắng | Trạng thái mắt `heart` |
| Mắt | MSToons 0:04 | Mắt lim dim thỏa mãn khi ăn | `half` + miệng nhai |
| Mắt | MSToons 7:36, BUS EATER ~6:50 | Mắt mở to tròng xanh, có chấm sáng | `sparkle` / `popped` |
| Mắt | BigSchool 2:04 | Mắt nhắm chặt khi té | `squeeze` (> <) |
| Má | MSToons 0:04, 0:19 | Má hồng tròn lớn, nổi rõ | Lớp `blush` + khối má 3D |
| Má | MSToons 7:36 | Má phồng to khi nhét đầy bánh | Khối má 3D `cube` phồng theo nhịp nhai |
| Miệng | MSToons 0:04, 7:36 | Miệng dính kem/vụn bánh, há có răng/lưỡi | `chew1/2`, `drool`, `scream` |
| Đầu | MSToons 0:19 | Đầu nghiêng (roll) khi say mê | `ROT_Y` trên `head`, lắc qua lại |
| Thân | MSToons 3:33 | Bụng phình to sau khi ăn (đổi tỉ lệ thân) | Squash/stretch bằng `SCA` |
| Thân | BigSchool 2:04 | Té lộn ngược qua ghế, chân chổng lên | Tư thế cực đoan, không chỉ giơ tay |
| Thân | BigSchool 2:11 | Hai tay giơ cao khi la | Tay bật lên khi giật mình |
| Gag kích thước | MSToons 5:08 | Nhân vật nhỏ xíu cạnh khúc gỗ khổng lồ | Đổi scale nhân vật/đạo cụ |
| Gag kích thước | MSToons 0:39 | Bị nhốt trong khối thạch dưới cái gắp | Tình huống gag vật lý |
| Góc máy | MSToons 0:27 | Góc nhìn từ trong miệng đang há | POV cực cận |
| Góc máy | MSToons 0:14 | Góc cao nhìn xuống đồ ăn có mặt | High angle |
| Góc máy | MSToons 0:35 | Sát đất ngước lên trời khi nhân vật bay | Worm's-eye |
| Góc máy | MSToons 5:04 | Qua vai, nền mờ | OTS + DOF |
| Góc máy | MSToons 3:24–3:30 | Camera bám theo nhân vật chạy | Tracking |
| Góc máy | BigSchool 2:21 | Tiền cảnh là đạo cụ (màn hình máy tính) | Khung trong khung |
| Hiệu ứng | MSToons 0:27 | Vòng xoáy cam khi bị nuốt | Hạt/hình 2D |
| Hiệu ứng | MSToons 0:31 | Chớp trắng chuyển cảnh | Flash frame (bước dựng) |
| Hiệu ứng | MSToons 3:24–3:33 | Tuyết, hơi lạnh, vệt gió trắng | Billboard 2D |
| Hiệu ứng | MSToons 3:21 | Chữ ngay trong cảnh ("Very Cold / Very Hot") | Biển chữ trong set |
| Hiệu ứng | MSToons 7:32 | Kẹo rắc bay khắp khung | Hạt |
| Bối cảnh | Mọi khung | Nhà kẹo, hồ băng, phòng gỗ, ghế, giường, bàn máy tính | Set bằng block có sẵn |

## So với scene 02 của ta (OBSERVED từ contact sheet thu02)

- **Mặt:** chỉ có 4 lớp phẳng với 8 kiểu mắt; không có má, mắt trái tim hay hiệu ứng.
- **Đầu:** luôn thẳng đứng, không có squash/stretch.
- **Thân:** chỉ có giơ tay và bước đi.
- **Camera:** ngang tầm mắt và đứng yên. Không có DOF, không rung, không nghiêng khung.
- **Bối cảnh:** bãi cỏ trống.

## Công cụ Mine-imator có sẵn mà ta chưa dùng

Đọc trong mã nguồn Mine-imator 2.0.2, file `GmProject/scripts`:

- **Rung máy:** `CAM_SHAKE`, `CAM_SHAKE_STRENGTH_*` và `CAM_SHAKE_SPEED_*`.
- **Xóa phông:** `CAM_DOF`, `CAM_DOF_DEPTH`, `CAM_DOF_RANGE`, `CAM_DOF_FADE_SIZE` và `CAM_DOF_BLUR_SIZE`.
- **Viền tối:** `CAM_VIGNETTE*`.
- **Uốn khớp:** `BEND_ANGLE_*`. Chưa kiểm chứng cho rig người.
- **Block lặp lại thành mảng:** template `block` với `repeat_enable` và `repeat`.
- **Billboard:** shape có `face_camera`.
- **Đổi màu:** `RGB_MUL` và `MIX_COLOR`.
- Khi lưu, keyframe chỉ ghi những giá trị khác mặc định, nên `VISIBLE: false` phải ghi rõ.

## Đã làm: scene 03 (`tools/mineimator/binbo_thu03/`)

- **Nội dung:** "Zu ngửi thấy pizza", dài 16 s, không lời, 6 shot.
- **Chuẩn bị file:** `prep.py`, `fx.py`, `build.py`; kiểm tra bằng `tests/test_mineimator_scene.py`.
- **Kỹ thuật dùng:** mắt heart/sparkle/squeeze/popped, má 3D phồng, mồ hôi trượt, "!" và "?" bật lên, tim bay, vụn bánh, hơi nước.
- **Diễn xuất:** đầu nghiêng, squash/stretch, nhún lấy đà rồi nhảy theo đường cong, đáp xuống thì bẹp người.
- **Camera:** góc thấp, crash zoom qua vai, rung máy, sát đất bám theo, góc cao, kéo lùi, nghiêng khung, DOF, vignette.
- **Bối cảnh:** sàn, tường, bàn, kệ sách, chậu hoa và thảm từ block có sẵn của Mine-imator.

Render kiểm chứng: `BinBo_MI_thu03`. Lỗi tìm thấy và cách sửa ghi trong `tools/mineimator/MEASURED_FACTS.md`.

## Kết quả đo scene 03 (bản c, OBSERVED 2026-11-03, `benchmark_frames.py`)

| Chỉ số | thu02 | **thu03** | BigSchool | MSToons |
|---|---|---|---|---|
| Chuyển động (median khác biệt khung 0.2 s) | 3.9 | **9.8** | 5.1–5.4 | 13–20 |
| Độ sáng | 149 | **139** | 116–133 | 73–95 |
| Độ bão hòa | 0.437 | 0.459 | 0.43–0.45 | 0.38–0.64 |
| Loudness | −13.1 LUFS | −14.4 LUFS | — | — |

**Còn lại (INFERRED từ contact sheet):**
- Ở góc xa, sàn gỗ bị z-fight với mặt đất mặc định. Bản d đã sửa: tắt ground, thay bằng lớp `grass_block` thấp hơn 0.5. Bản d chưa render được: Mine-imator bị treo khi mở bản d, nên chưa kiểm chứng.
- Má 3D phồng lên vẫn khó thấy từ góc cao.
- Độ sáng còn cao hơn BigSchool.
