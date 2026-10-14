# CineFactory OS - Audit of architecture and integration wiring
Date: 2026-10-10 | Device: DESKTOP-HJE6A6D | Existing HEAD: fec48c6
Canonical checkout: C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6
Scope: READ-ONLY inspection of application source, execution paths, integration contracts, live services, data and tests. No production source, permission or QC policy modified.

## Verdict
PARTIALLY CONNECTED - NOT YET A PROFESSIONAL END-TO-END AUTONOMOUS FILM COMPANY.

The repository/data merger achieved a single primary Git checkout and made real services and preserved research history visible beneath that checkout. A real entrypoint exists: cinefactory/cli.py company-run -> studio/company.py CompanyOrchestrator -> studio/company_handlers.py FilmCompanyHandlers -> studio/company_runner.py AutonomousCompanyRunner -> studio/execution.py ledger/DAG. Those are actual code paths.

But entrypoint reachability, data ownership, and production acceptance are DIFFERENT claims. Several substantial subsystems run independently, produce only planning JSON, or are not activated by the main company runner. The verified product is not yet a fully autonomous profitable YouTube studio.

## Evidence and method
- Existing full regression: 1310 PASS, 3 FAIL (historical v190/v196 Blender worker SHA mismatch). File .tools/cleanup_audit/pytest_after_db_union.log. Not rerun in this audit.
- Fresh integration regression: 69 PASS, 0 FAIL: company_runner, company_handlers, company_cine_bridge, company_block_animation, long_slide_episode, pod_daily_runner, pod_dispatch, canonical_workspace, research_lean_e2e. Log .tools/deep_audit_20261010/integration_tests.log.
- AST graph scanned 318 CineFactory Python production modules, 827 direct static import links. 50 module paths not reached from seven selected roots, including package initializers and manual entrypoints. This is NOT proof of 50 dead modules. Output .tools/deep_audit_20261010/entrypoint_import_graph.json.
- Compiled stage blueprints for generic animation, Minecraft, Roblox, LongSlide, ASMR-as-documentary and Minecraft gameplay; checked declared producer/consumer dependencies and literal handler output writes. Output .tools/deep_audit_20261010/stage_contract_static_audit.json.
- Inspected production source, CLI options, Task Scheduler, latest research reports, historical pilot media evidence, ComfyUI service and old/new filesystem locators.
- This is substantive source coverage and reproducible integration evidence; NOT a claim of human line-by-line semantic review of every file, all runtime variants or the finished movie.

## System wiring map and grading

