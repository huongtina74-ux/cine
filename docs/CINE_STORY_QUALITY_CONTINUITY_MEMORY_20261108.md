# CINE — PROFESSIONAL LONG-FORM STORY ROOM & EPISODE MEMORY v1 (2026-11-08)

Scope: all TEN registered research/script niches, each with its own creative profile, sources and approved-episode memory. Existing CINE Script Factory is upgraded, NOT replaced. The four original Bell & Leaf owner source texts and character faces/portal rules are unchanged. Every automatic result requires human creative review: no code or AI can guarantee zero repetition or that a story is engaging.

## Two different archives, never conflate them
- DEVELOPMENT PROPOSALS: brainstorms, rejected premises and drafts. Bell & Leaf's 1,000-card slate contains repeated boilerplate and was explicitly never approved as 1,000 full screenplays.
- APPROVED EPISODE MEMORY: append-only private local JSONL at data/story_quality/{niche_id}/{series_id}/approved_episodes.jsonl; entries include EP ID, plan/review hashes, reviewer/owner references, seven-axis premise fingerprint, seed signature and recorded continuity state changes. User sources/private showrunner remain Git-ignored. GitHub contains the code and authoring rules, not fabricated editorial approvals.

## Existing company pipeline upgraded
1. IDENTITY/FORMAT: select exact research niche_id, series_id and allowed script-factory mode. Bell & Leaf is magical_witch_family_stories / bell_leaf; generic A2, family audio, history, finance and science are separate. New project can bind --episode-id.
2. RESEARCH: collect and cite real direct-cohort competitor URLs, video/channel IDs, observation dates, inspected modality/timecodes, source reliability. Learn abstract hook/structure craft rather than competitor plots.
3. CREATIVE DIRECTIONS: generate 12 diverse development seeds for THIS episode or season slot, not mass-generated finished stories. Expand 3 genuinely different premises, choose original family/emotional and physical conflict.
4. NOVELTY: compare title, hook, objective, central conflict, twist, resolution, character emotion and lasting consequence to ALL previously approved episodes; Bell & Leaf additionally checks 1,000 unapproved proposed cards.
5. CHARACTER: make POV, initial belief, internal need, irreversible choice and changed final state specific. No all-knowing convenient hero or passive family.
6. CAUSAL BEATS: 12+ substantial beat records with earlier cause ID, physical observable action, obstacle, character choice, clear because and immediate consequence. No magical deus ex machina.
7. SCENE ARCHITECTURE: for 45 minutes, 18+ independent scene cards with ID, beat link, exact sequential start/end timestamps, location, scene purpose, visible character action and new knowledge/state. Long nonfiction episodes use evidence/questions, not fictionalized facts.
8. SETUP/PAYOFF: at least 3 real clues seeded BEFORE payoff, and solution is earned. Twist unrelated to preceding scenes is BLOCKED.
9. CONTINUITY: at least 2 real state changes (object, person, relationship, gate, community, knowledge, timeline) each linked to an actual beat; track unresolved threads, previous rescues and other world rules.
10. SCREENPLAY: new Script Factory projects must supply 05_outline/episode_quality_plan.json and at the script stage a substantive 06_script/script.md with beat IDs, scene IDs, a minimum text depth proportional to duration, and no repeated dialogue/scene templates.
11. INDEPENDENT STORY DOCTOR: provide 07_review/story_quality_review.json with exact current screenplay SHA256, reviewer different from writer, 3+ evidence notes and seven PASS checklist keys: causality, character_agency, setup_payoff, originality, continuity, distinct_emotional_resolution, niche_fit. Review identity cannot be authenticated by a text string alone.
12. OWNER APPROVAL / MEMORY: only after genuine owner and editor signoff explicitly register into append-only approved memory with SHA-matched plan, separately approved memory receipt and review evidence file. Register refuses duplicate ID or prior matching narrative premise. Never equate story PASS with production or YouTube monetization permission.

## Executable commands from CINE root
Generate 12 prompt directions for planned Bell & Leaf EP315 (no automatic screenplay):
    python tools/cf_story_quality_gate.py ideas --niche magical_witch_family_stories --series bell_leaf --slot BL-0315 --count 12 --out data/story_quality/brainstorm_BL-0315.json

Initialize existing CINE Script Factory, with bound episode ID:
    python tools/cf_script_factory.py init --id bell_leaf_ep0315 --niche magical_witch_family_stories --mode A2_ANIMATED_SCREENPLAY --minutes 45 --episode-id BL-0315 --writer actual_writer_id

Follow all existing research/insights/concepts/story prerequisites. At outline stage, create project/05_outline/episode_quality_plan.json: episode_id,niche_id,series_id,target_minutes,story(12 detailed fields),beats,scenes,setup_payoffs,character_arcs,continuity_deltas,creative_axes,editorial_questions, and for Bell & Leaf verified owner Canon metadata/tags. The exact object fields are tested in tests/test_cf_story_quality_gate_20261108.py.

    python tools/cf_story_quality_gate.py check --plan data/script_factory/projects/bell_leaf_ep0315/05_outline/episode_quality_plan.json --out data/story_quality/bl0315_preflight.json
    python tools/cf_script_factory.py advance --id bell_leaf_ep0315 --stage outline --actor actual_editor_id

After writing actual scripts, run normal script, review, final stages. The structure and hashes are rechecked at each downstream stage. ONLY after authorized independent editorial/owner signoff:
    python tools/cf_story_quality_gate.py register --plan PATH/episode_quality_plan.json --review PATH/human_approved_memory_receipt.json

Memory receipt requirements are DIFFERENT from the factory story_quality_review: plan SHA256, reviewer_id distinct from author_id, verdict PASS, 3 evidence notes, owner_approval_reference, evidence_file and evidence_sha256. CLI verifies fields/hashes, not real-world identities; approved records are only as trustworthy as actual authorized human signoff.

## Required specific checks for Bell & Leaf
- Canon identity 4 user-supplied originals locked; no retcon or actor redesign. Nine original main identities plus Elara support. Bix no bell; Bubu has exactly one gold collar bell and permanent spiral sparkling purple tail.
- Known OLD mapped-world travel uses verified repaired fixed bell station. Unknown NEW-world travel uses a specific Bubu echo and has limited return safety; Earth was initially unmapped, Earth renewal is gradual and limited.
- Family Mara can visit both OLD and NEW worlds plus Earth; Orin usually handles old routes and only occasionally appears physically. New/old/Earth/mixed 30/35/25/10 are planning proportions, never force stories to meet a quota.
- Secret antagonist Showrunner material never enters GitHub, public prompts, independent idea seed or user-facing novel-idea reports.
- No claim that 270 ten-second shots, lip-sync/voice, source art or actual episode video were completed merely because an outline passed story checks.

## Limits, no false assurances
These are deterministic STRUCTURAL and LEXICAL controls. Changing names and rewording can still fool similarity checks; they do not establish originality, copyright eligibility, human writing quality, actual English A2 comprehension or YouTube YPP acceptance. Human editor reviews full scenes, dialogue and semantic sameness. An unapproved proposal pool or corrupted approved-episode ledger fails closed. Existing pre-upgrade Script Factory projects are labeled LEGACY_PROJECT_UNVERIFIED and not silently upgraded; do not reset any dirty Windows worktrees to apply changes. Partial package routing in CINE research remains separately reported, not marked ready.

Tests:
    python -m pytest -q -p no:cacheprovider tests/test_cf_story_quality_gate_20261108.py
