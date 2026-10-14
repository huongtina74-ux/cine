# CineFactory v209: Professional Production Hardening

Date: 2026-10-10. Canonical repository: C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6
Status: ENGINEERING INTEGRATION / NOT COMMERCIALLY QUALIFIED FILM FACTORY.

## Changed in one integrated source revision

1. studio/company.py: New generic prompt-only projects default to professional governance; unclassified niche is blocked from production without owner greenlight. Existing library migrations may explicitly choose professional_governance=False; CLI always requires professional governance.
2. studio/script_continuity_v209.py and company_handlers.py: Replaced logic_report passed=True/findings=[] autopass with deterministic scene validation and structured STATE_ID handoff contradiction detection. The structural pass explicitly says independent causal, emotional, acting and camera review is PENDING.
3. cli.py: A strict company-run now preflights every required stage handler. Missing mandatory VOICE_PREP or any other executable returns a named BLOCKED_REQUIRED_HANDLER error before company runner dispatch.
4. studio/film_release_gate_v209.py and company_handlers.py: Strict FINAL_QC now rechecks the ACTUAL media (ffprobe, >=1080p, audio, fps and 30-60s pilot or 480-720s longform duration) and requires six externally trusted independent Ed25519 reviews for story, acting/identity, camera/edit, sound, rights and originality. Technical video PASS cannot become public release approval. Existing final owner approval remains separately required.
5. studio/operational_readiness_v209.py and CLI company-readiness: Read-only health board distinguishes written department charters, film-quality qualification, current worker heartbeats, actual research evidence state, source limitations, 7 niche contract graphs and model placeholders. A stale worker historical healthy flag never qualifies an active worker.

## Source- and authority-based production contract

Research input -> actual verified format / age / growth / competitor evidence -> approved niche and source-based signed work order -> Script Room and original continuity -> original legally cleared character/voice/scene assets -> authorized producer and render worker -> editorial, sound, color, effects -> actual ffprobe media -> signed independent film reviews -> explicit owner final approval -> private-first YouTube upload, provider receipt, owned Analytics -> owner-reviewable learning.

Each arrow requires source-bound artifacts, rights and independent QC; an available tool is not a qualified film department. Minecraft authored animation is not real-game capture. A competitor sample title is not watched footage. True owner Analytics cannot be read from public metadata.

## Safe operator commands

Open PowerShell in the canonical checkout:
  cd "C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6"

Get full company status without rendering or publishing:
  python -m cinefactory.cli company-readiness

Save operator state report without editing source/history:
  python -m cinefactory.cli company-readiness --output-file ".tools\deep_audit_20261010\v209_current_readiness.json"

Test the 60-second original animated Minecraft plan, no production:
  python -m cinefactory.cli company-plan --project-id mc_v209_plan --niche minecraft --minecraft-subniche minecraft_story_adventure --prompt "Original animated Minecraft adventure" --duration 60

Trusted Ed25519 public keys are supplied outside media projects through CINEFACTORY_FILM_REVIEWER_KEYS_FILE. Independent review signatures are supplied at data/projects/PROJECT_ID/inputs/independent_film_reviews.json and must reference the true master SHA. Reviewers' private signing keys must not enter Git. A film still requires explicit owner release consent after independent quality review.

## What remains unproven

- Research Daily P1 BLOCKED (official channel age and breakout proof incomplete), no approved niche pods.
- Real 30–60-second accepted ORIGINAL visual+acting+audio pilot with rights approval; then an accepted 8–10-minute original film.
- Actual staff-quality rigging/expression/animation/camera/lighting/music editing performance, measured time per accepted second and retake budget.
- Actual ComfyUI WAN local video workflow with complete non-placeholder model components, rights and VRAM certification.
- Active healthy continuous Blender workers, zero unauthorized GPU spend, retry/recovery throughput and per-shot costs.
- Authenticated user channel YouTube owner OAuth/private upload and first-party retention & analytics with tested reversible learning.
- Three historical Blender v190/v196 source-provenance SHA discrepancies require new independent evidence, not rewritten test hashes.

The project is a software architecture and testing milestone, not a Disney-level film-production certification.

## Engineering verification of this exact integrated release (10 Oct 2026)

- Canonical full-suite: **1,449 PASS / 3 historical FAIL**, 196.23 sec. Log: .tools/deep_audit_20261010/v209_full_final.log.
- Only remaining failures are v190/v196 historical Blender worker provenance SHA expectations. They are not rewritten or suppressed.
- New v209 gate tests: script mechanical continuity, declared state contradiction rejection, independent reviewer Ed25519 signature validation, external trust-root enforcement, mandatory handler preflight, truthful dynamic worker heartbeat, Windows PowerShell UTF-16 Research outcome parsing, explicit legacy compatibility and no false production-ready claims.
- Exactly five old v166 diagnostic harnesses were migrated to explicitly pass professional_governance=False. They continue to test their original diagnostic stage scheduling, retry, slate and repair semantics; they are NOT production entrypoints. New generic project default True is separately tested. The v166 diagnostic smoke: 23/23 PASS.
- Complete old-plus-new studio targeted cross-tests passed 82/82 (before the migrated test fixture update), and final full suite above is authoritative.
- Operational CLI: python -m cinefactory.cli company-readiness. Current Research Daily P1 BLOCKED, 08:00 scanner RESEARCH_PARTIAL, no verified breakout niche, 0 approved pods, 8 stale stored Turbo worker heartbeats, 0 fresh workers. Company production_ready remains False.
- Compilation: python -m compileall -q cinefactory scripts PASS.
- Zero paid image/video/audio API calls; no new original movie or YouTube upload was claimed or fabricated.

**FINAL ENGINEERING VERDICT: V209 GATES INTEGRATED/REGRESSION VERIFIED; ORIGINAL FEATURE-FILM QUALITY AND LIVE CHANNEL FLYWHEEL STILL NOT QUALIFIED.**
