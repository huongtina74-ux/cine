# CINEFACTORY REAL COMPANY PIPELINE AUDIT v265 — 2026-10-11

## Verdict and scope
**VERDICT = PARTIAL_FUNCTIONAL_DEMONSTRATION / NOT_PRODUCTION_QUALIFIED.**
This was a controlled original-IP Nova & Pip 45-second target with a 15-second R&D subtest. No paid credits, no YouTube OAuth, no uploads. The full native Company Orchestrator stopped safely before production. No complete 45s or 14min 3D professional video was rendered.

**Do not claim "company runs all 26 departments" from code definitions or handoff JSON.** This report separates desk paperwork, actual executable checks, stage ledger and playable media.

## 1. Evidence ledger: what ran

| Test | Actual operation | Objective observation | Pass? |
|---|---|---|---|
| Readiness | `python -m cinefactory.cli company-readiness` | `NOT_PRODUCTION_QUALIFIED`; 26 declared, **0 independently execution qualified, 0 independently art quality qualified** | Honest fail-closed |
| Worker check | Same readiness | **8 stored worker rows, 0 fresh active**, 8 stale reported healthy; historical 17 successes, 6 QC rejected, 2 dead letter (historical counts ≠ running workers) | BLOCKED |
| Company Plan | `company-plan ... --niche minecraft --domain animation --minecraft-subniche minecraft_story_adventure --duration 45` | Recipe candidates for Blender local and FFmpeg; originally both said executable even though Blender not found in current machine search | Original phantom capability DEFECT |
| Runtime route FIX | `runtime_route_grounding_v265.py`, integrated in `company.py` professional plans | Blender `executable=false` with `RUNTIME_EXECUTABLE_UNVERIFIED:blender.local`; FFmpeg `executable=true` only after actual binary `-version` pass, version 7.1 local build | PATCHED + tests |
| Native Company Run | `company-run ... --production-mode slate --tts-mode none --max-cycles 22` | **5 cycles**, Intake/Portfolio/Intelligence SUCCEEDED, EVIDENCE SKIPPED (no referenced-source packet bound), CORP PREFLIGHT NEEDS_REPAIR; 28 further statuses pending, 33 stage ledger entries total | Proper stop, no E2E pass |
| Preflight | Same run, corporate_preflight artifact | Nine blockers incl COMPETITOR_RESEARCH_REQUIRED, NICHE_RESEARCH_MISSING, SEO_DISCOVERY_REQUIRED, COMPETITOR_BASELINE_MISSING, RIGHTS/monetization and packaging baseline. No fake research approval | Safety works; disconnected input |
| Maizen Studio desk rerun | `maizen-studio --start` | Failed `DEPARTMENT_HANDOFF_ALREADY_EDITED` on immutable prior receipts; correctly protected changes but could not rerun | P1 resume/versionability defect |
| Maizen desk patch | `maizen-studio --start --output-dir data/verification/v265_company_e2e_reality/maizen_desk_handoffs_isolated` | 26 actual **desk receipt files** created in isolated version without altering previous; 18 DRAFT_CREATED, 5 PARTIAL_EVIDENCE, 3 BLOCKED_EXTERNAL_DEPENDENCY | PATCHED / desk only |
| Native video + audio smoke | `.tools/cine_e2e_rnd_animatic_v265.py` | Original-IP moving **2.5D animatic 15 seconds**, three screenplay-matched P01/P02/P03 shots; English Microsoft Zira scratch TTS, original procedural waterfall/amber synthesized sound, H.264 video/AAC audio, 640×360, **24 fps**, native decode PASS | BASIC MEDIA SMOKE PASS |
| Art QA | Still frames at 00:02/00:12 inspected | Flat stick/square actors, minimal acting, no 3D depth, no high-quality lighting/camera, no real imported OBJ rigs/lipsync, no independent film quality signoff | CINEMATIC **FAIL** |
| Source G02 | v262/v263 source reports | 120 windows still **not independently semantically reviewed**; 11 flagged were re-observed 1× but that cannot self-certify full films | BLOCKED |
| Publication | No upload token or owner approval | **No upload or release** | Safety preserved |

### The ledger's 18 checked stage statuses (of 33 total)
- SUCCEEDED: PROJECT_INTAKE, PORTFOLIO_GREENLIGHT, INTELLIGENCE
- SKIPPED: EVIDENCE (new project created without binding selected source videos and existing film research)
- NEEDS_REPAIR: CORPORATE_PREFLIGHT
- PENDING: CREATIVE_STRATEGY, PLANNING, WRITING, LOGIC, DIRECTION, ASSET_BUILD, PREVIS, TECHNICAL_DIRECTION, PRODUCTION, EDITORIAL, AUDIO, FINAL_QC, PUBLISHING
- The separately generated 15s video is an isolated original-IP R&D smoke test, **not** proof the Company Orchestrator executed those pending stages.

### Diagnostic scoring
`company_reality_probe_v265.py`: **3/14 very strict binary checks passed** (initial intelligence bootstrapped, FFmpeg executable actually validated, a real decodable R&D audio+video artifact created). This is a **checklist count, NOT a percent cinematic quality score, company completion percent or simulated estimate**.

## 2. What is genuinely good
- Correct block instead of unauthorized financial/media spend or upload.
- Durable stage ledger, resumable company project and artifacts.
- Source/research databases retained and provenance distinctions supported.
- Original script 840s/82 shots, original 27 static OBJ blockouts and 82 SVG/PNG storyboard items exist and have passed structural tests from v263. However NONE of these automatically demonstrate movie quality.
- Win32 offline TTS plus FFmpeg can produce a viewable/sounding test; full-file decode QA works.
- Immutable prior dept receipts protected. v265 safe isolated output recovers desk handoffs.
- v265 runtime routing hardening stops unverified Blender being falsely called executable.

