# CineFactory OS v1.6.26 — Source-Conditioned Speaker Attribution, Image Mouth Observability, Real Two-Shot Actor Identity

**Ngày:** 2026-10-09  
**Bản chất:** Nâng cấp code và kiểm chứng bằng 2 cảnh Blender thật, WAV thật của Windows SAPI, MP4 cuối cùng và 3 negative controls.  
**Release status:** `REAL_DIAGNOSTICS_AND_NEGATIVE_CONTROLS_PASS_PRODUCTION_BLOCKED`. Không có bằng chứng để cấp chuẩn tự động sản xuất cinematic, Disney-level, hoặc Wan nhiều seed.

## 1. Kỹ thuật đã triển khai

### 1.1. Speaker/source attribution trên file A/V đã mux

`cinefactory/studio/source_speaker_attribution.py` có:
- `ActorVoiceStem`: actor/line/start/end, đường dẫn WAV và SHA-256 để xác thực dữ liệu đầu vào.
- `SourceConditionedSpeakerVerifier`: decode WAV của mỗi speaker và audio cuối MP4 thành mono 16kHz PCM qua FFmpeg; tạo envelope RMS 20ms, so độ tương quan đúng cửa sổ phát ngôn, dò lệch giới hạn và đối chiếu với mẫu voice khác.
- Nhiều nguồn giọng cùng lúc bị chặn (`OVERLAPPING_SPEAKERS_UNATTRIBUTABLE`) vì không hỗ trợ blind diarization, tách overlap. Không tự tạo false pass nếu source tampered, thiếu audio, trùng line.
- **Đây là kiểm tra attribution khi CÓ mẫu WAV gốc (source-conditioned matching), KHÔNG phải speaker diarization độc lập**. Không chứng minh đúng timbre/diễn xuất hay nhân vật thể hiện đúng ngữ nghĩa câu.

Bằng chứng thật ở `data/verification/v186_real_speaker_face_multishot/v186_qualification_evidence.json`:
- A/David: tương quan **0.9766**, cạnh tranh 0.4564, margin 0.5202, lệch audio khoảng -0.02 giây.
- B/Zira: tương quan **0.9742**, cạnh tranh 0.4592, margin 0.5151, offset 0 giây.
- Negative: **cố ý remux đảo hai WAV** sang cửa sổ của người khác → `speaker_swap_negative.passed = false`.

### 1.2. Quan sát miệng từ hình ảnh, không đọc mesh miệng khi định vị

`cinefactory/studio/face_mouth_observability.py` có:
- `ActorFaceSearch`: actor ID và bounding box *của nhân vật*, có nguồn `RIG_ACTOR_BOX` hoặc `HUMAN_APPROVED_ACTOR_BOX`, cùng time window.
- `FacePatchMotionMouthDetector`: lấy fixed crop phần mặt trên của actor, xem biến thiên pixel grayscale theo chuỗi frame đã render, morphological cleaning và connected-component localization để tìm vùng thay đổi.
- Thuật toán **không nhập mouth projection, viseme keys hoặc tọa độ miệng** ở bước phát hiện. Nhưng **actor box vẫn do rig cung cấp**, cần scene tương đối ổn định, mặt hướng camera. Đây KHÔNG phải detector facial landmark tổng quát và không đảm bảo đối mặt với eye blink, lighting flicker, camera motion hoặc occlusion.
- Trên MP4 thật 640×360 có hai nhân vật: mouth candidate A pixel XYXY **(249,140,270,154)**, B **(370,143,391,154)**, mỗi người được đo 25 frame.
- Negative: đóng băng cùng một frame cho toàn bộ video → `frozen_face_negative.passed=false`.

`cinefactory/studio/mouth_image_rig_agreement.py` dùng **vị trí miệng vừa phát hiện từ pixel** để cross-check *sau đó* với union của Blender rig-mouth projection 41 samples từ v1.6.25:
- A IoU **0.631**, B IoU **0.671**, threshold 0.32, báo cáo `RIG_CONSTRAINED_IMAGE_LOCALIZATION_PASS`.
- Thử điều chỉnh giả tạo tọa độ candidate sang vị trí khác → **BLOCKED**.
- Đây không phải ground truth landmark độc lập từ người gán nhãn; `production_qualified=False`.

### 1.3. So định danh nhân vật qua hai lần render Blender thật

`cinefactory/studio/multishot_render_identity.py` có:
- `TwoShotImageIdentityVerifier`: đọc **hai MP4 render thực khác SHA-256**, có `.frame_qc.json` (RGB mean, HSV histogram, aHash64 và actor crop có nguồn rig) + `.geometry_qc.json` (ID rig có provenance).
- Score kết hợp Bhattacharyya histogram/độ chênh RGB/Hamming aHash, kiểm tra correct actor vượt threshold và có margin cách biệt với nhân vật khác. Bắt buộc hai video khác nhau và actor set/rig version nhất quán.
- Cảnh 1: `data/verification/v185_alignment_reid/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4`. Cảnh 2: `data/verification/v186_multishot_second/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4`; cảnh thứ hai render lại Blender với ambient/lighting intent mềm và golden khác, không phải copy file.
- Kết quả: A score **0.9921**, margin **0.1852**; B score **0.9952**, margin **0.1897**.
- Negative: cố ý đảo A/B ở hình học nhận diện của cảnh 2 → `relabel_negative.passed=false`.
- **Giới hạn:** crop/actor labels vẫn đến từ frame-QC Blender; chưa có independent full-video actor detection/re-ID across severe motion, changing outfits, cross-model generation, hoặc benchmark video Wan nhiều seed.

