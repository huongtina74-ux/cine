# CINE / BELL & LEAF — MUSE 3D ANIMATION IDENTITY LOCK PROTOCOL V2
**Date:** 2026-11-06 | **Status:** producer workflow proposal on story branch, not implemented Muse API or successful I2V acceptance, not merged active `main`.

## A. Identity and visual invariants
The show is a **STYLIZED 3D COMPUTER-ANIMATED FAMILY FANTASY**, not live action or real human photorealism. Each I2V clip starts with the **actual approved one-frame 16:9 CGI image** from the shot. Keep the original source character model and stylistic look on all generated frames: stylized head/face sculpt, eye spacing, mouth/nose placement, skin/fur shader, body proportions, hair, costume, original age, relative height, props and environment. "Realistic rendering" is allowable only for lighting and CGI material behavior; never change animated faces into photographic real actors. Film is D55 ~5500K neutral, no warm/yellow drift, 50mm moderate shot, slight depth of field. One take 10s, physical acting, not just zoom. No subtitles, text, contact sheet, nine-grid, split screen, unintended extra characters or image morphing.

**Character-tag reference rule:** ACTIVE TAGS list is per-shot only. Attach image references to actual UI character-reference slots only for tagged visible characters. A shot without an approved character never uses random character ref images. The actual I2V source FIRST FRAME must always be a SINGLE approved shot image, never a 3x3 composite. If the specific model offers a separate character-reference mechanism, use it according to the verified operator documentation, but do not confuse that with its input video frame. Preserve original master tag identities and reference/asset revision per character.

**Canonical body cues:** EVAN nonmagical human father; MARA original adult female witch; JUNO age 13 invented BIX; LIA age 11; BIX compact turtle-pangolin robot with NO bell; BUBU a SMALL original purple cat bell-spirit with exactly ONE gold neck bell and a constantly SPARKLING SPIRAL PURPLE TAIL; ORIN original elder wizard; GRANDPA_EARTH/GRANDMA_EARTH ordinary human grandparents. Reuse original user-approved visual images, not substitute generic stock CGI or photos.

## B. Image-first production gates
1. Retrieve current true canonical reference images and approved location views. Record `CHARACTER_TAG, CHARACTER_MASTER_ASSET_ID, REVISION, SHA256`, `LOCATION_VIEW_ID`. Never fabricate a missing visual.
2. Generate **ONE** 16:9 Flow CGI shot for the exact script timestamp. Inspect character face/age/wardrobe/tail, composition and location before any I2V.
3. Run Muse IMAGE-TO-VIDEO with the approved image as actual frame 0, only real supported reference slots and the per-shot prompt. Ask 10s/16:9; verify model name/version, actual runtime, FPS and output resolution instead of claiming a native 1080p/24fps output that the UI did not confirm.
4. If video shows face becoming a real person, age/skin change, new cast, changed Bix body or vanished Bubu sparkle, FAIL and regenerate from exact first frame after reducing shot complexity (one/two visible speakers, smaller head rotation, simpler camera and shorter action).
5. Check output at 0/2/5/8/end seconds. Reject face drift and no-motion zoom. Approve only after independent visual QC.
6. Assembly: 18 × 10-second shots into EP001 trailer, with consistent character master WAV, SFX, music and original/noninfringing score.

## C. VOICE MASTER / lip-sync contract
Do **not** assume a textual `VOICE_MARA` or `VOICE_BUBU` token is a real Muse speaker-embedding lock. Keep each character's approved WAV independent and immutable, with per-shot script and emotion/time window. If the EXACT chosen Muse engine proves uploaded-audio lip-sync conditioning, condition on the master WAV and verify waveform-to-mouth alignment; otherwise render visuals without new AI-generated speech and run validated external lip-sync afterward, keeping original WAV audio in final mix. Native-audio previews may be useful but they are not a substitute for fixed master voice acceptance. No unapproved extra dialogue or face-specific mouth movement on silent characters.

## D. Model/website research caveat — 2026-11-06
Several unrelated sites use the terms Muse AI / Muse Video. **Meta** publicly previewed Muse Video July 7, 2026 and specifically noted it was improving audio-video synchronization and fast-motion physics. **Meta** confirmed September 15, 2026 that Meta One includes expanded video generation powered by Muse models, without verifying a universal stable Character ID, public Video API or WAV lip-sync conditioning. Third-party sites can have completely different reference-input counts, maximum prompt lengths, durations and resolutions. Old `muse.ai` video-hosting platform rebranded Skiv on March 3, 2026; it must not be confused with Meta Muse video generation. Therefore do not hard-code reference count, API, resolution, native voice lock or false 'we rendered on Muse' claims.

Official sources:
- https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/
- https://about.fb.com/news/2026/09/introducing-meta-one-subscription-service-more-features-ai/
- https://muse.ai/blog/muse-ai-is-now-skiv

## E. Full and compact prompt packs
The EP001 trailer currently has 18 × 10.0s = 180s. Two local output formats are produced for owner upload: **FULL** director prompts and **COMPACT ≤2490 chars** per-shot I2V prompts for potentially limited third-party prompt fields; both have 18 one-line prompts separated by exactly one blank line, and both have matching Flow image preparations in TXT+PDF. These files were generated in the current response's conversation artifacts and need owner-approved source character images to actually run. Character-specific identity lock is only appended to BUBU/BIX-active shots to prevent unnecessary extra character hallucination. 

## F. Three test shots before paying for a full batch
T01 MARA CGI talking medium close-up; T02 BUBU's little bell & full sparkling purple spiral tail visible throughout; T03 MARA + JUNO speaking two-shot. Inspect middle and last frames, not just first. Acceptance = original CGI animation style, original faces/outfits unchanged, actual body/facial motion and controlled audio/lip-sync processing. If any FAIL, correct source references/shot complexity or confirm model capabilities before scaling to all 18 clips.

**Do not claim these textual rules mathematically guarantee 100% identity preservation. For long-running 1,000-episode animation, approved image anchors, consistent engine version and per-shot identity QC are essential.**