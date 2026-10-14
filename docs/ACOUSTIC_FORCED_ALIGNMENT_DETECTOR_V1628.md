# CineFactory OS v1.6.28 — Acoustic Phoneme Alignment + Visual Lip-Sync Check + Detector Candidate

**Date:** 09 Oct 2026
**Milestone:** Completed technical code and real-media qualification probes.
**Production status:** BLOCKED. Real acoustic phoneme timing successful, but neither true linguistic/phoneme content nor mouth shape is independently ground-truth certified. First YOLO in-domain model fails held-out detector QC.

## 1. Real local phoneme forced alignment (new)

- PocketSphinx **5.1.1** Windows wheel is stored at `.tools/wheels/pocketsphinx-5.1.1-cp311-cp311-win_amd64.whl` and unpacked to `.tools/pocketsphinx_lib`; no cloud API payments or dependency install into global Python. Local English trained HMM and dictionary bundled.
- `cinefactory/studio/acoustic_forced_alignment.py`: `PocketSphinxAcousticAligner.align` decodes **actual** WAV/AAC audio with FFmpeg 16 kHz mono PCM, verifies SHA256, validates dictionary, uses a **two-pass** HMM alignment (word alignment then `set_alignment()` for phoneme time starts/durations).
- It reports `AcousticWord` / `AcousticPhone` with an audio-measured start/end per phoneme, and checks sample duration, sequencing and gross speech energy. `transcript_conditioned=true`, `phone_labels_from_lexicon=true`; phoneme names are pronunciations of the PROVIDED text, not independent phoneme classification.
- Real samples from Windows voices on both WAV sources and decoded **final H.264/AAC MP4**:
  - Actor A `Hello!`: HH 0.10–0.15s, EH 0.15–0.20s, L 0.20–0.35s, OW 0.35–0.52s.
  - Actor B `Let's go!`: L 0.09–0.17s, EH 0.17–0.24s, T 0.24–0.30s, S 0.30–0.35s, G 0.35–0.44s, OW 0.44–0.62s.
  - Between PocketSphinx real-audio onset estimates and SAPI `SpeakProgress` independent metadata: A -0.0371s; B -0.0471s and -0.1453s. The system stores both clocks; no claim of certified ground-truth accuracy.
- `cinefactory/studio/phoneme_video_proxy_qc.py`: maps an open/closed mouth PROXY based on predetermined ARPAbet vowel/plosive groups; compares **independently audio-aligned** phone timings to actual pixel-luminance/darkness measured by `RenderedMouthProjectionQC` on FINAL MP4 at the pre-declared fixed **zero-lag** offset. No fitting offsets or smoothing to inflate score.
  - A pixel/phone proxy correlation **0.8680**, B **0.7949** (threshold .55).
  - Negative deliberately shift audio timing **350ms**: QC **BLOCKED**.
- Negative silent WAV and dictionary OOV word: **BLOCKED**.
- Safety-critical false-accept: PocketSphinx's lexicon-conditioned forced aligner can output a plausible alignment for **'go' even when the audio says 'Hello!'**. This is a known limitation of forced alignment, not a bug to conceal. Production gate demands an **additional independent ASR text check** for source AND final MP4, in addition to acoustic timings and visual metrics.
- From v1.6.27 independent ASR: A passes, B **low confidence**; therefore source and final spoken-text approval both blocked, even though B's forced phone times and visual timing proxy pass.
- `production_qualified=false`; `independent_phoneme_recognition_verified=false`; `visual_phoneme_sync_verified=false` in all acoustic reports. No human-labelled phoneme/viseme QA.

## 2. True neural pixel actor detector trial and held-out validation (new)

