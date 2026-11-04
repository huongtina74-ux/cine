"""Cinematic grade for vanilla Minecraft frames (no shader mod needed).

What the shader packs add that vanilla lacks: atmospheric haze, bloom on lights, sun shafts, filmic
contrast, colour split-toning, vignette. This adds all of them in post, per frame:

    python tools/mc_java/cinegrade.py IN.png OUT.png --preset dusk [--bars]
Presets: day, golden, dusk, night. Works on stills; the same function runs per frame for video.
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter

PRESETS = {
    #          haze  bloom  warm   teal   contrast sat   vign  lift   rays
    'day':    (0.18, 0.30, 0.025, 0.020, 1.10, 1.08, 0.30, 0.00, 0.00),
    'golden': (0.22, 0.45, 0.070, 0.035, 1.12, 1.12, 0.38, 0.00, 0.55),
    'dusk':   (0.16, 0.70, 0.055, 0.050, 1.14, 1.15, 0.42, 0.03, 0.00),
    'night':  (0.08, 0.95, 0.045, 0.060, 1.10, 1.10, 0.45, 0.07, 0.00),
}


def _blur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255


def _horizon_row(a):
    """Lowest row of the sky: the sky is bright, low-saturation-variance and starts at the top."""
    lum = a.mean(2)
    top = np.median(a[: max(2, a.shape[0] // 12)].reshape(-1, 3), 0)
    diff = np.abs(a - top).mean(2)
    rows = (diff < 0.08).mean(1)
    sky = np.where(rows > 0.55)[0]
    return int(sky.max()) if len(sky) else int(a.shape[0] * 0.3), top, lum


def grade(img, preset='golden', bars=False, seed=0):
    haze, bloom, warm, teal, con, sat, vig, lift, rays = PRESETS[preset]
    a = np.asarray(img.convert('RGB'), dtype=np.float32) / 255
    h, w, _ = a.shape
    # 1. levels
    hi = np.percentile(a, 99.6)
    a = np.clip(a / max(hi, 0.35) * 0.97, 0, 1)
    if lift:
        a = a + lift * (1 - a) ** 3
    # 2. aerial haze, strongest at the horizon, fading toward the camera
    yh, sky, lum = _horizon_row(a)
    y = np.arange(h, dtype=np.float32)[:, None, None]
    wgt = np.exp(-((y - yh) / (0.20 * h)) ** 2) * (y >= yh * 0.6)
    a = a * (1 - haze * wgt) + sky[None, None, :] * haze * wgt
    # 3. bloom on bright things (lanterns, sun, snow highlights)
    l = a.mean(2, keepdims=True)
    bright = np.clip((l - 0.72) / 0.28, 0, 1) * a
    glow = _blur(bright, w / 90) * 0.6 + _blur(bright, w / 30) * 0.4
    a = 1 - (1 - a) * (1 - bloom * glow)            # screen blend
    # 4. sun shafts: radial blur of the bright mask from the brightest point in the sky
    if rays:
        sm = _blur(bright.mean(2, keepdims=True).repeat(3, 2), 6)[..., 0]
        sy, sx = np.unravel_index(np.argmax(sm[: max(1, yh)]), sm[: max(1, yh)].shape)
        acc = np.zeros_like(a)
        src = Image.fromarray(np.clip(bright * 255, 0, 255).astype(np.uint8))
        n = 24
        for k in range(n):
            s = 1 + 0.035 * k
            im = src.resize((int(w * s), int(h * s)), Image.BILINEAR)
            ox, oy = int(sx * (s - 1)), int(sy * (s - 1))
            acc += np.asarray(im.crop((ox, oy, ox + w, oy + h)), dtype=np.float32) / 255 * (1 - k / n)
        acc /= n / 2
        a = 1 - (1 - a) * (1 - rays * np.clip(acc, 0, 1) * np.array([1.0, 0.85, 0.6], dtype=np.float32))
    # 5. split toning: teal shadows, warm highlights
    l = a.mean(2, keepdims=True)
    a = a + np.array([-0.4, 0.15, 1.0], dtype=np.float32) * teal * (1 - l) ** 2 \
          + np.array([1.0, 0.45, -0.6], dtype=np.float32) * warm * l ** 2
    # 6. filmic contrast + saturation
    a = np.clip(a, 0, 1)
    s_curve = a * a * (3 - 2 * a)
    a = a + (s_curve - a) * (con - 1) * 4
    l = a.mean(2, keepdims=True)
    a = l + (a - l) * sat
    # 7. vignette + grain
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    a = a * (1 - vig * 0.5 * r2[..., None])
    a = a + np.random.default_rng(seed).normal(0, 0.008, a.shape).astype(np.float32)
    a = np.clip(a, 0, 1)
    if bars:                                         # 2.39:1 letterbox inside a 16:9 frame
        bh = int(round((h - w / 2.39) / 2))
        a[:bh] = 0
        a[h - bh:] = 0
    return Image.fromarray((a * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--preset', default='golden', choices=sorted(PRESETS))
    ap.add_argument('--bars', action='store_true')
    o = ap.parse_args()
    grade(Image.open(o.src), o.preset, o.bars).save(o.dst)
    print('GRADE_OK', o.dst)
