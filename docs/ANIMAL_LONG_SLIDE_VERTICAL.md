# Animal Long Slide Vertical

Status: integrated vertical with real Blender preview execution. Final production remains fail-closed until visual and motion qualification are promoted.

## Company integration

The vertical is classified as MediaFormat.ANIMATION with domain animation.animal_long_slide.
It is authored procedural 3D animation, not authentic gameplay. Dialogue/lip-sync is not a hard dependency.

The normal company stages remain active:
Intelligence → Creative Strategy → Planning → Writing/Logic → Direction → Performance →
Production Design → Cinematography → Asset Build → Previs → Technical Direction →
Production → Editorial → Audio → Finishing → Final QC → Packaging → Analytics/Learning.

VOICE_PREP remains present for compatibility but is optional for this vertical.

## Implemented vertical contracts

- deterministic episode/module planner;
- exact module-count planning for mapping Long Slide modules to Company Shot Book shots;
- scene kinds for Long Slide, Spiral Slide, Paint Gate, Fountain, Cage, Key/Door, Ball Pit and Giant Animal;
- controlled-animation versus bounded-physics timing;
- obstacle placements and scene/obstacle compatibility;
- reusable camera beats plus camera candidate scoring and auto-repair;
- animal forward-axis normalization;
- semantic reaction/SFX events;
- originality signature and semantic novelty checking;
- vertical QC for duration, repetition, camera hold, event dead-air and physics overuse;
- asset manifest with commercial-rights and production-readiness gates;
- internal generated scene/obstacle asset library;
- external animal quarantine catalog with provenance and license evidence;
- Motion Foundry with skeleton-family compatibility and source-binary mismatch protection;
- execution planner producing per-module Blender render jobs;
- Blender binder producing real MP4 previews through headless Blender;
- LongSlideProducer mapping module renders back to exact company shot IDs;
- company production routing to blender_long_slide_preview or blender_long_slide.

## Validated preview evidence

The cow pilot has rendered successfully through the real binder:
- external rigged cow asset;
- Run Action;
- internal Long Slide scene;
- rotating hammer obstacle;
- forward-axis normalization;
- controlled root motion and grounding;
- multi-beat camera coverage;
- Eevee render and H.264 MP4 output.

Preview execution is intended for qualification and R&D. It is not equivalent to final production approval.

## Current fail-closed gates

LONG_SLIDE_NO_EXECUTABLE_ANIMALS means fewer than two animal assets have the asset and motion qualifications required for the requested mode.

LONG_SLIDE_ASSET_LIBRARY_UNQUALIFIED means a planned module depends on an asset or motion that is not qualified for the requested mode.

MOTION_SOURCE_ASSET_MISMATCH means a SOURCE_ACTION belongs to a different source binary than the selected canonical animal. It cannot be used until a retargeted motion is explicitly produced and qualified.

Final production remains blocked while visual_qc_passed / production_ready are false. Quarantine assets are allowed only when blender_preview is explicitly enabled and their license plus technical gates pass.

## Variation engine and monetization safety

YouTube's "inauthentic content" policy (renamed 15 Jul 2025, clarified Jul 2026) does not pay for characters put in the same situation over and over with the same outcome, AI content made from generic templates, or animals in exaggerated distress. It explicitly allows a series with recurring characters when each video has a distinct storyline. The vertical enforces that rule before anything is rendered:

- `config/animal_long_slide/series_bible.yaml` defines the channel brand, a named cast (one animal per character), environment themes (sky colour and sun), challenge formats with title and synopsis templates, camera styles and positive endings. Replace the placeholder brand before launch.
- `VariationDirector` (`cinefactory/animal_long_slide/variation.py`) picks each episode's format, lead character, cast, environment, ending and camera style. Choices are weighted towards options that have rested longest, and hard cooldowns block recent repeats (format 3 episodes, lead 2, environment 3, ending 2, camera style 2). Inside an episode it guarantees at least 3 scene kinds and 3 outcomes, no repeated module setup, different camera sequences in adjacent modules, the lead character in the first and last module, and a capped, always-resolved share of peril scenes.
- `VariationPolicy` compares every candidate with the last 10 approved episodes: at least 4 of 8 creative axes must change and structural similarity must stay at or below 0.5. Titles must stay at or below 0.6 similarity to the last 30 titles.
- `MonetizationSafetyGate` (`safety.py`) blocks packaging when an episode repeats recent ones, the title is copied, stuffed, too long or missing the brand, franchise or trademark terms appear (Spider-Man, Paw Patrol, Minecraft, Roblox, GTA and others), distress wording appears, the episode does not end positively, made-for-kids is not set, or human approval is disabled.
- When no candidate passes, `VariationExhaustedError` stops production. The engine never falls back to a repeat.
- The Blender worker executes the new camera patterns (`wide_establish`, `top_down`, `low_front`) and the episode environment theme, so variation is visible on screen, not only in metadata.

