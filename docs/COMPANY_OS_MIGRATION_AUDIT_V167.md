# CineFactory Professional Company OS — Migration Audit v1.6.7

## Baseline

Repository:
`C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6`

Branch:
`studio/v1.6.6-universal-company`

Verified before Company OS changes:
- Python compileall: PASS
- pytest with repo-local basetemp: 434 passed
- repository already contains a strong production/studio architecture
- existing uncommitted Animal Long Slide work is preserved and was not reset or overwritten

## KEEP

These existing systems are already aligned with the professional-company architecture and should remain authoritative:

- StudioKernel
- CompanyOrchestrator / CompanyStage blueprint
- Company control gates, spend gate, cost ledger, scale gate, technical debt
- StudioBlackboard and immutable artifacts
- StudioProjectSpec / MediaProductSpec / ProjectDNA
- DepartmentRegistry and permanent craft departments
- ProjectPod temporary delivery teams
- Production Conference and Scene Production Conference
- Production Qualification / adapter attestation
- Reference Intelligence / competitor video decomposition
- PatternMiner / NichePlaybook
- PlanningDepartment and scene tool planning
- Production Memory
- R&D intake, Knowledge Acquisition, Skills and Self Improvement
- QC Department and repair routing
- Core continuity/dependency/state systems
- Turbo durable queue, GPU/CPU/IO lanes, repair memory
- Block Animation Factory
- Animal Long Slide vertical
- Audio, Editorial, Color and Post departments
- zero-metered-production-API policy

## EXTEND

The following existing systems should be extended rather than replaced:

### StudioKernel
Add a ProfessionalCompanyLayer containing:
- corporate company functions
- niche registry
- niche SEO brains
- authority/RACI matrix
- structured handoffs
- dailies review governance
- creative-intent hierarchy
- maturity audit

### Intelligence
Keep existing competitor video abstraction and pattern mining.
Extend with:
- YouTube search-intent graph
- query/SERP snapshots
- new-channel breakout detection
- SEO content gaps
- post-publish search feedback

### Departments
Keep existing film/media craft departments.
Add company-level functions outside the per-shot craft hierarchy:
- Executive Strategy
- Finance & Investment
- Business Affairs / Legal
- People / Talent / Training
- Marketing / Publicity
- Procurement / Vendors
- Risk / Internal Audit
- YouTube Growth & SEO
- Data & Analytics
- Technology / Platform
- Knowledge / R&D

### Project / production governance
Keep existing production sheet, GateEngine, human gates and StudioTrace.
Extend with:
- explicit decision authority
- machine-readable department handoffs
- dailies note acceptance criteria
- creative-intent inheritance
- maturity evidence

## DO NOT DUPLICATE

The external Company OS prototypes previously built outside the repository contain concepts that overlap existing code. Do not copy these implementations into the repository:
- duplicate dependency graph
- duplicate event bus
- duplicate generic project brain
- duplicate generic scheduler
- duplicate capability registry
- duplicate generic QC engine
- duplicate learning registry

Use the existing CineFactory implementations and extend them.

## New v1.6.7 professional-company components

- `cinefactory/studio/corporate.py`
- `cinefactory/studio/niche_os.py`
- `cinefactory/studio/seo.py`
- `cinefactory/studio/authority.py`
- `cinefactory/studio/handoffs.py`
- `cinefactory/studio/review_board.py`
- `cinefactory/studio/hierarchy.py`
- `cinefactory/studio/maturity.py`
- `cinefactory/studio/professional_company.py`
- `config/niches/<niche>/...`
- `scripts/bootstrap_professional_niches.py`

## Seven active niche operating systems

1. Minecraft
2. Long Slices Game
3. ASMR Sleep — Hands + Objects
4. Audio Storytelling for Seniors
5. Fishing Silent
6. Rain / Sleep / White Noise
7. Roblox Animation

Each niche owns its own:
- audience intelligence
- competitors
- SEO/search-intent data
- format DNA
- production recipes/toolchains
- packaging/retention
- risk/monetization
- analytics and validated rules

Shared company and filmmaking principles remain outside niche folders.

## Safety decision

No existing Animal Long Slide modified/untracked file was overwritten by this migration batch.
No destructive git command was used.
