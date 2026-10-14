# CineFactory canonical integration — 2026-10-10

## Source of truth
The authorized working directory is `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6` (one nested checkout within the user-provided folder).
The launcher `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\RUN_CINEFACTORY.ps1` points to the versioned `scripts/workspace_runner.ps1`.
Use `-Mode status` for branch/workspace verification, `-Mode test` to run tests with per-run directories in the **outer project folder** `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\.tools\workspace`, or `-Mode api` to launch the local API. The test temp path must be *outside* the nested Git root to accurately exercise filesystem boundary checks.

## Why Downloads was scattered
Most sibling `cine_*` and `research_*` directories are per-test `pytest --basetemp` outputs, many with hundreds of fixture-generated JSON/CSV/JPG/MP4 files. They are not standalone source repositories.
However `CineFactory_Autonomous_Build/cinefactory-os-v1.6/cinefactory-os-v1.6` is an independent Git checkout containing the studio/company/Long Slide line of work. It must not be deleted as if it were test garbage. `Company Youtube` and `CineResearch_DailyState` are separate data/workflow sources and should retain provenance until their adapters are audited.

## Integration method and recovery
- Canonical starting branch: `visual/v1.6.2-fidelity`, SHA `962a350`, clean tree, 335/335 tests passed before merge.
- Preservation branch: `safeguard/20261010-before-company-merge`.
- Integration branch: `integration/unified-cinefactory-20261010`.
- Alternate committed branch: `studio/v1.6.6-universal-company`, SHA `44e1f5f`.
- Common ancestor `cac8761`; 24 vs 36 divergent commits.
- A three-way Git merge was performed with conflicting hunk preference for the canonical security-gated code (one textual conflict in `autopilot/runner.py` during dry merge).
- Uncommitted alternate source delta was preserved under `.tools/canonical_audit/candidate_modified.patch`; 37 modified files were applied with Git three-way checking. Their prior merged states were archived as `.tools/canonical_audit/merged_pre_candidate_patch.zip`.
- 298 previously untracked `cinefactory/config/docs/scripts/tests/workflows` candidate files were copied with SHA-256 comparisons and collision refusal; manifest is `.tools/canonical_audit/candidate_delta_manifest.json`.
- Candidate `data/verification`, `data/animal_long_slide`, `data/studio`, and `data/research` output/evidence were copied **only when destination files did not exist** (3,195 copied; 153 path collisions left intact). Details in `.tools/canonical_audit/data_migration_report.json`. Candidate `data/assets` (7,966 files, ~463 MiB) also copied with byte-for-byte SHA-256 verification and without any overwrite; see `.tools/canonical_audit/assets_migration_report.json`. Historic test evidence is not independent certification.
- Original alternate checkout remains unmodified. No source/test archive deletion or automatic publishing.

## Honesty and release gates
Integration branch is **NOT production-approved** until the combined suite passes and the authorized renderer/VLM/YouTube evidence gates are proven. Full commercial film production, licensed asset availability, official YouTube source age verification, authenticated owner approval, and artistic review remain separately gated.
Do not silently weaken `VISUAL_QC_MISSING_FAIL_CLOSED`, legal provenance, or commercial release policy to satisfy a legacy diagnostic-slate test. A passing unit test alone does not prove rendered-film quality.
## Verified integration tests and remaining gaps

- Original canonical baseline (before merge): **335 PASS**.
- Consolidated complete suite after importing source + source evidence + real assets (before migrating local PocketSphinx binary): **1,296 PASS, 9 FAIL**; `python -m compileall -q cinefactory scripts` passed.
- Four of these nine failed because the alternate checkout's local PocketSphinx runtime was missing. Copied the local 32-file/37.4-MiB `.tools/pocketsphinx_lib` without network/API calls and confirmed identical SHA-256 for its core Python file. The relevant 21-case acoustic suite then passed **21/21**.
- Long Slide and related assets passed **84/84** targeted tests. Diagnostic studio and autopilot paths were repaired without allowing unreviewed production footage to appear commercially approved.
- Detected dangerous leftover hardcoded absolute path in `scripts/daily_cinefactory_research_v199.ps1` and `scripts/install_daily_cinefactory_task_v199.ps1`: both erroneously targeted `CineFactory_Autonomous_Build`. Both now resolve the canonical checkout via `$PSScriptRoot`. Regression `tests/test_canonical_workspace_integration_v202.py` passed **4/4**.
- The EXISTING Windows Scheduled Task `CineFactory-Daily-YouTube-Research` was independently found still pointing to the alternate old checkout, despite the source script fix. It was updated **in-place** (action executable argument and working directory only) to canonical root, without running the job or altering its 08:00 daily trigger. Verified status `Ready`, next scheduled run 2026-10-11 08:00 local. Prior task XML exported before change to `.tools/canonical_audit/CineFactory-Daily-YouTube-Research-pre-repoint.xml` for exact reversal.
- Final full integration run after PocketSphinx migration, source path fixes and four new static regression gates: **1,304 PASS, 5 FAIL** (1,309 total). Python compileall PASS. Log: `.tools/canonical_audit/pytest_full_final.log`. Failures: (1) historic GitHub research source snapshots fail independent verification (`test_autonomous_source_research_v194`); (2) Wan checkpoint inputs absent and therefore CharacterFactory preview normalization blocks (`test_character_factory_v181`); (3) two rig evidence tests refuse historical Blender worker SHA-256 mismatch after source changed (`test_real_rig_dataset_v190`); (4) shot router refuses to route into unqualified Wan/Comfy video backend (`test_shot_routing_v183`). Do not rewrite historic hashes or bypass missing-model/routing admission to fake a PASS. Treat these 5 as unresolved validation/qualification gates, NOT approved software acceptance.
- Local `.tools/pocketsphinx_lib` is not Git-tracked. Machine-specific model executables and test media remain runtime prerequisites, not a portable install certificate.

**Not completed:** end-to-end autonomous cinematic episode, rights-authenticated publishing, independently qualified Blender/Wan/Comfy/Unreal production workers, real official YouTube verification, stale source evidence regeneration and signed approval.



## Working policy
1. Any future code change must start by identifying this absolute checkout and its active branch.
2. Shared source changes are integrated into the tracked `cinefactory/`, `config/`, `scripts/`, `tests/`, `docs/` modules, not left as separate Downloads source clones.
3. Persistent original project data belongs in the nested checkout `data/` with provenance; temporary test fixtures belong in the **outer parent** `.tools/workspace/`, to ensure `tmp_path` stays outside the checked project root. Retain run identifiers and preserve existing inputs.
4. External models or datasets are capability candidates until execution, licensing, resource budgets and independent QC are verified.
5. Never archive/delete sibling folders before classification and a verified provenance/backup manifest.
