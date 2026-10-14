# Autonomous Capability Acquisition R&D v1.6.17

## Goal

v1.6.17 turns the durable work item:

rnd.capability.acquire

from a passive queued record into an executable R&D control loop.

The new loop is:

METHOD SWITCH BLOCKED
-> durable R&D AGENT work
-> local capability inventory
-> re-evaluate current machine state
-> inspect existing tool mastery / qualification
-> if a qualified method now exists:
     requeue the canonical shot
-> otherwise:
     emit a schema-valid external research request
     defer without burning retry budget
-> ingest research response
-> license / security / artifact / sandbox / benchmark / adapter gates
-> never promote research claims directly
-> re-evaluate method registry
-> requeue only after an executable production method exists

## Core module

New:

cinefactory/studio/capability_acquisition.py

Main objects:

- ResearchEvidenceTier
- CapabilityAcquisitionState
- CapabilityResearchCandidate
- CapabilityResearchResponse
- AcquisitionCandidateRecord
- CapabilityAcquisitionCase
- CapabilityAcquisitionOutcome
- CapabilityAcquisitionStore
- CapabilityResearchBridge
- LocalCapabilityInventory
- CapabilityAcquisitionWorker

## Company integration

CapabilityAcquisitionWorker is now exposed through:

- AppContext.capability_acquisition
- ProfessionalCompanyLayer.capability_acquisition

The company therefore has one shared acquisition authority instead of per-niche
download/install logic.

## Durable R&D worker lane

ContinuousBlockFactory now has three lanes:

GPU
- blender.animation.render

IO
- timeline.accept
- block.episode.assemble

AGENT
- rnd.capability.acquire

The AGENT worker id is:

block-rnd-agent-0

It cannot claim unrelated GPU/IO work.

## Non-blocking defer/backoff

A new Turbo defer mechanism was added.

When a work item is waiting for external evidence:

- state becomes RETRY
- attempts are restored instead of consumed
- payload receives _not_before_utc
- the scheduler skips the work until the timestamp is reached
- ready_work_count also excludes deferred work
- WORK_DEFERRED is published to the event bus

This prevents:

- busy loops
- fake failures
- retry-budget exhaustion while waiting for evidence
- marking an unfinished research task SUCCESS

The generic daemon-level exception is:

WorkDeferred

TurboStore now supports:

defer_work(...)

## Local inventory first

Before asking an external agent to search the web, the R&D worker snapshots:

- GPU state
- CapabilityRegistry
- ProductionQualification decisions
- ExecutionMastery reports
- workflow registry
- model registry
- installed tool state
- versions
- executable paths

This enforces:

LOCAL INVENTORY
before
EXTERNAL DISCOVERY

and avoids researching/installing something that CineFactory may already have.

## Re-evaluation before research

Each acquisition tick re-runs the ProductionMethodSwitchController.

This is important because the environment may have changed after the original failure.

Examples:

- tool became available
- adapter became reachable
- model/workflow was added
- execution mastery was completed
- production qualification was promoted
- a local capability registry entry became executable

If the current machine can now satisfy the request, external research is skipped.

## Existing tool mastery audit

For known supported tools, the worker can inspect the installed/runtime state and reuse:

- ExecutionMasteryRunner
- ProductionQualificationBoard

Known mastery families currently include:

- Blender
- FFmpeg
- ComfyUI
- Resolve
- Premiere
- Photoshop
- After Effects
- Unreal
- Canva

The worker does not create a second qualification framework.

It reuses the existing company governance.

## External reasoning boundary

Production runtime policy still blocks arbitrary Internet egress.

Therefore v1.6.17 does not embed:

- browser credentials
- GitHub tokens
- model-hub tokens
- paid inference API keys
- paid research API keys

Instead the worker writes a schema-valid request under:

data/studio/capability_acquisition/reasoning/requests/

and expects an external reasoning agent such as OpenClaw/Codex/manual controlled agent
to write the response under:

data/studio/capability_acquisition/reasoning/responses/

The external agent is used for research/reasoning.

The deterministic factory remains responsible for production approval.

## Research request contract

The request includes:

- acquisition case id
- current method-switch request
- candidate-specific blockers
- required next capabilities
- local inventory snapshot
- required research sources
- acceptance gates
- hardware constraint
- local/free-first policy
- no-metered-generation policy
- do-not-install rule
- do-not-execute-unreviewed-code rule
- JSON schema for CapabilityResearchResponse

