from __future__ import annotations
"""v1.6.30 train actual CineFactory Minecraft/R6 worker-generated rigs.

Train/VAL only. External v186 video and heldout TEST are never used for
backprop, validation checkpointing, hyperparameter/threshold selection.
"""
import hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.blender_mask_dataset_qc import (
    BlenderMaskDatasetQC,BlenderVisibleMaskDatasetAssembler,
)
OUT=ROOT/"data"/"verification"/"v190_real_rig_dataset"

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    qcfile=OUT/"mask_dataset_qc.json"
    qc=BlenderMaskDatasetQC.model_validate_json(qcfile.read_text(encoding="utf-8"))
    if not qc.passed or qc.split_counts!={"train":72,"val":18,"test":24}:
        raise RuntimeError("REAL_RIG_DATASET_QC_NOT_SEALED")
    findings=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
        dataset_dir=OUT/"dataset",report=qc)
    if findings:raise RuntimeError("REAL_RIG_DATASET_TAMPER_DETECTED:"+str(findings[:3]))
    source=ROOT/"data"/"verification"/"v189_scene_diversity"/"model_runs"/"v189_multiscene"/"weights"/"best.pt"
    if not source.is_file():raise RuntimeError("V189_BASELINE_WEIGHTS_MISSING")
    import torch
    from ultralytics import YOLO
    torch.set_num_threads(8)
    model=YOLO(str(source))
    model.train(data=str(OUT/"dataset"/"data.yaml"),epochs=14,imgsz=384,
                batch=12,workers=0,device="cpu",seed=130,patience=14,
                project=str(OUT/"model_runs"),name="v190_actual_worker_rigs",
                exist_ok=True,plots=False,verbose=False,cache=False,
                deterministic=True,save=True,single_cls=True,amp=False)
    modelpath=OUT/"model_runs"/"v190_actual_worker_rigs"/"weights"/"best.pt"
    if not modelpath.is_file():raise RuntimeError("REAL_RIG_CHECKPOINT_MISSING")
    worker=ROOT/"scripts"/"blender_animation_worker.py"
    source_configs=OUT/"rig_snapshot_v190.json"
    snap=json.loads(source_configs.read_text(encoding="utf-8"))
    metadata={
        "status":"TRAINED_REAL_CINEFACTORY_WORKER_RIGS_EXTERNAL_TEST_PENDING",
        "train_images":72,"val_images":18,"heldout_images_unseen":24,
        "training_uses_test":False,
        "training_uses_v186_external_video":False,
        "model_path":str(modelpath.resolve()),"model_sha256":sha(modelpath),
        "initial_weights":str(source.resolve()),"initial_sha256":sha(source),
        "real_worker_sha256":sha(worker),
        "scene_rig_manifest_sha256":sha(source_configs),
        "source_rig_config_sha256":snap["source_sha256"],
        "mask_dataset_manifest_sha256":qc.manifest_sha256,
        "train_rig_families":["MINECRAFT","ROBLOX_R6"],
        "test_camera_family":"HELDOUT_WIDE_HIGH_LOW",
        "epoch_request":14,"imgsz":384,"batch":12,"device":"cpu",
        "license_risk":"ULTRALYTICS_AGPL_OR_COMMERCIAL_LICENSE_REVIEW_REQUIRED",
        "production_qualified":False,
        "generalized_real_video_detection":False,
    }
    (OUT/"training_manifest_v190.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print("V190_ACTUAL_RIG_TRAINING_COMPLETE",json.dumps(metadata,indent=2),flush=True)

if __name__=="__main__":main()