## 3. Priority remediation and measurable acceptance

### P0. Research → company blackboard binding
**Problem**: Company Youtube/CineFactory have scoped Maizen research, native-source G02 receipts and age-matched findings, but a brand new `company-run` cannot import them into `INTELLIGENCE/EVIDENCE` stages. "INTELLIGENCE SUCCEEDED" can mean a generic summary while `competitor_profile_count=0`. **Don't fabricate approvals or bypass corporate preflight.**
**Fix**: Design a signed/versioned `ResearchHandoff` with exact URLs/video IDs, format, G02 reviewer-type, allowed use and evidence hashes; import only approved public findings into project evidence_map, never raw third-party copyrighted media. Require stage evidence in creative script/shot plan when those conclusions are source-derived.
**Acceptance**: new project sees real channel/video proofs; rejects a metadata-only packet; Corporate Preflight remains blocked until required original niche commercial and rights baselines exist.

### P0. Actual backend and worker execution
**Problem**: `blender.local` planned executable without confirmed installed binary; 0/8 fresh workers and GPU free around 2.98GiB at one observation. A 27-asset static OBJ folder isn't a render engine.
**Fix**: v265 grounded core capability; next resolve real Blender path/license, persistent worker GPU heartbeats, first native original 3D scene with rigged Nova/Pip, isolate VRAM when loaded.
**Acceptance**: original shot outputs actual 3D motion with sound; Blender version+GPU+render receipt, real VRAM high-water, per-accepted-second time measured, script/voice synchronization.

### P1. Script/director/asset reality
**Problem**: 82 shots and 82 schematic boards are NOT validated shot blocking or film staging. First R&D output (viewed at 2/12 sec) is visually simple 2D, no polished 3D camera language.
**Fix**: 21-beat read-through at spoken runtime, acting/pose library, foley, consistent eyeline/geography; 45s true animated original test based on 9 shot cards and actual assets. Scene-level method selection and QA.
**Acceptance**: real 1080p24 45s with character ID, physical prop continuity, original VO, camera coverage and sound; independent shot-by-shot QC.

### P1. Creative Audio and Editorial
**Problem**: Scratch Windows voice and ambient works, but does not meet emotionally acted childlike/pro voice requirement; voice is single speaker, mix only basic amplitude, no casting/lipsync/audio cue validation.
**Fix**: Voice acting style Bible, 2 actor voices (with rights), spoken timing, word-level dialogue markup, sound cue sheet, rhythmic scene edit, loudness and unclipped dialog.
**Acceptance**: original 45s film with audible natural emotional acting; edit timing and sound spotting signed.

### P1. Resumable departmental coordination
**Problem**: old `maizen-studio --start` refuses modified pre-existing desk outputs; correct immutable-file safety but not operationally convenient.
**Fix**: v265 `--output-dir` gives isolated, versioned handoff receipts. Next add diff comparison, reconciliation and stale-handoff reporting; do not overwrite edits.
**Acceptance**: repeated runs produce tracked versioned manifest; actual departments consume previous outputs with provenance.

### P1. Native video + audio independent quality gate
**Problem**: original 120 windows still G02 unapproved; transcode PASS is not artistic PASS.
**Fix**: second AI agent independently reviews full native film with sound and moving picture + human signoff if project requires it; compare to own weak/median peers. Then independent QC of first actual original film with vision+audio and rights.
**Acceptance**: scene- and sound-timestamped native QC, no black box "fully watched" from contact sheets/VTT, signed if required, all discrepancies resolved.

### P2. Packaging/revenue flywheel
Not attempted because no qualified original film. Do NOT equate arbitrary view/sub trends with owned retention or RPM. After first approved video: honest title/thumbnail, measured CTR/reach/watch-time on owned account, versioned learning and next script.

## 4. Safe permissions
- 15s R&D clip is permitted original intellectual property, **separate from blocked competitor-research G02**. It is not production approval or an allowed shortcut through corporate governance.
- No external paid media API, no installation, no third-party clip reuse, no upload.
- v265 changes include runtime grounding and isolated desk receipts. Only independently verifiable real media is QA-eligible.

## 5. Actual local reproducible artifacts (on user's own Desktop)
`data/verification/v265_company_reality_check_readiness.json`
`data/verification/v265_company_plan_output.txt` (PowerShell UTF-16 output)
`data/verification/v265_company_run_probe.json` (PowerShell UTF-16 output)
`data/verification/v265_company_e2e_reality/nova_pip_RND_animatic_15s_v265.mp4`
`data/verification/v265_company_e2e_reality/rnd_animatic_15s_qa.json`
`data/verification/v265_company_e2e_reality/company_reality_scorecard.json`
`data/verification/v265_company_e2e_reality/maizen_desk_handoffs_isolated/manifest.json`
Code: `cinefactory/studio/runtime_route_grounding_v265.py`, `cinefactory/studio/company_reality_probe_v265.py`; tests with `tests/test_runtime_route_grounding_v265.py`, `tests/test_company_reality_probe_v265.py`.

**Final verdict: the company has functional research memory, stage planning and basic animation+audio tooling, but the production-grade end-to-end handoff is NOT READY. Primary bottleneck is authentic evidence import and executable render-worker readiness.**
