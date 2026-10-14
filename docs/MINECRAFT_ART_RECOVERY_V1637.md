# CineFactory v1.6.37 — Minecraft Art & Production Reality Check

**2026-10-09 — DIAGNOSTIC + FIRST ART PILOT COMPLETED, PROFESSIONAL PRODUCTION STILL BLOCKED.**

## The fundamental problem

The v1.6.36 'Golden Shot' compared Blender Workbench and Eevee **at 480x270/12fps with 2 seconds of footage, simple coloured cuboids, stiff minimal motion, a dark desk-filled test classroom and no sound**. It never compared professional Minecraft animation workflow quality, never studied BigSchool/ Maizen reference footage frame-by-frame and never created a story or acting/audio track. 936 passing code tests did **not** establish art quality. Calling it studio-grade was unjustified.

Actual v196 code: `scripts/blender_golden_scene_v196.py` uses `scripts/blender_animation_worker.py::proc_actor` rig `mc_a/mc_b`, whose skin asset reference is `procedural://skins/mc_a_pixel_16`, with basic per-cube material colors, dark eyes and static mouth. Arms are elementary box meshes attached to a root with rotation about box centre. Its 'animation' consists mostly of one arm swing and tiny torso rotation. The camera is a nearly static frontal shot. No original song, acting performances, music, scene storyline or proper facial visemes.

**Quality must be built into source geometry/rigging, acting/story and audio, not fixed by upscaling, extra GPU or switching renderers.**

## What we did THIS TURN, not fake competitor research

