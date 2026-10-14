# Capability Acquisition Execution Labs v1.6.18

## Goal

v1.6.18 closes two major production gaps left after the autonomous R&D coordinator:

1. Research evidence must become machine-verifiable local evidence before a capability
   can approach production approval.
2. A shot recovered after capability acquisition must be able to return to the episode
   pipeline instead of ending as an isolated recovered render.

The v1.6.18 control path is:

METHOD GAP
-> R&D RESEARCH
-> LOCAL ARTIFACT
-> PROVENANCE + SHA256
-> SBOM
-> STATIC SECURITY
-> HARDWARE FIT
-> TRUSTED SANDBOX
-> GOLDEN-SHOT BENCHMARK
-> ADAPTER / NORMALIZATION CONFORMANCE
-> QUALIFICATION EVIDENCE PACKAGE
-> PRODUCTION METHOD GATES
-> REQUEUE SHOT
-> RENDER + QC
-> CONTINUATION
-> TIMELINE
-> EPISODE ASSEMBLY

Research remains separate from production approval.

## Core modules

New:

- cinefactory/studio/capability_execution_lab.py
- cinefactory/studio/production_continuation.py

New tests:

- tests/test_capability_execution_lab_v178.py
- tests/test_production_continuation_v178.py

New real verifiers:

- scripts/verify_capability_execution_lab_v178.py
- scripts/verify_post_acquisition_continuation_v178.py

## Execution Lab safety boundary

The Execution Lab does not download arbitrary artifacts.

It only imports an artifact that already exists locally.

It also does not execute arbitrary candidate code merely because:

- an LLM recommended it
- a repository looks popular
- a license string was found
- a benchmark claim was found
- a research response says it is safe

Unknown code remains non-executable until an approved execution boundary exists.

## Compact Windows-safe evidence root

Execution Lab evidence is stored under:

.cflab/

This deliberately short root is necessary because CineFactory is commonly installed
under a long Windows Downloads path.

The first v1.6.18 test run exposed a real MAX_PATH failure when evidence used a deeply
nested data/studio/capability_execution_labs path.

v1.6.18 therefore uses:

- compact hashed case keys
- compact hashed candidate keys
- shortened content hash directory names

while retaining the full provenance values inside JSON manifests.

.cflab/ is excluded from git because it contains local/generated execution evidence.

## Provenance manifest

Every imported artifact receives a durable manifest containing:

- candidate id
- source URI
- source type
- source path
- imported path
- artifact kind
- SHA-256
- byte size
- version
- expected SHA-256
- hash verification result
- capture timestamp

Artifact forms currently supported:

- FILE
- ZIP
- DIRECTORY

The imported copy is content-addressed.

A hash mismatch blocks the security/package path.

## Archive safety

ZIP artifacts are inspected before any possible execution.

Current archive gates include:

- member count limit
- uncompressed expansion limit
- absolute-path rejection
- Windows drive-path rejection
- ../ traversal rejection
- embedded executable discovery

A ZIP containing:

../escape.py

is rejected with:

ARCHIVE_PATH_TRAVERSAL:../escape.py

No extraction/execution is required to detect it.

## Static security scan

Current static patterns include:

Critical:
- os.system(...)
- subprocess with shell=True

High:
- eval / exec
- pickle.load / pickle.loads
- Invoke-WebRequest / Invoke-RestMethod
- curl/wget public HTTP fetch

Medium:
- direct requests.* public HTTP
- raw socket usage

Executable artifact extensions are also surfaced.

Current executable extensions include:

- .exe
- .dll
- .msi
- .scr
- .com

A critical static finding makes the security gate fail.

Static scanning is intentionally conservative and is not claimed to be a complete
malware detector.

## SBOM evidence

The lab produces an initial software bill of materials from supported manifests.

Current automatic parsing:

Python:
- requirements.txt
- requirements-dev.txt

Node:
- package.json dependencies
- package.json devDependencies

pyproject.toml is detected but currently requires lock/dependency resolution before it
can be treated as a complete dependency graph.

The SBOM is evidence for later supply-chain review; it is not yet a full CVE scanner.

## Hardware compatibility

A candidate can declare expected VRAM.

The Execution Lab compares it against the real local GPU snapshot.

