# Rendered Frame Evidence + Bounded Auto Repair v1.6.13

## Goal

Move CineFactory from geometry-only verification toward local rendered-image evidence,
typed root-cause routing, and bounded automatic local repair without paid APIs and
without inventing maturity that has not been measured.

Operating rule:

MEASURE -> CLASSIFY ROOT CAUSE -> REPAIR SMALLEST OWNING LAYER -> RERENDER -> RE-QC

This milestone measures and acts on:
- rendered head / midpoint / tail appearance
- exposure and clipping
- actor appearance consistency from actual rendered pixels
- adjacent-cut appearance continuity
- actual 3D performance and render-state continuity from v1.6.12
- typed multi-owner failure routing
- bounded local repair plans
- rerender and re-QC in direct production mode
- the same rendered evidence and repair routing in Turbo mode

The implementation is local-first and zero-API.

## Local rendered-frame QC stack

Implementation:
- FFmpeg / FFprobe
- NumPy
- Pillow
- Blender geometry-projected actor screen boxes

No network service, paid API, cloud VLM, or external recognition service is required.

Core files:
- cinefactory/block_animation/rendered_frame_qc.py
- cinefactory/block_animation/repair.py
- cinefactory/block_animation/runtime.py
- cinefactory/media/ffmpeg.py
- cinefactory/production/failure_router.py
- cinefactory/studio/block_production.py
- scripts/blender_animation_worker.py

## Blender actor projection evidence

The Blender worker captures each actor's screen-space bounding box at the actual shot midpoint.

The box comes from:
- actual instantiated actor world-space geometry
- the actual animated midpoint frame
- the actual camera transform
- Blender world_to_camera_view projection

The normalized box is stored in render_state.

Actor render state now contains:
- start root/focus state
- midpoint root/focus state
- midpoint screen_box
- end root/focus state
- rig/style identity signature

The rendered-frame analyzer uses that box to crop the encoded video instead of comparing
the whole frame as if a camera cut were a character-identity change.

## Representative rendered-frame sampling

For each candidate render CineFactory extracts:
- head frame
- midpoint frame
- tail frame

Sampling is FPS-aware and avoids seeking beyond the final decodable frame.

For each sampled frame CineFactory measures:
- mean luminance
- luminance standard deviation
- shadow clipping ratio
- highlight clipping ratio
- mean saturation
- mean RGB
- deterministic 64-bit appearance hash

Each render persists:
- <shot>.mp4.frame_qc.json

Temporary extracted PNG frames are deleted automatically.

## Lighting-intent-aware exposure QC

Exposure QC now uses the actual render-state lighting intent.

This prevents one global threshold from falsely rejecting valid night scenes while still
blocking broken daytime renders.

DAY/default intent uses stricter thresholds than NIGHT/EVENING/DUSK.

A daytime frame around:
- mean luma ~0.04
- shadow clipping ~0.52

is a hard underexposure failure.

The same signal can remain valid under explicit NIGHT intent if it stays inside the
night-specific safety range.

Current severe global blocker remains:
- shadow clip ratio > 80%
- AND mean luminance < 0.12

Current overexposure hard blocker:
- highlight clip ratio > 65%
- AND mean luminance > 0.82

Warnings are still emitted for:
- elevated shadow clipping
- elevated highlight clipping
- extremely low contrast

## Combined QC root-cause ordering

A production bug was found during real repair testing.

Before the fix:
- FFmpeg black detection could reject a very dark render first
- the failure was classified as TECHNICAL_FAIL
- CineFactory rerendered the same bad lighting contract
- the actual cause, underexposure, was never allowed to own the repair

The Runtime now follows:

1. decode/probe render
2. collect FFmpeg visual evidence
3. collect rendered-frame signal evidence
4. arbitrate root cause
5. fail with the smallest explanatory failure class

If EXCESSIVE_BLACK_FRAMES is explained by measured underexposure/overexposure:
- the darkness is treated as LOOKDEV evidence
- it is not mislabeled as renderer/codec failure

