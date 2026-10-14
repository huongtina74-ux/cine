# Capability Acquisition Execution Labs v1.6.18

## Goal

v1.6.18 adds the missing evidence layer between:

RESEARCH CANDIDATE
and
PRODUCTION QUALIFICATION.

The production path is now:

CAPABILITY GAP
-> R&D research
-> local artifact
-> provenance/hash
-> SBOM
-> static security
-> hardware fit
-> trusted sandbox execution
-> golden-shot benchmark
-> adapter/normalization conformance
-> qualification evidence package
-> method qualification/registration
-> production requeue
-> post-acquisition episode continuation

The central safety invariant remains:

Research is not approval.
Artifact possession is not approval.
A passing benchmark is not approval.
Only a fully gated executable method may enter production.

## Core modules

New/extended:

- cinefactory/studio/capability_execution_lab.py
- cinefactory/studio/capability_acquisition.py
- cinefactory/studio/production_continuation.py
- cinefactory/appctx.py
- cinefactory/studio/professional_company.py
- cinefactory/studio/block_production.py
- cinefactory/turbo/daemon.py

Tests:

- tests/test_capability_execution_lab_v178.py
- tests/test_production_continuation_v178.py

Real verifiers:

- scripts/verify_capability_execution_lab_v178.py
- scripts/verify_production_continuation_v178.py

## Shared company capability

AppContext now exposes:

- capability_execution_lab

ProfessionalCompanyLayer now exposes:

- capability_execution_lab

It is the exact same object used by CapabilityAcquisitionWorker.

Therefore R&D, Risk, QC and Production can reference the same evidence store and policy
rather than constructing separate lab states.

## Short evidence root on Windows

The Execution Lab stores controlled evidence under:

.cflab/

This short path is intentional.

The project currently lives under a very long Windows Downloads path. Deeply nested
content-addressed paths can otherwise approach legacy Windows MAX_PATH behavior.

The lab still keeps:

- deterministic compact candidate keys
- SHA-256 provenance
- immutable imported evidence paths
- per-candidate report directories

The short root is a path-safety optimization, not a temporary trust bypass.

## Local artifact import

The lab does not download unknown external code.

It accepts an already-local file/directory/archive and creates a content-addressed
import.

Evidence includes:

- source URI
- source type
- source path
- imported path
- artifact type
- SHA-256
- bytes
- declared version
- expected hash
- whether expected hash matched

Supported artifact types:

- FILE
- ZIP
- DIRECTORY

Hash mismatch is a hard security blocker.

## Archive safety

ZIP artifacts are inspected before any execution.

Current hard checks include:

- member-count limit
- total uncompressed-byte limit
- absolute paths
- Windows drive paths
- .. traversal
- embedded executable extensions

Verified hostile fixture:

../escape.py

Result:

ARCHIVE_PATH_TRAVERSAL:../escape.py

The candidate never reached execution.

## Static security scan

The lab performs a conservative static scan over supported text/code files.

Current detections include:

CRITICAL:
- os.system(...)
- subprocess ... shell=True

HIGH:
- eval(...)
- exec(...)
- pickle.load / pickle.loads
- PowerShell Invoke-WebRequest / Invoke-RestMethod
- shell curl/wget public HTTP

MEDIUM:
- direct public requests.get/post/...
- raw sockets

This is a production gate, not a claim of complete malware detection.

A static PASS means:
- no configured critical blocker was found
- provenance hash matched
- archive safety passed

It does not replace a mature antivirus/EDR/supply-chain security program.

## Real malicious-package proof

The v1.6.18 verifier created a ZIP containing:

plugin.py:
    os.system('whoami')

and:

../escape.py

Observed:

security_status = FAIL

blockers:
- ARCHIVE_PATH_TRAVERSAL:../escape.py
- CRITICAL_STATIC_SECURITY_FINDING

finding:
- severity = CRITICAL
- code = OS_SYSTEM_EXECUTION
- path = plugin.py
- line = 2

Sandbox result:

BLOCKED

The malicious fixture was not executed.

## SBOM

The lab generates a lightweight dependency inventory.

Current automatic parsers include:

Python:
- requirements.txt
- requirements-dev.txt

Node:
- package.json dependencies
- package.json devDependencies

pyproject.toml is detected, but currently requires a lock-resolution step before the
lab claims exact resolved dependency versions.

The SBOM is deliberately evidence-oriented rather than pretending that an unresolved
version range is a full supply-chain lock.

## Hardware-fit gate

The lab can compare candidate VRAM requirements against the live GPU snapshot.

Target hardware:

NVIDIA RTX 3060 12GB

Verified machine snapshot in the real v1.6.18 run:

- NVIDIA GeForce RTX 3060
- VRAM: 12,288 MB

A candidate requiring 16 GB fails:

VRAM_REQUIREMENT_EXCEEDS_DEVICE

