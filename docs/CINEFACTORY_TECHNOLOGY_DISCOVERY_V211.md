# CINEFACTORY V211 — Technology Discovery in Niche and Competitor Research

Date: 2026-10-10. Repository: `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`.

## What is integrated

The existing v210 Technology Radar has **96 curated entries** across image, video, 3D, motion, voice/music, ComfyUI, post, SaaS and R&D. v211 makes this list useful across the production company, while allowing Research to discover *more* references when studying a niche or competitor channel/video.

1. **Niche classification**: v208 source-video metadata classifier identifies each video format separately, including Minecraft scripted Blender film vs actual captured gameplay vs livestream vs machinima. Mixed-channel cases are not collapsed into one production workflow.
2. **Department recommendations**: `technology_discovery_v211.propose_technology_for_format` maps niche format to media-production family, gives a bounded candidate shortlist from the full 96, records license gates and the responsible department. Never claims to know which tools the competitor actually used.
3. **Company blueprint**: `CompanyBlueprint.technology_research_advisory` carries the same advisory into the original studio project plan, without changing the executor, licensing or authorizing render.
4. **Competitor forensics**: `channel_forensics --channel-url ...` writes a `technology_advisory.by_metadata_format_candidate` alongside channel/video results. Real live-channel research now **automatically** performs at most two individual niche-format research bundles (one public GitHub search and one public Hugging Face model search per bundle) when metadata provides at least two video matches for a format. Use `--no-discover-public-repos` to opt out. User-supplied `--snapshot-json` remains OFFLINE even with the discover flag, so untrusted source fixtures never cause network requests.
5. **Daily niche research**: Windows scheduled script `scripts/daily_cinefactory_research_v199.ps1` now invokes the existing `run_two_track_research_v201.py --discover-technologies` in addition to --with-frontier/--scan-approved. This ROTATES two configured research formats/day across the seven CineFactory core niche branches and different Minecraft production modes, even if no new winning niche has been verified. It adds real public tech candidates to R&D but **never marks them as victorious niches**.
6. **Bounded source readers**: Public GitHub Search API and Hugging Face public model listing, fixed HTTPS origins, no auth header, no private API secrets, no paid model API. Results are public metadata only, 1 query each by default, 5 GitHub / 4 HF results maximum and small response/time budget. Queries are static format-technology search language, not copyrighted competitor titles.
7. **Pending immutable artifacts**: New source metadata creates content-addressed, append-only JSON receipts at `data/research/technology_discovery/events/github_<sha>.json` or `hf_<sha>.json`. Existing v210 entries are de-duplicated; repeat discoveries are de-duplicated against existing pending IDs. Some source records may include an **unverified vendor homepage hypothesis**, which is never fetched as part of v211.
8. **Strict advancement**: No event writes to approved v210 registry, installs custom ComfyUI nodes, downloads checkpoints, clones or executes unknown repositories, turns on paid APIs, picks a new production backend, uses other creators' characters, or authorizes YouTube publication. Actual qualification remains governed by v209, the original Tool Catalog, candidate acquisition/security gates and owner authorizations.

## Examples

- **Minecraft School Comedy** -> `FILM_3D`: original Blender rig, character concept art, qualified voice, music, sound/post; not a captured-gameplay studio.
- **Minecraft recorded survival** -> `GAME_CAPTURE`: original real gameplay footage capture and FFmpeg/Whisper/Remotion-type post, not a fictional Blender story or an AI-generated fake stream.
- **Minecraft live player** -> `LIVE_CAPTURE`: real runtime and stream capture; NOT eligible for longform-film view breakouts.
- **Minecraft staged machinima** -> `MACHINIMA`: actual game staging, not an independently rendered original Blender movie.
- **Audio senior storytelling** -> `VOICE_STORY`: spoken narrative, original/consented voice and music, sound QC.
- **ASMR hands, Fishing Silent, Rain** -> source-specific real media and audio post; generative synthetic visuals are not silently labeled real.
- **Mixed competitor channel** -> separate technology recommendations per sampled subformat with two or more matching titles; no blind reuse across unrelated lanes.
- **Unrecognized video format** -> `UNRESOLVED`, no safe inferred production stack.

## Operator commands

List initial 96 entries:
`python -m cinefactory.cli technology-radar --show-items`

Generate an offline technology recommendation (no Internet and no credits):
`python -m cinefactory.cli technology-discover --minor-niche minecraft_school_comedy --major-niche minecraft`

Find technology candidates from public GitHub and Hugging Face and add ONLY pending receipts:
`python -m cinefactory.cli technology-discover --minor-niche minecraft_school_comedy --major-niche minecraft --public-sources`

Analyze a competitor channel including the v210 shortlist and optionally find new source candidates:
`python -m cinefactory.cli channel-forensics --channel-url "https://www.youtube.com/@EXAMPLE/videos" --max-videos 10 --search-peers --discover-public-repos`

Daily scheduled research calls the technology scout automatically, using the same bounded public sources, without needing paid model API credentials. If an API is offline, rate-limited or returns a malformed response, the scan records a source error and does not promote a candidate.

## Real public-source smoke (2026-10-10)

