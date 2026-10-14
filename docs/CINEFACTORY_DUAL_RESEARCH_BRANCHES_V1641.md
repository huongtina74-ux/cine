# CineFactory v1.6.41 - Two Independent YouTube Research Departments

Date: 2026-10-09.
Project root:
C:\Users\ADMIN\Downloads\CineFactory_Autonomous_Build\cinefactory-os-v1.6\cinefactory-os-v1.6

## User specification

CineFactory must research daily along two completely independent streams.

**BRANCH 1 - Company-wide, permanent new-niche radar**:
- Search both niche-family lists and open-ended new-format frontier, without assuming all of YouTube is represented in a bounded public search.
- Candidate must be a truly NEW FORMAT compared with the company's catalog, or an independently substantiated substantially different execution method. Repeated known formats must NOT be marketed as new niches.
- At least one new channel whose channel CREATION (not first video upload) is proven as 0-30 days ago. That SAME channel must have at least 2 **different** long-form 8+ minute video IDs, each with >=1,000,000 public views. Avoid duplicates, shorts, livestreaming, timestamp assumptions, and cross-format counting.
- For lasting demand, independently confirm that >=1-year-old channels in the SAME niche/format still receive >=100,000 views on newly published videos, with a current source timestamp. Historical subscriber counts alone do not show demand today.
- Evaluate original creative viability, competition from genuinely newly created channels, commercial rights, achievable cost per accepted minute, throughput, geography, uncertainty of monetization, advertiser suitability, and long-term audience demand.
- $1k/month, $100k/month and $1m/month per channel are separate hypothetical scale scenarios: do not promise revenue or infer competitor RPM from public YouTube views. Use explicit scenario math, then independent legal/finance/actual channel Analytics before greenlight.
- Report winners only when empirical gates are proven; otherwise preserve unverified discovery candidates and specific missing evidence. Never automatically approve production.

**BRANCH 2 - Sustained niche-specific competitor intelligence**:
- Starts only after the company owner explicitly approves EACH niche and format. Approving Minecraft gameplay NEVER silently approves Minecraft cinematic animation.
- A: established leaders, recent uploads, historically popular samples, growing videos outperforming own channel baseline, and *source-verified* subscribers. Ratio of views / subscribers is NOT reach.
- B: discover newly created 0-30 day competitor channels; measure the count of >=1M videos, study rising leaders in exactly that format, track published dates with official age proof when available.
- C: search many distinct relevant keywords per approved format, check 0-15 day >=1M long-form video occurrences, derive format/language/engagement hypotheses, decide whether to adapt a **general creative pattern** or reject short-lived trends.
- Each accepted niche maintains its own references and source-backed scripts/director/storyboard/shot style, voice/music, asset/rig plan, production-method experiments, packaging/thumbnail/SEO hypotheses and independent QC. Learn from the OWN production channel's authorized CTR/watchtime/retention/monetization, not by guessing third-party Analytics.
- Be proactive; never copy competitor source footage, copyrighted text, character skins, background music, channel brands, or voice. Trend chasing is subordinated to original format promise and sustainable owned IP.

## Architecture implemented, v1.6.41

