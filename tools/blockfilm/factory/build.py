"""Assemble a vertical (1080x1920) "Who can …?" Short page from one SPEC file.

    python build.py specs/s02_tower.json OUT_DIR      # -> OUT_DIR/web/index.html (+ node_modules link)

Shared pieces are reused, not copied by hand:
- the core (renderer, pixel textures, materials) from ep01;
- the cast (Bin, Bo, Zu, rig, faces, poses) from ep03;
- the arena (factory/web/world.js, voxel AO mesher) and the contest engine (factory/web/contest.js).
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BF = HERE.parent


def build(spec_path, out_dir):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    for k in ('id', 'title', 'challenge', 'lanes', 'attempts'):
        assert k in spec, f'SPEC missing {k}'
    assert spec['challenge'] in ('launch', 'pillar'), spec['challenge']
    assert len(spec['attempts']) == 3 and len(spec['title']) == 2
    src = (BF / 'ep01_nut_do/web/index.html').read_text(encoding='utf-8')

    def cut(a, b):
        i = src.index(a); j = src.index(b, i)
        return src[i:j]

    head = src[:src.index('<script>\n') + len('<script>\n')]
    head = head.replace('width:1920px;height:1080px', 'width:1080px;height:1920px').replace('width="1920" height="1080"', 'width="1080" height="1920"')
    core = cut('const W=1920', '/* ---------- world ---------- */').replace('const W=1920,H=1080', 'const W=1080,H=1920')
    chars = (BF / 'ep03_zombie_outbreak/web/ep3_chars.js').read_text(encoding='utf-8')
    parts = [head, 'const SPEC=' + json.dumps(spec, ensure_ascii=False) + ';', core,
             (HERE / 'web/world.js').read_text(encoding='utf-8'), chars,
             (HERE / 'web/contest.js').read_text(encoding='utf-8'), '</script>\n</body></html>\n']
    html = '\n'.join(parts)
    assert 'width="1080" height="1920"' in html and 'const W=1080,H=1920' in html
    web = Path(out_dir) / 'web'
    web.mkdir(parents=True, exist_ok=True)
    (web / 'index.html').write_text(html, encoding='utf-8')
    nm = web / 'node_modules'
    if not nm.exists():
        os.symlink(BF / 'ep03_zombie_outbreak/web/node_modules', nm)
    return web / 'index.html'


if __name__ == '__main__':
    p = build(sys.argv[1], sys.argv[2])
    print('BUILD_OK', p)
