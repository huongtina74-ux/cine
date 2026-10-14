# CineFactory OS v1.6.23 — Multi-Actor Temporal Re-ID + Dialogue Lip-Sync Qualification

**Ngày:** 09/10/2026
**Trạng thái triển khai:** ĐÃ CODE + CÓ TEST + CÓ BẰNG CHỨNG ĐO THỰC TẾ.
**Trạng thái chuẩn sản xuất tự động:** **BLOCKED**; không tự động gỡ production gate.
**Lưu ý Git:** working tree đã có nhiều thay đổi của các phase trước; tuyệt đối không reset/commit hàng loạt.

## 1. Các hệ thống đã phát triển

### 1.1 Temporal Re-ID: `cinefactory/studio/temporal_reid.py`

- Có contract cho detection độc lập, detection dựa trên reference, và detection gán nhãn thủ công.
- Theo dõi định danh mỗi actor qua nhiều mốc thời gian; tính coverage, minimum appearance score, mất dấu, trở lại sau khi mất dấu.
- Phát hiện vùng ảnh hai actor trùng nhau (IoU >= 0.70), vị trí nhảy quá mức, thời gian không tăng và video lấy mẫu quá thưa.
- So sánh cross-character appearance margin; mặc định threshold identity >= 0.70, margin >= 0.08, coverage >= 80% và mất dấu liên tiếp tối đa 2 mẫu.
- Bắt buộc có bằng chứng nguồn. Tìm vùng bằng reference có thể **gợi ý drift** chứ không chứng minh tính năng phát hiện / re-identification độc lập.
- `assess_reference_seeded_video(...)` lấy mẫu **khung hình video Wan thật** qua OpenCV, đánh giá vùng ảnh bằng CharacterFactory và trả report có provenance.
- Dữ liệu reference-seeded **không thể đạt trạng thái PASS cho independent Re-ID**, và report có `production_qualified = false`.

### 1.2 Audio-Visual envelope QC: `cinefactory/studio/audio_visual_sync_qc.py`

- `windows_from_dialogue()`: tạo speaker windows từ các directive SPEAKER của DialoguePerformanceEngine **sau khi semantic QC đạt**.
- `verify(...)`: xác minh file có video + audio track thật, decode PCM mono bằng FFmpeg, lấy biến thiên vùng miệng có ROI được khai báo trên khung hình thật, tính tương quan theo các lag.
- Chặn missing video/audio, vùng miệng không có hoạt động, speaker windows bị chồng, audio quá yếu và lệch nhịp vượt giới hạn.
- Cấu hình hiện tại: khoảng lệch tối đa 120 ms, tương quan tối thiểu 0.55, video thử nghiệm <= 30 giây. **Đây là ngưỡng kỹ thuật sơ bộ, chưa hiệu chỉnh bằng dữ liệu người xem.**
- Phép đo `AUDIO_ENVELOPE_VS_MOUTH_DARK_PIXEL_ACTIVITY` chỉ chứng minh sự tương quan thô giữa biên độ audio và thay đổi vùng miệng; **không xác nhận phát âm đúng từ/âm vị, mouth shapes, voice identity, alignment chính xác hay chất lượng diễn xuất**.
- `audio_lipsync_measured = false`, `phoneme_alignment_verified = false`, `production_qualified = false`. Kể cả khi envelope PASS vẫn **không** được công nhận phoneme-level lip-sync.

### 1.3 Production qualification

- `PerformanceQualificationGate.assess()` fail-closed với temporal QC hoặc audio-video QC còn thiếu/chưa đạt.
- Cả ba object `TemporalReIDEngine`, `AudioVisualSyncVerifier`, `PerformanceQualificationGate` được chia sẻ qua `AppContext` và `ProfessionalCompanyLayer`.
- Blocker Wan hiện hữu `SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED` **không thay đổi**.

## 2. Bằng chứng chạy trên media

File JSON: `data/verification/v183_temporal_lipsync/qualification_evidence.json`

Runner: `scripts/verify_temporal_lipsync_v183.py`.

### 2.1 Clip Wan của v1.6.22 (thực)

Nguồn `data/verification/v182_three_actor_dialogue/wan/S_ABC.wan.mp4`, 320×176, 16 fps, 17 frames, khoảng 1,06 giây.

Khi lấy **10 sample** (thay vì 3 của v1.6.22), cross-reference seeded search cho thấy:

| Actor | Frame được ghép đủ tin cậy | Frame không đủ | Coverage | Kết quả |
|---|---:|---:|---:|---|
| A | 4 | 6 | 40% | FAIL |
| B | 5 | 5 | 50% | FAIL |
| C | 1 | 9 | 10% | FAIL |

