"""Original face-part textures for Bin, Bo, Zu (method D from the tutorial study: textured surfaces on the head).

Each PNG is 32x32 and covers the whole 8x8 front of the head (4 texels per skin pixel), transparent elsewhere.
Layers (separate surfaces, separate keyframe channels): eyes, pupils, brows, mouth.
Usage: python faces.py OUT_DIR
"""
import os
import sys

from PIL import Image, ImageDraw

S = 32
W = (255, 255, 255, 255)
K = (28, 22, 26, 255)
M = (118, 28, 42, 255)      # mouth inside
TG = (226, 96, 110, 255)    # tongue
TEAR = (110, 190, 255, 230)
CRUMB = (214, 160, 72, 255)
BLUSH = (255, 120, 140, 150)
HEART_C = (255, 70, 130, 255)
# 8x9 pixel heart, w = glint
HEART = ['.##..##.', '#w######', '#w######', '########', '.######.', '..####..', '...##...', '........', '........']

CH = {
    'bin': dict(skin=(244, 196, 160), hair=(214, 110, 40), iris=(52, 140, 74)),
    'bo': dict(skin=(196, 140, 100), hair=(36, 30, 34), iris=(92, 58, 34)),
    'zu': dict(skin=(140, 206, 120), hair=(96, 150, 84), iris=(40, 40, 48)),
}
# eye white boxes (x0, y0, x1, y1) in texels, character's right eye is on the image left
EYE_R = (3, 12, 11, 21)
EYE_L = (21, 12, 29, 21)


def canvas():
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def shade(c, f, a=255):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (a,)


