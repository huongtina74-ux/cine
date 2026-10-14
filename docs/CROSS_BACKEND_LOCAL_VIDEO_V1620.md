# CineFactory v1.6.20 — Cross-Backend Block-Shot Normalization + Local Video Backend

## Goal

v1.6.20 turns the previously unresolved ComfyUI video method into a real, local,
evidence-gated production backend for the subset of shots it can safely support.

The verified path is:

BLENDER METHOD FAIL / ALTERNATIVE REQUIRED
-> ProductionMethodSwitchController
-> canonical block-shot normalization
-> reference-conditioned Wan2.1-Fun Inpaint 1.3B
-> Turbo GPU work
-> ComfyUI local execution
-> canonical MP4 normalization
-> visual/frame/identity/contract QC
-> continuation
-> timeline.accept
-> episode assembly

The system still fails closed for unsupported shot requirements.

## Backend

Production method:

comfyui.wan21.fun.inpaint.1.3b

Execution handler:

block.video.comfy

Execution mode:

COMFY_VIDEO

Capability:

comfyui.local.video

Workflow:

comfy.wan21.fun.inpaint.1.3b@1

Normalizer:

blockvideo.wan21.fun.inpaint.v1

Backend profile:

WAN21_FUN_INPAINT_13B

## Exact local model bundle

Diffusion model:

.tools/ComfyUI/models/diffusion_models/
wan2.1_fun_inp_1.3B_bf16.safetensors

Bytes:

3,128,957,992

SHA-256:

8495d2b1673ffb18abb548a64ff3b0e4bd367734f653096f7a8a3ad46954d511

Text encoder:

.tools/ComfyUI/models/text_encoders/
umt5_xxl_fp8_e4m3fn_scaled.safetensors

Bytes:

6,735,906,897

SHA-256:

c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68

VAE:

.tools/ComfyUI/models/vae/
wan_2.1_vae.safetensors

Bytes:

253,815,318

SHA-256:

2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b

CrossBackendVideoService verifies all three local component hashes before production use.

## Model governance

Model registry record:

wan2.1-fun-inpaint-1.3b

Revision:

sha256:8495d2b1673ffb18abb548a64ff3b0e4bd367734f653096f7a8a3ad46954d511

License fields:

- code_license: Apache-2.0
- weights_license: Apache-2.0
- commercial_use_reviewed: true
- output_terms_reviewed: true

At the start of v1.6.20:

approved_for_production: false

The model was not promoted merely because the files existed or a smoke render worked.

## Canonical cross-backend contract

New/existing service:

cinefactory/studio/cross_backend_video.py

Canonical request:

CanonicalBlockVideoRequest

The contract carries:

- project id
- episode id
- shot id
- backend id
- normalizer id
- workflow id/version
- model id/revision
- prompt
- negative prompt
- width/height
- fps
- frame count
- normalized duration
- deterministic seed
- reference-conditioning contract
- camera-intent contract
- recurring-identity requirement
- semantic-performance requirement
- source visual style
- scene id
- canonical output path
- preview/production mode

The generative backend therefore does not receive an unstructured prompt alone.

## Block shot -> video normalization

The normalizer derives:

- reference image/video
- actor ids
- rig ids
- scene id
- visual style
- camera purpose
- shot size
- motion intent
- lens
- camera targets
- actions
- expressions
- selected creative-intent fields
- deterministic seed
- duration/FPS/frame count
- output resolution

The normalizer also adds explicit negative constraints for:

- identity drift
- clothing changes
- extra/missing limbs
- face/hand deformation
- camera teleport
- flicker
- temporal inconsistency
- duplicated characters
- background warp
- text/subtitles/watermarks
- severe exposure/blur failures

## Reference staging

CrossBackendVideoService accepts:

- reference image
- reference video

For video references, it deterministically extracts a frame and stages it into:

.tools/ComfyUI/input/

with a content-derived filename.

Reference evidence includes:

- source kind
- source path
- SHA-256
- staged filename
- actor ids
- rig ids

## Initial smoke result

Verifier:

scripts/verify_wan_smoke_v180.py

The first local reference-conditioned Wan smoke test succeeded.

Observed:

- Turbo state: SUCCESS
- canonical output: MP4
- duration: 1.0625 seconds
- FPS: 16
- visual QC: PASS
- rendered-frame QC: PASS
- recurring identity measured: true
- identity score: 0.9689097336
- semantic performance requirement: not requested
- exact camera geometry: not requested
- normalizer id preserved

Evidence:

data/verification/v180_cross_backend/
wan_smoke/
wan_smoke_verification.json

## Why one smoke test was not enough

Production approval remained false after the smoke test.

