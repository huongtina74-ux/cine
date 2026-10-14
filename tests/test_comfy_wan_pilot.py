from pathlib import Path
import pytest
from cinefactory.production.comfy_wan_pilot import build_workflow,_inputs_available

def test_wan_workflow_uses_local_installed_model_and_small_frames():
    flow=build_workflow()
    assert len(flow)==10
    assert flow["1"]["class_type"]=="UNETLoader"
    assert flow["6"]["class_type"]=="WanFunInpaintToVideo"
    assert flow["6"]["inputs"]["width"]==320
    assert flow["6"]["inputs"]["length"]==17
    assert flow["10"]["class_type"]=="SaveImage"
    assert all("url" not in node.get("inputs",{}) for node in flow.values())

def test_unsafe_dimensions_and_big_steps_refused():
    with pytest.raises(ValueError):build_workflow(width=2048)
    with pytest.raises(ValueError):build_workflow(steps=100)
    with pytest.raises(ValueError):build_workflow(frames=100)

def test_missing_local_checkpoint_prevents_backend_submission():
    info={node["class_type"]:{"input":{"required":{}}} for node in build_workflow().values()}
    info["UNETLoader"]["input"]["required"]["unet_name"]=[["other_model"]]
    info["CLIPLoader"]["input"]["required"]["clip_name"]=[["umt5_xxl_fp8_e4m3fn_scaled.safetensors"]]
    info["VAELoader"]["input"]["required"]["vae_name"]=[["wan_2.1_vae.safetensors"]]
    okay,reason=_inputs_available(info)
    assert not okay
    assert "Missing installed weight" in reason
