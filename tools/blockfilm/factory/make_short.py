"""ONE command: SPEC -> finished vertical Short + technical QC + measured production time.

    python tools/blockfilm/factory/make_short.py tools/blockfilm/factory/specs/s02_tower.json [--workers 2] [--stills]

Steps (each timed): build page -> export cues -> sound mix -> parallel render -> mux -> tools/cf_qc.py --profile shorts.
Writes OUT/<id>.mp4, OUT/production.json (MEASURED seconds per step) and the cf_qc report next to it.
Independent review (qc-reviewer -> qc_notes.md) is a separate step on purpose: maker != checker.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import audio  # noqa: E402
import build  # noqa: E402


def run(cmd, **kw):
    print('$', ' '.join(map(str, cmd)), flush=True)
    subprocess.run(list(map(str, cmd)), check=True, **kw)


def make(spec, out_root=None, workers=2, stills=False):
    spec = Path(spec).resolve()
    sid = json.loads(spec.read_text(encoding='utf-8'))['id']
    out = Path(out_root or HERE / 'out' / sid).resolve(); out.mkdir(parents=True, exist_ok=True)
    times = {}; t_all = time.time()

    def step(name, fn):
        t = time.time(); r = fn(); times[name] = round(time.time() - t, 1); return r

    step('build', lambda: build.build(spec, out))
    web = out / 'web'
    step('cues', lambda: run(['node', HERE / 'render.js', web, 'cues', out / 'cues.json']))
    cues = json.loads((out / 'cues.json').read_text())
    if stills:  # one still per story segment, for a quick look before the full render
        ts = [round((s['t0'] + s['t1']) / 2, 2) for s in cues['seg']]
        step('stills', lambda: run(['node', HERE / 'render.js', web, 'stills', out / 'stills', *ts]))
    step('audio', lambda: audio.mix(str(out / 'cues.json'), str(out / 'mix.wav')))
    step('render', lambda: run(['node', HERE / 'render.js', web, 'pvideo', out / 'picture.mp4', workers]))
    final = out / f'{sid}.mp4'
    step('mux', lambda: run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out / 'picture.mp4', '-i', out / 'mix.wav',
                             '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                             '-movflags', '+faststart', final]))
    qc = subprocess.run([sys.executable, ROOT / 'tools/cf_qc.py', final, '--profile', 'shorts', '--out-dir', out / 'qc'],
                        capture_output=True, text=True)
    times['total'] = round(time.time() - t_all, 1)
    prod = {'id': sid, 'spec': str(spec.relative_to(ROOT)), 'video': str(final.relative_to(ROOT)),
            'duration_s': cues['total'], 'frames': int(cues['total'] * 30), 'workers': workers,
            'seconds_MEASURED': times, 'render_s_per_frame_MEASURED': round(times['render'] / (cues['total'] * 30), 3),
            'cf_qc_exit': qc.returncode, 'cf_qc_last_line': (qc.stdout.strip().splitlines() or [''])[-1]}
    (out / 'production.json').write_text(json.dumps(prod, indent=1))
    return prod


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('--out'); ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--stills', action='store_true')
    a = ap.parse_args()
    p = make(a.spec, a.out, a.workers, a.stills)
    print('SHORT_OK' if p['cf_qc_exit'] == 0 else 'SHORT_QC_FAIL', json.dumps(p))
