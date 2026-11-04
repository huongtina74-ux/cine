import importlib.util
import math
import os

_spec = importlib.util.spec_from_file_location(
    'gen_mountains', os.path.join(os.path.dirname(__file__), '..', 'tools', 'mc_java', 'gen_mountains.py'))
gm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gm)


def test_ring_is_flat_inside_and_outside():
    assert gm.height(gm.CX, gm.CZ) == 0
    assert gm.height(gm.CX + gm.R_IN - 2, gm.CZ) == 0
    assert gm.height(gm.CX + gm.R_OUT + 2, gm.CZ) == 0


def test_no_vertical_outer_wall_and_smooth_surface():
    # the old stripes came from big jumps between neighbours; 1x1 noise keeps most steps small
    steps = []
    for a in range(0, 360, 3):
        for r in range(gm.R_IN, gm.R_OUT):
            x = round(gm.CX + r * math.cos(math.radians(a)))
            z = round(gm.CZ + r * math.sin(math.radians(a)))
            steps.append(abs(gm.height(x, z) - gm.height(x + 1, z)))
    steps.sort()
    assert steps[len(steps) // 2] <= 2
    assert steps[int(len(steps) * .9)] <= 4
    edge = [gm.height(round(gm.CX + (gm.R_OUT - 1) * math.cos(t / 10)), round(gm.CZ + (gm.R_OUT - 1) * math.sin(t / 10)))
            for t in range(63)]
    assert max(edge) <= 3


def test_peaks_are_tall_and_materials_mixed(tmp_path):
    counts = gm.write(str(tmp_path))
    assert set(counts) == {'mtn_0.mcfunction', 'mtn_1.mcfunction', 'mtn_2.mcfunction', 'mtn_3.mcfunction', 'mtn_trees.mcfunction'}
    assert all(n < gm.MAX_CMDS for n in counts.values())
    text = ''.join(open(os.path.join(tmp_path, f)).read() for f in counts)
    for block in ('grass_block', 'andesite', 'tuff', 'snow_block', 'place feature minecraft:'):
        assert block in text
    tops = [int(line.split()[2]) for line in text.splitlines() if line.startswith('setblock')]
    assert max(tops) - gm.G >= 30
