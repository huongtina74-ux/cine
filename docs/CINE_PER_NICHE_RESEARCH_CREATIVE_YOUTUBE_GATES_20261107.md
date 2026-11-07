# CINE — MỘT CÔNG TY, NHIỀU NGÁCH: NGHIÊN CỨU → SÁNG TÁC → YOUTUBE → HỌC HỎI
Verified policy source date: 2026-11-07. Scope: huongtina74-ux/cine; all niches, but NEVER pool research cohorts, editorial canon, or baseline metrics. This is a per-niche operational contract with deterministic validation, **not** a claim every old EXE agent already calls the new tool.

## 0. Authority, names and inventory
- Registry of research subniches: config/research/per_niche/niches.json (currently 10 IDs).
- Target folder config/niches/slow_english_a2 is the **Bell & Leaf package**, wired to niche ID magical_witch_family_stories and series bell_leaf, NOT a synonym for generic slow_english_a2_story.
- Additional local package folders (e.g. minecraft, roblox_animation, animal_long_slide, fishing_silent, rain_sleep_white_noise, asmr_sleep_hands_objects, long_slices_game, audio_storytelling_seniors) are NOT automatically included as active research subniches. Never inherit a nearby genre's sources or business baseline. Register and verify exact subniche identity/official format before claiming E2E coverage.
- Canonical competitor snapshots/track history remain in data/research/cine_per_niche.sqlite via tools/cf_per_niche_registry.py. Do NOT fork an unsynchronized competitor database in a second studio OS.
- Per-niche creative/policy profile: config/research/per_niche/creative_youtube_risk_profiles_v1.json. Verify registry coverage and unmapped packages with python tools/cf_creative_youtube_gate.py inventory.

## 1. Department pipeline — one logical DAG, stage handoffs must have provenance
| Gate | Responsible role | Mandatory real artifact | Fail-closed conditions |
|---|---|---|---|
| G0 Identity & rights | Niche director / Owner | niche_id, subniche, series_id if relevant, intended audience, creative DNA, owner Canon, target market, format, recorded asset rights | Unregistered subniche, inherited default policy, mixed niche |
| G1 Peer discovery | Research | source URLs, stable channel/video IDs, dates, official channel age when known, channel watchlist, source access status | 0 direct peers or URLs missing; unknown ≠ zero |
| G2 A/B/C competitor intelligence | Forensics | separately mature leaders, genuinely new channels, 0–5d early warnings, <=15d million-view candidates, own-channel 5 comparable videos per outlier baseline, timestamped view snapshots | Inferred age presented as official, 2×1M based on same video, fake velocity, cross-niche baseline |
| G3 Actual deep review | Story/AV researcher | legal transcript/AV inspection modality, coverage intervals/timecodes, hook/turn/voice/visual/payoff notes, counter-evidence, provenance | Metadata only claimed as full video, invented competitor CTR/RPM/retention |
| G4 Abstract durable insight | Creative analyst | evidence IDs -> abstract mechanism -> **new** opportunity -> confidence/expiry -> falsifiable hypothesis | Feeding transcript, exact scene/characters, named competitor plot into script generator |
| G5 Original treatment & script | Genre-specific writer | owner/canon check, original DNA, 3 originality axes, precise hook/goals/obstacles/twist/payoff; per-episode dedup when series | Generic templates, identical ending, swapped character/world, unreviewed legal/claim risk |
| G6 Independent reviews | Story editor, rights and niche-policy reviewer | author/reviewer separation, creative originality, age classification, copyright/voice/music/asset license, AI disclosure assessment | Missing decision or invalid evidence; unknown status MUST remain REVIEW |
| G7 Production QC | Audio/visual/packaging departments | voice approval & provenance, visual identity, continuity, actual video/live playback, subtitles separated, music rights, accurate title/thumbnail | Mock/synthetic render mistaken for actual I2V, lip-sync unverified, no audience disclosure decision |
| G8 YouTube publish review | Owner/publisher | YouTube audience designation, realistic altered-content disclosure decision, YPP inauthentic/reused review, Content ID/copyright & ad suitability, privacy | No owner approval, no evidence, automatic claim of "risk free"; no private publish without authorization |
| G9 Analytics & learning | Analytics + independent editor | owned YouTube Studio metrics with date/video_id/chapters/retention; comparison against valid same-channel baseline; tested hypothesis, signed learning decision | Competitor private data fabricated, untested theory promoted to universal writing rule |

One gate ≠ approval of downstream stage. A PASS in CLI preflight means ONLY sufficiently formed input for human editorial review. Even with all decisions present, the preflight returns INDEPENDENT_EDITORIAL_REVIEW_REQUIRED and release_authorized=false. True YouTube/YPP eligibility is up to YouTube and applicable law.

