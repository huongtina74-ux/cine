# Bell & Leaf A2 — Existing CINE Research → Screenplay Connection

Hierarchy: **CINE → Slow English → A2 → Magical Witch Family Stories → Bell & Leaf**. This is a **subniche** in the existing CineFactory, not a new factory/project.

The Windows Script Room original has **21** specialists. All have now been imported into the same existing GitHub CINE `.claude/skills` namespace, retaining their individual method and input/output contracts. Their **38 dependency links and 27 output files** are validated by `config/story_factory/a2_bell_leaf_skill_graph.json`.

## One eight-stage Company Script Factory, not a second engine

| Existing stage | Skills, causal order | Verified artifact boundary |
|---|---|---|
| research | r01 → r04 → r05 | URL and date-backed sources, peer-cohort outliers, transcript/AV coverage labeling |
| insights | r02, r03 → r06 → r07 | Audience hypothesis, coded comments, psychology and opportunities |
| concepts | s01 | Five materially different original concepts |
| story | s02 | Approved Bell & Leaf Story DNA, character knowledge and Veylora arc; never redesign visual canon |
| outline | s03 → s04 → s05 → s06; s09 **optional** | Character-specific hook, BUT/THEREFORE beats, treatment and emotions |
| script | s07 → s08 | Natural A2 dialogue and complete Fountain screenplay, not an audio narration script |
| review | s10, s11, s12, s13 | Continuity, independent story doctor, comprehension and original/safety review |
| final | s14 | Script SHA lock, voice and 10-second shot handoff, not finished video |

Note: **s03 must follow s02** because the hook depends on the established character and world. **s09 anthology** is disabled by default; Bell & Leaf is a continuous magical family adventure with Veylora progression. Other Slow English audio/animation series remain in separate niches and should not inherit these character/genre rules.

Actual software entry points: `tools/cf_script_factory.py` (existing deterministic 8-stage runner ported from owner's Windows checkout), `tools/cf_a2_story_contract.py` (CINE source evidence, 21-role DAG and A2-specific quality), `scripts/slow_english_a2_preflight.py` (approved script/shot Canon routing). The production code and models remain separate.

**Truthful status:** The 21 skills are instructions; no automatic skill execution or multimodal study of competitor videos is proven. The Python gates inspect artifacts, SHA and declared reviewer evidence; they cannot prove the human truly approved content by themselves. A2 mode reports `production_authorized: false`. The dirty Windows checkout with separate Git history remains untouched; GitHub integration is NOT Windows rollout.

Daily radar public sources require exact `magical_witch_family_stories` cohort. Broad `slow_english_a2_story` exists only as the adjacent parent market. Never merge audiences, outlier denominators, video age, or content baselines.

## Final Script Lock → existing CINE Shot Director (safe bridge)

Once the CINE eight-stage Script Factory reports ALL structural stage gates PASS and an actual independent showrunner has validated creative approvals, a project may supply `08_final/shot_handoff.json` with exact current `script_sha256`, exact `shots_sha256`, `shots_file` as a relative project path, `shot_count`, `project_id=slow_english_a2_bell_leaf`, `subniche_id=magical_witch_family_stories`, `shot_duration_seconds=10`, `narrator_allowed=false`.

Command: `python tools/cf_a2_director_bridge.py --id bell_leaf_ep001 --out <your-approved-preview-output>`.

The bridge checks eight-stage Script Factory hashes/attestations, verifies the shot map hash and 10s rule, then uses the existing `scripts/slow_english_a2_preflight.py` and its original CINE Canon resolver. It writes Flow/Muse one-line prompts and a blocking QC report, never consumes metered media credits or marks a movie produced. Because current image/voice source approvals are missing, video production remains blocked.

Optional outside repositories are documented in `config/story_factory/a2_bell_leaf_external_skill_sources.json`: Story Skills and youtube-niche-finder are MIT read-only references observed on Windows, NOT runtime dependencies; their code and skills have not been installed in the CINE Python service. Neither repo authorizes copying competitor scripts or results in confirmed audiovisual reviews.
