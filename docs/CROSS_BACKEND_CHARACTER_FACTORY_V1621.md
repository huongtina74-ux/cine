# CineFactory v1.6.21 — Cross-Backend CharacterFactory + Identity Continuity

## Goal

v1.6.21 upgrades character consistency from whole-frame reference similarity into a
persistent, actor-specific identity system shared across production backends.

The verified flow is:

RigRegistry
-> Global Character Identity
-> versioned state
-> actor-specific reference pack
-> cross-backend request binding
-> generated actor crop
-> per-actor identity QC
-> adjacent backend-transition continuity

CharacterFactory extends the existing rig registry, Asset Bible, rendered-frame QC and
continuity systems. It does not replace them.

## New core module

cinefactory/studio/character_factory.py

Main contracts:

- CharacterBackendId
- CharacterBackendBinding
- CharacterStateVersion
- CharacterReferencePack
- CharacterIdentityRecord
- ActorIdentityAssessment
- MultiCharacterIdentityReport
- CharacterTransitionAssessment
- CharacterTransitionReport
- CharacterFactoryStore
- CharacterFactory

## Company integration

AppContext now exposes:

character_factory

ProfessionalCompanyLayer exposes the same CharacterFactory instance.

CrossBackendVideoService also receives that same instance.

This gives one identity authority for:

- Blender/block animation
- Wan local video
- future Minecraft runtime
- future Roblox Studio R6
- future Roblox Studio R15

## Global identity bootstrap

CharacterFactory bootstraps from:

config/block_animation/characters.yaml

The existing CharacterRigDefinition already contains the identity source data:

- rig id
- style
- skin/avatar path
- material profile
- expression profile
- accessories
- identity dictionary
- skeleton profile
- tags

Global IDs are deterministically derived from the strongest existing token:

1. color_identity
2. avatar_id
3. skin_id
4. rig_id fallback

Examples:

mc_a -> CHAR_MC_A

r6_a -> CHAR_R6_A

## Persistent character records

The real v1.6.21 run created records under:

data/studio/character_factory/records/

for the existing production identities, including:

- CHAR_MC_A
- CHAR_MC_B
- CHAR_MC_C
- CHAR_MC_D
- CHAR_MC_E
- CHAR_MC_F
- CHAR_R6_A
- CHAR_R6_B
- CHAR_R6_C
- CHAR_R6_D
- CHAR_R6_E
- CHAR_R6_F
- CHAR_R15_TEST

Debug block rigs remain represented for CI/smoke compatibility.

## Verified Minecraft identity

Real record:

CHAR_MC_A

Style:

MINECRAFT

Immutable traits:

- skin_id = mc_a_pixel_16
- hair = blue
- shirt = orange
- pants = navy
- face = bright
- color_identity = MC_A

Identity lock:

preserve color_identity=MC_A, face=bright, hair=blue, pants=navy,
shirt=orange, skin_id=mc_a_pixel_16

These descriptors are now added to the cross-backend video prompt.

## Backend bindings

For mc_a, the real record includes:

BLENDER_BLOCK
- rig_id: mc_a
- adapter: block_animation.rig

WAN21
- rig_id: mc_a
- adapter: reference_conditioning
- qualification: REFERENCE_REQUIRED

MINECRAFT_RUNTIME
- rig_id: mc_a
- adapter: native_character_binding

Roblox R6 identities bind to:

ROBLOX_STUDIO_R6

R15 identities bind to:

ROBLOX_STUDIO_R15

These native bindings define identity contracts for future runtime backends. They do not
claim those runtime backends are already complete.

## Versioned mutable state

Immutable identity and mutable production state are separate.

CharacterStateVersion tracks:

- version
- costume_id
- accessories
- expression_profile
- notes
- timestamp

State changes append a new version.

They do not overwrite the previous state.

Tests prove:

state v1
-> costume/accessory update
-> state v2

while v1 remains durable.

## Actor-specific reference packs

CharacterFactory can capture a trusted actor reference from a previously accepted render.

Input:

rendered media
+
rendered-frame QC sidecar

The sidecar already contains actor-specific evidence produced by Blender QC:

- actor id
- screen box
- crop size
- luma
- saturation
- RGB mean
- HSV histogram
- perceptual hash

CharacterFactory extracts the actor crop and creates a durable CharacterReferencePack.

The pack binds:

- reference id
- global character id
- actor id
- rig id
- source backend
- source media path
- source media SHA-256
- crop path
- crop SHA-256
- screen box
- appearance evidence
- state version
- costume
- accessories

## Real reference pack