1. Inspected the real v196 rendered comparison and worker's avatar/room source code; confirmed low-quality debug-style art controls, no production-ready skin/rig.
2. Researched published **technical pipelines** (not claims about which software BigSchool or Maizen privately uses):
   - [Blender Studio Minecraft Animation Workshop](https://studio.blender.org/training/minecraft-animation-workshop/): chapters for exported Minecraft worlds, skin textures, Boxscape character rigs, acting/props, lighting, rendering and sound. Some course chapters require membership; sources are curriculum descriptions, not personally watched full workshop.
   - [Official Blockbench](https://www.blockbench.net/): Minecraft-style modeling, UV/pixel texturing and graph/timeline animation, useful for first-party skin/mob/props; supports original artist-made assets.
   - [MCprep GitHub](https://github.com/Moo-Ack-Productions/MCprep): original Blender addon for world import material preparation, rig/mob spawning, asset libraries, effects; **original README advertises compatibility around Blender 4.0 and older versions**; installed Blender is 4.5.14. Treat as **COMPATIBILITY UNVERIFIED**; also review default Minecraft asset use/valid game licence.
   - [Mine-imator official](https://www.mineimator.com/download) 2.0.2: dedicated Minecraft 3D video/rig/animation/camera/VFX software; excellent candidate for small-scale Minecraft-oriented comparison, BUT **not installed/benchmarked on this PC**, unattended script automation unverified.
   - [Minecraft official use rules](https://www.minecraft.net/usage-guidelines): differentiate monetized original videos from use of publisher IP for unrelated brand promotion; media, music, cloned channel character designs and redistributed asset packs require scope-specific review.
3. Attempted earlier public BigSchool `n3PT62-WX20` YouTube reference: yt-dlp metadata succeeded; short video media download returned HTTP 403. TubeAlfred returned zero credits. **We have not viewed its full animated frames or soundtrack**. This release MUST NOT claim real shot-by-shot BigSchool/Maizen forensic breakdown, retention curve, hidden rigs, title-to-shot timing or production app attribution. Reference stills or thumbnails may inspire generalized criteria, never a proven pipeline or a reason to copy original channel IP. Optional vidIQ full-watch tool charges 25 credits each, **not invoked**.
4. Implemented and verified separate Python **MinecraftArtGate** `cinefactory/studio/minecraft_art_gate_v197.py`: script/character/face/pivots/expression/animation/UV-skin/lighting/camera/audio/QC/rights fail-closed thresholds. `tests/test_minecraft_art_gate_v197.py` tests old technical benchmark fails despite valid render, 4K upscale cannot rescue flat production art, scripted audio requirements enforce voice/lipsync, and even qualified claims cannot auto-publish.
5. Built first-party **visual prototype only**, using a copy of v196 actors and entirely original self-generated pixel materials / 16x16 packed texture patterns: `scripts/blender_minecraft_visual_pilot_v197.py`.
   - Added separate eyebrows, eyelids/eyes, cheek/shapes, two identities (cobalt/orange and purple/mint), shoulder-pivot control, motion poses, village hut, chunky trees, grass/path, sun and Eevee lighting.
   - Originally a white gem obscured composition; adjusted in follow-up `scripts/blender_minecraft_storyboard_v197.py` to a green treasure and introduced 3 original cameras/cuts at frames 1,17,33; expressive eye blink at frames 20–25.
   - Rendered **48 real 960x540 @24fps frames**, 2 seconds, H.264 MP4 with an entirely original procedurally synthesized 2-second WAV chime/AAC sound track via `scripts/package_minecraft_visual_pilot_v197.py`.
   - Visual review contact sheet at `data/verification/v197_minecraft_art_direction/three_shot_real_frame_review.jpg`; output `minecraft_3shot_visual_pilot_with_original_sfx.mp4`; signed SHA and actual ffprobe H264/AAC frames in `pilot_media_evidence.json`.
   - The result is **still crude**: action lacks clear plot, actual production quality 64x64 UV skin files and 3D overlay, elbow/hip IK, expressive phoneme face, walking cycles, better world assets/material art, narratively staged shots, professional voice, foley, SFX/music mastering and approval.
6. Audited actual old vs new using `scripts/audit_minecraft_recovery_v197.py`. Old v196: **15 hard blockers**. New v197: **12 hard blockers** (still FAIL). No misleading claim that prototype meets competitor quality. Actual file hashes/decoded media tested.

## How a professional Minecraft vertical should actually decide tools

| Department / stage | Preferred tool and asset strategy | Technical delivery / acceptance |
|---|---|---|
| Competitive Format Analysis | Actual accessible reference *video frames + audio + timestamps*, otherwise only public metadata; retention if owner provides analytics | Theme/beat/shot/voice/story style sheet, confidence/source pointer, no cloning |
| Storyroom & Director | Original script -> 30-60 sec pilot with 3-act character conflict -> locked storyboard and animatic | 10-15 purposeful shots where appropriate; character eye lines, readable poses, sound/music beat map |
| Asset & World | **Blockbench** as original skin/props/asset source; first-party 64x64 pixel RGBA Minecraft-style textures (where compatible) and UV setup; imported original map/OBJ; MCprep if Blender4.5 audit passes | Character consistency and rights ledger; UV nearest-neighbour images, second-layer skin/accessories, believable voxel props/world |
| Character Engineering | Blender full-feature rig + bone pivot IK/FK (shoulder, elbow, wrist, neck, hip, knee, ankle), face control for eyebrows/eyes/pupils/eyelids/7+ relevant mouth shapes; avoid primitive floating cuboids | Persistent independent character IDs, geometry boundary, deformation and pose QC with director-approved extremes |
| Performance Animation | Blender NLA library: idle, speech, run, walk, turn, reaction, startled, laugh, interacting-with-props, face/blink/syllables; genuine anticipation, follow-through, footplant, inertia | Acting replay with context, no dead air/unmotivated stiff standing |
| Real-world/gameplay | **Minecraft actual runtime** and approved capture software if authentic gameplay is central; alternative Mine-imator where automation shown viable | No fabricated 'real Minecraft gameplay', reproducible recording, game/publisher rights |
| Camera/Cinematography | Blender camera coverage based on storyboards: wide/medium/close/action/cutaway with correct axis, 24fps+; art-directed bounce light and color | Key scene legible at phone size; correct eyeline, identity, silhouettes; no excessive dark/flat render |
| Sound | Consented original voice or licensed TTS; original music/SFX, Foley, beat/phoneme alignment and controlled audio mastering | Speech intelligible, correct dialogue/viseme, no clipped sound, music/voice usage rights |
| Edit/QC | FFmpeg/Remotion/DAW as proven fit; mixed cinematic render quality modes | Frame/shot continuity, no mask/prop collisions, exact dialogue, copyright, hand-reviewed 1080p24 30-60s **minimum pilot** |
| Production Economics | Preview renderer Workbench, finals Eevee/Cycles after *qualified real comparison* | Actual accepted minutes including retakes/reviews, GPU watts/time, human touch, rights cost |

**Not yet proven:** Which exact rigs, software or render farms BigSchool/Maizen use. They may use combinations of systems; never attribute an engine from thumbnail or still.

## Next prioritized corrective engineering

**P0: actual reference forensic evidence** from three distinct authorized BigSchool/Maizen-style long-form episodes: obtain playable footage (user-supplied lawful analysis copy, officially accessible video or user-approved paid credits); frame/audio/time annotations at real timestamps, plot beat chart, character expression/texture/lighting/shot/audio breakdowns, independent contrast to CineFactory. No such claim until source proof.

**P0: actual character department**: design two ORIGINAL Minecraft-compatible skin PNGs and proper geometry/UV source, configurable expressions and pose rig, persistent wardrobe, props. Use artist test packs with verifiable commercial rights. Add import adapters and version manifests, independent holdout tests.

**P0: true 30–60sec episode**: coherent hook/obstacle/reaction/punchline and original voices/music, 3D acting with 8–12 scene beats, 1080p24 delivery, human art/acting/director listening panel. Only these shots may be used to qualify a released Minecraft style.

**P1: production pipeline fit**: capture reference engine options Mine-imator/Blockbench/MCPREP + Blender 4.5 exact compatibility, runtime and license on 3060, R&D trials by shot type. No assumed cost $0 and no unapproved downloads/install.

**P1: iterative artist/research loop**: when visual QC rejects a pilot, create defect tickets with still, timestamp, cause, reference & changed rig/lighting assets; rerender only affected shots; require multi-project negative controls before studio-wide rule changes.

## Current acceptance verdict

**v197 pilot: BLOCKED_MINECRAFT_ART_PRODUCTION**. Actual small film/video exists with SHA and audio, but is *not publishable as a pro Minecraft episode*. Focused tests pass. Do not mistake a technically-valid mp4 for a premium Minecraft animation.

Artifacts on the connected Windows PC:
`C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6\data\verification\v197_minecraft_art_direction`.

No old production worker modified, no user repo reset, code commit, deployment, competing channel asset copying, paid watch credits, unapproved installs or publication.


## Verified acceptance checkpoint — 2026-10-09

- **943/943 repository tests PASS**, 161.97 seconds, 0 failure, exit code 0. `python -m compileall -q cinefactory scripts tests` PASS. Existing active tracked source check PASS (only informational Windows LF/CRLF warnings).
- This version adds 7 checks on art gate, actual generated 2s 960x540 @24fps original Minecraft-inspired three-shot H.264/AAC pilot, original synthesis WAV/MP4 SHA verification, and strict explicit creative/rights blockers. Existing 936 tests preserved.
- First-party sandbox render produced `original_village_frame17.png`, `minecraft_original_storyboard_3shot.blend`, `three_shot_real_frame_review.jpg`, `minecraft_3shot_visual_pilot_with_original_sfx.mp4` and `recovery_gap_audit.json`.
- Original v196 tech benchmark **15 art blockers**; new v197 art exploration **12 blockers**. It is an actual media pilot, NOT a publishable finished Minecraft animation nor verified BigSchool/Maizen competitor reverse engineering.
- Exact working directory remained `C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6`. Existing production `scripts/blender_animation_worker.py` unchanged by this v197 art proof. Changes not committed, published or deployed.
