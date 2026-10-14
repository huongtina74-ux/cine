from __future__ import annotations
"""Train candidate using only the QC-approved TRAIN and VALIDATION Blender groups.

YOLO sees neither TEST RGB nor TEST labels during fit/checkpoint selection.
No data leakage, auto-deployment, or threshold tuning to match holdout.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
OUT=ROOT/"data"/"verification"/"v189_scene_diversity"

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    from cinefactory.studio.blender_mask_dataset_qc import BlenderMaskDatasetQC
    qc_path=OUT/"mask_dataset_qc.json"
    report=BlenderMaskDatasetQC.model_validate_json(qc_path.read_text(encoding="utf-8"))
    if not report.passed or report.split_counts!={"train":96,"val":24,"test":32}:
        raise RuntimeError("V189_DATASET_NOT_VERIFIED_OR_SPLIT_SIZE_CHANGED")
    source=ROOT/".tools"/"models"/"yolo11n_coco.pt"
    if not source.is_file():
        raise RuntimeError("YOLO_BASELINE_MODEL_MISSING")
    import torch
    from ultralytics import YOLO
    torch.set_num_threads(8)
    model=YOLO(str(source))
    training=model.train(
        data=str(OUT/"dataset"/"data.yaml"),
        epochs=16,imgsz=384,batch=16,workers=0,device="cpu",
        seed=129,patience=16,project=str(OUT/"model_runs"),
        name="v189_multiscene",exist_ok=True,
        plots=False,verbose=False,cache=False,
        deterministic=True,save=True,
        single_cls=True,amp=False,
    )
    checkpoint=OUT/"model_runs"/"v189_multiscene"/"weights"/"best.pt"
    if not checkpoint.is_file():
        raise RuntimeError("V189_MODEL_CHECKPOINT_MISSING")
    meta={
        "status":"DIAGNOSTIC_TRAINING_DONE_HOLDOUT_PENDING",
        "train_images":96,"val_images":24,"test_images_not_seen":32,
        "training_uses_test":False,
        "input_model":str(source.resolve()),
        "input_sha256":digest(source),
        "trained_model":str(checkpoint.resolve()),
        "trained_sha256":digest(checkpoint),
        "train_data_manifest_sha256":report.manifest_sha256,
        "training_epochs_requested":16,"training_imgsz":384,
        "training_batch":16,"device":"cpu",
        "train_and_val_families":["primary","complementary"],
        "test_family":"unseen_palette",
        "review_required":"ULTRALYTICS_MODEL_LICENSE_AGPL_OR_COMMERCIAL_LICENSE",
        "production_qualified":False,"generalized_actor_detection":False,
    }
    (OUT/"training_manifest_v189.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    print("V189_TRAINING_COMPLETE",json.dumps(meta,indent=2),flush=True)

if __name__=="__main__":
    main()