Source:

data/verification/v179_candidate_promotion/
cycles_matrix/
S01.cycles.golden.mp4

Actor:

A

Rig:

mc_a

Global identity:

CHAR_MC_A

Reference id:

REF_a34a1509cfe946596e

Persisted crop:

data/studio/character_factory/
references/CHAR_MC_A/
REF_a34a1509cfe946596e.png

Persisted pack:

data/studio/character_factory/
references/CHAR_MC_A/
REF_a34a1509cfe946596e.json

## Immutable reference semantics

A reference ID is content-addressed from:

global character id
+
actor id
+
source media SHA-256

The same old render cannot be captured again later and silently relabeled as a newer
costume/accessory state.

If the character state has advanced, the original pack stays bound to its original
state_version.

This prevents:

old visual evidence
-> state changed
-> same old file incorrectly treated as evidence for new state

## Stale-state gate

When a reference pack state version differs from the character's current state version,
per-actor identity evaluation fails with:

CHARACTER_REFERENCE_STATE_VERSION_STALE

A new visual reference is therefore required after an intentional identity-affecting
state change.

## Cross-backend request upgrade

ReferenceConditioning now carries optional actor-specific identity metadata:

- actor_screen_boxes
- global_character_ids
- actor_reference_ids
- actor_identity_descriptors

If trusted actor evidence exists, CrossBackendVideoService populates these fields.

Example verified mapping:

A -> CHAR_MC_A

The generated prompt now also contains the global identity lock and immutable traits.

## Backward compatibility

Actor-specific identity data is optional.

If a reference does not have compatible actor-sidecar evidence:

v1.6.20 whole-frame reference-anchor QC remains available.

If actor reference packs exist:

per-actor identity QC becomes authoritative for recurring identity.

Whole-frame similarity remains only fallback/supporting evidence.

## Per-actor generated-output measurement

For a Wan render, the known actor screen box is passed into RenderedFrameAnalyzer.

The generated frame is cropped at that actor region.

The current actor crop is then compared with the actor-specific trusted reference pack.

The existing RenderedAppearanceEvaluator measures:

- HSV histogram similarity
- perceptual hash similarity
- RGB-distance penalty

This is much stronger than comparing only the complete frame because background changes
cannot dominate the character score.

## Identity collision detection

For multi-character shots, each current actor crop can also be compared against the
other characters' reference packs.

If the current crop matches another character materially better than its expected
identity, CharacterFactory emits:

CHARACTER_IDENTITY_COLLISION

Current collision policy also requires the competing score to exceed the identity floor
and beat the expected score by a configured margin.

This protects against identity swaps.

The v1.6.21 collision gate is covered by deterministic synthetic unit tests.

It has not yet been claimed as real multi-character Wan production evidence.

## Cross-backend transition continuity

CharacterFactory can measure the same global character directly across adjacent backend
outputs.

Transition report fields include:

- actor id
- global character id
- previous backend
- current backend
- measured flag
- pass/fail
- score
- detailed appearance comparison
- findings

This supports chains such as:

Blender -> Wan

Wan -> Blender

and later:

Minecraft Runtime -> Wan
Roblox Studio -> Wan
Wan -> Minecraft Runtime
Wan -> Roblox Studio

## Real v1.6.21 verifier

Script:

scripts/verify_character_factory_v181.py

The verifier used:

Blender Cycles reference
-> MethodSwitchController
-> Wan2.1-Fun Inpaint 1.3B
-> Turbo GPU
-> actor-specific identity QC
-> Blender/Wan transition comparison

No synthetic render was used for the main verification path.

## Real Wan result

Output:

data/verification/v181_character_factory/
renders/
S01.wan.character.mp4

Size:

8,070 bytes

Turbo state:

SUCCESS

QC:

PASS

Identity metric:

PER_ACTOR_REFERENCE_APPEARANCE

Actor:

A

Global character:

CHAR_MC_A

Actor-specific identity score:

0.9816576460131068

Measured:

true

Passed:

true

Collision findings:

none

## Whole-frame comparison

The same render also retained the v1.6.20 fallback whole-frame anchor result:

whole-frame score:

0.9714107635515506

Actor-specific score:

0.9816576460131068

This demonstrates that the runtime actually used the new actor-specific evidence path
rather than only renaming the old whole-frame metric.

## Real transition continuity

Blender -> Wan:

- measured: true
- passed: true
- score: 0.9898495124850641

Wan -> Blender:

- measured: true
- passed: true
- score: 0.9898495124850641

The test used the same global character:

CHAR_MC_A

