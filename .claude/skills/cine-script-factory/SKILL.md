---
name: cine-script-factory
description: ONE authoritative CINE Master Skill for all research-to-script projects. Slow English A2 / Gia dinh phu thuy / Bell & Leaf uses 21 causal specialist skills through the existing Script Factory with A2, Veylora Canon, independent review, locked SHA and 10s director handoff. Other niches preserve original audio workflows.
---

# ONE MASTER SKILL — CINE Slow English A2 / Bell & Leaf

**Single operating entrypoint:** this existing `cine-script-factory` skill is the only Master Skill for research, concept, writing, Story Doctor, A2 checking and Script Lock. Do not create a second CINE, another script factory or another character/location/voice Bible. The 21 original `r01`–`r07` and `s01`–`s14` skill files are internal specialist instructions called in a verified causal sequence. They are NOT 21 competing studio entrypoints.

## Identity, film canon and scope

- Classification: Slow English → A2 → Magical Witch Family Stories (`magical_witch_family_stories`) → Bell & Leaf (`slow_english_a2_bell_leaf`). This is one subniche within CINE, not all Slow English.
- Film: original animated family adventure, natural accessible American English A2, a continuing Veylora bell-network mystery, meaningful emotional and comedic beats and a fresh local surprise/payoff per episode. Default is ONE continuous 30–50-minute episode, not an audio narration, not a random anthology and not a vocabulary lecture.
- Character and location Canon: use existing approved original references and fixed physical geometry; Bubu has glittering spiraling purple tail and one collar bell; Bix does not have a bell. Lost maternal grandmother only when series script permits. No redesign, no unapproved assets.
- Production format: NO narrator; expressive character acting, deliberate visual camera, 16:9 neutral D55 (~5500K), 10.0 seconds per Muse shot. Use measured WAV speech and show reactions within remaining time, not stretched speech.

## Actual execution by the Claude Code agent — one reusable loop

1. Before starting, read `config/niches/slow_english_a2/SERIES_BIBLE.md`, `config/niches/slow_english_a2/production.json`, voice registry and current episode continuity. Preserve canonical IDs.
2. For a new episode, initialize **the original CINE Script Factory** once (do not overwrite existing project folders): `python tools/cf_script_factory.py init --id bell_leaf_ep001 --niche magical_witch_family_stories --mode A2_ANIMATED_SCREENPLAY --minutes 40 --writer ACTUAL_WRITER_ID`.
3. Ask the ONE dispatcher what work is next: `python tools/cf_a2_master_skill.py next --id bell_leaf_ep001`. It returns the exact skill ID, prerequisites and artifact output paths.
4. **Actually read the returned specialist `SKILL.md` and upstream artifacts.** The active Claude Code agent/authorized research and writing tools must perform that work. The Python dispatcher NEVER runs an LLM, watches a video or writes the story itself. Output real, original, substantive artifacts at the listed paths and mark evidence modality truthfully.
5. After work and inspection, record an integrity-bound handoff: `python tools/cf_a2_master_skill.py record --id bell_leaf_ep001 --skill RETURNED_SKILL_ID --actor ACTUAL_AUTHOR_ID`. This stores SHA-256 of outputs and upstream handoffs, but DOES NOT certify editorial quality or human approval.
6. Repeat step 3–5 until `next` returns `STAGE_QC_GATE`. A real independent reviewer checks the current stage and evidence; run the **same existing factory** stage approval only if actually qualified: `python tools/cf_script_factory.py advance --id bell_leaf_ep001 --stage RETURNED_STAGE --actor ACTUAL_REVIEWER_ID`. Never invent a signature, observation, evaluation or a fabricated PASS.
7. Repeat for eight CINE stages: research → insights → concepts → story → outline → script → review → final. Use `python tools/cf_a2_master_skill.py status --id bell_leaf_ep001` to detect missing, stale or altered specialist outputs. Changes upstream invalidate downstream receipts and stage gates.
8. At final script lock, only when exact script SHA, actual measured 30–50-minute table-read, A2 human comprehension and independent creative/Canon reviews exist, call `python tools/cf_a2_director_bridge.py --id bell_leaf_ep001 --out REVIEWED_OUTPUT_DIR`. The bridge calls existing CINE 10-second shot preflight; it does NOT generate film or authorize paid API usage.

