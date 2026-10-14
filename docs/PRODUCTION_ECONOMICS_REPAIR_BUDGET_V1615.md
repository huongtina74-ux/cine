# Production Economics + Repair Budget Controller v1.6.15

## Goal

Make CineFactory decide not only whether a failed shot can be repaired, but whether
another local repair is economically justified for that shot's production importance.

v1.6.15 adds a quality-preserving production-economics layer:

HARD QC
-> ROOT CAUSE
-> REPAIR CANDIDATE
-> SHOT CLASS / QUALITY FLOOR
-> GPU BUDGET
-> REPAIR HISTORY
-> PROJECT BUDGET
-> ECONOMIC DECISION
-> REPAIR / SWITCH METHOD / ESCALATE / STOP

A failed take is never accepted merely to save compute.

Economics controls the next production action, not the truth of QC.

## Company-level integration

ProductionEconomicsController is now exposed by ProfessionalCompanyLayer.

FactoryOperationsManager also owns a ProductionEconomicsController and surfaces
production-economics KPIs in FactoryHealthReport.

Company health can now include:
- execution cost
- first-pass yield
- repair success rate
- GPU waste ratio
- GPU seconds per accepted render
- economics flags

This makes repair efficiency visible at the factory-operations level rather than only
inside a shot renderer.

## Production shot classes

v1.6.15 defines five independent production-value classes:

- HERO
- A
- B
- C
- BACKGROUND

This is not the same as visual style.

For example:
- Minecraft is a visual/production style
- HERO is an economic/quality class

A Minecraft episode can contain HERO, A, B, C and BACKGROUND shots.

Shot class can be supplied through:
- episode.metadata.shot_classes[shot_id]
- creative_intent.production_class
- creative_intent.shot_class
- creative_intent.quality_class
- creative_intent.quality_tier

Fallback complexity aliases:
- HERO -> HERO
- RED -> A
- YELLOW -> B
- GREEN -> C

Default when no class is declared:
- B

Aliases:
- BG / EXTRA -> BACKGROUND

## Default professional profiles

### HERO

- base GPU budget: 120 seconds
- additional budget: 60 GPU seconds per output second
- local repair allowance: 4 rounds
- measured quality floor: 0.92
- repair-memory sample floor: 4
- minimum historical strategy success rate: 0.18
- maximum repair waste ratio: 0.92

### A

- base GPU budget: 90 seconds
- additional budget: 45 GPU seconds per output second
- local repair allowance: 3 rounds
- quality floor: 0.88
- repair-memory sample floor: 4
- minimum strategy success rate: 0.22
- maximum repair waste ratio: 0.88

### B

- base GPU budget: 60 seconds
- additional budget: 30 GPU seconds per output second
- local repair allowance: 2 rounds
- quality floor: 0.82
- repair-memory sample floor: 3
- minimum strategy success rate: 0.25
- maximum repair waste ratio: 0.82

### C

- base GPU budget: 40 seconds
- additional budget: 20 GPU seconds per output second
- local repair allowance: 1 round
- quality floor: 0.76
- repair-memory sample floor: 3
- minimum strategy success rate: 0.30
- maximum repair waste ratio: 0.75

### BACKGROUND

- base GPU budget: 25 seconds
- additional budget: 12 GPU seconds per output second
- local repair allowance: 1 round
- quality floor: 0.70
- repair-memory sample floor: 2
- minimum strategy success rate: 0.35
- maximum repair waste ratio: 0.70

Global max_repair_rounds remains a safety ceiling.

Therefore effective local repair allowance is:

min(
  class repair allowance,
  producer global repair ceiling
)

## Per-shot overrides

A shot can override its economic envelope in creative_intent.economics.

Currently supported:
- max_gpu_seconds
- max_local_repairs
- quality_floor

This is useful for a producer-approved exception without changing company-wide policy.

## Project GPU budget

Episode-level override:

episode.metadata.economics.max_project_gpu_seconds

