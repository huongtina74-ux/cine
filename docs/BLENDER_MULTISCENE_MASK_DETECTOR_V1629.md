# CineFactory OS v1.6.29 — Real Blender Voxel Dataset Factory + Pixel Masks + Held-Out Detection QC

**Date:** 2026-10-09  
**Purpose:** Replace a single-shot YOLO training prototype with a reproducible factory generating *actual Blender renders*, visible actor masks, and honest scene-level held-out benchmarking.  
**Production qualification:** **BLOCKED** until independent production-grade validation and licensing. A synthetic-test PASS does not authorize general-purpose detection.

## Implemented system

### 1. Blender scene dataset factory

`scripts/blender_voxel_dataset_v189.py` runs Blender 4.5 headlessly. A seeded procedural Workbench scene synthesizes:
- Minecraft-inspired box/voxel characters with torso, square heads, limbs, skin, black eyes, mouth, and optional hair/belts;
- 2–3 actors, different heights and body/clothing palettes, slight limb poses, positions/depths;
- floor/back wall/props, different environment color families and front/oblique camera angles;
- a full-color diagnostic Blender RGB image and a separately rendered **visible flat white mask** for each actor, while other actors/background props are black/occlude the subject;
- all camera, seed, split, actor-part IDs and per-mask file paths in `raw/render_index.json`.

These are real Blender raster renders, not photo backgrounds with boxes painted by OpenCV. But they are deliberately *small 384x256 engineering frames* from a procedural voxel art generator; they are NOT production Minecraft skins, Roblox R6 rigs, photorealistic or Disney-level animation.

### 2. Pixel-mask to YOLO dataset QC

`cinefactory/studio/blender_mask_dataset_qc.py`:
- reads real RGB and independent mask PNGs, derives actor bounding boxes from the visible white pixels **after occlusion**;
- rejects missing image/mask, small actor, invalid image bounds, overlapped actor masks, duplicate RGB hashes, duplicate scene/seed identities, or invalid label provenance;
- separates train/val/test into different deterministic seeds and scene IDs;
- validates all images and label fingerprints before detector inference (including post-QC tampering);
- writes per-sample evidence and `dataset/data.yaml` in YOLO format.

Observed from full collection: **152 scenes** (96 train / 24 validation / 32 test); **382 separately masked actor instances**; **no overlapping actor-mask pixels**; dataset and label audit **PASS**. Seed and family conditions are distinct; all splits nevertheless come from *one procedural generator*.

### 3. Training and model selection

`scripts/train_multiscene_detector_v189.py`: starts with `.tools/models/yolo11n_coco.pt` and trains a single-class `voxel_actor` detector using ONLY train and validation sets, 16 epochs, `imgsz=384`, batch 16, CPU (the Python Torch interpreter does not have CUDA); stores `model_runs/v189_multiscene/weights/best.pt` and SHA256 manifest.

`cinefactory/studio/multiscene_detector_qc.py`: model gets only test pixels at inference. Truth labels from independent Blender actor masks are read AFTER detection. Selects threshold using **validation only** over fixed confidences 0.10, 0.20, 0.30, 0.40, 0.50, maximizes F1 subject to validation precision floor 0.80, then measures holdout test once at the chosen threshold with detection IoU >=0.50 and precision/recall floors 0.80 each.

`scripts/verify_multiscene_detector_v189.py`: seals model, training manifest, dataset integrity, computes held-out 32-scene benchmark, *also tests on the prior actual CineFactory Blender speaking scene* (v186) and compares with v188 failed detector. A successful held-out procedural scene test cannot qualify the model to recognize arbitrary Minecraft/Roblox actors, Wan/ComfyUI output, or an 8+ minute video.

### 4. Negative controls and company integration

`tests/test_blender_multiscene_v189.py` tests intentionally poisoned YOLO labels, altered RGB bytes, reused seed, overlapping/duplicated masks, forbidden evaluation on training split, missing human-review records, and insufficient real-world generalization evidence.

`scripts/make_voxel_dataset_contact_sheet_v189.py` produces `voxel_dataset_preview_v189.jpg` with 12 examples across train/validation/test for visual inspection; the automatically built contact sheet is **not a human-approved baseline**.

