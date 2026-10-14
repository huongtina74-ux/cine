# Rendered Evidence + Root-Cause Auto-Repair v1.6.13

## Goal

Move CineFactory from structural/render-success QC into measured rendered-frame evidence,
root-cause-aware failure routing, and bounded autonomous local repair.

This milestone adds a closed local loop:

RENDER
-> COLLECT STRUCTURAL + PIXEL EVIDENCE
-> CLASSIFY ROOT CAUSE
-> ROUTE TO SMALLEST OWNER
-> APPLY SAFE LOCAL REPAIR WHEN SUPPORTED
-> RERENDER
-> RE-MEASURE
-> ACCEPT ONLY A PASSING TAKE

The loop is deliberately bounded and does not rewrite story, canonical identity, or
complex continuity state.

## Rendered-frame evidence

Implemented in:
- cinefactory/block_animation/rendered_frame_qc.py

Dependencies:
- local FFmpeg / FFprobe
- NumPy
- Pillow
- no cloud model
- no paid API

For every accepted render the runtime samples:
- head frame
- midpoint frame
- tail frame

Measured frame signals include:
- mean luminance
- luminance standard deviation
- shadow clipping ratio
- highlight clipping ratio
- mean saturation
- mean RGB
- 64-bit average hash

## Actor appearance evidence

Blender render-state capture now includes a mid-shot actor screen-space box computed
from actual 3D actor geometry projected through the real camera.

The rendered-frame analyzer crops each actor from the actual encoded video and stores:
- crop size
- mean luminance
- mean saturation
- mean RGB
- HSV histogram
- average hash

This is explicitly an appearance-consistency proxy.
It is not semantic face recognition.

## Rendered actor appearance consistency

The first accepted appearance for each actor becomes the episode baseline.

Later accepted candidates are compared against that baseline using:
- HSV histogram cosine similarity
- average-hash similarity
- RGB mean distance

Current score:
- 70% HSV histogram
- 20% average hash
- 10% bounded RGB-distance contribution

A strong mismatch creates:
RENDERED_IDENTITY_DRIFT

This measurement is now allowed to populate TakeRecord.identity_score, with semantics:

RENDERED_ACTOR_APPEARANCE_CONSISTENCY_AGAINST_FIRST_ACCEPTED_BASELINE

It does not claim human-level identity recognition.

## Real two-shot rendered evidence

Minecraft two-shot verification remained accepted.

Shot 2 measured:
- identity appearance score: 0.821454
- C01 appearance score: 0.854569
- C01 histogram similarity: 0.885708
- C02 appearance score: 0.788339
- C02 histogram similarity: 0.803526
- cut appearance score: 0.876318
- 3D continuity score: 1.0

Measured cut deltas:
- luminance delta: 0.017591
- saturation delta: 0.040651
- RGB distance: 0.090250

No repair directive was produced for the valid two-shot episode.

Evidence:
- data/verification/v172_continuity/continuity_verification.json
- per-shot *.frame_qc.json sidecars

## Cut appearance continuity

For adjacent shots in the same scene, when lighting intent is unchanged, CineFactory
compares the previous tail frame with the current head frame.

Measured:
- luminance delta
- saturation delta
- RGB mean distance

It combines this with the existing actual 3D render-state continuity.

The Dailies continuity semantics can therefore become:

ADJACENT_RENDER_STATE_AND_FRAME_APPEARANCE_CONFORMANCE

Scene transitions or deliberate lighting-intent changes are not falsely scored as
same-look continuity failures.

## Exposure / clipping QC with lighting intent

Rendered-frame QC now distinguishes ordinary/day scenes from intentionally low-light
night/evening/dusk scenes.

Default/day hard underexposure proxy:
- shadow clipping > 45%
- AND mean luminance < 0.055

Default/day shadow warning threshold:
- > 36%

Night/evening/dusk hard proxy is more permissive:
- shadow clipping > 86%
- AND mean luminance < 0.035

Night shadow warning threshold:
- > 68%

A universal severe-underexposure guard remains in place.

