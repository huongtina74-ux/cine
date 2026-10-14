# CineFactory canonical workspace consolidation — 2026-10-10

## Canonical location and invariant

Git source of truth: `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`.
Outer project folder is `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6`.
Do not create new development repositories under Downloads. Production and research runtime data belong under canonical `data/`. Temporary test fixtures, audit logs and recovery archives belong in `<outer>\.tools/` and are excluded from Git.

## Completed verified removals

- Exactly **114** loose `cine_*`, `research_*`, `bridge_test_*` pytest temporary trees were inventoried and classified, totaling **34,408 files / 240,530,755 bytes**. No independent Git checkout, symlink or non-pytest top-level child was present in these 114 trees.
- Created `<outer>\.tools\cleanup_archive\pytest_fixtures_20261010.zip` (**135,795,634 bytes**), with per-file SHA-256 manifest `pytest_archive_manifest.json`; verified archive ZIP CRC, source and archive SHA-256 for every file before removal. A deletion receipt lists each of 114 directories. **All 114 deleted successfully**.
- `CineResearch_DailyState` (497 original files, 6.86 MiB) was moved into canonical `data\research_runtime` by verified copy and **deletion of old external folder** after matching SHA-256 with both source and backup ZIP. Source deletion receipt: `.tools\cleanup_audit\state_retirement_receipt.json`. No observed loss of research state.
- Existing Windows scheduled tasks `CineFactory_Research_Daily_P1`, `CineFactory_Research_Health_P1`, `CineFactory_NichePod_Watch_P2` were repointed to canonical `scripts\research_scheduled_runner.ps1` without changing recurrence. Prior task XML backups are in `.tools\cleanup_audit\task_backups`. The existing 08:00 `CineFactory-Daily-YouTube-Research` was already repointed to canonical in the prior integration.
- Legacy project/data reconciliation imported **10,085 missing files**, found **1,216 identical**, and protected **two different SQLite DB files** under `.tools\legacy_conflicts_20261010\data` without overwriting canonical DBs. Detailed report: `.tools\cleanup_audit\legacy_data_reconciliation.json`. **SQLite data records remain pending explicit logical merge and conflict audit.**

## ComfyUI service cutover

- Previously the old `CineFactory_Autonomous_Build` checkout was running a local ComfyUI service on TCP 8188. The canonical checkout initially had no executable ComfyUI.
- Copied its ComfyUI install and local virtual environment to canonical `.tools\ComfyUI` (~17.56 GiB); retained its previous input upload.
- Confirmed PyTorch CUDA availability; verified exact SHA-256 equality for **43 ComfyUI model files / 14,383,850,938 bytes**, report `.tools\cleanup_audit\comfy_model_hashes.json`.
- Independent startup smoke on port 8189 with CPU passed HTTP 200. Then, after confirming old port 8188 queues were empty, cut service over to canonical python and confirmed HTTP 200 from **PID 17196**, with rollback procedure prepared.
- Patched `scripts/start_comfyui.ps1` so a healthy-but-stale ComfyUI from a different checkout cannot silently impersonate canonical runtime.
- No claim that all Wan models/workflows passed premium full-film QC; local health alone does not qualify commercial output.

## Source reconciliation and retention boundaries

- The old `CineFactory_Autonomous_Build` is a **second independent Git checkout**, not a pytest fixture. It must not be removed until exact file and path dependency audit and the canonical suite run without this old absolute location. Its committed history has been merged into canonical Git (merge commit `8b6a701`) and a standalone `.bundle` passed git bundle verify.
- Candidate models, GPU software, generated run files and scripts must be compared by hash. Conflicting code, prior events and old databases go to quarantine, not silently replaced in canonical.
- `Company Youtube` is a separate active data source/repository. It is intentionally left intact with canonical research adapters using its explicit source path; it is not part of the pytest-directory cleanup.
- The full CineFactory suite previously had **1,304 PASS, 5 FAIL** and is **not production accepted**; the five failing gates require source provenance or real backend qualification. Static workspace regressions were independently **8/8 PASS**.
- **Do not call the migration finished if the original second Git checkout or any task still depends on the old path.** Final source cutoff and test results should be appended when independently confirmed.

## Final physical source retirement and test evidence

