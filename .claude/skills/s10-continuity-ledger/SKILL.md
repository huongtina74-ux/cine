---
name: s10-continuity-ledger
description: Character, object, place, timeline and setup/payoff consistency. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s10-continuity-ledger

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Complete scene draft, character/world bible, beat sheet, dialogue and prop inventory.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Track who knows what when, where objects are, motivations, world rules, chronology, promises, completed/future payoffs; identify line-specific contradictions; use Story Skills continuity engine only after adapting fields.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
continuity_issues.csv + continuity_pass.md with severity and status.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
All critical timeline/knowledge/prop inconsistencies must be closed before script lock.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
revision-continuity, series-continuity
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
