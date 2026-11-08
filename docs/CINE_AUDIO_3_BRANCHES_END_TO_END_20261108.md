> **NON_CANONICAL_REFERENCE / HISTORICAL WORKFLOW:** The only rule-owner index is CINE config/audio/authority_index_v1.json. CINE config/audio/branch_registry_v1.json owns strategy and research; Afanta studio_os/docs/AUDIO_QC_CANON_V1.md owns production process. This dated guide is a contextual reference, never a new editable rule source.

# CINE / AFANTA — AUDIO MASTER NICHE — THREE INDEPENDENT CHANNEL LANES
Version: cine-audio-portfolio-v1 | 2026-11-08 | Status: LOCAL CONFIGURED, E2E RELEASE NOT APPROVED

## Architecture and strict boundaries

CINE (Research & Strategy, Editorial Governance) -> immutable scope-specific handoff -> Afanta (Writing / native TTS / Media / QC / publication control) -> owner-controlled YouTube account -> own-channel Analytics -> learning proposals back to CINE.

Parent `audio` is a **taxonomy and shared infrastructure**, NOT an audience pool or unified KPI baseline.

| CINE source scope | Afanta channel key | Afanta niche | Local workspace | Mode |
|---|---|---|---|---|
| everyday_history_sleep | history_sleep | history_for_sleep_en | afanta_history_sleep_pilot | verified nonfiction, bedtime |
| mom_grandma_family_original | quiet_justice | senior_daytime_audio_en | afanta_quiet_justice_pilot | wholly original fiction, daytime |
| science_space_nature_sleep | cosmos_sleep | science_for_sleep_en | afanta_cosmos_sleep_pilot | verified nonfiction, bedtime |

Roots:
- CINE: `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`
- Afanta: `C:\Users\ADMIN\Downloads\AfantaStudio_Viettruyen\AfantaStudio_Viettruyen`
- Parent registry: `config/audio/branch_registry_v1.json`
- CINE per-lane packages: `config/niches/<CINE_SOURCE_ID>/{niche.yaml,research.yaml,visual_bible.yaml,toolkit.yaml,learnings.yaml,README.md}`
- Afanta identical registry: `studio_os/audio_portfolio_contract_v1.json`
- Afanta project contracts: `output/audio_studio/<AFANTA_SLUG>/cine_audio_branch_contract.json`
- Afanta frozen draft runbooks: `output/audio_studio/<AFANTA_SLUG>/cine_audio_e2e_runbook.json`

## Pipeline: 13 ordered gates (same interfaces, different editorial rules)

| # | Stage / owner | Input | Required evidence / output (never auto-PASS) |
|---|---|---|---|
| 01 | Competitor Research / CINE Research Director | Exact English audio niche | Dated channel IDs, verified creation dates, format checked by listening, video dates, runtime, age-matched snapshots, independent baseline |
| 02 | Audience Radar / CINE Research | Reddit, Goodreads, YouTube questions | Copyright-safe abstract theme cards, source links, positive/negative signals; NO source stories, quotes-as-fiction or copied character DNA |
| 03 | Topic Approval / CINE Editorial | Verified demand + gaps | Three distinct concepts scored for originality, feasibility, traffic hypothesis, rights, factual burden; human topic decision |
| 04 | Evidence/Originality / CINE Story & Fact Editor | Selected concept | History/Space: claim-by-claim ledger with citations and reviewed uncertainty; Family Drama: original character, situation, moral dilemma and non-template plot DNA |
| 05 | Outline / CINE + Afanta Writer | Evidence and distinct concept | 8–18 chapter/scene outline with runtime beat budget, causal chain, chapter pacing, unique opening and closing |
| 06 | Script Draft / Afanta + Story Doctor | Approved outline | Original draft; factual claim review or fiction-originality audit; sentence clarity, tension retention, no recycled payoff, final human review |
| 07 | Voice/TTS / Afanta Audio Dept | Locked approved script | Reviewed commercial voice rights; consistent voice identity, WAV/audio recording, pronunciation dictionary and chapter QA |
| 08 | Mastering / Afanta Audio Dept | Narration WAV | Normalization, measured peaks/silence/clipping, music licensing, real listening beginning/middle/end, audio_sha256 and technical QC |
| 09 | 16:9 Video / Afanta Editorial | Audio + licensed graphic plan | Original/licensed imagery, story-aligned imagery/animations, credited/rights manifest, produced MP4 with unchanged audio sync |
| 10 | Technical, Rights, YPP / Afanta QC | All final files | Technical audio/video QC, accurate title/thumbnail, human release asset review, policy review, 6 valid human HMAC approvals bound to VIDEO SHA |
| 11 | PRIVATE YouTube / Explicit owner | RELEASE_READY from fresh manual audit | Manual explicit OAuth channel selection and PRIVATE upload only; record real YouTube video ID |
| 12 | Public Release / Separate explicit owner | Verified private video & approval | Independently authorized public visibility; no direct auto-release from this setup |
| 13 | Own Analytics / CINE Analytics + Afanta | Actual YouTube Studio CSV | D7/D14/D30 same-age results, CTR + retention by traffic source, new hypotheses labeled PROPOSED until own A/B test |