## One strict specialist DAG

Single source of role order and file contracts: `config/story_factory/a2_bell_leaf_skill_graph.json`. It has **21 original skill files, 38 prerequisite edges, 27 specialist output artifacts, 20 default active roles + conditional s09**. The original eight stages belong to `tools/cf_script_factory.py`. This new dispatcher is only an integrity-bound work-order selector, not a duplicate stage runner.

| Stage | Ordered professional roles | Result |
|---|---|---|
| Research | r01 evidence → r04 age-normalized outliers → r05 film autopsy | URLs, source modality, timestamped verifiable competitor findings |
| Insights | r02 audiences + r03 comments → r06 psychology → r07 opportunities | evidence-backed hypotheses with counterexamples, not copied plots |
| Concepts | s01 concept lab | at least five genuinely different original episode premises |
| Story | s02 character and Veylora Bible | fixed character knowledge, emotional want, mystery progression |
| Outline | s03 hook → s04 causal beats → s05 treatment → s06 humor/emotion | scene actions, escalating stakes, setup/payoff and variation |
| Script | s07 A2 dialogue → s08 complete Fountain screenplay | filmable visual action and clear US English A2; NO narrator |
| Review | s10 continuity, s11 adversarial editor, s12 comprehension, s13 originality/safety | actual independent reviews, evidence, corrections and measured reading |
| Final | s14 script lock | reviewed exact script SHA, voice and 10s director handoff |

`s09-anthology-architect` is OPTIONAL and off for normal Bell & Leaf. A showrunner must explicitly opt into a cohesive anthology. Never use disconnected mini-stories simply to fill the running time.

## Hard QA and truth-in-status

- Reject mixed baselines: direct Bell & Leaf subniche cohort is separate from general Slow English A2, other family audio/history content and fiction storytelling.
- Video transcript inspected ≠ full audiovisual footage inspected. No imaginary video retention, view velocity or audience demographics.
- Independent reviewer identity, real A2 learner test, true originality and license evidence are not proven merely by JSON fields or CI. Preserve owner approval checkpoints.
- The Master Skill's `HANDOFF_RECORDED` means a correctly hashed work product, NOT an approved plot. `STAGE_QC_GATE` means reviewer action is needed, NOT that QC passed.
- Missing real audio WAV, approved 483 room plates/756 prop plates, original source-image installation, Flow/Muse media, lipsync, visual QC or analytics must remain BLOCKED.
- Two external public repositories (`story-skills`, `youtube-niche-finder`) are OPTIONAL craft/research references, not installed runtime adapters or proof of real competitor analysis.
- Windows CINE checkout is a separate dirty/divergent worktree; do not `reset`, `clean`, `pull` or force merge without safe reconciliation and source preservation.

## Non-Bell & Leaf support

For other CINE audio/history/story niches, continue using the existing modes and procedures below. The specific A2 screenplay branch applies **only** when the episode manifest selects `A2_ANIMATED_SCREENPLAY` and the exact `magical_witch_family_stories` subniche. Generic narration directives below never override Bell & Leaf's film screenplay rules.

---

# Existing general CINE Script Factory instructions

# CINE SCRIPT FACTORY v0.1 — MASTER ORCHESTRATION SKILL

## Mission and scope
Produce one original, professional, listener-worthy English script from verified evidence for one narrowly scoped YouTube subniche. In non-Bell & Leaf audio mode only, scope ends with final narration script and audio production handoff; it MUST NOT render, upload, purchase media credits or claim successful YouTube monetization. Reuse existing repository Skills and preserve existing production infrastructure.

