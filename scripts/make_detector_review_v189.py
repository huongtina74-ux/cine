from __future__ import annotations
"""Static side-by-side audit gallery of held-out *post-selection* predictions.

Yellow = truth from Blender rendered pixel masks. Cyan = independently
predicted YOLO boxes. Intended for expert review; never a self sign-off.
"""
import json,sys
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
OUT=ROOT/"data"/"verification"/"v189_scene_diversity"

def main():
    from ultralytics import YOLO
    data=json.loads((OUT/"v189_qualification_evidence.json").read_text(encoding="utf-8"))
    report=data["synthetic_unseen_scene_detector"]
    model=YOLO(data["training"]["trained_model"])
    conf=float(report["chosen_confidence"])
    rows=[]
    for i in [0,3,8,12,17,25]:
        file=OUT/"dataset"/"images"/"test"/(f"test_{i:04d}.png")
        img=cv2.imread(str(file))
        if img is None:raise ValueError(f"REVIEW_IMAGE_MISSING:{file}")
        h,w=img.shape[:2]
        gt=img.copy()
        pred=img.copy()
        for line in (OUT/"dataset"/"labels"/"test"/(file.stem+".txt")).read_text(encoding="utf-8").strip().splitlines():
            c,cx,cy,bw,bh=(float(z) for z in line.split())
            x0,y0,x1,y1=int((cx-bw/2)*w),int((cy-bh/2)*h),int((cx+bw/2)*w),int((cy+bh/2)*h)
            cv2.rectangle(gt,(x0,y0),(x1,y1),(0,220,255),2)
        detections=model.predict(pred,imgsz=384,conf=conf,device="cpu",verbose=False)[0]
        for rect,score in zip(detections.boxes.xyxy,detections.boxes.conf):
            x0,y0,x1,y1=(int(v) for v in rect)
            cv2.rectangle(pred,(x0,y0),(x1,y1),(255,225,0),2)
            cv2.putText(pred,f"{float(score):.2f}",(x0,max(12,y0-4)),
                        cv2.FONT_HERSHEY_SIMPLEX,.45,(255,225,0),1)
        combined=np.concatenate([gt,pred],axis=1)
        cv2.rectangle(combined,(0,h-24),(w*2,h),(12,12,12),-1)
        cv2.putText(combined,f"{file.stem}: RENDERED MASK GT",(5,h-7),
                    cv2.FONT_HERSHEY_SIMPLEX,.47,(0,220,255),1)
        cv2.putText(combined,f"YOLO PREDICTED / conf {conf:.2f}",(w+5,h-7),
                    cv2.FONT_HERSHEY_SIMPLEX,.47,(255,225,0),1)
        rows.append(combined)
    gallery=np.concatenate(rows,axis=0)
    path=OUT/"heldout_detector_predictions_review_v189.jpg"
    assert cv2.imwrite(str(path),gallery,[int(cv2.IMWRITE_JPEG_QUALITY),90])
    print("V189_HELDOUT_PREDICTIONS_GALLERY",path,"SHAPE",gallery.shape)
if __name__=="__main__":main()
