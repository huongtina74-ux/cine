# Automatic Production Method Switching v1.6.16

## Goal

v1.6.16 closes the gap between:

ECONOMICS_DECISION = SWITCH_METHOD

and an actual alternative production execution path.

Before this milestone CineFactory could correctly decide that another local repair was
not economically justified, but it stopped at a Production Method Planner handoff.

v1.6.16 adds a fail-closed method-selection and execution layer:

QC FAIL
-> ROOT CAUSE
-> LOCAL REPAIR PLAN
-> PRODUCTION ECONOMICS
-> SWITCH_METHOD
-> METHOD CANDIDATE ASSESSMENT
-> LICENSE / QUALIFICATION / VRAM / CONTINUITY / AUTOMATION GATES
-> SELECT QUALIFIED METHOD
-> ENQUEUE DURABLE METHOD-SWITCH WORK
-> RENDER
-> QC
-> ACCEPT ONLY IF PASSING
-> TIMELINE
-> ASSEMBLY

If no qualified method exists:

SWITCH_METHOD
-> BLOCKED_ACQUISITION
-> CAPABILITY ACQUISITION REQUEST
-> DURABLE R&D AGENT WORK
-> no failed take reaches editorial

The system never treats tool discovery as production approval.

## New company capability

New core module:

cinefactory/studio/production_method_switch.py

The controller is exposed through AppContext and ProfessionalCompanyLayer so the
production company uses one method-switch authority rather than independent per-tool
fallback logic.

Main objects:

- MethodSwitchStatus
- MethodSwitchPolicy
- MethodExecutionMode
- ProductionMethodSpec
- MethodSwitchRequest
- MethodCandidateAssessment
- MethodSwitchDecision
- CapabilityAcquisitionRequest
- ProductionMethodSwitchStore
- ProductionMethodSwitchController

## Method-switch policies

QUALITY_FIRST_ALTERNATIVE

Used when production economics says an important shot should preserve quality even if
the current execution method is no longer worth repairing.

BALANCED_ALTERNATIVE

Used when quality and throughput should both remain material.

FAST_LEAN_ALTERNATIVE

Reserved for low-value/throughput-oriented work where a faster valid alternative is
preferred.

Policy changes candidate ranking.

It does not bypass hard eligibility gates.

## Candidate gates

Every alternative method is assessed against hard gates before selection.

Current gate families include:

- capability is registered
- capability is executable
- local-only policy
- commercial-safety evidence
- production qualification
- Turbo execution handler exists
- minimum quality target
- VRAM budget
- method-switch GPU reserve
- required tags
- workflow availability
- workflow model production approval
- block-shot normalization adapter
- continuity policy
- recurring-character identity risk
- niche/style compatibility

A high score cannot override a failed hard gate.

## Same-tool specialization versus cross-tool switching

CineFactory distinguishes two trust boundaries.

### Same canonical tool specialization

Example:

Blender Eevee
-> Blender Cycles

The same canonical:
- scene
- actors
- rigs
- camera
- animation
- timing
- props
- creative intent

is preserved.

Only the qualified execution method changes.

Because the same Blender production runtime is already executing the canonical shot,
this does not introduce a new third-party/tool trust boundary.

### Cross-tool switching

Examples:

Blender
-> ComfyUI video
-> Unreal Sequencer
-> Minecraft runtime
-> Roblox Studio

These require additional proof because the backend can reinterpret:
- scene geometry
- identity
- camera
- motion
- world state
- temporal continuity

Therefore cross-tool switching requires production qualification and a semantic
block-shot normalization adapter before it can auto-execute.

## New executable method: Blender Cycles quality recovery

v1.6.16 adds CYCLES to the block-animation render contracts.

Modified:
- EpisodeSpec.render_engine
- RenderQualityProfileDefinition.engine

Supported values now include:
- BLENDER_EEVEE_NEXT
- BLENDER_WORKBENCH
- CYCLES