A multi-shot qualification controller was added instead.

New module:

cinefactory/studio/video_backend_qualification.py

Core objects:

- VideoQualificationPolicy
- VideoQualificationCase
- VideoBackendQualificationAttestation
- VideoBackendQualificationStore
- VideoBackendQualificationController

## Qualification policy

Default hard requirements:

- at least 2 runtime cases
- bundle hashes PASS
- ComfyUI tool qualification PASS
- commercial-use review PASS
- output-terms review PASS
- workflow/model/profile match
- backend contract match
- output media exists
- QC PASS
- recurring identity measured
- identity >= 0.80 per case
- multi-shot benchmark minimum dimension >= 0.80

The controller uses worst-case dimension scores, not average alone.

## First multi-shot qualification attempt

Two real Wan cases were generated with two deterministic seeds.

Case 1:

identity = 0.98491199997

PASS

Case 2:

identity = 0.66998877935

FAIL

Observed matrix:

- mean identity = 0.82745038966
- minimum identity = 0.66998877935

Result:

qualification = FAIL

Blockers:

- VIDEO_IDENTITY_SCORE_BELOW_FLOOR
- BENCHMARK_DIMENSION_BELOW_FLOOR:identity:0.6700

The model registry remained unapproved.

This is important: a strong average did not hide a bad seed/case.

## Root cause

Both cases used references with the same reference-frame SHA-256.

The difference was therefore not caused by a different identity reference.

The second seed generated substantially different head-frame color/luminance and lower
reference-anchor similarity.

The runtime workflow was using only a temporal start-image anchor.

## Identity anchoring improvement

The Wan-Fun inpaint node supports both:

- start_image
- end_image

v1.6.20 now uses the canonical reference at both temporal boundaries.

Dynamic workflow binding:

start_image -> canonical reference
end_image   -> same canonical reference

This constrains temporal identity drift while still generating the frames between the
anchors.

The qualification floor was not reduced.

## Second multi-shot qualification

After dual temporal anchoring, the same two-case qualification was rerun.

Case 1 identity:

0.98657898899

Case 2 identity:

0.98048360711

Observed minima:

- quality = 1.0
- identity = 0.98048360711
- temporal = 1.0
- camera_contract = 1.0
- control = 1.0

Matrix:

PASS

Aggregate mean:

0.99670625961

Aggregate minimum:

0.99609672142

Qualification blockers:

none

## Durable qualification evidence

Trusted attestation:

data/studio/video_backend_qualification/
VIDEOQUAL_d98dd42fbba91aa84ff6.json

The attestation binds:

- backend id
- exact model id
- exact model revision
- exact workflow id/version
- exact normalizer id
- bundle status
- tool qualification
- rights review
- output-terms review
- each runtime case
- benchmark matrix
- blockers

Attestations outside the trusted qualification store cannot promote a model.

## ModelRegistry promotion

ModelRegistry now has an explicit evidence-gated production promotion method.

Promotion requires:

- commercial-use review
- output-terms review
- local artifact existence
- exact SHA-256 match
- non-empty qualification evidence reference

After the trusted Wan qualification passed:

approved_for_production: true

The registry also records the qualification-attestation path.

Stale notes such as:

"Production approval remains false until ..."

are removed automatically after successful promotion so the registry cannot contradict
its own approval state.

## Company integration

AppContext now exposes:

video_backend_qualification

ProfessionalCompanyLayer exposes the same controller.

The controller shares the same:

- CrossBackendVideoService
- ModelRegistry
- WorkflowRegistry
- CapabilityExecutionLab
- ProductionQualificationBoard

as the rest of CineFactory.

No duplicate video qualification registry was created.

## Production routing

After model promotion, ProductionMethodSwitchController re-evaluates the method normally.

Verified request:

- current tool: Blender
- current method: blender.cycles.quality
- local-only: true
- commercial-safe: true
- max VRAM: 12 GB
- backend switch allowed: true
- recurring identity required: true
- reference frame provided
- required tag: reference_conditioning
- min quality: 0.70

Observed:

status:

SELECTED

selected method:

comfyui.wan21.fun.inpaint.1.3b

handler:

block.video.comfy

## Scoped authority

Wan was not made a universal replacement backend.

### Precise camera geometry

Request:

precise_camera_required = true

Observed Wan blocker:

PRECISE_CAMERA_GEOMETRY_UNSUPPORTED

Decision:

BLOCKED_ACQUISITION

### Semantic character performance

Request:

semantic_performance_required = true

Observed Wan blocker:

SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED

Decision:

BLOCKED_ACQUISITION

The method can therefore be selected only for the class of shots it has actually proven.