`cinefactory/appctx.py` and `cinefactory/studio/professional_company.py` expose the two new service instances: `blender_mask_dataset_qc` and `multiscene_detector_qc`.

`PerformanceQualificationGate.assess(v189_required=True,...)` explicitly demands valid pixel masks, heldout detector QC, independently grounded real domain generalization, and **independent human actor label review**. Such approval has not been supplied; status remains **BLOCKED** by design.

## Important engineering limits / safety

1. Held-out scenes are *different random configurations and color/lighting/prop/camera family*, but share procedural geometry/renderer. Synthetic performance is not validated real-world performance; masks are engine-generated, not human-labelled.
2. Actor-instance class is generic `voxel_actor`. Class detection does **not** independently re-identify which actor is A or B or certify story continuity.
3. No semantic segmentation network was trained: segmentation masks exist as GT labelling source for detection. Do not call YOLO output a pixel segmentation mask.
4. Strict intellectual-property/licensing review needed for Ultralytics model weights/AGPL and production use. Avoid copying branded Minecraft/Roblox textures and assets without rights clearance.
5. Python torch CPU-only, Blender Workbench diagnostic renders low-res; 4K/persistent worker speed and actual full-length episode pipeline are separate qualifications.
6. Existing dirty branch is preserved: **no Git reset, broad commit, deployment, or replacement of current production model**.

## File paths / replay

Root: `C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6`

- `data/verification/v189_scene_diversity/raw/render_index.json` — 152 scenes and actor masks.
- `data/verification/v189_scene_diversity/mask_dataset_qc.json` — per-scene hashes, boxes, overlap metrics, splitting.
- `data/verification/v189_scene_diversity/dataset/data.yaml` — actual dataset.
- `data/verification/v189_scene_diversity/voxel_dataset_preview_v189.jpg` — contact sheet.
- `data/verification/v189_scene_diversity/model_runs/v189_multiscene/weights/best.pt` — candidate checkpoint only.
- `data/verification/v189_scene_diversity/training_manifest_v189.json` — model lineage.
- `data/verification/v189_scene_diversity/v189_qualification_evidence.json` — all held-out measurements and release gate.
- `data/verification/v189_scene_diversity/regression_v189.txt` — full unit/integration regression.

```powershell
& .tools/blender-4.5.14-windows-x64/blender.exe -b -t 4 --python scripts/blender_voxel_dataset_v189.py -- --output data/verification/v189_scene_diversity --train 96 --val 24 --test 32
python scripts/train_multiscene_detector_v189.py
python scripts/verify_multiscene_detector_v189.py
python -m pytest -q tests/test_blender_multiscene_v189.py
python -m pytest -q
```

## Next acceptance targets (v1.6.30)

Prove multi-rig/multi-engine generalization: create several **independently sourced production-style** character assets, camera/occlusion/background distributions and properly sealed scene/project-based splits; add human-reviewed mask/actor examples and real long-form production frames; measure precision/recall, occlusion/crowd identity switches and false accept on imitations. Consider a commercially appropriate model/license before deployment. Train only after mixed-domain benchmark and rights constraints are clear.


## Measured held-out results on actual Blender-generated frames