Operating loop:

```bash
python scripts/plan_long_slide_series.py --channel <channel> --count 3
# a person reviews data/animal_long_slide/series/<channel>/episodes/EP_xxxx/
python scripts/plan_long_slide_series.py --channel <channel> --approve EP_0001
```

Planning never writes the channel history. `--approve` re-checks the episode against the current history and records it, so the next plan is forced to differ from everything approved. These controls lower the risk of a monetization review; they cannot guarantee YouTube's decision.

## Look development

Leading channels in the niche (studied from their storyboard frames, Oct 2026) show bright game-engine worlds: a gradient sky, water and green hills behind the course, palm or pine trees, patterned floors (checker, zigzag, tiles), dense colourful props, textured animals with readable faces, low and close cameras, saturated colour. Several also use trademarked props (Pepsi cups, Cars-style vehicles, Spider-Man), which this vertical never copies.

`scripts/long_slide_lookdev.py` applies an equivalent look to every themed module, procedurally and deterministically:

- one biome per environment theme in the series bible: ground, hills, water, tree type (palm, pine, lollipop, cactus, round, autumn), clouds or stars, floor checker colours, rail stripes and prop palette;
- glossy checker floors, striped rails, theme-tinted glossy obstacles, softened (smooth + one subdivision) vinyl-toy animals;
- gradient sky, soft sun shadows, Standard view transform for saturated primaries, compositor bloom and a saturation lift, depth of field on the animal, motion blur;
- a lower, closer "toy" camera set that keeps faces in frame, with occlusion checked at five samples per beat so moving obstacles are avoided where possible.

Unthemed jobs keep the original look. Use `--still FRAME` on the worker to render review stills.

## Character FX and real props

`scripts/long_slide_fx.py`, `scripts/long_slide_props.py` and the pure planning helpers in `scripts/long_slide_fx_plan.py` (unit-tested without Blender) add what the niche leaders rely on most:

- **Cartoon eyes.** Every animal gets big glossy eyes with pupils and a catch-light, placed on top of the forehead from the deformed `Head` vertex group, parented to the head bone so they follow the run cycle, with irregular blinks.
- **Races.** `module.metadata["companions"]` lists up to two friends from the episode cast. They run the side lanes (the lead keeps the centre lane for the camera rigs) at outcome-driven paces: SUCCESS keeps the lead in front, COMIC_FAIL lets a friend win (and keep running across the finish platform), other outcomes mix the order. `VariationDirector(renderable_animals=...)` restricts friends to animals the renderer can animate; peril modules stay solo. The execution planner resolves each companion's asset and run motion and fails closed on invalid lists (same as lead, duplicates, more than two, bad ids, unknown or motionless animals). Race shots pull every camera back by 1.3x.
- **Paint gates.** Any trigger tagged `event=paint_transform` gets hanging paint strips in lane colours, and every animal is recoloured by a world-position wipe the moment it passes, with a droplet splash. Legacy viewport-only materials are converted to Principled BSDF first, which also lets the vinyl-toy finish reach the animals.
- **Facing without a head bone.** Rigs such as the duck (bones `Bone..Bone.004`) are turned to +Y from their bounds: the head is the higher end of the long axis. Their eyes use the highest part of the front of the body.
- **Locomotion fix.** The worker now prefers run, then walk, then idle. Before, the lead used the idle pose because the module sequence starts with "idle", so it slid without moving its legs.
- **Camera clutter.** Camera candidates are penalised when a 3x3 grid of screen rays hits set geometry well in front of the animal, not only when the animal itself is blocked.
- **Real CC0 set dressing.** `config/animal_long_slide/kit_props.yaml` maps each environment theme to props from six Kenney kits (nature, platformer, coaster, marble, food, holiday) and the kid-safe subset of Quaternius Ultimate Platformer, all registered in `source_packs.yaml` with their CC0 `License.txt`. `KitPropCatalog` only ships rows from packs that are APPROVED for commercial use in every `source_packs.yaml` entry, whose folder sits under the folder holding their local `License.txt`, and whose file stays inside that folder. Missing files and refused packs are skipped, logged and passed to the worker log as `KIT_PROP_FINDING`; a prop file that fails to import is skipped without stopping the render. The worker places backdrop props (trees, flowers, giant sweets, snowmen, cactus), start banners, finish flags and spinning coins or stars over the lanes that pop when an animal's head reaches them. Weapons, bombs, spikes, saws and skulls are excluded.

Render cost with three animals and props is about 1.1 s per 720p frame on the current machine.

## Complete episodes

