---
name: s13-originality-and-kids-safety
description: Originality, IP and audience-intent compliance. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s13-originality-and-kids-safety

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Script, competitor evidence, intended audience, character names and real-world behaviors.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Check accidental plot duplication, reused popular-character names or copycat title/thumbnail, unsafe behavior modeling, stigmatization, cruelty, and child-directed vs mixed-audience classification for platform compliance.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
originality_safety.md with risks and remediations.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Children-like appearance alone is not demographic proof; correct Made-for-Kids assessment requires actual intent and content, not a monetization shortcut.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
editorial-review, research
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