- Full regression **without any legacy path compatibility**: **1,266 PASS, 32 FAIL, 15 ERROR**, demonstrating historical artifacts/fixtures contain absolute paths to the old Git checkout. Log: `.tools/cleanup_audit/pytest_without_legacy_root.log`. That is an unacceptable regression and was not deployed.
- Created a **Windows junction compatibility alias** from `C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6` to the canonical Git checkout. This is a filesystem pointer, NOT a copied repository. It exists solely for immutable historical evidence with old absolute paths; marked its tiny container Hidden/System so Explorer's ordinary Downloads view stays clean. Do not delete this alias until legacy evidence references have been migrated and tested without it.
- With that pointer to the **canonical** checkout, targeted affected files passed **229 PASS / 3 FAIL** (three historical Blender SHA mismatch failures). Final complete test suite: **1,310 PASS / 3 FAIL**; no new failures caused by removing the old physical checkout. Log: `.tools/cleanup_audit/pytest_alias_full.log`. The three unresolved tests relate to v190/v196 Blender worker source lineage; do not overwrite historical source hashes.
- Complete old checkout file audit before removal: **28,601 identical**, **420 missing files imported**, **324 source conflicts archived**, **1,989 external reference-repository files preserved**; see `.tools/cleanup_audit/legacy_filediff_reconciled.json`. Code conflicts in quarantine are source-preserving, not canonical runtime overrides.
- Git history for both the old CineFactory checkout and the old ComfyUI clone was preserved as verified independent bundles under `<outer>\.tools\cleanup_archive`.
- **The old physical `CineFactory_Autonomous_Build` clone was removed successfully**, including its large old ComfyUI installation. Files were reconciled beforehand, 43 real model file hashes checked, and the canonical ComfyUI service was confirmed at 8188. Exact deletion receipt: `.tools/cleanup_audit/legacy_purge_receipt.json`. Windows long-path and read-only cleanup was needed for old Git objects/pytest temporary trees.
- Three Windows research jobs and the 08:00 research job now execute from canonical paths; external `CineResearch_DailyState` was deleted after triple-file backup verification. `Company Youtube` remains a separate active evidence repository; do not mix its large data/history into pytest artifacts or purge it as garbage.
- **Open engineering debt:** replace historical machine-specific absolute paths with portable, source-hash-bound locators and reissue versioned test evidence; independently validate two archived SQLite database conflicts; remove the compatibility alias only after a clean relocation test. Commercial cinematic production remains blocked by the remaining acceptance failures and human/artistic/license gates.

## Verified SQLite ledger union — actual applied migration

Further read-only audit established that the two archived SQLite databases had **matching schemas**, no declared foreign keys, successful `PRAGMA quick_check`, and **no conflicting values for any shared primary key**. The old ledgers were NOT equivalent or safely replaceable wholesale.

- `cinefactory.db`: +112 unique projects, +230 unique assets, +1,904 immutable audit events. Existing 66 projects, 132 assets and 1,122 audit events were preserved. Union totals: **178 projects, 362 assets, 3,026 audit events**.
- `turbo.db`: +1,381 factory events, +469 throughput samples, +25 work items, +8 workers, +5 execution cost samples and +1 repair-memory record. Union totals: **2,173 factory events, 781 throughput samples, 25 work items, 8 workers, 5 cost samples, 1 repair record**.
- Versioned code: `scripts/migrate_legacy_sqlite_once.py`. Initial dry-run built candidate SQLite databases and validated all rows from both databases, duplicate primary-key equality, integrity check, foreign-key check and expected union counts. Only after this succeeded was `--apply` run on canonical databases, in per-database `BEGIN IMMEDIATE` transactions with live preimage revalidation and rollback on any error. **Both reported `APPLIED_UNION_VERIFIED`.**
- Original and legacy SQLite backups and staged candidate files were saved under `<outer>\.tools\cleanup_archive` and `<repo>\.tools\cleanup_audit`. Applied report: `.tools/cleanup_audit/20261010T114117_db_union_report.json`. No existing rows overwritten, deleted or silently ignored.
- Scope of this union is the two local CineFactory SQLite ledgers; it does not claim semantic agreement of every historical event or certification of the commercial media pipeline.

## Post-merge acceptance and safe operating boundary

- Full suite after actual SQLite ledger union: **1,310 PASS / 3 FAIL**; Python compileall PASS. The only remaining failures are `test_real_worker_source_provenance_unchanged` in v196 and two v190 real-rig tests, all due to historical source SHA-256 mismatch after the Blender worker was modified. No additional failures from the SQLite merge. Log: `.tools/cleanup_audit/pytest_after_db_union.log`.
- Three direct migration tests passed, and eight canonical workspace regression tests passed, for **11/11 targeted PASS**.
- Inspected imported `turbo.db` work item state: 17 `SUCCESS`, 6 `QC_REJECTED`, 2 `DEAD_LETTER`, **zero queued/running** from the imported 25. The eight historical worker rows still have `healthy=1` as recorded at their historical heartbeat timestamps; this must not be construed as current worker process health. Fresh heartbeat/lease checks remain mandatory for runtime job scheduling.
- Existing `Company Youtube` is intentionally still independent as the authorized source repository; unrelated Downloads items and non-CineFactory folders were not deleted.
- The old `CineFactory_Autonomous_Build` name remains only as a hidden/system Windows **junction compatibility alias** to the canonical repo, not a second source copy. Remove it only after migrating old paths embedded inside immutable verification artifacts.
