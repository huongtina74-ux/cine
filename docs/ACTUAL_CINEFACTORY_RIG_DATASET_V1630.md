# CineFactory OS v1.6.30 — Actual Worker Rig Training + Real Occlusion & Cross-Domain Gate

**Checkpoint date:** 2026-10-09. **Code implemented directly on connected Windows machine.**
**Production release: BLOCKED.** No reset, commit, deploy, or automatic replacement of the existing detector.

## Why v1.6.29 was insufficient

V1.6.29 had **100% precision and recall on its own procedural voxel generator's 32 test scenes** while detecting **0% of characters in an existing CineFactory v186 real Blender classroom video**. The v186 scene contains seated characters, desk/chair occlusion, complex room assets, low-key light and project-specific Minecraft rigs. The v189 synthetic generator portrayed mainly unobstructed standing figures. Improving synthetic results on the same visual domain is not evidence of real production generalization.

## v1.6.30 actual code changes

1. `scripts/blender_actual_rig_dataset_v190.py`: loads the actual existing `scripts/blender_animation_worker.py` definitions (without running its stdin service), takes real `config/block_animation/characters.yaml` and `scenes.yaml` as a SHA256-stamped JSON snapshot and calls the **existing CineFactory rig and room constructors**, including `proc_minecraft_actor`, `proc_roblox_r6_actor` and `proc_room`. The builder is non-destructive: it does not patch the worker, registries, or engine rendering pipelines.
2. Builds a mixed dataset with original MC/R6 character appearance and real CineFactory classroom geometry. 2–3 characters, seated/standing limb postures, desks/chairs, background shelves/windows, camera azimuth/elevation and dark/medium/bright diagnostic illumination. Real Blender 4.5 Workbench frames at **384×256** with visible-per-character masks obtained by rendering exact production-worker actor mesh members white and all other meshes black, preserving actual occlusion by geometry.
3. Independently grounded labels are generated only **after** Blender renders by the existing `BlenderVisibleMaskDatasetAssembler`. No fixed bounding-box projection feeds inference. Per-sample raw RGB/mask hashes, worker source hash, rig IDs, postures, split/seed/camera/lighting, and test label lineage are recorded.
4. **114 distinct actual-worker scenes**, **286 actor instances** and **0 mask-overlap pixels** passed the dataset QC. Strict train/val/test **72 / 18 / 24** scenes. Training includes Minecraft and Roblox R6 and seated characters; test has new deterministic camera/seeds, with a heavier seated proportion. Separate, stronger **external v186 CineFactory video** was not involved in training, validation or threshold selection.
5. `scripts/train_real_rig_detector_v190.py`: 14 local **CPU** fine-tuning epochs (Torch on this Windows interpreter is CPU only), from isolated v189 YOLO checkpoint, on actual factory rigs; no premium API. The new checkpoint and initial weights have immutable hashes in `training_manifest_v190.json`. Both split test and external video are **excluded** from training/calibration.
6. `cinefactory/studio/real_rig_domain_qc.py`: additional production-domain admission layer: local split pixel-mask QC, held-out Minecraft/R6 bounding-box precision/recall, **external v186 scene**, improvement versus the v189 model **on the exact same video**. External-video acceptance floors are predeclared precision/recall 0.60/0.60 with absolute recall improvement ≥0.10. All model decisions are based on evidence, never on an expected “success.”
7. `scripts/verify_real_rig_detector_v190.py`: reads and SHA-protects training dataset/worker source/snapshot, selects confidence with **validation only** then computes test-set metrics. It then evaluates the chosen checkpoint against v186 and measures the v189 baseline on the same v186 clip, while preserving authentic negative results. Writes full `v190_qualification_evidence.json`.
8. `cinefactory/appctx.py`, `cinefactory/studio/professional_company.py`: shares a new `real_rig_domain_qc` service. `PerformanceQualificationGate.assess(v190_required=True,...)` refuses release without external proof, multiproject diversity, independently human-reviewed GT and commercial licensing clearance.
9. `tests/test_real_rig_dataset_v190.py`: checks real CineFactory rig/scene/config SHA provenance, seeded pose/camera split isolation, visible mask bounding coordinates, invalid masks/tampered labels/colliding seeds, external test lineage, baseline and immutable release gate.

## Reproducibility / main evidence files

All relative to CineFactory repo root:
- `data/verification/v190_real_rig_dataset/rig_snapshot_v190.json` — real rig/scene configuration snapshot and SHA.
- `data/verification/v190_real_rig_dataset/raw/render_index.json` — 114 Blender source image/mask paths, rig IDs, camera and postures.
- `data/verification/v190_real_rig_dataset/mask_dataset_qc.json` — 286 actor-mask QC measurements.
- `data/verification/v190_real_rig_dataset/dataset/data.yaml` — YOLO train/val/test layout.
- `data/verification/v190_real_rig_dataset/model_runs/v190_actual_worker_rigs/weights/best.pt` — candidate weights, **not promoted**.
- `data/verification/v190_real_rig_dataset/training_manifest_v190.json` — input/output hashes and split protection.
- `data/verification/v190_real_rig_dataset/v190_qualification_evidence.json` — independent target benchmark and admission status.
- `data/verification/v190_real_rig_dataset/regression_v190.txt` — final full regression log.
- `data/verification/v190_render_log.txt`, `data/verification/v190_train_console.log` — process logs.

