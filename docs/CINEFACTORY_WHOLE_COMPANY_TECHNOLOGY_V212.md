# CineFactory v212 — Whole-company technology council & ongoing source watch

Date: 10 October 2026. Scope: actual CineFactory repo at C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6.

## Implementation

- The existing 96-entry v210 Technology Radar remains the baseline of researched model/tool/web candidates; legal and technical gates are preserved.
- v211 continues to discover GitHub repos and Hugging Face model references when researching niches or competitors, writing immutable pending R&D receipts. It never executes outside code.
- The new technology_council_v212 module maps the exact minor niche and production family to technology candidates, distinct scene intents (dialogue, camera, acting, VFX, environment, music, montage, captions, real capture) and all 26 company departments. It does not confuse scripted Minecraft animation with real captured gameplay or livestreaming.
- Existing CompanyBlueprint now persists department_technology_advisory with per-stage candidate IDs, responsible department and separate Claude/MCP watch sources. Executor, signed greenlight, actual permissions and commercial review are unchanged.
- The competitor forensics dossier now contains whole_company_department_options_by_format, separated by metadata-derived video format. It explicitly does not prove the other producer's actual software.
- New technology_watch_v212 uses exactly 23 allowlisted public sources. Four rotate each day across Anthropic/Claude, MCP, AI/software and SaaS. No URLs supplied by YouTube titles or GitHub descriptions are fetched; URL redirects are blocked and response sizes capped.
- Anthropic sources: Claude Code, Agent SDK, official/community plugins, public Claude Platform release notes. MCP sources: official MCP Registry (video, Blender, YouTube, audio searches), registry and reference GitHub repos. AI/software includes ComfyUI, Blender, FFmpeg, FLUX, FreeVideo, MOSS, ACE-Step, HyperFrames. SaaS sources include official Runway, Adobe, HeyGen public pages.
- GitHub release/tag and commit metadata remain untrusted source evidence. MCP registry result names do NOT imply a server can be installed, used, trusted or invoked. SaaS HTML digest changes are change alerts only, not semantic AI releases.
- Every source result enters append-only SHA-256 JSON receipts under data/research/technology_discovery/watch. A source failure is reported, not interpreted as a new release.

## Integrated daily monitoring

The existing Windows Scheduled Task CineFactory-Daily-YouTube-Research, registered for 08:00 local, invokes scripts/daily_cinefactory_research_v199.ps1. It in turn invokes run_two_track_research_v201.py --discover-technologies, now including the v212 source watcher. The task was Ready when inspected and next scheduled for 11 October 2026 08:00. A scheduled run after the code change has not yet been observed. The separate Research P1 / Health P1 tasks had pre-existing failures; not cured by adding a technology watcher.

## Actual source smoke, October 10, 2026

Four permitted public sources were checked on the owner's Windows host without credits or model installation:
- Claude Code: GitHub release v2.1.296, published 2026-10-09 19:28:59 UTC.
- Claude Agent SDK: GitHub release v0.3.296, published 2026-10-09 19:28:19 UTC.
- Official MCP Registry blender search: multiple public name matches, all UNVERIFIED for rights, security and operational usage.
- Runway official changelog: ValueError from bounded source fetch; logged as unavailable. No fabricated latest version or successful fetch.

Official sources for ongoing research: https://github.com/anthropics/claude-code ; https://github.com/anthropics/claude-agent-sdk-typescript ; https://github.com/anthropics/claude-plugins-official ; https://platform.claude.com/docs/en/release-notes/overview ; https://github.com/modelcontextprotocol/registry ; https://registry.modelcontextprotocol.io/v0.1/servers ; https://github.com/Comfy-Org/ComfyUI .

## Commands (from nested canonical checkout)

- python -m cinefactory.cli technology-radar --show-items : baseline 96.
- python -m cinefactory.cli technology-backlog : pending model and repo research.
- python -m cinefactory.cli technology-watch : read-only official watch status.
- python -m cinefactory.cli technology-watch --public-sources : check 4 rotating official sources.
- python -m cinefactory.cli technology-watch --public-sources --source-id claude_code --source-id mcp_registry_blender : specific public source checks.
- python -m cinefactory.cli technology-match --minor-niche minecraft_school_comedy --major-niche minecraft --department AUDIO : craft-role technology candidates.
- python -m cinefactory.cli technology-match --minor-niche minecraft_recorded_survival --major-niche minecraft --scene-intent real_capture --department PRODUCTION : real-gameplay tech; excludes animation rigs.
- python -m cinefactory.cli company-plan --niche minecraft --minecraft-subniche minecraft_story_adventure --prompt "Original pilot" --duration 60 : company plan carries per-stage technology advisory; it cannot bypass approvals.

## Maturity boundaries

Company now knows what to research for each niche and keeps watching new official source versions. It does NOT automatically install new AI weights, call paid Claude API, connect MCP servers, use others' footage/IP, switch production backend, qualify commercial licenses, claim a GPU benchmark or publish to YouTube.

Before adoption: security and maintainer audit, package integrity, commercial/worldwide model and output license, compatibility and actual RTX 3060 12GB benchmark, original film/audio quality QC, rollback, separate owner authorization. A working vendor website and impressive demo are not proof of an independently accepted original film.

An update is only checked on the schedule while the Windows machine and public network are available. No guarantee of real-time continuous monitoring while the PC is powered off.


## Engineering verification and current release status

- First v212 full test used an incorrect temporary directory *inside* the repository. The legacy v195 hostile-file-path test then correctly treated the fixture as inside the allowed root, tried FFprobe and failed for an invalid test video. This was a test harness location error, not a change to the security boundary. No security requirement was weakened.
- Isolated v195 hostile-path test repeated with a temporary directory *outside* repository: **1/1 PASS**. Log: .tools/deep_audit_20261010/v212_outside_repo_sec_test.log.
- Full company regression rerun with correct outside-repository --basetemp: **1,518 PASS / 3 historical FAIL**, about 197 seconds. Log: .tools/deep_audit_20261010/v212_final_full_outside_repo.log. Exactly three long-standing Blender v190/v196 SHA provenance checks failed; historical expected hashes are unchanged.
- Final focused integration after the small long_slices_game taxonomy alias and persisted daily-watch-report adjustments: **120/120 PASS**; Python compileall PASS. Log: .tools/deep_audit_20261010/v212_targeted_last.log.
- Windows real scheduler: CineFactory-Daily-YouTube-Research Ready, next 11 October 2026 at 08:00. Exact source watcher was verified manually (see smoke results). No claim that scheduled v212 ran before its next trigger; separate P1 research/health tasks still have earlier errors.
- Watch-source output evidence: .tools/deep_audit_20261010/v212_live_source_watch.json. A failed vendor changelog remains an explicit SOURCE_UNAVAILABLE finding and can be reviewed, not counted as a successfully confirmed latest version.
- This engineering gate is **integrated for source discovery, department advice, and monitoring**, NOT a commercial film-production certification, nor approval to install MCP/Claude/plugins/weights or spend credits.