## Camera semantics

The canonical contract preserves:

- camera purpose
- pattern id
- motion
- shot size
- lens
- motion strength
- targets

For the current Wan backend, this is intent-level control.

The backend does not claim exact geometric camera reproduction.

Runtime QC therefore reports:

CAMERA_INTENT_BOUND_BUT_NOT_GEOMETRICALLY_MEASURED

for supported non-precise-camera shots.

## Identity QC

Current recurring-identity measurement:

REFERENCE_FRAME_ANCHOR_SIMILARITY

The metric combines:

- HSV histogram similarity
- average perceptual hash similarity
- mean RGB-distance penalty

Current qualification floor:

0.80

This is a useful automated anchor check, but it is not yet actor-specific face/body
semantic identity verification.

That remains a future improvement.

## Turbo execution

Cross-backend method-switch work:

kind:

block.video.method_switch

handler:

block.video.comfy

resource:

GPU

Model affinity:

COMFYUI:wan2.1-fun-inpaint-1.3b@<exact revision>

Scheduler payload also declares required VRAM.

The work remains inside the normal Turbo resource-control plane.

## Canonical output normalization

ComfyUI currently returns decoded frames through SaveImage.

CrossBackendVideoService:

1. collects returned output frames
2. re-stages them into a contiguous deterministic sequence
3. invokes local FFmpeg
4. normalizes:
   - FPS
   - size
   - aspect fit/pad
   - H.264
   - yuv420p
   - faststart
5. writes the canonical target MP4

Production downstream therefore receives a normal CineFactory media path rather than a
ComfyUI-specific frame collection.

## Runtime QC

Each generated cross-backend video is checked for:

- output existence
- duration contract
- FPS contract
- black duration
- frozen duration
- rendered-frame quality
- recurring identity/reference anchor
- camera contract
- semantic-performance support state

Any blocker makes:

qc_passed = false

Turbo then raises RenderQualityRejected instead of silently accepting the artifact.

## Real qualification outputs

Evidence:

data/verification/v180_video_backend_qualification/
video_backend_qualification_verification.json

Qualification renders:

S01.wan13b.mp4

7,345 bytes

S02.wan13b.mp4

8,100 bytes

Both:

- SUCCESS
- 16 FPS
- 1.0625 seconds
- QC PASS
- recurring identity measured and above floor

## End-to-end cross-backend method switch

Final verifier:

scripts/verify_cross_backend_method_switch_v180.py

Scenario:

1. current method is blender.cycles.quality
2. an alternative method is requested after Blender failure context
3. ProductionMethodSwitchController evaluates all hard gates
4. Wan method is selected
5. canonical block shot is normalized to CanonicalBlockVideoRequest
6. Turbo GPU worker executes block.video.comfy
7. local ComfyUI executes Wan
8. media is normalized to canonical MP4
9. QC passes
10. ProductionContinuationManager accepts the recovered render
11. timeline.accept is enqueued
12. episode assembly is enqueued
13. IO worker executes timeline
14. IO worker executes assembly
15. final episode is produced

## Real method-switch evidence

Method decision:

SELECTED

Selected method:

comfyui.wan21.fun.inpaint.1.3b

Selected handler:

block.video.comfy

Reasons:

- selected=comfyui.wan21.fun.inpaint.1.3b
- score=0.6063
- all hard execution gates passed

Wan work:

SUCCESS

Identity score:

0.98630050415

QC:

PASS

Normalizer:

blockvideo.wan21.fun.inpaint.v1

Output:

data/verification/v180_cross_backend_method_switch/
renders/
S01.wan.method_switch.mp4

Bytes:

7,216

## Post-production continuation evidence

Dependency graph:

Wan render work
-> timeline.accept
-> block.episode.assemble

Observed:

timeline state:

SUCCESS

assembly state:

SUCCESS

Timeline dependency:

the Wan render work id

Assembly dependency:

the recovered timeline work id

Final recovered episode:

data/verification/v180_cross_backend_method_switch/
renders/
V180_METHOD_SWITCH.mp4

Bytes:

11,822

This closes the v1.6.20 goal:

Blender method gap
-> local AI-video backend
-> QC
-> continuity
-> timeline
-> episode

## Evidence-score semantic regression fix

Full-suite validation exposed one separate semantic bug in BlockAnimationProducer.

Previously:

identity_qc.score could be counted even when the backend had not marked the value as
measured.

This violated existing score semantics.

The fix is:

identity_score is accepted from backend identity_qc only when:

measured = true

Rendered actor-appearance evidence remains authoritative when available.

This does not weaken Wan QC because Wan explicitly produces:

measured = true

for reference-anchor identity evidence.