The Blender worker now configures Cycles when explicitly selected:
- Cycles render engine
- sample count from the approved render-quality contract
- preview sample cap
- denoising
- GPU-preferred device setting

The method does not mutate global Blender device preferences.

It preserves the existing worker's configured/fallback behavior.

## Cycles method specification

Method:

blender.cycles.quality

Capability:
- blender.local
- OFFLINE_3D

Handler:
- blender.animation.render

Resource:
- GPU

Current method model:
- quality: 0.95
- control: 0.98
- determinism: 0.96
- speed: 0.32
- estimated VRAM: 8 GB
- same-scene semantics: true
- commercial safety: true
- estimated time multiplier: 2.5

These are routing policy values, not a claim that Cycles universally scores 0.95
against external competitors.

External benchmark evidence is still required for benchmark-leading claims.

## Safe repair transfer into method switching

When a local root-cause repair is valid but production economics says the incumbent
method should not receive another local attempt, CineFactory can transfer the safe
execution correction into the alternative method.

Example verified in v1.6.16:

Eevee render:
- exposure = -1.5 EV
- rendered-frame QC fails underexposure

Root-cause repair plan:
- exposure -1.5 EV -> 0.0 EV

Economics:
- local Eevee GPU budget exhausted
- action = SWITCH_METHOD

Method Switch:
- select Blender Cycles
- preserve canonical shot
- carry the safe exposure correction
- render through Cycles

This is different from blindly retrying Eevee.

## Durable Turbo method-switch work

Method-switch execution uses a separate work kind:

block.render.method_switch

Payload records:
- method_switch = true
- method_id
- method_switch_round
- method_switch_of_work_id
- canonical transformed BlenderAnimationJob

The work is durable in TurboStore.

It is not counted as:
- first-pass render
- local repair render

This distinction is important for factory KPIs.

## Method-switch metrics

Turbo execution metrics now separate:

first pass:
- block.render

repair:
- block.render.repair

method switch:
- block.render.method_switch

New metrics:
- method_switch_samples
- method_switch_successes
- method_switch_success_rate

This prevents successful alternative-method work from falsely inflating the local
repair success rate.

## Real Blender + Turbo method-switch verification

Verifier:

scripts/verify_production_method_switch_v176.py

Scenario:

- one Minecraft HERO shot
- original method: Blender Eevee
- exposure forced to -1.5 EV
- local shot GPU budget forced to 1 second
- separate method-switch GPU reserve: 60 seconds
- project GPU budget: 120 seconds
- recurring identity and continuity priority enabled

The first Eevee take rendered media but failed rendered-frame quality.

Observed first work:
- kind: block.render
- state: QC_REJECTED
- selected as failed take
- local repair not executed because production economics chose SWITCH_METHOD

Economics:
- action: SWITCH_METHOD
- reason: SHOT_GPU_BUDGET_EXHAUSTED
- owner: PRODUCTION_METHOD_PLANNER
- policy: QUALITY_FIRST_ALTERNATIVE

## Candidate deliberation from the real run

### Blender Cycles

blender.cycles.quality

Observed:
- eligible: true
- execution ready: true
- routing score: 0.9888
- same canonical tool trust boundary
- same-scene semantics: true
- projected GPU work inside the explicit method-switch reserve

Selected.

### ComfyUI video

comfyui.video.production

Not selected.

Observed blockers include:
- VIDEO_WORKFLOW_MISSING
- BLOCK_SHOT_NORMALIZATION_ADAPTER_MISSING
- METHOD_COMMERCIAL_SAFETY_UNVERIFIED
- HERO quality target not met by the current generic capability record
- continuity backend switch blocked

Important environment fact:

ComfyUI is production-qualified at the tool/adaptor level on the current installation,
but the workflow registry currently contains only the approved SD1.5 image mastery
workflow.

There is no production-qualified video workflow/model pair in the current registry.

Therefore CineFactory correctly refuses to infer video production readiness merely from
ComfyUI tool qualification.

### Unreal

unreal.sequence.quality

Not selected.

