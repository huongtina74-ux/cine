---
name: s11-adversarial-story-editor
description: Independent Story Doctor structural critique. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s11-adversarial-story-editor

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Full screenplay, intended audience, rival evidence, concept scorecard.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Audit character agency, weak/confusing opening, unjustified middle, predictable escalation, false suspense, flat dialogue, audience boredom, unearned twist and episode repetition; cite scene/line; prescribe causal rewrites.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
story_doctor.md with critical/major/minor issues and rewrite proposals.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Do not rubber-stamp author's self-scores; no script lock with unresolved critical problems.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
editorial-review, feedback-triage
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
