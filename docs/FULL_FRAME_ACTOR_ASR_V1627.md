# CineFactory v1.6.27 — Full-frame Reference Actor Tracking + Offline Independent ASR on Final Media

**Date:** 2026-10-09
**Status:** V1.6.27 implemented and controlled diagnostic evidence collected. **Production qualification: BLOCKED**; A speech recognition PASS / B low-confidence BLOCKED.

## Engineering additions

1. `cinefactory/studio/full_frame_actor_search.py`: `FullFrameReferenceActorScanner` trains an image template from an annotated reference shot, then scans the **entire target video frame** for each actor without using target screen coordinates. It measures first- and second-best template similarity, vetoes duplicate/lookalike candidates, constructs unseeded target detection boxes, and runs `TemporalReIDEngine` on sampled frames. Origin `DetectionOrigin.INDEPENDENT` means independent of prior **target location**, not independent of reference identity; **not a general-purpose actor detector**. Training still requires rig-annotated reference crops.
2. `FullFrameReferenceActorScanner.evaluate_rig_ground_truth` is a **post-detection-only** evaluation against Blender rig boxes for the target shot; annotations are never passed into the scanner. No human-labeled frames, varying poses/camera, or Wan multi-seed qualification.
3. `scripts/windows_asr_independent.ps1` uses Windows `System.Speech.Recognition.SpeechRecognitionEngine` with **DictationGrammar** (not the expected script text). Independent text output has recognized words and confidence, source SHA256, no word timestamps. This recognizer is distinct from the SAPI TTS `VisemeReached` events, but both belong to Windows speech tech.
4. `cinefactory/studio/independent_speech_asr.py`: `OfflineIndependentASR` checks WAV hashes, transcript normalization and confidence; refuses to treat low-confidence matches as accurate. No source transcript is passed to the recognizer. `phoneme_alignment_verified`, `independently_forced_aligned` and `production_qualified` remain **False**.
5. `scripts/verify_real_actor_asr_v187.py` builds actual evidence on Blender shot A (v1.6.25) and lighting-varied shot B (v1.6.26), creates a clean *target MP4 copy without annotation files*, generates a visual lookalike-impostor negative MP4, independently recognizes original TTS WAVs **and final muxed MP4 speech windows**, checks wrong-text audio and swapped-voice final-video negative, runs v1.6.27 production QC gate.
6. `cinefactory/appctx.py` and `cinefactory/studio/professional_company.py` now expose `full_frame_reference_actor` and `offline_independent_asr` as shared company services.
7. `cinefactory/studio/audio_visual_sync_qc.py` optionally consumes `v187_required=True`, scan, rig benchmark, independent source-WAV ASR and final-mux ASR reports. Even if image matching passes, it cannot qualify production without unconstrained detection, independently human-annotated evaluation, high-confidence audio, and forced phoneme-aligned evidence.

## Actual two-shot rendered-video evidence

Inputs:
- Reference: `data/verification/v185_alignment_reid/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4`.
- Second actual Blender render: `data/verification/v186_multishot_second/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4`. Different SHA256, lighting variant, same two rigs.
- Copy without target sidecars: `data/verification/v187_unseeded_video_asr/target_without_sidecars.mp4`.

Measured:
- Full-frame actor search matched actor A and B across **12/12 sampled frames** (24/24 actor detections), with independent **target frame search location** and confidence-vs-alternate-candidate checks.
- Evaluated **only after detection** using Blender rig ground-truth boxes: mean IoU **0.98407083**, minimum IoU **0.98146735**. This rig-generated ground truth is not independent human annotation.
- Detector also succeeded on a byte-identical target video **with no target geometry/frame-QC JSON sidecars at all**; verifying actual implementation cannot secretly read target boxes.
- Negative `NEGATIVE_second_actor_lookalike.mp4`: inserting an exact visual duplicate of actor A elsewhere in target frame causes `TWO_SIMILAR_SCREEN_ACTOR_CANDIDATES`, **BLOCKED**.

## Independent offline dictation evidence

Installed Microsoft SpeechRecognitionEngine en-US system recognizer available, no paid API/model download.
- Original WAV A: recognized `Hello`, confidence **0.7589** — PASS at threshold 0.55.
- Original WAV B: recognized `Let's go`, confidence **0.1109** — BLOCKED for low confidence.
- Independently decoded speaker audio from **final H.264/AAC MP4**:
  - A: `Hello`, confidence **0.7896** — PASS.
  - B: `Let's go`, confidence **0.3635** — BLOCKED for low confidence.
- Negative: same `Hello` WAV with entirely wrong expected transcript — **BLOCKED**, mismatch.
- Negative: **real final MP4 with speaker WAVs swapped in time windows** from v1.6.26, both A/B recognitions not accepted — **BLOCKED**.
- Neither Windows RecognizedWordUnit nor this script supplies per-word onset timing; **no independent phoneme forced alignment**. No source audio/word timestamps are passed into ASR. Transcript is used ONLY after recognition for scoring.

## Evidence & reproducibility

`data/verification/v187_unseeded_video_asr/v187_qualification_evidence.json` is the complete JSON evidence. Videos and WAVs from negative controls in the same folder. Independent ASR JSON sidecars contain WAV hash/provenance and scores.

```powershell
python scripts/verify_real_actor_asr_v187.py
python -m pytest -q tests/test_fullframe_asr_v187.py
python -m compileall -q cinefactory scripts tests
python -m pytest -q
```

## Blockers to production release

- Reference templates must come from an annotated first shot and do not generalize to unseen actors, outfits, camera move, pose, occlusion, complex lighting or arbitrary rendered/Wan footage. A *true* unconditioned detector and independent ground truth still required.
- Only a **12-frame sampling of one controlled target render** has target-location-independence evidence; not a long-form temporal or multi-seed benchmark.
- Windows offline recognizer's confidence can be very low for short phrases; B legitimately fails. Future work: freely licensed local ASR+CTC/forced aligner, calibration, phoneme and independent source/voice attribution over mixed conversations.
- Must independently verify speech timing/phoneme visemes from final video with source transcript, speaker diarization, mouth landmarks/visibility, and audio latency measurement.
- Need 4K/long-form, crowd, camera cuts, performance quality human review, rights/license clearance, GPU efficiency and real release-grade tests. A code pass does not equal artistic/Disney-standard video.

No Git reset, no commit, no deployment, no production gate bypass.


## Final verification / release decision

- Targeted integration across v1.6.23–v1.6.27: **85/85 PASS**.
- Full repository `python -m pytest -q`: **685 passed, 0 failed, 214.23 seconds**, process exit code 0.
- `python -m compileall -q cinefactory scripts tests` → **PASS**.
- `git diff --check` on tracked code → **PASS**. Git displayed Windows newline conversion warnings only (LF / CRLF), not whitespace errors.
- Regression log: `data/verification/v187_unseeded_video_asr/regression_v187.txt`.
- Evidence: `data/verification/v187_unseeded_video_asr/v187_qualification_evidence.json`.
- Qualified diagnostic observations: target-sidecar-free full-frame video search **PASS**; 24 detections over 12 frames; rig-box evaluation mean IoU 0.984; visual lookalike and swapped dialogue negative controls **BLOCKED**; independent ASR A PASS but B **LOW CONFIDENCE BLOCKED** on both source WAV and final mux.
- Full automated cinematic/lip-sync/real-Wan production approval: **BLOCKED**. No unauthorized Git reset/commit or deployment.