If no explicit project GPU budget exists, the controller derives it from the sum of
shot-class budgets multiplied by a project reserve multiplier.

Current default reserve multiplier:
- 1.15

The project budget is checked before another local repair is enqueued.

## Economic actions

### ACCEPT

Reserved for a valid accepted result.

Economics does not override hard QC.

### REPAIR_LOCAL

Another local repair is economically justified.

Requirements can include:
- repair is locally supported
- repair round is still allowed
- projected next GPU work remains inside shot budget
- projected next GPU work remains inside project budget
- repair strategy is not proven ineffective
- waste has not exceeded the class policy

### SWITCH_METHOD

Local repair is no longer a good production strategy, but the shot is valuable enough
to deserve a different qualified production method.

Typical owner:
- PRODUCTION_METHOD_PLANNER

Typical policy:
- HERO/A -> QUALITY_FIRST_ALTERNATIVE
- B -> BALANCED_ALTERNATIVE

Resulting directive:
- failure_code: MODEL_CAPABILITY
- action: SWITCH_PRODUCTION_METHOD
- invalidates: VIDEO_TAKE, METHOD_SELECTION

CineFactory does not pretend that the alternative method has already been executed.
It issues an explicit upstream method-selection handoff.

### ESCALATE_UPSTREAM

The shot should not continue local repair and requires a production/finance/method
decision upstream.

Possible owners:
- PRODUCTION_SUPERVISOR
- PRODUCER_FINANCE_REVIEW
- PRODUCTION_METHOD_PLANNER

A failed take remains failed.

### STOP_BUDGET

Used for lower-value shots where another local repair is not economically justified.

Result:
- failure_code: COST_POLICY_FAIL
- owner: PRODUCER
- action: STOP_LOCAL_REPAIR_BUDGET
- retryable: false

This does NOT accept the failed shot.

Producer must:
- drop it
- redesign it
- use another method
- or explicitly authorize a new budget

## Decision inputs

For every failed Turbo take, the economics controller can use:

- shot class
- shot duration
- class quality floor
- current repair round
- global repair ceiling
- current lineage GPU seconds
- current lineage wasted GPU seconds
- mean GPU seconds per attempt
- projected next GPU seconds
- total project GPU seconds
- project GPU budget
- repair directives
- local repair support
- repair-memory attempts
- repair-memory success rate
- repair-memory average score
- current measured aggregate quality score

The economic decision is written into TakeRecord.evidence.

## Quality-floor enforcement

A work item can now satisfy hard structural QC yet still fail the approved production
class if its measured aggregate craft score is below the class quality floor.

Finding:

QUALITY_CLASS_FLOOR_MISS:<CLASS>:score=<x>:required=<y>

This routes to:

- failure_code: MODEL_CAPABILITY
- owner: PRODUCTION_METHOD_PLANNER
- action: SWITCH_TO_HIGHER_QUALITY_METHOD
- retryable: false

This is deliberately not treated as an ordinary local rerender.

A HERO shot therefore cannot quietly pass at BACKGROUND-level craft quality.

## Repair-strategy economics

RepairMemory is no longer only used as a ranking hint.

When enough samples exist, economics can reject continued use of a historically weak
strategy.

Decision trigger:

attempts >= class min_strategy_samples
AND
success_rate < class min_strategy_success_rate

High/medium-value shots:
- SWITCH_METHOD

Low-value shots:
- STOP_BUDGET

Small sample counts do not trigger this rule.

This prevents over-learning from one or two repair attempts.

## Repair-waste policy

GPU waste is monitored per shot lineage.

Waste ratio is:

rejected GPU seconds / total lineage GPU seconds

To avoid premature strategy changes, the waste-ratio gate does not act before at least
two repair rounds have been attempted.

After sufficient attempts, excessive waste can trigger:
- SWITCH_METHOD for high/medium-value shots
- STOP_BUDGET for low-value shots

## Turbo execution metrics

