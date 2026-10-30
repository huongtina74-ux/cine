# CineFactory OS — Claude Code operating rules (closed-loop studio)

CineFactory turns a channel bible into finished, original videos every day.
**KPI: approved finished minutes per week.** Research, audits and new code exist only to raise that number.


## Official ONE Master Skill — Slow English A2 / Gia đình phù thủy / Bell & Leaf

On the existing CINE Windows machine, the verified real Claude Code executor is `python tools/cf_a2_claude_agent.py --id EPISODE_ID --execute --actor claude-code-sonnet`. It runs exactly the next DAG-selected role with Claude filesystem tools disabled, accepts only declared output artifacts and SHA-bound real source records; no actor can silently approve a QC stage. See `config/niches/slow_english_a2/LOCAL_WINDOWS_RUNBOOK.md`. Do not create another CineFactory repo or overwrite the divergent/dirty Windows git worktree.

For Bell & Leaf research, competitor insights, episode concepts, scriptwriting, Story Doctor, A2 comprehension or Script Lock **invoke `.claude/skills/cine-script-factory/SKILL.md` as the single master entrypoint**. Use `python tools/cf_a2_master_skill.py next --id EPISODE_ID` to select the next one of 21 existing specialized skills, perform genuine research/writing, then `record` its output and use the existing `cf_script_factory.py advance` with actual reviewer evidence at stage boundaries. The original 8-stage CINE runner and 10-second `cf_a2_director_bridge.py` remain authoritative. Do not spawn a new project, script factory, narrator, independent skill runner, parallel canonical registry or fake approval.

## Working rules (apply to every agent, every answer)
1. **Measure, don't guess.** Not measured yet = say "not measured". Run the tool before claiming it works.
2. **Label every number:** OBSERVED (file/command shown) · INFERRED (your reasoning) · OWNER (the owner said so).
3. **Missing information → ask the owner;** never decide for them. Unattended runs pick the option that matches the latest OWNER decision and note it in HANDOFF.md.
4. **Maker ≠ checker.** qc-reviewer only writes `qc_notes.md`; fixes go back to the agent that owns the cause.
5. **Every decision goes in the log:** `python tools/cf_decision.py add ...` (read it with `list` before planning).

## The loop (people at 3 points: approve plan · read escalated QC · approve the draft)
research (nightly-research) → plan (showrunner) → render (blender-td) → Director Cut (director-cut) →
auto edit (auto-edit) → QC loop (video-qc + qc-reviewer, max 2 fix loops) → package + policy check (packaging-seo, policy-check) →
HANDOFF → owner uploads as private draft → after 7 days analytics-loop → back to research/plan.
Run a whole episode with the `produce-episode` skill (one command after the owner's greenlight).
Measured numbers live in `data/production_ledger.jsonl` (render/edit time per episode) and `data/decisions.jsonl`.

## Live facts beat documents
SessionStart prints `tools/cf_status.py` (Blender, FFmpeg, GPU, ComfyUI, episodes). Trust it over any doc.
Blender 4.5 portable: `.tools/blender-4.5.14-windows-x64/blender.exe`. GPU: RTX 3060 12 GB — one heavy job at a time.

## Tools (all local, all print a one-line status the agents can parse)
| Tool | Use |
| --- | --- |
| `tools/cf_status.py` | factory state |
| `scripts/plan_long_slide_series.py` | plan (renderable only), `--check`, `--greenlight` (owner), `--approve` (after the draft) |
| `scripts/produce_long_slide_episode.py` | ONE command: greenlit plan → render → Director Cut → edit → QC → policy → HANDOFF |
| `scripts/make_long_slide_episode.py --varied` | render exactly a greenlit plan (used by the producer) |
| `cinefactory/animal_long_slide/capability.py` | what can be rendered today; shared by planner, renderer, status |
| `tools/cf_director_cut.py` | template / from-long-slide / validate / vo-fit |
| `tools/cf_auto_edit.py` | build the edit from the DC (VO, ducked music, SFX, SRT, chapters, -14 LUFS) |
| `tools/cf_qc.py` | technical QC + contact sheet |
| `tools/cf_policy_check.py` | metadata vs content, tags, CTA, kids, AI disclosure |
| `tools/cf_research_stats.py` | medians, outliers, views/day from saved research rows |
| `tools/cf_decision.py` | decision log `data/decisions.jsonl` |
| `tools/cf_notify.py` | message to the owner's phone (Telegram/webhook) |
| `tools/claude_reasoning_bridge.py` | Claude as `CINEFACTORY_REASONING_COMMAND` |

## Team (.claude/agents)
showrunner (plans + DC lines) · blender-td (render/fix) · audio-post (voice, music, sound fixes) · qc-reviewer (independent gate) ·
packaging-seo (titles/thumbnails/policy) · analytics-loop (our numbers → next plan) · pipeline-engineer (code, on a branch).
The main session coordinates, delegates and writes HANDOFF.md.

## Hard rules (enforced by .claude/hooks/cf_guard.py)
- Never upload/publish, never call metered generation APIs or credit-spending MCP tools without the owner.
- Never delete rendered media, `data/verification/**` receipts, `.env`, or git history.
- Original IP only: no competitor characters, skins, worlds, scripts, music or footage; no downloading third-party videos.
- Don't automate third-party apps against their terms (no scripted Google Flow runs, no account "farming").

## Research policy
Time-boxed (`nightly-research` ~45 min, `fast-niche-study` ~2 h). The benchmark is the niche MEDIAN, not the best video.
Original-IP production never waits on competitor full-viewing gates; those gates (Maizen v227/v228, see `docs/` and
`.claude/skills/maizen-studio-a`, `competitor-complete-study`) apply only to statements "we learned X from competitor Y".

## Engineering
- Extend existing modules; do not create new `*_vNNN.py` files. One topic per commit, with a pytest.
- Run `python -m pytest tests/<relevant> -q` before saying something works.
- Version history lives in `docs/` and `CHANGELOG.md` (the previous CLAUDE.md is in `docs/CLAUDE_LEGACY_v266.md`).