Therefore a decoded video that is dark because of bad lighting can be:
- technical_pass = true
- visual_pass = false
- failure_code = LOOKDEV_FAIL

A backend/render failure that cannot produce a valid media file remains:
- technical_pass = false
- visual_pass = false

## Rendered actor appearance evidence

At the shot midpoint the analyzer crops each actor using the Blender-projected screen box.

For each actor crop it measures:
- mean luminance
- mean saturation
- mean RGB
- 12 x 4 HSV histogram
- deterministic 64-bit appearance hash

The first accepted rendered appearance of an actor becomes the episode baseline.

Later candidates are compared against the first accepted baseline instead of only the
immediately previous shot. This prevents gradual drift from redefining the canonical
appearance.

Current actor-appearance score combines:
- HSV histogram similarity: 70%
- appearance-hash similarity: 20%
- RGB mean similarity: 10%

Current hard rendered appearance drift:
- combined score < 0.48
- OR histogram similarity < 0.38

Warning range:
- combined score < 0.62
- OR histogram similarity < 0.52

Score semantics:

RENDERED_ACTOR_APPEARANCE_CONSISTENCY_AGAINST_FIRST_ACCEPTED_BASELINE

This is a rendered-appearance consistency proxy.

It is NOT semantic face recognition and must not be described as semantic re-identification.

## Real two-shot actor appearance verification

The professional Minecraft two-shot verification was rerun after enabling pixel evidence.

Shot 1:
- passed = true
- identity_score = NOT_MEASURED
- performance_score = 1.0
- camera_score = 1.0
- continuity_score = NOT_MEASURED
- establishes the actor appearance baseline

Shot 2:
- passed = true
- aggregate score = 0.9399033112
- rendered identity/appearance score = 0.8214541674
- performance score = 1.0
- camera score = 1.0
- combined continuity score = 0.9381590776

C01:
- appearance score = 0.8545694845
- HSV histogram similarity = 0.8857082586
- appearance hash similarity = 0.765625
- RGB mean distance = 0.1205834272
- passed = true

C02:
- appearance score = 0.7883388502
- HSV histogram similarity = 0.8035263336
- appearance hash similarity = 0.65625
- RGB mean distance = 0.0349672914
- passed = true

The verification changes camera coverage between shots, so valid shot-size/composition
changes are not automatically rejected.

## Adjacent-cut appearance continuity

For adjacent accepted shots CineFactory compares:

previous accepted shot TAIL
against
current candidate shot HEAD

The measurement runs only when:
- scene_id is the same
- lighting intent is unchanged

Scene transitions are not falsely scored.

A deliberate lighting-intent change is not falsely scored as continuity failure.

Measured:
- luminance delta
- saturation delta
- RGB mean distance

Score weights:
- luminance stability: 45%
- saturation stability: 20%
- RGB stability: 35%

Current hard cut blockers:
- luminance delta > 0.28
- OR RGB distance > 0.38

## Real cut-appearance verification

Healthy same-scene Minecraft cut:
- cut appearance score = 0.8763181551
- luminance delta = 0.0175912082
- saturation delta = 0.0406511426
- RGB distance = 0.0902497768
- passed = true

3D render-state continuity:
- score = 1.0

Combined continuity:
- score = 0.9381590776

When both dimensions are measurable the score semantics are:

ADJACENT_RENDER_STATE_AND_FRAME_APPEARANCE_CONFORMANCE

Unmeasured dimensions are never filled with synthetic 1.0 values.

## Typed multi-owner failure routing

FailureRouter now supports:
- classify()
- classify_all()

A shot can contain more than one real failure.

Examples:
- camera + performance
- continuity + lookdev
- asset identity + lighting

classify_all() returns the minimal distinct repair owners rather than silently dropping all
but the first matching problem.

Supported ownership includes:

IDENTITY_DRIFT
- owner = ASSET_ENGINE

CONTINUITY_FAIL
- owner = CONTINUITY_ENGINE

CAMERA_INTENT_FAIL
- owner = CINEMATOGRAPHY_ENGINE

PERFORMANCE_FAIL
- owner = PERFORMANCE_ENGINE

