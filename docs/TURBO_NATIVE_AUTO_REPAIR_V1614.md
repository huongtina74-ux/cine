# Turbo-Native Auto Repair v1.6.14

## Goal

Move the bounded auto-repair loop from the direct producer path into the durable
Turbo control plane so a rejected render can be repaired, re-enqueued, measured,
audited, costed, and consumed by downstream post-production without retrying the
same deterministic bad contract.

The durable Turbo loop is now:

WORK QUEUED
-> GPU CLAIM
-> BLENDER RENDER
-> STRUCTURAL + PIXEL QC
-> SUCCESS or QC_REJECTED
-> ROOT-CAUSE ROUTING
-> LOCAL REPAIR PLAN
-> NEW REPAIR WORK ITEM
-> GPU RERENDER
-> RE-QC
-> ACCEPTED WORK ONLY
-> TIMELINE
-> EPISODE ASSEMBLY

## Deterministic QC failure is not an ordinary retry

A successful media render that fails deterministic quality gates is represented as:

WorkState.QC_REJECTED

not:
- SUCCESS
- RETRY
- generic DEAD_LETTER

The rejected work preserves:
- rendered path
- render evidence
- pixel QC
- geometry QC
- render state
- failure findings

The original work item is never retried unchanged.

Instead, the repair planner creates a new work item:

kind = block.render.repair

with:
- repair_round
- repair_of_work_id
- serialized RepairDirective records
- repaired BlenderAnimationJob contract

Each render work item uses max_attempts=1 for deterministic QC rejection.

This prevents wasting GPU time retrying an identical bad contract.

## Durable QC_REJECTED state

TurboStore now supports QC_REJECTED as a terminal execution state.

reject_work() stores:
- QC_REJECTED state
- finished timestamp
- error
- full result_json

Dependency propagation treats QC_REJECTED as terminal failure.

If an old downstream item depended on a rejected work item, it becomes BLOCKED.

The replacement repair work is a new lineage entry.

## Post-production depends only on the accepted repaired work

Timeline and episode assembly are not enqueued until the shot has an accepted take.

For a repaired shot:

original render -> QC_REJECTED
repair 1        -> QC_REJECTED
repair 2        -> SUCCESS
                         |
                         v
                 timeline.accept
                         |
                         v
                 episode assembly

The timeline dependency is the final SUCCESS work ID, not the original rejected work.

This prevents a stale or rejected take from leaking into editorial.

## Repair lineage

Each replacement render records:

repair_round
repair_of_work_id
repair_directives

Example verified lineage:

round 0:
- kind: block.render
- state: QC_REJECTED

round 1:
- kind: block.render.repair
- repair_of_work_id: round-0 work
- state: QC_REJECTED

round 2:
- kind: block.render.repair
- repair_of_work_id: round-1 work
- state: SUCCESS

This lineage is durable in SQLite.

## Repair memory

TurboStore repair_memory is both written and consumed.

Recorded dimensions:
- failure_code
- workflow_id
- shot_class
- strategy
- prompt_directive
- attempts
- successes
- average score

When planning the next repair, BlockAnimationProducer queries the best historical repair
for the current:
- failure code
- block_animation workflow
- visual style / shot class

The result is passed to LocalBlockRepairPlanner as preferred_strategies.

The planner keeps the same safety boundaries:
- a memory hint can prioritize a known strategy
- it cannot make an unsupported failure locally repairable
- it cannot bypass retryable/non-retryable policy
- it cannot rewrite story, canonical identity, or complex continuity state

Repair plans expose memory_hints for audit.

## Execution cost accounting

Turbo now records ExecutionCostSample for each executed work item.

Per sample:
- work_id
- project_id
- worker_id
- kind
- resource
- final state
- duration_seconds
- output_units
- accepted flag
- repair_round

This separates:
- accepted compute
- rejected/wasted compute
- GPU compute
- GPU wasted compute

