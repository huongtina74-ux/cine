---
name: s08-professional-screenplay
description: Scene-formatted filmable screenplay prose. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s08-professional-screenplay

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Approved treatment, character bible, dialogue and story beats.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Write INT/EXT locations, action observable by camera, character cues and English dialogue; use subtext, decisions, transitions in motivation; give every scene goal/obstacle/change. Avoid fixed shot lenses or visual-generation instructions.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
screenplay.fountain and scene_index.csv.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Every scene serves causality; no unnatural narration dump, no incoherent prop/time state.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
scene-craft, chapter-writing
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