Target system in the current factory:

NVIDIA GeForce RTX 3060
12 GB VRAM

A 16 GB candidate tested against a 12 GB snapshot fails with:

VRAM_REQUIREMENT_EXCEEDS_DEVICE

The current gate checks basic VRAM fit.

It does not yet model:
- peak transient VRAM
- fragmentation
- simultaneous model residency
- host RAM offload penalties
- PCIe transfer overhead

Those belong in later runtime benchmarks.

## Trusted sandbox rule

The default sandbox state for an external candidate is:

BLOCKED

with:

- EXECUTION_SANDBOX_NOT_AVAILABLE
- UNTRUSTED_CANDIDATE_CODE_NOT_EXECUTED

A candidate gets SANDBOX PASS only through an explicitly trusted executor/evidence path.

This prevents the Execution Lab itself from becoming a generic arbitrary-code runner.

## Evidence replay protection

v1.6.18 hardens the v1.6.17 evidence model.

Previously a generic local JSON containing:

{"passed": true}

could be interpreted as evidence by the old acquisition helper.

That is no longer sufficient.

Trusted execution evidence must:

1. exist under .cflab/reports/
2. match the expected case id
3. match the expected candidate id
4. match the expected report type

Therefore a PASS sandbox report from candidate A cannot be replayed as candidate B's
sandbox evidence.

Arbitrary JSON outside the lab root is rejected.

## Security-review tightening

A research-agent security reference alone no longer marks a candidate security-reviewed.

The current acquisition rule requires:

- artifact hash verified
- static security report PASS
- trusted sandbox report PASS
- security evidence reference present

This is deliberately stricter than v1.6.17.

## Golden-shot benchmark

For registered production methods, the Execution Lab can benchmark a real Block
Animation runtime result.

Current measured dimensions:

1. quality
2. identity
3. temporal
4. camera_contract
5. control

These scores are derived from runtime evidence, not from routing metadata.

### Quality

Uses:
- qc_passed
- rendered_frame_qc.passed

### Identity

Uses:
- identity_qc.passed
- identity_qc.score

The current Blender identity score means rig/structural identity conformance, not
semantic face-recognition identity.

### Temporal

Uses:
- black-frame duration
- frozen-frame duration
- clip duration
- visual QC pass/fail

### Camera contract

Uses:
- geometry QC
- screen-target blockers
- measured render-state camera start/end

### Control

Uses:
- creative_intent_bound
- performance_qc score

The benchmark threshold is currently:

0.80 aggregate

This is a production gate, not a claim of market superiority.

## Real v1.6.18 golden-shot verification

Verifier:

scripts/verify_capability_execution_lab_v178.py

Registered method:

blender.cycles.quality

Execution path:

ProductionMethodSwitchController
-> block.render.method_switch
-> FactoryDaemon GPU
-> Blender Cycles
-> BlockAnimationRuntime
-> deterministic QC

Real output:

data/verification/v178_capability_execution_lab/
golden_shot/
S01.cycles.golden.mp4

Latest verified media size:

5,355 bytes

Real machine snapshot during the verifier:

- NVIDIA GeForce RTX 3060
- 12,288 MB VRAM

Observed gates:

- provenance hash: PASS
- security: PASS
- hardware: PASS
- trusted sandbox: PASS
- benchmark: PASS
- conformance: PASS
- qualification evidence package: PASS

Measured benchmark dimensions in this deterministic fixture:

- quality: 1.0
- identity: 1.0
- temporal: 1.0
- camera_contract: 1.0
- control: 1.0
- aggregate: 1.0

This means the verification fixture passed all currently measured contracts.

It does NOT mean Blender Cycles is universally perfect or externally benchmark-leading.

## Qualification evidence package

The lab creates a durable QualificationEvidencePackage pointing to:

- provenance report
- SBOM report
- security report
- hardware report
- sandbox report
- benchmark report
- conformance report

Package PASS requires every mandatory gate to PASS.

The real Cycles package was written under the compact .cflab report tree.

## Malicious-candidate verification

The same real verifier creates an intentionally malicious ZIP containing:

- ../escape.py
- plugin.py with os.system('whoami')

Observed:

security:
- FAIL

