# CineFactory v1.6.34 — Autonomous Public Source Research & Critical R&D Intake

**Date:** 2026-10-09  
**Status:** REAL LIVE PUBLIC GITHUB RESEARCH VERIFIED — PRODUCTION/TOOL RELEASE BLOCKED.  
**Branch at start:** studio/v1.6.6-universal-company, HEAD 44e1f5f. Preserve existing working tree.

## Production-grade planning rationale

The production company must research each niche and each scene's required capabilities before tool selection:
1. Study market, content format and reference-video structure (obtained video vs URL must be distinguished).
2. Identify exact art, physics, story, audio, curriculum and asset specifications from a *new, original* production brief.
3. Discover possible tools/repositories/models from official documentation, with dated/bounded source provenance and rights context.
4. Distinguish **mentioned features** from **executable capability**, **scoped quality benchmark**, **commercial usage rights** and final **production readiness**.
5. Have creative/technical/finance/legal/QA experts challenge the proposals, request controlled A/B golden shots, measure accepted-minute costs and reject unsafe or weak plans.
6. Only promote a production recipe after creative signoff, commercial clearances and multiple-shoot/project acceptance. Never rely on one vendor README/AI generated score.

### Current engineering milestone completed

A real read-only public GitHub ingestion adapter and a multi-niche source research orchestrator were built and wired into `AppContext` and `ProfessionalCompanyLayer`.

**Live source collection** is OFF by default. A user/operator must explicitly invoke `--live-public-github-read`. The adapter connects to **https://api.github.com only**, through fixed allowlisted repositories; GET-only, no unapproved redirects, max 5 repos/10 calls, max response bytes/timeouts, no environment tokens, no installation, no code execution, no media downloads or paid APIs. Source JSON/README bytes are written as append-only SHA-256 content-addressed snapshots under the repository for audit. A changed/tampered SHA or file outside the snapshot root cannot be used by the advisor.

**Scope of README analysis:** bounded lowercased line scanning for workflow/video/graphics/audio/physics/API/licensing terms. Counts are only *research signals that those words occur*, never verified working features, actual Blender/ComfyUI output quality or GPU support. Malicious README instructions remain inert data.

**Scope of GitHub metadata:** public canonical repo identity, archived status, pushed_at, default branch, description, topics, repository-declared SPDX, number of stars/issues. Stars are never treated as output quality. GitHub repo licence metadata does **not** equal authorization to use LTX/ComfyUI checkpoint weights, singer voices, music, video clips or proprietary assets.

## Live run — 2026-10-09

Read five real repositories and associated README payloads, **10 GitHub public GET calls**, 0 fetch errors:

| Public repo | Repo-declared SPDX observed | Archived | Production capability |
|---|---|---|---|
| `blender/blender` | NOASSERTION | false | Code/source identified; actual Blender local workflow benchmark from earlier milestones is separate |
| `godotengine/godot` | MIT | false | Candidate Godot physics game runtime, **not installed/executable verified** in current machine PATH |
| `Comfy-Org/ComfyUI` | GPL-3.0 | false | ComfyUI source exists; local video model/checkpoint performance remains unmeasured |
| `musescore/MuseScore` | NOASSERTION | false | Candidate score/MIDI authoring, NOT an automatic original-song creation engine |
| `Lightricks/LTX-Video` | Apache-2.0 | false | Candidate AI video model repo; **model checkpoint/weights license and RTX3060 performance unapproved/unmeasured** |

**Important:** NOASSERTION means GitHub's current repository metadata does not assert a machine-readable SPDX designation; it is not necessarily unlicensed. Exact LICENSE text must be read and legally reviewed. A software repo SPDX value is NOT a blanket approval for the input/output rights or model distribution.

Three real updated R&D proposals were built from the downloaded source evidence:
- **Preschool 3D**: 2 official repo metadata/README candidates (Blender and MuseScore). Education, original songwriting/music licensing and controllable singing/organic rig remain blockers.
- **Long Slide**: Godot and Blender. Actual original physics simulation, course assets and deterministic game-runtime/video benchmark remain blockers.
- **AI Family Drama**: ComfyUI and LTX-Video. Actual GPU video workflow, model weight commercial terms, multi-shot identity and finished-minute costs remain blockers.

All produced typed plans and structured future reasoning-agent packets. No external LLM was invoked; no video was rendered in this live research run. Each source has raw bytes and verified SHA; model `StrategicResearchReasoner` still records `active_model_reasoner_connected=false`.

## Code and evidence

- `cinefactory/studio/github_research_adapter_v194.py`: bounded secure public Github source collector, provenance and immutable snapshots.
- `cinefactory/studio/autonomous_source_research_v194.py`: multi-niche scope, dated source->claims->adversarial R&D decisions->future agent packet, keyword research cues only.
- `scripts/run_autonomous_source_research_v194.py`: CLI live research cycle with explicit network opt-in.
- `cinefactory/appctx.py`, `cinefactory/studio/professional_company.py`: share **offline-default** `autonomous_source_research` service; existing production routes not changed.
- `tests/test_autonomous_source_research_v194.py`: network OFF, allowlist, SSRF, redirects, versioned snapshots and injected README instructions, hash tamper/escaped paths, archived/identity checks, cost/rights/production blocks and real SHA evidence on 5 fetched repos.

