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

**Windows runtime now available (verified 2026-10-30):** For a Bell & Leaf episode already initialized in the existing CINE data/script_factory/projects folder, run `python tools/cf_a2_claude_agent.py --id EPISODE_ID --execute --actor claude-code-sonnet`. This program asks the ONE Master dispatcher for the next skill, sends only that skill, its upstream artifacts and canonical context to authenticated Claude Code using stdin with NO Claude filesystem tools, validates exact output paths/source URLs, writes only the allowed episode artifacts and creates SHA-bound handoff receipts. Without `--execute`, it only prepares the prompt. Do not use Claude's unrestricted repository editing permissions. **R01 requires real dated sources at `01_research/input_sources.json`.** A completed role handoff does NOT authorize human editorial approval, direct-peer claims, paid media generation, or publishing. Read `config/niches/slow_english_a2/LOCAL_WINDOWS_RUNBOOK.md` for the exact operational procedure.

1. Before starting, read `config/niches/slow_english_a2/SERIES_BIBLE.md`, `config/niches/slow_english_a2/production.json`, voice registry and current episode continuity. Preserve canonical IDs.
2. For a new episode, initialize **the original CINE Script Factory** once (do not overwrite existing project folders): `python tools/cf_script_factory.py init --id bell_leaf_ep001 --niche magical_witch_family_stories --mode A2_ANIMATED_SCREENPLAY --minutes 40 --writer ACTUAL_WRITER_ID`.
3. Ask the ONE dispatcher what work is next: `python tools/cf_a2_master_skill.py next --id bell_leaf_ep001`. It returns the exact skill ID, prerequisites and artifact output paths.
4. **Actually read the returned specialist `SKILL.md` and upstream artifacts.** The active Claude Code agent/authorized research and writing tools must perform that work. The Python dispatcher NEVER runs an LLM, watches a video or writes the story itself. Output real, original, substantive artifacts at the listed paths and mark evidence modality truthfully.
5. After work and inspection, record an integrity-bound handoff: `python tools/cf_a2_master_skill.py record --id bell_leaf_ep001 --skill RETURNED_SKILL_ID --actor ACTUAL_AUTHOR_ID`. This stores SHA-256 of outputs and upstream handoffs, but DOES NOT certify editorial quality or human approval.
6. Repeat step 3–5 until `next` returns `STAGE_QC_GATE`. A real independent reviewer checks the current stage and evidence; run the **same existing factory** stage approval only if actually qualified: `python tools/cf_script_factory.py advance --id bell_leaf_ep001 --stage RETURNED_STAGE --actor ACTUAL_REVIEWER_ID`. Never invent a signature, observation, evaluation or a fabricated PASS.
7. Repeat for eight CINE stages: research → insights → concepts → story → outline → script → review → final. Use `python tools/cf_a2_master_skill.py status --id bell_leaf_ep001` to detect missing, stale or altered specialist outputs. Changes upstream invalidate downstream receipts and stage gates.
8. At final script lock, only when exact script SHA, actual measured 30–50-minute table-read, A2 human comprehension and independent creative/Canon reviews exist, call `python tools/cf_a2_director_bridge.py --id bell_leaf_ep001 --out REVIEWED_OUTPUT_DIR`. The bridge calls existing CINE 10-second shot preflight; it does NOT generate film or authorize paid API usage.

## Evidence-quality and stage-assembly gates (CINE Windows, 2026-11-02)

A SHA-locked specialist receipt is NOT proof of successful research. The deterministic Master dispatcher now exposes three separate states. If `next` returns `BLOCKED_RESEARCH_QUALITY`, stop the writing pipeline: source cohort/method/modality, original R01 register, R04 outlier URLs, R05 actual AV/timestamp analysis, and `evidence.json` must be independently checked and corrected; rerun affected roles before stage approval. Historical metadata-only Slow English videos MUST NOT be relabeled direct magical-family peers, or used as evidence of audience retention and story beats. Use `python tools/cf_a2_research_quality.py --project-dir data/script_factory/projects/EPISODE_ID` for explicit defects. A source's claim to be video-reviewed still needs independent human/media evidence.

