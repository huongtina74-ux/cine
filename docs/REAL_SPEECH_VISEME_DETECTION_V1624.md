# CineFactory OS v1.6.24 — Real Speech / Viseme Runtime + Independent Actor Detection Benchmark

**Ngày:** 2026-10-09
**Phạm vi:** Hai giọng nói Microsoft SAPI thật → thời gian viseme của synthesizer → mouth keyframes Blender → video có audio; detector tìm nhân vật bằng dấu hiệu màu quét toàn khung hình trong cảnh block có kiểm soát.

**Tình trạng:** Có mã và bằng chứng thực nghiệm. **KHÔNG đạt chuẩn production tự động / cinematic lip-sync / independent multi-actor detection ở môi trường bất kỳ**.

## I. Các module đã code

1. `scripts/sapi_viseme_synthesize.ps1`: sử dụng `System.Speech.Synthesis.SpeechSynthesizer` nội bộ trên Windows, lựa chọn giọng có sẵn theo tên, ghi WAV trực tiếp, bắt event `VisemeReached` với `AudioPosition` và lưu JSON kèm hash SHA-256. Không dùng dịch vụ/API trả phí. Giọng có sẵn: Microsoft David Desktop, Microsoft Zira Desktop, Microsoft Huihui Desktop.
2. `cinefactory/studio/real_speech_viseme.py`: khai báo `SpeechVisemeTrack`, kiểm tra event times, giới hạn audio trong line window; verify WAV stream/duration/hash, JSON sự kiện/giọng/text trước khi cho phép attach. Chuyển SAPI ID thành proxy `jaw_open` + `mouth_width` cho mặt nhân vật block. **Bảng jaw/width do kỹ thuật đề xuất, chưa benchmark phoneme/viseme bằng video có nhãn.**
3. `cinefactory/block_animation/execution.py`: truyền cue `speech_viseme_tracks` từ shot đã cấp phép qua execution plan thực vào worker.
4. `scripts/blender_animation_worker.py`: `apply_speech_visemes()` keyframe `mouth.scale` cho actor thực, kiểm tra phạm vi thời gian, nguồn event, hash, số sự kiện, trùng dòng; ghi `viseme_debug` vào geometry-QC sidecar. Không báo `audio_visual_sync_verified=True` nếu chỉ keyframe.
5. `cinefactory/studio/independent_actor_detection.py`: baseline full-frame color segmentation bằng OpenCV. Dò connected component trên **toàn frame, không khởi tạo region từ actor reference cũ**, đo localization qua IoU với ground truth, precision/recall/false positives, reject lớp màu quá gần nhau; có `IndependentActorDetectionLab` để tạo detector theo profile.
6. `cinefactory/appctx.py` và `cinefactory/studio/professional_company.py`: đưa `real_speech_viseme` và `independent_actor_detection` vào hệ thống điều hành công ty.
7. `tests/test_real_speech_independent_v184.py`: unit/integration tests cho SAPI thật, channel mapping, false positives, detector không có reference crop, temporal reacquisition ngắn, hash tamper, audio duration, stage-to-Blender plan wiring.
8. `scripts/verify_real_speech_independent_v184.py`: chạy end-to-end thật tạo WAV + event cho 2 nhân vật, render Blender, mux audio speech thành MP4, chạy detector benchmark có nhãn và negative control.

## II. Evidence thực tế

Báo cáo máy đọc: `data/verification/v184_speech_detection/v184_qualification_evidence.json`

Media (có thể mở trực tiếp trên máy):

- `data/verification/v184_speech_detection/two_actors_speech_audible.mp4` — video Blender + **hai voice tracks thật của Microsoft SAPI** được trộn theo cửa sổ thời gian, đầu ra H264/AAC.
- `data/verification/v184_speech_detection/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4` — output hình gốc.
- `data/verification/v184_speech_detection/SPEECH_A_A.wav` — David.
- `data/verification/v184_speech_detection/SPEECH_B_B.wav` — Zira.
- `data/verification/v184_speech_detection/SPEECH_A_A.visemes.json` và `SPEECH_B_B.visemes.json` — timing event theo synthesizer.
- `data/verification/v184_speech_detection/independent_actor_control.mp4` — kiểm tra actor A/B trong flat-color synthetic scene, có B tạm mất dấu 2 frame.

Kết quả lần chứng thực đầu tiên:

- WAV David khoảng **1.279 giây**, **6 viseme events**.
- WAV Zira khoảng **1.379 giây**, **8 viseme events**.
- Blender xác nhận đã apply đúng **6 + 8 events**, geometry QC PASS, performance geometry QC PASS.
- MP4 có stream video H.264 **160×90** và audio AAC, tổng thời lượng **3.750 giây**. Độ phân giải này chỉ là **preview kỹ thuật**, chưa phù hợp chất lượng thành phẩm.
- Benchmark detector: **TP 22, FP 0, FN 0**, precision **1.0**, recall **1.0** trên **12 frame synthetic color scene được gán ground truth**. Occlusion 2 frame, temporal association PASS trong đúng ngữ cảnh này.
- Negative control: cố ý thêm vật thể khác cùng màu nhân vật; precision giảm, benchmark **FAIL** như kỳ vọng. Điều này nêu rõ giới hạn của detector.
- `production_qualified=False` cho speech-to-viseme, detector và toàn bộ pipeline; không nới `SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED` của Wan.