Current blockers include:
- capability not executable
- production qualification failed
- Turbo handler not registered
- block-shot normalization adapter missing
- commercial-safety evidence incomplete
- continuity backend switch blocked

### Minecraft runtime

minecraft.runtime.capture

Not selected.

Current blockers include:
- capability not executable
- production qualification missing
- Turbo handler missing
- block-shot normalization adapter missing
- commercial-safety evidence incomplete
- continuity backend switch blocked

### Roblox Studio

roblox.studio.capture

Not selected for the Minecraft shot.

In addition to readiness blockers, the candidate receives:
- NICHE_STYLE_MISMATCH

## Real Cycles result

The selected alternative work:

- kind: block.render.method_switch
- method: blender.cycles.quality
- state: SUCCESS

Selected take:
- S01_BLENDER_TURBO_02

Selected media:
- data/verification/v176_method_switch/renders/block_animation/shots/0000_S01.method_switch01.mp4

The transformed shot used:
- render_engine = CYCLES
- render_quality.engine = CYCLES
- repaired exposure = 0.0 EV

The failed Eevee take remained rejected.

## Editorial dependency proof

The real Turbo lineage was:

block.render
QC_REJECTED
    |
    v
block.render.method_switch
SUCCESS
    |
    v
timeline.accept
SUCCESS
    |
    v
block.episode.assemble
SUCCESS

The timeline depended only on the successful method-switch work.

The assembly depended only on the successful timeline work.

The rejected Eevee work was not consumed by post-production.

## Latest measured verification economics

Latest isolated v1.6.16 run:

- passed: true
- method-switch samples: 1
- method-switch successes: 1
- method-switch success rate: 1.0
- GPU seconds: ~7.734
- GPU wasted seconds: ~4.734
- GPU waste ratio: ~61.21%

The waste is expected in this fault-injection verification because the first Eevee
render is deliberately made unacceptable.

These numbers are not claimed as representative production economics.

## Fail-closed next-switch behavior

The verifier also asks CineFactory:

"What if Blender Cycles is already the current method and another method is needed?"

For the current machine/project state, no cross-tool method passes every gate.

Observed decision:
- BLOCKED_ACQUISITION

CineFactory creates:

data/studio/method_switch_requests/VERIFY_METHOD_SWITCH_V176__S01.json

The request records:
- candidate-specific blockers
- required quality
- VRAM budget
- failure codes
- required next capabilities
- approved research source classes
- mandatory acceptance gates

## Durable R&D acquisition queue

A blocked method switch no longer ends at a JSON file.

The controller can now build:

kind:
- rnd.capability.acquire

handler:
- rnd.capability.acquire

resource:
- AGENT

state on enqueue:
- QUEUED

The work carries:
- acquisition request path
- project / episode / shot
- current method
- requested method policy
- quality target
- VRAM limit
- failure codes
- research sources
- mandatory qualification gates

Research source classes currently requested:
- OFFICIAL_DOCS
- MODEL_CARDS
- GITHUB
- COMFYUI_WORKFLOW_REGISTRY
- TOOL_ADAPTER_REGISTRY

Mandatory gates:
- LICENSE_REVIEW
- SECURITY_REVIEW
- HARDWARE_COMPATIBILITY
- SANDBOX_BENCHMARK
- QUALITY_BENCHMARK
- AUTOMATION_READINESS
- BLOCK_SHOT_NORMALIZATION
- PRODUCTION_QUALIFICATION

The AGENT work remains queued until an actual R&D acquisition worker is available.

It is never marked success merely because the request was created.

## Integration with the existing R&D governance model

CineFactory already contains ExternalToolIntake with states:

- DISCOVERED
- LICENSE_REVIEW
- SECURITY_REVIEW
- SANDBOX
- BENCHMARK
- ADAPTER
- APPROVED
- BLOCKED
- DEPRECATED

An external candidate cannot become APPROVED unless required commercial, security,
sandbox, benchmark and regression gates pass.

v1.6.16 intentionally points acquisition work toward that existing governance model
instead of creating a second independent approval system.