on both sides of each transition.

## Current identity floor

CharacterFactory default actor/transition floor:

0.70

This is separate from the v1.6.20 backend qualification floor.

A future broader multi-scene qualification matrix should recalibrate this threshold using
larger real datasets rather than lowering or raising it from one shot.

## AppContext sharing

Unit tests prove:

ctx.character_factory
is
ctx.studio.professional_company.character_factory

and:

ctx.cross_backend_video.character_factory
is
ctx.character_factory

No duplicate in-memory identity authority exists.

## Tests

New:

tests/test_character_factory_v181.py

Coverage includes:

- deterministic Minecraft identity bootstrap
- deterministic Roblox R6 identity bootstrap
- backend binding coverage
- real Blender sidecar reference-pack extraction
- durable actor crop creation
- versioned character state
- stale-reference rejection after state change
- same source cannot be relabeled as newer state
- actor identity collision detection
- cross-backend request identity metadata
- global identity descriptors in generative prompt
- Blender/Wan transition measurement
- AppContext/ProfessionalCompany shared CharacterFactory

Targeted v1.6.21 + v1.6.20 regression rerun:

38 PASS

## Full repository verification

Previous milestone:

v1.6.20
- 564 PASS

Current milestone:

v1.6.21 final rerun
- compileall PASS
- pytest 589 PASS
- failures 0

## Primary evidence

Main verification JSON:

data/verification/v181_character_factory/
character_factory_verification.json

Size:

10,163 bytes

Real Wan render:

data/verification/v181_character_factory/
renders/
S01.wan.character.mp4

Size:

8,070 bytes

Real actor crop:

data/studio/character_factory/
references/CHAR_MC_A/
REF_a34a1509cfe946596e.png

Size:

3,323 bytes

Reference-pack manifest:

data/studio/character_factory/
references/CHAR_MC_A/
REF_a34a1509cfe946596e.json

Size:

2,924 bytes

## Main files

New:

- cinefactory/studio/character_factory.py
- tests/test_character_factory_v181.py
- scripts/verify_character_factory_v181.py
- docs/CROSS_BACKEND_CHARACTER_FACTORY_V1621.md

Integrated/extended:

- cinefactory/studio/cross_backend_video.py
- cinefactory/appctx.py
- cinefactory/studio/professional_company.py

## What v1.6.21 now proves

CineFactory can now:

1. create deterministic global identities from the existing rig registry
2. keep backend-specific bindings under one global character
3. separate immutable identity from mutable state
4. version costume/accessory changes
5. capture a trusted actor crop from a real Blender render
6. bind the crop to source hash and state version
7. prevent old media from being relabeled as evidence for a newer state
8. transmit global identity metadata into a Wan request
9. add explicit identity descriptors to the generation prompt
10. crop the corresponding actor in generated Wan output
11. calculate per-actor identity instead of whole-frame identity only
12. make actor-specific QC authoritative when actor packs exist
13. detect synthetic multi-character identity collisions
14. measure the same character across Blender -> Wan
15. measure the same character across Wan -> Blender
16. retain v1.6.20 fallback compatibility when actor evidence is unavailable
17. persist identity/reference evidence locally without metered APIs

## What v1.6.21 does not claim

It does not yet prove:

- real multi-character Wan identity separation
- automatic actor detection when screen boxes are unavailable
- semantic face recognition
- body-shape embeddings
- accessory segmentation
- occlusion/re-identification
- large camera-angle invariance
- long-duration identity stability
- real Minecraft runtime -> Wan identity continuity
- real Roblox Studio -> Wan identity continuity
- dialogue/performance identity under strong facial animation
- production leadership from one real character verification case

Those remain future maturity gates.

## Recommended next milestone

v1.6.22 should focus on:

Multi-Character Identity + Semantic Performance / Dialogue Performance Engine.

Recommended order:

1. create real two-character and three-character Blender reference scenes
2. render actor-specific trusted references for every character
3. run Wan multi-character qualification across multiple seeds
4. validate identity collision/swap detection on real output
5. add actor-region tracking across frames instead of fixed mid-frame boxes
6. add per-actor head/body subregions where available
7. add Dialogue Performance Engine contracts
8. bind objective/subtext/emotion/listening behavior to animation/performance
9. add speech/phoneme timing contract
10. add gaze/listening/reaction continuity
11. qualify semantic-performance QC
12. remove SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED only after real evidence
13. then extend CharacterFactory bindings to real Minecraft/Roblox runtime backends

This order strengthens real character interaction before expanding the number of
production backends.
