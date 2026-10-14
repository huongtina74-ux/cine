# CineFactory v1.6.35 — Video Production Intelligence

**Date: 2026-10-09. Status: implemented video-evidence advisory layer; not production-certified.**

## R&D goal

Observe actual video pixels and audio where accessible and authorized; derive scoped production tests for specialist departments. Metadata and tool READMEs cannot reveal unseen shot timing, rig, exact video-generation engine, animation/control quality, rights or total accepted-minute costs.

CineFactory must distinguish a verified public video URL from a downloaded, decoded and analyzed recording. Technical pixel statistics must never be promoted into creative approval.

## Implemented modules and operational integration

- cinefactory/studio/video_production_intelligence_v195.py: VideoProductionIntelligence service, bounded VideoReferenceInput, ObservedVideoSignals, ProductionObservationHandoff and niche-specific production alternatives. Wraps existing ReferenceVideoDecomposer, NicheResearchConference and Stage blueprints, rather than rebuilding FFmpeg/CV2. Each method remains CANDIDATE_NOT_DEDUCED_FROM_PIXELS and production_approved=false.
- cinefactory/appctx.py and cinefactory/studio/professional_company.py: shared video_production_intelligence advisor. Existing production engine/workflows unchanged.
- scripts/study_video_production_v195.py: processes 2 owned video clips; optional explicit --live-public-youtube-metadata (single fixed canonical 11-character video ID, no external video download).
- scripts/make_owned_video_review_v195.py: contact sheet of 6 actually decoded owned video frames, with frame index/time/media SHA and decoded PNG SHA. Pixels checked against original CV2-decoded stream. No competitor media retained.
- tests/test_video_production_intelligence_v195.py: 31 focused tests on real owned media, raw/frame hashes, public BigSchool metadata-only, read-only URL scope, rights/paid API restrictions, malformed video IDs/SSRF, no false visual inference, and specialist/conditional QA routing.
- docs/VIDEO_PRODUCTION_INTELLIGENCE_V1635.md: this operating handbook.

## Actual source evidence

| Media | Proof actually established | Scoped observation | Not proved |
|---|---|---|---|
| Owned CineFactory v185 video | SHA and 90 decoded frames (640x360) | 3.75 s, zero detected cuts, camera motion proxy STATIC_DOMINANT, audio silence ratio 0.767 | exact production method from video alone, independent artistic benchmark |
| Owned CineFactory v186 video | Distinct SHA and 90 decoded frames (640x360) | zero cuts; camera STATIC_DOMINANT; audio silence ratio 1.0 | silence being a defect without scene audio requirements |
| Public BigSchool video n3PT62-WX20 | Actual public yt-dlp metadata only | Channel BigSchool, duration 1931 seconds, upload date 2020-10-08, tens of millions of reported views, not live | no video frames, no audio or transcript downloaded; no exact shots, rig or software inferred |

Note: A bounded 12-second opening excerpt request returned HTTP 403 from YouTube CDN. Original licensed/competitor video download DID NOT succeed; raw transient network log was removed, and the research report explicitly does not claim video frames decoded. TubeAlfred had insufficient credits and was not used as a paid alternative.

The owned video contact sheet shows dark classroom/studio frames with voxel actor faces behind foreground desks. This assistant visual review is qualitative and NOT independent human expert signoff. Cinematography review (light/exposure/readability/coverage) is recommended; a static camera and lack of cuts may be intentional, so only conditional QA tickets are generated.

## Technical research/department-specific improvements

- Editing and cinematography: real FFmpeg shot/cut statistics, observed global optical-flow camera motion proxy and exact 90-frame sources; flag STATIC_DOMINANT only as a review request for animated scenes, not automatic quality failure.
- Audio: detect measured near-silent audio stream and request Audio QC only when the scene script calls for speech/music. Do not assume no speech because subtitles were unavailable.
- Preschool 3D Music: organic original rig, original licensed composition/performer, MIDI/beat timeline and song-syllable/viseme sync are separate specialist requirements and tests, not directly derivable from metadata.
- Long Slide/Game: Godot runtime physics and Blender cinematic simulation are alternative pilot candidates; evaluate original same-course deterministic collisions and actual render times, not hidden renderer guesses.
- AI Drama: controlled Blender/hybrid and qualified local ComfyUI model weights are pilot hypotheses. Commercial rights, 12GB VRAM and multi-shot identity continuity remain unmeasured.
- Audio Story/ASMR/Rain: camera/mic/audio mastering pipeline remains central; do not force Blender for every genre.
- QA/Finance: actual quality and cost per accepted video minute remain UNKNOWN until matched golden shot trials, human blind review and restart/retry accounting.

