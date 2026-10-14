# CineFactory v228 — Company-wide FULL competitor video/audio study

Effective: 2026-10-11. Owner's permanent rule: **For EVERY niche/channel and EVERY reference episode whose content or production method CineFactory studies, see/hear the WHOLE VIDEO, not one 10-second part or a handful of preview frames. Only then draw conclusions about narrative, acting, visuals, audio, cuts, workflow and replicable original formats.**

## Two separate research phases

- **DISCOVERY / MARKET SCREENING**: Official public video metadata (duration, posting date, views), channel-age/14-day breakouts, title/format hypotheses. Can operate daily cheaply without watching every candidate. Results only CANDIDATE/NOT_YET_WATCHED; NEVER factual deep content or software analysis.
- **DEEP VIDEO RESEARCH**: Choose the video shortlist, then watch the **complete continuous picture+original sound** of *every selected episode*; full source asset hash, independent metadata, ffprobe/FFmpeg full decoding, per-<=30-second visual and audio observation, voice/dialogue, character/acting, camera/edit, environment/props, event sequence, pacing, hook/climax/outro, and uncertainties. Separate reviewer audits the continuous evidence and full-video synthesis. Each added selected episode expands the required set; all must pass before cohort is accepted.

Full frame decoding ≠ watching/understanding actual audio+video. Reviewer attestations ≠ objective cryptographic proof of cognition. Fail closed on missing licensed source, sound track, timecode window, detailed observations, reviewer, or second check. One screenshot, storyboard mosaic, transcript, title, timestamp descriptions and 10-second highlights cannot substitute for the full original episode. Full source availability is rights-constrained; no paid credits or unauthorized downloads triggered.

## Universal code integration

- `config/technology/competitor_full_video_first_v228.json` — company-wide policy covering 26 departments and all niche families.
- `cinefactory/studio/universal_competitor_review_v228.py` — generic research gate `competitor_full_review_gate(niche_id, video_ids)`, per-department status `competitor_study_department_gate`. Maizen calls previously hardened `maizen_full_video_review_gate` v227 with its three mandatory full sources, and supports newly selected generic videos too.
- `cinefactory/studio/niche_technology_strategy_v213.py` — all niche technology advisory outputs now include `universal_full_video_audio_first_gate`; when a competitor conference specifies `video_cases`, those are the selected video IDs and they ALL must qualify. Market metadata, candidate tools and speculative video DNA cannot be promoted as verified.
- `cinefactory/studio/video_production_intelligence_v195.py` — automated FFmpeg/OpenCV decomposition explicitly marks `audiovisual_analysis_complete=false` and adds a blocked capability requiring a full independent review. A software decode does not prove film comprehension or the name of the rival's secret renderer.
- `cinefactory/studio/claude_mcp_gateway_v218.py` — two new read-only MCP tools; callers never auto-pay, auto-download source or approve/execute a backend.
- `cinefactory/cli.py` — `competitor-full-review --niche <slug> [--video-id <id>...]` and optional `--department <department>` for individual department go/no-go reports.
- `CLAUDE.md` and `.claude/skills/competitor-complete-study/SKILL.md` direct research and technical agents to call these gates before competitor-based production-method decisions.

## Independent source receipt contract for new non-Maizen videos

Public source metadata must be independently checked, under `data/research/competitor_source_metadata/<video_id>.json`, schema `cine.company.competitor_source_metadata.v228`, with `video_id`, canonical `source_url`, integer `duration_seconds`, `source` (DIRECT_YOUTUBE_VIDEO_PAGE or OFFICIAL_YOUTUBE_DATA_API), `source_verified=true`, and `checked_at`. A bare boolean by itself does not prove an actual official API query; auditors validate provenance.

Keep authorized full AV source under ignored `data/research/competitor_source_media/<video_id>.mp4` (MKV/WEBM also allowed); keep `data/verification/v228_competitor_full_video_reports/<video_id>.json` with schema `cine.company.competitor_full_watch_report.v228`, source SHA, independent watcher+reviewer, **full 00:00 to end** visual/audio observations with intervals ≤30 s and whole-film synthesis. Full decoded proof under `<video_id>.media_receipt.json` must have `cine.company.competitor_full_decode.v228`, matching ID+SHA, correct source duration and complete video/audio success. This version provides a read-only evidence validator, not an automatic source downloader/transcript provider. **Records not present or untrusted => BLOCKED**.

## Re-evaluate every category: research observations vs hypothetical technology

The full source can tell us story structure, shot patterns, acting, editing, dialogue and actual sound. It often CANNOT reveal whether the competitor used specific Blender add-ons, Unreal Engine, Mine-imator, custom NPC scripts, Claude Code, Higgsfield, a private 3D renderer, or automatic bots. Name these as **HYPOTHESIS** until explicit first-party behind-the-scenes or toolchain evidence confirms them. Use original works/assets and signed commercial rights. Full-source study authorizes inference and creative design only; installing a tool, running a paid provider, production work-order and YouTube publishing still require their own separate conditions and owner approvals.

For selected Maizen Studio A, v227's hard `G03–G28` gate remains intact and mandatory. In other niches, v228 is enforced at the shared **research conclusion/advisory level** and in video intelligence handoff; it does not yet intercept every legacy production executor or already-signed independent original-only work order. Never claim cross-engine universal runtime enforcement when only shared research gateways and agents enforce this version.

## Operational checks

```powershell
python -m cinefactory.cli competitor-full-review --niche roblox_animation --video-id zhPBXzHsLuo
python -m cinefactory.cli competitor-full-review --niche long_slices_game --department TECHNICAL_DIRECTION
python -m cinefactory.cli competitor-full-review --niche minecraft_maizen
python -m cinefactory.cli maizen-full-video-review
python -m cinefactory.cli maizen-research-stage --stage-id G03 --enforce
```

**At this checkpoint**: selected Maizen videos **0/3 fully verified**, other generic selected competitor videos have no approved complete-media reports. Full video/audio research is **NOT complete**; scripts/methods from metadata and screenshots remain speculative research, not vetted rival workflow.