The research prompt explicitly says:

research facts and candidates only;
do not claim production approval.

## Preferred research sources

The current request prioritizes:

- OFFICIAL_DOCS
- MODEL_CARDS
- GITHUB / maintainer repositories
- COMFYUI_WORKFLOW_REGISTRY
- TOOL_ADAPTER_REGISTRY

Research sources are evidence inputs, not approval.

## Research candidate schema

Each candidate can report:

- candidate id
- name
- tool/method id
- source URI/type
- version
- capabilities
- license
- license evidence URI
- evidence tier
- commercial-use finding
- estimated VRAM
- local support
- automation interfaces
- security notes
- evidence references
- local artifact path/hash
- sandbox report
- benchmark report
- adapter regression report

## Evidence tiers

License evidence is classified as:

- OFFICIAL
- MAINTAINER
- COMMUNITY
- UNKNOWN

Commercial-use knowledge is not treated as trusted unless:

- a license is identified
- evidence URI exists
- evidence tier is OFFICIAL or MAINTAINER

Community assertions alone cannot unlock production.

## Research does not equal approval

Even when a reasoning response says a tool looks good, CineFactory still requires
local deterministic evidence.

A candidate cannot pass the intake pipeline without:

1. trusted license evidence
2. commercial use allowed
3. local artifact hash verification
4. security evidence
5. sandbox report PASS
6. benchmark report PASS
7. adapter regression report PASS

Only then can ExternalToolIntake reach APPROVED.

## Local artifact verification

If a research candidate provides:

local_artifact_path
local_artifact_sha256

the worker computes the SHA-256 of the actual local file.

A mismatch or missing artifact blocks progression.

External text claiming that a file was reviewed is insufficient.

## Sandbox / benchmark / adapter proof

The worker recognizes report files only when:

- the file exists locally
- it contains valid JSON
- passed == true

Separate report paths exist for:

- sandbox
- benchmark
- adapter regression

This keeps the gates inspectable and durable.

## Existing R&D intake state machine reused

The worker reuses ExternalToolIntake:

DISCOVERED
-> LICENSE_REVIEW
-> SECURITY_REVIEW
-> SANDBOX
-> BENCHMARK
-> ADAPTER
-> APPROVED

The original safety invariant remains:

APPROVED requires
- commercial use known
- commercial use allowed
- security reviewed
- sandbox passed
- benchmark passed
- regression passed

## Critical method-binding gate

Even a fully evidenced external candidate is not automatically executable.

If the candidate is not bound to:

- CapabilityRegistry
- a registered ProductionMethodSpec
- an execution handler
- a semantic normalization path
- production qualification

the acquisition case is moved back to:

ADAPTER

with:

APPROVED_CANDIDATE_NOT_BOUND_TO_EXECUTABLE_METHOD

This prevents the dangerous transition:

GOOD RESEARCH RESULT
-> RUN UNKNOWN CODE

## Resume context

When block production creates rnd.capability.acquire, it now persists:

- original MethodSwitchRequest
- canonical CompiledShot
- target output path
- preview/full-render mode
- switch round
- failed work id
- Blender executable when applicable

This is the minimum durable context required to resume the blocked shot.

## Automatic requeue

If a later acquisition tick discovers that a production method now passes all hard
method-switch gates:

- the canonical shot is reconstructed
- the method transform is applied
- a new durable production work item is created
- it is enqueued through TurboStore
- the acquisition case becomes REQUEUED
- the acquisition AGENT work can finish SUCCESS

Current executable requeue path:

Blender canonical shot
-> blender.cycles.quality
-> block.render.method_switch

No creative intent, camera or animation rewrite is needed.

## Live verification

Verifier:

scripts/verify_capability_acquisition_v177.py

Evidence:

data/verification/v177_capability_acquisition/
capability_acquisition_verification.json

### Case A — external research required

Request:

current method = blender.cycles.quality

No alternate cross-tool method passes every gate.

Observed:

- rnd.capability.acquire claimed by AGENT worker
- state after tick: RETRY
- attempts: 0
- reason: AWAITING_AGENT_RESEARCH_RESPONSE
- case state: AWAITING_RESEARCH
- schema-valid reasoning request created
- response path reserved
- metered_generation_api = false

