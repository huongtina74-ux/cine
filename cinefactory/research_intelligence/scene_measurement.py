"""Objective visual scene measurements from locally observed, authorized frames.

Frame deltas, brightness and image contrast are measurable; they are NOT plot,
pacing, emotional engagement, retention or 'professional camera' verdicts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .core import _write_json


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure_sampled_frames(observation_json: str | Path, output_json: str | Path) -> dict:
    """Hash-check all exact timestamp frames, measure their pixel properties."""
    import cv2
    import numpy as np

    file=Path(observation_json).resolve(strict=True)
    packet=json.loads(file.read_text(encoding="utf-8"))
    if packet.get("schema")!="cine.research.observation.v1":
        raise ValueError("Local frame observation required")
    frames=packet.get("frames")
    if not isinstance(frames,list) or not 1<=len(frames)<=48:
        raise ValueError("1..48 existing observed frames required")
    baseline=None
    last=None
    samples=[]
    time_keys=set()
    for idx,frame in enumerate(frames):
        sec=frame.get("second")
        if (isinstance(sec,bool) or not isinstance(sec,(float,int)) or sec<0
            or sec>=packet.get("duration_seconds",0) or sec in time_keys):
            raise ValueError("Invalid or repeated observation timestamp")
        time_keys.add(sec)
        src=Path(frame["path"]).resolve(strict=True)
        if src.suffix.lower() not in (".jpg",".jpeg") or not src.is_file():
            raise ValueError("Original frame JPEG missing")
        if not src.is_relative_to(file.parent/"frames"):
            raise ValueError("Frame path is outside canonical observation directory")
        if src.stat().st_size>3_000_000 or _sha(src)!=frame.get("sha256"):
            raise ValueError("Frame hash or size changed")
        pic=cv2.imread(str(src),cv2.IMREAD_COLOR)
        if pic is None or pic.size==0:
            raise ValueError("JPEG could not be decoded")
        h,w=pic.shape[:2]
        if h*w>4_000_000 or h<48 or w<48:
            raise ValueError("Frame pixel budget invalid")
        gray=cv2.cvtColor(pic,cv2.COLOR_BGR2GRAY)
        scaled=cv2.resize(gray,(96,54))
        rgb=cv2.cvtColor(pic,cv2.COLOR_BGR2RGB)
        # Full-image metrics, not object detection, action or script inference.
        luminance_mean=float(gray.mean())
        luminance_std=float(gray.std())
        edge_proxy=float(cv2.Laplacian(gray,cv2.CV_64F).var())
        change=None
        if last is not None:
            change=float(cv2.absdiff(scaled,last).mean())/255
        if baseline is None:baseline=scaled
        last=scaled
        samples.append({
            "sample_id":f"frame_{idx:04d}",
            "second":round(float(sec),3),
            "path":str(src),"sha256":frame["sha256"],
            "height_px":h,"width_px":w,
            "mean_rgb_0_255":[round(float(v),2) for v in rgb.mean(axis=(0,1))],
            "mean_luminance_0_255":round(luminance_mean,2),
            "luminance_stddev_0_255":round(luminance_std,2),
            "edge_variance_proxy":round(edge_proxy,3),
            "change_from_previous_sample_0_1":round(change,4) if change is not None else None,
            "temporal_interval_seconds":round(float(sec)-float(frames[idx-1]["second"]),3) if idx else None,
            "visual_semantics":"NOT_DETERMINED",
        })
    diffs=[x["change_from_previous_sample_0_1"] for x in samples
           if x["change_from_previous_sample_0_1"] is not None]
    result={
        "schema":"cine.research.scene_measurement.v1",
        "state":"HASH_VERIFIED_OBJECTIVE_FRAME_FACTS",
        "source_observation_path":str(file),"observation_sha256":_sha(file),
        "samples":samples,"frame_count":len(samples),
        "sampling_strategy":packet.get("sampling",{}).get("strategy","unknown"),
        "average_inter_sample_change_proxy_0_1":round(sum(diffs)/len(diffs),4) if diffs else None,
        "mean_frame_luminance_0_255":round(sum(x["mean_luminance_0_255"] for x in samples)/len(samples),2),
        "conclusions_about_story_hook":"UNKNOWN",
        "conclusions_about_retention":"UNKNOWN",
        "conclusions_about_motion_quality":"UNKNOWN",
        "production_permission":False,
        "limitations":[
            "Sparse frame changes cannot establish real shot cuts, actual movement or true editing pace",
            "Luminance and edge variance are proxies, not aesthetics or animation-quality ratings",
            "No reliable voice/dialogue, timeline semantics or emotional impact from this module",
        ],
    }
    _write_json(Path(output_json),result)
    return result
