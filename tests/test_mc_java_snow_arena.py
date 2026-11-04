import importlib.util
import os
import re
import sys

HERE = os.path.join(os.path.dirname(__file__), '..', 'tools', 'mc_java')
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('gen_snow_arena', os.path.join(HERE, 'gen_snow_arena.py'))
ga = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ga)


def test_functions_fit_vanilla_limits(tmp_path):
    counts, n = ga.write(str(tmp_path))
    assert n >= 1500                                   # crowd size
    assert all(c < ga.MAX_CMDS for c in counts.values())
    text = '\n'.join(open(os.path.join(tmp_path, f + '.mcfunction')).read() for f in counts)
    # 1.21.9+ renamed chain -> iron_chain; a bare minecraft:chain makes the whole function fail to load
    assert not re.search(r'\s(minecraft:)?chain\[', text)
    for line in text.splitlines():
        if line.startswith('fill '):
            x0, y0, z0, x1, y1, z1 = map(int, line.split()[1:7])
            assert (abs(x1 - x0) + 1) * (abs(y1 - y0) + 1) * (abs(z1 - z0) + 1) <= 32768, line


def test_layout_has_gate_towers_keep_and_aisle():
    ga.build_all()
    v = ga.V
    assert (ga.AX, ga.G + 2, ga.AZ - 64) not in v                     # gate is open
    spires = [k for k, b in v.items() if b == 'lightning_rod']
    assert len(spires) == 10 + 4 + 1                                  # 10 wall towers, 4 turrets, donjon
    assert any(b == 'iron_chain[axis=x]' or b == 'iron_chain[axis=z]' for b in v.values())
    crowd, _ = ga.crowd()
    xs = [float(c.split()[2]) for c in crowd if c.startswith('summon') and 'arenacrowd' in c and 'profile' not in c]
    assert all(abs(x - ga.AX) >= 2.6 for x in xs)                     # aisle stays clear
