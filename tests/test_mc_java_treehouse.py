import importlib.util
import os
import re
import sys

HERE = os.path.join(os.path.dirname(__file__), '..', 'tools', 'mc_java')
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('gen_treehouse', os.path.join(HERE, 'gen_treehouse.py'))
gt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gt)


def test_functions_fit_limits_and_use_valid_names(tmp_path):
    counts = gt.write(str(tmp_path))
    assert all(n < gt.MAX_CMDS for n in counts.values())
    text = '\n'.join(open(os.path.join(tmp_path, f + '.mcfunction')).read() for f in counts)
    assert not re.search(r'\s(minecraft:)?chain\[', text)                 # 26.x name is iron_chain
    assert 'leaves[persistent=true]' in text and 'leaves ' not in text.replace('leaves[', 'leaves[')  # no decaying leaves
    for line in text.splitlines():
        if line.startswith('fill '):
            x0, y0, z0, x1, y1, z1 = map(int, line.split()[1:7])
            assert (abs(x1 - x0) + 1) * (abs(y1 - y0) + 1) * (abs(z1 - z0) + 1) <= 32768, line


def test_cast_stands_on_the_first_deck_and_horde_is_outside_the_wall():
    gt.build_all()
    cast = gt.cast()
    for c in cast:
        if 'mannequin' in c:
            x, y, z = (float(v) for v in c.split()[2:5])
            assert gt.V.get((round(x), int(y) - 1, round(z)), '').startswith(('spruce_planks', 'stripped_spruce'))
        elif c.startswith('summon'):
            x, z = float(c.split()[2]), float(c.split()[4])
            assert ((x - gt.TX) ** 2 + (z - gt.TZ) ** 2) ** .5 > gt.PAL_R