`technology-discover --minor-niche minecraft_school_comedy --major-niche minecraft --public-sources` was executed on the actual machine. GitHub search returned zero new pending repo records from its limited result; Hugging Face returned one tentative model result whose name referenced a proprietary animation-studio brand. It was recorded as **pending, NOT rights-cleared, NOT quality-verified, NOT downloaded**. The collector was then hardened to filter branded character/style model IDs from future automatic shortlists. Prior historical receipts remain immutable source evidence and are never retroactively upgraded to safe candidates.

The receipt is not a claim that CineFactory observed the competitor using that model, and the model was not installed.

## Quality and source rules

- GitHub repository licence (MIT/Apache) does not clear bundled model weights, music, footage, trademarks, assets, output commercialization or global distribution.
- User-supplied channel descriptions, video titles, README markdown, GitHub description and model card content remain untrusted DATA; no shell execution or AI instructions are derived from them.
- A model name referencing Disney/Pixar/other recognizable characters is not an automatic original-character asset.
- Published YouTube video metadata is not viewing/decoding the visual footage; guessed competitor tool attribution is explicitly false.
- No single model/website is a Disney replacement. Blender scene graphs, controllable character rigs, independent narrative/camera/acting/sound/art QC and exact signed rights/owner gate remain intact.
- Candidate labels are **research hypotheses**, not executable skills, not software installed and not commercial production-qualification.

## Operational limitations

- GitHub unauthenticated Search API has strict public rate limits and may find zero relevant matches. Hugging Face free public model search is not a complete model discovery census.
- Current source adapters do not prove exact model build/license for a discovered search hit; independent source and model card review remains required before promotion.
- Automatic SaaS website discovery from the entire web would require a separately qualified public search connector. The 96 base contains known SaaS sites; an external website linked from a GitHub repository can be stored only as an UNVERIFIED homepage hint; no unbounded browsing or arbitrary URL fetching is performed.
- Production still cannot be marked qualified without accepted original pilot and entire 8–10 minute original film, signed reviews and actual first-party audience analytics.
- Scheduled v211 research will execute in the next normally triggered Windows research task if that task is enabled and invokes the updated local script. This is an integration change, not proof of a scheduled run after this commit.

## Test evidence and rollout

New tests: `tests/test_technology_discovery_v211.py` verify source-truth routing, GitHub/HF public mock response, source normalization, brand guard, safe website hints, immutable receipts, de-duplication, separated gameplay vs animation, offline defaults and company blueprint integration. Regression results govern the final verdict. No output media or paid credits were generated in this upgrade.


## Inspect newly added technology candidates (append-only backlog)

`python -m cinefactory.cli technology-backlog --limit 60`

The command reads `data/research/technology_discovery/events`, verifies each JSON receipt's SHA-256 against its immutable filename and checks that the receipt has **no permissions** to install a model, spend credits, select an unqualified backend or publish. Corrupted/tampered receipts are reported as errors, not trusted. The original 96 candidate registry is kept separate from the ever-growing backlog.

A future R&D approval must inspect the model card/weights, use terms of commercial worldwide release, dependency integrity, local actual benchmark, original scene/voice/art quality and an owner-signed production decision; public search never issues these approvals.


## Audio model search correction from live smoke (10 October)

The real public `VOICE_STORY` search returned four unverified Hugging Face candidate references, including Hindi/Marathi-targeted models and one speech-to-text reference. The first-pass receipts remain immutable (no binaries/weights installed or executed). After detecting this, the v211 collector was strengthened to exclude obviously non-English source-specific TTS names and models whose published pipeline tag identifies a DIFFERENT task such as automatic speech recognition. Existing receipts are not magically commercial-safe just because they are present in the backlog.

This is why pending R&D catalogue growth is NOT production capability growth. Results are not claims that the competitor actually uses those models; even a matching result must pass licence, local RTX3060 benchmark, controlled style identity, first-party voice rights and original audio QC.


## Verification and Git integration (10 October 2026)

- Full CineFactory repository regression: **1,492 passed, 3 failed** (~195.73 sec). The exact failing tests remain the historical Blender-worker v190/v196 SHA provenance checks; worker hash evidence was not changed. Log: `.tools/deep_audit_20261010/v211_exact_final_all.log`.
- Latest v211 + v208 + v210 + v209 focused suite after task/language-specific HF filter changes: **106/106 PASS**. Log: `.tools/deep_audit_20261010/v211_english_filters.log`.
- Local Python `compileall` passed.
- Two actual read-only public-source probes: one Minecraft animation research route and one English-first audio storytelling route. GitHub: **0 newly imported repo records in those bounded searches**; Hugging Face: **5 metadata-only pending references total** before stricter brand/language/task filtering was added. Some earlier records have non-English or branded labels, and remain immutable unqualified observations; no claim those tools meet the English channel requirements.
- Daily Windows PowerShell runner was updated, but a scheduled execution *after the change* has not been verified. It will not install or qualify new tools and errors from public rate-limited sources must remain visible.
- These changes do not resolve preexisting Research P1 BLOCKED, YouTube channel-age evidence, live render worker health, Blender provenance SHA drift, real artist reviews or commercial release readiness.