## 2. Tích hợp công ty và production gate

- `cinefactory/appctx.py` và `cinefactory/studio/professional_company.py` có `speaker_stem_qc`, `image_mouth_observability`, `mouth_rig_crosscheck`, `multishot_render_identity` dùng chung object thực trong corporate context.
- `cinefactory/studio/audio_visual_sync_qc.py`: `PerformanceQualificationGate.assess(v186_required=True,...)` giờ yêu cầu cả 4 loại evidence mới và phải giữ fail-closed nếu thiếu independent diarization, independent face landmarks, actual unconstrained multishot identity.
- Không mở Wan semantic performance gate, không thay đổi workflow không yêu cầu lip-sync, không deploy, không Git commit, không reset working tree.

### Những việc chưa đạt trước khi có quyền sản xuất hàng loạt

1. Independent speaker diarization trên audio không có WAV nguồn, support overlap/interruptions; audio-word-phoneme forced alignment độc lập với TTS.
2. Generalized face detector + stable 2D landmarks hoặc 3D calibrated face/mouth under camera motion, occlusion và nhiều style (Minecraft/Roblox).
3. Shot-to-shot actor grounding không nhờ metadata/crop rig; human-labeled reference, số liệu confusion/switches/cross-shot re-ID trên thật nhiều scene và seed Wan.
4. Viseme-to-phoneme accuracy đánh giá theo video/audio actual với false-accept test; review performance từ chuyên gia và benchmark thẩm mỹ.
5. 4K/video dài 8+ phút, audio/stem licenses, công suất RTX3060, đo GPU time, revision cost và kinh tế sản xuất.

## 3. Artifacts và lệnh chạy lại

- `scripts/verify_multishot_real_v186.py` — second Blender render (thay đổi ánh sáng và giữ asset identity).
- `scripts/verify_speaker_face_multishot_v186.py` — WAV-vs-final MP4, image localization, crosscheck, two-shot identity và 3 negative videos.
- `tests/test_speaker_face_multishot_v186.py` — negative và regression tests, cùng chuỗi test v1.6.23–25.
- `data/verification/v186_real_speaker_face_multishot/v186_qualification_evidence.json` — full, machine-readable evidence có hashes/statuses/scores/blockers.
- `data/verification/v186_real_speaker_face_multishot/NEGATIVE_swapped_voices.mp4` — video negative hoán đổi thoại.
- `data/verification/v186_real_speaker_face_multishot/NEGATIVE_frozen_mouth.mp4` — video negative cố tình frozen image.
- `data/verification/v186_multishot_second/two_actors_speech_audible.mp4` — video clip thứ hai H.264/AAC với ánh sáng thay đổi.

```powershell
python scripts/verify_multishot_real_v186.py
python scripts/verify_speaker_face_multishot_v186.py
python -m pytest -q tests/test_speaker_face_multishot_v186.py
python -m compileall -q cinefactory scripts tests
python -m pytest -q
```

**Milestone tiếp theo:** v1.6.27 — Real video semantic face tracking + actor-independent identity benchmark + independent speech audio alignment & hard release-quality acceptance, không tự phong production qualified.


## 4. Final regression / checkpoint

- `python -m compileall -q cinefactory scripts tests`: **PASS**.
- `git diff --check -- cinefactory/appctx.py scripts/blender_animation_worker.py`: **PASS**, Windows LF/CRLF informational warnings only.
- v1.6.23–v1.6.26 targeted integration `tests/test_speaker_face_multishot_v186.py tests/test_alignment_mouth_multiseed_v185.py tests/test_real_speech_independent_v184.py tests/test_temporal_lipsync_v183.py`: **64 PASS**.
- **FULL repository `python -m pytest -q`: 664 PASS, 0 FAIL, 197.08 seconds, exit code 0.**
- Log được lưu tại `data/verification/v186_real_speaker_face_multishot/regression_v186.txt`.
- Qualification evidence: `v186_qualification_evidence.json` → `REAL_DIAGNOSTICS_AND_NEGATIVE_CONTROLS_PASS_PRODUCTION_BLOCKED`. Global production gate `BLOCKED`, đúng chủ đích.
- Branch vẫn `studio/v1.6.6-universal-company`, HEAD `44e1f5f`; không stage/commit/deploy/reset, giữ các thay đổi trước đó.

**Mốc v1.6.26:** code & regression hoàn tất; benchmark thực có kiểm soát đạt, negative controls bảo vệ đúng. **Không** cấp phép tự động production release cho dialogue cinematic / Wan / 4K.


## 4. Final regression / checkpoint

- `python -m compileall -q cinefactory scripts tests`: **PASS**.
- `git diff --check` on tracked changes: **PASS**. Windows LF/CRLF warnings are informational.
- Targeted integration v1.6.23 through v1.6.26: **64 passed**.
- **FULL repository pytest: 664 passed, 0 failed, 197.08 seconds**, exit code 0.
- Regression log: `data/verification/v186_real_speaker_face_multishot/regression_v186.txt`.
- Final evidence `v186_qualification_evidence.json`: `REAL_DIAGNOSTICS_AND_NEGATIVE_CONTROLS_PASS_PRODUCTION_BLOCKED`.
- No stage, commit, deploy or Git reset. Production qualification remains BLOCKED for unsatisfied independent/real-world QC criteria.

**Milestone:** v1.6.26 implemented and verified at diagnostic level, not approved as general production automation.