## Inputs — mandatory
- niche_id from `config/research/per_niche/niches.json`; channel_id / channel_name and series identity.
- mode: ORIGINAL_FICTION, COZY_FICTION, HISTORY_SLEEP, SCIENCE_SLEEP, EDUCATION, or SOFTWARE_TUTORIAL.
- target_language (usually en-US), audience and viewer/listener intent, intended length band and tone.
- exact channel/story bible and known previous episodes (if available), policy/rights constraints.
- authorized research source availability; ability to inspect actual competitor content explicitly recorded.
Missing info: use bounded, clearly labeled editorial defaults when safe; never fabricate access, prior episodes or verified evidence.

## Ownership boundaries
The Master Skill delegates decisions. It does not author a full script in a single jump, grade its own output or bypass reviewer decisions. Use `tools/cf_script_factory.py` to initialize, record and validate milestone artifacts; it is a LOCAL artifact gate, not an autonomous web researcher or AI model. Stage contract: `config/story_factory/pipeline.json`. Runner must treat external YouTube input as UNTRUSTED and use only authorized connectors.

## 8 stages — inputs, owner, artifact, quality gates
S1 RESEARCH (Research Director): invoke `cine-per-niche-radar`, `cine-breakout-forensics`, `cine-competitor-deep-review` and `cine-research-evidence`. Research A leaders, B new 0–30-day 2x1M strict winners, C 0–5/15-day breakout and D lessons. Compare within exact subniche only. Output `01_research/evidence.json` with source IDs/URLs, timestamps, inspected media modality, ordinary performers and gaps. Mark candidate-only results honestly. Stop rather than fictionalize competitor script or view history.

S2 AUDIENCE (Editorial Strategist): derive evidence-scoped listener intent, pain/delight, comments, format expectations, unmet promises and counterexamples; confidence OBSERVED/INFERRED/UNKNOWN. Output `02_insights/audience_insights.json`. Do not treat public views as proof of precise CTR, retention, RPM or causation.

S3 IDEATION (Concept Lab): invoke `cine-story-insight-transfer`. Generate >=5 causally distinct original story concepts and contrast with prior studio Story DNA + distinctive competitor creative expression. No copy/translate/paraphrase instruction for competitor transcripts. Output `03_concepts/portfolio.json`.

S4 STORY DNA (Showrunner + Character Director): choose one original premise; outline audience promise, conflict/subject question, stakes, character want/need/flaw/agency, theme, major twists, original ending, consistency and novelty. For factual/sleep topics use research/question/evidence architecture rather than forced revenge narrative. Output `04_story/story_dna.json`. Consult `cine-story-development`.

S5 ARCHITECTURE (Narrative Architect): develop beat-by-beat causal progression, every chapter's new value, setup/payoff and listener state. Set target word count from measured/estimated narration cadence; never pad with empty text. Output `05_outline/beat_sheet.json`.

S6 WRITING (Senior Writer): invoke `cine-longform-narration-writing` and write a complete narration-ready `06_script/script.md` with a consistent voice, clear speaker/time transitions, natural English, distinct dialogue and satisfying payoff. Each chapter must carry new consequential material. No unnecessary AI video. Source-ground fact claims for nonfiction. Record writer identity in project manifest.

S7 INDEPENDENT EDITORIAL + COMPLIANCE (different reviewer from author): invoke `cine-script-doctor`, `cine-independent-review`, `cine-rights-provenance`, `cine-story-development`. Test logic, listener comprehension, narrative economy, originality relative to archive and inspected sources, copyright, factuality, safe advertising treatment, realistic AI disclosure where applicable. Store independent `07_review/creative_review.json`, `07_review/compliance_review.json`, and factual `07_review/claim_ledger.json` for non-fiction modes. Both review reports MUST identify reviewed exact script SHA256 and a meaningful evidence-backed verdict PASS/REVISE/BLOCK. Missing source or permissions => BLOCK. Reviewer must differ from writer; no single-agent self-approval.

