# Trusted Candidate Lab Executor + Automatic Promotion v1.6.19

## Goal

v1.6.19 closes the authority gap between:

R&D CANDIDATE DISCOVERED
and
SAFE REGISTRY PROMOTION / PRODUCTION EXECUTABILITY.

The new control path is:

CAPABILITY GAP
-> R&D candidate
-> artifact classification
-> rights gate
-> durable candidate-lab work
-> Turbo GPU scheduling
-> trusted declarative execution
-> Execution Lab evidence
-> workflow registry promotion
-> multi-shot benchmark matrix
-> method attestation
-> production routing only if every hard gate passes

The central rule is:

REGISTRY_PROMOTED != PRODUCTION_EXECUTABLE

A workflow can be useful and safely registered without gaining authority to render
canonical block shots.

## Core module

New:

cinefactory/studio/candidate_promotion.py

Main objects:

- TrustedArtifactClass
- CandidateExecutionState
- PromotionState
- CandidateSandboxProfile
- CandidateClassification
- TrustedCandidateExecution
- BenchmarkMatrixRow
- BenchmarkMatrixReport
- PromotionAttestation
- CandidatePromotionStore
- TrustedCandidateLabExecutor
- MultiShotBenchmarkMatrix
- CandidatePromotionController

## Company integration

AppContext now exposes:

- candidate_promotion

ProfessionalCompanyLayer now exposes:

- candidate_promotion

The controller shares:

- ModelRegistry
- ExecutorRegistry
- WorkflowRegistry
- ProductionMethodSwitchController
- CapabilityExecutionLab

with the rest of CineFactory.

CapabilityAcquisitionWorker receives the same promotion controller.

## Promotion states

The authority levels are:

EVIDENCE_ONLY

The candidate has evidence but no lab/promotion authority.

LAB_APPROVED

The candidate has passed the relevant lab evidence layer.

REGISTRY_PROMOTED

A safe scoped artifact such as a declarative local ComfyUI workflow may be written to
the workflow registry.

This does not mean it may replace a canonical production backend.

PRODUCTION_EXECUTABLE

The registered production method additionally passes:

- method specification exists
- execution handler exists
- capability is executable
- qualification gates
- rights/commercial policy
- quality floor
- VRAM policy
- continuity policy
- workflow/model gates
- normalization gates
- multi-shot benchmark matrix

BLOCKED

One or more hard gates remain unresolved.

## Trusted artifact classes

v1.6.19 classifies local candidate artifacts before any execution decision.

Current classes:

- COMFYUI_WORKFLOW_JSON
- MODEL_SAFETENSORS
- PURE_DATA_ASSET
- REGISTERED_METHOD_MANIFEST
- PYTHON_CODE
- SCRIPT_CODE
- NATIVE_BINARY
- ARCHIVE
- UNKNOWN

## Automatic execution authority

Current automatic execution is intentionally narrow.

Allowed execution class:

COMFYUI_WORKFLOW_JSON

It is not executed as a process.

It is submitted only through CineFactory's already-approved:

local.comfyui

executor.

Non-executable automatic validation classes include:

MODEL_SAFETENSORS
PURE_DATA_ASSET

These can be hashed / inspected / registered as evidence but are not executed as code.

Hard-blocked automatic classes include:

PYTHON_CODE
SCRIPT_CODE
NATIVE_BINARY
ARCHIVE
UNKNOWN

Arbitrary Python/native plugins therefore cannot move from research to execution through
this controller.

## Candidate sandbox profile

Default declarative profile:

profile_id:
declarative_local_v1

Policy:

- public network allowed: false
- loopback/LAN allowed: true
- candidate process spawn allowed: false
- source read-only intent: true
- scratch-only write intent: true
- maximum artifact size: 512 MB
- maximum workflow nodes: 250
- maximum configured runtime: 900 seconds
- maximum output files: 64

The underlying ComfyUI executor already has its own local/LAN URL restriction and runtime
timeout.

The candidate controller does not grant shell/process execution to workflow JSON.

