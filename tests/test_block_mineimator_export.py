import json
from pathlib import Path

import pytest
import yaml

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import EpisodeSpec
from cinefactory.block_animation.mineimator import (
    HUMAN_PARTS, MineImatorError, MineImatorExporter, clip_pose, inspect_project, load_project)

ROOT = Path(__file__).resolve().parents[1]
# Value names read from Mine-imator's app_startup_lists.gml (subset the exporter may write).
KNOWN_VALUES = {"POS_X", "POS_Y", "POS_Z", "ROT_X", "ROT_Y", "ROT_Z", "BEND_ANGLE_X", "VISIBLE", "TRANSITION",
                "CAM_FOV", "CAM_ROTATE", "CAM_ROTATE_DISTANCE", "CAM_ROTATE_ANGLE_XY", "CAM_ROTATE_ANGLE_Z", "SOUND_OBJ"}


def _template(tmp_path, *, camera=True, audio=True, names=("Nova", "Pip")):
    """A minimal .miproject shaped like Mine-imator's project_save_* output."""
    timelines, n = [], 0
    for name in names:
        n += 1; cid = f"C{n}"
        timelines.append({"id": cid, "type": "char", "name": name, "temp": f"T{n}", "default_values": {}, "keyframes": {}, "parent": "root",
                          "parts": [f"{cid}_{p}" for p in HUMAN_PARTS]})
        for p in HUMAN_PARTS:
            timelines.append({"id": f"{cid}_{p}", "type": "bodypart", "name": p, "model_part_name": p, "part_of": cid,
                              "default_values": {}, "keyframes": {}, "parent": cid})
    if camera:
        timelines.append({"id": "CAM1", "type": "camera", "name": "Camera", "default_values": {}, "keyframes": {}, "parent": "root"})
    resources = [{"id": "R1", "type": "skin", "filename": "nova.png"}]
    if audio:
        resources.append({"id": "R9", "type": "sound", "filename": "placeholder.wav"})
        timelines.append({"id": "A1", "type": "audio", "name": "VO", "default_values": {}, "keyframes": {"0": {"SOUND_OBJ": "R9"}}, "parent": "root"})
    doc = {"format": 30, "created_in": "2.0.2", "project": {"name": "tpl", "tempo": 24, "video_width": 1920, "video_height": 1080},
           "resources": resources, "templates": [], "timelines": timelines}
    path = tmp_path / "template.miproject"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def _episode():
    return EpisodeSpec.model_validate_json((ROOT / "examples/block_animation/original_episode.json").read_text())


def _compiled(ep=None):
    return EpisodeAssembler.from_root(ROOT).compile(ep or _episode())


def test_inspect_reports_ready_template(tmp_path):
    r = inspect_project(_template(tmp_path))
    assert r["ready_as_template"] and r["tempo"] == 24
    assert {c["name"] for c in r["characters"]} == {"Nova", "Pip"}
    assert all(not c["missing_parts"] for c in r["characters"])
    assert r["audio_tracks"][0]["sounds"] == ["placeholder.wav"]


def test_inspect_flags_missing_camera(tmp_path):
    r = inspect_project(_template(tmp_path, camera=False))
    assert not r["ready_as_template"] and "NO_CAMERA_TIMELINE" in r["problems"]


def test_binary_mproj_is_rejected(tmp_path):
    p = tmp_path / "old.miproject"; p.write_bytes(b"\x00\x01binary")
    with pytest.raises(MineImatorError, match="re-save"):
        load_project(p)


def test_export_writes_keyframes_without_touching_template(tmp_path):
    tpl = _template(tmp_path); before = tpl.read_text()
    out = tmp_path / "out" / "ep.miproject"
    rep = MineImatorExporter.from_root(ROOT).export(_compiled(), tpl, out, actor_map={"builder": "Nova", "friend": "Pip"})
    assert tpl.read_text() == before
    doc = json.loads(out.read_text())
    assert rep.frames == round(2.5 * 24) + round(2.0 * 24) and rep.calibration_status == "UNCALIBRATED"
    assert any(w.startswith("UNCALIBRATED_AXES") for w in rep.warnings)
    nova = next(t for t in doc["timelines"] if t["name"] == "Nova")
    arm = next(t for t in doc["timelines"] if t.get("part_of") == nova["id"] and t["model_part_name"] == "right_arm")
    cam = next(t for t in doc["timelines"] if t["type"] == "camera")
    assert nova["keyframes"] and arm["keyframes"] and cam["keyframes"]
    for tl in doc["timelines"]:
        for kf in tl["keyframes"].values():
            assert set(kf) <= KNOWN_VALUES, set(kf) - KNOWN_VALUES
    # builder points at 0.35s in shot 1: the right arm must swing forward during the gesture
    swings = [abs(kf.get("ROT_X", 0)) for f, kf in arm["keyframes"].items() if 10 <= int(f) <= 40]
    assert max(swings) > 45
    # cuts are hard: the last keyframe of each shot is instant
    assert cam["keyframes"][str(round(2.5 * 24) - 1)]["TRANSITION"] == "instant"
    assert cam["keyframes"]["0"]["CAM_ROTATE"] is True and 10 < cam["keyframes"]["0"]["CAM_FOV"] < 90


def test_walk_moves_the_character(tmp_path):
    ep = _episode()
    shot = ep.shots[0].model_copy(update={"actions": [ep.shots[0].actions[0].model_copy(update={"clip_id": "walk", "start_seconds": 0.0, "end_seconds": 2.0})]})
    ep = ep.model_copy(update={"shots": [shot]})
    out = tmp_path / "walk.miproject"
    MineImatorExporter.from_root(ROOT).export(_compiled(ep), _template(tmp_path), out, actor_map={"builder": "Nova", "friend": "Pip"})
    nova = next(t for t in json.loads(out.read_text())["timelines"] if t["name"] == "Nova")
    k = nova["keyframes"]; first, last = k["0"], k[max(k, key=int)]
    moved = abs(last["POS_X"] - first["POS_X"]) + abs(last["POS_Y"] - first["POS_Y"])
    assert moved > 1.4 * 1.5 * 16 * 0.8  # ~2 s of walking at 1.4 blocks/s, in Mine-imator units


def test_audio_is_attached(tmp_path):
    wav = tmp_path / "ep_mix.wav"; wav.write_bytes(b"RIFF0000WAVE")
    out = tmp_path / "out" / "ep.miproject"
    rep = MineImatorExporter.from_root(ROOT).export(_compiled(), _template(tmp_path), out,
                                                     actor_map={"builder": "Nova", "friend": "Pip"}, audio_path=wav)
    doc = json.loads(out.read_text())
    assert rep.audio == "ep_mix.wav" and (out.parent / "ep_mix.wav").exists()
    assert next(r for r in doc["resources"] if r["id"] == "R9")["filename"] == "ep_mix.wav"


def test_unknown_character_names_the_fix(tmp_path):
    with pytest.raises(MineImatorError, match="--map builder="):
        MineImatorExporter.from_root(ROOT).export(_compiled(), _template(tmp_path), tmp_path / "x.miproject")


def test_every_library_clip_has_a_pose():
    clips = yaml.safe_load((ROOT / "config/block_animation/animations.yaml").read_text())["animations"]
    for c in clips:
        pose = clip_pose(c["clip_id"], 0.3, 0.4, 1.0)
        assert pose is not None, c["clip_id"]
    assert clip_pose("not_a_clip", 0, 0) is None