| Layer | Source | Verdict | Relevant limitation |
| --- | --- | --- | --- |
| Canonical Git/data migration | docs/WORKSPACE_CLEANUP_20261010.md | REAL, PRESERVED | Old evidence paths need compatibility alias |
| CLI company execution | cinefactory/cli.py | CONNECTED TO COMPANY RUNNER | Missing --niche argument in company-run |
| Company orchestration | studio/company.py, company_runner.py, execution.py | REAL DAG, checkpoint, ledger, retry | Does not fail closed on every unbound data input |
| Department registry | studio/contracts.py, departments.py | 26 role names, 15 Default DepartmentSpec | 11 specialist departments lack first-class default spec |
| Niche governance | studio/company.py | PARTIAL | professional_governance=bool(safe_project.niche); CLI default project has niche=None |
| 08:00 public YouTube research | scripts/daily_cinefactory_research_v199.ps1 | SCHEDULED / RUNS | Source-limited RESEARCH_PARTIAL; zero verified winning niche |
| 08:10 Company Youtube P1 | scripts/research_scheduled_runner.ps1 | SCHEDULED / BLOCKED | Exit result 2; official age/catalog proof missing, dependency on separate Company Youtube repo |
| 09:00 P2 approved pod watch | research_intelligence/pod_daily_runner.py | RUNS but NO_PODS | No owner-approved pod nor verified bridge |
| Pod production conference | production/niche_production_conference.py | MODULE PRESENT | NichePod manifest stores an entrypoint STRING and NOT_SCHEDULED, not an executed automatic CompanyStage handoff |
| Script and creative QA | studio/company_handlers.py | PARTIALLY CONNECTED | Basic logic() builds scene list and sets passed=True; specialist review not universal |
| Blender / long slide / animation | block_animation/, animal_long_slide/, studio/block_production.py | PROTOTYPE REAL | No approved professional >=8min output |
| ComfyUI | .tools/ComfyUI | HTTP 200 live on 8188 | Runtime-up does not qualify every model/workflow commercially |
| Editorial/audio/master | studio/company_handlers.py, post/mastering.py | FFmpeg implementation exists | Film-level acting, dialogue, music, rights and independent artistic acceptance unproven |
| Final QC | studio/company_handlers.py:final_qc | TECHNICAL CHECKS REAL | require_audio=False; default human topic/spend/final approvals False |
| Publishing | studio/company.py stages | MISSING | PACKAGING then ANALYTICS_LEARNING; no PUBLISH stage |
| Owned YouTube learning | studio/company_handlers.py:analytics_learning | INCOMPLETE | Writes AWAITING_PLATFORM_METRICS and PENDING_EVIDENCE yet returns ok=True |
| Self-improvement | studio/self_improvement.py | POLICY/PLANNER PRESENT | No verified automatic main company-run invocation; no unattended validated source patch lifecycle |
| Product status/version | pyproject.toml, api/app.py, BUILD_STATUS.md | INCONSISTENT | Versions 1.6.0 vs 1.4.0, legacy build status 66 PASS |

## P0 integration defects reproduced/grounded

1. MAIN CLI DOES NOT SELECT NICHE. The company-run command in cinefactory/cli.py has no --niche option and builds StudioProjectSpec with prompt/language/duration/planning_inputs but no niche. StudioProjectSpec.niche defaults to None, while studio/company.py:~751 turns on professional governance only when safe_project.niche is truthy. A standard CLI prompt therefore bypasses specialist review stages that are present for correctly niche-tagged programmatic projects. Generic baseline governance must always be applied, with explicit/validated niche selection for specialization.

2. STAGE DAG IGNORES UNSATISFIED INPUTS. CompanyStageDAG in studio/execution.py creates edges only if an artifact name already exists in the declared producer dictionary. Reproduced with an artificial PRODUCTION stage requiring NON_EXISTENT_ASSET: dependencies returned the empty set. Stage compiler therefore can call a later stage READY even though a required input has no producer. For stage_blueprint(DOCUMENTARY, governance=True, niche=asmr_sleep_hands_objects), declared inputs of TECHNICAL_DIRECTION include shot_book, asset_manifest, director_cut, performance_plan and previs_report without declared producing stages in that blueprint. This is a STATIC DOCUMENTARY BLUEPRINT test, not a live ASMR episode execution. Separate intrinsic, optional, user-provided inputs from required produced artifacts; fail-fast schema lint before scheduling.

3. DECLARED OUTPUT != VERIFIED OUTPUT. FilmCompanyHandlers generally returns produced_artifacts=list(ctx.stage.artifacts_out); CompanyExecutionEngine.succeed in execution.py compares only these strings, not immutable blackboard receipts, verified file hashes, authentic media stream properties or producer/reviewer signoff. Some handlers perform real blackboard writes, but runner success cannot by itself prove the content exists or was independently accepted. Introduce typed artifact manifest per stage with provenance/expiry/reviewer.

4. RESEARCH TO PRODUCTION HANDOFF NOT AUTOMATICALLY SEALED. Existing Research A and B have different persistence/schedule states, and P1 was BLOCKED during this audit. Niche pod code explicitly says CONFIGURED_NOT_SCHEDULED, production conference is an entrypoint string, and only a tool audit imports its catalog from production/niche_production_conference.py. No verified activation from an actual approved niche to film company runner, cost/rights signoff, original script and production trial. Dynamic use elsewhere is possible; not established from this audit.