DailiesReport now exposes execution_metrics.

Key aggregate fields:
- total_seconds
- accepted_seconds
- wasted_seconds
- gpu_seconds
- gpu_wasted_seconds
- waste_ratio
- gpu_waste_ratio
- by_state

QC_REJECTED GPU work is counted as wasted compute.

This enables production decisions based on quality AND GPU efficiency.

## Real isolated Turbo + Blender verification

Verifier:
scripts/verify_turbo_auto_repair_v174.py

The verifier now uses its own isolated SQLite TurboStore:

data/verification/v174_turbo_auto_repair/turbo_verification.db

This prevents previous verification runs from polluting:
- work counts
- repair-memory counts
- execution-cost metrics

Injected defect:
- Minecraft shot exposure forced to -3.0 EV

Expected bounded repair path:
- -3.0 EV -> -1.5 EV
- -1.5 EV -> 0.0 EV
- maximum local repair rounds = 2

Observed:

TAKE 1
- take: S01_BLENDER_TURBO_01
- repair_round: 0
- technical_pass: true
- visual_pass: false
- failure: LOOKDEV_FAIL
- Turbo state: QC_REJECTED
- repair: exposure -3.0 -> -1.5

TAKE 2
- take: S01_BLENDER_TURBO_02
- repair_round: 1
- technical_pass: true
- visual_pass: false
- failure: LOOKDEV_FAIL
- Turbo state: QC_REJECTED
- repair: exposure -1.5 -> 0.0
- repair memory hint consumed

TAKE 3
- take: S01_BLENDER_TURBO_03
- repair_round: 2
- technical_pass: true
- visual_pass: true
- Turbo state: SUCCESS
- selected take

Final selected file:
data/verification/v174_turbo_auto_repair/renders/block_animation/shots/0000_S01.turbo_repair02.mp4

Episode assembly:
- SUCCESS

No remaining RepairDirective:
- PASS

## Verified dependency chain

The isolated run produced exactly:

GPU render work 1:
- QC_REJECTED

GPU repair work 2:
- QC_REJECTED
- repair_of = work 1

GPU repair work 3:
- SUCCESS
- repair_of = work 2

timeline.accept:
- SUCCESS
- dependency = GPU repair work 3 only

block.episode.assemble:
- SUCCESS
- dependency = timeline.accept only

This proves post-production consumes the selected repaired take rather than the original
rejected work.

## Real repair-memory result

Because the isolated run made two repair attempts for the same LOOKDEV strategy:

failure_code:
- LOOKDEV_FAIL

strategy:
- REBALANCE_LIGHTING_AND_COLOR

observed memory:
- attempts: 2
- successes: 1
- success_rate: 0.5
- average_score: 1.0

The second repair plan consumed the memory hint from the first recorded attempt.

The 0.5 rate is expected for this stress test:
- first +1.5 EV repair remained underexposed
- second +1.5 EV repair passed

It is evidence, not a hand-authored success claim.

## Real execution-cost result

Stress-test execution metrics:

total execution seconds:
- ~14.127 s

accepted seconds:
- ~4.314 s

wasted seconds:
- ~9.813 s

GPU seconds:
- ~14.016 s

GPU rejected/wasted seconds:
- ~9.813 s

overall waste ratio:
- ~69.46%

GPU waste ratio:
- ~70.01%

GPU state breakdown:

QC_REJECTED:
- samples: 2
- seconds: ~9.813
- output units: 48
- accepted seconds: 0
- wasted seconds: ~9.813

SUCCESS:
- samples: 1
- seconds: ~4.203
- output units: 24
- accepted seconds: ~4.203
- wasted seconds: 0

IO SUCCESS:
- samples: 2
- seconds: ~0.111

These high waste ratios are intentionally caused by the injected -3 EV stress failure.
They are not claimed as representative production efficiency.

