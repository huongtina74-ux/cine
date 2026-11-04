"""Assemble web/index.html: shared core (renderer, pixel textures, mesher) from ep01 + this episode's world, cast and story."""
from pathlib import Path
src = Path('../ep01_nut_do/web/index.html').read_text(encoding='utf-8')
def cut(a, b):
    i = src.index(a); j = src.index(b, i)
    return src[i:j]
head = src[:src.index('<script>\n') + len('<script>\n')]
core = cut('const W=1920', '/* ---------- world ---------- */')
mesher = cut('// face-culled mesher', '\nfor(const x of[-1,0])')
web = Path('web')
parts = [head + core, (web / 'ep3.js').read_text(encoding='utf-8'), mesher, (web / 'ep3_chars.js').read_text(encoding='utf-8'), (web / 'ep3_story.js').read_text(encoding='utf-8')]
html = '\n'.join(parts)
(web / 'index.html').write_text(html, encoding='utf-8')
print('index.html', len(html))
