# CineFactory v1.6.33 — Evidence-Driven Strategic Reasoning + Scientific Learning

**Date:** 2026-10-09  
**Status:** implemented as an **advisory** company service; NO release/production execution permissions.  
**Hardware & environment:** Windows, RTX 3060 12 GB, Blender and FFmpeg available; no auto paid APIs, no software installed.

## Design intent

The company should **reason rigorously**, not pretend it knows the best engine from a list. It needs to pose falsifiable hypotheses about each production method, examine contradictory or stale evidence, ask several departments to criticize claims, select the next highest-value experiments, measure actual accepted-video cost and learn only after controlled tests. The new v193 implementation is a deterministic, inspectable *reasoning-policy framework*. It is NOT a newly trained reasoning language model or an unrestricted live web-reading intelligence. It provides a strict handoff contract for future connected thinking agents while keeping authority in company QA/rights controllers.

## Architecture

```text
Project/Niche/Script/Video reference
     |
[Niche Research Conference v192 + Production Selection Council v191]
     |
[Structured Evidence Intake + Exact Scope + SHA256 / 120-day freshness]
     |                  |
   Source            Critic viewpoints: Director/Technical/Finance/
   Quality           Copyright/QA/Preschool Curriculum when required
     |                  |
     +--> Multi-hypothesis research question / conflicting evidence veto
                          |
              Priority experiment queue (bounded)
                          |
      Future AUTHORIZED research-agent packet and source retrieval
                          |
              Independent sandbox media benchmark
                          |
       Human/QA/IP signoff + production method proposal
                          |
      Scientific learning: verified regression and multi-project evidence
                          |
        Existing LearningPolicy / release and authority gates
```

## What each component actually does

1. `cinefactory/studio/evidence_reasoning_v193.py`: typed exact-scope research claims. Verified local file paths must be inside repository and SHA256 match actual bytes; stale (>120 days), future, uninspected, missing benchmark, license-not-cleared or scope-changed claims never imply a production-ready method. Opposing supported vs contradicted claims remain `CONFLICT_REQUIRES_TEST`, never resolved by popularity/majority vote. One vendor's documentation is not independent replication. Records have the precise source IDs, original claim IDs and negative controls.
2. `cinefactory/studio/strategic_reasoning_v193.py`: bounded planning for 13 known niches + an unknown-niche discovery fallback. Each task includes 2 competing hypotheses, question, exactly what media artifacts to produce and what uncertainty to resolve; priorities are **heuristics**, not fake posterior probabilities. Conflict issues take priority, child safety and rights are hard blockers. Budget values are carried as constraints; the planner does not pretend missing VRAM/runtime/cost measurements are zero. All tasks `execution_authorized=false`.
3. `cinefactory/studio/scientific_learning_v193.py`: connects controlled A/B experiments to the pre-existing `LearningPolicy`. Causal trials must change exactly one factor; single-project results cannot become all-studio rules. Independent human review, regression, license clearance and real metrics are required. The best possible return is **eligible for review**, never an automatic promotion to production.
4. `cinefactory/studio/reasoning_agent_bridge_v193.py`: creates a bounded, structured packet for a future user-authorized LLM/Codex/research connector. Untrusted scripts and external docs are **data not instructions**. A response validator rejects unknown citations, different tasks/niches, fabricated quality/cost numbers, unsupported claims of independent replication and false execution/rights approvals. No model runs/paid APIs are called by this module.
5. Existing `cinefactory/appctx.py` and `cinefactory/studio/professional_company.py` now expose the shared `strategic_research_reasoner`, `scientific_learning_bridge` and `reasoning_agent_bridge` alongside previous v192 R&D conferences. Current production routes are **unchanged**, no forced runtime integration was claimed.

## Scientific cases actually run

`scripts/verify_strategic_reasoner_v193.py` produced four concrete research-decision outputs:
- `preschool_reasoning.json`: Original 3D music / curriculum / singer / organic rig / original IP; counterhypotheses and separate education, music rights and expert safety reviews.
- `long_slices_reasoning.json`: Physics/game engine readiness and deterministic production; no fake Godot installed/qualified claim.
- `new_unknown_niche_reasoning.json`: Unregistered genre leads to format/source research and tool feasibility discovery, **not** fabricated working production recipe.
- `real_codec_evidence_reasoning.json`: This uses the **genuine measured v192 FFmpeg x264/CRF21/90-frame H264 benchmark** and compares a narrow scoped speed observation. The input JSON is backed by SHA256 `30e3ca9325112b30c1784d4e9301964e3a5843c7acae714870b38a092d14531e`. The fact that one preset was faster on a short clip does **not** prove a superior 4K feature film renderer or artistic quality.
- `scientific_learning_candidate_v193.json`: V190 actor detector recall improved on one existing video over v189. Learning is correctly **blocked from global promotion** (one project, limited annotations, missing independent creative approval/model license).
- `reasoning_summary_v193.json`: the actual 4-case audit, all release gates closed.

