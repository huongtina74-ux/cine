# Bin & Bo: Mine-imator test scene 02 (17 s), built with the techniques from the tutorial study

Study notes for ~80 tutorials are in `reports/research/mineimator_study/` (groups A–E).

What changed from scene 01:
- **Faces.** Every character has a faceless skin, and the face is built as a rig of 4 textured surfaces parented to `head`: eyes, pupils, brows and mouth. Each layer is its own channel of instant `TEXTURE_OBJ`/POS keys, so an emotion and lip-sync can play at the same time.
  - Sources: [C: puXk5_aVtvY 2:10, eSVLFPCLBZk 0:52, Un_RU3KwleY 3:33].
  - Measured: the head origin is the centre of the head and the face plane is at Y=4 in head space. Layers sit at 4.02–4.045 to avoid z-fighting, and the surfaces use SCA 0.5 (16 → 8 units).
- **Lip-sync.** The mouth opens to 4 levels (rest / 1 / 2 / 3) depending on loudness, with one key every 3 frames. The shape family follows the emotion: open, grin or wail. [C: jGvOjgVfN_A 3:19, 10:37, 12:04]
- **Blinks.** A half / closed / half blink 6 frames before each line, then another every ~3 s. Pupils hide behind the face while the eyes are closed. [C: QRwM5E7NVaA 7:21]
- **Walk.** Legs on linear easing with a ±16° swing sized to the stride, arms on ease, plus a body twist and a settle step at the stop. [B: NU0fAvOgEv0 13:09, BmWf6dR4kks 3:22]
- **Idle.** Breathing on the body part, so no one is ever fully still. [B: aMTNQBzSGA8, C: QRwM5E7NVaA 5:37]
- **Camera FOV.** Wide 44, medium 34, close-up 28. [D: camera notes]

Pipeline:

    python prep.py WORK
    python ../binbo_thu01/tts.py <kokoro_dir>     # or copy vo/ from scene 01
    python build.py WORK
    # copy WORK/proj to C:\Users\ADMIN\Mine-imator\Projects\BinBo MI thu 02\ ; Render > Render animation (1080p, 24 fps)
    python mix.py                                   # voice + SFX + music, then mux with ffmpeg

Coordinate facts (measured on renders):
- `ROT_Z=t` faces (sin t, cos t) for both characters and the camera view.
- Camera `+ROT_X` tilts the view down.
- `+ROT_X` tips the top of a part forward, so a hanging arm swings back.