## Local/LAN network boundary

The trusted executor must not be PUBLIC_INTERNET.

Current accepted path:

127.0.0.1 / private LAN
-> local.comfyui

The workflow itself is independently scanned by WorkflowSafetyValidator.

It rejects configured public/network or metered-provider signals.

Therefore both:

executor network scope
and
workflow contents

must satisfy policy.

## Model approval gate

A ComfyUI candidate cannot run merely because its JSON is syntactically valid.

The workflow must reference a model that passes:

ModelRegistry.require_approved(...)

This requires the model record to satisfy the existing production controls, including:

- approved_for_production
- commercial_use_reviewed
- output_terms_reviewed

The real v1.6.19 verifier used:

stable-diffusion-v1-5-emaonly

revision:

sha256:6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa

which was already present and production-approved.

## Durable candidate execution

Candidate execution is now a Turbo work item.

Kind:

lab.comfyui.candidate

Handler:

lab.comfyui.execute

Resource:

GPU

This is important.

R&D AGENT workers do not directly call ComfyUI and consume GPU outside the scheduler.

The flow is:

AGENT
-> enqueue lab.comfyui.execute
-> defer

GPU
-> claim lab work
-> execute trusted local workflow
-> persist result

AGENT
-> wake later
-> inspect lab evidence
-> evaluate promotion

## GPU resource accounting

ContinuousBlockFactory's GPU lane now recognizes:

- blender.animation.render
- lab.comfyui.execute

The candidate work may also include:

required_vram_gb

for the existing Turbo scheduler's VRAM gate.

This keeps candidate qualification inside the same resource-control plane as production.

## Candidate lab result

Durable evidence records:

- candidate id
- artifact class
- sandbox profile
- preflight state
- execution attempted
- execution passed
- output artifacts
- workflow SHA-256
- ComfyUI object-info SHA-256
- findings
- model id/revision
- executor provenance

A rejected candidate may complete the lab evaluation without gaining promotion.

"Lab work completed" is not the same as "candidate approved".

## Rights gate before promotion

Automatic workflow promotion requires explicit scoped rights clearance.

Current promotion API requires:

rights_cleared = true

R&D derives this only when:

- license name exists
- license evidence exists
- evidence tier is OFFICIAL or MAINTAINER
- commercial_use_allowed is true

If this is not satisfied:

COMMERCIAL_RIGHTS_NOT_CLEARED
-> BLOCKED

The workflow is not added to the registry.

## Safe workflow promotion

After trusted execution and Execution Lab evidence pass, the promotion controller can
write a workflow into a WorkflowRegistry.

The promoted structure is versioned under:

<promotion registry>/promoted/<workflow_id_version>/

with:

- workflow.json
- workflow.manifest.yaml

Collision behavior is fail-closed.

If the same workflow id/version already exists with different content:

PROMOTION_WORKFLOW_VERSION_COLLISION

If the manifest differs:

PROMOTION_MANIFEST_VERSION_COLLISION

Existing identical promotion is idempotent.

## Isolated real registry verification

The real v1.6.19 verifier used an isolated WorkflowRegistry under:

data/verification/v179_candidate_promotion/
promoted_workflows/

This proves registry installation without polluting the production workflow directory.

The promoted workflow was:

verify.v179.comfy.sd15@1

State:

REGISTRY_PROMOTED

Registry count:

1

## Real ComfyUI execution

ComfyUI was reachable locally at:

http://127.0.0.1:8188

The verifier used the existing approved core-node workflow:

comfy.mastery.sd15@1

The candidate was executed through:

Turbo GPU work
-> lab.comfyui.execute
-> local.comfyui

Observed:

lab work state = SUCCESS
execution_passed = true

Real artifact:

data/verification/v179_candidate_promotion/
comfy_candidate/
CineFactory_Mastery_00002_.png

Size:

425,732 bytes

The executor captured:

- prompt id
- workflow SHA-256
- object_info SHA-256
- required nodes
- available nodes
- model requirement
- deterministic seed
- output provenance