# ---------------- eyes (white + lids) ----------------
def eyes(state, c):
    im, d = canvas()
    skin = c['skin'] + (255,)
    lid = shade(c['skin'], .82)
    for (x0, y0, x1, y1), side in ((EYE_R, 1), (EYE_L, -1)):
        if state in ('open', 'wide', 'half', 'sad', 'angry', 'cry'):
            yy0 = y0 - 2 if state == 'wide' else y0
            d.rectangle((x0, yy0, x1 - 1, y1 - 1), fill=W)
            d.rectangle((x0, yy0, x1 - 1, yy0), fill=K)          # lash line
            if state == 'half':
                d.rectangle((x0, y0, x1 - 1, y0 + 4), fill=lid)
                d.rectangle((x0, y0 + 4, x1 - 1, y0 + 4), fill=K)
            if state in ('sad', 'cry'):   # inner corner raised -> lid slants down to the outside
                for i in range(x1 - x0):
                    k = i if side == 1 else (x1 - x0 - 1 - i)
                    h = max(0, (x1 - x0 - 1 - k) // 2)          # outer side covered more
                    if h:
                        d.rectangle((x0 + i, y0, x0 + i, y0 + h), fill=lid)
            if state == 'angry':          # inner corner pushed down
                for i in range(x1 - x0):
                    k = i if side == 1 else (x1 - x0 - 1 - i)
                    h = max(0, k // 2)
                    if h:
                        d.rectangle((x0 + i, y0, x0 + i, y0 + h), fill=lid)
            if state == 'cry':
                tx = x0 + 1 if side == 1 else x1 - 3
                d.rectangle((tx, y1, tx + 1, S - 4), fill=TEAR)
        elif state == 'closed':
            d.rectangle((x0, y1 - 4, x1 - 1, y1 - 3), fill=K)
        elif state == 'happy':      # ^ ^
            mid = (x0 + x1) // 2
            for i in range(x0, x1):
                yy = y0 + 3 + abs(i - mid) // 1
                d.rectangle((i, min(yy, y1 - 2), i, min(yy, y1 - 2) + 1), fill=K)
            d.ellipse((x0 - 1, y1 + 1, x0 + 5, y1 + 4), fill=BLUSH) if side == 1 else d.ellipse((x1 - 5, y1 + 1, x1 + 1, y1 + 4), fill=BLUSH)
        elif state == 'heart':      # love-struck: pink pixel hearts with a white glint (pupils hidden)
            for yy, row in enumerate(HEART):
                for xx, ch in enumerate(row):
                    if ch != '.':
                        d.point((x0 + xx, y0 - 1 + yy), fill={'#': HEART_C, 'w': W, 'k': K}[ch])
        elif state == 'sparkle':    # huge glossy iris with big glints (anime "want it!"), pupils hidden
            d.rectangle((x0, y0 - 2, x1 - 1, y1 - 1), fill=W)
            d.rectangle((x0, y0 - 2, x1 - 1, y0 - 2), fill=K)
            iris = shade(c['iris'], 1.6) if sum(c['iris']) < 200 else c['iris'] + (255,)
            d.rectangle((x0 + 1, y0 - 1, x1 - 2, y1 - 1), fill=iris)
            d.rectangle((x0 + 3, y0 + 2, x1 - 4, y1 - 3), fill=K)
            d.rectangle((x0 + 1, y0 - 1, x0 + 3, y0 + 1), fill=W)
            d.rectangle((x1 - 3, y1 - 3, x1 - 2, y1 - 2), fill=W)
        elif state == 'squeeze':    # > <  (joy / effort), pupils hidden; point of the chevron faces the nose
            mid = (y0 + y1) // 2
            for i in range(4):
                xa = (x0 + 1 + 2 * i) if side == 1 else (x1 - 3 - 2 * i)
                d.rectangle((xa, mid - 3 + i, xa + 1, mid - 2 + i), fill=K)
                d.rectangle((xa, mid + 3 - i, xa + 1, mid + 4 - i), fill=K)
        elif state == 'dot':        # blank shock: tiny black dots on the skin
            cx_, cy_ = (x0 + x1) // 2, (y0 + y1) // 2
            d.rectangle((cx_ - 1, cy_ - 1, cx_, cy_), fill=K)
        elif state == 'popped':     # eyes bulging out: oversized whites, pin-prick pupil drawn in (pupils hidden)
            d.rectangle((x0 - 1, y0 - 3, x1, y1 + 1), fill=W)
            d.rectangle((x0 - 1, y0 - 3, x1, y0 - 3), fill=K)
            cx_, cy_ = (x0 + x1) // 2, (y0 + y1) // 2
            d.rectangle((cx_ - 1, cy_ - 1, cx_, cy_), fill=K)
    return im


def pupils(c, size='normal'):
    im, d = canvas()
    w, h = {'normal': (4, 6), 'big': (5, 7), 'small': (2, 4)}[size]
    for (x0, y0, x1, y1) in (EYE_R, EYE_L):
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 1
        d.rectangle((cx - w // 2, cy - h // 2, cx - w // 2 + w - 1, cy - h // 2 + h - 1), fill=c['iris'] + (255,))
        d.rectangle((cx - 1, cy - h // 2 + 1, cx, cy + h // 2 - 2), fill=K)
        d.point((cx - w // 2, cy - h // 2), fill=W)                  # highlight
    return im


# ---------------- brows ----------------
def brows(state, c):
    im, d = canvas()
    col = shade(c['hair'], .8)
    for (x0, y0, x1, y1), side in ((EYE_R, 1), (EYE_L, -1)):
        for i in range(x0, x1):
            k = (i - x0) if side == 1 else (x1 - 1 - i)         # 0 at outer edge .. 7 at inner edge
            base = {'neutral': 9, 'raised': 8, 'angry': 8 + k // 3, 'sad': 10 - k // 3,
                    'curious': 8 if side == 1 else 10, 'worried': 10 - k // 4}[state]
            d.rectangle((i, base, i, base + 1), fill=col)
    return im


# ---------------- mouth ----------------
def mouth(state, c):
    im, d = canvas()
    cx, y = 16, 25
    if state == 'rest':
        d.rectangle((cx - 3, y, cx + 2, y + 1), fill=K)
    elif state == 'smile':
        d.rectangle((cx - 3, y + 1, cx + 2, y + 2), fill=K)
        d.rectangle((cx - 5, y - 1, cx - 4, y), fill=K)
        d.rectangle((cx + 3, y - 1, cx + 4, y), fill=K)
    elif state == 'frown':
        d.rectangle((cx - 3, y, cx + 2, y + 1), fill=K)
        d.rectangle((cx - 5, y + 2, cx - 4, y + 3), fill=K)
        d.rectangle((cx + 3, y + 2, cx + 4, y + 3), fill=K)
    elif state.startswith('open'):              # open1..open3: graded by loudness
        n = int(state[-1])
        hh = (2, 4, 6)[n - 1]
        ww = (3, 4, 5)[n - 1]
        d.rectangle((cx - ww, y - 1, cx + ww - 1, y - 1 + hh), fill=M)
        if n >= 2:
            d.rectangle((cx - ww + 1, y - 1, cx + ww - 2, y - 1), fill=W)   # top teeth
        if n == 3:
            d.rectangle((cx - 2, y + hh - 3, cx + 1, y + hh - 2), fill=TG)
    elif state == 'oh':
        d.ellipse((cx - 3, y - 2, cx + 2, y + 4), fill=M)
    elif state.startswith('grin'):              # happy talking: wide smile, grin1..grin3
        n = int(state[-1])
        hh = (2, 3, 5)[n - 1]
        d.rectangle((cx - 5, y - 1, cx + 4, y - 1 + hh), fill=M)
        d.rectangle((cx - 5, y - 1, cx + 4, y - 1), fill=W)
        d.rectangle((cx - 6, y - 2, cx - 6, y - 1), fill=K)
        d.rectangle((cx + 5, y - 2, cx + 5, y - 1), fill=K)
    elif state.startswith('wail'):              # crying talk: wide open frown, wail1..wail3
        n = int(state[-1])
        hh = (2, 4, 6)[n - 1]
        d.rectangle((cx - 4, y, cx + 3, y + hh), fill=M)
        d.rectangle((cx - 5, y + hh - 1, cx - 5, y + hh + 1), fill=K)
        d.rectangle((cx + 4, y + hh - 1, cx + 4, y + hh + 1), fill=K)
    elif state == 'drool':                       # dreamy open smile, tongue out, drool drop at the corner
        d.rectangle((cx - 4, y - 1, cx + 3, y + 2), fill=M)
        d.rectangle((cx - 4, y - 1, cx + 3, y - 1), fill=W)
        d.rectangle((cx - 2, y + 1, cx + 1, y + 4), fill=TG)
        d.rectangle((cx + 4, y + 1, cx + 4, y + 5), fill=TEAR)
        d.rectangle((cx + 3, y + 5, cx + 5, y + 6), fill=TEAR)
    elif state == 'scream':                      # huge shocked mouth, teeth + tongue
        d.rectangle((cx - 5, y - 3, cx + 4, y + 5), fill=M)
        d.rectangle((cx - 4, y - 3, cx + 3, y - 2), fill=W)
        d.rectangle((cx - 3, y + 3, cx + 2, y + 5), fill=TG)
    elif state == 'wavy':                        # awkward / nervous ~~~
        for i in range(-5, 5):
            d.rectangle((cx + i, y + (i % 2), cx + i, y + (i % 2)), fill=K)
    elif state.startswith('chew'):               # cheeks full: closed wide mouth moving, crumbs
        n = int(state[-1])
        if n == 1:
            d.rectangle((cx - 4, y, cx + 3, y + 1), fill=K)
        else:
            d.rectangle((cx - 3, y - 1, cx + 2, y + 1), fill=M)
            d.rectangle((cx - 3, y - 1, cx + 2, y - 1), fill=K)
        for px, py in ((cx - 6, y + 2), (cx + 5, y - 1), (cx + 1, y + 3)):
            d.point((px, py), fill=CRUMB)
    return im


EYE_STATES = ['open', 'half', 'closed', 'happy', 'sad', 'angry', 'wide', 'cry', 'heart', 'sparkle', 'squeeze', 'dot', 'popped']
NO_PUPIL = {'closed', 'happy', 'heart', 'sparkle', 'squeeze', 'dot', 'popped'}   # eye states that draw their own pupils
BROW_STATES = ['neutral', 'raised', 'angry', 'sad', 'curious', 'worried']
MOUTH_STATES = ['rest', 'smile', 'frown', 'oh', 'open1', 'open2', 'open3', 'grin1', 'grin2', 'grin3', 'wail1', 'wail2', 'wail3',
                'drool', 'scream', 'wavy', 'chew1', 'chew2']


def faceless_skin(src_png, dst_png, c):
    """Copy a 64x64 skin and wipe the eyes/mouth area of the front face (keeps the hair rows)."""
    im = Image.open(src_png).convert('RGBA')
    d = ImageDraw.Draw(im)
    d.rectangle((8, 10, 15, 15), fill=c['skin'] + (255,))
    im.save(dst_png)


def main(out):
    os.makedirs(out, exist_ok=True)
    n = 0
    for name, c in CH.items():
        for s in EYE_STATES:
            eyes(s, c).save(f'{out}/{name}_eyes_{s}.png'); n += 1
        for s in ('normal', 'big', 'small'):
            pupils(c, s).save(f'{out}/{name}_pupils_{s}.png'); n += 1
        for s in BROW_STATES:
            brows(s, c).save(f'{out}/{name}_brows_{s}.png'); n += 1
        for s in MOUTH_STATES:
            mouth(s, c).save(f'{out}/{name}_mouth_{s}.png'); n += 1
    print(f'FACES_OK::{n}')


if __name__ == '__main__':
    main(sys.argv[1])
