# CineFactory v205: Department, Native-Media, Research Handoff and Release Infrastructure

Date: 2026-10-10. Canonical checkout:
`C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`

**Engineering state: PARTIAL / REVIEW REQUIRED. Not a production-qualified 8-10 minute media company.**

## Verified v205 hardening results — October 10

- **Final complete v205 regression after all code changes: 1,344 PASS / 3 FAIL**, runtime 195.48 seconds. All 3 failures are the pre-existing SHA lineage checks of the v190/v196 Blender worker; do not rewrite historical sources or fixture hashes. Exact record: `.tools/deep_audit_20261010/v205_final_verified_suite.log`. No newly introduced failing tests.
- Targeted contracts, CLI exact-project routing, signed metadata, source deduplication, trusted Analytics OAuth, durable private-upload receipt, independent QC re-verification and compatibility checks: **39/39 PASS**. Raw record: `.tools/deep_audit_20261010/v205_final_delta_suite.log`.
- Four real CLI company-plan calls each returned 10 correctly wired stages under `NICHE_PROJECT_INTAKE`, no unbound stage inputs, and an **unapproved production state**: ASMR hands/objects, audio stories for seniors, fishing silent, rain/white noise.
- CLI now supports `company-plan --project-id` so an operator can inspect the **same** signed pilot project it will later execute. `research-to-studio --project-id` refuses writing when the signature authorizes another project. Pilot signatures are scoped to 30–60 seconds only.
- Source provenance is still limited by the quality of imported YouTube API archives and independent human source verification. A JSON field saying `VERIFIED_OFFICIAL_API` cannot itself prove that Google served that response. Owner approval grants only an original pilot; automatic earnings/viral declarations remain prohibited.
- Film signature verification is rechecked at the publication boundary. An owner-upload signature binds movie hash, metadata hash, channel and expiry; read-back confirmation yields a durable separate receipt. On uncertain upload failure the reserved attempt remains blocked for manual provider reconciliation; never silently retry.
- Current real acceptance: one tiny diagnostic FFmpeg composite, **no owner-approved original 8–10-minute film**, no real YouTube upload and no owned-channel Analytics readings. No paid generation API was called.

**The current source code is not a production release.**

## 1. What is integrated

- 26 / 26 `DepartmentId` values now have distinct mission/knowledge/skills/tool/input/output/rules/QC charters. Existing `DepartmentRegistry` was extended in place (no parallel fake organizational tree). The 11 added charter specs are in `studio/department_charters_v205.py`. A charter is not an independent executable expert or a film-quality certification.
- Four native media niches (ASMR hand/object, Audio Storytelling, Fishing Silent, Rain/White Noise) use specialist production graphs/handlers instead of the Minecraft/Roblox animation previsualization graph. The specialist path has ten core departments/stages including source rights, actual FFmpeg source assembly, technical audio, independent film QC, private-first publishing and Analytics.
- The legacy explicit `MediaFormat.NARRATIVE_FILM` blueprint preserves the original story architecture and review structure even when passed a niche name. New non-film project paths use specialist lanes. The CLI chooses handler registration based on the actual saved blueprint stage list rather than niche name alone.
- `Research -> Studio` now has an immutable approved-pod/source bundle -> signed Ed25519 owner event -> work order in `data/projects/<project_id>/inputs/` -> project-intake verification -> original-pilot greenlight. This path is *limited to 30-60 seconds of local original pilot*. A new work order doesn't authorize full episodes or public publishing.
- The company compiler retains explicit stage wiring failures, signed pilot-only approval trace and strict per-stage blackboard receipts. Source manifest hashes are verified at the rights gate and again before encoding. No service/worker is certified solely from HTTP up.
- Actual local FFmpeg smoke: two 1s generated diagnostic video+audio clips passed original-source technical assembly, produced a real encoded MP4, reached sound check, and correctly stopped at the independent-film QC gate. The resulting movie is NOT a channel-ready video.
- Long-form acceptance `studio/longform_acceptance_v205.py`: real FFprobe duration/fps/width/height/audio/hash gate, six different trusted Ed25519 film reviewer signoffs (story, acting/identity, camera/edit, sound, rights, originality). A mock JSON saying `approved` is not release authorization.
- Standard professional blueprint now includes a distinct `PUBLISHING` stage before Analytics (not just Packaging -> Analytics), and its handler fail-closes without authenticated provider upload.
- Native-media specialist publishing has a Google YouTube private-first adapter, exact-channel OAuth preflight, per-video signed owner approval, immutable **pre-network idempotency reservation**, read-after-write provider receipt and no public visibility change.
- YouTube Analytics adapter can query the explicitly connected owner's video statistics using separate OAuth. Observations are persisted with provenance, while learning candidates remain REVIEW_REQUIRED with `promotable=False`; no automatic company self-modification.
- CLI accepts explicitly scoped credentials on `company-run`: `--allow-private-upload`, `--owner-youtube-oauth-file`, `--owner-youtube-analytics-oauth-file`, `--owner-channel-id`. No credentials are connected, uploaded, published or inferred by default.

