# CineFactory OS v204 - Canonical Company Architecture & Phase-1 Wiring Repair
Date: 2026-10-10. Canonical source: `C:\\Users\\ADMIN\\Downloads\\cinefactory-os-v1.6\\cinefactory-os-v1.6`.

**State: PHASE 1 IMPLEMENTED; COMMERCIAL FILM PRODUCTION NOT YET QUALIFIED.**
Do not treat file migration, tests, agent names or working ComfyUI as proof of cinematic output. Never copy or delete historical evidence without an explicit inventory, hash, backup and reversible plan.

## Professional organizational contracts

```text
Company Owner / Corporate Governance
  |-- Business portfolio, finance, copyright, security
  |-- Research Branch 1 (all-market discovery, verified evidence)       [SOURCE LIMITED]
  |-- Research Branch 2 (approved niche deep study, source-linked)      [NO APPROVED POD]
  |-- Creative development & planning
  |     |-- Project DNA -> narrative/format bible -> Script Room -> Logic/Creative review
  |     |-- Storyboard/Director -> camera/acting/sound intent
  |-- Production Director / Technical Conference
  |     |-- Scene routing -> model + workflow + license + VRAM qualification
  |     |-- Asset rigs + animation / Animal Long Slide / gameplay / ComfyUI
  |-- Quality and Postproduction
  |     |-- Dailies -> Editor -> Sound -> Color/Finishing
  |     |-- technical QC, independent art/rights, human final acceptance
  |-- Publishing -> Owned Analytics -> Learning governance               [NOT IMPLEMENTED END TO END]
  |-- Platform, worker operations, fault recovery, versioning and audits
```

No department is promoted to READY merely because it has a module. A department requires: binding in company-run, declared input/output contracts, validated artifacts, source/tool readiness, rights and an executed test; a live media department also requires independently inspected film samples.

## Canonical paths and source-of-truth policy

- Main CLI, Orchestrator, Company Runner and ledger: `cinefactory/cli.py`, `cinefactory/studio/company.py`, `cinefactory/studio/company_runner.py`, `cinefactory/studio/execution.py`.
- Wiring compiler: `cinefactory/studio/contract_integrity.py` (producer/consumer contract audit).
- Stage artifact verifier: `cinefactory/studio/artifact_receipts.py` (owned blackboard receipt, validated state, content hash).
- Niche organization & configs: `cinefactory/studio/niche_os.py`, `config/niches/<niche>/`. One baseline governance and specialized production policy per niche.
- Separate Company Youtube data provider remains at its existing authorized directory. Its outputs are EVIDENCE, not automatic permission to produce.
- Research execution and state: `cinefactory/research_intelligence/`, `data/research_runtime/`; run mode from canonical `scripts/research_scheduled_runner.ps1`.
- Company public YouTube scanner remains separate executable at `scripts/daily_cinefactory_research_v199.ps1`, with its own source scope. Neither scanner certifies winning niche automatically.
- Active media tools: `.tools/ComfyUI`, `.tools/blender-4.5.14-windows-x64` (only if executable is proven), `cinefactory/executors/`.
- Canonical production artifacts `data/projects/<project_id>/`; immutable research and film evidence under `data/research/` and `data/verification/`. Structured logs and temporary tests under `.tools/`, not loose Downloads folders.
- Historic Git clone removed; remaining old-path junction only supports immutable evidence. `Company Youtube` is intentionally preserved as an independent data producer.

## Wiring improvements implemented

1. `company-plan` and `company-run` now accept explicit `--niche` and `--domain`, persist them in `StudioProjectSpec`. Both CLI entrances request professional governance. Existing persisted blueprints and direct library callers retain legacy planning mode to avoid silently rewriting old runs.
2. `INTELLIGENCE` now declares its existing `research_portfolio` output; downstream PLANNING no longer consumes a declared orphan.
3. `audit_company_wiring` distinguishes authorized project inputs from outputs that must be supplied by another stage. Missing, duplicate and self-produced dependencies are reported as exact blockers. `AutonomousCompanyRunner` refuses invalid strict blueprints; CLI emits `BLOCKED_STAGE_CONTRACT` with missing names.
4. Professional stage success now requires real blackboard artifacts owned by the declared department, validated/locked metadata and matching SHA-256 of the stored payload. Legacy diagnostic ledgers retain explicit non-strict replay semantics, not film certification.
5. Explicit niche research-only greenlight does not grant production permission. Strict production handler returns `NICHE_PRODUCTION_GREENLIGHT_REQUIRED` before assets/renders. Corporate blueprint shows `NICHE_PRODUCTION_NOT_GREENLIT` and related readiness blockers.
6. Strict company CLI final approval is required. Strict ANALYTICS_LEARNING stage fails with `AWAITING_VERIFIED_PLATFORM_METRICS`, preventing the historical placeholder from posing as completed feedback.
7. `scripts/repair_research_locators.py` rebases the CURRENT mutable research health pointer to canonical state, preserving source JSON and old reference in a backup; future research reports include a relative locator. `daily_health` validates the relative locator when present.
8. `scripts/company_architecture_doctor_v204.py` regenerates a read-only per-niche, per-department status ledger. It intentionally reports missing production readiness rather than incrementing a claimed READY counter.