| Module | Responsibility | Operational limitation |
|---|---|---|
| cinefactory/studio/two_track_research_v201.py | Persistent approval registry, new format proposals and novelty review, distinct-ID >=1M gate, new vs mature creation age gate, financial scenarios, per-approved 3-cohort analysis, own JSON reports | Cannot manufacture source age, RPM or player audio |
| cinefactory/studio/research_frontier_v201.py | Bounded searches beyond the 14 registered formats, recent-video lookup, known-format fingerprinting and UNKNOWN candidate queue | Search order non-exhaustive; cannot certify novelty from a title |
| cinefactory/studio/channel_provenance_v201.py | Optional official YouTube Data API channels.list snippet.publishedAt and subscribers from authenticated user-provided API key | NO KEY = UNKNOWN channel age; no vidIQ subscription required |
| cinefactory/studio/approved_niche_keyword_scan_v201.py | 3-4 controlled query variants per approved format, strict source gate, own run ledger | No approved format = ZERO network requests; metadata alone does not prove watched video |
| scripts/run_two_track_research_v201.py | Offline evaluation, optional frontier, optional approved-only keyword scans, separate owner Markdown briefs and Claude Code advisory packets | No Claude Code use, upload or spending automatically |
| scripts/daily_cinefactory_research_v199.ps1 | Runs existing public metadata scan, then both research branches and frontier on existing Windows scheduled task | User must be signed in; no 24/7 cloud service |
| cinefactory/studio/daily_youtube_breakout_v199.py | Read-only company services .two_branch_owner_report() and .niche_research_approvals() | Explicit user approval always separate |
| tests/test_two_track_research_v201.py and tests/test_approved_niche_keyword_scan_v201.py | Hard-gate, isolated format approval, mixed-niche rejection, exact ages, two video IDs, mature demand, evidence and quota tests | Synthetic fixture tests do not establish actual creator business performance |

Source video metadata store:
data/research/youtube_breakout/cinefactory_breakout.sqlite3

Saved reports:
data/research/youtube_breakout/two_track_reports/BRANCH_1_GLOBAL_OPPORTUNITIES_<UTC>.md
data/research/youtube_breakout/two_track_reports/BRANCH_2_APPROVED_NICHES_<UTC>.md
data/research/youtube_breakout/two_track_reports/two_track_<UTC>.json
data/research/youtube_breakout/frontier/frontier_<UTC>.json
data/research/youtube_breakout/approved_deep_research/keyword_scan_<UTC>.json
data/research/youtube_breakout/approved_agent_handoffs/<niche>_<format>_<UTC>.json

## Precise permission and commands

Daily schedule already exists as native Windows Task Scheduler:
CineFactory-Daily-YouTube-Research
At 08:00 local; Windows user must be logged in, machine on. This task now also invokes:
  python scripts/run_two_track_research_v201.py --with-frontier --scan-approved

To run safe offline analysis of ALREADY saved evidence:
  python scripts/run_two_track_research_v201.py

To scan public broad-interest source and approved niche keywords:
  python scripts/run_two_track_research_v201.py --with-frontier --scan-approved

TO APPROVE ONE SPECIFIC NICHE-FORMAT, must be the explicit owner's decision, not a scheduler operation:
  python scripts/run_two_track_research_v201.py --approve-niche minecraft minecraft_gameplay --confirmation "DUYET minecraft minecraft_gameplay"
Approving Minecraft gameplay leaves minecraft_animation OFF. No niches have been approved on behalf of the user as of this audit.

To PAUSE that one format:
  python scripts/run_two_track_research_v201.py --pause-niche minecraft minecraft_gameplay --confirmation "DUNG minecraft minecraft_gameplay"

For official channel creation day and subscriber counts, optionally create a user-owned YouTube Data API key and set environment YOUTUBE_DATA_API_KEY for the user; check quota and Google Cloud conditions. Then:
  python scripts/run_two_track_research_v201.py --refresh-channel-facts-if-key-present
This key is not configured in the audited environment. No vidIQ / paid YouTube app needed for public search.

New proposed format fingerprint (creates RESEARCH HYPOTHESIS, not verified winner):
  python scripts/run_two_track_research_v201.py --propose-format "Original mechanic" "unique gameplay-simulation mechanic and audience" NEW_CATEGORY "Document differences vs existing niche"
Novelty review requires independent source evidence from at least 2 sources and an explicit human research review; the code NEVER promotes a newly proposed format from its title alone.

## Confidence and operations

