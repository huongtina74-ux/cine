---
name: s02-character-bible
description: Distinct original characters and relationship engine. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s02-character-bible

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Approved premises, target audience, thematic promise and story-world rules.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. For each lead define WANT/NEED/FEAR/FLAW/CONTRADICTION/CHOICE/CHANGE; give each supporting character their own goal and unmistakable voice; define relationships, recurring family rules and authentic contradictions.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
character_bible.md + relationship_state.json.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Characters must cause events through plausible choices; forbid magical adults fixing everything on demand.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
character-management, worldbuilding
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