ACTION_FAIL
- owner = BLOCKING_ACTION_ENGINE

LOOKDEV_FAIL
- owner = LIGHTING_COLOR_ENGINE

TECHNICAL_FAIL
- owner = RENDER_ENGINE

Narrative/story failure:
- owner = DIRECTOR_ENGINE
- not converted into a generic rerender

## Root-cause suppression

Rendered actor appearance can change because lighting changed, even if the canonical asset
itself is correct.

A real destructive verification proved this:
- the second shot was deliberately altered with brightness + saturation drift
- C02 actor appearance score fell to ~0.236
- cut appearance score fell to ~0.085

The same evidence also showed strong same-scene lookdev drift.

The router correctly produced:

LOOKDEV_FAIL
-> LIGHTING_COLOR_ENGINE
-> REBALANCE_LIGHTING_AND_COLOR

and suppressed an unnecessary ASSET_ENGINE repair because there was no structural/canonical
identity failure.

If structural identity evidence also exists, the ASSET_ENGINE directive is retained.

## Typed repair directives in Dailies

ShotDailiesReport and DailiesReport carry:

repair_directives: list[RepairDirective]

Each directive contains:
- shot_id
- failure_code
- owner
- retryable
- action
- prompt_directive
- invalidated artifacts
- original findings

TakeRecord.failure_code records why a rejected take failed.

Rejected takes never become:
- actor appearance baselines
- render-state continuity baselines

This prevents self-reinforcing drift and downstream failure cascades.

## Bounded local repair planner

Implemented in:
- cinefactory/block_animation/repair.py

LocalBlockRepairPlanner only changes reversible execution parameters.

It must not rewrite:
- story purpose
- narrative intent
- canonical assets
- canonical identity
- scene meaning
- approved continuity state

Locally supported repair classes:
- LOOKDEV_FAIL
- CAMERA_INTENT_FAIL
- PERFORMANCE_FAIL
- ACTION_FAIL
- TECHNICAL_FAIL

Not locally auto-repaired:
- canonical identity failure
- rights/security failure
- non-local continuity failure
- story/director failure
- unknown failure without a safe deterministic repair

## Lookdev auto repair

For LOOKDEV_FAIL CineFactory may modify render exposure while preserving creative intent.

When a previous accepted frame exists, exposure correction can use measured previous-tail
luminance versus current-head luminance.

When the failure is explicit UNDEREXPOSED/OVEREXPOSED without a safe reference, the repair
uses a bounded correction.

Current correction is clamped to avoid runaway changes.

Repair evidence records:
- exposure_before
- exposure_after
- exposure_delta
- preserve_creative_intent = true

## Camera local repair

For camera framing failures the local planner can conservatively:
- widen the lens/FOV
- increase framing margin
- increase horizontal safe margin
- increase vertical safe margin
- reduce camera motion strength

It preserves:
- shot purpose
- target semantics
- creative intent

## Performance/action local repair

For retryable performance/action failures the local planner can:
- raise insufficient action intensity conservatively
- bound action speed to a stable execution range
- enforce full gaze cue intensity

It does not invent a new story action.

## Technical local repair

For retryable technical failures the repair plan can rerender the same approved contract.

This does not mutate creative intent.

## Direct production auto-repair loop

BlockAnimationProducer.produce() now supports a bounded loop.

Default:
- max_repair_rounds = 2

Per shot:

candidate take 1
-> render
-> collect QC
-> classify failure(s)
-> build local repair plan
-> rerender candidate take 2
-> re-QC
-> optional candidate take 3
-> select only an accepted take

Every attempt remains in ShotDailiesReport.takes.

A failed take records:
- repair_round
- failure_code
- findings
- repair_plan_next

The final selected take is the first take that satisfies all active hard gates.

If the failure is unsupported/non-retryable:
- auto repair stops
- the unresolved repair directive is returned upstream

## Real Blender auto-repair stress verification

A real Minecraft shot was deliberately compiled with:

render exposure = -3.0 EV

