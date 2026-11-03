"""Original 2D effect textures for scene 03 (cartoon emotion marks and props), all drawn here in code.

Effects were chosen after a frame-by-frame look at the competitor benchmark (reports/research/
2026-11-03_expression_camera_study.md): blush, sweat drop, "!" / "?" pop-ups, floating hearts, sparkles,
crumbs and steam, plus a top-view pizza for the hero prop and a solid pink for the 3D cheek blocks.
Usage: python fx.py OUT_DIR
"""
import math
import os
import sys

from PIL import Image, ImageDraw

K = (28, 22, 26, 255)
W = (255, 255, 255, 255)


def blank(s=32):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def blush():
    """Face layer (same 32x32 face grid as faces.py): two soft pink ovals under the eyes + 3 hatch lines."""
    im, d = blank()
    for x0 in (2, 21):
        d.ellipse((x0, 21, x0 + 9, 25), fill=(255, 110, 140, 170))
        for k in range(3):
            d.line((x0 + 2 + 2 * k, 24, x0 + 3 + 2 * k, 22), fill=(230, 70, 110, 220))
    return im


def sweat():
    im, d = blank()
    d.polygon([(16, 3), (24, 18), (16, 28), (8, 18)], fill=(120, 200, 255, 235))
    d.ellipse((8, 12, 24, 28), fill=(120, 200, 255, 235))
    d.ellipse((11, 15, 15, 19), fill=W)
    d.line([(16, 3), (24, 18)], fill=(40, 110, 200, 255), width=1)
    return im


def mark(ch):
    """'!' or '?' pop-up: bold glyph with a white outline, drawn on a 16x16 pixel grid then scaled."""
    glyph = {'!': ['..####..', '..####..', '..####..', '..####..', '...##...', '...##...', '........', '..####..', '..####..'],
             '?': ['.######.', '##....##', '......##', '....###.', '...##...', '...##...', '........', '...##...', '...##...']}[ch]
    col = (240, 40, 40, 255) if ch == '!' else (255, 200, 30, 255)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(glyph):
        for x, c in enumerate(row):
            if c == '#':
                px[x + 4, y + 3] = col
    out = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            if px[x, y][3] == 0 and any(0 <= x + dx < 16 and 0 <= y + dy < 16 and px[x + dx, y + dy][3]
                                        for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                out.putpixel((x, y), W)
    out.alpha_composite(im)
    return out.resize((32, 32), Image.NEAREST)


def heart():
    rows = ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...']
    im = Image.new('RGBA', (9, 8), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == '#':
                im.putpixel((x + 1, y + 1), (255, 60, 120, 255))
    im.putpixel((2, 2), W)
    return im.resize((36, 32), Image.NEAREST)


def sparkle():
    im, d = blank()
    c = (255, 230, 90, 255)
    d.polygon([(16, 1), (19, 13), (31, 16), (19, 19), (16, 31), (13, 19), (1, 16), (13, 13)], fill=c)
    d.rectangle((14, 14, 17, 17), fill=W)
    return im


def crumb():
    im, d = blank(8)
    d.rectangle((1, 1, 6, 6), fill=(214, 160, 72, 255))
    d.rectangle((1, 1, 3, 3), fill=(240, 200, 120, 255))
    return im


def steam():
    im, d = blank()
    for (x, y, r) in ((12, 18, 8), (19, 14, 7), (15, 9, 6)):
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 110))
    return im


def pizza(s=64):
    """Top view, pixel-art pizza: crust ring, sauce edge, cheese, pepperoni, basil."""
    im, d = blank(s)
    c = s / 2
    d.ellipse((1, 1, s - 2, s - 2), fill=(196, 130, 58, 255))          # crust
    d.ellipse((6, 6, s - 7, s - 7), fill=(206, 62, 40, 255))           # sauce rim
    d.ellipse((8, 8, s - 9, s - 9), fill=(255, 208, 92, 255))          # cheese
    for a in range(6):                                                  # slice cuts
        x = c + math.cos(a * math.pi / 3) * (c - 7)
        y = c + math.sin(a * math.pi / 3) * (c - 7)
        d.line((c, c, x, y), fill=(230, 176, 70, 255), width=1)
    for (x, y) in ((22, 20), (40, 18), (46, 36), (30, 34), (18, 42), (36, 48), (26, 27)):
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(170, 30, 36, 255))
        d.point((x - 2, y - 2), fill=(220, 90, 90, 255))
    for (x, y) in ((33, 24), (21, 33), (43, 44), (14, 28)):
        d.rectangle((x, y, x + 2, y + 1), fill=(60, 140, 50, 255))
    return im


def solid(rgb):
    return Image.new('RGBA', (4, 4), rgb + (255,))


FX = {'blush': blush, 'sweat': sweat, 'mark_excl': lambda: mark('!'), 'mark_q': lambda: mark('?'),
      'heart': heart, 'sparkle': sparkle, 'crumb': crumb, 'steam': steam, 'pizza': pizza,
      'cheek_pink': lambda: solid((255, 150, 170)), 'cheek_zu': lambda: solid((150, 214, 128))}


def main(out):
    os.makedirs(out, exist_ok=True)
    for k, f in FX.items():
        f().save(os.path.join(out, f'fx_{k}.png'))
    print(f'FX_OK::{len(FX)}')


if __name__ == '__main__':
    main(sys.argv[1])
