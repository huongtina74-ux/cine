---
name: r04-competitive-outlier
description: Age-normalized competitor and trend research. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# r04-competitive-outlier

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Catalogues, exact views, duration, publishedAt, channel joined date and timestamp snapshots.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Find all-time leaders, recent 0-30d, new 0-30d channels, short 0-5d warning, 0-15d >=1M; compare same-channel videos at comparable ages when snapshots exist; dedupe canonical ID; retain watchlist after channel ages.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
outlier_board.csv with baseline, count, source, confidence and separate breakout-status.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
0-30d channel with 2 separate A2 >=8min videos each >=1M to confirm; 2 snapshots for VPH, >=3 for acceleration; ratio views/sub never proof alone.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
research
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
