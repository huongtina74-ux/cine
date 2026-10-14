from __future__ import annotations
"""v190 independent pixel-side visual comparison on the EXISTING v186 MP4.

Yellow = post-inference rig/Blender sidecar GT, cyan = YOLO model predicted
from raw decoded MP4 frame alone. Visualization never promotes model quality.
"""
import json,sys
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

def main():
    from ultralytics import YOLO
    out=ROOT/"data"/"verification"/"v190_real_rig_dataset"
    evidence=json.loads((out/"v190_qualification_evidence.json").read_text(encoding="utf-8"))
    model=YOLO(evidence["trained_model"]["model_path"])
    path=ROOT/"data"/"verification"/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    truth=json.loads(Path(str(path)+".frame_qc.json").read_text(encoding="utf-8"))["actors"]
    cap=cv2.VideoCapture(str(path))
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if n<4:raise ValueError("EXTERNAL_VIDEO_MISSING_FRAMES")
    rows=[]
    conf=evidence["sealed_holdout_render"]["chosen_confidence"]
    try:
        for idx in [0,max(1,n//3),max(2,2*n//3),n-1]:
            cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
            ok,frame=cap.read()
            if not ok:raise RuntimeError("EXTERNAL_SAMPLE_DECODE_FAILED")
            h,w=frame.shape[:2]
            left=frame.copy()
            right=frame.copy()
            result=model.predict(frame,conf=conf,device="cpu",imgsz=384,verbose=False)[0]
            # Class 0 actor predictions are drawn first, before any truth.
            for rect,score in zip(result.boxes.xyxy,result.boxes.conf):
                x0,y0,x1,y1=(int(v) for v in rect)
                cv2.rectangle(right,(x0,y0),(x1,y1),(255,220,0),2)
                cv2.putText(right,f"{float(score):.2f}",(x0,max(13,y0-5)),
                            cv2.FONT_HERSHEY_SIMPLEX,.42,(255,220,0),1)
            for actor,b in truth.items():
                ndc=b["screen_box"]
                x0=round(ndc["x0"]*w);x1=round(ndc["x1"]*w)
                y0=round((1-ndc["y1"])*h);y1=round((1-ndc["y0"])*h)
                cv2.rectangle(left,(x0,y0),(x1,y1),(0,240,255),2)
                cv2.putText(left,actor,(x0,max(13,y0-6)),
                            cv2.FONT_HERSHEY_SIMPLEX,.48,(0,240,255),1)
            pair=np.concatenate([left,right],axis=1)
            cv2.rectangle(pair,(0,h-22),(w*2,h),(12,12,12),-1)
            cv2.putText(pair,f"v186 frame {idx} - BLENDER RIG BOX GT",(7,h-6),
                        cv2.FONT_HERSHEY_SIMPLEX,.43,(0,240,255),1)
            cv2.putText(pair,f"ACTUAL YOLO PREDICTION confidence {conf:.2f}",(w+7,h-6),
                        cv2.FONT_HERSHEY_SIMPLEX,.43,(255,220,0),1)
            rows.append(pair)
    finally:cap.release()
    final=np.concatenate(rows,axis=0)
    target=out/"v190_external_v186_actual_predictions.jpg"
    assert cv2.imwrite(str(target),final,[int(cv2.IMWRITE_JPEG_QUALITY),89])
    print("V190_ACTUAL_VIDEO_VISUAL_EVIDENCE_PASS",target,"dimensions",final.shape)
if __name__=="__main__":main()
