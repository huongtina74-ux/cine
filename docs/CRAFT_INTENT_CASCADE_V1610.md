# Craft Intent Cascade v1.6.10

## Goal

Carry approved creative intent from pre-production into technical and post-production
execution instead of allowing Story/Director/Storyboard decisions to disappear after review.

This milestone focuses on Minecraft and Roblox Animation, where the full cinematic
pre-production path is active.

## New stage

CRAFT_EXECUTION_DESIGN

Inputs:
- story_architecture
- script
- director_cut
- director_treatment
- shot_book
- cinematography_bible
- animatic_plan

Outputs:
- creative_intent_graph
- camera_diagnostics
- performance_direction
- lighting_color_intent
- sound_spotting

The stage runs after STORYBOARD_EDITORIAL and before LAYOUT_TECHVIS.

## Scene -> Beat -> Shot creative-intent cascade

Implemented in `cinefactory/studio/craft_execution.py`.

Each shot now carries:
- scene purpose
- mapped story beat when deterministically resolvable
- beat purpose
- shot narrative purpose
- audience knowledge target
- audience emotion target
- audience endpoint
- character performance objectives
- camera purpose
- edit intent
- sound intent
- lighting intent
- entry/exit continuity state
- camera side and motion-axis contract

Beat mapping is deterministic.
CineFactory does not invent a beat relation when it cannot resolve one; unresolved mappings
are surfaced as findings.

## Camera diagnostics

Automated pre-production checks now include:

- motivated camera movement
- CameraSpec vs WorldState camera-side consistency
- 180-degree/action-axis crossing inside a scene
- screen-direction / motion-axis changes
- missing eyeline targets
- suspicious small focal-length/framing changes
- extreme focal-length jumps
- repeated adjacent shot-size review

Hard blockers:
- unmotivated movement
- camera/world-side contradiction
- unexplained side-of-axis crossing inside a scene

Warnings remain reviewable rather than falsely blocking when ambiguity is legitimate.

## Performance Direction

Per shot / subject:
- objective
- action verb
- gaze target
- expression intent
- gesture intent
- reaction trigger
- pose readability requirement
- body-mechanics requirements
- reaction/timing rules

Core rules include:
- objective before decorative gesture
- stimulus -> recognition -> response
- readable holds after important information/emotional changes
- preserve planted foot contacts
- believable balance and weight transfer
- prop contacts must align in world space

The resulting performance direction is passed into Technical Direction and Production.

## Lighting / Color intent

Each shot receives:
- narrative purpose
- light state
- time of day
- exposure priority
- adjacent-shot continuity priority
- color intent

Global rules:
- readability and continuity before decorative contrast
- protect recurring identity/material colors
- match adjacent shots before local polish
- exposure changes require motivated story/environment change

FINISHING now emits a `color_plan`.

Important honesty constraint:
the current FFmpeg finishing path does NOT claim that professional shot-by-shot creative
grading has been executed. Shot states remain `approved=False` and carry a
`PLAN_ONLY` note until a validated executable grading adapter is integrated.

## Sound spotting -> Audio execution

Sound Spotting is no longer an unused document.

For each shot CineFactory now defines:
- ambience intent
- Foley events derived from action beats
- music intent
- dialogue priority
- silence intent capability

`AudioIntentCompiler` converts this plan into timed `AudioCue` records using cumulative
shot timing. The Audio stage therefore begins with scene/shot intent rather than an empty
AudioPlan.

## Technical Direction integration

Production handoff scene plans now receive:
- scene production objective from approved creative intent
- audience knowledge target
- audience emotion target
- per-shot intent notes
- per-character/shot performance objective notes

This preserves the Director/Story intent as tool routing and production decisions are made.

## Downstream stage dependencies

For Minecraft / Roblox professional pipeline:

CREATIVE_REVIEW consumes:
- camera_diagnostics
- performance_direction
- creative_intent_graph
- lighting_color_intent
- sound_spotting

TECHNICAL_DIRECTION consumes:
- creative_review_approval
- creative_intent_graph
- camera_diagnostics
- performance_direction
- lighting_color_intent
- sound_spotting

PRODUCTION consumes:
- creative_intent_graph
- performance_direction

EDITORIAL consumes:
- creative_intent_graph

AUDIO consumes:
- sound_spotting
- shot_book

FINISHING consumes:
- lighting_color_intent

## Niche isolation

CRAFT_EXECUTION_DESIGN is currently enabled only for:
- Minecraft
- Roblox Animation

It is intentionally NOT forced into:
- Audio Storytelling for Seniors
- Long Slices Game
- ASMR Sleep — Hands + Objects
- Fishing Silent
- Rain / Sleep / White Noise

Those niches require their own production grammar.

## Verification

Previous full-suite milestone:
- v1.6.9: 460 PASS

v1.6.10 focused craft/downstream verification:
- 19 PASS

v1.6.10 full repository verification:
- compileall PASS
- pytest 470 PASS
- failures 0

New tests cover:
- deterministic Scene -> Beat -> Shot mapping
- 180-degree axis-cross blocker
- camera/world side contradiction
- eyeline warning
- performance-direction generation
- lighting/color intent generation
- sound spotting generation
- downstream stage dependency propagation
- AudioCue timeline compilation
- transparent PLAN_ONLY ColorPlan semantics
- professional Minecraft E2E with CRAFT_EXECUTION_DESIGN

## Remaining high-priority work

1. Real animation/backend consumption of performance-direction fields:
   pose, gaze, expression, reaction timing and contact constraints.
2. Camera diagnostics using actual camera transforms/3D geometry, not only semantic contracts.
3. Real storyboard/animatic playback review rather than semantic/keyframe evidence only.
4. Executable lighting/lookdev validation against rendered frames.
5. Validated professional color-grading adapter and shot-match measurement.
6. Sound cue asset selection, generation, placement and perceptual mix QC.
7. Shot-to-shot visual/audio pairwise QC tied back to creative intent.
8. Competitor pairwise benchmark evidence before any L5/benchmark-leading claim.
