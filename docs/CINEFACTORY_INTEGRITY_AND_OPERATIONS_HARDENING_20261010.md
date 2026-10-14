# CineFactory OS — Evidence, Premium and Scheduled Operations Hardening
Date: 2026-10-10 Asia/Bangkok
Repository: `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`
Starting revision: `1783bbb`. Status: actual source changes and targeted regressions, NOT a claim of cinematic acceptance.

## Confirmed vulnerabilities and patches

### P0 — Source-lineage TOCTOU / forged bridge-derived views and gate conclusions
Finding: `verify_imported_company_sources` previously verified only SHA-256 of the two Company Youtube CSV files. The separate derived `cine.bridge.company_snapshot.v1` JSON was editable; its `candidates[].channels[].videos[].views`, `triage.status`, `triage.gates`, and source selection could diverge without changing CSV hashes. This could poison watch alerts and an owner activation flow.

Fix:
- New `bridge_integrity.verify_bridge_semantics`, now called by `market_bridge.verify_imported_company_sources`.
- Each claimed channel, observed time, creation time, subscriber count, age and evidence state must match an actual row in the original hashed channel CSV.
- Each claimed video ID must be unique and must match an actual hashed video CSV record: source URL, video owner, publish/observation timestamp, 8-minute duration, exact source view number, label, topic matching and evidence status.
- Source links must be exactly the imported selected set. Input review flags must match the candidate flags. The five-gate triage is recomputed from the source-matched current candidate and required to match the saved triage.
- `activate_research_pod` now invokes the same semantic verifier; fake local owner approval records and unchanged source hashes cannot bypass the consistency gate.
- Regression: forged views with unchanged CSV, forged triage, mismatched review flags, duplicate video IDs and fake locally approved pod are rejected before watch/activation.
- **Limit:** This validates that a bridge faithfully reflects *what the Company CSV says*. It does NOT independently prove the CSV represented true YouTube API data, authenticated human review or actual RPM.

### P0 — Premium shot identity and strict boolean gates
Finding: constructing `expected` by dict and `actual` by set silently hid repeated `shot_id`. The production conference used truthiness for gate flags, allowing the string `"true"`, and missing director counters were treated as equivalent to zero.

Fix:
- Explicitly reject duplicate/missing shot IDs, empty shot plans, and actual/planned mismatches.
- `deep_content_analysis_completed`, `tool_benchmark_completed` and `owner_approval_authenticated` must be JSON booleans `true`; plan counters must be actual integer 0.
- No change to fail-closed slate/Comfy renderer controls. These metadata gates alone are NOT evidence that the reviewer or owner was cryptographically authenticated.

### P1 — Local authorized-footage intake race and resource bounds
Finding: input manifest SHA was checked only at first read. Files might change during FFmpeg/frame extraction; large inputs could cause expensive reads.

Fix:
- Bound local video size to 32 GiB, refuse zero bytes before expensive hash.
- Match input SHA against actual FFmpeg timeline source SHA and rehash after mechanical and frame study. A changed file is marked `MEDIA_SOURCE_CHANGED_DURING_ANALYSIS` and never emits completed intake.
- Regression: simulated replacement during processing and budget overflow reject before completion.
- **Limit:** Permission reference is still a claimant-provided local statement, not legal verification of copyright ownership.

### P1 — Scheduled Pod Watch failure invisibility / duplicate evidence snapshots
Finding: a malformed/missing data source could throw before producing `latest_run.json`; multiple snapshots with the same local time could masquerade as a previous comparison or block valid operations without a clear reason.

Fix:
- Daily scheduler writes immutable `BLOCKED_DISPATCH_ERROR` attempt summary with sanitized error class and saves latest status through atomic `os.replace` even when input invalid. Locked overlapping runs remain blocked.
- P2 CLI exits nonzero for every state other than `NO_PODS`/`WATCHES_COMPLETE`.
- Dispatcher deduplicates identical same-timestamp snapshots, refuses conflicting same-timestamp snapshots for the affected niche pod (does not manufacture view-velocity).
- Regression: missing input persists error, lock released, subsequent attempt succeeds; identical duplicate coalesces and conflicting duplicates block.

## Verification boundaries / remaining business-critical work

**Still OPEN, not hidden:**
1. Exact age and view proof requires authenticated official YouTube Data API (channels.list/videos.list), not youtubei.js, and real multi-format cross-market search. View counts are observations, not causal RPM or revenue guarantees.
2. Owner approval remains a **local JSON event**, explicitly `owner_event_is_authenticated=False`. Human-authenticated owner click and tamper-evident signoff must be implemented before unassisted decision-making.
3. ComfyUI Wan2.1 1.3B technical smoke did render a 320×192 2.125s clip, but no realistic world, professional acting/voice/edit or full length was independently accepted. Blender executable still not confirmed on the current path.
4. Competitor footage cannot be downloaded/analyzed without sufficient rights. Local frame/audio mechanics and sampled review packets do not equal fully semantic 8–15-minute VLM+audio screenplay/acting understanding.
5. Windows tasks need long-running observed reliability, safe data staging/backups and storage alarm. The scheduled niche pod currently has `NO_PODS`, not a live approved niche; P1 scanner remains partially blocked without exact official provenance.
6. Supply-chain trust of third-party Comfy nodes, checkpoint licenses, SaaS/GPU cost controls, human visual baselines, actual 720p/1080p/4K full-film pilot, and independent artistic QC are NOT closed by these code changes.

All changes are intended to be retrospective/source-preserving; no current approved niche, upload or paid API activity is initiated here.