Missing GPU evidence yields BLOCKED rather than optimistic PASS.

## Sandbox boundary

The lab never executes arbitrary candidate code by default.

Without a registered trusted executor:

sandbox_status = BLOCKED

findings:
- EXECUTION_SANDBOX_NOT_AVAILABLE
- UNTRUSTED_CANDIDATE_CODE_NOT_EXECUTED

This is intentional.

A sandbox PASS requires:

- static security PASS
- an explicitly trusted executor id
- successful trusted execution evidence

v1.6.18 does not turn a research ZIP into a subprocess.

## Trusted registered-method benchmark

For an already registered and executable production method, CineFactory can use its
existing trusted Turbo handler as the sandbox executor.

Real verified method:

blender.cycles.quality

Executor:

turbo.blender.animation.render

The method was already:
- present in MethodSwitchController
- bound to the Blender canonical shot contract
- connected to a registered Turbo handler
- using the existing trusted Blender runtime

Therefore it could be benchmarked through the normal production path.

## Golden-shot benchmark

v1.6.18 converts measured block runtime evidence into five explicit dimensions:

1. quality
2. identity
3. temporal
4. camera_contract
5. control

### quality

Derived from:
- overall QC
- rendered-frame QC

### identity

Derived from:
- identity_qc.pass
- identity_qc.score

### temporal

Derived from:
- visual QC
- black duration
- freeze duration
- actual clip duration

### camera_contract

Requires:
- geometry QC PASS
- start camera state
- end camera state
- no geometry target blockers

### control

Derived from:
- creative intent binding
- measured performance QC

The benchmark threshold is policy-controlled.

Current default floor:

0.80

## Real v1.6.18 golden-shot result

Method:

blender.cycles.quality

Turbo render:

SUCCESS

Rendered file:

data/verification/v178_capability_execution_lab/
golden_shot/
S01.cycles.golden.mp4

Rendered bytes:

5,355

Measured benchmark:

- quality = 1.0
- identity = 1.0
- temporal = 1.0
- camera_contract = 1.0
- control = 1.0
- aggregate = 1.0

This is a PASS for this controlled golden-shot fixture.

It is not a claim that Blender Cycles universally achieves perfect quality, nor that it
is externally benchmark-leading.

## Conformance gate

The candidate/method must also pass:

- adapter registered
- handler registered
- normalization passed
- canonical roundtrip passed

This prevents a good-looking render from being promoted if it cannot preserve the
factory's canonical contracts.

For same-scene Blender Cycles, semantic continuity can be proven without a cross-backend
normalizer because the canonical scene/rig/camera/animation remain inside Blender.

Cross-tool methods still require explicit normalization evidence.

## Qualification evidence package

The final lab package references:

- provenance report
- SBOM report
- security report
- hardware report
- sandbox report
- benchmark report
- conformance report

A package passes only if every required lab gate is PASS.

The real Cycles qualification package passed.

Evidence root:

.cflab/reports/

## Acquisition integration

CapabilityAcquisitionWorker now automatically creates a static Execution Lab package
when a research response includes:

- local artifact path
- expected SHA-256

It does not trust arbitrary external JSON files claiming:

{"passed": true}

Candidate-supplied sandbox/benchmark/regression paths are trusted only when they resolve
inside the Execution Lab trusted report root.

A PASS file outside .cflab/reports is ignored.

Verified test:

arbitrary external pass JSON -> NOT TRUSTED.

## Candidate promotion remains fail-closed

Even if:
- license evidence is trusted
- commercial use is allowed
- local hash matches
- static security passes

the candidate still cannot reach production without:

- trusted sandbox PASS
- trusted benchmark PASS
- trusted adapter regression/conformance
- executable method binding

For an unknown tool, the lab returns blockers rather than executing it.

This preserves the v1.6.17 invariant:

APPROVED RESEARCH CANDIDATE
does not imply
EXECUTABLE PRODUCTION METHOD.

## Post-acquisition production continuation

v1.6.18 also closes the episode-level recovery gap.

When an episode contains a shot blocked on capability acquisition, CineFactory stores a
durable EpisodeContinuation record.

Per-shot states:

- PENDING
- ACCEPTED
- WAITING_CAPABILITY
- REQUEUED
- FAILED

The episode does not enter post-production until all required shots are ACCEPTED.

## Continuation lifecycle

BLOCKED SHOT
-> WAITING_CAPABILITY
-> acquisition
-> method becomes executable
-> REQUEUED
-> recovered render SUCCESS
-> ACCEPTED
-> if all shots accepted:
     timeline.accept for each shot
     -> block.episode.assemble

Post-production recovery is idempotent.

Calling acceptance again does not duplicate timeline/assembly work.

## Continuation safety

A non-acquisition failure remains FAILED.

It does not automatically trigger post-production recovery.