This avoids approving obviously crushed daylight while not forcing a night scene to
look like daylight.

## Evidence-first root-cause arbitration

Runtime now collects both:
- FFmpeg black/freeze evidence
- rendered pixel exposure evidence

before final failure classification.

Important real failure found:
an intentionally underexposed Blender render originally triggered:
EXCESSIVE_BLACK_FRAMES

and was incorrectly routed as:
TECHNICAL_FAIL -> RENDER_ENGINE

The runtime was changed so decoded darkness that is explained by measured
underexposure is routed as a LookDev problem instead of a renderer/codec failure.

Principle:
COLLECT EVIDENCE FIRST -> CLASSIFY ROOT CAUSE SECOND

## Root-cause failure routing

FailureCode now includes:
- LOOKDEV_FAIL

LookDev failures route to:
- owner: LIGHTING_COLOR_ENGINE
- action: REBALANCE_LIGHTING_AND_COLOR

Identity appearance drift normally routes to:
- ASSET_ENGINE

However, when rendered identity drift co-occurs with explicit whole-shot lookdev/color
drift and no structural/canonical identity failure exists, asset repair is suppressed.
CineFactory repairs the smaller causal layer first.

This prevents lighting/color mistakes from causing unnecessary character asset changes.

## Multi-owner repair plans

FailureRouter now provides classify_all().

A shot can return several independent owners, for example:
- camera -> CINEMATOGRAPHY_ENGINE
- performance -> PERFORMANCE_ENGINE
- lookdev -> LIGHTING_COLOR_ENGINE

Duplicate repair actions are consolidated.

Root-cause suppression is applied when one measured failure plausibly explains another.

## Dailies repair directives

ShotDailiesReport and DailiesReport now carry:
- repair_directives

TakeRecord continues to store:
- failure_code
- findings
- evidence
- score semantics
- repair_round

This makes the QC report directly actionable instead of only descriptive.

## Bounded local auto-repair

Implemented in:
- cinefactory/block_animation/repair.py
- cinefactory/studio/block_production.py

Default:
- max_repair_rounds = 2
- therefore maximum local attempts per shot = 3

Flow:

TAKE 1
-> fail
-> route
-> safe local repair
-> TAKE 2
-> re-measure
-> optional second repair
-> TAKE 3
-> accept only if QC passes

Rejected takes remain in Dailies evidence.

The selected take is never a failed take.

## Locally supported repair classes

### LOOKDEV_FAIL

Safe repair:
- adjust render exposure only
- preserve story
- preserve shot purpose
- preserve camera/performance contract
- retain repair metadata

When previous accepted frame evidence exists, exposure correction can use luminance
ratio against the previous cut.

Without a trusted reference:
- UNDEREXPOSED -> conservative +1.5 EV step
- OVEREXPOSED -> conservative -1.5 EV step

Exposure remains clamped to the existing render-quality limits.

### CAMERA_INTENT_FAIL

Safe local repair can:
- widen field of view by lowering lens focal length
- increase framing margin
- increase horizontal/vertical safe margins
- reduce excessive camera motion strength

It does not change narrative shot purpose or targets.

### PERFORMANCE_FAIL / ACTION_FAIL

Safe local repair can:
- strengthen approved action intensity within limits
- normalize unreasonable speed
- strengthen approved gaze intensity

It does not invent a new action.

### TECHNICAL_FAIL

Safe local behavior:
- rerender the same contract

It does not mutate story/craft intent.

## Deliberately unsupported local auto-repairs

CineFactory does not locally auto-repair:
- RIGHTS_FAIL
- SECURITY_FAIL
- canonical IDENTITY_DRIFT
- complex CONTINUITY_FAIL
- non-retryable DIRECTOR/STORY failures

These remain routed upstream.

The local repair planner marks them unsupported rather than silently changing assets,
story, or world state.

## Real injected lookdev-drift verification

A valid rendered Minecraft shot was modified locally with FFmpeg:
- brightness +0.35
- saturation 2.0
- contrast 1.10

