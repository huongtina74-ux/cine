---
name: r03-comment-insight
description: Viewer voice, complaints, learning value and anti-preferences. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# r03-comment-insight

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Comment samples from popular, median, recent and weaker videos with provenance.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Filter obvious creator comments/spam if possible, remove personal names, code requested topics, emotions, ESL comprehension, quality complaints, preferred characters and objections. Track independent commenters/videos/channels and how sampling biases conclusions.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
comment_insights.md and coded_comment_sample.csv with counts and example paraphrases.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Never treat self-selected comments or emoji-only comments as a demographic sample.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
research, reader-panel
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
