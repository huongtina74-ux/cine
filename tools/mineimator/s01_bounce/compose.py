"""Final MC-S1 #01: Mine-imator render + blockfilm overlay (banner, scoreboard, counters) + blockfilm mix.wav (-14 LUFS).

    python compose.py RAW.mp4 OUT.mp4
Needs tools/blockfilm/s01_bounce/out/overlay.mov (node render.js overlay out/overlay.mov 0 18) and out/mix.wav (audio.py).
"""
import os
import subprocess
import sys

BF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'blockfilm', 's01_bounce', 'out')
raw, out = sys.argv[1], sys.argv[2]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-i', os.path.join(BF, 'overlay.mov'), '-i', os.path.join(BF, 'mix.wav'),
                '-filter_complex', '[0:v]scale=1080:1920,fps=30,setpts=PTS-STARTPTS[b];[1:v]setpts=PTS-STARTPTS[o];[b][o]overlay=0:0:format=auto,format=yuv420p[v]',
                '-map', '[v]', '-map', '2:a', '-t', '18', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
print('COMPOSE_OK', out)