### Điều KHÔNG được tự suy diễn

- Có `VisemeReached` không đồng nghĩa có forced alignment độc lập trên giọng người thu.
- Mapping SAPI→ jaw/width mang tính kỹ thuật: **không chứng minh shape đúng từng âm vị**.
- Mouth keyframe QC là evidence animation được áp dụng; **không chứng minh bằng quan sát pixel khẩu hình khớp âm thanh thực trên từng frame**.
- Benchmark 100% trên hộp màu có điều kiện không có nghĩa detector nhận diện được các nhân vật Minecraft/Roblox trong scene nhiều texture, chuyển góc, ánh sáng hoặc video Wan.
- Có hai giọng audio mix không có nghĩa speaker diarization ở cảnh thực đã đo và đạt.
- Chưa có đánh giá thẩm mỹ/chuyên gia, chưa qualified cho long-form tự động, không chứng nhận tiêu chuẩn Disney.

## III. Những việc phải làm trước khi mở gate

- Detector nhiều appearance cues (shape, texture, face, pose/embedding), ground-truth từ nhiều cảnh/seed và chuyển động khó, benchmark false accepts/re-id switches.
- Forced alignment trên audio WAV thực của từng speaker (có timestamps/token confidence), training/validation âm vị và chính tả theo ngôn ngữ.
- Mouth/face landmark hoặc projection 3D đã hiệu chuẩn, frame-by-frame viseme verification thay vì chỉ keyframe sidecar.
- Audio speech mix/stem diarization chính xác khi có overlap; QC âm thanh và lip-sync ở video cuối cùng không dựa vào giả định.
- Review shot nhiều cảnh ở resolution cao, temporal identity và staging; kiểm tra trên nội dung dài với chi phí RTX3060.
- Multi-seed regression, lưu evidence hash và tỷ lệ false accept/false reject, chỉ promote production sau khi đáp ứng các chuẩn riêng.

## IV. Lệnh tái xác minh

```powershell
python scripts/verify_real_speech_independent_v184.py
python -m pytest -q tests/test_real_speech_independent_v184.py
python -m compileall -q cinefactory scripts tests
python -m pytest -q
```

**Bước tiếp theo đề xuất:** v1.6.25 — Audio-constrained phoneme/viseme alignment verification + face/mouth tracking calibration + multi-seed character re-ID. Tiếp tục free/local-first, giữ production QC fail-closed.


## V. Kiểm tra tín hiệu của media cuối cùng (không chỉ WAV nguồn)

Artifact: `data/verification/v184_speech_detection/audio_window_signal_qc.json`.

Audio AAC của chính `two_actors_speech_audible.mp4` đã được giải mã thành mono PCM, đo RMS theo **cửa sổ lời thoại A/B** để kiểm tra tín hiệu thực tồn tại trên output:

| Cửa sổ | Audio RMS |
|---|---:|
| Actor A / David, 0.35–1.629 giây | 0.05837 |
| Actor B / Zira, 2.049–3.429 giây | 0.05253 |
| Im lặng giữa lượt, 1.819–1.999 giây | 0.00000 |

Có hai vùng âm thanh không im lặng, tách bởi vùng yên lặng theo lịch thoại. Đây là bằng chứng **audio thật đã đi qua mux**, không phải phép đo người nghe nghe đúng từng chữ hay đánh giá chất lượng giọng nói/khẩu hình.


## VI. Kết quả hồi quy sau tất cả thay đổi — FINAL

- `python -m compileall -q cinefactory scripts tests` → **PASS**.
- `git diff --check` với các file code tracked có sửa → **PASS** (Windows cảnh báo tự chuyển LF/CRLF khi Git chạm vào file, không phải lỗi).
- `python -m pytest -q tests/test_real_speech_independent_v184.py` → **13 PASS**.
- `python -m pytest -q` → **627 PASS / 0 FAIL**, **189.47 giây** (exit code 0).
- Evidence script chạy lại sau kiểm tra hash/WAV/event source → **PASS**, output `REAL_SPEECH_RENDER_AND_CONTROLLED_DETECTOR_PASS_PRODUCTION_BLOCKED`.
- Log regression được lưu tại `data/verification/v184_speech_detection/regression_v184.txt`.
- Không Git commit/reset, không deploy; không sửa gate gốc `SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED`.

**Release judgment:** v1.6.24 implementation + verification PASS; real-audio speech-to-viseme demonstration available; full cinematic/phoneme-level lip-sync + multi-scene detector **NOT QUALIFIED**.