Reject handoffs if source niche IDs differ; no cross-lane peer medians, voice packs, script template plots, ads evidence or analytics. NEVER use a story from Reddit as a script. No greenlight, no fake signed reviews, no fake media.

## Channel-specific editorial law

### everyday_history_sleep (110 min initial pilot)
- Investigate ordinary life, work, small towns, tools, meals, transit and domestic environments. No invented witness quotations, diary entries, historically impossible composite events presented as documentary truth.
- Separate PRIMARY ARCHIVE, SCHOLARLY SECONDARY, CONTESTED CLAIM and INFERENCE, each with exact URL/date.
- Dramatic reconstruction must be explicitly labeled. Calm 115–135 WPM, minimal startle; exact facts should remain verifiable in spoken script.
- Pilot topics remain in Afanta `channel_plan.json`; an ideation topic is not fact-check clearance.

### mom_grandma_family_original (55 min initial pilot)
- Sub-series: Mom Cried (emotion), Dad Justice (dignity), Grandma Independence (agency), Elder Care Boundaries (mature decision-making).
- Never recycle 'relative humiliates elderly person -> surprise rich person -> humiliator shocked' as a mandatory formula. Each script differs in goals, cause, turning points, outcome, character agency and emotional coda. No portrayals presented as verified personal cases.
- No assumption that audiences for translated video drama equal audiences for original narration. Use only native audio-led English comps for baseline.
- Clear but expressive 145–160 WPM, quality audition for principal voice(s).

### science_space_nature_sleep (95 min initial pilot)
- Facts primarily backed by NASA/ESA/observatory/peer-reviewed work; verify values, unit conversions, time windows, model/observation boundaries and uncertainty.
- Never invent planets/discoveries/astronomical images, imply scientific certainty where there is only inference, or promise medical sleep treatment.
- Gradual 120–140 WPM cosmic scale journey with gentle pacing, little abrupt music or ad interruption.

## Command map (read-only by default)

From CINE root:
```powershell
python tools/cf_audio_branches.py show
python tools/cf_audio_branches.py audit
python tools/cf_niche.py routes everyday_history_sleep --json
python tools/cf_niche.py routes mom_grandma_family_original --json
python tools/cf_niche.py routes science_space_nature_sleep --json
python tools/cf_niche.py audit everyday_history_sleep
```

From Afanta inner root:
```powershell
python tools/afanta_studio.py portfolio-status
python tools/afanta_studio.py audio-branches
python tools/afanta_audio_branches.py plan --slug afanta_history_sleep_pilot
python tools/afanta_audio_branches.py plan --slug afanta_quiet_justice_pilot
python tools/afanta_audio_branches.py plan --slug afanta_cosmos_sleep_pilot
python tools/afanta_studio.py trend-report
```
The `plan` command returns a stage-wise execution map. Stage 01 candidates from `scan` are UNVERIFIED. Use `ingest` only after exact audio format verification and rights-safe metadata. `brief`, `draft-local`, `tts`, `render`, `audio-qc`, `video-qc`, `metadata`, `release`, `prepare`, `analytics` already exist in Afanta and must be run with real cleared inputs. An edited plan is not evidence of completed production.

## QA / acceptance and rollback

1. Verify both registry files have identical SHA256; project contracts reference same SHA; bound Afanta `studio_state.json` niche and channel_plan key are exact.
2. Verify CINE identity lists three `SCRIPT_FACTORY` branches with `parent_niche_id=audio`, no blockers. This is routing, NOT a production greenlight.
3. Run `python -m unittest discover -s tests -p test_cf_audio_branches_v1.py -v` in CINE and `python -m unittest discover -s studio_os/tests -p test_audio_branches.py -v` in Afanta.
4. Run Afanta prior regression tests and ensure all three remain RELEASE_HOLD until independent human signoff. Verify legacy `AfantaStudio.exe` and original novels unchanged via original receipt tool.
5. Pre-existing CINE worktree has numerous concurrent dirty files. This implementation creates dedicated files; NEVER use `git add -A` or commit/force-push shared modifications without a change-owner review.
6. Roll back by removing ONLY the new `config/audio/branch_registry_v1.json`, the 3 explicitly created config/niches branch directories, `tools/cf_audio_branches.py`, the CINE test/doc/skill, Afanta `studio_os/audio_portfolio_contract_v1.json`, 3 project `cine_audio_*\*.json` files and `studio_os/audio_branches.py` / `tools/afanta_audio_branches.py`. Do not delete project state, media, scripts, source novels, or compiled EXE. Current Afanta CLI has two additive subcommand changes; revert only these if desired.

## Known blockers (do not silently resolve)
- Real verified audio-only 30-day new-channel baseline NOT DONE; archived nonrandom search results are research leads only.
- Channel names/handles and actual YouTube account creation NOT DONE.
- Owner-specific TTS voice audition and commercial rights NOT DONE.
- Three complete, audited scripts; mastered WAV; real 16:9 video; six HMAC approvals NOT DONE.
- Public monetization/RPM and YPP eligibility UNKNOWN until owned channel data exists.

No production media or YouTube upload was executed during this portfolio integration.