blockers:
- ARCHIVE_PATH_TRAVERSAL:../escape.py
- CRITICAL_STATIC_SECURITY_FINDING

finding:
- OS_SYSTEM_EXECUTION

sandbox:
- BLOCKED

The candidate is never executed.

## Adapter and normalization conformance

Current conformance requires:

- adapter registered
- execution handler registered
- normalization passed
- canonical round-trip passed

For same-scene methods such as Blender Eevee -> Blender Cycles, canonical scene semantics
can satisfy normalization because scene, rig, camera and animation are preserved.

Cross-backend methods still require explicit normalization evidence.

Research prose cannot satisfy this gate.

## Acquisition-worker integration

CapabilityAcquisitionWorker now automatically runs the static portion of the Execution
Lab when a research candidate supplies:

- local artifact path
- expected SHA-256

It generates:

- provenance
- SBOM
- static security
- hardware fit
- qualification evidence package

It does not manufacture sandbox or benchmark success.

A candidate remains blocked until trusted evidence exists.

## Stronger unbound-candidate behavior

An otherwise strong candidate that has not been bound to:

- ProductionMethodSpec
- registered execution handler
- normalization path
- canonical round-trip

now fails at:

CONFORMANCE:FAIL

rather than becoming APPROVED first and only later discovering the missing binding.

This moves failure earlier in the acquisition lifecycle.

## Post-acquisition continuation

New:

cinefactory/studio/production_continuation.py

The company now persists episode recovery state when a shot is blocked on capability
acquisition.

Per-shot continuation states:

- PENDING
- ACCEPTED
- WAITING_CAPABILITY
- REQUEUED
- FAILED

A continuation record stores:

- project id
- episode id
- output path
- shot order
- shot duration
- accepted render work ids
- acquisition work ids
- recovered paths
- selected method
- post-production state

## Continuation creation

If BlockAnimation production ends with one or more capability-acquisition failures:

- already accepted shots are stored as ACCEPTED
- acquisition-blocked shots are WAITING_CAPABILITY
- unrelated hard failures are FAILED

Post-production is not enqueued while any required shot remains unresolved.

## Durable resume context

Capability acquisition now carries:

- canonical CompiledShot
- output path
- render-preview mode
- switch round
- failed render work id
- Blender executable when applicable
- continuation id
- continuation shot id

When R&D requeues the shot, the method-switch work receives the continuation contract.

## QC-gated acceptance

A recovered method-switch render is not marked continuation-accepted merely because it
was queued.

Acceptance happens only after:

- the render handler returns success
- BlockAnimationRuntime QC has passed
- Turbo marks the render work SUCCESS

Only then does FactoryDaemon call:

ProductionContinuationManager.accept_requeued_render(...)

## Automatic return to post-production

When all episode shots become ACCEPTED, CineFactory automatically creates:

timeline.accept
-> block.episode.assemble

Timeline work depends on the accepted render work.

Episode assembly depends on all timeline work.

The recovered failed render is therefore not bypassing the normal post-production
dependency graph.

## Deterministic/idempotent continuation work IDs

Continuation post work uses deterministic IDs:

WORK_CONT_TL_<hash>

and:

WORK_CONT_ASM_<hash>

This means a retry/crash/repeated continuation notification does not create duplicate
timeline or assembly jobs.

## Real end-to-end continuation verification

Verifier:

scripts/verify_post_acquisition_continuation_v178.py

Scenario:

1. one Minecraft block-animation shot
2. blender.local deliberately marked non-executable
3. MethodSwitch is blocked
4. rnd.capability.acquire is created
5. episode continuation is stored as WAITING_CAPABILITY
6. blender.local becomes executable
7. R&D worker re-evaluates
8. acquisition work succeeds
9. blender.cycles.quality is requeued
10. GPU worker renders and passes QC
11. continuation moves to ACCEPTED
12. timeline work is automatically enqueued
13. assembly work is automatically enqueued
14. IO worker executes timeline
15. IO worker executes assembly
16. final episode file is created
17. repeated continuation acceptance does not add duplicate work

Latest real result:

Acquisition:
- SUCCESS

Recovered render:
- method: blender.cycles.quality
- engine: CYCLES
- SUCCESS
- file size: 5,355 bytes

Timeline:
- SUCCESS

