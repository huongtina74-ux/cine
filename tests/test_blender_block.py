"""Blender block rig + Zu pizza test scene (needs the `bpy` wheel: pip install bpy==5.2.3; skipped otherwise)."""
import os
import subprocess
import sys

import pytest

bpy = pytest.importorskip('bpy')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'blender_block'))
import rig  # noqa: E402


def test_uv_rects_follow_the_minecraft_skin_layout():
    r = rig._uvbox(0, 0, 8, 8, 8)            # head
    assert r['front'] == (8, 8, 16, 16) and r['top'] == (8, 0, 16, 8) and r['back'] == (24, 8, 32, 16)
    r = rig._uvbox(40, 16, 4, 12, 4)         # right arm
    assert r['front'] == (44, 20, 48, 32) and r['right'] == (40, 20, 44, 32)


def test_rig_builds_and_face_keys_are_constant(tmp_path):
    from PIL import Image
    bpy.ops.wm.read_factory_settings(use_empty=True)
    skin = tmp_path / 'skin.png'
    Image.new('RGBA', (64, 64), (120, 200, 120, 255)).save(skin)
    face = tmp_path / 'face'
    face.mkdir()
    for layer, states in rig.LAYERS.items():
        for s in states:
            Image.new('RGBA', (32, 32), (255, 255, 255, 255 if s != 'none' else 0)).save(face / f't_{layer}_{s}.png')
    R = rig.build('t', str(skin), str(face), str(tmp_path), k=1 / 32)
    for part in ('head', 'body', 'armR', 'armL', 'legR', 'legL'):
        assert R[part].parent is not None
    # head front face is at -Y and the face planes sit just in front of it
    assert all(p.location.y < -4 / 32 for p in R['face'].values())
    rig.set_face(R, 1, eyes='open')
    rig.set_face(R, 10, eyes='heart')
    nt = R['face']['eyes'].data.materials[0].node_tree
    kps = [kp for fc in rig.fcurves(nt) for kp in fc.keyframe_points]
    assert len(kps) == 2 and all(kp.interpolation == 'CONSTANT' for kp in kps)
    pup = R['face']['pupils'].data.materials[0].node_tree
    loc = pup.nodes['TILE'].inputs['Location']
    bpy.context.scene.frame_set(10)
    assert abs(loc.default_value[0] - rig.LAYERS['pupils'].index('none') / len(rig.LAYERS['pupils'])) < 1e-6


@pytest.mark.slow
def test_zu_pizza_builds_and_the_hand_reaches_the_slice(tmp_path):
    out = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'blender_block', 'zu_pizza', 'build.py'), str(tmp_path)],
                         capture_output=True, text=True, timeout=900)
    assert out.returncode == 0, out.stderr[-2000:]
    import json
    rep = json.load(open(tmp_path / 'build_report.json'))
    grab = [e for e in rep['arm_solve'] if e['frame'] == 126][0]
    assert grab['hand_mm'] < 25                          # hand really on the crust
    assert all(e.get('tip_mm', 0) < 10 for e in rep['arm_solve'])   # slice tip on target (mouth at the bite)
    assert len(rep['cams']) == 6 and rep['frames'] == 240
