# CineFactory P0 — Deep Video Evidence, real testing 2026-10-09

STATUS: PARTIALLY IMPLEMENTED, LIVE PUBLIC THUMBNAIL AND AUTHORIZED LOCAL FRAME/AUDIO OBSERVATION VERIFIED. **Automatic semantic video understanding is not yet verified.**

## Scope and non-invention policy

Automated search/collector remains solely in `Company Youtube`. The CineFactory module `deep_video_intelligence.py` extends the existing `evidence_research.py`, `smart.py`, `core.py` and CineCouncil workflows rather than creating separate independent decisions.

Two source modalities are deliberately separate:

1. **PUBLIC_YOUTUBE_THUMBNAIL**: public YouTube thumbnail bytes from the exact validated `video_id` and allowlisted `https://i.ytimg.com` host. JPEG MIME/size/dimensions validated. Record file SHA256, width, height, RGB mean and luminance range as *direct image measurements*. All semantics, hook, video frames, sound, dialogue, retention, CTR, copyright clearance remain `UNKNOWN` or `NOT_OBSERVED`. No video stream is downloaded from YouTube.
2. **AUTHORIZED_LOCAL_VIDEO**: requires a real local video file explicitly marked `OWNED`, `LICENSED` or `USER_PROVIDED_WITH_PERMISSION`. Uses existing `observe_smart` plus ffprobe/ffmpeg, optional OpenCV change heuristics; creates selected frame JPEG files, hashes, timestamps, track types, audio-volume measurement for first 120s, and separate pending department task files. The authorization is *declared* by the caller and is not independently verified by CineFactory.

Neither source produces an automatically verified plot, pacing, audience retention, animation quality, licensed status, or psychological causal explanation. Those require actual content inspection and review.

## Architecture and provenance

Public chain: canonical Company public search → selected canonical catalogs → `evidence.json` with frozen source hashes → **one unchanged `council_issue.json`** → Deep Video evidence → department tasks. The Deep Video review references the exact original issue SHA256; it must not create a competing arbitration result. It is one YouTube public lineage even when collected by different methods.

Implemented:
- `prepare_public_video_review`: bounded 1–12 images; prioritizes fresh on-topic million-view hits, mature leader samples, then newcomer video candidates. Never chooses a title deliberately excluded by topic QA. Writes `deep_review.json` and JPEG evidence into a new immutable run folder; missing images are explicit `THUMBNAIL_UNAVAILABLE`.
- `verify_deep_video_review`: rechecks original `evidence.json` hash, shared council issue hash, ID/title/channel/URL match, each JPEG's SHA256 and image measurements, and refusal to magically promote semantic statuses. This acts as a fail-closed replay integrity check; hashes are not cryptographic author authentication.
- `observe_authorized_footage`: bounded 2–48 frames from the actual local file with optional scene-change hints and FFmpeg audio stats; queues Story/Visual/Animation/Audio/Editorial/Packaging/Quality tasks as pending approval.
- `evidence-live --deep-thumbnails N`: optional end-to-end single command. Maintains same canonical `council_issue.json`. No new YouTube Data API call or paid LLM usage.

## Live trials on Windows DESKTOP-HJE6A6D

### Test A — Public YouTube evidence, real images
Source: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_03\evidence.json`
- Selected video `Wq6KnyIErYs`, Minecraft animation on GameToons, approximate public display 1.3M views, video ~21 days old.
- Actual thumbnail downloaded from `i.ytimg.com`: 480×360 JPEG. Stored SHA256 and RGB/luminance facts; no claim video footage was observed.
- `deep-video-verify` matched original shared issue `review-minecraft-animation-e7c8c6f76885`. Review status pending.

### Test B — One-command end-to-end fresh live sample
Run directory: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_04`
- `state=REVIEW_PACKET_CREATED`; 6/6 channel catalogs successfully collected, 34 usable longform video public observations, 2 mature leader channels, 4 mature channels with recent on-topic >=100k public displayed view proxies.
- 3 videos with public display >=1M within displayed approximate last 15 days, all from **ESTABLISHED channel MSToons**, not a new 0–30 day breakout channel:
  - `W7R8k10Kjfk` ~1.3M, ~6 days;
  - `qtWfSIqNfdU` ~1.3M, ~4 days;
  - `7wQK-YJOu4o` ~1.2M, ~13 days.