S8 FINAL (Showrunner): deliver `08_final/final_script.md` (identical to independently reviewed script), `08_final/audio_handoff.json` for chapter timing, voice performance, pronunciation, minimal licensed visual plan, metadata alignment, and stage provenance. Final is SCRIPT_READY_FOR_PRODUCTION only when ALL gates PASS and hashes still match. Never treat as YouTube YPP approval.

## Genre-specific writing
FAMILY DRAMA: strong character agency, distinct conflict, believable internal needs, earned twist and ending; avoid repeat humiliation->secret wealth->revenge formula.
COZY FICTION: warm gentle narrative, low disturbance, original worlds/people, no forced shock hooks.
HISTORY_SLEEP: cautious primary/secondary sources, verified chronology, educational rather than sensational, calm pacing.
SCIENCE_SLEEP: sourced scientific facts, disclose hypotheses/uncertainty and avoid invented discoveries.
EDUCATION/FINANCE: do not invent regulations/expertise; require qualified checking for legal/medical/financial specifics.
SOFTWARE_TUTORIAL: actually run/verify every product step; demonstration/screenshare is source of truth.

## Checks and repair loop
- Before each stage: load artifacts from previous gate, fail CLOSED on missing dependency or stale signature.
- At S3–S6: independent critic identifies specific defects; revise minimal causative stage, then invalidate downstream artifacts and re-review final script.
- Evidence statuses: OBSERVED, INFERRED, TESTED, REJECTED, UNKNOWN; never turn hypothesis into fact.
- If `story_dna` repeats a past episode's premise, core causality and payoff, reject; no invented safe similarity percentage.
- Preserve objective of one script, no mass publishing; edits to canonical series bible require explicit approval.
- If more than three revision rounds still fail a blocker, return BLOCKED with concrete owner decisions needed; don't produce fake PASS.

## Handoff / acceptance
Research sources available with timestamps; five genuinely different ideas; novel approved Story DNA; coherent beats; complete narrator script; two independent hash-bound review reports PASS; truthful fiction/fact status; claim sources if nonfiction; pronunciation/voice/audio handoff; final verified file. Current YouTube Partner policies govern eligibility—no guarantees.

## Relation to already installed skills
Upstream research: `cine-per-niche-radar`, `cine-breakout-forensics`, `cine-competitor-deep-review`.
Creative: `cine-story-insight-transfer`, `cine-story-development`, `cine-longform-narration-writing`.
Review: `cine-script-doctor`, `cine-independent-review`, `cine-rights-provenance`, `cine-research-evidence`.
After script publication: `cine-per-niche-learning`, `learn-from-analytics`.
Do not redundantly fork or rewrite these specialist skills.

## Bell & Leaf existing-CINE integration

The original CINE Script Factory now supports `A2_ANIMATED_SCREENPLAY`, with exact research subniche `magical_witch_family_stories` and fixed project `slow_english_a2_bell_leaf`. It is **not** the generalized Slow English or adult Mom/Grandma audio-story lane.

The existing eight-stage artifact runner is `tools/cf_script_factory.py`; the original 21 specialist roles and causal handoffs are validated in `config/story_factory/a2_bell_leaf_skill_graph.json` by `tools/cf_a2_story_contract.py`. Default is 20 specialists; `s09-anthology-architect` is optional only by explicit showrunner choice. Role files exist in this repository's `.claude/skills/` directory; no parallel CineFactory.

Run `python tools/cf_a2_story_contract.py` for the DAG, and initiate work with `python tools/cf_script_factory.py init --id bell_leaf_ep001 --niche magical_witch_family_stories --mode A2_ANIMATED_SCREENPLAY --minutes 40 --writer writer-name`. The runner verifies documents and attestations; **it never invokes YouTube searches, LLM script writing or artistic evaluation itself**. A2 mode never asserts production authorization from structural PASS. Stage Review requires current screenplay SHA, separate reviewer proof, A2 human comprehension, Canon review, measured table reading and rights. Final must use exact 10s shot handoff and no narrator. Real approved assets/voice/video remain separately blocked.