`scripts/emit_reasoning_agent_packet_v193.py` additionally emits:
- `external_reasoning_agent_packet_v193.json`: bounded questions/citations, research agent currently disconnected.
- `illustrative_agent_response_v193.json`: static authored *example*, clearly **not the work of an external model**.
- `agent_response_review_v193.json`: schema/citation/authority admission of the example as R&D-only, never execution authorization.

All relative paths under `data/verification/v193_evidence_reasoning/`.

## Intelligent self-criticism policy

Each proposed solution must answer:
1. **Creative Director:** Will it deliver original, audience-relevant storytelling, performance and art? Must compare blind reviewer judgments.
2. **Technical Director:** Can exact version/rig/model/runtime meet locked shot requirements and 12GB VRAM? Must render a reproducible golden shot.
3. **Finance:** Cost per accepted video minute including rejected generations, retries, human time, electricity, storage, licensing and API. Unknown = UNKNOWN, not $0.
4. **IP/Legal:** License of *engine* != licensing of weights, LoRAs, input assets, model/voice training, music and publishing. Must have scope-specific rights.
5. **QA:** Independent holdouts and negative tests for cross-shot character consistency, camera/lighting, audio, children, gameplay/physics and originality.
6. **Preschool Education:** Character IP, original song, appropriate curriculum, safe choreography and Made-for-Kids review. Do not assume copying CoComelon-like artistic expression is permitted.

When two claims conflict, the next action is to **reproduce a controlled A/B**, not choose the nicer-looking result. When the source is old, refresh exact-version docs. When the result only passed one scene, require independent holdouts. A high measured score is never enough by itself to grant automatic production access.

## Verification and limitations

- `tests/test_strategic_reasoning_v193.py` tests deliberate conflicts even with 40 copies of one supporting claim, out-of-scope and forged source hashes, stale docs, uninspected URLs, fake benchmark metrics, claims of AI quality without trials, high VRAM, unconfirmed rights, child-safety review, evidence handoff, learning-generalization and prompt-injection/agent-output guards.
- The production-reasoning API **does not currently invoke an LLM**, connect to YouTube/web/GitHub automatically, watch the reference video or compile a complete video. The real live research/LLM agent requires a separately connected capability. It can then supply source-verified claims and propose experiments; final execution still requires its existing runtime/permission gates.
- Reusable learning still uses the existing `LearningPolicy` and stored evidence; independent reviewer approval cannot be inferred from AI-generated prose.
- Active software, model, and backends remain limited to their **previously verified scopes**. v193 has not claimed that 13 genres are production ready.

## Next implementation milestones

**v1.6.34 — Authorized source/video research adapters:** scoped YouTube metadata/transcripts/reference media extraction, official docs/repo search, model cards/licensing ingestion, content hashes, source recency, prompt-injection firewall, bounded research budgets; no automatic paid API.

**v1.6.35 — Experimental Selection Lab:** same-input cross-engine 15–60s actual media trials for (a) Minecraft/Blender, (b) original Preschool music/character, (c) Long Slice real-time physics or licensed AI footage, with blinded creative QA, compute/cost ledger and verified rights.

**v1.6.36 — Continual production learning:** defect cause analysis + experiments + signed human/QA improvements across 3+ independent projects, rollback and regression. Prevent performance optimizations that degrade artistic quality and prevent quality optimizations with disproportionate cost.

**No Git reset, commit or deployment in this milestone.** The user may explicitly authorize tool installs, connections or production releases in a subsequent step.


## Verified checkpoint — 2026-10-09 (completed)

- **Targeted v1.6.33: 43/43 PASS**, including forged-sources, stale/outside-path SHA, conflicting evidence, 40 copies of one misleading claim, unlicensed tools, preschool safety, unknown niche, bounded planning, unsafe agent responses and excessive generalization.
- **Full CineFactory regression: 842/842 PASS; 0 FAILED**, 138.81 seconds, process exit code 0, on connected Windows machine.
- `python -m compileall -q cinefactory scripts tests`: PASS; tracked diff check PASS (informational Windows LF/CRLF warnings only).
- `data/verification/v193_evidence_reasoning/regression_v193.txt`: complete full regression log.
- `scripts/verify_strategic_reasoner_v193.py` and `scripts/emit_reasoning_agent_packet_v193.py`: 4 real research cases and one *explicitly illustrative* structured LLM handoff reviewed; all remaining non-executable.
- Original v190 detector and v191/v192 company routes preserved. v193 code exists only in the connected machine's dirty working tree; **no commit, stage, clean, reset, tool install, download, paid API, deploy or publication performed**.
- **Important caveat:** 842 tests certify the software contracts/negative controls tested; they do not certify human-equivalent intelligence, autonomous new-source exploration, best production workflow for each niche or finished feature-length video.
