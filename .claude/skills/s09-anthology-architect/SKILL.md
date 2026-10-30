---
name: s09-anthology-architect
description: 30-50 minute anthology pacing from standalone stories. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s09-anthology-architect

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Five to seven reviewed 5-8min stories, recurring series world, audience preferences.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Curate opening story with strongest promise; vary protagonist, conflict, emotion, speed and endings; ensure truthful title describes initial story, preserve each mini-plot's payoff, optionally add cross-chapter running theme.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
episode_map.md with story durations, tones, audience reasons and transitions.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Do not pad length by multiplying clones; do not count individual mini stories below 8 min as >=8min viral test videos.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
series-continuity, plot-structure
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.

## NON-NEGOTIABLE FINAL EPISODE LENGTH
The ONLY finished deliverable is one fully written 30–50 minute Slow English A2 video screenplay (default target ~40m), not merely 5–8 minute standalones or a 40m outline. Segment writing is an INTERNAL tool. Before marking the script ready:
- Specify whether observed evidence supports a multi-story anthology or a continuous film-like narrative.
- Write EVERY scene and line across the full target span; no unfilled write-later chapters.
- Keep timing by story/act/scene; estimate spoken dialogue and action pacing, then require a timed read to verify actual runtime.
- Evaluate promises and payoffs of each unit AND the 30–50m viewing experience.
- Apply editorial, A2 and originality checks to the entire long-form episode, not only the first chapter.
Mark EPISODE_SCRIPT_INCOMPLETE if only sample, synopsis or beat sheet exists. Mark RUNTIME_UNVERIFIED without actual timed read.
