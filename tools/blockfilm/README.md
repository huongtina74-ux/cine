# blockfilm — code-driven block-world episodes (Bin & Bo)

This is the engine that produced `Bin_Bo_Tap1_Nut_Do_Bi_An.mp4`. It was made 2026-11-01 and is 51 s long, 1080p30, with a Vietnamese voice.
Everything runs headless in any Linux/Windows box with Python, Node and the pre-installed Playwright Chromium.
- No Minecraft install is needed, and no Mine-imator or Blender GUI.
- No Mojang assets are used: every texture is drawn procedurally.
- Bin & Bo are original characters.

## Pipeline (one folder per episode, e.g. `ep01_nut_do/`)
1. `script.json` holds the lines in order: `id`, `who` (bin/bo/nar/...), `text`, optional `cap`, `pre`/`post` pauses.
2. `python tts.py` records every line **first**. It uses the Piper voice (`PIPER_VOICES` = folder of `vits-piper-*` models), adds pitch per character and runs loudnorm. It writes `web/timeline.json` with the start and duration of each line.
3. `python env.py` adds a mouth-movement envelope per line, so mouths follow the voice.
4. `web/index.html` is the episode, built with three.js r149. It contains:
   - the set
   - the characters
   - `pose()`, a reusable action library: idle, talk, walk, run, flail, point, press, wag, yell, cheer, hug, pant, fall, dazed, nod, ...
   - `drawFace()` for eyes and mouth states
   - `renderAt(t)`, where the shots are timed off the lines (`S('id')` / `E('id')`)
   - captions drawn as an overlay
5. Render the video with `node render.js video out/part.mp4 T0 T1`. It runs one Chromium per segment, so segments can render in parallel. For test stills, use `node render.js stills out/chk t1 t2 ...`.
6. `python audio.py` builds the music and SFX in numpy (original, no samples), ducks them under the voice, and mixes to `out/mix.wav`. Then ffmpeg muxes the result.
7. `node thumb.js` renders the thumbnail. `mkboard.py` makes the review board.

`web/` needs `npm install` (three, @fontsource/baloo-2). node_modules, audio and out are not committed.

## Why it moves well (measured on ep01)
- **Action-driven story.** Button, trapdoor, fall, lava, explosion: physical motion is easy to animate in code.
- **18 shots in 51 s**, each with a designed camera: a falling cam, a crane, over-the-shoulder, a low angle with the prop in the foreground. Shake and zoom punches are added on top.
- **Named, exaggerated poses** from one library, not hand-keyed joints.
- **Face states plus voice-driven mouth.** Expression comes from the face and the audio, not subtle body acting.

## Checks
`python -m pytest tests/test_blockfilm_episode.py -q` checks the following for every episode folder:
- the script, timeline and picture use the same beat ids
- the timeline is monotonic
- the referenced beats exist
