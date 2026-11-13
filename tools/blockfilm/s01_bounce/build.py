"""Assemble web/index.html for the 9:16 Short: shared core + mesher from ep01, cast from ep03, this Short's world and story."""
from pathlib import Path
src = Path('../ep01_nut_do/web/index.html').read_text(encoding='utf-8')
def cut(a, b):
    i = src.index(a); j = src.index(b, i)
    return src[i:j]
head = src[:src.index('<script>\n') + len('<script>\n')]
core = cut('const W=1920', '/* ---------- world ---------- */')
mesher = cut('// face-culled mesher', '\nfor(const x of[-1,0])')
# vertical 1080x1920
head = head.replace('width:1920px;height:1080px', 'width:1080px;height:1920px').replace('width="1920" height="1080"', 'width="1080" height="1920"')
core = core.replace('const W=1920,H=1080', 'const W=1080,H=1920')
web = Path('web')
chars = Path('../ep03_zombie_outbreak/web/ep3_chars.js').read_text(encoding='utf-8')
parts = [head + core, (web / 's01.js').read_text(encoding='utf-8'), mesher, chars, (web / 's01_story.js').read_text(encoding='utf-8'), '</script>\n</body></html>\n']
html = '\n'.join(parts)
assert 'width="1080" height="1920"' in html and 'const W=1080,H=1920' in html
(web / 'index.html').write_text(html, encoding='utf-8')
print('index.html', len(html))