## Real ComfyUI preflight

Required core nodes in the verified run included:

- CheckpointLoaderSimple
- CLIPTextEncode
- EmptyLatentImage
- KSampler
- VAEDecode
- SaveImage

Observed:

- missing node types: none
- invalid model inputs: none
- workflow safety findings: none
- preflight valid: true

No custom downloaded candidate code was executed.

## Explicit Python rejection

The verifier created an untrusted Python file.

Classification:

PYTHON_CODE

Result:

auto_execution_allowed = false

Finding:

AUTO_EXECUTION_CLASS_BLOCKED:PYTHON_CODE

The file was never executed.

## Multi-shot benchmark matrix

v1.6.18 proved one golden shot.

v1.6.19 introduces a method-level matrix.

Production executable attestation now requires multiple representative cases.

Default test policy used:

required_cases = 2
minimum_dimension_score = 0.80

Each case is evaluated using the existing runtime evidence dimensions:

- quality
- identity
- temporal
- camera_contract
- control

The matrix stores:

- every individual BenchmarkReport
- per-dimension mean
- per-dimension minimum
- aggregate mean
- aggregate minimum
- blockers

The minimum matters.

A high average cannot hide one badly failing shot.

## Real Cycles matrix

The verifier created two separate golden-shot cases:

S01
S02

Both were transformed through:

blender.cycles.quality

Both ran as real Turbo GPU render work.

Observed states:

S01 = SUCCESS
S02 = SUCCESS

Files:

data/verification/v179_candidate_promotion/
cycles_matrix/
S01.cycles.golden.mp4

data/verification/v179_candidate_promotion/
cycles_matrix/
S02.cycles.golden.mp4

Each file:

5,355 bytes

## Real matrix scores

Observed matrix:

matrix_passed = true

aggregate mean:

1.0

aggregate minimum:

1.0

Per-dimension minima:

- quality = 1.0
- identity = 1.0
- temporal = 1.0
- camera_contract = 1.0
- control = 1.0

These scores apply to the controlled v1.6.19 verification fixtures.

They are not a universal external-quality claim.

## Registered-method attestation

CandidatePromotionController can now attest an existing production method.

Inputs:

- trusted QualificationEvidencePackage
- multi-shot BenchmarkMatrixReport
- MethodSwitchRequest
- registered ProductionMethodSpec

The controller re-runs the specific MethodSwitch assessment.

Only if all layers pass does it issue:

PRODUCTION_EXECUTABLE

## Real Cycles production attestation

Method:

blender.cycles.quality

Evidence:

- trusted qualification package: PASS
- two-shot matrix: PASS
- method-switch hard gates: PASS

Result:

PRODUCTION_EXECUTABLE

The attestation is durable under:

data/verification/v179_candidate_promotion/
promotion/
attestations/

## Weak-case rejection proof

The verifier then created a second matrix where one identity score was deliberately
reduced to:

0.50

Policy floor:

0.80

Observed:

weak_matrix_passed = false

Weak method attestation:

BLOCKED

Therefore:

one bad representative case
cannot be hidden by
one perfect case.

## Benchmark matrix durability

The real verifier stored:

MATRIX_V179_CYCLES.json
MATRIX_V179_CYCLES_WEAK.json

under:

data/verification/v179_candidate_promotion/
promotion/
benchmark_matrices/

Promotion attestations and matrix evidence are separate durable artifacts.

## Automatic R&D -> GPU -> promotion integration

CapabilityResearchCandidate now optionally carries:

workflow_manifest

When R&D receives such a candidate with:

- local artifact
- expected hash
- workflow manifest
- rights evidence

CapabilityAcquisitionWorker can initiate automatic scoped promotion.

It does not execute the candidate itself.

## New acquisition state

New durable state:

AWAITING_LAB

The acquisition sequence is:

RESEARCH_RECEIVED
-> enqueue lab.comfyui.candidate
-> AWAITING_LAB
-> RETRY without burning attempts
-> GPU lab work
-> AGENT retry
-> promotion evaluation

