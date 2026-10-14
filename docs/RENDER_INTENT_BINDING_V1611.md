# Render Intent Binding + Geometry QC v1.6.11

## Goal

Convert approved Story/Director/Craft intent into executable Blender/block-animation
controls and refuse to claim quality dimensions that were not actually measured.

This milestone closes the gap between:
- creative intent contracts
- block-animation episode contracts
- Blender execution plans
- real Blender scene transforms
- render-time camera evidence
- Dailies scoring

## Company -> Block backend binding

CompanyToBlockAdapter now accepts:
- CreativeIntentGraph
- PerformanceDirectionPlan
- LightingColorIntentPlan

For each shot the adapter binds:
- creative intent metadata
- per-subject performance directives
- lighting intent
- action cues
- expression cues
- gaze cues
- supported reaction triggers
- camera pattern derived from shot camera grammar

Legacy callers remain supported. If professional craft contracts are absent,
the deterministic v1.6 fallback behavior remains available.

## Performance binding

Performance directives are translated into executable block-animation cues.

Current supported action mapping includes:
- run / sprint / chase -> run
- walk / approach / cross -> walk
- point -> point
- wave -> wave
- push -> push
- grab / take / pick up -> grab
- jump -> jump
- fall -> fall
- flinch -> flinch
- recoil / shock -> shock_recoil
- look / turn / notice -> turn_head

Expression intent maps into the existing expression library.

GazeCue is a new block-animation contract:
- actor_id
- target_actor_id or target_point
- start/end time
- intensity

Episode assembly validates gaze actors and targets and fail-closes on invalid references.

## Blender gaze execution

The persistent Blender worker now consumes gaze cues.

For procedural Minecraft/Roblox rigs it:
1. resolves a head control
2. resolves the world-space target
3. computes local yaw/pitch relative to actor root
4. bounds rotations to safe ranges
5. keys the head at the requested timing
6. emits gaze execution evidence

Gaze is no longer only a planning note.

## Lighting intent execution

The Blender worker now receives the shot LightingColorIntent.

Current executable rules include:
- soft-light intent modifies key/fill balance
- night/evening/dusk modifies energy, color and world contribution
- sunset/golden-hour modifies key/rim warmth
- default visual-style multipliers remain deterministic

The worker emits a lighting_debug record with actual energies and whether intent was bound.

This is executable lighting intent, but it is not yet a claim of final lookdev/color
superiority. The v1.6.10 ColorPlan remains PLAN_ONLY until a validated grading path exists.

## Geometry-aware camera QC

A new Blender-side gate runs before animation render.

It uses actual scene/camera/actor geometry and:
- world_to_camera_view projection
- shot safe-frame margins
- actual camera location
- actual head/focus point
- Blender scene ray_cast

For every required camera target it verifies:
- target is in front of camera
- target is inside horizontal/vertical safe frame
- camera ray reaches the intended actor instead of an occluder

Current hard blockers:
- CAMERA_TARGETS_MISSING
- TARGET_BEHIND_CAMERA
- TARGET_OUTSIDE_SAFE_FRAME
- TARGET_OCCLUDED

If geometry QC fails, Blender raises GEOMETRY_CAMERA_QC_FAILED before the expensive
animation render is accepted.

The worker writes:
- <shot>.mp4.geometry_qc.json

The sidecar includes:
- geometry QC
- gaze execution evidence
- lighting evidence
- creative intent
- performance directives

## Runtime fail-closed behavior

BlockAnimationRuntime reads the Blender worker result.
A failed geometry_qc is a hard render QC failure.

Successful runtime results now preserve:
- geometry_qc
- geometry_qc_sidecar
- gaze_debug
- lighting_debug
- creative_intent_bound
- performance_directive_count
- existing FFmpeg visual QC

## Evidence-based Dailies

BlockAnimationProducer no longer assigns perfect semantic scores by assumption.

Measured dimensions:
- camera_score = geometry framing/occlusion conformance
- performance_score = gaze execution conformance

Unmeasured dimensions:
- identity_score = None / NOT_MEASURED
- continuity_score = None / NOT_MEASURED

Aggregate score is the mean of measured execution-conformance dimensions only.

This prevents a technically successful render from being mislabeled as fully verified
character identity or continuity quality.

Turbo path also separates:
- technical_pass = render/backend success
- visual_pass = execution/craft conformance

A semantic failure therefore no longer corrupts technical failure statistics.

## Real Blender verification

Executable:
- .tools/blender-4.5.14-windows-x64/blender.exe

Verification render:
- data/verification/v171/intent_preview.mp4

Result:
- geometry_qc.passed = true
- no geometry blockers
- C01 projected inside safe frame; ray hit C01_head
- C02 projected inside safe frame; ray hit C02_head
- both gaze directives applied
- lighting intent bound
- FFmpeg visual QC passed
- black_seconds = 0
- freeze_seconds = 0

Observed camera evidence:
- horizontal safe margin: 0.12
- vertical safe margin: 0.14
- camera location came from the real Blender scene
- raycast hit actual actor head meshes

Observed lighting evidence for motivated-soft / DAY:
- key_energy = 1013.76
- fill_energy = 501.76
- rim_energy = 640.0
- world_strength = 0.5

## Real Dailies verification

Verification:
- data/verification/v171_dailies/dailies_evidence.json

Result:
- Dailies passed
- technical_pass = true
- visual_pass = true
- performance_score = 1.0
- camera_score = 1.0
- identity_score = null / NOT_MEASURED
- continuity_score = null / NOT_MEASURED
- creative_intent_bound = true
- performance_directive_count = 2
- no findings

The 1.0 scores above mean execution conformance for the dimensions measured in this
verification shot. They are not a claim of universal Disney-level animation quality.

## Verification suite

Previous milestone:
- v1.6.10: 470 PASS

v1.6.11 targeted compatibility:
- block-animation compatibility: 22 PASS
- intent binding/runtime tests: 8 PASS
- real Blender render: PASS
- real BlockAnimationProducer/Dailies path: PASS

v1.6.11 full repository:
- compileall PASS
- pytest 478 PASS
- failures 0

## Key modified/new files

- cinefactory/block_animation/contracts.py
- cinefactory/block_animation/assembler.py
- cinefactory/block_animation/qc.py
- cinefactory/block_animation/execution.py
- cinefactory/block_animation/runtime.py
- cinefactory/studio/block_adapter.py
- cinefactory/studio/block_production.py
- cinefactory/studio/company_handlers.py
- scripts/blender_animation_worker.py
- scripts/verify_craft_render_v171.py
- scripts/verify_dailies_v171.py
- tests/test_render_intent_binding_v171.py

## Remaining high-priority gap

The next major gap is no longer basic intent transport.

Next priorities:
1. actual body-pose / gesture / contact validation using 3D transforms
2. identity measurement from rendered frames rather than NOT_MEASURED
3. shot-to-shot continuity measurement from rendered evidence
4. lighting/readability measurement on rendered frames
5. pairwise adjacent-shot visual matching
6. sound asset placement + perceptual mix QC
7. automatic repair routing from measured render defects
8. competitor-pair craft benchmark before any benchmark-leading/L5 claim
