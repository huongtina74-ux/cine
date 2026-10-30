---
name: r02-audience-jtbd
description: Audience segmentation and viewer jobs-to-be-done. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# r02-audience-jtbd

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Verified comments, learner interviews, optional authorized Studio Analytics, channel stories.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Build behavioral and motive segments independent of age; distinguish children's appeal from actual child demographics; record jobs, pain, context, desired emotion, learning benefit and contrary evidence.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
audience_segments.md with at least four hypotheses, explicit confidence and evidence links.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Do not invent children %, geography, sex, country or watch time; specify what would falsify each segment.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
reader-panel, research
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
