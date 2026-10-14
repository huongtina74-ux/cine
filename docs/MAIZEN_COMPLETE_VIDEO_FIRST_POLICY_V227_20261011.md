# CineFactory v227 — STRICT FULL-VIDEO-FIRST production research gate

Owner instruction (2026-10-11): **Never analyze how a competitor produces an episode from 10s clips, sparse thumbnail mosaics, transcripts or chapter titles. Every source video used to draw a production conclusion MUST be watched in its entire moving visual runtime WITH its original audio, then compared and deconstructed.** This is a studio-wide rule, explicitly enforced in Maizen Studio A.

## What has been implemented

- New policy `config/niches/minecraft/maizen_full_video_policy_v227.json`: all selected reference videos are mandatory; Maizen's initial 3 full episodes, total **3,832 seconds (1h 3m 52s)**, each visual-and-audio timecode window <=30s.
- New `cinefactory/studio/maizen_full_video_gate_v227.py`: verifies timestamp coverage from 00:00:00 to the full YouTube duration, evidence of moving footage and sound for EACH interval, nontrivial human/reviewer notes, original local file SHA, full decode receipt with video/audio streams and matching video ID, and independent evidence review. If any video/interval/sound/receipt is missing, the whole cohort is BLOCKED.
- New `cinefactory/studio/maizen_media_decode_v227.py`: **explicit offline command only** checks a locally provided complete authorized video, ffprobe duration/video/audio tracks, decodes the ENTIRE video stream and audio stream with FFmpeg (can take minutes), then writes a SHA-bound receipt. This does not replace visual/audio interpretation.
- New CLI `maizen-full-video-review`: check locked status, create blank 30s study worksheets with `--prepare-templates`, query individual JSON worksheet using `--video-id <id>`, and explicitly validate legal full local source with `--video-id <id> --verify-local-media`.
- Claude Code first-party read-only MCP tools: `maizen_full_video_review_gate` and `maizen_full_video_review_template` alongside earlier Maizen status, per-shot methods and full 26-department plan. Pending human project MCP approval cannot be bypassed.
- Company-wide `technology_council_v212` now states the rule for all 26 departments and all company DAG stage advisories: entire film+original audio are required before any competitor-specific production-method conclusion; short samples cannot replace that evidence.
- The selected MAI01 `maizen_studio_status`, `maizen_department_work`, `maizen_production_method_audit`, `minecraft_company_roadmap` G03–G28, and first blocker display must honor the full-watch gate. Existing v225 completed desk planning receipts and v226 research method hypotheses remain HISTORICAL PRELIMINARY DRAFTS, NOT new production approvals.
- Future videos added to the policy's required references join the compulsory cohort; all are fail-closed until full visual+audio evidence is verified. Each added video needs independent source metadata verification.

## Required initial reference cohort

| Official source | Duration | 30s or shorter windows | Full source A/V reviewed? |
|---|---:|---:|---|
| Maizen – https://www.youtube.com/watch?v=ZmT0ITUGUII | 28:04 | 57 | NO |
| Maizen – https://www.youtube.com/watch?v=zhPBXzHsLuo | 18:37 | 38 | NO |
| Maizen – https://www.youtube.com/watch?v=oX6Azwe5QLg | 17:11 | 35 | NO |
| **TOTAL** | **1:03:52** | **130** | **0/3 verified** |

### Only acceptable input

The reviewer must legitimately access full original moving video+audio, confirm video ID and duration, keep its source material outside Git and outside paid AI providers, and actually watch/listen through all content. A full decode via ffmpeg alone does NOT mean footage was watched or understood. A blank worksheet, thumbnail preview, metadata, translated transcript, or a claimed screenshot is NEVER a substitute.

Each <=30s worksheet interval has separate OBSERVED picture and OBSERVED sound, dialogue summary (or explicit observed silence), acting, camera/edit, stage/props, method hypotheses labeled HYPOTHESIS and remaining uncertainty, with an evidence frame timestamp inside that window. Source media SHA, verified full ffprobe/ffmpeg decode, viewer attestation AND a separate reviewer audit of all intervals are mandatory. The study agent must distinguish actor skill/game commands/assets from verified *proprietary* renderer: an entire episode still does NOT reveal the exact software if not officially disclosed.

