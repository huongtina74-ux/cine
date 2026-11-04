import importlib.util
import os

import numpy as np
from PIL import Image

_spec = importlib.util.spec_from_file_location(
    'cinegrade', os.path.join(os.path.dirname(__file__), '..', 'tools', 'mc_java', 'cinegrade.py'))
cg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cg)


def _frame():
    a = np.zeros((90, 160, 3), np.uint8)
    a[:30] = (140, 180, 240)          # sky
    a[30:] = (90, 90, 95)             # stone
    a[60:64, 78:82] = (255, 220, 120)  # a lantern
    return Image.fromarray(a)


def test_all_presets_keep_size_and_glow_lights():
    src = _frame()
    for p in cg.PRESETS:
        out = np.asarray(cg.grade(src, p))
        assert out.shape == (90, 160, 3)
        ring = out[56:68, 74:86].astype(float).mean() - out[80:88, 10:20].astype(float).mean()
        assert ring > 10, p                       # bloom spreads light around the lantern


def test_bars_are_2_39_letterbox():
    out = np.asarray(cg.grade(_frame(), 'day', bars=True))
    bh = int(round((90 - 160 / 2.39) / 2))
    assert out[:bh].max() == 0 and out[-bh:].max() == 0
