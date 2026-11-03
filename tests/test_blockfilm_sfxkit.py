"""blockfilm sound kit: every sound renders, is finite, short and within peak."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "blockfilm"))
import sfxkit  # noqa: E402


@pytest.mark.parametrize("name", sorted(sfxkit.SOUNDS))
def test_sound_renders(name):
    x = sfxkit.SOUNDS[name]()
    assert x.dtype == np.float32 and x.ndim == 1
    assert 0.03 * sfxkit.SR < len(x) < 4.0 * sfxkit.SR
    assert np.all(np.isfinite(x))
    assert 0.2 < np.max(np.abs(x)) <= 1.0


def test_reel_writes_cues(tmp_path):
    cues = sfxkit.reel(str(tmp_path / "reel.wav"))
    assert [c["name"] for c in cues] == list(sfxkit.SOUNDS)
    assert (tmp_path / "reel.wav").stat().st_size > 1000