Research sources in the real request:

- OFFICIAL_DOCS
- MODEL_CARDS
- GITHUB
- COMFYUI_WORKFLOW_REGISTRY
- TOOL_ADAPTER_REGISTRY

### Case B — capability becomes available

The verifier deliberately creates acquisition while:

blender.local executable = false

Then before R&D claims the work:

blender.local executable = true

The R&D worker re-evaluates the method request.

Observed acquisition result:

- acquisition work: SUCCESS
- case state: REQUEUED
- selected method: blender.cycles.quality
- durable method-switch work created

The requeued work was then claimed by a real GPU FactoryDaemon.

Observed:

- render engine: CYCLES
- work state: SUCCESS
- media file created
- rendered file size: 5,355 bytes

Verified path:

data/verification/v177_capability_acquisition/
requeue_render/
S01.capability_resume01.mp4

This proves that acquisition can react to a real environment change and return a
canonical shot to production without manually reconstructing the Blender job.

## Worker evidence from the live verifier

AGENT worker:

verify-rnd-agent-v177

- resource: AGENT
- capability: rnd.capability.acquire

GPU worker:

verify-rnd-gpu-v177

- resource: GPU
- capability: blender.animation.render
- active affinity: BLENDER:CYCLES

The machine snapshot reported:

NVIDIA GeForce RTX 3060
VRAM: 12,288 MB

## Tests

New:

tests/test_capability_acquisition_v177.py

Coverage includes:

- durable AGENT defer
- retry budget is not consumed by waiting
- not-before scheduling
- schema-valid reasoning request generation
- no metered-generation API
- external research candidate does not self-approve
- trusted license evidence still requires local artifact
- security gate
- sandbox gate
- benchmark gate
- adapter regression gate
- fully evidenced but unbound candidate remains blocked at ADAPTER
- environment change re-evaluation
- automatic canonical shot requeue
- Cycles method-switch work reconstruction

Targeted v1.6.17 + v1.6.16:

11 PASS

Cross-version regression:

59 PASS

## Full repository verification

v1.6.16:
- 528 PASS

v1.6.17:
- compileall PASS
- pytest 532 PASS
- failures 0

## Key files

New:

- cinefactory/studio/capability_acquisition.py
- tests/test_capability_acquisition_v177.py
- scripts/verify_capability_acquisition_v177.py
- docs/AUTONOMOUS_CAPABILITY_ACQUISITION_RND_V1617.md

Modified:

- cinefactory/appctx.py
- cinefactory/studio/professional_company.py
- cinefactory/studio/production_method_switch.py
- cinefactory/studio/block_production.py
- cinefactory/turbo/store.py
- cinefactory/turbo/daemon.py
- cinefactory/block_animation/factory.py

## What v1.6.17 now does autonomously

1. claims capability-acquisition work
2. snapshots local inventory
3. re-checks method availability
4. reuses current mastery/qualification evidence
5. prepares external research work when necessary
6. waits without consuming retries
7. validates structured research responses
8. separates research evidence from approval
9. verifies local artifact hashes
10. validates durable gate reports
11. refuses unbound candidates
12. automatically requeues the canonical shot when a method becomes executable
13. executes the requeued render through the normal Turbo GPU path

## What remains intentionally blocked

v1.6.17 does not allow the production runtime to:

- browse arbitrary public Internet directly
- install a model because an LLM recommended it
- install plugins automatically
- execute unreviewed repository code
- accept community licensing claims as production evidence
- mark a research response as security approval
- bypass semantic normalization requirements
- create a new runtime adapter from prose and immediately execute it

These are safety and production-integrity boundaries, not missing error handling.

## Next milestone

v1.6.18 should add Capability Acquisition Execution Labs:

1. controlled artifact fetch/import boundary
2. hash + provenance manifest
3. static security scan
4. dependency/SBOM review
5. isolated sandbox runner
6. RTX 3060 hardware benchmark
7. golden-shot benchmark matrix
8. quality / identity / temporal / camera / control scoring
9. automation-readiness evaluation
10. adapter conformance tests
11. block-shot normalization conformance
12. automatic qualification evidence package
13. method registry promotion after all gates
14. post-acquisition episode continuation / editorial recovery

That milestone would move CineFactory from:

research + gated requeue

to:

research -> safely acquire -> benchmark -> qualify -> register -> continue production.
