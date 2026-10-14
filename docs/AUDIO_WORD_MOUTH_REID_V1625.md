# CineFactory OS v1.6.25 — Audio-Constrained Words / Rendered Mouth Pixels / Multi-Seed Re-ID

**Ngày:** 09-10-2026
**Trạng thái:** Đã code, chạy video thực Blender, chạy synthetic benchmark có negative control; production **BLOCKED** do thiếu căn chỉnh âm vị độc lập, nhận diện nhân vật thực và QC hình dạng khẩu hình cấp cao.
**Git:** working tree trước phase đã có rất nhiều file uncommitted; không reset/commit/deploy, giữ nguyên các thay đổi cũ.

## 1. Hệ thống đã viết

### A. SAPI word timestamps + đối chiếu WAV/PCM

- `scripts/sapi_viseme_synthesize.ps1` thu thập cả `VisemeReached` và `SpeakProgress` ngay từ Windows SAPI, lưu chữ, ký tự đầu, số ký tự, và thời gian bắt đầu trong JSON có file WAV SHA-256.
- `cinefactory/studio/audio_constrained_alignment.py` giải mã WAV thật bằng FFmpeg sang PCM mono 16kHz; xác minh file hash, thứ tự event, chuỗi từ đã chuẩn hóa, vị trí character span, thời lượng, hoạt động năng lượng PCM trong mỗi khoảng của từng từ.
- Nếu audio rỗng, dữ liệu bị sửa, transcript mâu thuẫn hoặc một từ không có tín hiệu đủ ngưỡng: BLOCKED.
- Nguồn timestamps là **SYNTHESIZER_SPEAK_PROGRESS**, tức thời gian do chính TTS tạo. Đây là **audio-constrained consistency**, KHÔNG phải forced alignment trên audio người thật, không nhận dạng âm vị và không xác nhận đúng phát âm.

### B. Rendered rig-mouth projection & measured pixel activity

- `scripts/blender_animation_worker.py` đã thêm `project_viseme_mouth_samples()`: tại các frame chọn từ dòng thoại, Blender đánh giá mouth mesh đã keyframe rồi chiếu 8 góc bounding box vào camera, lưu tọa độ normalized top-left, thời gian, predicted jaw và projected pixel dimensions trong geometry sidecar.
- `cinefactory/studio/rendered_mouth_qc.py` đọc MP4 thật bằng OpenCV; lấy ROI vùng miệng từ projection, tạo ROI union bất biến cho từng dòng, kiểm tra số sample, pixel resolution, dải hoạt động và tương quan với chuỗi jaw cue.
- **Chống bão hòa:** dùng tỷ lệ pixel tối (`DARK_PIXEL_FRACTION`) theo mặc định; chỉ khi signal này không đủ biên độ và inverse mean luminance có biên độ tối thiểu mới dùng `INVERSE_MEAN_LUMA_SATURATION_FALLBACK`. Việc chọn thước đo căn cứ biến thiên ảnh **trước khi** so sánh cue (không chọn thước đo cho score cao nhất).
- Phép đo chuyển động pixel này chưa chứng minh actor thực sự thấy miệng đầy đủ dưới occlusion/chuyển camera, không nhận dạng shape của từng âm vị, không đo độ khớp audio-versus-image độc lập ở mức viseme/phoneme.
- Điểm quan trọng: sidecar rig projection có `visibility_verified: false` vì đây là phép chiếu hình học, không phải face landmark/segmentation độc lập.

### C. Multi-seed actor re-identification benchmark

- `cinefactory/studio/multi_seed_identity_qc.py`: dựng deterministic flat-color synthetic frames theo mỗi seed, background noise, lighting jitter, nhân vật chuyển vị trí và B mất hình hai frame; dùng detector độc lập quét cả khung hình, tính IoU/precision/recall + liên kết định danh xuyên thời gian.
- Ít nhất 3 seed riêng; seed nào không đạt đủ precision/recall hoặc tracking đều chặn đánh giá tổng thể.
- Negative control một seed có vật thể giả mạo màu cùng actor; hệ thống phát hiện và chặn.
- Đây là kiểm thử **controlled scenes**, không đại diện dữ liệu thực phức tạp, Wan 2.1 nhiều seed hay long-form.