If `next` returns `STAGE_ASSEMBLY_REQUIRED`, the 21 specialized outputs do not cover all eight Script Factory stage artifacts. Create the exact returned missing files using *actual source-backed professional synthesis* of the prior skill outputs, not placeholders or copy/paste fiction. The existing factory expects an additional 14 outputs across Research/Insights/Concepts/Story/Outline/Script/Review/Final; five review outputs may require genuine independent reviewer/timing work. Never let the same author fabricate both an A2 screenplay and a human review signature. Only `STAGE_QC_GATE` means documents can be presented for review, not that they have passed.

`writer_executor_v1.py` and `script_factory_bridge.py` remain **audio_storytelling_seniors** modules (podcast only), not Bell & Leaf A2 film adapters. Do not use or connect those audio-first programs to this series. External Story Skills excerpts are optional writing techniques; the 21-role DAG and Bell & Leaf Series Bible stay authoritative.

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

## 2026-11-08: Story Quality and Approved-Episode Memory (existing Script Factory integration)
Mandatory before authoring any NEW episode in ANY CINE research niche: read docs/CINE_STORY_QUALITY_CONTINUITY_MEMORY_20261108.md and the cine-story-quality-memory specialist instruction. This is NOT a second Master Skill.
On init, record exact niche, mode, series and --episode-id; do not import another niche's format or creative DNA. New projects require the separate 05_outline/episode_quality_plan.json and 07_review/story_quality_review.json. The real tools/cf_script_factory.py checks them during advance/status, not merely an agent promise.
Showrunner and Outline team MUST write at least twelve distinctly causal beats, timed scenes for full runtime, three prior-seeded payoffs, a character decision arc and two real continuing-state changes. Bell & Leaf retains exactly the owner's four locked sources; never expose hidden showrunner identity or redesign original faces.
Run python tools/cf_story_quality_gate.py ideas --niche magical_witch_family_stories --series bell_leaf --slot BL-0315 --count 12 for truly different seed combinations across episode IDs; these are NOT full scripts. Run python tools/cf_story_quality_gate.py check --plan PATH_TO_EPISODE_QUALITY_PLAN.json before outline stage advancement, fixing all BLOCKED errors.
After complete screenplay, the Editor checks actual scene/beat traces, distinct dialogue/action, revised character state, fair-play clues, past approved episode memory and specific similarities to the unapproved 1000 Bell & Leaf cards. The independent story review must quote current script SHA and record seven checklist verdicts with three real notes. A PASS code is only structural and NEVER owner/YouTube approval.
Do NOT run memory register automatically. The manual append-only approved-episode ledger is only for genuinely owner-reviewed episodes. Legacy project without story_quality_contract_version=1 remains LEGACY_PROJECT_UNVERIFIED, not claimed to meet the upgraded standard. Existing senior audio modes remain separate and follow their own registered quality profile.