A study of the niche leader's latest upload (FunAnimationLive, 7 Oct 2026, 11:43, 144 storyboard frames) shows what makes a finished video, beyond the renderer: one continuous 11-12 minute programme in a few game segments, a fixed round per animal that repeats signature set pieces (coloured garage doors, giant balls that shatter, a colour dome, a rainbow parade of copies of the animal), a cut every 3-5 seconds that alternates close-ups and wide shots, and constant music and sound effects. The pipeline now produces that shape end to end:

```bash
python scripts/make_long_slide_episode.py --episode EP_DEMO_01 --seconds 66 --seed 21
# -> data/animal_long_slide/episodes/EP_DEMO_01/episode.mp4 (+ episode.json, upload_package.json)
```

- **Shot list.** `VariationDirector(nominal_module_seconds=9.5)` cuts the target length into short modules (the internal course is about 12 m, so long modules made the animals crawl). `blocked_scenes` keeps out scene kinds the renderer cannot stage yet: the spiral template is a helix but runners travel a straight line, so `SPIRAL_SLIDE` is blocked in the episode maker until a path rig exists.
- **Preview cast.** `config/animal_long_slide/series_bible_preview.yaml` keeps the channel, worlds and formats but uses only animals the renderer can animate today (cow, duck, horse, pig, sheep, zebra, fox, husky). Switch back to `series_bible.yaml` once the licensed wild-animal pack is qualified.
- **Set pieces** (`module.metadata["gimmicks"]`, built by `scripts/long_slide_gimmicks.py`): `door_reveal` opens every episode (coloured garage doors slide up while the runners wait), `clone_parade` ends it, or the module before when the last two would repeat (five rainbow copies of the lead pop in and run behind it in a V, each on its own lane, the one in the lead's lane more than a body length back; companions are dropped to free the lanes), `ball_smash` appears in between (giant patchwork balls burst into keyframed pieces when an animal reaches them, placed clear of obstacle slots). Never the same piece twice in a row; peril modules get none.
- **Sound cues.** FX code records what happens on screen (`long_slide_events.py`: door, race start, coin pop, paint splash, smash, clone pop) and the worker writes `<clip>.events.json` next to each rendered module.
- **Music and SFX** (`scripts/long_slide_audio.py`, numpy only, no licence or API): a major-key bed with bass, strummed chords, marimba melody and drums whose tempo, key, progression and melody come from the episode seed; each cue becomes a synthesised effect at its exact frame, a whoosh marks every cut, and the music ducks under the effects.
- **Assembly** (`scripts/assemble_long_slide_episode.py`): checks `ffmpeg`/`ffprobe` first, then builds animated title and end cards (Pillow), the module clips in order (filter graph in a script file, so long episodes stay under the Windows command-line limit), the mixed track, H.264 + AAC 48 kHz at -14 LUFS with `faststart`.
- **Resumable and fail-safe.** Blender runs with `--python-exit-code 1`, so a worker error fails the module instead of passing silently, and any old clip is deleted before a render. A finished module gets a `.job.sha256` stamp of its job; a re-run reuses a clip only when the stamp matches the current plan and ffprobe counts the frames the sidecar promises. Set pieces and props are decoration: a failure is logged (`GIMMICK_FAILED`, `KIT_PROP_IMPORT_FAILED`) and the module still renders.
- **Measured.** EP_DEMO_01 (7 modules, 71.5 s with cards) rendered in about 22 minutes at 720p on the current machine (about 3 minutes per 9.4 s module), -13.9 LUFS, peak -1.2 dBFS.

The biggest remaining gap to the market leaders is still the animal models themselves (low-poly, viewport-coloured, no facial rig). A commercially licensed, rigged and textured cartoon animal pack remains the next quality step.

## Current asset strategy

Strong preview candidates include the Quaternius rigged/animated farm and ultimate animals. OpenGameArt provides useful canonical candidates for elephant, tiger, lion, hippo and duck; some still require motion, rig or material work. Dinosaur and buffalo candidates remain researched but their non-BLEND animation playback paths require additional binder qualification.

## Next production milestone

1. automate visual qualification for animal assets and internal scene/obstacle templates;
2. implement motion preview QC for foot contact, loop continuity and forward travel;
3. create or retarget locomotion for elephant, tiger, lion and hippo;
4. rig/animate gorilla or replace it with a stronger licensed candidate;
5. qualify baked-track/hierarchy animation paths for dinosaur and buffalo;
6. improve Long Slide environment, materials, obstacle presentation and camera language toward the target channel quality bar;
7. add semantic SFX/reaction sidecars and shared FFmpeg episode assembly;
8. render a multi-animal pilot episode through Company Runner preview mode;
9. promote only assets/templates/motions that pass visual, technical, licensing and novelty gates.
