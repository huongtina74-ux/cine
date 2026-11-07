---
name: cine-bell-leaf-writers-room
description: Source-bound writing and continuity for Slow English A2 / Bell & Leaf only. Use before every new Bell & Leaf episode, treatment, dialogue, trailer, 10-second shot plan, and canon-change request.
---
# CINE Bell & Leaf Writers' Room — required entrypoint

## Mandatory loading order
1. docs/story/bell_leaf/BELL_LEAF_WRITERS_ROOM_CANON_CONTRACT_V1_20261107.md
2. config/niches/slow_english_a2/bell_leaf_writer_contract_v1.json
3. docs/story/bell_leaf/BELL_LEAF_OWNER_SOURCE_CONFLICT_REGISTER_20261107.md
4. docs/story/bell_leaf/BELL_LEAF_WRITERS_ROOM_SOP_V1_20261107.md
5. docs/story/bell_leaf/BELL_LEAF_CANON_CURRENT.md only for nonconflicting additional details.
6. Local OWNER ORIGINALS in data/story/bell_leaf/owner_sources_private/20261107 when authorized, including PRIVATE showrunner dossier; NEVER copy them to public GitHub or prompt vendors. If missing, report unverified private access, do not invent.

## Non-negotiable
Niche=slow_english_a2, series=bell_leaf; NO borrowing generic slow-A2 or audio-niche canon. The user's four source documents are immutable. NO autonomous changes to the story base, magical world rules, cast roles or hidden adversary. New episodes must be original inside those boundaries. Any conflict or unclear reveal -> OWNER_DECISION_REQUIRED. Keep current script scope distinct from the owner-approved reference art and voice registry.
- Mara family travels BOTH old and new worlds, plus standalone Earth stories. Orin usually old worlds, rarely onscreen. Trial mix 35 OLD / 30 NEW / 25 EARTH / 10 MIXED, never a hard quota.
- Veylora ecological decline precedes deliberate disaster. Earth was UNMAPPED; no ancient station, only rebuilt later. Affinity and magic renewal differ.
- Fixed gate STATIONS for verified known worlds; Bubu one collar bell only echo-triggered temporary unknown passage and constrained Earth home anchor; no teleport on demand.
- Bubu purple SPIRAL SPARKLE tail all times; Bix NO BELL; 9 original core identity tags plus Elara as supported asset. Juno boy 13, Lia girl 11.
- Keep masked opponent's real identity and plan confidential; do not expose in public scripts, GitHub or external provider prompts.
- Every 40–50m screenplay requires local satisfying resolution, enduring consequences, real physical logic, A2-natural dialogue, camera/action planning. Prompt output: one continuous line per 10s shot, exactly one blank line between shots, ACTIVE TAGS FOR THIS SHOT: [..], 16:9 neutral daylight D55, no grids/captions.
- Do not claim script completed from treatment, voices approved from candidate WAV, identity passed from PNG SHA, or animation passed from synthetic FFmpeg.

## Work product
For every draft, output: EP ID + premise, 46-minute optional beat plan, character POV and emotional conflict, locations/gates & cause, research trace, scene-by-scene A2 screenplay, physical and clue continuity ledger, per-shot tags, blockers and approvals. Use labels SOURCE_LOCKED, PROPOSED, CONTINUITY_PENDING, STORY_REVIEW_REQUIRED, ASSET_BLOCKED, PRIVATE_REVEAL_RESTRICTED, RELEASE_HOLD.
Use Change Request under SOP section G when user explicitly requests an edit; quote current source, show minimal delta, update dependencies only after user approval. Stop before any publishing or signed approvals.

## Minimum self-test
Run python -m pytest -q tests/test_bell_leaf_writer_contract_20261107.py before handoff; resolve failed invariant rather than claiming PASS.

## Mandatory pre-draft and pre-lock narrative uniqueness gate (2026-11-07)
- The 1,000-row index in docs/story/bell_leaf/slates and complete UNAPPROVED development slate are proposal backlogs, not 1,000 approved screenplays.
- BEFORE drafting, run: python tools/bell_leaf/episode_uniqueness_gate.py audit --out data/story/bell_leaf/episode_novelty_audit.json. The baseline is EXPECTED to say REVIEW_REQUIRED because templates repeat.
- For each new episode pitch, supply episode_id,title,lead,setting_class,hook,goal,conflict,twist,resolution,continuity_delta in a JSON file. Run: python tools/bell_leaf/episode_uniqueness_gate.py check --candidate PATH_TO_PITCH.json --out data/story/bell_leaf/PITCH_NOVELTY_RECEIPT.json
- BLOCKED or missing 1000 baseline HALTS the writing and s14 lock. MANUAL_NOVELTY_REVIEW_REQUIRED is not an approval; editor checks motive, scene sequence, payoff, dialogue, last 20 approved episodes, and original source research.
- NO_AUTOMATIC_APPROVAL: this lexical gate cannot prove semantic originality or rights. Direct-cohort competitor research receipts with URL/date/AV method and independent editorial signoff are required before approval. Missing evidence = RESEARCH_NOT_VERIFIED.
- AFTER the full screenplay is written, rerun on its extracted premise/payoff and record linked episode IDs and continuity consequences in the editorial ledger. Do not confuse proposed 1000 titles with approved stories.
