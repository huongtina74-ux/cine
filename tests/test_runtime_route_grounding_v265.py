"""v265: catalog routes cannot masquerade as installed Blender/FFmpeg runtimes."""
from cinefactory.cli import context
from cinefactory.studio.contracts import StudioProjectSpec
from cinefactory.studio.runtime_route_grounding_v265 import (
    ground_professional_plan,backend_executable_probe)
def plan():
    return context().studio.control_plane.plan(StudioProjectSpec(
        studio_project_id="CF_ROUTE_PROBE_TST",
        prompt="Animated original 3D voxel adventure, two heroes, waterfall mystery.",
        domain="animation",niche="minecraft",duration_seconds=45))

def test_runtime_unavailable_blender_must_remove_route_executable():
    raw=plan()
    assert any(x.selected_capability_id=="blender.local"
               for p in raw.segments for x in p.routes)
    def probe(backend):
        return {"backend":backend,"available":backend!="blender.local"}
    cooked=ground_professional_plan(raw,probe=probe)
    assert cooked.executable is False
    assert any("RUNTIME_EXECUTABLE_UNVERIFIED:blender.local" in b for b in cooked.blockers)
    assert all(not x.executable for p in cooked.segments for x in p.routes
               if x.selected_capability_id=="blender.local")
    assert all(p.executable is False for p in cooked.segments)
    # Keep original immutable blueprint plan candidate for reproducible audits.
    assert any(x.executable for p in raw.segments for x in p.routes
               if x.selected_capability_id=="blender.local")

def test_runtime_verified_blender_preserves_eligible_execution_route():
    raw=plan()
    cooked=ground_professional_plan(raw,probe=lambda b:{"backend":b,"available":True})
    assert not any("RUNTIME_EXECUTABLE_UNVERIFIED" in b for b in cooked.blockers)
    assert all(x.executable for p in cooked.segments for x in p.routes if x.selected_capability_id=="blender.local")

def test_real_local_probe_never_falsely_says_executable_without_running():
    result=backend_executable_probe("blender.local")
    if result["available"]:
        assert result["executed"] and result["path"]
    else:
        assert not result["executed"] and result["path"] is None
    other=backend_executable_probe("nonexistent.provider")
    assert other["available"] is None and not other["executed"]