- **Actual Blender render count:** 152 unique scenes, 382 actor masks, no overlapping mask pixels. 96 TRAIN / 24 VAL / 32 TEST. Each scene is rendered separately by Blender Workbench at **384x256**.
- **Training:** 16 CPU epochs with YOLO11n COCO weights fine-tuned on 96 rendered scenes; checkpoint at `data/verification/v189_scene_diversity/model_runs/v189_multiscene/weights/best.pt` and SHA256 in training manifest.
- **Validation-only model threshold selection:** fixed confidences 0.10 / 0.20 / 0.30 / 0.40 / 0.50 all reached precision 1.0 and recall 1.0 on the 24 same-generator validation scenes. Highest predeclared tie-break selects **0.50**, without reading TEST labels.
- **32 unseen TEST scenes** from a different palette/environment/seed family but the **same procedural voxel generator**: precision **1.0**, recall **1.0**, F1 **1.0** at IoU >=.50, confidence .50.
- **External pipeline counterexample:** the previously rendered *real CineFactory Blender video* from v186, not generated by the new standalone synthetic generator: recall **0.0** at the same predeclared confidence. Prior v188 YOLO model on that video: recall **0.0**.
- **Interpretation:** model learned the generator's domain; it **has not generalized to existing CineFactory characters**, let alone Roblox, complex Minecraft assets or AI-generated scenes. The 100% held-out synthetic result must NOT be displayed as production detector performance.
- **Visual audit:** `voxel_dataset_preview_v189.jpg` shows representative multi-actor frames, and `heldout_detector_predictions_review_v189.jpg` compares **yellow rendered-mask ground truth vs cyan actual model detections** in six held-out test scenes. This is a static review sample, NOT independently approved human visual baseline.
- **Dataset replay:** a second fresh Blender render for 3 seeds exactly matches the original RGB **after image decoding, pixel-for-pixel**, including all actor masks. Byte SHA256 differs (PNG container metadata), so use decoded-pixel equality for reproducibility while checking each exact file's SHA256 for provenance. Test `test_blender_render_replay_is_pixel_deterministic_even_if_png_bytes_differ` guards this.
- **Production release:** **BLOCKED** by design. The generic block actor detector needs additional **real CineFactory rig/motion/style sources** in training, true multi-project out-of-domain holdout and independent human-approved annotations. It is not promoted or wired as a replacement production detector.

Evidence: `data/verification/v189_scene_diversity/v189_qualification_evidence.json` machine-readable verdict `REAL_BLENDER_SYNTHETIC_MASKS_PASS_TEST_PASS_PRODUCTION_BLOCKED`.


### Observed domain failure signature on v186

Review of a real frame from v185/v186 shows **characters sitting at school desks, most legs/torso blocked by furniture, dark classroom lighting, overhead/sidelight contrast, background window shapes**. V189 rendered dataset is mostly standing full-height voxel figures in a clean open Workbench room. This is a concrete, unaddressed domain shift; 0.0 recall of the v189 model on old CineFactory footage is consistent with it (causality not yet isolated experimentally).

**Required v1.6.30 countermeasure:** use **existing actual CineFactory character rigs** and scene templates; randomize sitting/standing, partial torso occlusion, desks/chairs, interior/exterior/background clutter, fill/rim/key shadows, dark and bright environments, camera high/low/side, varying wardrobe/skins and continuity. Produce per-actor visible masks via Blender object-ID/segmentation passes after true occlusion, then test on completely held-out *project/scene/camera* groups and independently annotated samples. Only after measured recall/precision and IP/license review may a model candidate be considered for a production opt-in review. Never overwrite the old detector until acceptance.

## 6. Full regression closure — 2026-10-09

- First full run: **723 passed / 3 failed** (283.64s), source of the failures was mask decoding returning HxWx3 rather than an assumed HxW grayscale array in some full-suite contexts. The original failure log is retained at `regression_v189.txt`, not erased.
- Surgical fix: `BlenderVisibleMaskDatasetAssembler._sample` explicitly normalizes 2D / BGR / BGRA Blender PNG mask inputs to 2D grayscale; rejects non-neutral 3-channel mask data. Independent test for rendered-mask bounds uses Pillow grayscale decode, not the same OpenCV backend. A dedicated simulated three-channel OpenCV regression was added.
- Focused preceding-suite verification **77 passed**; complete targeted v1.6.23–v1.6.29 before the additional new fix regression **126 passed**.
- **FINAL full repository test: 727 passed / 0 failed in 250.08 seconds (4m10s), exit code 0**. `python -m compileall -q cinefactory scripts tests` PASS; tracked `git diff --check` PASS (only Git LF→CRLF informational warnings).
- Final regression log: `data/verification/v189_scene_diversity/regression_v189_final.txt`.
- Evidence verdict `REAL_BLENDER_SYNTHETIC_MASKS_PASS_TEST_PASS_PRODUCTION_BLOCKED` has not been changed to imply real-domain success. Full external CineFactory video recall **0.0** remains a blocker.
- Working branch `studio/v1.6.6-universal-company`, HEAD `44e1f5f` preserved. No resets, no staging or broad commits, no deployment or production model replacement.
