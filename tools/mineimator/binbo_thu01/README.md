# Bin & Bo — Mine-imator test scene 01 (17 s)

Scripted Mine-imator 2.0.2 scene. Python writes the whole `.miproject`; Mine-imator only renders it.

Pipeline (run inside a work folder):
1. `python tts.py <kokoro_dir>` — Kokoro (Apache-2.0) lines into `vo/*.wav` plus `vo/lines.json` (per-frame mouth envelope).
2. `python skins.py proj/skins` — original 64x64 skins for Bin, Bo and Zu, 10 face variants each.
3. `python build.py <workdir>` — writes `proj/BinBo MI thu 01.miproject`. Uses `template.miproject` for project and render settings.
4. Copy `proj/` to `C:\Users\ADMIN\Mine-imator\Projects\BinBo MI thu 01\`, open it in Mine-imator, then Render > Render animation (1080p, 24 fps).
5. `python mix.py` — voice + sfxkit SFX + music bed, -14 LUFS. Mux it with ffmpeg onto the exported MP4.

Facts checked against the source (stuffbydavid/mine-imator) and on the RTX 3060 PC:
- Keyframes store only non-default values, so a key left out of a keyframe means default (0). `build.py` carries state forward.
- Face swap: a `TEXTURE_OBJ` keyframe (skin resource id) on the **body** part. Head and hat inherit it, so head rotation keys stay separate.
- Facing: `ROT_Z = t` points a character, and the camera view, along (sin t, cos t). So 90 faces +X, -90 faces -X and 180 faces -Y. Camera `+ROT_X` tilts the view down.
- `+ROT_X` tips the top of a part forward. A head looks down, while a hanging arm or leg swings back. To raise an arm in front, use a negative value.
- Root timelines need unique `parent_tree_index` values, or some are missing from the tree.
- GUI driving: Mine-imator ignores fast clicks. Press, hold about 0.3 s, then release.