## Automatic acquisition verifier

Real verifier:

scripts/verify_acquisition_auto_promotion_v179.py

Scenario:

1. block-shot method request is already using Cycles
2. no valid alternate block method exists
3. acquisition work is created
4. research response contains an approved local SD1.5 image workflow candidate
5. AGENT processes the response
6. AGENT enqueues GPU candidate lab work
7. acquisition work is deferred
8. attempts remain 0
9. GPU lane executes the ComfyUI candidate
10. GPU lab work succeeds
11. AGENT retries after the durable not-before period
12. trusted evidence is ingested
13. workflow is REGISTRY_PROMOTED
14. method gap is re-evaluated
15. acquisition remains unresolved because the image workflow does not solve the block-shot
   production method gap

## Real automatic acquisition states

First AGENT pass:

acquisition:
RETRY

reason:

AWAITING_CANDIDATE_LAB_EXECUTION

attempts:

0

Candidate lab work:

resource = GPU
state before GPU = QUEUED

After GPU:

state = SUCCESS
passed = true

Second AGENT pass:

promotion = REGISTRY_PROMOTED

But acquisition remains:

RETRY

reason:

CAPABILITY_GATES_STILL_INCOMPLETE

Method decision remains:

BLOCKED_ACQUISITION

This is deliberate scoped authority.

## Why the image workflow did not unlock the blocked shot

The candidate was an image-generation workflow.

The unresolved production request was a canonical block-animation method gap.

Promoting an image workflow therefore cannot imply:

"we now have a block-video backend."

The system re-runs MethodSwitchController and leaves the shot blocked.

This prevents category substitution errors.

## Promotion versus production method

v1.6.19 therefore has two independent questions.

Question 1:

Is this artifact safe/useful enough to enter a scoped registry?

Possible answer:

REGISTRY_PROMOTED

Question 2:

Can this method execute this production contract?

Possible answer:

PRODUCTION_EXECUTABLE
or
BLOCKED

This separation is mandatory for safe autonomous R&D.

## Workflow promotion does not auto-create arbitrary method code

The controller does not generate a new Python adapter or native execution handler from
an LLM response.

If a video workflow is promoted but the method still lacks:

- block-shot normalization
- continuity adapter
- appropriate quality evidence
- commercial method evidence
- production qualification
- registered execution behavior

MethodSwitchController continues to block it.

## Windows path hardening

v1.6.19 exposed another Windows MAX_PATH edge case in deeply nested pytest temp roots.

Execution Lab imports were previously:

imports/
  <case>/
    <candidate>/
      <digest>/
        artifact

This could still exceed legacy path limits.

Imports are now globally content-addressed:

imports/
  <digest-prefix>/
    artifact.<suffix>

Case and candidate identity remain in provenance metadata and report paths.

This shortens the physical import path without weakening hash identity.

The fix was discovered by a real targeted regression, not by theoretical inspection.

## Tests

New:

tests/test_candidate_promotion_v179.py

Coverage includes:

- Python candidate blocked
- native candidate blocked
- declarative workflow only through trusted local executor
- no public-network authority
- no candidate process-spawn authority
- multi-shot matrix PASS
- weak matrix rejection
- rights gate before registry promotion
- safe auto qualification and workflow registration
- AppContext / ProfessionalCompany shared controller
- candidate lab as durable GPU work
- acquisition waits for GPU lab
- promotion occurs only after GPU lab PASS

Additional v1.6.18 context-sharing test was also added for the shared Execution Lab.

## Verification counts

Candidate/promotion targeted suite after scheduler integration:

24 PASS

Cross-version regression:

66 PASS

## Full repository verification

Previous milestone:

v1.6.18:
- 546 PASS

Current milestone:

v1.6.19:
- compileall PASS
- pytest 555 PASS
- failures 0

## Real evidence

Primary verifier:

data/verification/v179_candidate_promotion/
candidate_promotion_verification.json

Size:

2,707 bytes

Real Comfy artifact:

