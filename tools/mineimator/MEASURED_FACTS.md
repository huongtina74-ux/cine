# Mine-imator 2.0.2: facts we have verified

Each line is labelled **SOURCE** (read in stuffbydavid/mine-imator 2.0.2 GmProject/scripts) or **RENDER** (seen on a render on the CINE PC, RTX 3060). Anything not yet verified belongs in reports/research/mineimator_study/00_CAM_NANG_MINE_IMATOR.md §7, not here.

## File format (.miproject = JSON)
- SOURCE: a keyframe stores only values that differ from the default (`project_save_values`). If a key leaves a value out, that value is the default (0 for transforms) at that key, so generators must carry state forward.
- SOURCE: transition names are `linear, instant, bezier, ease{in,out,inout}{quad,cubic,quart,quint,sine,expo,circ,elastic,back,bounce}`.
- SOURCE: timeline types are `char spblock scenery item block bodypart particles text cube cone cylinder sphere surface model camera spotlight pointlight folder background audio path pathpoint shape lightsource`.
- SOURCE: resource types are `pack packunzipped skin downloadskin itemsheet legacyblocksheet blocksheet scenery fromworld particlesheet texture font sound model`. The `filename` path is relative to the project folder.
- SOURCE: a surface/cube template is `{"type":"surface","shape":{"tex":<res id>, "invert":bool, ...}}`. A surface is a 16×16 square in the XZ plane (rad 8), its texture's top is at +Z, and `backfaces=true`.
- SOURCE: colours are saved as `"#RRGGBB"` (LIGHT_COLOR, BG_*_COLOR, MIX_COLOR …).
- SOURCE: the background/environment is a `background` timeline with keys `BG_SKY_TIME, BG_SUNLIGHT_STRENGTH, BG_SUNLIGHT_ANGLE, BG_SUNLIGHT_COLOR, BG_AMBIENT_COLOR, BG_NIGHT_COLOR, BG_SKY_COLOR, BG_FOG_*, BG_WIND_*` and others. Its defaults are the project's `background` block.
- SOURCE: point and spot lights are `pointlight`/`spotlight` timelines. Light keys and their defaults: LIGHT_COLOR white, LIGHT_STRENGTH 1, LIGHT_RANGE 250, LIGHT_SIZE 2, LIGHT_FADE_SIZE 0.5, LIGHT_SPOT_RADIUS 50, LIGHT_SPOT_SHARPNESS 0.5.
- SOURCE: **render presets override the file.** If `project.render_settings` is non-empty (for example `"performance"`) and the matching `.mirender` preset exists, loading the project re-imports that preset over the saved `render` block. Use `""` (Custom, Full edition) to keep our own render values.
- SOURCE: visibility is the `VISIBLE` value, and a texture swap is the `TEXTURE_OBJ` value (a resource id).
- SOURCE: a keyframe only stores values that differ from `tl_value_default`. `VISIBLE` defaults to true, so a hidden key must write `"VISIBLE": false`; `SCA_*`, `ALPHA` and `CAM_FOV` default to 1/1/45, so a value of 0 must be written explicitly.
- SOURCE + RENDER: every point3D in the file (for example `block.repeat`, `rot_point`) is saved as **[x, up, y]** (`json_save_var_point3D` / `value_get_point3D` swap Y and Z). In scene 03 v1, `repeat: [3, 2, 1]` meant for a 3×2 rug rendered as a red wall 3 wide and 2 blocks tall.
- RENDER: a `block` template with `repeat_enable` tiles one block into a box of 16-unit blocks that is **centred on the timeline position in X and Y and rises from it in Z**. This comes from fitting a camera projection to thu03 frame 383: 67 px total error, against 390 px for the corner-origin guess. The corner guess put the floor only in front of the camera and left the table 8 units off, so Zu stood in the air behind it with his legs hidden.
- RENDER: shapes with `face_camera: true` (billboards) ignore their parent. Hearts parented to Zu's head floated near the world origin, and the "!" over Bin never appeared, so use billboards only at root level.
- RENDER: `cube` shapes parented to the head as puffable cheeks rendered as large blocks across Zu's mouth, offset from the expected centre. They were replaced by widening the head on each chew.
- SOURCE: camera extras available as keyframe values: `CAM_SHAKE` (+ `CAM_SHAKE_STRENGTH_X/Y/Z`, `CAM_SHAKE_SPEED_X/Y/Z`), `CAM_DOF` (+ `CAM_DOF_DEPTH`, `CAM_DOF_RANGE` default 200, `CAM_DOF_FADE_SIZE` default 100, `CAM_DOF_BLUR_SIZE` default .01), `CAM_VIGNETTE` (+ `_STRENGTH`, `_RADIUS`, `_SOFTNESS`). Camera `ROT_Y` gives a dutch roll (RENDER: visible tilt in scene 03).
- SOURCE: a shape template with `face_camera: true` is a billboard (used for hearts, sparkles, crumbs, steam, "!" / "?").

