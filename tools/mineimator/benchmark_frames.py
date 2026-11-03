"""Frame metrics shared with the in-browser competitor sampler (benchmark_sampler.js).

Both sides read 160x90 RGB at 5 frames per second and report: mean luma, luma contrast (std),
HSV saturation, Hasler-Suesstrunk colourfulness, hard cuts (frame difference > 10 and > 3x the local
median, merged within 2 samples), cuts per minute, average shot length and median frame difference
("motion": how much the picture changes in 0.2 s). Usage: python benchmark_frames.py VIDEO
"""
import json
import subprocess
import sys

import numpy as np

f = sys.argv[1]
W, H = 160, 90
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", f"fps=5,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
def stats(x):
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    mx, mn = x.max(-1), x.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    rg, yb = r - g, 0.5 * (r + g) - b
    cf = np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    return y.mean(), y.std(), s.mean(), cf
S = np.array([stats(x) for x in fr])
gray = (0.299 * fr[..., 0] + 0.587 * fr[..., 1] + 0.114 * fr[..., 2])
d = np.abs(np.diff(gray, axis=0)).mean(axis=(1, 2))
raw_c = [i + 1 for i in range(len(d)) if d[i] > 10 and d[i] > 3 * np.median(d[max(0, i - 5):i + 6])]
cuts = [c for k, c in enumerate(raw_c) if k == 0 or c - raw_c[k - 1] > 2]
dur = len(fr) / 5
motion = float(np.median(d))
out = dict(file=f, seconds=dur, luma=float(S[:, 0].mean()), contrast=float(S[:, 1].mean()), saturation=float(S[:, 2].mean()),
           colorfulness=float(S[:, 3].mean()), cuts=len(cuts), cuts_per_min=len(cuts) / dur * 60,
           avg_shot_s=dur / (len(cuts) + 1), motion_median=motion, cut_times=[c / 5 for c in cuts])
print(json.dumps(out, indent=1))
