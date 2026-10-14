import json
from pathlib import Path
import pytest
from PIL import Image,ImageDraw

from cinefactory.research_intelligence.vlm_benchmark_gate import (
    EXPECTED,audit_vlm_cpu_benchmark,
)

MODEL="HuggingFaceTB/SmolVLM2-256M-Video-Instruct"
REV="067788b187b95ebe7b2e040b3e4299e342e5b8fd"


def fixture(tmp_path, *, right=True):
    data=[]
    for idx,key in enumerate(["redblue","green","white"]):
        meta=EXPECTED[key]
        image=Image.new("RGB",(256,256),meta["corner"])
        paint=ImageDraw.Draw(image)
        if key=="redblue":
            paint.rectangle((85,85,165,165),fill=meta["center"])
        elif key=="green":
            paint.ellipse((70,70,180,180),fill=meta["center"])
        image.save(tmp_path/(key+".png"))
        predicted=meta["ground_truth"] if right else "NO"
        data.append({"id":key,"ground_truth":meta["ground_truth"],
                     "prediction":predicted,
                     "correct":predicted==meta["ground_truth"],
                     "inference_seconds":0.1,"image_path":str(tmp_path/(key+".png"))})
    source=tmp_path/"report.json"
    source.write_text(json.dumps({"schema":"cine.research.vlm_cpu_smoke.v1",
                        "model":MODEL,"revision":REV,
                        "hardware":{"run_device":"cpu"},"state":"CPU_EXPERIMENT_COMPLETE",
                        "production_permission":False,"tests":data}),encoding="utf-8")
    return source


def test_all_correct_still_not_approved(tmp_path):
    report=fixture(tmp_path)
    result=audit_vlm_cpu_benchmark(report,tmp_path/"gate.json")
    assert result["state"]=="CPU_SMOKE_PASS_NOT_GENERALIZED"
    assert result["controlled_accuracy"]==1.0
    assert result["cuda_acceleration_benchmarked"] is False
    assert result["model_deploy_approved"] is False


def test_poor_accuracy_fails(tmp_path):
    source=fixture(tmp_path,right=False)
    result=audit_vlm_cpu_benchmark(source,tmp_path/"gate.json")
    assert result["state"]=="SMOKE_REJECT_POOR_CONTROLLED_ACCURACY"
    assert result["controlled_accuracy"]<0.8


def test_forged_correct_flag_is_rejected(tmp_path):
    source=fixture(tmp_path)
    raw=json.loads(source.read_text(encoding="utf-8"))
    raw["tests"][0]["prediction"]="NO"
    source.write_text(json.dumps(raw),encoding="utf-8")
    with pytest.raises(ValueError,match="Correctness"):
        audit_vlm_cpu_benchmark(source,tmp_path/"fake.json")


def test_changed_image_reference_cannot_pass(tmp_path):
    source=fixture(tmp_path)
    img=Image.new("RGB",(256,256),(0,0,0))
    img.save(tmp_path/"redblue.png")
    with pytest.raises(ValueError,match="pixel"):
        audit_vlm_cpu_benchmark(source,tmp_path/"fake.json")


def test_no_inference_is_not_smoke_pass(tmp_path):
    source=fixture(tmp_path)
    raw=json.loads(source.read_text(encoding="utf-8"))
    raw["state"]="CPU_EXPERIMENT_FAILED"
    source.write_text(json.dumps(raw),encoding="utf-8")
    report=audit_vlm_cpu_benchmark(source,tmp_path/"gate.json")
    assert report["state"]=="NO_VALID_COMPLETED_BENCHMARK"


def test_no_duplicate_benchmark_overwrite(tmp_path):
    source=fixture(tmp_path)
    audit_vlm_cpu_benchmark(source,tmp_path/"gate.json")
    with pytest.raises(FileExistsError):
        audit_vlm_cpu_benchmark(source,tmp_path/"gate.json")