- v1.6.40 search correctly quarantines title/source mismatches for 14 formats.
- v1.6.41 added a broad discovery frontier that can surface suspected previously uncatalogued formats. It does not yet know how to infer an entirely new winning genre without an authorized reasoning agent/independent content viewing: put such clips in UNKNOWN, not "hot winning niche".
- v1.6.41 samples saved 7 real videos from last public scan. Zero validated creation days, zero owner-approved formats, zero two-million-video verified new channels. Honest report should indicate NO_EMPIRICAL_WINNING_NICHE_CONFIRMED, NO_USER_APPROVED_NICHES.
- 2+ different 1M clips and same-format mature demand become a verified signal only after channel age is officially established; monetization never becomes "proven" from those facts.
- Former free search may miss new channels. The preferred way to strengthen date-filter, pagination, creation-age lookups is free-quota YouTube Data API with owned key; this is separate from vidIQ. Public web searches remain helpful but are bounded, not exhaustive.
- Actual competitor video full watch, speech/music/acting movement, exact cut analytics, retention and owner channel revenue cannot be inferred from storyboard stills, metadata or captions. Must use accessible authorized media and sources.
- Automatic Claude Code high-reasoning department remains OFF until the user's account is authenticated and spending/usage policy is authorized; handoff is an inert data file, not an LLM call.
- Separate technical and business gates remain in force. New code cannot automatically run full production, install models, override rights or publish.

## Next completion criteria before calling this "intelligent fully autonomous"

1. Channel birth time from genuinely verified sources across broader channels (official API optional, with quota). Discovery of TWO distinct 1M+ videos on one verified <=30-day-old channel during continuous multi-day checks; cross-check title+visual format identity. No fake ages.
2. Independent deep video watch/analysis where accessible, including audio, script, scene composition, acting, camera, title/thumbnail, actual timestamps, and analysis of multiple channels/videos per specific niche.
3. Scoped signed approval UI for niche + format plus per-niche strategy dossier and new format novelty review.
4. Claude Code connected, scheduled with user budget and security sandbox, able to review source evidence, compare 2-4 methods per stage, propose original creative concepts and repair decisions (not rubber stamp).
5. From owned channel API: CTR, retention, average watch time, allowed reach/impression metrics, copyright status and actual RPM, then improvement loops.
6. Compare accepted-minute production throughput, true human art QC, hardware/license fit and rights across niche-specific engines. No universal Blender/CineFactory renderer for all formats.

No git commit/reset/clean or deployment. Existing company source remains on Windows; this is an actual, bounded, two-stream research mechanism rather than a guarantee of viral income.


## Verified limit of public channel Popular listing

The Maizen channel video URL, both plain and with view=0&sort=p parameters, returned the SAME first three uploads through installed yt-dlp. Consequently the channel's true all-time most popular rankings CANNOT be certified with this URL alone. Branch 2 popular_videos means maximum views among available sampled videos, not a definitive all-time ranking. Requires more complete authorized data and independent verification. This is a declared research limitation, not a silently passed requirement.


## Final verification checkpoint - 2026-10-09

Full repository regression: 1045/1045 tests PASSED, 145.43 seconds, zero failures, exit code 0. Log: data/research/youtube_breakout/logs/regression_v201_final.txt. Compileall PASSED; tracked Git diff check PASSED (Windows line-ending warning only).

The full local Windows scheduled-research script was also manually run end to end with exit code 0: 14 public-source format queries, 20 watch metadata verifications, 3 title/age/length-qualified candidate videos, 18 low-resolution public storyboard tiles, and 1 transient metadata source error; the scan status was honestly RESEARCH_PARTIAL. Then Branch 1 frontier + Branch 2 approval scan were executed and two owner-facing Markdown reports generated. This manual integration run does not certify future automatic execution until the next scheduled trigger. Windows scheduled task was still Ready, next run 2026-10-10 08:00 local time, account login required.

Current actual source state: 0 officially verified new-channel birth dates, 0 owner-approved formats, 0 confirmed new niches satisfying TWO distinct 1M-video evidence requirements, 0 fully played/audio-inspected competitor movies via the free scanner, and 0 paid Claude Code reasoning calls. No installs, upload or deployment performed.

Repo HEAD remains 44e1f5f on studio/v1.6.6-universal-company. Existing working-tree edits are preserved; no commit/reset/clean performed.
