---
name: s03-micro-hook-designer
description: Strong but honest first thirty seconds. Invoke only within CINE A2 research-to-screenplay text workflow.
---
# s03-micro-hook-designer

# CINE A2 SCRIPT ROOM
This is an original Agent Skill designed for the CINE A2 Research → Screenplay pipeline.
It is not an image/voice/video generation module. It does not independently connect to YouTube or produce real evidence. Invoke with actual input files and keep immutable evidence citations.


## Inputs
Approved logline, target emotion, title promise, character desire and world rules.

## Method
1. Validate the actual evidence provenance and audience hypothesis status.
2. Generate 3 different openings: cold open, visual cause/effect, meaningful problem; locate trigger in <=30s if story supports it; create immediate dramatic question without explaining the whole plot.
3. Identify at least one competing interpretation or counterexample.
4. Draft the deliverable, with machine-readable references when available.

## Output contract
hooks.md with opening line, action, question, stakes, originality and language notes.
State EXACT confidence labels: VERIFIED, SUPPORTED_HYPOTHESIS, SPECULATIVE, UNKNOWN, or BLOCKED; include source video/channel IDs and timestamps for claims grounded in competitors.

## Blocking quality gate
Hook must occur in the actual first mini-story, not mislead via compilation title or manufactured threat.
If gate fails, return BLOCKED and explicitly list missing evidence. Never make up datasets, video watch histories or test results.

## Optional installed Story Skills references (upstream MIT repository, read not auto-invoke)
scene-craft, premise-workshop
Upstream cloned at: ../../repos/story-skills/skills/ ; its prose writing workflow is not automatically equivalent to A2 screenplay workflow.

## Handoff
Save output to a named file in the project; include input artifact IDs and any unresolved risk. Do not transition to imaging, audio or video production.

## Required first-15-second hook for EVERY Bell & Leaf episode (2026-11-09)
The 0-10 second opening shot S001 MUST create a TRUE, clearly visible, episode-specific question or tension. The next 10-second shot S002 MUST connect or reinforce it by 15s. Keep every Muse source shot at exactly 10.0s (24fps/240 frames): NEVER generate a 15s shot to implement the 15s hook. No long logo/recap first, fake drama, fabricated stakes, rapid A2 exposition or automatic claim of audience retention. Vary genre: mystery, heartfelt decision, comedy trouble, urgent problem, visual surprise or disaster when truly justified. Do not re-use the Veylora disaster intro on future episodes. For EP001: S001 previews the real past Veylora event with only Mara and Orin; S002 cuts to the present Earth kitchen as Bix makes an ordinary two-note cup sound and Mara freezes. The past event is fully explained later at SC-006. No Evan, Juno, Lia, Bix, Bubu or Earth grandparents can appear in the historic teaser. No masked villain reveal. The Veylora station location plate is NOT approved; block final images. Require opening_hook in story plan, run tools/bell_leaf/opening_hook_gate.py and tools/cf_story_quality_gate.py check. A structural PASS requires separate human story/art review and real first-30s audience retention after publication.