Measured result:
- C01 appearance score: 0.691168
- C02 appearance score: 0.235507
- C02 histogram similarity: 0.140536
- cut appearance score: 0.084716
- luminance cut delta: 0.332958
- RGB cut distance: 0.565999

Observed findings:
- RENDERED_IDENTITY_DRIFT:C02
- CUT_APPEARANCE_DRIFT

Root-cause routing result:
- LOOKDEV_FAIL
- owner: LIGHTING_COLOR_ENGINE
- action: REBALANCE_LIGHTING_AND_COLOR

ASSET_ENGINE was correctly suppressed because the global lookdev drift plausibly
explained the rendered identity proxy drift and there was no structural identity error.

Evidence:
- data/verification/v173_rendered_repair/rendered_repair_verification.json
- data/verification/v173_rendered_repair/shot2_lookdev_drift.mp4

## Real autonomous Blender repair verification

A real Minecraft Blender shot was forced to:
- exposure = -3.0 EV

Attempt 1:
- exposure: -3.0
- technical_pass: true
- visual_pass: false
- measured underexposure on HEAD/MID/TAIL
- routed LOOKDEV_FAIL -> LIGHTING_COLOR_ENGINE
- repair: -3.0 -> -1.5 EV

Attempt 2:
- exposure: -1.5
- technical_pass: true
- visual_pass: false
- still measured underexposed under the stricter day profile
- repair: -1.5 -> 0.0 EV

Attempt 3:
- exposure: 0.0
- technical_pass: true
- visual_pass: true
- selected take: S01_BLENDER_03
- head luminance: ~0.10414
- shadow clipping: ~23.16%
- frame warnings: none

The two rejected takes remained recorded.
No remaining repair directive existed after the third take passed.

Evidence:
- data/verification/v173_auto_repair/auto_repair_verification.json
- data/verification/v173_auto_repair/renders/block_animation/shots/

## New and modified key files

New:
- cinefactory/block_animation/rendered_frame_qc.py
- cinefactory/block_animation/repair.py
- tests/test_rendered_frame_qc_v173.py
- tests/test_block_auto_repair_v173.py
- scripts/verify_rendered_repair_v173.py
- scripts/verify_auto_repair_v173.py

Modified:
- scripts/blender_animation_worker.py
- cinefactory/media/ffmpeg.py
- cinefactory/block_animation/runtime.py
- cinefactory/studio/block_production.py
- cinefactory/production/contracts.py
- cinefactory/production/failure_router.py
- cinefactory/domain/enums.py
- tests/test_failure_router.py
- scripts/verify_continuity_v172.py

## Verification

Previous milestone:
- v1.6.12: 485 PASS

v1.6.13 targeted final regression:
- 37 PASS

Real Blender / media verification:
- valid two-shot rendered appearance PASS
- actor appearance consistency PASS
- cut appearance continuity PASS
- injected lookdev drift DETECTED
- root-cause repair routing PASS
- real -3 EV autonomous repair PASS
- bounded three-take selection PASS
- technical-vs-lookdev semantics PASS

Full repository:
- compileall PASS
- pytest 504 PASS
- failures 0

## Remaining high-priority gaps

1. Turbo/distributed path still routes repair directives but does not yet enqueue bounded repair work automatically.
2. Rendered identity remains a color/appearance proxy, not a benchmarked semantic identity model.
3. Appearance comparison should eventually include segmentation/object masks so background contamination is reduced.
4. Pose/optical-flow continuity directly across the edit boundary is not yet measured.
5. Audio evidence still needs perceptual loudness, clipping, silence, dialogue intelligibility and continuity QC.
6. Auto-repair effectiveness needs production metrics: repair success rate, rounds, regression rate, wasted GPU seconds.
7. Cross-shot repair needs a dependency invalidation graph so a repaired shot can selectively invalidate downstream approvals.
8. Competitor pairwise craft benchmark remains required before any benchmark-leading/L5 quality claim.
9. Turbo auto-repair and scheduler-level cost/quality budgeting should be the next execution-system milestone.

CineFactory must continue to distinguish:
- measured evidence
- proxy evidence
- inferred causes
- unmeasured claims
