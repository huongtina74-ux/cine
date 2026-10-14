from __future__ import annotations
"""v1.6.29 static preview contact sheet with GT pixel-mask bboxes only.

This is an internal visual review artifact; no automatic human approval.
"""
import json
import sys
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.blender_mask_dataset_qc import BlenderMaskDatasetQC

OUT=ROOT/"data"/"verification"/"v189_scene_diversity"

def main():
    data=BlenderMaskDatasetQC.model_validate_json(
        (OUT/"mask_dataset_qc.json").read_text(encoding="utf-8")
    )
    if not data.passed:
        raise ValueError("BLENDER_MASK_QC_NOT_PASS")
    samples=[]
    for split in ("train","val","test"):
        group=[r for r in data.samples if r.split==split]
        for ix in [0,4,9,15]:
            sample=group[min(ix,len(group)-1)]
            pixels=cv2.imread(str(OUT/"dataset"/"images"/split/(sample.scene_id+".png")))
            if pixels is None: raise ValueError("GALLERY_MISSING_SOURCE_IMAGE")
            for row in sample.boxes:
                x0,y0,x1,y1=row.image_box
                cv2.rectangle(pixels,(x0,y0),(x1-1,y1-1),(42,255,255),2)
                cv2.putText(pixels,row.actor,(x0,y0-5),
                            cv2.FONT_HERSHEY_SIMPLEX,.45,(255,255,255),1)
            pixels=cv2.resize(pixels,(384,256))
            cv2.rectangle(pixels,(0,228),(384,256),(20,20,20),-1)
            cv2.putText(pixels,f"{sample.split} / {sample.scene_id} / seed {sample.seed}",
                        (12,247),cv2.FONT_HERSHEY_SIMPLEX,.46,(255,255,255),1)
            samples.append(pixels)
    contact=np.concatenate([
        np.concatenate(samples[i:i+4],axis=1)
        for i in (0,4,8)
    ],axis=0)
    output=OUT/"voxel_dataset_preview_v189.jpg"
    assert cv2.imwrite(str(output),contact,[int(cv2.IMWRITE_JPEG_QUALITY),88])
    print("GALLERY_OK",output,"DIMENSIONS",contact.shape)
if __name__=="__main__": main()