The purpose is to prove CineFactory can now SEE the cost of failed repair loops.

## Repair-budget principle

Turbo now has two separate retry concepts:

### Infrastructure retry

Used for transient execution failures where the same work may reasonably succeed later.

### Creative/QC repair round

Used when the rendered output deterministically violates quality evidence.

For QC failures:
- do not retry identical work
- modify only the allowed execution contract
- enqueue a new repair work item
- respect max_repair_rounds

This separation protects GPU throughput.

## Failure safety

Turbo-native auto repair still refuses unsafe or high-level automatic rewrites.

Local supported categories remain:
- LOOKDEV_FAIL
- CAMERA_INTENT_FAIL
- PERFORMANCE_FAIL
- ACTION_FAIL
- TECHNICAL_FAIL

Not automatically repaired locally:
- RIGHTS_FAIL
- SECURITY_FAIL
- canonical identity drift
- complex continuity failures
- Director/Story failures
- unsupported/non-retryable directives

These remain visible as final Dailies repair directives.

## Event evidence

FactoryDaemon publishes distinct events:

WORK_SUCCEEDED
WORK_QC_REJECTED
WORK_FAILED

QC rejection events include:
- kind
- state
- findings
- elapsed_seconds
- repair_round

This makes an always-on factory observable instead of silently rerendering.

## Verification

Previous milestone:
- v1.6.13: 504 PASS

v1.6.14 targeted Turbo + repair regression:
- 26 PASS

Real Turbo + Blender isolated stress verification:
- QC_REJECTED state preservation: PASS
- repair work re-enqueue: PASS
- repair lineage: PASS
- repair-memory write: PASS
- repair-memory consumption: PASS
- selected-take dependency routing: PASS
- timeline: PASS
- episode assembly: PASS
- GPU cost accounting: PASS
- GPU waste accounting: PASS
- bounded repair budget: PASS

Full repository:
- compileall PASS
- pytest 509 PASS
- failures 0

## Key v1.6.14 files

Core:
- cinefactory/turbo/contracts.py
- cinefactory/turbo/store.py
- cinefactory/turbo/daemon.py
- cinefactory/block_animation/runtime.py
- cinefactory/block_animation/repair.py
- cinefactory/studio/block_production.py
- cinefactory/production/contracts.py

Tests:
- tests/test_turbo_auto_repair_v174.py
- tests/test_turbo_daemon.py
- tests/test_turbo_store.py
- tests/test_turbo_dependency_blocking.py

Real verifier:
- scripts/verify_turbo_auto_repair_v174.py

Evidence:
- data/verification/v174_turbo_auto_repair/turbo_auto_repair_verification.json
- data/verification/v174_turbo_auto_repair/turbo_verification.db

## Remaining high-priority work

1. Add project/episode repair budgets based on GPU seconds, not only round count.
2. Add automatic stop/escalation when a repair strategy repeatedly fails or exceeds cost budget.
3. Add repair-strategy ranking using enough evidence to avoid overlearning from tiny samples.
4. Add selective dependency invalidation for already-approved downstream artifacts when a previously accepted shot is later replaced.
5. Add distributed/multi-GPU scheduling policies and VRAM-aware repair placement.
6. Add audio QC and audio repair into the same durable control-plane model.
7. Add production dashboards for:
   - first-pass yield
   - repair success rate
   - GPU waste ratio
   - seconds per accepted shot
   - failures by owner/root cause
   - repair rounds by niche
8. Add policy that can trade quality target vs GPU budget per shot class (HERO/A/B/C/BACKGROUND).
9. Benchmark repair efficiency on representative full episodes, not only synthetic one-shot stress cases.
10. Preserve the distinction between:
   - infrastructure retry
   - deterministic QC rejection
   - bounded creative repair
   - upstream redesign

v1.6.14 proves the durable Turbo repair loop is executable.
It does not yet prove optimal factory economics or benchmark-leading visual quality.