## v1.6.15 compatibility verification

The production-economics verifier was rerun after method switching and acquisition
queue integration.

BACKGROUND case:
- remains STOP_BUDGET
- no repair work
- no method switch
- no R&D acquisition work
- no timeline
- no assembly

HERO case with no method-switch reserve sufficient for an executable alternative:
- remains failed
- method switch status = BLOCKED_ACQUISITION
- exactly one rnd.capability.acquire work is queued
- no local repair render
- no timeline
- no assembly
- failed take is not accepted

This preserves the v1.6.15 safety semantics while making the unresolved capability gap
actionable.

## Tests

New:
- tests/test_production_method_switch_v176.py

Coverage includes:
- quality-first selects Cycles
- same-tool trust boundary
- ComfyUI video cannot become executable without video workflow and normalizer
- no eligible method creates acquisition request
- blocked switch builds durable AGENT acquisition work
- Cycles transform preserves actors/camera/actions
- Cycles transform changes execution renderer
- durable Turbo method-switch work construction
- repair and method-switch KPIs remain distinct

Targeted v1.6.16 / v1.6.15 / v1.6.14 regression:
- 22 PASS

Cross-version production regression before final full suite:
- 54 PASS

## Full repository verification

Previous milestone:
- v1.6.15: 521 PASS

v1.6.16:
- compileall PASS
- pytest 528 PASS
- failures 0

## Key files

New:
- cinefactory/studio/production_method_switch.py
- tests/test_production_method_switch_v176.py
- scripts/verify_production_method_switch_v176.py
- docs/AUTOMATIC_PRODUCTION_METHOD_SWITCH_V1616.md

Modified:
- cinefactory/block_animation/contracts.py
- scripts/blender_animation_worker.py
- cinefactory/appctx.py
- cinefactory/studio/professional_company.py
- cinefactory/studio/block_production.py
- cinefactory/turbo/store.py
- cinefactory/studio/production_economics.py
- scripts/verify_production_economics_v175.py

Evidence:
- data/verification/v176_method_switch/production_method_switch_verification.json
- data/verification/v176_method_switch/turbo_verification.db
- data/verification/v176_method_switch/renders/block_animation/
- data/studio/method_switch_requests/

## What v1.6.16 proves

CineFactory can now:

1. distinguish local repair from method switching
2. reserve separate compute for an alternative method
3. evaluate multiple method candidates
4. enforce execution/license/VRAM/continuity/automation gates
5. select an executable alternative
6. transform the canonical shot without changing creative intent
7. enqueue the alternative as durable Turbo work
8. re-run QC
9. allow editorial only after alternative-method success
10. keep method-switch metrics separate from repair metrics
11. fail closed when no alternative is qualified
12. create an explicit capability-acquisition request
13. enqueue durable R&D acquisition work for the unresolved gap

## What v1.6.16 does NOT claim

It does not claim that:
- ComfyUI video is production ready
- Unreal is production ready
- Minecraft runtime capture is production ready
- Roblox runtime capture is production ready
- all cross-backend continuity is solved
- automatic external repo/model installation is permitted
- one Cycles stress test proves external benchmark leadership

Those claims require the missing qualification evidence.

## Next high-priority milestone

v1.6.17 should implement the Autonomous Capability Acquisition R&D Worker that consumes:

rnd.capability.acquire

The worker should:

1. read the acquisition request
2. inspect existing local inventory first
3. search approved external research sources when permitted
4. create controlled candidates
5. resolve official documentation/model-card/license evidence
6. perform security review
7. check RTX 3060 12 GB compatibility
8. sandbox the candidate
9. benchmark representative shots
10. compare quality / speed / identity / control / automation
11. build or validate the execution adapter
12. build the block-shot normalization adapter
13. run regression
14. submit production qualification
15. promote only if all gates pass
16. register the new production method
17. requeue the previously blocked shot

Until that worker exists, acquisition work remains durable and visible but intentionally
unexecuted.
