# CineFactory — One-Pass Company Hardening & Honest Acceptance
Date: 2026-10-10 Asia/Bangkok | Action: IMPLEMENTED + REAL TESTS, **not full studio completion**.

## Scope that was changed IN CODE

### A. Three fake-visual-PASS vulnerabilities: CLOSED
Files: `cinefactory/production/asset_factory.py`, `storyboard.py`, `video_factory.py`, `cinefactory/qc/visual_policy.py`.

Previously, missing `visual_qc` was equivalent to pass + 1.0 identity/continuity/performance/camera in generated output. This is NOT defensible professional QA. After the change:
- Generated ComfyUI (any premium/generative) requires an actual external local Visual QC command; missing QC fails CLOSED.
- Four metrics must all be finite numbers in [0,1] with `passed=true`. Bare truth, null metric, NaN/Inf, negative, >1 and below-threshold scores are rejected.
- Entire-film QC also uses the same fail-closed metric validator. Passing a shell command response is an advisory review, not authenticated semantic truth.
- Diagnostic slate is allowed by explicit internal flag **only for `production_mode=slate`**. The three components record `DIAGNOSTIC_SLATE_NOT_VISUALLY_REVIEWED`, **visual score = 0.0**, but deterministic FFmpeg slate assembly remains executable for technical smoke/CI. Its `release_ready` and `quality_certified` are always False. Thus a diagnostic completed MP4 cannot masquerade as an approved cinematic result.

### B. Premium preproduction research/production binding: IMPLEMENTED AS A STRICT GATE
Files: `cinefactory/production/premium_gate.py`, `cinefactory/autopilot/contracts.py`, `runner.py`.

New `AutopilotRequest.quality_tier`: `diagnostic` (legacy slate testing) or `premium`. Premium requires:
- Original actual footage backend rather than slate; current connected main Autopilot supports ComfyUI only. Blender and Unreal remain **candidate/in separate animation subsystem** and will be refused until genuinely connected.
- Non-scaffold reasoner; Visual QC command; source-locked, matching `production_conference.v1`, `director_plan.v1` and `conference_director_link.v1` with SHA256 chain.
- Exact niche, complete full video competitor research, completed quality-vs-time tool pilot evidence, owner decision marker, rights clearance and director-ready plan. Self-asserted markers are **not authenticated**; even a fully completed plan merely permits a controlled pilot, NOT automated publishing or quality certification.
- Exact planned shot IDs, shot duration, compatible planned workflow lane and verified capability. No silent Comfy substitution when director prescribed Blender.
- Final `AutopilotResult` now explicitly contains `quality_certified=false`, `release_ready=false`. Commercial release needs a separate independent authenticated human/rights signoff system to be implemented, not merely a model score.

### C. Read-only approved-niche research watch runner: IMPLEMENTED, NOT SCHEDULED
New `cinefactory/research_intelligence/pod_dispatch.py` with `python -m cinefactory.research_intelligence.pod_dispatch`. Collects approved `pod.json` and fresh canonical Company bridge snapshots; verifies source lineage; compares previous and latest; invokes the existing `pod_watch.watch_niche`. Bounded number of pods and snapshot files; refuses stale, mutated, mismatched or missing evidence. Outputs per-pod `watch.json` and immutable summary. Does NOT call YouTube, Claude, paid models, publish, grant ownership, or create Windows tasks.

**Remaining:** authenticated owner-click event, trusted durable runner with health check and genuine fresh marketplace snapshots. No automated full-video semantic view yet; this is the **watch layer only**.

### D. Verified acceptance dashboard
New `scripts/studio_acceptance_snapshot.py` records real observed Branch 1/2/Production states from source files and rendered project manifests. Does NOT mark Disney parity, competitor superiority or autonomous operation as proven.

### E. Actual YouTube scanner run, light profile
2026-10-10 `CINE-P1-20261010-001`:
- Public canonical scan started, covered 30/30 query buckets; captured extra intermediate evidence table / lane-B catalogs.
- Timed out at 180 s. Final `PARTIAL`, `strict_0_30_two_1m_niche_gate=NOT_EVALUATED_WITH_FULL_PROOF`, 0 verified qualifying niches from this run, no authorized bridge.
- Official exact age, million-views count, evergreen + economic gate is not proven; YT Data API credential absent. No niche fabricated.
- This is **not** a successful Daily research acceptance. Need small-step incremental/resumable snapshots, independent feed quotas, official verification/key budget, and repeated daily schedule evidence.

## What previous work already implemented, but is NOT magically finished by this patch
- Breakout discovery source, 5-gate review, Council and owner approval; cannot certify daily market discovery until source evidence is complete.
- Competitor research title/image/timecode worklists and multi-tool bakeoff contracts; full film understanding, scripts, shots, audio and expression observations have not passed independent semantic validation on opponent films.
- Existing original Blender character rigs, clips, expressions, camera and episode assembly; not yet demonstrated on a commercially acceptable 8–15 minute episode in this rollout.
- ComfyUI running locally is not evidence that chosen commercial checkpoint/model and custom nodes are executable. Earlier local SmolVLM2-256M CPU smoke 2/3 controlled questions was REJECTED.
- Rough cut FFmpeg concat is not professional fine editing (Resolve/Edit/Fusion/Fairlight remain candidate until tested).

## Safe usage

One-time diagnostic smoke:
```powershell
cd "C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6"
python -m pytest tests -q -p no:cacheprovider
```

Once there are locally approved pod files and fresh canonical imported bridges, run watch:
```powershell
python -m cinefactory.research_intelligence.pod_dispatch --pods-root "C:\path\to\approved_pods" --bridges-root "C:\path\to\verified_bridge_snapshots" --output-root "C:\path\to\NEW_IMMUTABLE_WATCH_RUN"
```

Premium generation requires approved, **immutable**, provenance-linked conference + director plan and a genuine visual reviewer:
```text
quality_tier=premium
production_mode=comfyui
reasoning_mode=file or command
visual_qc_command=<an actually tested independent renderer QC executable>
studio_director_plan_file=<auditable review-bound plan.json>
studio_conference_file=<auditable conference.json>
```
No fallback to generated video without QC is allowed. `quality_certified` remains false until a separately verified release layer is written and proven.

## Current status and next acceptance actions

1. DONE: remove false missing-QC passes; preserve explicit, zero-art-score, non-releasable slate.
2. DONE: bind premium pipeline admission to a verifiable research/director decision chain (fail-closed).
3. DONE: read-only niche pod watch dispatcher, real source verification, no extra scanner.
4. DONE: run light canonical discovery once with honest partial result and source snapshot.
5. OPEN: make scanner incremental/resumable, multi-market and truly reliable daily; provide real official data access/candidate verification.
6. OPEN: connect owner-approved pod to durable scheduler and 3-lane daily watches with valid snapshots and worker controls.
7. OPEN: local/cloud high-grade multimodal whole-video analysis, timecoded scenes/audio and independent specialist reviews; rights.
8. OPEN: connect Blender/Unreal/Comfy/Resolve as genuinely executable scene-quality workers, multi-GPU/cloud and measured pilot comparisons.
9. OPEN: benchmark original human-reviewed 8–15 minute Minecraft/Roblox film versus comparable professional channels, correct shortcomings before business launch; studio-grade fine edit/audio/color, signed quality and analytics loop.

**No Disney-quality claim; no guaranteed YouTube earnings; no product/market readiness claim.**