```powershell
# Existing snapshots are already produced; no need to regenerate unless rebuilding.
python scripts/train_real_rig_detector_v190.py
python scripts/verify_real_rig_detector_v190.py
python -m pytest -q tests/test_real_rig_dataset_v190.py
python -m pytest -q
```

## Truthfulness & release limits

* The **geometry and rigs** are from the genuine CineFactory worker, but **image output is still Workbench diagnostic quality**; not the same rendering profile as the v186 Eevee scene. Success in the Workbench dataset does not guarantee Eevee output generalization.
* Source mask labels are *deterministically rendered* actor visibility and work well for training detection; they are **not independent human-verified semantic ground truth**.
* The v186 existing-video QC compares against **Blender rig-sidecar bboxes after inference**. It does not have human segmentation ground truth and tests only one scene, not multi-project shooting.
* Model class is one generic `voxel_actor`; this is NOT actor re-identification (A vs B), face landmark validation, full lip-sync or audio speaker attribution.
* YOLO/Ultralytics AGPL/commercial terms require validation and rights clearance for any business deployment. No automatic certification.
* The original git branch/worktree is preserved, with no deploy or unapproved overwrite.

### Next if cross-domain detector remains insufficient

Expand the *same existing worker's* scene randomization into camera changes and seat/table occlusion nearer to v186, real Eevee render domain, mix multiple scene projects with project-group splits, annotate independent production frames by a reviewer and use human-verified negative hard examples. Never calibrate on the protected held-out v186 clip after reporting it as a test.


## Verified actual results (2026-10-09)

- Full actual-CineFactory-workbench rig dataset: **114 new Blender scenes; 286 independently rendered visible actor masks** (0 mask-overlap pixels), QA PASS. Scenes grouped 72 train, 18 val and 24 test; Minecraft and Roblox R6 real factory rigs, seated/standing posture, existing classroom assets, camera/lighting variation. The source worker and registry files have SHA256 provenance; the source worker was not modified.
- **14 CPU training epochs** from v189 baseline, resulting new weights `data/verification/v190_real_rig_dataset/model_runs/v190_actual_worker_rigs/weights/best.pt`; training excludes heldout test and original external video v186 entirely.
- Confidence threshold fixed at **0.50**, selected by validation before exposing the model to test or external video.
- **24 new held-out actual-worker Workbench scenes:** precision **1.000**, recall **1.000** (IoU ≥0.50). This is an *internal shared-constructor synthetic domain*, not certified independent artistic quality.
- **Original v186 actual CineFactory class-room H.264 MP4**: **12 sampled frames; 2 actors/frame**, from existing Blender Eevee pipeline. YOLO v190 **precision 1.000, recall 1.000** under same preselected 0.50 confidence and 0.50 IoU. Previous v189 model on the EXACT same v186 video: **recall 0.000**. V190 diagnostic admission **PASS** on these predeclared criteria; no model training/tuning was done on v186.
- **Original v186 independent image evidence:** `data/verification/v190_real_rig_dataset/v190_external_v186_actual_predictions.jpg` compares 4 actual MP4 decoded frames, with original rig-bbox ground truth (yellow) and model-predicted actor boxes (cyan). The model receives pixel RGB alone, not rig ground truth; sidecar used only after predictions.
- **Production gate still BLOCKED**, because human-grounded labels, multiproject/long-form generalized character tracking, commercial license review and multi-style independent verification were not completed.
- Technical evidence: `data/verification/v190_real_rig_dataset/v190_qualification_evidence.json`, status `ACTUAL_WORKER_RIG_DATASET_PASS_SYNTHETIC_HELDOUT_PASS_EXTERNAL_VIDEO_PASS_PRODUCTION_BLOCKED`.
- Real source mask review: `data/verification/v190_real_rig_dataset/actual_worker_rig_mask_contact_sheet_v190.jpg`. This is not independently human-approved ground truth.


## Final verification / source integrity checkpoint

- **Targeted v1.6.26–v1.6.30 tests: 100 PASS.**
- **Whole repository: 744 passed, 0 failed, 172.87 seconds (2m52s)**, command `python -m pytest -q` exit code 0.
- `python -m compileall -q cinefactory scripts tests` PASS.
- `git diff --check` tracked source PASS; Git LF/CRLF warnings only.
- Complete log: `data/verification/v190_real_rig_dataset/regression_v190.txt`.
- Candidate model baseline vs external actual v186 Blender video: old v189 **recall 0.000**; new v190 **precision 1.000 / recall 1.000** across **12 sampled frames, 24 actor boxes**, unchanged threshold 0.50.
- Visual proof: `data/verification/v190_real_rig_dataset/v190_external_v186_actual_predictions.jpg` uses YOLO predictions from video pixels (no GT fed to model), with post-facto Blender rig box overlay.
- **V190 diagnostic domain gate PASS, production release gate BLOCKED.** Outstanding independent human labels, multiple held-out projects, commercial model license, general moving cameras/occlusion/re-ID, long-form 4K production quality.
- Working tree was kept intact, no Git reset/staging/commit, no production deployment or replacement.
