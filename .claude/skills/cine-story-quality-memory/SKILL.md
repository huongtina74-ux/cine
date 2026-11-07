---
name: cine-story-quality-memory
description: Mandatory causal plot, originality, scene detail, character agency, continuity-memory and editor-review gate for every new CINE Script Factory episode across registered niches. Protect Bell & Leaf owner Canon.
---
# CINE Story Room — Professional Original Episode Quality Gate

Before every new story, screenplay or script-lock, read docs/CINE_STORY_QUALITY_CONTINUITY_MEMORY_20261108.md and config/story_factory/story_quality_profiles_v1.json. Select exact niche and project/series_id. This is an extension of the existing CINE Script Factory, not a new pipeline or a second registry.

## Script author responsibilities
1. Read research briefs with provenance for THIS niche and available history of approved episodes. Competitor analysis informs abstract techniques only, not plots or dialogue.
2. Use tools/cf_story_quality_gate.py ideas --niche NICHE --series SERIES --slot EPISODE_ID --count 12. These are SEEDS, NOT finished scripts or approved episodes. Expand at least three different premises and check the 1000 Bell & Leaf proposals when applicable.
3. Pick a character-specific goal, internal need, obstacle, meaningful personal price and final changed state. Build a local story with earned payoff and enough genuine differences to justify its own episode.
4. Author a comprehensive episode quality plan: 12+ causally linked beats; 18+ timed scenes for a 45-minute episode (format-adaptive for other niche durations); 3 planted/payoff clues; 2+ lasting continuity deltas; distinct character arc, 3 different creative axes and 3 adversarial editorial questions.
5. For Bell & Leaf, preserve FOUR_OWNER_TEXTS_20261107, owner-uploaded character identities, two bell mechanisms, Earth renewal constraints and family-first adventures. Never promote private Showrunner antagonist revelations into public creative packets.
6. Run tools/cf_story_quality_gate.py check --plan PATH_TO_QUALITY_PLAN.json and fix BLOCKED. Independent editorial review is ALWAYS required even after no structural errors. Compare the full story to previous scripts, not just matching titles or keywords.
7. Let existing tools/cf_script_factory.py advance validate outline, script and review/final. New project manifests require the plan at 05_outline/episode_quality_plan.json and story_quality_review.json with current script SHA and independent editor evidence at 07_review/.
8. Do not claim a treatment (or 1000 ideas) is a complete 45-minute screenplay. Script must trace actual scene and beat IDs, have sufficient unique story/dialogue development and no repeated template passages.
9. Only after real owner/editor signoff explicitly record a memory receipt via tools/cf_story_quality_gate.py register, append-only in data/story_quality/NICHE/SERIES/approved_episodes.jsonl. Never forge an approval to unblock another stage.
10. Keep final production approvals separate: art face master, voice WAVs, Muse I2V & lip-sync, rights, YouTube audience/synthetic disclosures and monetization assessment.

## Triggers to stop (not auto-resolve)
Causal plot hole, unseeded twist, incoherent scene timestamps, duplicate conflict+resolution, wrong niche/mode, repeated beat or screenplay lines, Bell & Leaf canon mutation, missing prior-state consequences, invalid reviewer, missing source evidence, corrupt approved ledger. Ask for human editorial/owner decision where genuinely needed; never silently retcon protected facts.

## Acceptance
Run python -m pytest -q -p no:cacheprovider tests/test_cf_story_quality_gate_20261108.py. Structural PASS is NOT artistic, semantic originality, or YouTube YPP approval. Continue original screenplay creation only after a real writer/editor has independently reviewed the generated evidence.
