"""Record every line first (Piper, English). Writes web/timeline.json with start/dur per line."""
import json, os, subprocess, wave
from piper import PiperVoice, SynthesisConfig
T = os.environ.get('PIPER_VOICES', 'voices').rstrip('/') + '/'
def mk(name):
    d = T + f'vits-piper-{name}/'
    return PiperVoice.load(d + f'{name}.onnx', config_path=d + f'{name}.onnx.json')
voices = {'lessac': mk('en_US-lessac-medium'), 'amy': mk('en_US-amy-medium'), 'libri': mk('en_US-libritts_r-medium')}
# who -> (voice, speaker id or None, speed, pitch factor)
V = {'bin': ('libri', int(os.environ.get('BIN_SID', 20)), 1.0, 1.32), 'bo': ('lessac', None, 0.95, 1.08),
     'zu': ('amy', None, 0.92, 1.5), 'nar': ('lessac', None, 0.95, 0.9)}
S = json.load(open('script.json'))
t = 0.0; out = []
os.makedirs('audio', exist_ok=True)
for i, b in enumerate(S):
    v, sid, sp, pf = V[b['who']]
    raw = f'audio/raw_{i:02d}.wav'; fin = f'audio/v_{i:02d}.wav'
    cfg = SynthesisConfig(length_scale=1 / sp, noise_scale=0.75, noise_w_scale=0.9, speaker_id=sid)
    with wave.open(raw, 'wb') as w:
        voices[v].synthesize_wav(b['text'], w, syn_config=cfg)
    sr = wave.open(raw).getframerate()
    af = (f'asetrate={int(sr*pf)},aresample=48000,atempo={1/pf:.4f},'
          'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
          'loudnorm=I=-16:TP=-1.5')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', af, '-ar', '48000', '-ac', '1', fin], check=True)
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', fin]))
    t += b['pre']; b2 = dict(b, i=i, start=round(t, 3), dur=round(d, 3), file=fin); out.append(b2); t += d + b['post']
    print(f"{b['id']:6s} {b2['start']:6.2f} {d:5.2f}")
json.dump({'beats': out, 'total': round(t, 3)}, open('web/timeline.json', 'w'), ensure_ascii=False, indent=1)
print('TOTAL', round(t, 2))