## Security, rights, and provenance

Local media must be under the CineFactory root, explicitly attested owned/authorized, under 180 MiB, and within a maximum configured duration. Hash before/after analysis must match. Public YouTube reference accepts a canonical ID, not a free-form URL or IP; metadata is fetched with --skip-download, and there is no raw media/voice/music archive created for competitors. Source media is never automatically training data or approved commercial stock. The system never triggers paid API, downloads model weights, publishes output or runs unreviewed scripts.

For local video, actual present stream audio and camera metrics are observed, but global optical-flow estimates can be affected by subject movement. Exact Blender/Godot/ComfyUI model choice cannot be reliably reverse-engineered from final pixels.

## Evidence locations (repository-relative)

- data/verification/v195_video_production_intelligence/study_summary_v195.json
- data/verification/v195_video_production_intelligence/v195_owned_voxel_v185_decoded_evidence.json
- data/verification/v195_video_production_intelligence/v195_owned_voxel_v186_decoded_evidence.json
- data/verification/v195_video_production_intelligence/bigschool_public_metadata_only_evidence.json
- data/verification/v195_video_production_intelligence/owned_frame_evidence_manifest_v195.json
- data/verification/v195_video_production_intelligence/owned_actual_decoded_frames_review_v195.jpg
- data/verification/v195_video_production_intelligence/regression_v195.txt

## Next engineering milestones

1. v1.6.36 Authorized actual public video research: where legitimately available, collect bounded frame, subtitle and audio observations using existing ReferenceIntelligence or provider APIs; if content access fails, return unavailable. Aggregate *multiple independent video/channel* abstracts without copying their expressive elements. Preserve copyright gates.
2. v1.6.37 Multi-engine Golden Shot Benchmark: same original 15-60 second shot via >=2 actually qualified engines, blind human visual/audio review, GPU/VRAM/time/retries/watts and cost per accepted minute; adaptive algorithm compares Pareto-optimal choices rather than a static Blender default.
3. v1.6.38 Original preschool musical pilot: child-safe curriculum, original licensed music/voice, organic character rig, syllable/beat choreography, mixed 2D+3D video and reviewer signoff.
4. v1.6.39 Script/shot level art direction and corrective quality gates, with cross-shot camera/audio/actor consistency; reject fake benchmark and spurious copyright grants.
5. v1.6.40 multi-niche production, 4K longform reliability, localization, original characters and release review.

**Current result is real local audiovisual research and public metadata intake, not an AI that has watched every competitor video nor an automatic creator of full-length feature-quality films.**


## Final acceptance — completed 2026-10-09

- **Full existing repository regression: 909/909 PASS, 0 failures, 146.39 seconds**, exit code 0. Previous baseline v1.6.34 was 878 tests; 31 focused v1.6.35 tests all pass.
- **Source compileall PASS**; targeted Git diff check PASS (Windows LF/CRLF warnings informational only).
- Actual media proof: two unique first-party render files at 640x360, 90 decoded frames each; hashes revalidated, audio/video measured with FFmpeg/OpenCV. Six first-party decoded frame PNGs and QA contact sheet created and compared pixel-exact against live CV2 decoder output.
- Real BigSchool YouTube metadata lookup succeeded; **video content not decoded**, 12-second sample HTTP 403, no copyrighted media retained. Video acquisition not a production capability proven by this result.
- The pipeline creates per-niche/camera/audio exploratory suggestions and department review flags but never grants IP rights, auto-publishes, selects a hidden animation engine as fact or claims art quality passed.
- No install, no paid API, no external model download, no versioned repo commit or deployment. Existing production rendering code preserved.