### D. Studio integration & qualification

- `cinefactory/appctx.py` và `cinefactory/studio/professional_company.py`: cung cấp `audio_word_alignment`, `rendered_mouth_qc` và phương thức `independent_actor_detection.multiseed(...)`.
- `cinefactory/studio/audio_visual_sync_qc.py`: `PerformanceQualificationGate.assess(..., v185_required=True)` giờ đọc báo cáo word, pixel-mouth và multi-seed thực thay vì tự pass bởi có cue.
- Tự động giữ `INDEPENDENT_FORCED_ALIGNMENT_UNQUALIFIED`, `RENDERED_PHONEME_SHAPES_UNQUALIFIED`, `MULTISEED_REAL_VIDEO_IDENTITY_UNQUALIFIED` và các gate temporal/audio-video chưa đầy đủ. Không sửa Wan `SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED`.

## 2. Bằng chứng thực tế

Source/runners:
- `scripts/verify_scene_speech_v185.py` tạo lại WAV + 2 giọng Microsoft David/Zira, viseme event timing, render Blender hai nhân vật trong cảnh front-facing ở `EpisodeSpec.width=1280,height=720` với preview thực tế 50% = 640×360, rồi mux audio.
- `scripts/verify_alignment_mouth_reid_v185.py` đọc bằng chứng từ script trên và xuất JSON tổng hợp: `data/verification/v185_alignment_reid/v185_qualification_evidence.json`.

Media:
- `data/verification/v185_alignment_reid/two_actors_speech_audible.mp4` — video H264/AAC có tiếng nói David/Zira, khoảng 3.75 giây, **640×360 preview**, chưa đạt cinematic 4K.
- `data/verification/v185_alignment_reid/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4.geometry_qc.json` — projections 41 mẫu, geometry/performance cue QC.
- `data/verification/v185_alignment_reid/SPEECH_A_A.wav` và `SPEECH_B_B.wav` + file `.visemes.json` để kiểm tra hash/word timing/viseme provenance.
- `data/verification/v185_alignment_reid/v185_render_evidence.json` — source render manifest.

### Actual word/PCM evaluation

- A / David (`Hello!`): 1 word event, `SYNTH_WORD_PCM_CONSISTENT`; word peak RMS khoảng **0.1597**.
- B / Zira (`Let's go!`): 2 word events, `SYNTH_WORD_PCM_CONSISTENT`; word peak RMS khoảng **0.1633 / 0.0833**.
- Phép đo đúng trong phạm vi dữ liệu của synthesizer; không tự gắn `forced_alignment_verified=true`.

### Actual rendered video pixel evidence

- Trước restaging, nhân vật quay sang nhau và cả A/B FAIL `MOUTH_PIXEL_ACTIVITY_INSUFFICIENT`; không được hạ QC threshold.
- Đổi riêng shot nghiệm thu thành **front-facing**, độ phân giải preview **640×360**.
- Nhân vật A: **PASS**, tín hiệu `DARK_PIXEL_FRACTION`, pixel-vs-keyframe jaw correlation **0.7546**, pixel activity range **0.5652**, 20 samples.
- Nhân vật B: vùng mặt quá tối khiến dark threshold bão hòa 100%; dùng phép đo luma thay thế **chỉ bởi pixel signal range**, không chọn theo score. **PASS**, `INVERSE_MEAN_LUMA_SATURATION_FALLBACK`, correlation **0.7647**, range **0.0532**, 21 samples.
- 41 projection samples thực từ Blender, trường `image_mouth_motion_measured=true`, `phoneme_shapes_verified=false`, `production_qualified=false`.
- Video chứng minh các vùng miệng *thay đổi pixel tương quan với cue được dựng*, chứ không xác nhận trực tiếp ảnh nói đúng từng âm vị hoặc giọng trùng nhân vật trong cảnh thật.

### Multi-seed baseline & negative control

- Seeds `[1, 7, 16]`, 12 frame/seed, B vắng hai frame giữa shot.
- Cả 3 seed đạt ngưỡng controlled benchmark; worst precision = **0.954545...**, worst recall = **0.954545...**; không giả định 100% tuyệt đối.
- Seed 7 bị cố ý thêm vật thể khác cùng màu actor: aggregate benchmark **BLOCKED**, xác minh false-positive guard.
- Ground truth synthetic, không dùng kết quả này thay thế benchmark rendered/gameplay/Wan thực.