A queued or requeued render is not treated as accepted media.

Only a successful render handler result with a path can trigger:

accept_requeued_render(...)

## Real end-to-end continuation verification

Verifier:

scripts/verify_production_continuation_v178.py

Scenario:

1. canonical Minecraft shot exists
2. blender.local is intentionally marked non-executable
3. method switch cannot proceed
4. durable acquisition work is created
5. EpisodeContinuation records the shot as WAITING_CAPABILITY
6. blender.local becomes executable
7. R&D acquisition worker re-evaluates
8. acquisition work succeeds
9. blender.cycles.quality is requeued
10. GPU daemon renders the recovered shot
11. render succeeds
12. daemon informs ProductionContinuationManager
13. shot becomes ACCEPTED
14. timeline work is enqueued
15. assembly work is enqueued
16. IO daemon executes timeline
17. IO daemon executes assembly
18. final recovered episode is written

Observed acquisition:

- state = SUCCESS

Observed recovered render:

- method = blender.cycles.quality
- state = SUCCESS
- bytes = 5,355

Observed timeline:

- state = SUCCESS
- dependency = recovered render work only

Observed assembly:

- state = SUCCESS
- dependency = recovered timeline work

Final episode:

data/verification/v178_production_continuation/
renders/
VERIFY_CONTINUATION_V178.mp4

Final episode bytes:

6,165

This proves recovery is no longer limited to re-rendering a shot. The recovered media
can return to the normal post-production dependency graph.

## Company-level integration

ProfessionalCompanyLayer now exposes:

- capability_acquisition
- capability_execution_lab
- production_continuation

AppContext exposes the same services.

The execution lab object is shared with CapabilityAcquisitionWorker.

## Tests

v1.6.18 targeted Execution Lab + acquisition + method switch:

21 PASS

Execution Lab + Production Continuation + acquisition + method switch:

24 PASS

Cross-version regression:

57 PASS

## Full repository verification

Previous milestone:

v1.6.17:
- 532 PASS

Current milestone:

v1.6.18:
- compileall PASS
- pytest 546 PASS
- failures 0

## Key evidence

Execution Lab:

data/verification/v178_capability_execution_lab/
capability_execution_lab_verification.json

Golden shot:

data/verification/v178_capability_execution_lab/
golden_shot/
S01.cycles.golden.mp4

Production continuation:

data/verification/v178_production_continuation/
production_continuation_verification.json

Recovered shot:

data/verification/v178_production_continuation/
renders/
S01.recovered.cycles.mp4

Recovered final episode:

data/verification/v178_production_continuation/
renders/
VERIFY_CONTINUATION_V178.mp4

Trusted qualification packages:

.cflab/reports/

## What v1.6.18 proves

CineFactory can now:

1. import an already-local candidate into a controlled evidence area
2. verify provenance/hash
3. reject hash mismatch
4. detect ZIP path traversal
5. detect configured critical static execution patterns
6. generate dependency inventory
7. check RTX 3060 VRAM fit
8. refuse to execute unknown code by default
9. execute a registered method through a trusted production handler
10. convert real runtime QC into benchmark dimensions
11. verify adapter/handler/normalization conformance
12. create a durable qualification evidence package
13. prevent arbitrary external PASS JSON from becoming trusted evidence
14. persist blocked-episode continuation state
15. requeue a recovered canonical shot
16. detect successful recovered render
17. restore timeline dependencies
18. restore episode assembly
19. produce a final recovered episode

## What v1.6.18 does not claim

It does not claim:

- static regex scanning is complete malware analysis
- arbitrary GitHub repositories are safe to execute
- unknown binaries can be sandboxed automatically
- SBOM dependency versions are fully resolved without lock data
- external model licenses are automatically legally certified
- every cross-backend adapter is implemented
- every candidate can auto-register itself
- one golden shot proves universal quality leadership

These remain evidence-dependent gates.

## Next milestone

v1.6.19 should build the trusted Candidate Lab Executor and Promotion Controller for
specific safe candidate classes.

Priority:

1. define allowed artifact classes:
   - declarative ComfyUI workflow JSON
   - model files with approved loaders
   - pure-data assets
   - signed/approved adapters

2. create isolated execution profiles:
   - no public network
   - read-only source
   - writable scratch only
   - explicit executable allowlist
   - CPU/RAM/VRAM/time limits
   - process-tree kill
   - output allowlist

3. produce deterministic sandbox evidence

4. run multi-shot benchmark matrices instead of one golden shot

5. perform niche-specific scoring

6. generate qualification attestations from verified lab evidence where policy permits

7. promote already-supported tool/method records only after qualification gates pass

8. keep arbitrary new Python/native code behind explicit security review

That moves CineFactory from:

controlled evidence + registered-method execution

to:

controlled candidate execution + gated automatic promotion.
