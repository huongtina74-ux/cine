"""Mine-imator scene generator: the written .miproject must be internally consistent."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "tools" / "mineimator"
TRANSITIONS = {"linear", "instant", "bezier"} | {
    f"ease{w}{c}" for w in ("in", "out", "inout")
    for c in ("quad", "cubic", "quart", "quint", "sine", "expo", "circ", "elastic", "back", "bounce")}


@pytest.fixture(scope="module", params=["binbo_thu01", "binbo_thu02"])
def project(request, tmp_path_factory):
    D = ROOT / request.param
    work = tmp_path_factory.mktemp(request.param)
    if (D / "prep.py").exists():
        subprocess.run([sys.executable, str(D / "prep.py"), str(work)], check=True, cwd=D)
    else:
        subprocess.run([sys.executable, str(D / "skins.py"), str(work / "proj" / "skins")], check=True)
    out = subprocess.run([sys.executable, str(D / "build.py"), str(work)], check=True,
                         capture_output=True, text=True).stdout
    assert "MIPROJECT_OK" in out
    mi = next((work / "proj").glob("*.miproject"))
    return work, json.loads(mi.read_text())


def test_references_resolve(project):
    work, d = project
    res = {r["id"]: r for r in d["resources"]}
    for r in res.values():
        assert (work / "proj" / r["filename"]).exists()
    temps = {t["id"] for t in d["templates"]}
    tls = {t["id"]: t for t in d["timelines"]}
    for t in d["timelines"]:
        assert t["parent"] == "root" or t["parent"] in tls
        if t.get("temp") not in (None, "null"):
            assert t["temp"] in temps
        if t["type"] == "surface":
            assert tls[t["parent"]].get("model_part_name") == "head"
        for kf in t["keyframes"].values():
            assert kf["TRANSITION"] in TRANSITIONS
            if "TEXTURE_OBJ" in kf:
                assert kf["TEXTURE_OBJ"] in res


def test_root_tree_indices_unique(project):
    _, d = project
    idx = [t["parent_tree_index"] for t in d["timelines"] if t["parent"] == "root"]
    assert len(idx) == len(set(idx))


def test_camera_cuts_and_length(project):
    _, d = project
    cam = next(t for t in d["timelines"] if t["type"] == "camera")
    frames = sorted(int(f) for f in cam["keyframes"])
    assert frames[0] == 0 and frames[-1] == d["project"]["timeline"]["region_end"]
    cuts = [f for f in frames if cam["keyframes"][str(f)]["TRANSITION"] == "instant"]
    assert len(cuts) >= 5


def test_benchmark_frames_counts_hard_cuts(tmp_path):
    """Three flat colour shots of 2 s each (5 fps sampling) = 2 cuts, 3 shots of ~2 s."""
    vid = tmp_path / "three_shots.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=red:s=320x180:d=2:r=24",
                    "-f", "lavfi", "-i", "color=c=blue:s=320x180:d=2:r=24", "-f", "lavfi", "-i", "color=c=white:s=320x180:d=2:r=24",
                    "-filter_complex", "[0][1][2]concat=n=3:v=1", "-pix_fmt", "yuv420p", str(vid)], check=True)
    out = subprocess.run([sys.executable, str(ROOT / "benchmark_frames.py"), str(vid)], check=True, capture_output=True, text=True).stdout
    m = json.loads(out)
    assert m["cuts"] == 2 and abs(m["avg_shot_s"] - 2.0) < 0.2
    assert m["saturation"] > 0.3 and m["luma"] > 60