TurboStore execution_cost_summary now reports:

- render_samples
- first_pass_samples
- first_pass_accepted
- first_pass_yield
- repair_samples
- repair_successes
- repair_success_rate
- accepted_render_count
- gpu_render_seconds
- gpu_seconds_per_accepted_render

Existing metrics remain:
- total_seconds
- accepted_seconds
- wasted_seconds
- gpu_seconds
- gpu_wasted_seconds
- waste_ratio
- gpu_waste_ratio
- by_state

TurboStore also provides execution_cost_for_work_ids().

This is used to calculate economics for one repair lineage without mixing unrelated
shots.

## First-pass yield

Definition:

accepted initial GPU renders / all initial GPU renders

Repair work is excluded from the denominator.

This makes first-pass yield a useful production-engineering KPI instead of being
inflated by eventual repairs.

## Repair success rate

Definition:

accepted repair renders / all repair renders

This helps answer:

"Are our repair loops actually solving defects, or just burning GPU?"

## GPU seconds per accepted render

Definition:

all GPU render seconds / accepted render count

This gives the factory a direct throughput/economics metric that includes the cost of
failed attempts.

## Company economics flags

Current KPI report can flag:

LOW_FIRST_PASS_YIELD

when:
- enough samples exist
- first-pass yield is below the policy floor

Default:
- minimum 5 samples
- first-pass yield floor 0.55

HIGH_GPU_WASTE

when:
- GPU waste ratio > 0.50

These are operational warnings, not automatic creative overrides.

## Real v1.6.14 stress run under v1.6.15 economics

The existing -3 EV Turbo auto-repair scenario still passed after economics was added.

Observed:

- 3 render samples
- first pass accepted: 0 / 1
- first-pass yield: 0.0
- repair attempts: 2
- repair successes: 1
- repair success rate: 0.5
- selected take: S01_BLENDER_TURBO_03

Measured execution:
- GPU seconds: ~13.078
- GPU wasted seconds: ~9.109
- GPU waste ratio: ~69.65%
- GPU seconds per accepted render: ~13.078

Economics flag:
- HIGH_GPU_WASTE

The default B budget still allowed both local repairs because:
- projected compute stayed within the shot GPU budget
- project budget was not exhausted
- repair round ceiling was not exceeded
- repair history did not have enough samples to prove the strategy ineffective

This proves v1.6.15 did not break the valid v1.6.14 repair loop.

## Real v1.6.15 BACKGROUND budget-stop verification

Verifier:
- scripts/verify_production_economics_v175.py

Injected defect:
- Minecraft shot exposure = -3 EV

Production class:
- BACKGROUND

Forced shot GPU budget:
- 1.0 second

Project budget:
- 1000 seconds
  (intentionally high so the shot budget is the deciding factor)

Observed initial GPU render:
- ~5.047 seconds
- technical pass: true
- visual pass: false
- LOOKDEV underexposure evidence
- Turbo state: QC_REJECTED

Economics:

- GPU spent: ~5.047 s
- projected next GPU attempt: ~5.047 s
- shot GPU budget: 1.0 s
- decision: STOP_BUDGET
- reason: SHOT_GPU_BUDGET_EXHAUSTED
- owner: PRODUCER
- recommended policy: FAST_LEAN_OR_DROP

Final economics directive:
- COST_POLICY_FAIL
- STOP_LOCAL_REPAIR_BUDGET
- retryable: false

Verified:
- only one GPU render work existed
- zero block.render.repair work
- zero timeline.accept work
- zero episode assembly work
- failed take was NOT accepted

## Real v1.6.15 HERO budget-switch verification

Same injected defect:
- exposure = -3 EV

Production class:
- HERO

Forced shot GPU budget:
- 1.0 second

Project budget:
- 1000 seconds

Observed initial GPU render:
- ~5.016 seconds
- technical pass: true
- visual pass: false
- Turbo state: QC_REJECTED

Economics:

