---
name: cine-audio-post
description: Prepare CineFactory dialogue, sound spotting, ducked mixes and audio review evidence. Use for unintelligible narration, pronunciation, music masking or subtitle sync.
metadata:
  source-review-date: "2026-10-18"
  qualification: "candidate-awaiting-production-pilot"
---

# Audio post

**AUDIO_BRANCHES_USE_AFANTA_QC:** For the three CINE-to-Afanta Audio-first branches, the CINE config/audio/authority_index_v1.json routes all production/media QC decisions to Afanta studio_os/docs/AUDIO_QC_CANON_V1.md. This film-audio skill applies to CineFactory's own film output and provides advice only, not competing Afanta QC criteria.

Use the selected CineFactory checkout. If required tools, documents or media are unavailable, report the missing dependency and complete only supported analysis; do not invent command results or schema fields. Exercises below are evaluation scenarios, not authorization to render, spend or publish.

Read the script, actual voice files, shot timings and the active delivery profile. CineFactory's -14 LUFS and -1 dBTP values are local delivery targets, not universal platform requirements.

## Method
For evidence-bearing production work, read [references/production.md](references/production.md). It maps this specialty to the executable packet checks, source/use limits and evaluation procedure. In CineFactory, available tools are `tools/cf_professional.py` and the existing stage SOPs.

1. Review voice source and consent/license evidence. Keep pronunciation notes, voice identity and approved takes by character.
2. Build a spotting table: time/shot, sound event, narrative role, source/license, entry/exit and relation to dialogue. Deliberate silence can be expressive; sleep/ASMR work must not inherit dialogue-heavy pacing blindly.
3. Fix edits, clicks, inconsistent room tone and pronunciation before adding music. Forced alignment and ASR are aids; compare important words to the actual audio.
4. Use voice to control music attenuation, with fades and pause behavior appropriate to phrasing. Listen for pumping, clipped consonants and loss of ambience; a ducking flag alone is not a mix review.
5. Preserve useful stems and render through the current auto-edit path. Measure the encoded final mix against the selected profile, including true peak and sync, then listen on the intended playback system when available.
6. Report any missing listening capability. Numerical loudness PASS cannot establish intelligibility, emotion or pronunciation.

## Deliverable and exercise
Deliver voice selection, spotting table, mix settings, measurement report and a listening record with exact intervals.

Exercise: music returns loudly between every short sentence. Change one envelope/pause setting, compare the same 20-second passage and record whether pumping and word masking improve. Pass requires an actual listening observation or an explicit awaiting-listening result.

## Sources and coverage
- [Audacity Auto Duck manual](https://manual.audacityteam.org/man/auto_duck.html): technical page read on 2026-10-18; control-track synchronization and fade/pause behavior reviewed.
- [Blackmagic training](https://www.blackmagicdesign.com/products/davinciresolve/training): Fairlight lesson descriptions reviewed; long-form lessons not completed.
- The spotting, listening record and experiment are original CineFactory procedures.