- 3/3 thumbnail JPEGs downloaded and integrity checked. All `actual_video_frames_status=NOT_OBSERVED`, `story_hook_status=UNKNOWN`. Owner approval remains false.
- Same issue `review-minecraft-animation-89e6a8455f08`; no parallel decision allowed.
- Council issues and evidence registry: `...\evidence_live_04\council\`
- Human-readable research report: `...\evidence_live_04\evidence.md`
- Machine evidence: `...\evidence_live_04\deep_intelligence\deep_review.json`
- Full run manifest: `...\evidence_live_04\live_run_manifest.json`

### Test C — Real FFmpeg over synthetic OWNED local video
- Generated local four- and twelve-second clips from FFmpeg synthetic testsrc + tone, NOT third-party YouTube footage.
- Called `deep-video-local --authorization OWNED`; one live example extracted 8 actual JPEG frames plus measured audio track. Captured exact timestamps/frame hashes and 7 pending department tasks. Frame evidence is real for the synthetic file, NOT proof of any watched YouTube video.
- Local sample run `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\synthetic_observed\`.
- Independent tests created a 4-second clip and required real generated frames + audio and unapproved departments.

### Transcript experiment
On a public Minecraft video, `youtubei.js getInfo` returned title, duration and thumbnails, but `getTranscript` returned `Transcript panel not found`. The parser showed compatibility errors against YouTube's evolving components. Hence transcript coverage for that sample is **NOT AVAILABLE FROM THE PROBED METHOD**, not hallucinated. A robust legal/authorized transcript source and availability monitor remain needed.

## One-command PowerShell execution

Working directory: `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`

```powershell
python -m cinefactory.research_intelligence evidence-live --company-root "C:\Users\ADMIN\Downloads\Company Youtube" --queries-json "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_01\queries.json" --youtubejs-entry "C:\Users\ADMIN\AppData\Local\Temp\ytseo-youtubei-runtime\node_modules\youtubei.js\dist\src\platform\node.js" --output-dir "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\NEW_UNIQUE_RUN" --niche "Minecraft animation" --max-channels 6 --max-results 7 --videos-per-channel 12 --deep-thumbnails 3 --timeout 120
```

When local authorized MP4 footage becomes available:

```powershell
python -m cinefactory.research_intelligence deep-video-local --source "C:\path\owned_or_licensed.mp4" --output-dir "C:\CineResearch\unique_video_review" --niche "Minecraft animation" --video-id "XXXXXXXXXXX" --authorization OWNED --max-frames 16
```

One may also check any public review for integrity:

```powershell
python -m cinefactory.research_intelligence deep-video-verify --review "C:\...\deep_intelligence\deep_review.json"
```

## Test safety and remaining gaps

- No pay-per-token calls, YouTube authentication or publication.
- Source/channel/video identity checks; public-only site allowlist; JPEG byte & dimensions caps; no arbitrary supplied HTTP URLs.
- Mutated evidence or thumbnail/issue fails closed; impossible auto-promoted semantic states are rejected; missing thumbnail remains unknown.
- Formal model review is **not yet invoked**. Department tasks are prepared but not completed: need local/authorized video or visual-capable tool to examine frames, reliable transcript coverage, structured agent reports with timestamps and adversarial Quality council.
- Metadata public proxies may not represent actual organic recommendation traffic, precise views, YPP approval or RPM.
- The YouTube collector may change with public markup. Cross-topic title gate is a guard, **not actual semantic video classification**.
- Need owner approval and verified rights before production/publication; this step is not P0 acceptance.

Engineering state should be derived from the final tests/commit in the session.