Thấp hơn coverage floor 80%. Nhiều `REFERENCE_SEEDED_CROSS_IDENTITY_CONFUSION` được phát hiện. **Chưa thể kết luận video thật sự đổi nhân vật**, vì score từ vùng ảnh tham chiếu cố định có thể dễ nhầm ở resolution thấp. Nhưng rõ ràng **không đủ bằng chứng để pass Re-ID dài hạn**.

Clip này **không có audio track**, nên `AudioVisualSyncVerifier` trả `ACTUAL_AUDIO_TRACK_REQUIRED`. Không được coi là có kiểm chứng lip-sync.

### 2.2 Synthetic controls — dùng để chứng minh cơ chế test

Fixture sinh tự động trong `data/verification/v183_temporal_lipsync/`: video miệng hình chữ nhật đóng/mở + audio beep 440Hz được ghép vào MP4. **Không phải giọng nói, không phải diễn xuất người thật / Minecraft, không phải TTS.**

- Positive A/V control: `ENVELOPE_ONLY_PASS`, tương quan khoảng **0.946**, best-offset xấp xỉ 0 ms.
- Delayed mouth control (+6 frame ở 20 fps): `BLOCKED`; offset đo khoảng **-300 ms**, vượt 120 ms.
- Thử nghiệm thiếu audio: `BLOCKED`, không tự điền audio giả.
- Production decision trên bằng chứng video Wan thực: `BLOCKED`.

## 3. Code và tests

Các file chính:

- `cinefactory/studio/temporal_reid.py`
- `cinefactory/studio/audio_visual_sync_qc.py`
- `cinefactory/appctx.py`
- `cinefactory/studio/professional_company.py`
- `tests/test_temporal_lipsync_v183.py`
- `scripts/verify_temporal_lipsync_v183.py`
- `docs/TEMPORAL_REID_LIPSYNC_V1623.md` (tài liệu này)

Câu lệnh xác minh (chạy tại repository):

```powershell
python scripts/verify_temporal_lipsync_v183.py
python -m pytest -q tests/test_temporal_lipsync_v183.py
python -m compileall -q cinefactory scripts tests
python -m pytest -q
```

## 4. Production gates còn thiếu, không được đánh tráo

1. **Independent multi-object detection** có ID track ổn định, không dùng crop dựa trên vị trí cố định làm bằng chứng duy nhất.
2. **Dense/long-video evaluation:** nhiều scene, góc máy, seed, chuyển cảnh, che khuất thật, nhân vật có ngoại hình gần giống nhau.
3. **Audio thật của lời thoại:** TTS/voice-recording đủ quyền sử dụng, có audio IDs/hash và temporal alignment đã xác minh.
4. **Viseme from phoneme:** chạy forced alignment chính xác theo audio thực, map phoneme→viseme theo rig; animate và đo sai lệch của hình mouth theo từng âm, không chỉ biên độ audio.
5. **Speaker diarization & stem isolation:** không gán audio nền, sound effects hoặc nhạc làm giọng nói; không suy speaker từ mono mixed track.
6. **Face/mouth landmarks & per-actor ROI tracking:** vùng miệng được phát hiện/định vị tin cậy xuyên chuyển động/góc máy thay vì ROI cố định.
7. **Human-reviewed aesthetic QC:** không coi measured cue-conformance hay correlation là chất lượng Disney.
8. **Benchmark có nhãn ground-truth:** tinh chỉnh ngưỡng bằng false accept/reject, đo precision, recall, offset MAE trước khi nâng trạng thái gate.

## 5. Bước tiếp theo đề xuất

**v1.6.24 — Real Speech/Viseme Runtime + Independent Actor Detector Benchmark**: xây đường âm thanh→forced alignment→viseme→Blender/Wan evidence, thêm detector độc lập, tập dữ liệu nhiều góc/seed/occlusion có ground truth, giữ fail-closed khi thiếu bằng chứng.

Hệ thống chưa được công nhận hoàn toàn tự động cho hội thoại nhiều nhân vật. v1.6.23 là giai đoạn đo lường + gating, giúp phát hiện lỗi thực từ sớm thay vì tự xác nhận PASS trên dữ liệu chưa đủ.


## 6. Kết quả hồi quy cuối cùng (đã xác minh)

- `python -m compileall -q cinefactory scripts tests` → **PASS**.
- `python -m pytest -q tests/test_temporal_lipsync_v183.py` → **14 PASS**.
- `python -m pytest -q` → **614 PASS, 0 FAIL**, 193.33 giây (lần chạy sau toàn bộ thay đổi v1.6.23).
- Script bằng chứng `scripts/verify_temporal_lipsync_v183.py` → hoàn tất, trạng thái `DIAGNOSTICS_COMPLETED_PRODUCTION_BLOCKED`; trạng thái là dự kiến do fail-closed, không phải lỗi chương trình.
- **Không release/unblock Wan Semantic Performance, không deploy, không git commit tự động**. Những mốc này cần đánh giá riêng dựa trên test giọng nói và khẩu hình thực sự.
