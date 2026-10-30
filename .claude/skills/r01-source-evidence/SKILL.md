---
name: r01-source-evidence
description: Provenance ledger and evidence assurance. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# r01-source-evidence

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Raw YouTube records, URLs/IDs, scrape time UTC, source method, video and channel IDs.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Normalize IDs and observation date; distinguish UI Popularity from ordinary sort; label METADATA_ONLY, TRANSCRIPT_REVIEW or FULL_AV_REVIEW; reconcile video and subscriber discrepancies; attach source to every claim.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
evidence_register.json with id,url,observed_at_utc,method,claim,confidence,limitations.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Reject undocumented timestamps, invented engagement, raw inaccurate follower values, and claims about private competitor analytics.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
research
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.
