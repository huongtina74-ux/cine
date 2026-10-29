# CINE — MUSE 10-SECOND SHOT LOCK TEMPLATE (VERSIONED)

**Shot**: `{EPISODE_ID} / {SHOT_ID}`; duration EXACT **10.00s**; scene location `{SITE_ID}/{SPACE_ID}`; approved frame `{PLATE_ID}`; source SHA256 `{SHA256}`; `CAMERA_ANCHOR_ID={CAMERA_ANCHOR_ID}`; image status must be `APPROVED`. If not, development-only PREVIS, no production release.

**FIRST FRAME / EXACT SPATIAL REFERENCE**: supply approved master image as INPUT, with approved identity pack images and consistent view plate; all door/window/fixed props remain exactly where shown in floor plan, no new furniture or fantasy decoration. Full-bleed native 16:9.

**SHOT PURPOSE & ACTION**: `{BEAT}` from approved screenplay. Animate `{CHARACTERS}` and `{PROPS}` in physically credible state transitions. No camera-only zoom masquerading as character animation. Articulations visible and purposeful. If empty environment, restrained foliage, cloth and background activity only.

**CAMERA**: `{SHOT_SIZE}`, full-frame 50mm baseline (override only if approved), composition, eye height and camera world-coordinate anchor; stable gimbal/dolly/tripod; `{PAN_TILT_DOLLY}`. Avoid parallax causing windows to move physically. Plausible depth of field; primary character/architecture critically sharp.

**10-second beat timing**: `00.0–02.0` setup `{BEAT1}`; `02.0–06.0` action `{BEAT2}`; `06.0–08.5` emotional/reactive beat `{BEAT3}`; `08.5–10.0` resolution/transitional hold `{BEAT4}`. No unexplained cut inside shot.

**LIGHT & COLOR**: source D55 5500K clear neutral natural daylight, no yellow cast, no warm LUT, accurate neutral whites/grays; match previous/next shots and real site sunlight direction. For night follow locked nighttime look rather than blindly 5500K physical lamps.

**DIALOGUE ENGLISH A2**: `{EXACT_LINE}` spoken by `{SPEAKER_ID}` with fixed external master WAV `{VOICE_MASTER_ID}`; phoneme-level lipsync if face visible. If no dialogue: `NO SPEECH`. Never generate random/offscreen narrator or new voice timbre.

**AUDIO MIX**: location ambiences `{AMB_SFX}` + narrative foley `{FOLEY}`; no unpleasant constant bell jingles. Preserve intelligible A2 speech, low instrumental underscore only when approved.

**NEGATIVE**: no object morphing; no recast; no added bells, magic particles, floating furniture, orange-yellow wash, mirrored reverse, camera warps, sharpness loss, frame borders, side-panels, AI text, duplicate characters, new unregistered props.

**REQUIRED QC**: compare frame 0/120/239 (24fps) to approved anchors; duration exact; lip-sync, prop states, white balance, clean sound and no hallucinated words. Any failure -> repair shot; cannot mark `PASS` on prompt text alone.