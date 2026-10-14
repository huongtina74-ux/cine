from __future__ import annotations
"""v1.6.30 visual audit: authentic-worker Blender scene frames + true mask bboxes."""
from pathlib import Path
import sys,json
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.blender_mask_dataset_qc import BlenderMaskDatasetQC

def main():
    folder=ROOT/"data"/"verification"/"v190_real_rig_dataset"
    qc=BlenderMaskDatasetQC.model_validate_json(
        (folder/"mask_dataset_qc.json").read_text(encoding="utf-8"))
    if not qc.passed:raise ValueError("MASK_DATASET_NOT_QUALIFIED")
    images=[]
    for split in ("train","val","test"):
        rows=[x for x in qc.samples if x.split==split]
        indices=[0,2,5,9]
        for idx in indices:
            s=rows[min(idx,len(rows)-1)]
            img=cv2.imread(str(folder/"dataset"/"images"/split/(s.scene_id+".png")))
            if img is None:raise ValueError("MISSING_PREVIEW_IMAGE")
            for box in s.boxes:
                x0,y0,x1,y1=box.image_box
                cv2.rectangle(img,(x0,y0),(x1-1,y1-1),(0,220,255),2)
                cv2.putText(img,box.actor,(x0,max(12,y0-4)),
                    cv2.FONT_HERSHEY_SIMPLEX,.45,(0,220,255),1)
            h,w=img.shape[:2]
            cv2.rectangle(img,(0,h-24),(w,h),(12,12,12),-1)
            cv2.putText(img,f"{s.split} {s.scene_id} / seed {s.seed}",(5,h-7),
                cv2.FONT_HERSHEY_SIMPLEX,.45,(255,255,255),1)
            images.append(img)
    combined=np.concatenate([np.concatenate(images[i:i+4],axis=1) for i in [0,4,8]],axis=0)
    target=folder/"actual_worker_rig_mask_contact_sheet_v190.jpg"
    assert cv2.imwrite(str(target),combined,[int(cv2.IMWRITE_JPEG_QUALITY),87])
    print("REAL_WORKER_RIG_MASK_CONTACT_PASS",target,combined.shape)
if __name__=="__main__":main()
