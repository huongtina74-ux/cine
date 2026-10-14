"""Verify local VLM smoke results against objective image fixtures.

Small smoke data are never sufficient to license model promotion or video analysis.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from .core import _write_json

EXPECTED={
    "redblue":{"ground_truth":"YES","corner":(220,35,35),"center":(12,25,230)},
    "green":{"ground_truth":"NO","corner":(36,190,59),"center":(240,230,12)},
    "white":{"ground_truth":"NO","corner":(240,240,240),"center":(240,240,240)},
    "redblue2":{"ground_truth":"YES","corner":(220,35,35),"center":(12,25,230)},
}


def audit_vlm_cpu_benchmark(report_json: str|Path, output_json: str|Path) -> dict:
    from PIL import Image
    source=Path(report_json).resolve(strict=True)
    packet=json.loads(source.read_text(encoding="utf-8"))
    if packet.get("schema")!="cine.research.vlm_cpu_smoke.v1":
        raise ValueError("Unrecognized vision benchmark report")
    if packet.get("model")!="HuggingFaceTB/SmolVLM2-256M-Video-Instruct":
        raise ValueError("Model lineage mismatch")
    if packet.get("revision")!="067788b187b95ebe7b2e040b3e4299e342e5b8fd":
        raise ValueError("Model revision mismatch")
    if packet.get("hardware",{}).get("run_device")!="cpu":
        raise ValueError("This benchmark audits CPU-only inference")
    if packet.get("production_permission") is not False:
        raise ValueError("Smoke cannot approve production")
    observations=packet.get("tests",[])
    if not isinstance(observations,list) or len(observations)>4:
        raise ValueError("Bad benchmark test list")
    details=[]
    ids=set()
    for case in observations:
        if not isinstance(case,dict):
            raise ValueError("Malformed smoke observation")
        ident=case.get("id")
        if ident not in EXPECTED or ident in ids:
            raise ValueError("Unknown/repeated fixture")
        ids.add(ident)
        original=EXPECTED[ident]
        if case.get("ground_truth")!=original["ground_truth"]:
            raise ValueError("Changed reference answer")
        image=Path(case["image_path"]).resolve(strict=True)
        if image != source.parent/(ident+".png"):
            raise ValueError("Untrusted image fixture path")
        with Image.open(image) as im:
            rgb=im.convert("RGB")
            if (rgb.size!=(256,256) or rgb.getpixel((0,0))!=original["corner"]
                or rgb.getpixel((128,128))!=original["center"]):
                raise ValueError("Image labels and actual pixels diverged")
        pred=str(case.get("prediction","")).upper()
        if case.get("correct") is not (pred==original["ground_truth"]):
            raise ValueError("Correctness flag differs from original fixture")
        seconds=case.get("inference_seconds")
        if (isinstance(seconds,bool) or not isinstance(seconds,(float,int))
            or not math.isfinite(seconds) or seconds<0):
            raise ValueError("Invalid inference runtime")
        details.append({"id":ident,"correct":pred==original["ground_truth"],
                        "seconds":seconds,"image_sha256":hashlib.sha256(image.read_bytes()).hexdigest()})
    valid=packet.get("state")=="CPU_EXPERIMENT_COMPLETE" and len(details)>=3
    correct=sum(x["correct"] for x in details)
    fraction=correct/len(details) if details else None
    if not valid:
        classification="NO_VALID_COMPLETED_BENCHMARK"
    elif fraction<0.8:
        classification="SMOKE_REJECT_POOR_CONTROLLED_ACCURACY"
    else:
        classification="CPU_SMOKE_PASS_NOT_GENERALIZED"
    unique_predictions=sorted({str(x.get("prediction","")).strip().upper()
                               for x in observations if isinstance(x,dict)})
    median=sorted(x["seconds"] for x in details)[len(details)//2] if details else None
    flags=[]
    if valid and fraction<0.8:
        flags.append("CONTROLLED_IMAGE_ACCURACY_BELOW_EXPERIMENTAL_FLOOR")
    if valid and len(unique_predictions)==1:
        flags.append("CONSTANT_ANSWER_POSSIBLE_MODEL_OR_PROCESSOR_BIAS")
    if median is not None and median>10:
        flags.append("CPU_MEDIAN_IMAGE_LATENCY_OVER_10_SECONDS")
    flags.append("ONLY_BOUNDED_SYNTHETIC_IMAGES_NOT_REAL_VIDEO_BENCHMARK")
    result={
        "schema":"cine.research.vlm_benchmark_gate.v1",
        "state":classification,
        "source_report":str(source),
        "source_report_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "sample_count":len(details),"controlled_accuracy":fraction,
        "sample_results":details,
        "unique_model_predictions":unique_predictions,
        "quality_flags":flags,
        "cpu_inference_median_seconds":median,
        "cuda_acceleration_benchmarked":False,
        "actual_competitor_video_inference_completed":False,
        "sample_size_sufficient_for_production":False,
        "human_ground_truth_qa_complete":False,
        "model_deploy_approved":False,
        "production_permission":False,
        "required_next_evidence":[
            "Human-labeled multi-format 30+ image/video-frame set across unrelated niches",
            "Precision for visual attributes, hallucination rate and temporal-reference correctness",
            "Measured max RAM/VRAM, average latency, stress concurrency and model fallback",
            "Independent visual Quality review of actual authorized frames and source rights",
        ],
    }
    target=Path(output_json)
    if target.exists():
        raise FileExistsError("Benchmark gate output immutable")
    _write_json(target,result)
    return result