## 2. Source and authority hierarchy

```text
Approved Research Pod (immutable bridge + verified source bundle)
  -> separate 24-hour Ed25519 signed pilot decision, local-only
  -> exact project ID + niche + 30-60s manifest
  -> project-specific production work order (immutable)
  -> owner-generated source clips + rights docs, independent signed rights clearance
  -> real FFmpeg assembly (no loops/padding/borrowed footage)
  -> technical audio + independent film QC, six distinct trusted reviewers
  -> approved master + truthful metadata + explicit made-for-kids answer
  -> *separate* per-video signed owner permission, OAuth token, reservation file
  -> Google videos.insert(private) + live provider readback
  -> authorized owned YouTube Analytics API response
  -> source-linked observations, experiment hypothesis, owner-reviewed skill learning
```

A synthetic test can exercise the signatures and protocols. A synthetic test **cannot** establish truth of YouTube external metadata, licensing, ownership, actual artistic quality, or platform performance.

## 3. Safe operator commands (no auto-upload)

PowerShell, after `cd C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`:

```powershell
python scripts/company_architecture_doctor_v204.py
python -m cinefactory.cli company-plan --prompt "Original ASMR hand-object video" --niche asmr_sleep_hands_objects --duration 60 --project-id PILOT_001
python -m cinefactory.cli research-to-studio --project-id PILOT_001 --approved-pod "PATH_TO_POD_JSON" --verified-evidence "PATH_TO_ARCHIVED_SOURCE_EVIDENCE_JSON" --owner-event "PATH_TO_SIGNED_PRODUCTION_EVENT_JSON" --trusted-owner-key "PATH_TO_TRUSTED_OWNER_PUBLIC_PEM"
python -m cinefactory.cli company-run --project-id PILOT_001 --niche asmr_sleep_hands_objects --prompt "Original ASMR hand-object video" --duration 60 --max-cycles 2
```

The third command **requires authentic, independently verified source evidence and a signed event**. It must not be faked to pass tests. The public key must be an externally trusted key chosen by the owner; never store private signing keys inside project or Git.

Provide the public verification key through the runtime environment `CINEFACTORY_OWNER_TRUST_PUBKEY` for the signed pilot to pass preflight. Provide actual clips under `data/projects/PILOT_001/inputs` plus their manifest and separate signed rights review before production. For actual optional private upload, supply owner OAuth only after signed film acceptance and separate signed private-upload permission. The CLI requires an explicit `--allow-private-upload` switch and a matching `--owner-channel-id` even when OAuth exists.

**No automatic public publishing command exists.** There is no default paid API usage. No file from historical signed evidence was deleted or its SHA changed to make tests green.

## 4. Current blockers / what is NOT finished

1. **Eleven charter departments**: specs now exist, but independent executive skills, tool runtime, art QC and output acceptance across every niche still need live evidence. Do not mark all 26 as QUALIFIED.
2. **Four specialist lanes**: graph and real FFmpeg source assembly now exist; only diagnostic-source assembly was tested. Actual 8-10 minute original footage/audio and niche-specific aesthetic tests not accepted. Some sources (fishing location, narrated copyright rights) still require genuine independent legal/human review.
3. **Research**: no independently established current 0-30d channel with 2 distinct 8m+ million-view videos in the live evidence store. Real research pod must be approved; work-order cryptography cannot prove a claim sourced from false YouTube metadata. Research providers are still source-limited.
4. **Full film**: no real 8-10 minute mastered episode reviewed by story, acting, camera, sound and rights specialists in this audit. 30-60 second Minecraft v197 earlier pilot was not quality qualified.
5. **YouTube**: adapter is implemented but no production owner OAuth was supplied or exercised live. No upload, owned Analytics results, CTR, retention, RPM or monetization verified. Private-first upload reservation requires reconcile/manual review after uncertain network failure (not automatic retry).
6. **Historical Blender source provenance**: 3 old v190/v196 checks still expected to fail until true new acceptance data are independently reissued; never rewrite archived hashes.

## 5. Release gate

Production-complete is a *future* status, conditional on:
- Verified source-backed approved niche; exact work order + authenticated approvals; no one can self-declare research/rights/film quality.
- 30-60 second original pilot accepted by art/sound/camera/rights independent reviewers on the *actual rendered media*; clean production/QA evidence and repeatable accepted seconds/hour.
- One original 8-10 minute film passes file integrity, scene identity and full-film human QC in the intended niche, without fake loops or uncontrolled reuse.
- Per-video private upload independently verified on an owned channel, real Analytics returned after enough observation, reviewed improvement with rollback and regression checks.
- All tests pass, including newly versioned validated historical provenance, and all actual services have fresh leases/heartbeats.

**Verdict: ENGINES AND CONTRACTS CONNECTED FOR VALIDATION; NOT FULLY AUTONOMOUS COMMERCIAL FILM-ACCEPTED.**