All under `data/verification/v194_autonomous_research/`:
- `research_cycle_evidence_v194.json` — full Pydantic evidence provenance.
- `research_cycle_summary_v194.json` — human-readable machine JSON summary.
- `github/raw/github_repo_<sha>.json` and `github/raw/github_readme_<sha>.json` — original response body / readme decoded bytes, content-addressed.
- `plans/preschool_3d_musical_live_source_research.json`
- `plans/long_slices_game_live_source_research.json`
- `plans/ai_family_drama_live_source_research.json`
- `agent_packets/*_research_packet.json` — future authorized LLM/agent tasks, not executed.
- `regression_v194.txt` — full pytest regression evidence after execution.

### Run again (safe defaults and opt-in)

```powershell
# 1. No network: return research proposal / capacity blockers, no fetch
python scripts/run_autonomous_source_research_v194.py

# 2. Opt-in PUBLIC read-only GitHub research (~10 short GETs, no keys)
python scripts/run_autonomous_source_research_v194.py --live-public-github-read

# 3. Target one niche and avoid README download (repository metadata only)
python scripts/run_autonomous_source_research_v194.py --live-public-github-read --niches long_slices_game --no-readme

# Tests
python -m pytest -q tests/test_autonomous_source_research_v194.py
python -m pytest -q
```

No API key is required for these specific *public Github metadata* reads; anonymous GitHub rate limits apply. YouTube Data API is separate, requires credentials/quota and is not automatically invoked.

## Security and truthfulness controls

- *No silent auto-install*: repository discovery does not import/clone/execute source code.
- *Prompt-injection firewall*: README words/markdown are only counted as data; never command or authorization. Raw README must not be put directly into a privileged LLM instruction role.
- *Provenance*: actual body SHA256; non-matching/moved/tampered snapshots fail closed.
- *Strict origin & scope*: fixed HTTPS API origin and static allowlisted repository slugs; no arbitrary URLs, redirects or LAN targets.
- *No business license inference*: repository SPDX is observation only, no model weights/song/voice/output legal approval.
- *Independent performance*: repository popularity and README text never provide quality/VRAM/cost benchmark proof.
- *Bounded cost*: no tokens/premium APIs, 10 HTTP GET max by default on intentional live run, response bytes and timeouts capped.
- *No release*: every recommendation is a future test hypothesis with all production execution flags false.

## Multiphase roadmap AFTER v1.6.34

| Phase | R&D deliverable | Acceptance condition |
|---|---|---|
| **v1.6.35** | Authorized YouTube/reference video analysis using current `ReferenceIntelligence` + optional connected TubeAlfred/YouTube API, plus PDF/manual/model-card adapters | Actually decoded local/authorized media plus video-frame/transcript provenance; unknown content must be UNKNOWN, proprietary assets quarantined |
| **v1.6.36** | Controlled multi-engine Golden Shot Benchmark Lab | Original same-shot 30–60 s video via 2+ qualified backends; human blind review; visual/audio quality floors and VRAM/walltime/accepted-minute cost captured |
| **v1.6.37** | Original preschool 3D music trial: script/education -> original MIDI/score -> authorized vocal -> organic character -> beat/viseme animatic | 30–60s sample actually rendered and signed by curriculum, original-music rights and human editorial QC |
| **v1.6.38** | Continuous R&D Watcher & Knowledge-to-Production Promotion Board | Bounded recurring source change watch under explicit schedule, signed multi-project validations, rollback & regression evidence; no automatic payment/install/publish |
| **v1.6.39** | GPU/resource/factory cost optimisation across niches | Peak VRAM, camera/shot continuity, per-accepted-minute cost, human retouch time; prioritise quality floor over mere speed |
| **v1.6.40** | Multi-niche full episode pilot certification | Minecraft, preschool music and non-Blender story/game project delivered with independent QC and review |

The production goal is not an AI that claims to be perfect: it is a transparent, falsifiable and cost-aware research system that **knows what it can prove and when to run a better experiment**.

## Documentation sources for API contracts

- GitHub REST public repository endpoint: https://docs.github.com/en/rest/repos/repos
- YouTube Data API video metadata and 1 quota unit per videos.list request: https://developers.google.com/youtube/v3/docs/videos/list
- OpenAI public read-only documentation MCP: https://developers.openai.com/learn/docs-mcp

Current v1.6.34 source research uses GitHub public API ONLY. YouTube auto browsing, arbitrary web exploration, executable model testing and programmatic Codex agent invocation remain out of scope and must not be represented as done.


## Final verification (2026-10-09) — COMPLETE

- Full repository regression: **878/878 tests PASS, 0 failures, 140.61 seconds**; `python -m pytest -q` exit code 0.
- Focused v1.6.34: **36/36 PASS**; covers default-off internet, bounded repo allowlist, SSRF/redirect, tampered source SHA, archived repositories, hostile README text, source attribution, private identity, no-claim-of-license, no release and 5 live verified repo snapshots.
- All source/modules/scripts `python -m compileall -q cinefactory scripts tests`: PASS.
- `git diff --check` targeted tracked source: PASS (only expected LF-to-CRLF informational warnings on Windows).
- Actual live read-only GitHub research: **5 repositories, 10 GETs, no errors**, each metadata+README immutable hash checked.
- Three niche source-backed reports and agent handoff packets were generated. No external LLM was invoked; human creative assessment and true multi-engine A/B are still future work.
- Canonical live evidence is preserved when running default OFFLINE scan; offline logs are separately named, and no unapproved network request is made in offline mode.
- Git branch and old HEAD untouched; original worktree retained. No commit/staging, reset, cleaning, tool install, model download, YouTube video fetch, paid API call, publication or deployment.
- **All production gates remain BLOCKED for newly discovered source methods**, regardless of public repo licensing metadata.
