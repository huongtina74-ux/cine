---
name: s12-a2-comprehension-check
description: English listening readability and comprehension gate. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s12-a2-comprehension-check

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Final dialogues, A2 communication objectives, measured learner feedback when available.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Separate automated grammar/readability checks from real learner comprehension; review referents, pace recommendations, repetition, learner ability to retell causality, vocabulary overload and unnatural textbook lines.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
a2_qa.md with per-scene issues, suggested rewrite and HUMAN_TEST_PENDING status.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Do not assert CEFR A2 certification from automatic analysis; record missing learner tests explicitly.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
line-editing, reader-panel
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