## The seven CineFactory departments / handoff sequence — STRICT ORDER

1. **Research (G01/G02):** identify official longform video, get allowed complete A/V, verify file and metadata; WATCH EVERY SECOND and log all 130 windows. No claim based on snippets.
2. **Competitor deconstruction (G03):** AFTER full A/V: independently reconstruct opening hooks, characters, motivations, target goal, events, escalation, every reveal, climax, chapters and timing, with timestamps; compare multiple full reference films.
3. **Script Room / Script Logic (G06/G07):** only from accepted full research findings; original Nova/Pip 14-minute story, unique narrative, English dialogue, per-scene motivations, causal beats and logic. Prior v225 drafts not approved.
4. **Production Design / Assets / Character & Acting (G09–G11):** derive original world/scene needs, character rig movement and expressions **only from evidence**, then create original skins, stages, props, animation methods, identity/rights. No JJ/Mikey copied assets.
5. **Technical Director / R&D (G13/G16):** compare verified OBSERVABLE production mechanisms and known vendor evidence; choose Blender CG vs authored Minecraft game stage vs hybrid PER SCENE. Do not infer a proprietary renderer from appearance. 10-second clips may later test local GPU/rig technically, NEVER justify competitor analysis. Backend benchmark needs independently approved full-length final output metrics.
6. **Audio / Editorial / Color (G20–G22):** study actual source soundtrack from start to finish (dialogue, voice actor/dub, ambiences, SFX/music, clip sync, score) and temporal editing/camera/color; design licensed original audio and timeline accordingly.
7. **QC / Management (G23–G26):** independent verification of EACH source review and ENTIRE first-party produced final video+audio, attribution vs hypothesis, original content/IP rights, true elapsed accepted render time and release signoff; no production-promotion or auto-upload before approval.

Stage **G01/G02 may continue metadata and A/V acquisition. All G03–G28 MAI01 planning/technique/production conclusions remain BLOCKED** until complete reference evidence is approved. Even after reference gate passes, this is NOT production or publishing permission: licensed assets, cinematic quality, voice rights, and real 8–14min output must independently pass.

## How to operate on authorized full copies

Save legal reference clips on the Windows CineFactory machine as:

- `data/research/maizen_source_media/ZmT0ITUGUII.mp4`
- `data/research/maizen_source_media/zhPBXzHsLuo.mp4`
- `data/research/maizen_source_media/oX6Azwe5QLg.mp4`

MP4, MKV or WEBM are accepted; each filename must be the exact video ID. Ensure the source has both full video and sound. Do NOT commit copyrighted reference copies.

```powershell
python -m cinefactory.cli maizen-full-video-review
python -m cinefactory.cli maizen-full-video-review --prepare-templates
python -m cinefactory.cli maizen-full-video-review --video-id zhPBXzHsLuo --verify-local-media
python -m cinefactory.cli maizen-full-video-review
python -m cinefactory.cli minecraft-company-roadmap --lane SCRIPTED_MINECRAFT_GAMEPLAY
```

Three BLANK report files are generated to `data/verification/v227_maizen_full_video_reports/<ID>.json`. No report should be marked watched until a reviewer examines full media and fills all 30-second intervals with grounded observations. The reviewer and independent auditor must be different identities. Never auto-populate generic observations or claim false playback.

### Actual status as of 2026-10-11

Source YouTube embedded/downloading through workstation at one 10-second Maizen excerpt yielded HTTP 403; TubeAlfred transcript tool yielded 402 insufficient credits (0 credits spent). Only v224 public thumbnail preview+metadata are currently available. **No legally obtained full source media has been verified; all 3 full watches are PENDING; no technical conclusion or production approval is allowed.**

Security: explicit offline full decode uses local ffmpeg only and doesn't access YouTube, external OAuth/paid APIs, nor auto-install. Reviewing content is nontrivial and cannot be truthfully automated solely by ffmpeg decode. A second independently grounded picture+sound reviewer remains required. The historical 26 v225 desk receipts are preserved, not silently rewritten.