## Read-only LEGACY Script Factory archive — previous scripts do not disappear
- NEW: tools/cf_story_archive_scan.py scans data/script_factory/projects/*/manifest.json for the selected *exact* niche_id. It discovers old story DNA/beat sheets and full script/final Markdown even if they were written before the new episode memory ledger existed. It NEVER upgrades old stage attestations into true human approval and it never publishes or writes historic scripts to GitHub.
- Inventory CLI: python tools/cf_story_archive_scan.py --niche mom_grandma_family_original --out data/story_quality/legacy_mom_grandma_inventory.json. Run separately for magical_witch_family_stories, audio and other registered niches. No cross-niche borrowing or comparison.
- New outline quality preflight compares the current 7-axis premise/goal/conflict/twist/payoff against prior same-niche historic story DNA as well as the new approved ledger. Substantively copied conflict+resolution => BLOCKED. Historical project record malformed or cross-niche => BLOCKED. Missing archive => explicit warning, not false assurance.
- New script/review/final stage checks copy across the actual prior same-niche screenplay using 7-word overlap shingles. Strong overlap => BLOCKED; moderate overlap demands reviewed_historical_project_ids in the separate editorial review receipt, but a textual acknowledgement cannot prove genuine editor identity.
- Legacy archive SHA changes are signaled; these scripts remain comparisons even when their original stage hashes are stale. Only an actual owner-approved human review can register a new record in the append-only approved ledger.
- **Real local audit as-of 2026-11-08:** 3 Script Factory projects found; Mom/Grandma had one complete historical script and one empty pilot, Bell & Leaf had one initialized pilot but no completed full screenplay in that folder. Other files/episodes outside Script Factory may exist and are NOT covered until indexed. The new memory ledger was empty before onboarding. Hence NO claim of 1,000 unique finished episodes.


## Owner visual source package 2026-11-08: mandatory for Bell & Leaf (EP001–EP1000+)

Owner provided 23 reference PNGs in Windows folder SLOW NGLISH PHÙ THUỶ. Consult docs/story/bell_leaf/OWNER_VISUAL_REFERENCE_HANDOFF_20261108.md, config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json and the existing character source lock at config/niches/slow_english_a2/CHARACTER_VISUAL_CANON_LOCK_CURRENT.json before every shot. Do NOT change names, faces, clothing identity, prop shape or locked house appearance.

Official existing CINE location registry .claude/skills/cine-a2-muse-reference-anchoring/integration/config/LOCATION_CURRENT.json now includes owner_source_anchors_20261108 on nine existing BELL rooms, but the multi-view approval_state is still PENDING_NOT_GENERATED. All original one-angle plates and 3 concept boards are inspectable at assets/canon/location_refs/slow_english_a2/bell_leaf/owner_provided_20261108. The 3 collages have alternative façades; never use as production geometry or single independent 16:9 shot images. A huge central bell hall is NOT yet verified as Earth's private newly built fixed station. True camera reverses, night angles, room adjacencies and props still require independent approval.

EP001 reference file docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json has 270 S001–S270 rows; each row gives location anchor path/SHA if supplied, candidate visible character refs and explicit active tags. Shot cast tags are inferred from the screenplay and MUST be human director-verified. Offscreen actors must not receive face refs. AILA has NO owner-approved face: do not invent it. No media upload IDs or video QC PASS have been fabricated. Provider upload and independent image/video validation remain required for each generated shot.

Run python tools/bell_leaf/inspect_visual_reference_20261108.py --require-assets --shot S001 before an EP001 production test; if owner binary assets are absent or SHA mismatches, BLOCK. Native 16:9 one frame, neutral D55 daylight, no subtitles or 9-grid, 10s take with acting/lip-sync, Bix without bell, Bubu with one gold neck bell and permanently sparkling purple spiral tail.

## Bell & Leaf Muse 3D animation drift prevention (2026-11-08)

For the exact niche slow_english_a2 / magical_witch_family_stories / bell_leaf ONLY, read docs/story/bell_leaf/MUSE_I2V_PROVIDER_STYLE_CONTINUITY_20261108.md and config/niches/slow_english_a2/i2v_provider_contracts_20261108.json. "Muse" alone does not identify a provider: Meta Muse Video, Fawna Muse and unrelated websites cannot be treated as one model. No remote model/paid generation has been verified or authorized. Before I2V, call tools/bell_leaf/muse_i2v_preflight.py for the exact EP001 shot and first-frame. For 10s video inspection call tools/bell_leaf/muse_i2v_frame_qc.py, which produces only human-review PENDING screenshots at 0/2/5/8/9.7 seconds. Require source face SHA, one standalone approved 16:9 CGI first frame, exact on-screen cast, approved site/space and camera topology, explicit account/model and provider receipt. Never use a 9-grid as the rendered scene frame, even if a third-party model suggests it as a composite identity input. Voice comes from approved fixed WAV, not a VOICE_NAME prompt. Failure on ANY real-human recast, altered Bubu spiral sparkle/one neck bell, Bix added bell, wrong stage geometry or camera-only zoom is a hard rejection. The unrelated generic character examples Mia, Grandpa Walter, Biscuit must never enter the Bell & Leaf prompts. This contract does not modify other CINE subniches or grant production PASS.

## Mandatory Bell & Leaf 3D Prompt Director (2026-11-08)

For magical_witch_family_stories/Bell & Leaf (NOT unrelated generic Slow English/audio), load .claude/skills/cine-bell-leaf-stylized-3d-prompt-director/SKILL.md BEFORE preparing any image or Muse 10-second video prompt. Production prompt compiler: tools/bell_leaf/compile_3d_animation_prompts.py; canonical style/format contract: config/niches/slow_english_a2/stylized_3d_prompt_contract_v1.json. Image must be one independent 16:9 scene with SHA-verified owner face/hero and correct owner location plate; video must animate that approved first-frame with one purposeful 0-2/2-7/7-10s acting arc and genuine moving character (not camera zoom). Cast visible in one shot ONLY, voice-only character references excluded, BIX no bell, BUBU exactly one gold collar bell and continuous sparkling spiral purple tail, no live-action recast or legacy Mia/Walter/Biscuit. Output separate image and video TXT with exactly one prompt line, one blank line between shots. A prompt template or SHA does not authorize I2V: missing angles, Aila face, authorized provider or human visual/voice QC remain BLOCKED.

## Bell & Leaf Memory Hub — mandatory source bootstrap (2026-11-08)

For the exact \`bell_leaf / magical_witch_family_stories\` series, load \`.claude/skills/cine-bell-leaf-memory-hub/SKILL.md\` and **run** \`python tools/bell_leaf/story_memory_resolver.py --episode BL-0001 --stage story --out data/story_quality/<unique>.json\` before writing, reviewing or changing any new scene. For artwork/shot prompts run the same tool with \`--stage image --shot S001\` (or \`video\`) and load ONLY that shot's active face/body and location references. For EP002+ use \`--stage next --episode BL-0002\` first, then story-uniqueness gates. This integrates existing source-of-truth owner Canon, prior episode states, used plot events, Skills, character and location imagery by source/hash; do **not** duplicate their rules or treat historical v1.1 270-shot draft as v2 production script. Story, character face, location reverse angle and video QC approvals remain separate and not automatic. Missing source or conflicting state is BLOCKED.

## Required first-15-second hook for EVERY Bell & Leaf episode (2026-11-09)
The 0-10 second opening shot S001 MUST create a TRUE, clearly visible, episode-specific question or tension. The next 10-second shot S002 MUST connect or reinforce it by 15s. Keep every Muse source shot at exactly 10.0s (24fps/240 frames): NEVER generate a 15s shot to implement the 15s hook. No long logo/recap first, fake drama, fabricated stakes, rapid A2 exposition or automatic claim of audience retention. Vary genre: mystery, heartfelt decision, comedy trouble, urgent problem, visual surprise or disaster when truly justified. Do not re-use the Veylora disaster intro on future episodes. For EP001: S001 previews the real past Veylora event with only Mara and Orin; S002 cuts to the present Earth kitchen as Bix makes an ordinary two-note cup sound and Mara freezes. The past event is fully explained later at SC-006. No Evan, Juno, Lia, Bix, Bubu or Earth grandparents can appear in the historic teaser. No masked villain reveal. The Veylora station location plate is NOT approved; block final images. Require opening_hook in story plan, run tools/bell_leaf/opening_hook_gate.py and tools/cf_story_quality_gate.py check. A structural PASS requires separate human story/art review and real first-30s audience retention after publication.