Round 0:
- exposure = -3.0
- encoded render existed
- technical_pass = true
- visual_pass = false
- measured underexposure at HEAD/MID/TAIL
- failure = LOOKDEV_FAIL
- owner = LIGHTING_COLOR_ENGINE

Repair 1:
- -3.0 EV -> -1.5 EV

Round 1:
- technical_pass = true
- visual_pass = false
- still underexposed under DAY intent

Repair 2:
- -1.5 EV -> 0.0 EV

Round 2:
- technical_pass = true
- visual_pass = true
- frame QC passed
- selected take = S01_BLENDER_03
- remaining repair directives = none

Accepted frame evidence at 0 EV:
- head luma ~0.1041
- midpoint luma ~0.1041
- tail luma ~0.1041
- shadow clipping ~0.231
- highlight clipping = 0

This demonstrates a real:

FAIL -> ROOT CAUSE -> REPAIR -> RERENDER -> RE-QC -> ACCEPT

cycle through Blender rather than only a mocked/unit-test loop.

Verification artifact:
- data/verification/v173_auto_repair/auto_repair_verification.json

## Deliberate rendered-drift verification

A healthy second Minecraft render was deliberately modified with FFmpeg:
- brightness +0.35
- saturation x2.0
- contrast x1.10

Measured:
- C02 appearance score ~0.236
- C02 histogram similarity ~0.141
- cut luma delta ~0.333
- cut RGB distance ~0.566
- cut appearance score ~0.085

Result:
- cut failed
- appearance drift detected
- root cause classified as LOOKDEV_FAIL
- repair owner = LIGHTING_COLOR_ENGINE
- ASSET_ENGINE repair suppressed because no canonical/structural identity failure existed

Verification artifact:
- data/verification/v173_rendered_repair/rendered_repair_verification.json

## Direct vs Turbo status

Both direct and Turbo production receive:
- Blender geometry QC
- performance QC
- rendered-frame QC
- actor appearance evidence
- cut appearance evidence
- Dailies scoring
- typed repair routing

Direct production additionally has the new bounded executable local repair->rerender loop.

Turbo currently emits the same typed repair directives but does not yet automatically enqueue
replacement Turbo work items from those directives.

This gap is explicit and must not be hidden.

## Tests

New/expanded coverage includes:
- local FFmpeg frame extraction
- actor screen-box crop evidence
- actor appearance comparison
- hard rendered appearance drift
- same-scene cut appearance
- scene-transition non-measurement
- DAY vs NIGHT exposure thresholds
- LOOKDEV routing
- multi-owner repair routing
- lookdev root-cause suppression of false asset repair
- structural identity preserving asset repair
- local lookdev repair contract
- local camera repair contract
- unsupported identity auto-repair
- bounded Producer retry loop
- technical-pass vs visual-pass semantics
- repair evidence in failed takes
- successful repaired take selection

Targeted latest verification:
- 26 PASS

Full repository verification:
- compileall PASS
- pytest 502 PASS
- failures = 0

Previous milestone:
- v1.6.12 = 485 PASS

Current milestone:
- v1.6.13 = 502 PASS

## Important non-claims

v1.6.13 does NOT yet prove:
- semantic face recognition
- person re-identification comparable to a trained vision system
- pixel-perfect segmentation
- optical-flow continuity around exact edit boundaries
- costume-specific semantic recognition
- CIE Lab / DeltaE professional color matching
- perceptual audio mix quality
- expert-human aesthetic judgment
- competitor-superiority
- Disney-level production maturity

The system now has stronger measurable supervision and one real bounded self-repair loop,
but those larger claims require separate evidence.

## Next high-priority layer

1. Turbo-native repair work re-enqueue and retry budgets
2. render masks / actor mattes to reduce background contamination in actor appearance crops
3. pose / silhouette evidence from actual rendered frames
4. optical-flow / motion-boundary continuity around edits
5. perceptual CIE Lab / DeltaE color matching
6. costume and prop rendered-identity evidence
7. perceptual dialogue / SFX / music / loudness and masking QC
8. automatic repair adapters for those new measured dimensions
9. pairwise competitor/reference craft benchmark before any L5 / benchmark-leading claim
