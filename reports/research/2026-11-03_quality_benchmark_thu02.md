# Đối chiếu chất lượng: cảnh thử Mine-imator thu02 vs đối thủ (2026-11-03)

## Nguồn và cách đo

**Video của ta**
- `BinBo_MineImator_thu02_anhsang.mp4`: 17 s, 1080p24, lighting recipe B + subsurface, Kokoro VO + music mix.

**Video đối thủ**
- Watched in a Chrome tab on 2026-11-03, muted.
- Took 60 s from the opening plus one 60 s window from the middle of each video.

| Video | Kênh | Lượt xem (OBSERVED) | Lớp sản xuất (INFERRED từ khung hình) |
|---|---|---|---|
| [Baby Steve Becomes Thor](https://www.youtube.com/watch?v=twcBG93WBQE) | BigSchool (kênh mẫu của chủ kênh) | 7.40M | Hoạt hình 3D ngôi thứ ba, rig khối Minecraft — **cùng lớp với Mine-imator của ta** |
| [JJ BUS EATER was Buried Under The Water](https://www.youtube.com/watch?v=Lnl-4FT77Ws) | MSToons | 1,296,839 | Hoạt hình 3D cao cấp: bối cảnh đầy đủ, camera động, hạt hiệu ứng, HUD đồ họa, 4K |
| [SURVIVING in BUS During ZOMBIE APOCALYPSE](https://www.youtube.com/watch?v=UH1HSIN4L20) | Maizen | 4.77M | Phần lớn là gameplay góc nhìn thứ nhất (HUD Minecraft) + phụ đề to dán chết + cảnh dàn dựng ngôi thứ ba |
| [Steve and Alex rescuing a Baby Villager… Pizza](https://www.youtube.com/watch?v=tRXWDQFJ1Do) | DL Minecraft | 502K | **Video AI** (người thật bán-hiện-thực, góc dưới phải có dấu ✦), không phải hoạt hình Minecraft |

**Metrics (identical on both sides)**
- Every frame is shrunk to 160×90 and read every 0.2 s.
- Our video is measured with `tools/mineimator/benchmark_frames.py`; competitors with `tools/mineimator/benchmark_sampler.js`, which seeks and reads pixels inside the page and downloads nothing.
- Test: `tests/test_mineimator_scene.py::test_benchmark_frames_counts_hard_cuts`.
- Detected cuts are approximate (±20%, INFERRED). A flash or a whip pan can count as a cut.

## Số đo (OBSERVED 2026-11-03)

| Chỉ số | **Ta (thu02)** | BigSchool 0–60 s / 120–160 s | MSToons 0–60 / 360–420 s | Maizen 0–60 / 600–660 s |
|---|---|---|---|---|
| Độ phân giải tải lên | 1920×1080 | 1920×1080 | **3840×2160** | 1920×1080 |
| Cắt cảnh / phút | 17.6 | **45 / 39** | 13 / 12 | 13 / 7 |
| Độ dài shot trung bình | 2.8 s | **1.3 / 1.5 s** | 4.3 / 4.6 s | 4.3 / 7.5 s |
| Chuyển động (median khác biệt khung 0.2 s) | **3.9** (thấp) | 5.4 / 5.1 | **13.1 / 20.3** | 2.9 / 10.6 |
| Độ sáng trung bình (0–255) | **149** (sáng nhất) | 116 / 133 | 73 / 95 | 113 / 81 |
| Tương phản (std độ sáng) | 45.6 | 51.3 / 49.7 | 29.5 / 49.4 | 51.2 / 35.5 |
| Độ bão hòa (0–1) | 0.437 | 0.434 / 0.449 | 0.642 / 0.375 | 0.307 / 0.145 |
| Colorfulness | 74 | 71 / 75 | 77 / 78 | 56 / 37 |

- DL Minecraft was sampled with the older method, which dropped frames, so only its colour is reliable: luma 50, saturation 0.59, colorfulness 40 (dark, warm).
- Its cut count is not used.

## Kết luận từ số đo (INFERRED)

1. **Màu sắc của ta KHÔNG thua.**
   - Our saturation (0.437) and colorfulness (74) are about the same as BigSchool (0.43–0.45 / 71–75).
   - Earlier, from thumbnails only, I said "màu nhạt" (washed out). The measurement shows that was wrong, and the principles file has been corrected.
2. **Ảnh của ta quá sáng và phẳng.** Luma is 149, versus 116–133 for BigSchool and 73–113 for MSToons and Maizen. The reason is a frame that is ⅓ open sky plus bright grass, with no walls or objects to cast shadows.
3. **Ta tĩnh nhất nhóm hoạt hình.**
   - Our motion is 3.9; BigSchool is 5.1–5.4; MSToons is 13–20, because its camera moves all the time and its action is continuous.
   - Our camera stands still in every shot and the characters barely move.
4. **Nhịp cắt ở giữa.**
   - BigSchool, our reference channel, cuts very fast: shots of 1.3–1.5 s, mostly reaction close-ups.
   - MSToons cuts more slowly (4.3–4.6 s), but each shot has a moving camera.
   - So there are two ways to create energy: cut fast with a still camera (BigSchool), or cut less with a moving camera (MSToons). Our scene does neither.
5. **4K:** only MSToons uploads in 4K. This is not a priority; it costs about 4× the render time.

## Đối chiếu bằng mắt (OBSERVED từ khung hình đã xem; đánh giá là INFERRED)

| Hạng mục | Ta (thu02) | BigSchool | MSToons | Khoảng cách |
|---|---|---|---|---|
| Bối cảnh | Bãi cỏ phẳng + trời, không vật thể | Cửa gỗ, tường, cây, nhà, thành phố nền | Đáy biển có san hô, nhà tù có tường + rào thép gai + núi, phòng trong nhà | **Lớn nhất** |
| Bố cục khung | 2/6 khung tốt; 1 khung khối tay vàng che ¼ màn hình (7.3 s); 1 khung nhân vật bị cắt, trời chiếm ⅓ (12.1 s); toàn cảnh nhân vật quá nhỏ (1.3 s, 15.4 s) | Nhân vật chiếm 70–90% chiều cao khung, 2–4 nhân vật/khung | Cận mặt chiếm cả khung; góc thấp, tay tiền cảnh có chủ đích | Lớn |
| Hiệu ứng cảm xúc | Chỉ mắt/miệng | **Nước mắt xanh chảy** trên mặt Steve | HUD "ENEMY?" + khung ngắm đỏ + chữ ZOOM, hạt mảnh vỡ lấp lánh | Lớn |
| Đạo cụ | Không có | Điện thoại hồng, bình thuốc, cung, mũ bảo hộ | Xe buýt quái vật chân nhện, mũ lặn kính | Lớn |
| Khuôn mặt | Rig 4 lớp, mắt to, nhép môi theo thoại | Mặt là da skin, ít biểu cảm động | Mặt pixel phẳng mắt to (cùng kiểu với ta) | **Ta ngang hoặc hơn** |
| Màu/ánh sáng | Ánh sáng ngày ấm, đều | Ánh sáng ngày đều, sáng | Đổi tông theo cảnh (xanh dưới nước, hồng HUD, nắng) | Trung bình (thiếu đổi tông theo cảm xúc) |
| Chữ trên màn hình | Không | Logo @BigSchool | Chữ đồ họa trong cảnh | Nhỏ |
| Âm thanh | −13.1 LUFS, có VO + nhạc + SFX | chưa đo (xem tắt tiếng) | chưa đo | chưa đo |

Chưa so được: story structure and length. Our scene is a 17 s test, while theirs are 13–28 min episodes. Transcripts did not open on YouTube, so dialogue density is not measured.

## Danh sách sửa, xếp theo tác động (INFERRED)

1. **Dựng bối cảnh** from blocks already available in Mine-imator: floor, walls, trees, one house. The `binbo_thu*` generator places block or scenery timelines, so we don't need to wait for a Minecraft Java import. Target: every shot has at least 2 depth planes (foreground and background).
2. **Camera có chuyển động trong mọi shot**: a slow push-in of 5–10%, a slight orbit, and a fast whip pan on joke beats. Target: motion median ≥ 5, at BigSchool's level.
3. **Nhịp hội thoại kiểu BigSchool**: one reaction close-up after each line, average shot 1.5–2.5 s.
4. **Luật bố cục tự kiểm** in the generator:
   - the face sits in the upper ⅓;
   - in a medium shot the character fills ≥ 60% of frame height;
   - sky is ≤ 20% of the frame;
   - nothing may block more than 15% of the frame unless it is meant to.
   Add a test or contact-sheet QC for the first frame of every shot. This fixes the 7.3 s and 12.1 s errors.
5. **Lớp hiệu ứng cảm xúc trên đầu** (surfaces, the same way as the face): tears, sweat drop, blush, anger vein, hearts, "!?".
6. **Một đạo cụ chính mỗi tập** (pizza, treehouse…), shown in the thumbnail and in shot 1.
7. **Hạ độ sáng về 115–130**: frame less sky, sun 1.5 → 1.2, darker ambient, and a light vignette in the edit.
8. **Hạt hiệu ứng** with Mine-imator particles (dust, sparkle, splash) on action beats.

## Giới hạn

- Only 4 videos, and only 2 windows of 60 s each per video.
- Sound was not compared, because the competitor videos played muted.
- The competitor-complete-study gate (watching the whole video, image + sound) has not been met. So statements about acting and sound design remain hypotheses.
- Only the numbers above are OBSERVED.