Assembly:
- SUCCESS
- final episode size: 6,165 bytes

Final episode:

data/verification/v178_post_acquisition_continuation/
episode/
VERIFY_CONTINUATION_V178.mp4

Continuation state:

- shot: ACCEPTED
- post_enqueued: true

The dependency chain was verified:

recovered Cycles render
-> timeline.accept
-> block.episode.assemble

## Tests

Execution Lab + acquisition + continuation targeted regression:

- 19 PASS

Earlier continuation/method/economics regression:

- 34 PASS

Cross-version v1.6.14 through v1.6.18:

- 73 PASS

## Full repository verification

Previous milestone:

v1.6.17:
- 532 PASS

v1.6.18:
- compileall PASS
- pytest 547 PASS
- failures 0

## Key files

New:

- cinefactory/studio/capability_execution_lab.py
- cinefactory/studio/production_continuation.py
- tests/test_capability_execution_lab_v178.py
- tests/test_production_continuation_v178.py
- scripts/verify_capability_execution_lab_v178.py
- scripts/verify_post_acquisition_continuation_v178.py
- docs/CAPABILITY_EXECUTION_LABS_V1618.md

Modified:

- cinefactory/studio/capability_acquisition.py
- cinefactory/studio/block_production.py
- cinefactory/turbo/daemon.py
- cinefactory/appctx.py
- cinefactory/studio/professional_company.py
- tests/test_capability_acquisition_v177.py
- .gitignore

## Evidence

Execution Lab:

data/verification/v178_capability_execution_lab/
capability_execution_lab_verification.json

Golden Cycles render:

data/verification/v178_capability_execution_lab/
golden_shot/
S01.cycles.golden.mp4

Post-acquisition continuation:

data/verification/v178_post_acquisition_continuation/
post_acquisition_continuation_verification.json

Recovered shot:

data/verification/v178_post_acquisition_continuation/
episode/
S01.capability_recovered.mp4

Final recovered episode:

data/verification/v178_post_acquisition_continuation/
episode/
VERIFY_CONTINUATION_V178.mp4

Local generated evidence:

.cflab/

## What v1.6.18 proves

CineFactory can now:

1. import an already-local candidate artifact safely
2. preserve provenance and SHA-256
3. reject hash mismatch
4. detect ZIP traversal
5. detect several critical/high-risk static execution patterns
6. generate an initial SBOM
7. check basic RTX 3060 VRAM fit
8. refuse to execute unknown candidate code by default
9. protect lab evidence from cross-candidate replay
10. create measured golden-shot benchmark evidence
11. create a multi-gate qualification evidence package
12. keep research evidence separate from production approval
13. persist an episode blocked by capability acquisition
14. requeue its canonical shot when a method becomes executable
15. accept the recovered shot only after real QC success
16. automatically return the episode to timeline and assembly
17. avoid duplicate post-production work during retries

## What v1.6.18 does not claim

It does not claim that:

- static scanning is a full malware scanner
- the current SBOM parser is complete
- package vulnerabilities/CVEs are automatically resolved
- remote artifacts can be downloaded safely yet
- arbitrary third-party code has an OS-level sandbox
- digital signatures are verified
- every external model license is automatically legally approved
- the 1.0 golden-shot fixture score means benchmark leadership
- ComfyUI video, Unreal, Minecraft runtime or Roblox runtime are now production-ready

Those capabilities still require real evidence and adapters.

## Next milestone

Recommended v1.6.19:

Trusted Artifact Intake + Isolated Execution Sandbox + Automatic Method Promotion.

Priority sequence:

1. controlled artifact fetch/import service
2. domain allowlist + HTTPS-only + size/content limits
3. expected-hash / release-manifest verification
4. Git commit/tag provenance where available
5. signed-release verification where available
6. expanded SBOM and lockfile parsing
7. dependency vulnerability policy
8. isolated subprocess/container sandbox
9. no-network sandbox default
10. CPU/RAM/VRAM/time/disk quotas
11. golden-shot benchmark harness for candidate adapters
12. automatic adapter conformance suite
13. production qualification evidence generation
14. guarded method-registry promotion
15. automatic retry of the original blocked production item

Only after these gates should CineFactory move from:

"research candidate"

to:

"new external production capability automatically acquired and promoted."
