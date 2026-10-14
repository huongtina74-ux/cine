# CineFactory OS v266 — Real Research → Orchestrator Evidence Bridge
Date: 2026-10-12. Scope: scoped Minecraft/Maizen original-IP project; no paid APIs, no rendered 3D, no YouTube release.

## Direct implementation
1. `cinefactory/studio/research_evidence_bridge_v266.py`: read-only source loader for 3 existing, explicit Maizen evidence sources: 52 candidate YouTube-video public metadata rows (source list bounded), public About source, 120-window G02 **unsigned** native review ledger. Checks source SHA-256 on both handoff creation and loading. Project ID must match and every derived input is rechecked against source, so handoffs cannot declare user-certified facts.
2. `company-run --import-maizen-research --project-id <ID> --niche minecraft`: builds a project-bound research handoff before run, marks EVIDENCE required. `--resume` reuses the saved handoff and refuses a new import. New-project scope only; not a global automatic collector or unapproved promotion.
3. `FilmCompanyHandlers.intelligence`: loads source-linked, sanitized research sample into project `research_pack`; competitor video metadata remains UNVERIFIED SEMANTIC, source-derived production methods unapproved. Existing `INTELLIGENCE` and corporate stages intact.
4. `FilmCompanyHandlers.evidence`: explicit EVIDENCE handler only on imported handoff; writes a source-bound evidence_map with video IDs, 120 pending windows, source hashes, signed=false; returns `G02_INDEPENDENT_AV_REVIEW_PENDING` instead of silently SKIPPED or forging PASS. Existing projects without this explicit scope preserve their previous evidence registration policy.
5. No render/publishing escape hatch introduced. Backend runtime grounding from v265 still prevents Blender executable claims without launching a real binary.

## Actual native company-run evidence
First test with tts_mode=none correctly detected `BLOCKED_REQUIRED_HANDLER:VOICE_PREP`. After providing a TTS route flag so the experiment could reach the research gate, `CF_MAIZEN_V266_G02_ACTUAL` (45-second fictional/original Minecraft-animation intent) completed:
- PROJECT_INTAKE: SUCCEEDED
- PORTFOLIO_GREENLIGHT: SUCCEEDED
- INTELLIGENCE: SUCCEEDED (the scoped research pack is attached)
- EVIDENCE: NEEDS_REPAIR — `G02_INDEPENDENT_AV_REVIEW_PENDING`
- CORPORATE_PREFLIGHT: NEEDS_REPAIR — `CORPORATE_PREFLIGHT_BLOCKED`
- CREATIVE_STRATEGY / WRITING / DIRECTOR / PRODUCTION: PENDING (correct, NOT skipped forward)
- Film or actual 3D production executed: NO.
- Release or upload executed: NO.

Native stdout/probe evidence: `data/verification/v266_company_with_handoff.json` (PowerShell UTF-16), project-bound source hashes at `data/projects/CF_MAIZEN_V266_G02_ACTUAL/company/research_handoff.json`. This is not an independent certification of the source films.

## Quality and ethics gates remaining
G02 STILL OPEN: original 3 films (Mine Block/JJ Cartoons/MSToons) were structurally captured and flagged 11 of 120 windows re-observed at 1x. It has NOT been independently fully watched/listened to for native semantic content across the entire duration; no human signoff exists. Two independent AI model passes can be implemented but must be honestly labeled AI reviewed. Source toolchain cannot be inferred with certainty from output.
Corporate Preflight STILL OPEN: baseline/contemporaneous competitors and licensing/monetization, SEO and commercial risk still need verified inputs. Never bypass preflight to tick green.
Production worker STILL OPEN: on-device `blender.local` not established as executable by v265 runtime probe; files `blender.exe` in `.tools/*test*` are fake test fixtures and NOT evidence of a real engine. Previous readiness counted 0 fresh active workers and 8 stale rows. RTX3060 VRAM may be occupied; no actual 3D rig/animated shot rendered or qualified in v266.
Productization requires a verified Blender/Minecraft runtime, genuine original rigs and a 45s 1080p24 video+audio pilot that passes independent cinematographic QA; previously produced 15s v265 640x360 2.5D test does not count.

## Measurable next action
P0. Independent native A/V model research pipeline + real second reviewer over all source film seconds; compare against weak/median reference videos; incorporate G02 evidence into handoff once actually signed by identified qualified reviewer/agent, with no self approval.
P0. Resolve real Blender install/path/license; start one persistent worker with subprocess and fresh heartbeat, render an original small motion shot, inspect exported video.
P1. Resume corporate pipeline only after source/commercial gates qualify; use original-IP R&D branch in isolation for tech benchmarking, not as permission to publish.

The current milestone proves research imports into an actual project and G02 prevents unsupported promotion; it does **not** prove the whole company is production ready.