- GPU spent: ~5.016 s
- projected next attempt: ~5.016 s
- shot budget: 1.0 s
- decision: SWITCH_METHOD
- reason: SHOT_GPU_BUDGET_EXHAUSTED
- owner: PRODUCTION_METHOD_PLANNER
- recommended method policy: QUALITY_FIRST_ALTERNATIVE

Final economics directive:
- MODEL_CAPABILITY
- SWITCH_PRODUCTION_METHOD
- retryable: false

Verified:
- no blind local repair was enqueued
- no timeline work was enqueued
- no assembly work was enqueued
- failed HERO take was NOT accepted

This is the intended class distinction:

BACKGROUND:
budget exhausted -> stop local repair / producer decision

HERO:
budget exhausted -> preserve shot importance and switch/escalate production method

## Factory Operations visibility

FactoryHealthReport now contains:
- execution_cost
- economics

This lets the always-on company watchdog expose production-efficiency signals alongside:
- GPU health
- stale workers
- dead letters
- blocked work
- SLA breaches
- throughput

## Professional Company Layer

ProfessionalCompanyLayer now exposes:
- economics: ProductionEconomicsController

Economics is therefore part of the professional company architecture rather than an
implementation detail of Blender.

## Verification

Previous milestone:
- v1.6.14: 509 PASS

v1.6.15 targeted final regression:
- 37 PASS

Real Blender/Turbo:
- v1.6.14 three-take repair under economics: PASS
- BACKGROUND budget-stop: PASS
- HERO method-switch: PASS
- failed take leakage to timeline: NONE
- failed take leakage to assembly: NONE
- execution KPI capture: PASS
- factory economics health reporting: PASS

Full repository:
- compileall PASS
- pytest 521 PASS
- failures 0

## Key files

New:
- cinefactory/studio/production_economics.py
- tests/test_production_economics_v175.py
- scripts/verify_production_economics_v175.py
- docs/PRODUCTION_ECONOMICS_REPAIR_BUDGET_V1615.md

Modified:
- cinefactory/turbo/store.py
- cinefactory/studio/block_production.py
- cinefactory/studio/factory_operations.py
- cinefactory/studio/professional_company.py
- cinefactory/production/failure_router.py
- tests/test_factory_operations_v166.py
- tests/test_professional_company_os_v167.py

Evidence:
- data/verification/v175_production_economics/production_economics_verification.json
- data/verification/v175_production_economics/background_budget_stop/
- data/verification/v175_production_economics/hero_budget_switch/

## Remaining high-priority gaps

1. SWITCH_METHOD currently emits a production-method handoff but does not yet execute
   the alternative toolchain automatically.
2. Add Capability Router integration so an economic SWITCH_METHOD can select and enqueue
   a qualified alternate backend automatically.
3. Add per-niche economics profiles because ASMR, Minecraft, Long Slice and Rain/Sleep
   have very different production-cost structures.
4. Add episode-level opportunity-cost scheduling so GPU time is assigned to the highest
   expected value work, not just FIFO/priority.
5. Add revenue/RPM/expected-view inputs carefully as estimates, with evidence labels,
   so business value can influence project budgets without inventing private metrics.
6. Add repair-value-of-information: sometimes a cheap diagnostic preview should run
   before an expensive full-quality repair.
7. Add dynamic budgets learned from actual seconds/accepted-shot distributions by
   niche, shot class, toolchain and hardware.
8. Add budget reservation before launching expensive work so concurrent projects
   cannot each assume the same remaining GPU budget.
9. Add production accounting dashboards and historical trend reports.
10. Add explicit producer authorization workflow for budget overrides.
11. Add automatic downgrade/omit rules only where story/editorial intent explicitly
    permits omission; never silently drop a required story beat.
12. Add benchmark evidence before claiming factory economics is industry-leading.

v1.6.15 proves that CineFactory can now distinguish:

- can repair
- should repair
- should switch method
- should escalate
- should stop local spending

while keeping hard QC authoritative.