- The stock **Ultralytics YOLO11n** person detector (COCO weights, `.tools/models/yolo11n_coco.pt`) was run on actual Minecraft Blender 640×360 frames. It detects chairs/bench/TV but **fails to recognize the block actors as person**: `coco_person_recall=0.0`. No false promotion.
- `scripts/train_block_actor_detector_v188.py`: creates labelled frames from only **first REAL Blender render**, with rig-labelled boxes to train `block_actor` (class 0).
- **56 frames from reference only:** 44 train + 12 in-source validation, 10 CPU epochs, `imgsz=320`. Uses first render as training and second *distinct* render as sealed held-out evaluation. No second-shot labels or pixels used in training, but both shots have the same rigs/scene and mostly similar appearance. This is **not a generalization benchmark**.
- Training metadata `data/verification/v188_acoustic_detector/training_manifest_v188.json`, model `data/verification/v188_acoustic_detector/train_runs/block_actor_v188/weights/best.pt`; weights SHA256 saved.
- `cinefactory/studio/trained_actor_detector_qc.py`: separate `HeldoutActorDetectorEvaluator` feeds the full raw second-render pixel frame into model (NO coordinates), then compares predictions against held-out rig boxes **after inference** with IoU threshold .50, precision/recall floors .85/.85.
- Actual held-out measurements at operational confidence .20: **precision=0.0, recall=0.0**; trained candidate **BLOCKED**. This does not mean the model cannot fit the source training scene: its in-source validation mAP varied, and inference on second scene at very low confidence .001 showed ~108 weak overlapping candidates with maximum confidences about **.019**, not valid detections.
- Lowering confidence to artificially obtain any candidate would create many false positives, so operational QC floors and no-promotion policy were **not changed**.
- CPU-only PyTorch on current Windows interpreter (`torch.cuda.is_available() == false`); Blender may separately use GPU for rendering. RTX3060 alone doesn't imply all Python frameworks have CUDA enabled.
- **Licensing:** Ultralytics/model weights can carry AGPL and/or separate commercial licensing requirements. Do not ship a paid commercial product using these assets without review. Likewise review PocketSphinx/CMU model and dictionary notices for redistribution/commercial use.

## 3. Integration and release policies

- `cinefactory/appctx.py` and `cinefactory/studio/professional_company.py` register three services: `acoustic_forced_alignment`, `phoneme_video_proxy_qc`, `trained_actor_detector_qc`.
- `cinefactory/studio/audio_visual_sync_qc.py`: new opt-in `PerformanceQualificationGate.assess(v188_required=True,...)` consumes:
  - real acoustic timing reports (both actors),
  - video pixel vs ARPAbet proxy checks,
  - on-device trained detector held-out report,
  - independent content ASR results of source speech AND final mux.
- Gate never promotes lexicon-generated labels to independent phoneme verification, heuristic pixel proxy to human-approved viseme shapes, or same-rig Blender held-out test to generalized real-world identity.
- Existing short/vlog/non-dialogue lanes unchanged and not newly gated by default. `v188_required=True` is explicit.
- No production release, no Git reset, no indiscriminate commit, no deployment.

## 4. Evidence, commands and next stage

- `scripts/verify_acoustic_detector_v188.py` — real decoded source/MP4 two-pass HMM, video lip proxy, wrong-text/silence/shift controls, YOLO COCO baseline and trained model heldout, release gate.
- `data/verification/v188_acoustic_detector/v188_qualification_evidence.json` — machine-readable all metrics and outcomes (expected status: `REAL_ACOUSTIC_ALIGNMENT_PASS_DETECTOR_DOMAIN_BENCHMARK_BLOCKED_PRODUCTION_BLOCKED`).
- `tests/test_acoustic_detector_v188.py` — comprehensive new tests, both positives and negatives.
- `scripts/train_block_actor_detector_v188.py` — repeatable local 10-epoch training with SHA-proof training vs heldout.
- `data/verification/v188_acoustic_detector/NEGATIVE_SILENCE.wav` and `A_FINAL_MUX_AUDIO.wav`, `B_FINAL_MUX_AUDIO.wav`.

```powershell
python scripts/train_block_actor_detector_v188.py
python scripts/verify_acoustic_detector_v188.py
python -m pytest -q tests/test_acoustic_detector_v188.py
python -m compileall -q cinefactory scripts tests
python -m pytest -q
```

### Next stage

**v1.6.29** should focus on **diverse Blender scene generation, actor mask/depth/ID passes for accurate training labels, real multiple-rig/color/camera/lighting held-out split, detector calibration and independent human-labelled results**. Do not simply add epochs against the same two nearly identical shots and call it generalization. For dialogue, obtain genuine independent ASR+phoneme-content verification on longer/real speech, and human or geometric landmark ground truth to verify viseme shape and latency.

**Status:** acoustic forced phone *timing* works at local preview level, but source/MP4 ASR for B and generic actor detector remain blocked. Not Disney-level certified production.


## 5. Final test closure / source integrity

- Integrated v1.6.23–v1.6.28 relevant tests: **106/106 PASS**.
- Complete repository test command `python -m pytest -q`: **706 passed, 0 failed, 247.30 seconds (4m07s)**; exit code 0.
- `python -m compileall -q cinefactory scripts tests` **PASS**; `git diff --check` on tracked source changes **PASS**, Windows LF/CRLF warnings only.
- Regression evidence: `data/verification/v188_acoustic_detector/regression_v188.txt`.
- Production release remains `BLOCKED`, including actual source/final speaker B ASR confidence, lack of independently recognized phone content and human-labeled viseme accuracy, and failed YOLO block actor detector.
- New code is persisted on the local Windows machine. No git reset / stage / commit / deployment.
