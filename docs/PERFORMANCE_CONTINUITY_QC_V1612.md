# 3D Performance & Render Continuity QC v1.6.12

## Goal

Measure actual 3D execution quality rather than assuming that a successful render
means the intended performance and continuity were delivered.

This milestone adds measurable Blender evidence for:
- action execution
- gaze accuracy
- foot/ground contact
- body balance
- hand/prop attachment
- rig structure identity conformance
- adjacent-shot continuity
- lighting-control continuity

Pixel-level rendered identity recognition is intentionally still NOT_MEASURED.

## Blender-side 3D Performance QC

The persistent Blender worker now evaluates animated scene geometry before accepting
a render.

### Action execution

Procedural action cues are checked at actual animation frames.

Examples:
- point / push / grab / wave:
  right-arm rotation delta must be measurable
- walk / run:
  root displacement must exceed movement threshold
- jump:
  root vertical lift must exceed threshold
- fall:
  root pitch rotation must exceed threshold
- shock_recoil / flinch:
  root reaction transform must change
- turn_head:
  head yaw must change

External armature actions that do not expose procedural controls are explicitly marked
NOT_MEASURED rather than being falsely passed or failed.

## Gaze accuracy

Gaze is now evaluated after animation at the cue midpoint.

The worker compares:
- actual head local forward vector in world space
- vector from head/focus point to intended target

Current pass threshold:
- <= 28 degrees

The professional Minecraft verification achieved:
- C01 -> C02: 0.0 degrees in the first verification render
- two-shot verification: approximately 0.96 degrees
- C02 -> C01: same measured behavior

## Foot / ground contact

For each actor the worker samples:
- first frame
- midpoint
- last frame

It evaluates world-space foot/leg bounding boxes.

Current rules:
- ground penetration below -0.12 is a blocker
- static/non-jump/non-fall performance must retain ground contact
- contact threshold is <= 0.14 above ground

Real Minecraft verification:
- sampled foot minimum Z = 0.0 for the base shot
- second verification shot remained within contact tolerance
- no penetration blockers

## Balance / weight-support proxy

For non-fall poses, the actor root XY projection is compared with the world-space
support bounds of the feet/legs.

The support polygon proxy is expanded by a small margin for stylized block rigs.

A root outside that support region is a hard blocker.

This is a geometry-based balance proxy, not a biomechanics simulation.

## Prop contact

Handheld props are now checked at an active frame.

The QC validates:
- prop object exists
- expected socket/bone exists
- actual parent matches the expected socket/bone
- prop is visible during the active range
- world-space prop-to-socket distance is within the allowed attachment envelope

Important bug found and fixed during this milestone:
the first implementation incorrectly measured prop local location after parenting.
A real Minecraft-book verification exposed a false distance of 4.477.

The QC was corrected to world-space socket distance.

Real verification after the fix:
- prop: minecraft_book
- actor: A
- socket: right_hand
- bone_name: hand.R
- actual parent: A_armR
- expected parent: A_armR
- world distance: ~0.856
- visible: true
- passed: true

External armature/bone parenting is also handled separately so a real .blend armature
is not judged using procedural mesh-part assumptions.

## Scene-rig identity conformance

The worker validates actual instantiated rig structure:
- expected style vs actual style
- required procedural parts for procedural Minecraft/Roblox rigs
- actual armature presence for external rigs

It emits:
SCENE_RIG_STRUCTURE_CONFORMANCE_NOT_PIXEL_IDENTITY

This is useful structural identity evidence, but CineFactory still leaves the public
TakeRecord identity_score as None / NOT_MEASURED because rendered-frame identity
recognition has not yet been benchmarked.

## Render-state capture

Every accepted Blender shot can now return an actual render state containing:
- shot_id
- scene_id
- start/end frame
- actor root positions
- actor root rotations
- actor focus points
- stable 3D identity signatures
- prop parent/socket/world location state
- actual camera start/end transform and lens
- actual lighting controls
- creative-intent binding state

This becomes the evidence used for adjacent-shot continuity.

## Adjacent render continuity

Implemented in:
cinefactory/block_animation/render_continuity.py

The Producer compares:
previous accepted shot END
against
current rendered shot START

Only when:
- both states exist
- scene_id is non-empty
- both shots belong to the same scene

Scene transitions are deliberately NOT scored as continuity failures.

### Same-scene checks

Actors:
- stable scene identity signature
- root position continuity
- root yaw continuity

Props:
- parent/socket continuity
- world-position continuity

Lighting:
- when light_state and time_of_day intents are unchanged,
  actual key/fill/rim/world controls must remain stable

Current hard thresholds:
- actor root jump > 0.75 -> blocker
- actor yaw jump > 1.0 rad -> blocker
- prop world jump > 0.85 -> blocker
- same-intent lighting relative drift > 25% -> blocker

Smaller drift ranges are surfaced as warnings.

## Real two-shot continuity verification

Verification artifact:
data/verification/v172_continuity/continuity_verification.json

Result:
- episode passed
- shot 1:
  performance_score = 1.0
  camera_score = 1.0
  continuity_score = NOT_MEASURED because no previous shot
- shot 2:
  performance_score = 1.0
  camera_score = 1.0
  continuity_score = 1.0

Measured shot-2 continuity included:
- C01 identity signature MATCH
- C02 identity signature MATCH
- C01 root-position delta ~0.0419
- C02 root-position delta 0.0
- root yaw delta 0.0
- key/fill/rim/world lighting relative drift 0.0

## Dailies semantics

TakeRecord now distinguishes:

Measured:
- camera_score = geometry framing/occlusion conformance
- performance_score = measured 3D action/gaze/contact/balance conformance
- continuity_score = adjacent actual-render-state conformance when measurable

Not yet measured:
- identity_score = None

Evidence contains:
- geometry_qc
- identity_qc
- performance_qc
- render_state
- render_continuity
- lighting_debug
- visual_qc

Aggregate score is the mean only of dimensions actually measured.

If a shot fails, its render state is not carried forward as the continuity baseline.
This prevents one rejected shot from creating a cascade of false downstream failures.

## Real verification evidence

Single-shot craft verification:
- data/verification/v171/intent_preview.mp4
- data/verification/v171/intent_preview.mp4.geometry_qc.json

Prop contact verification:
- data/verification/v172_prop/prop_contact_verification.json

Two-shot continuity verification:
- data/verification/v172_continuity/continuity_verification.json

## Tests

New:
- tests/test_render_continuity_v172.py

Coverage includes:
- stable same-scene continuity
- actor position jump blocker
- scene transition not falsely measured
- identity-signature change blocker
- same-intent lighting drift blocker
- Dailies integration with 3D performance and continuity evidence
- continuity failure blocking professional execution score

## Verification

Previous milestone:
- v1.6.11: 478 PASS

v1.6.12 targeted regression:
- 27 PASS

Real Blender:
- 3D action QC PASS
- gaze accuracy PASS
- foot contact PASS
- balance PASS
- prop contact PASS
- rig structure identity PASS
- two-shot render continuity PASS

Full repository:
- compileall PASS
- pytest 485 PASS
- failures 0

## Remaining quality gaps

The next major layer should be rendered-image/audio evidence:

1. pixel-level character identity measurement from rendered frames
2. shot-to-shot image appearance matching
3. lighting/readability/exposure measurement from actual frames
4. costume/prop visual identity verification
5. optical-flow / pose continuity around cuts
6. sound asset placement and perceptual mix QC
7. automatic repair routing from these measured defects
8. competitor pairwise craft benchmark for maturity L5 evidence

CineFactory must not claim these dimensions are solved until they are independently measured.