data/verification/v179_candidate_promotion/
comfy_candidate/
CineFactory_Mastery_00002_.png

Size:

425,732 bytes

Cycles golden shots:

data/verification/v179_candidate_promotion/
cycles_matrix/
S01.cycles.golden.mp4

5,355 bytes

data/verification/v179_candidate_promotion/
cycles_matrix/
S02.cycles.golden.mp4

5,355 bytes

Automatic acquisition verifier:

data/verification/v179_acquisition_auto_promotion/
acquisition_auto_promotion_verification.json

Size:

9,254 bytes

## Durable promotion evidence

The primary verification produced:

3 promotion attestations

and:

2 benchmark matrix reports

These include:

- successful Comfy workflow registry promotion
- successful Cycles production attestation
- blocked weak-matrix Cycles attestation

## Key files

New:

- cinefactory/studio/candidate_promotion.py
- tests/test_candidate_promotion_v179.py
- scripts/verify_candidate_promotion_v179.py
- scripts/verify_acquisition_auto_promotion_v179.py
- docs/TRUSTED_CANDIDATE_LAB_PROMOTION_V1619.md

Modified:

- cinefactory/studio/capability_acquisition.py
- cinefactory/studio/capability_execution_lab.py
- cinefactory/appctx.py
- cinefactory/studio/professional_company.py
- cinefactory/turbo/daemon.py
- cinefactory/block_animation/factory.py
- tests/test_capability_execution_lab_v178.py

## What v1.6.19 now does autonomously

1. classify candidate artifacts
2. reject arbitrary executable/code classes from automatic execution
3. validate declarative ComfyUI workflow JSON
4. enforce approved-model lookup
5. enforce local/LAN executor policy
6. enqueue candidate execution as durable GPU work
7. preserve AGENT/GPU resource separation
8. defer acquisition without consuming retry attempts
9. execute approved declarative workflow through local ComfyUI
10. capture real execution provenance
11. build trusted Execution Lab evidence
12. promote a safe workflow into a scoped WorkflowRegistry
13. issue durable promotion attestations
14. benchmark registered methods across multiple real cases
15. use worst-case dimension scores, not average only
16. refuse production attestation when one matrix case fails
17. issue PRODUCTION_EXECUTABLE only after method hard gates pass
18. automatically process candidate promotion from R&D acquisition responses
19. re-evaluate the original production gap after promotion
20. leave the gap blocked if the promoted artifact does not satisfy that contract

## What v1.6.19 intentionally does not do

It does not:

- auto-run downloaded Python packages
- auto-run EXE/DLL/MSI/native plugins
- auto-install GitHub repositories
- auto-pip-install arbitrary requirements
- allow public Internet inside production candidate execution
- treat safetensors as executable code
- make an image workflow solve a video contract
- bypass model licensing review
- bypass method qualification
- bypass cross-backend normalization
- claim benchmark leadership from two controlled fixtures

These remain hard safety and engineering boundaries.

## Next high-priority milestone

v1.6.20 should target the largest remaining production gap:

Cross-Backend Block-Shot Normalization + Local Video Workflow Qualification.

Recommended order:

1. define canonical BlockShot -> generative-video contract
2. define identity/reference conditioning contract
3. define camera/motion intent serialization
4. define temporal duration/FPS contract
5. define canonical output normalization back into CineFactory
6. build local video workflow registry
7. qualify one RTX-3060-compatible video model/workflow
8. run license/model-card/security review
9. execute through Trusted Candidate Lab
10. benchmark multiple shots
11. compare against Cycles and current Blender paths
12. create identity / temporal / camera continuity gates
13. register a real ComfyUI video ProductionMethodSpec only after evidence
14. remove BLOCK_SHOT_NORMALIZATION_ADAPTER_MISSING only for that qualified adapter
15. prove method-switch Blender -> local video -> QC -> continuation end-to-end

That milestone would turn the current safe workflow-promotion machinery into a genuinely
usable second video backend rather than only a registry/R&D capability.
