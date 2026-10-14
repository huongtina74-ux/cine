from __future__ import annotations
"""Train in-domain Minecraft/Roblox-style block actor detector using only the
first real Blender render and rig-labelled boxes. Held-out second render is
NEVER used in training. This is a tiny same-rig/domain experiment, not
general object detection certification. Ultralytics licensing review needed.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path
import cv2
import numpy as np
import yaml

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
OUT=ROOT/"data"/"verification"/"v188_acoustic_detector"
DATASET=OUT/"block_actor_data"

def main():
    reference=ROOT/"data"/"verification"/"v185_alignment_reid"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    target=ROOT/"data"/"verification"/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    source_ref=json.loads((ROOT/"data"/"verification"/"v185_alignment_reid"/"v185_render_evidence.json").read_text(encoding="utf-8"))
    target_ref=json.loads((ROOT/"data"/"verification"/"v186_multishot_second"/"v186_render_evidence.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(reference.read_bytes()).hexdigest()==source_ref["blender"]["sha256"]
    assert hashlib.sha256(target.read_bytes()).hexdigest()==target_ref["blender"]["sha256"]
    assert source_ref["blender"]["sha256"]!=target_ref["blender"]["sha256"]
    gt=json.loads(Path(str(reference)+".frame_qc.json").read_text(encoding="utf-8"))["actors"]
    assert set(gt)=={"A","B"}
    OUT.mkdir(parents=True,exist_ok=True)
    for branch in ("train","val"):
        (DATASET/"images"/branch).mkdir(parents=True,exist_ok=True)
        (DATASET/"labels"/branch).mkdir(parents=True,exist_ok=True)
    capture=cv2.VideoCapture(str(reference))
    try:
        count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        assert count>=50
        ids=sorted(set(int(round(x)) for x in np.linspace(0,count-1,56)))
        train_count=val_count=0
        for j,idx in enumerate(ids):
            capture.set(cv2.CAP_PROP_POS_FRAMES,idx)
            ok,frame=capture.read()
            assert ok
            branch="val" if j%5==0 else "train"
            name=f"blender1_{idx:05d}"
            assert cv2.imwrite(str(DATASET/"images"/branch/(name+".png")),frame)
            rows=[]
            for actor in sorted(gt):
                b=gt[actor]["screen_box"]
                # Blender sidecar is NDC bottom-left. YOLO image coords
                # are center x/y from top-left.
                x=(b["x0"]+b["x1"])/2
                y=1-(b["y0"]+b["y1"])/2
                w=b["x1"]-b["x0"]
                h=b["y1"]-b["y0"]
                assert 0<x<1 and 0<y<1 and 0<w<1 and 0<h<1
                rows.append(f"0 {x:.8f} {y:.8f} {w:.8f} {h:.8f}")
            (DATASET/"labels"/branch/(name+".txt")).write_text("\n".join(rows)+"\n",encoding="utf-8")
            if branch=="train":train_count+=1
            else:val_count+=1
    finally:capture.release()
    yaml_path=DATASET/"data.yaml"
    yaml_path.write_text(yaml.safe_dump({
        "path":str(DATASET.resolve()),"train":"images/train","val":"images/val",
        "nc":1,"names":{0:"block_actor"},
    }),encoding="utf-8")
    from ultralytics import YOLO
    weights=ROOT/".tools"/"models"/"yolo11n_coco.pt"
    assert weights.is_file()
    model=YOLO(str(weights))
    model.train(
        data=str(yaml_path),epochs=10,imgsz=320,batch=8,
        workers=0,device="cpu",seed=1287,patience=5,
        project=str(OUT/"train_runs"),name="block_actor_v188",
        exist_ok=True,plots=False,verbose=False,cache=False,
        deterministic=True,save=True,augment=True,
    )
    best=OUT/"train_runs"/"block_actor_v188"/"weights"/"best.pt"
    assert best.is_file()
    metadata={
        "status":"TRAINED_FIRST_RENDER_ONLY_NOT_GENERALIZED",
        "model_path":str(best),"model_sha256":hashlib.sha256(best.read_bytes()).hexdigest(),
        "train_source_sha256":source_ref["blender"]["sha256"],
        "heldout_second_video_sha256":target_ref["blender"]["sha256"],
        "same_scene_and_character_rigs":True,
        "train_images":train_count,"in_source_validation_images":val_count,
        "epochs_requested":10,"image_size":320,"device":"cpu",
        "license_risk":"ULTRALYTICS_AGPL_AND_MODEL_TERMS_MUST_BE_REVIEWED_FOR_COMMERCIAL_USE",
        "production_qualified":False,
        "out_of_domain_verified":False,
        "generalized_actor_detector":False,
    }
    (OUT/"training_manifest_v188.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(json.dumps(metadata,indent=2))
if __name__=="__main__":main()