5. LEGACY PATH REFERENCES NOT ALL REBASED. Source CineResearch_DailyState folder no longer exists, and data/research_runtime/latest_health.json points to its original absolute path; Test-Path(old health report) was False and Test-Path(new canonical report) True. scheduled_pod_watch.log also contains legacy report paths. Historic reports may legitimately preserve original provenance, but new status indexes must reference current canonical data via a portable resolution layer rather than silently resolving missing files. Old CineFactory_Autonomous_Build compatibility junction to canonical source remains intentional for SHA-bound historic evidence.

6. DECLARED DEPARTMENT PROFESSIONALISM IS UNEVEN. The code has 26 DepartmentId roles but 15 default DepartmentSpecs. This does not mean 11 roles have no handler; it means consistent mission/skills/input/output/QC ownership is incomplete. Script logic stage's passed=True with empty findings is not a meaningful independent causality test. Approvals default to AUTO_APPROVED; 7 niche configs have competitor lists empty.

7. REAL OUTPUT QUALITY HAS NOT PASSED. v197 Minecraft pilot (real 2s 960x540 with audio) was labeled BLOCKED_MINECRAFT_ART_PRODUCTION and publishable=false by its own recorded quality evaluation. No accepted >=8min full-length film observed in audited evidence. ComfyUI 8188 service up; that is different from certified model, media, audio, license and production scene. Studio quality must be measured on approved 30-60s first-party pilot and an 8-10min episode before scale.

8. BUSINESS LOOP OPEN. The CompanyStage graph ends PACKAGING -> ANALYTICS_LEARNING with no verified uploader, post-release owned CTR/retention/RPM observations or versioned validated production learning. The ANALYTICS_LEARNING handler returns success with AWAITING_PLATFORM_METRICS; this needs explicit WAITING_DATA state and must never be claimed as feedback complete.

## Repair order - preserve original strategic intent
P0: one company-wide governance baseline with complete department authorities, explicit niche/format selection, and compile-time producer/consumer contract enforcement. Require true stage receipts, fail-closed artifact checks, reject diagnostic slates as actual production masters.
P0: reconcile 08:00 discovery, 08:10 Company scan and 09:00 P2 under a verified Research Evidence Bus with age/video/legal/freshness provenance, explicit approval, an executable scheduled production handoff and research work orders. No guessed million-view breakout.
P0: bring niche_production_conference into actual authorized production strategy; choose backend by scene and test model/workflow/rights before execution. Protect local zero-metered-API default; paid/cloud requires separate authorization.
P0: create original 30-60s storyboard-locked acting/rig/voice/audio/edited QA benchmark >=1080p24, compare accepted-shot throughput/retake cost; then build one >=8-minute episode with independent editorial/art/audio/rights signoff.
P1: authenticated publish private-first, owner analytics ingestion, learning review only when real performance data mature, safe memory/skill promotion with rollback and tests.
P1: portable evidence locators for historical research paths, fresh worker heartbeat and service monitoring, explicit version/build/qualifications report, close remaining three historic Blender provenance failures using new versioned evidence rather than falsifying signatures.

## Release acceptance
No missing required artifact producers for any supported format or prompt-only path. No stage success purely from output string claims. A user-approved niche can be traced by exact hashes from research to accepted pilot; rights/quality gates genuine. Full-length film independently approved. Publish/analytics/learning authorized and verified. Relevant regression green, no metered API surprise, all changes to canonical checkout.

Final verdict: CODE MODULES AND INFRASTRUCTURE HAVE BEEN CONSOLIDATED, BUT THE COMPANY HAS NOT BEEN INTEGRATED AND QUALIFIED TO THE LEVEL OF A PROFESSIONAL AUTONOMOUS FILM STUDIO. DO NOT TREAT 69/69 OR 1310/1313 TEST RESULTS AS COMMERCIAL FILM ACCEPTANCE.
