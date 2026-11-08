---
name: cine-audio-three-branch-orchestrator
description: Route CINE's three Audio-first niche projects to the existing Afanta production QC pipeline using canonical, drift-checked rules.
---

# CINE Audio — thin orchestrator, not another rulebook

**AUDIO_AUTHORITY_INDEX_REF:** `config/audio/authority_index_v1.json` (CINE, sole ownership index).

Before acting, read the canonical CINE `config/audio/branch_registry_v1.json` for strategy and the relevant CINE canonical research/story sources named in the index. Read Afanta `studio_os/docs/AUDIO_QC_CANON_V1.md` and its canonical risk/QC code for production. Never duplicate thresholds, channel plans, copyright rules or technical QC policy here.

## Dispatch (workflow references, not a second set of rules)

1. From the CINE repository, run `python tools/cf_audio_branches.py audit` and `python tools/cf_audio_authority.py audit`. If the authority check says HOLD, **do not dispatch a production-ready assignment**.
2. Use CINE's actual, source-verified research, audience and story-development contracts. Retain accurate URLs, source dates, actual video modality, provenance and creative decisions. Research/craft documents do not constitute signed Afanta release evidence.
3. Select the exact CINE branch ID from the registry; never mix channel audience, competitor baseline, stories, or voice/canon between branches. The Afanta target slug/niche comes only from that registry, never a hardcoded copy in this skill.
4. CINE owns the source cohort. Create an unapproved handoff template with `python tools/cf_audio_handoff.py template --slug ACTUAL_PROJECT`; use the exact CINE branch/slug in the registry. Populate the existing CINE-owned verified_audio_cohort.json using genuinely inspected, source-grounded audio-first observations, and the independent research evidence file. A human reviewer signs off the specific source SHA and manifest. Run `python tools/cf_audio_handoff.py check --slug ACTUAL_PROJECT`. Only after its read-only gate passes may Afanta ingest this **exact source path**. No second research dataset may be marked VERIFIED in Afanta.
5. Hand the approved creative intent and genuinely verified evidence to Afanta, with exact file SHA and a project-specific review receipt. A placeholder, unsigned manuscript or a text description of a competitor is not independently verified evidence.
5. In Afanta, run `python tools/afanta_studio.py audio-authority-audit`, then its own risk, script, original corpus, fact/rights, TTS/audio, visual, signed release gates. **Afanta alone** decides `RELEASE_READY`.
6. Private YouTube upload and public visibility require separate explicit owner approval. CINE must not claim successful publication or money earned based on manifests.

**Boundaries:** CINE = research and creative strategy; Afanta = production, independent QC, physical assets and release authority. Former CINE stage checklists and dated SOPs are historical guides, not competing canonical rules. The original protected AfantaStudio.exe and Desktop shortcut are unchanged and have no demonstrated in-process connection to Python controls.

**CINE Git safety:** The working tree contains unrelated ongoing work. Stage/commit only exact Audio files after verification; never use `git add -A` or touch Bell & Leaf sources as a side effect.
