# Project Intake & Professional Greenlight v1.6.8

## Purpose

Move Professional Company OS from a registry into the real CompanyOrchestrator execution graph.

## New execution order

PROJECT_INTAKE
-> PORTFOLIO_GREENLIGHT
-> INTELLIGENCE
-> CORPORATE_PREFLIGHT
-> CREATIVE_STRATEGY
-> PLANNING
-> WRITING / LOGIC
-> DIRECTION / PERFORMANCE / DESIGN / CINEMATOGRAPHY
-> TECHNICAL DIRECTION
-> PRODUCTION
-> POST
-> FINAL QC
-> PACKAGING
-> ANALYTICS / LEARNING

## Project Intake

Resolves:
- platform
- requested niche
- recognized CineFactory niche
- inferred niche
- explicit vs inferred niche
- strict niche gate policy

Explicit niche requests are strict.
Inferred niches remain advisory for backward compatibility until the caller explicitly selects the niche.

## Portfolio Greenlight

Unknown explicit niches fail closed.

Known explicit niches may enter Research while incomplete, but are not production-greenlit until all baseline domains exist:

- niche research
- competitor baseline
- SEO/search-discovery baseline
- production recipe/toolchain baseline
- packaging/retention baseline
- niche risk + monetization baseline

This separates:
- permission to research
- permission to spend/produce

## Corporate Preflight

Runs after Intelligence and before Creative Strategy.

Checks:
- competitor research readiness
- SEO/search-discovery readiness
- niche risk/monetization readiness
- company finance policy readiness
- rights/policy planning readiness

Final asset/tool licensing still remains downstream fail-closed; preflight does not falsely claim final rights clearance.

## SEO evidence policy

Competitor private metrics are never treated as public facts.

Allowed evidence labels:
- PUBLIC_FACT
- ESTIMATE
- INFERENCE
- UNKNOWN

## Backward compatibility

Generic projects continue using shared company/filmmaking rules and are not forced into an incomplete niche.

Projects whose niche is inferred from prompt/domain receive advisory niche context.
Projects that explicitly set one of the seven registered niches receive strict niche gating.

## Validation

- explicit unknown niche -> HOLD
- registered niche with empty baselines -> PROCEED_RESEARCH only
- registered niche with all baselines -> GREENLIGHT
- inferred niche -> advisory mode
- runner with explicit incomplete niche reaches Intelligence then stops at CORPORATE_PREFLIGHT
- Creative Strategy cannot execute after failed Corporate Preflight

## Final verification

- compileall: PASS
- focused regression after compatibility repair: 23 PASS
- explicit niche fail-closed execution test: PASS
- full repository suite: 451 PASS
- previous clean baseline: 434 PASS
- net new tests: 17
- regression failures remaining: 0

Compatibility policy:
- ProjectIntake metadata is computed for every blueprint.
- Mandatory PROJECT_INTAKE / PORTFOLIO_GREENLIGHT / CORPORATE_PREFLIGHT execution stages are enabled for explicitly selected niches.
- Generic and inferred-niche legacy projects preserve the historical stage graph while receiving advisory professional-company context.