## 2. Per-niche differences, not one universal writing formula
- Family stories for seniors: original emotional dilemma, roles, strong consequence, credible character agency and a distinct ending. No copied anonymous Reddit confession or relationship plot.
- Cozy & sleep: sustained interest in soft emotional movement; acoustic consistency; avoid 200 generic text-to-speech episodes that differ only in names.
- History mysteries / everyday history: date/period/place fact checks, separate documented history from dramatization; original source research and citations; no readings of protected books without rights.
- Science/space/nature: date-bound scientific facts and uncertainty; avoid invented studies or statements of settled scientific certainty.
- Retirement finance: country, jurisdiction, data as-of date, disclaimer and editorial evidence; do not imply guaranteed returns, personalized advice or regulations without verification.
- Software/AI: hands-on evidence, actual version/tool availability and original demonstration; label hypothetical features as experiments.
- Horror original fiction: distinct narrative stakes and resolution, audio/music provenance, ad suitability sensitivity.
- Generic Slow English A2: comprehensible language and original standalone stories; may use broad A2 listening research but never imports Bell & Leaf character assets/continuity.
- Bell & Leaf: all four owner-locked source texts, nine core faces + Elara support, world rules, scene/story continuity and mandatory 1,000-card uniqueness review from docs/story/bell_leaf; do not alter Canon without owner.
- Gameplay, Minecraft, Roblox, Yoga, Brain Break, ASMR, silent fishing, game-animation, rain channels: FIRST register an exact specific peer cohort and ownership/targeting profile. For gameplay use IP and footage licenses/game terms; for yoga/brain break assess child-directed factors on real videos rather than selecting a desired RPM label.

## 3. YouTube policy interpretations that cannot be gamed
Official, current public references:
- Monetization originality, inauthentic/mass-produced and reused: https://support.google.com/youtube/answer/1311392 (renamed 'inauthentic content' July 15, 2025).
- Audience designation / COPPA factors: https://support.google.com/youtube/answer/9528076
- Realistic AI-generated/altered content disclosure: https://support.google.com/youtube/answer/14328491
- Copyright fair use context and case-specific legal complexity: https://support.google.com/youtube/answer/9783148

Original AI-assisted series content is not categorically banned. Reusing cast, series intro or consistent format can be allowed if episodes themselves deliver materially distinct creative value. Many templated episodes, voice reading stolen text or slideshow with minimal added substance may be ineligible for YPP; no tool predicts YouTube decisions with certainty.
- Audience: family friendly / animated alone does not automatically mean Made for Kids; but a teacher-targeted description does not automatically exempt child-directed yoga or classroom content. Examine audience, actors/characters, language, activities, topics, marketing and reality, then designate truthfully.
- Altered/synthetic disclosure: assess the actual output's realism and circumstances; fantastical/stylized non-realistic animation differs from photorealistic fake real events or real-person impersonation. Don't mark "NO" purely because content is AI or "YES" blindly for all animation.
- Rights: A model-generated asset or a platform-supplied soundtrack is NOT automatically cleared for commercial YouTube use; record terms, license scope, voice consent, references and receipts. Fair use not guaranteed by citing a source, changing pitch, or cutting a video.
- Policy review requires independent owner confirmation; do not auto-create release approval from JSON strings alone.

## 4. Required handoff / CLI
A per-episode JSON creative brief may be written to data/... (gitignored). Set exact registry niche_id, exact direct_cohort_key, research.baseline_niche_id equal niche_id, two *distinct* direct video IDs with URLs and observations, one transcript/AV-inspected source with timecoded intervals, abstract mechanism and new original application; three independent originality axes, rights inventory and six explicit policy decision/reason fields. Link learning hypotheses to source IDs.
Run: python tools/cf_creative_youtube_gate.py preflight --brief data/path/to/episode_brief.json --out data/.../creative_youtube_preflight.json
BLOCKED (exit 2): correct errors before agent script/film/publish. INDEPENDENT_EDITORIAL_REVIEW_REQUIRED (exit 0): human review, actual rights and platform settings still necessary. A record's authoring alone is NOT proof that competitor audio/video was inspected.
For Bell & Leaf, provide separate actual uniqueness tool receipt before passing G5. Don't import the 1000 episode proposal as already approved content.
Always log a cross-niche or owner Canon conflict as BLOCKED instead of guessing.

## 5. What is still unverified or incomplete
- Live API ingestion, real AV viewing, captions/comments for EVERY niche, current YouTube Studio analytics and owner approvals: NOT proven by these files.
- New CLI is a formal preflight plus a skill/workflow contract; it is NOT yet demonstrated to be executed inside every legacy CineFactory Windows EXE/Claude agent. No auto publishing.
- Existing canonical registry has 10 research niches, while additional local content package folders require separate registration. This is PARTIAL_CONTENT_ROUTING, not all-niches ready.
- Preflight lexical gates are not a semantic plagiarism detector or a legal YouTube compliance guarantee.

## Owned Analytics → Learning promotion preflight (never automatic)
- Preserve each niche's own public competitor evidence separate from PRIVATE authenticated YouTube Studio measurements. A public competitor URL cannot establish competitor CTR/RPM/retention.
- For a proposed update to script/skill rules, collect an owned experiment: same niche_id + baseline_niche_id; OWNED_YOUTUBE_STUDIO evidence, >=5 distinct comparable baseline videos on same owned channel, treatment video, exact metric/date/duration, intervention, confounders, reviewer independent of researcher, rollback reference and original source receipt.
- Run: python tools/cf_creative_youtube_gate.py learning --brief data/your_niche/learning_event.json --out data/your_niche/learning_review.json
- BLOCKED = no promotion. INDEPENDENT_LEARNING_REVIEW_REQUIRED = candidate for analyst/owner review only. No CLI output can write/approve a skill change, forge Studio authorization or prove causation. Version and roll back any owner-approved change before using it in the next cycle.