## Reproducible operator commands

Run from canonical repo PowerShell:

```powershell
python -m cinefactory.cli company-plan --prompt "Original Minecraft animation" --niche minecraft --duration 60
python -m cinefactory.cli company-plan --prompt "ASMR hand-object sleep film" --niche asmr_sleep_hands_objects --duration 600
python scripts/company_architecture_doctor_v204.py --output ".tools/operations/last_company_doctor.json"
python scripts/repair_research_locators.py --state-root "data/research_runtime"
python -m pytest tests/test_professional_company_wiring_v204.py -q -p no:cacheprovider
```

`company-run` can be used only when source-bound producer contracts and approvals allow the next step. Do not use a diagnostic slate as a publishable film. Do not force or fake a production greenlight.

## Explicit unfinished phases

**P0 remaining:** Integrate Research 08:00 + P1 08:10 + P2 09:00 in a single evidence registry without changing their provenance; create an authenticated owner-approved pod-to-company work order; add true procedural/real-capture stage families for ASMR, Audio Stories, Fishing and Rain (current documentary/podcast blueprints report unbound inputs); complete all 11 missing default department specs with real executors/evals; unify model+workflow qualification and film QC. Run one owner-approved original 30-60s movie benchmark with image/audio/identity/rig and independent reviewer.

**P1 remaining:** Original independently accepted >=8min film, sustained zero-paid-API worker tests, authenticated private-first YouTube publishing, owned Analytics ingestion, validated learning promotion, correction of 3 historical Blender provenance SHA tests using new versioned evidence rather than rewriting source hashes. Reconcile remaining legacy absolute references and unify versions `pyproject.toml`, API and BUILD_STATUS.

**Do not declare the company completed** until a real project travels from verified research evidence to approved long-form film and owner-authorized publication, with accepted-second throughput and human art/rights signoff. This patch primarily fixes the **operational wiring**, not the entire business ambition.

## Actual engineering acceptance, 2026-10-10

- Full regression started after initial new professional wiring: **1,319 passed, 3 failed**, runtime ~185s. The 3 residual failures remain Blender v190/v196 historic worker SHA comparisons (same known baseline class). Log: `.tools/deep_audit_20261010/full_suite_v204.log`.
- Subsequent focused post-gate run after final QC/greenlight additions: **30 passed**, includes owner production gate and strict slate anti-publication, 2 research locator tests, daily Research and prior diagnostic company tests. Log: `.tools/deep_audit_20261010/v204_final_gates.log`. Full suite has not been repeated *after* those final very small checks, so do not assert every possible scenario is green.
- `python -m compileall -q cinefactory scripts` PASS.
- Operational doctor snapshot generated at `.tools/deep_audit_20261010/company_operating_status_v204.json`. 26 declared roles / 15 fully specified default departments; evaluated 7 representative niche production formats: Minecraft, Roblox and Long Slide are stage-wired but research/production-readiness-pending; ASMR, Audio Storytelling, Fishing, Rain are stage-wiring-blocked in the documentary/podcast variant.
- Research index repaired with immutable original state index copy: `.tools/cleanup_audit/research_locator_backups/`. Current report is canonical; daily-health correctly returns `ALERT_INCOMPLETE` for a source data coverage problem, not `HEALTHY`.

**Release verdict:** `FOUNDATION_WIRING_IMPROVED_NOT_PRODUCTION_ACCEPTED`. Do not auto-publish, auto-use paid APIs, edit signed historical evidence or mark unfinished department capabilities READY.