## 3. Phạm vi an toàn / điều kiện phải đạt trước production

- **Phoneme audio alignment độc lập** (e.g. forced alignment thực, đo confidence, ngữ pháp ngôn ngữ).
- **Ground-truth viseme / face landmarks** và mouth visibility dưới camera moves, occlusions, facial angles; đo pixel-to-phoneme và audio-to-visual latency với tolerance qua kiểm thử có nhãn.
- **Speaker voice attribution** trong dialogue mix và voice license cho sản xuất/monetization; giấy phép Microsoft SAPI phải kiểm tra cụ thể trước khi phát hành thương mại.
- **Real multi-seed / multi-shot identity QA**, đa appearance và rig/pose/style, đánh giá confusion/ID switches, nhân vật giống nhau, chuyển cảnh, ánh sáng khó, so sánh với human labels.
- **Cinematic dailies QC** theo creative brief; không đánh đồng measured metrics với chất lượng thẩm mỹ/Disney.
- **Controlled and production gates remain separate**; chưa nâng mức phê duyệt Wan generative dialogue hoặc 4K.

## 4. Chạy lại

```powershell
python scripts/verify_scene_speech_v185.py
python scripts/verify_alignment_mouth_reid_v185.py
python -m pytest -q tests/test_alignment_mouth_multiseed_v185.py
python -m compileall -q cinefactory scripts tests
python -m pytest -q
```

Bước kế tiếp: **v1.6.26 — Speaker-aware real dialogue alignment & Landmark-Based Mouth Observability + Multi-shot Real Render Re-ID Evaluation**, theo chuẩn fail-closed.


## 5. Kiểm tra end-to-end cuối cùng trên MP4 có audio

Sau render Blender, hệ thống kiểm tra lại **cùng 41 projection samples trên MP4 thực đã mux H.264/AAC** (không chỉ render không tiếng):

- `final_mux_mouth_pixel_qc.status = PIXEL_CONFORMANCE_ONLY_PASS` — cả hai actor PASS trong giới hạn tín hiệu pixel trên khu vực mouth ROI đã cung cấp từ rig.
- RMS âm thanh giải mã từ **MP4 cuối**, theo hai cửa sổ thoại: A **0.05837**, B **0.05253**; không chỉ đo WAV nguồn.
- Hai phép đo này cung cấp độc lập sự hiện diện của audio và sự biến thiên vùng miệng theo cue trong file video cuối. Chúng **không** tạo chứng nhận phoneme-to-viseme synchronization hay chống được clip giả/giọng nhầm nếu thiếu benchmark có nhãn.
- Bằng chứng được lưu trong `data/verification/v185_alignment_reid/v185_qualification_evidence.json` dưới `final_mux_mouth_pixel_qc` và `final_mux_actor_audio_window_qc`.


## 6. Final software verification after full v1.6.25 upgrade

- `python -m compileall -q cinefactory scripts tests` → **PASS**
- `git diff --check` (relevant tracked changes) → **PASS**. Git printed LF→CRLF working tree warnings on Windows; no whitespace errors.
- `python -m pytest -q tests/test_alignment_mouth_multiseed_v185.py tests/test_real_speech_independent_v184.py tests/test_temporal_lipsync_v183.py` → **44 passed**
- `python -m pytest -q` → **644 passed, 0 failed** (196.03s), exit code 0.
- `scripts/verify_scene_speech_v185.py` → completed with two real SAPI speech tracks + Blender render + MP4 audio mux, geometry/performance QC PASS.
- `scripts/verify_alignment_mouth_reid_v185.py` → `DIAGNOSTICS_COMPLETED_PRODUCTION_BLOCKED`, measured word WAV and actual raw/mux video mouth pixel signals PASS, synthetic multiseed control PASS, deliberate impostor BLOCKED.
- Long-form or real-world production qualification: **BLOCKED**. Not a bug in the code; more independent evidence required.
- No auto Git commit, source reset, live deployment or release promotion.
