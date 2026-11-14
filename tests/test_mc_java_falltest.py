import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, '..', 'tools', 'mc_java', 'falltest', 'gen_falltest.py')


def test_falltest_functions(tmp_path):
    out = subprocess.run([sys.executable, GEN, str(tmp_path)], capture_output=True, text=True, check=True).stdout
    assert 'FALLTEST_OK' in out
    names = {p.name for p in tmp_path.iterdir()}
    assert {'ft_build.mcfunction', 'ft_actors.mcfunction', 'ft_go.mcfunction', 'ft_end.mcfunction', 'ft_report.mcfunction'} <= names
    assert all(f'ft_l{i}.mcfunction' in names for i in range(6))
    build = (tmp_path / 'ft_build.mcfunction').read_text()
    # every fill stays under Minecraft's 32768-block limit
    for line in build.splitlines():
        if line.startswith('fill '):
            x0, y0, z0, x1, y1, z1 = map(int, line.split()[1:7])
            assert (abs(x1 - x0) + 1) * (abs(y1 - y0) + 1) * (abs(z1 - z0) + 1) <= 32768, line
    assert 'iron_chain' not in build or ' chain' not in build
