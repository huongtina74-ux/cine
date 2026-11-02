"""Assemble web/index.html: shared core (renderer, pixel textures, mesher) from ep01 + this episode's world and story."""
from pathlib import Path
src = Path('../ep01_nut_do/web/index.html').read_text(encoding='utf-8')
def cut(a, b):
    i = src.index(a); j = src.index(b, i)
    return src[i:j]
head = src[:src.index('<script>\n') + len('<script>\n')]
core = cut('const W=1920', '/* ---------- world ---------- */')
mesher = cut('// face-culled mesher', '\nfor(const x of[-1,0])')
web = Path('web')
html = head + core + (web / 'ep2.js').read_text(encoding='utf-8') + '\n' + mesher + '\n' + (web / 'ep2_rest.js').read_text(encoding='utf-8')
(web / 'index.html').write_text(html, encoding='utf-8')
print('index.html', len(html))