## Tests

New:

tests/test_video_backend_qualification_v180.py

Coverage includes:

- one case cannot qualify
- low identity blocks qualification
- two good cases can qualify and promote exact model
- outside-store attestation cannot promote
- AppContext/Company share the same video qualification controller
- Wan dynamic workflow binds reference to both start and end temporal anchors
- stale pre-qualification model notes are removed on promotion

Cross-version targeted verification:

45 PASS

Regression-fix targeted verification:

14 PASS

Registry promotion test after cleanup:

1 PASS

## Full repository verification

Previous milestone:

v1.6.19:
- 555 PASS

v1.6.20 final:
- compileall PASS
- pytest 564 PASS
- failures 0

An intermediate full-suite run caught:

1 fail / 563 pass

The failure was the unmeasured identity-score semantic regression described above.

After fixing it:

564 / 564 PASS

## Key evidence files

Smoke:

data/verification/v180_cross_backend/
wan_smoke/
wan_smoke_verification.json

20,132 bytes

Qualification:

data/verification/v180_video_backend_qualification/
video_backend_qualification_verification.json

7,577 bytes

Trusted qualification attestation:

data/studio/video_backend_qualification/
VIDEOQUAL_d98dd42fbba91aa84ff6.json

5,254 bytes

End-to-end method switch:

data/verification/v180_cross_backend_method_switch/
cross_backend_method_switch_verification.json

4,200 bytes

## Main files

New:

- cinefactory/studio/video_backend_qualification.py
- tests/test_video_backend_qualification_v180.py
- scripts/verify_video_backend_qualification_v180.py
- scripts/verify_cross_backend_method_switch_v180.py
- docs/CROSS_BACKEND_LOCAL_VIDEO_V1620.md

Existing v1.6.20 components completed/extended:

- cinefactory/studio/cross_backend_video.py
- cinefactory/studio/production_method_switch.py
- workflows/comfyui/wan21_fun_inpaint_13b.json
- workflows/comfyui/wan21_fun_inpaint_13b.manifest.yaml
- scripts/verify_wan_smoke_v180.py

Modified supporting files:

- cinefactory/models/registry.py
- cinefactory/appctx.py
- cinefactory/studio/professional_company.py
- cinefactory/studio/block_production.py
- models/registry.yaml

## What v1.6.20 now proves

CineFactory can now:

1. verify the exact local Wan video bundle
2. normalize a canonical block shot into a local generative-video request
3. use reference images or videos
4. bind camera intent
5. bind actors/rig ids and creative intent into the request
6. stage references deterministically
7. generate local Wan video through ComfyUI
8. normalize generated frames into canonical MP4
9. enforce visual and frame QC
10. measure recurring identity against the reference
11. reject a seed/case with inadequate identity stability
12. improve the workflow without lowering the quality floor
13. qualify the exact backend across multiple cases
14. persist a trusted qualification attestation
15. promote the exact model/revision only after evidence passes
16. select the Wan method through the normal MethodSwitchController
17. refuse unsupported exact-camera shots
18. refuse unsupported semantic-performance shots
19. execute the selected backend as normal Turbo GPU work
20. route a successful recovered render into timeline and episode assembly
21. produce a final recovered episode

## What v1.6.20 does not claim

It does not claim:

- Wan replaces Blender universally
- exact 3D camera geometry is preserved
- dialogue/acting semantic performance is qualified
- global histogram/hash similarity is sufficient for long-form character identity
- two short qualification cases prove broad production leadership
- multi-character interaction identity is solved
- long-duration temporal consistency is solved
- arbitrary camera motion is qualified
- all Minecraft/Roblox shots should use generative video

These remain explicit routing blockers or future qualification work.

## Next milestone

The highest-value next milestone is v1.6.21:

Cross-Backend CharacterFactory + Identity Continuity.

Recommended focus:

1. global Character ID independent of backend
2. canonical appearance/reference pack per character
3. costume/state/version tracking
4. actor-specific reference crops
5. face/body/skin/clothing/accessory descriptors
6. cross-backend reference-conditioning adapters
7. actor-specific identity embeddings/features
8. per-actor frame identity QC instead of only whole-frame anchor similarity
9. multi-character identity collision detection
10. identity continuity across adjacent shots
11. identity continuity across Blender -> Wan -> Blender cuts
12. recurring-character qualification matrix across seeds/cameras/scenes
13. CharacterFactory support for Minecraft voxel and Roblox R6 identities
14. repair routing when identity drift occurs
15. cross-backend identity acceptance evidence

After that, semantic performance/dialogue and exact-camera/control upgrades can be layered
on top of a stronger identity foundation.
