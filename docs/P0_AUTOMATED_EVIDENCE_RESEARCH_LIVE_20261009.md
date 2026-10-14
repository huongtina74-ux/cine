# P0 Automated Evidence Research — Live validation (2026-10-09)

Status: PARTIAL IMPLEMENTATION / LIVE RESEARCH PROBE PASSED. NOT VERIFIED NICHE DISCOVERY.

## Business intent
Company Youtube remains the only canonical **public search/catalog collector**. CineFactory now runs, reconciles and QA-checks its outputs for the two-branch Research system: monitor established leaders, independent newcomer evidence, and 0–15d fresh million-view video signals. Search results are not proof of title/topic match, retention, RPM, age, rights or YouTube recommendation traffic.

## Actual Windows code and interfaces
Module: `cinefactory/research_intelligence/evidence_research.py`.
- `plan_research_channels`: match one seed niche, balance new channels, mature leaders and other results; freeze query and selected CSV by SHA-256.
- `analyze_research_evidence`: validate one frozen search and matching catalog run, keep only long-form (>=8 minutes), require a traceable displayed views label; reject conflicts in video/channel identifiers; compute **PROVISIONAL** newcomer, leader, recent-demand and fresh-million signals. Check actual **niche title tokens** separately so search hits about other games aren't counted as Minecraft.
- `prepare_evidence_council`: single canonical issue and evidence registry. All search/catalog/analysis files have the SAME `youtube-public-lineage`; independent corroboration is NOT fabricated. Actual model/department opinions remain `PENDING_APPROVED_DEPARTMENT_REVIEW`.
- `run_live_evidence_research`: one user-run CLI; only calls existing Company Youtube scripts `collect_youtubejs_recent_search.mjs` and `collect_youtubejs_channel_catalogs.mjs` (no new collector). Runs read-only; supports explicit budgets and full Windows child-process tree termination on timeouts. No YouTube Data API or paid Claude/model call.
- Creates a human-readable `evidence.md` plus JSON, a channel shortlist, unalterable run manifest and review-specific tasks by exact video ID for leader, newcomer, fresh trend, cross-topic QA.

## Actual live tests on 2026-10-09

Niche sample **Minecraft animation** (engineering smoke test only, NOT owner approval).

**Live01** (two queries; direct collector calls + CLI join): 14 public search observations / 12 channel IDs; About fetched for eight; six channel catalogs collected with 69 videos, no collector errors. The initial report found 1 fresh million-view proxy, **but it was GameToons video `05IwOFRKYC4`, title about Poppy Playtime, not Minecraft**. The title-alignment correction removed it from Minecraft trend metrics. Final corrected report: six catalog channels, two 1M+ subscriber leader proxies, four mature channels with >=100k recent title-aligned video *display* signals; zero new 0–30d channels in this sample, zero fresh million-view title-aligned video signals, zero strict qualified niches.
- Original (superseded) naive report: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_01\evidence.json`
- Corrected report (USE THIS): `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_01\evidence_topic_qc_tasks.json`
- Topic QA excludes Poppy Playtime via per-video cross-topic task, not by erasing raw source.

**Live02** (single command 2 query, 3 catalog channels): state `REVIEW_PACKET_CREATED`, runtime ~8s. One channel joined within the 0–30 day *About date proxy*, but zero with two million-view videos. Different searches and samples legitimately yield different candidates; no result is called verified.

**Live03** (single command 2 query, six catalog channels): state `REVIEW_PACKET_CREATED`, runtime ~11s. Six catalog channels; three >=1M subscriber leader display proxies, three recent on-title mature demand proxies, zero 0–15d million-view title-aligned signals, zero 0–30d breakout, one cross-topic high-view video excluded.
- Final human report: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_03\evidence.md`
- Final machine evidence: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_03\evidence.json`
- Council review tasks and frozen single-origin registry: `...\evidence_live_03\council\`
- Run audit: `...\evidence_live_03\live_run_manifest.json`

All probes are bounded snapshots, not exhaustive market scans; public counts are rounded and age labels approximate. The catalog source does not prove whether long uploads include past live broadcasts. All `strict_breakout_witnesses=0`, `five_gate_status=NOT_EVALUATED`, `eligible_for_owner_approval=false`.

## One-command live usage (PowerShell)

Run in the CineFactory repo:

```powershell
python -m cinefactory.research_intelligence evidence-live --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --queries-json "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_01\queries.json" --youtubejs-entry "C:\Users\ADMIN\AppData\Local\Temp\ytseo-youtubei-runtime\node_modules\youtubei.js\dist\src\platform\node.js" --output-dir "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\NEW_UNIQUE_RUN" --niche "Minecraft animation" --max-channels 6 --max-results 7 --videos-per-channel 12 --timeout 120
```

Change output dir every time; old run data is never overwritten. Input queries JSON has 1–5 same-niche search items, e.g. two `query` strings and one fixed `seed_cluster="Minecraft animation"`. The Node `youtubei.js` module path is environment-specific and should be revalidated after tool updates. Script may fail if YouTube limits unauthenticated public access; in that case status is `FAILED_OR_INCOMPLETE`, not complete. Browser/ToS/licensing requirements must be respected when using source material.

## Quality acceptance evidence
- CineFactory 207/207 unit/integration tests PASS, `compileall` and `git diff --check` PASS.
- Company Youtube original validators 56/56 pass as expected, plus Node parser 3/3 pass.
- New tests cover frozen sources, plan/candidate matching, new vs mature channel classification, video ID ownership cross-joins, malformed high views, near-boundary channel age, topic contamination, budget/timeout, one-command fake collector, and incomplete council authorization.
- The live samples are genuine public metadata observations, but NOT evidence that a complete deep video analysis or human-authenticated cross-department debate has been performed.

## Remaining gaps, no false final claim
1. Real official YouTube Data API key or independently confirmed channel/video metadata for exact dates, views and publisher identity; current no-key public lane is candidate discovery only.
2. True multimedia video analysis of hook/storyboards, scenes, camera, thumbnail, sound and rights; current title comparison is metadata QA only.
3. Extend sampling beyond two English keywords for niches using tested per-market coverage. Canonical Company broader scanner still US/en.
4. Fully verified five-gate dossier (novelty, 2x1M newcomer, evergreen, economics, newcomer entry) + actual multi-role CineCouncil cross-examination. User approval remains required.
5. Link this bounded workflow into the approval-controlled Research Pod and daily scheduler, instead of scheduling an unapproved sample niche automatically.
6. Prove reliable recurring operation and monitor quota, outages and content drift before marking P0 operational.

**Recommended next substage:** replace per-title topic heuristic with permitted multimodal scene-level observation and add narrow reviewer QA for official 0–30d entrants, then complete research council and Five-Gate evidence only when all independent factual sources are available.