## Space and orientation
- RENDER: for characters and the camera view, `ROT_Z = t` faces the direction (sin t, cos t). So 0 = +Y, 90 = +X, -90 = −X, 180 = −Y.
- RENDER: camera `+ROT_X` tilts the view down.
- RENDER: on body parts, `+ROT_X` tips the top of the part forward. A head therefore looks down, while a hanging arm or leg swings back; raise an arm in front with a negative ROT_X.
- RENDER: in head space the origin is the centre of the head, the face plane is at Y=+4, and Z is up. Face surfaces at Y 4.02–4.045 with SCA 0.5 cover the face exactly.
- RENDER: looking along +Y, screen-right is −X.
- RENDER: root timelines need unique `parent_tree_index` values, otherwise some don't appear in the timeline tree.

## GUI driving (computer use)
- RENDER: Mine-imator ignores fast clicks. Press, hold about 0.3 s, then release. The Save/Open dialogs only appear when they are clicked this way.
- RENDER: re-opening the project that is already open does not reload it. Open another project first, then reopen it.
- RENDER: the export dialog keeps its last FPS, which is reset to 30 in a new app instance, so check it each time.
- RENDER: opening a new `.miproject` in the same project folder as the one already open did not reload the scene (scene 03 v2 in folder `BinBo MI thu 03`); putting it in a new folder (`BinBo MI thu 03b`) did. Ship each revision to its own folder.
- RENDER: the Claude desktop window can sit on top of Mine-imator while it is driven; start every action batch by clicking the Mine-imator taskbar button and check with a zoom, never with the masked screenshot.

## Performance (RTX 3060)
- RENDER: 1080p24, 24 samples, high-quality render: 409 frames took about 3.5 min, roughly 0.5 s per frame.

## Lighting (light lab v1 and v2, `binbo_thu02/lightlab.py`, renders sent to the owner)
- SOURCE + RENDER: `BG_SKY_TIME` is the sun's angle from the zenith, offset by 90°: 0 puts the sun straight overhead, -45 gives 45° elevation, -76 gives a low golden-hour sun. In v1, -12 made the sun higher (wrong direction).
- RENDER: with `BG_SKY_ROTATION` 0 the sun sits on the +Y side, i.e. behind characters that face the camera at -Y. That backlit look is the good golden-hour shot (the sun disc shows in the frame). Rotation 180 puts the sun behind the camera and washes out the faces.
- RENDER: `SUBSURFACE` 0.6 on the characters plus `render_subsurface_samples` 16 makes skin warmer, brighter and softer. This was the clearest improvement over the default.
- RENDER: with Custom render settings (`render_settings: ""`), 48 samples and 1080p24, the render ran at about 0.75 s/frame for the light lab (96 frames in about 70 s, 2 characters) and about 1.25 s/frame for scene 02 with lights + subsurface (408 frames in about 8.5 min). That is roughly 2.5× the time of 24 samples without subsurface.
- RENDER: for night, the day settings recoloured — sun `#3B4C9B` at strength 0.25, ambient `#10152B`, sky `#0B1130`, custom fog `#0B1022`, plus a warm point lamp (`#FFB24D`, strength 2.2, range 120) — gave a believable night. Without custom fog the horizon stays a bright band (v1).
- RENDER (scene 03 v1): face layers `heart`, `sparkle`, `squeeze`, `popped` eyes, `drool` / `chew` / `scream` / `wavy` mouths and the `blush` layer read clearly in close-ups; arms at `ROT_X -150, ROT_Z +34·side` crossed in front of Bin's face (fixed to `-172, -32·side`).
- RENDER: a rim point light behind the characters at strength 1.6–3, range 60–90, has hardly any visible effect on Minecraft-style blocks. The edge highlight needs a stronger, closer light or a sun backlight.
