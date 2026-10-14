"""Measure exact per-pixel run-to-run reproducibility; not aesthetic quality.

Uses immutable captured PNGs for the same base .blend across four render
starts per engine. Differences can reflect temporal antialiasing,
renderer/GPU nondeterminism and driver context, not actor identity alone.
"""
from pathlib import Path
import json
import statistics
import sys
import hashlib
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/verification/v196_golden_benchmark"

def main():
    summary={}
    for engine in ("workbench","eevee"):
        base=OUT/"frames"/engine
        total=0
        exact=0
        mae=[]
        maxerr=[]
        per_trial={}
        for round_id in (2,3,4):
            variant=OUT/"repeatability"/f"round_{round_id:02d}"/"frames"/engine
            scored=[]
            for frame_idx in range(1,25):
                left=cv2.imread(str(base/f"frame_{frame_idx:04d}.png"),cv2.IMREAD_UNCHANGED)
                right=cv2.imread(str(variant/f"frame_{frame_idx:04d}.png"),cv2.IMREAD_UNCHANGED)
                if left is None or right is None or left.shape!=right.shape:
                    raise RuntimeError("RENDER_REPEAT_PIXEL_FRAME_MISMATCH")
                delta=cv2.absdiff(left,right)
                err=float(np.mean(delta))
                scored.append(err)
                mae.append(err)
                maxerr.append(int(np.max(delta)))
                if np.array_equal(left,right):
                    exact+=1
                total+=1
            per_trial[str(round_id)]={"median_pixel_mae":round(statistics.median(scored),4),
                                     "max_frame_pixel_mae":round(max(scored),4)}
        summary[engine]={
            "total_cross_run_frames":total,
            "pixel_exact_frame_ratio":round(exact/total,5),
            "median_pixel_mae_0_to_255":round(statistics.median(mae),5),
            "maximum_single_pixel_channel_difference":max(maxerr),
            "per_trial":per_trial,
            "baseline_media_sha256":hashlib.sha256(
                (OUT/(engine+".mp4")).read_bytes()).hexdigest(),
            "human_rated_appearance_comparison":False,
            "render_quality_approved":False,
        }
        print("PIXEL_REPLAY_PROOF",engine,
              summary[engine],flush=True)
    doc={
        "schema":"v1.6.36",
        "status":"REAL_SAME_BLENDER_PROJECT_PIXEL_REPEATABILITY_AUDITED",
        "same_blender_scene_only":True,
        "difference_is_not_subjective_image_quality_score":True,
        "unknown_source_of_pixel_variation":True,
        "renderer":summary,
    }
    (OUT/"pixel_repeatability_v196.json").write_text(
        json.dumps(doc,indent=2),encoding="utf-8")
if __name__=="__main__":main()
