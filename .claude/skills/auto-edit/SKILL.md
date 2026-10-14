---
name: auto-edit
description: Build the finished episode from director_cut.json with tools/cf_auto_edit.py (cuts, dissolves, VO, ducked music, SFX, subtitles, chapters, -14 LUFS), check the edit report and hand it to QC. Use after the director-cut skill, or to re-cut after QC notes.
---
# Auto edit

1. Preview first (fast, 640x360): `python tools/cf_auto_edit.py <dc> --preview --repo .`
   Read `<name>.edit_report.json`: every WARN must be understood. "VO runs past the end of the shot" = fix the DC (shorter line or longer shot), not the audio.
2. Full render: `python tools/cf_auto_edit.py <dc> --repo .`
   Output in `<episode>/edit/`: `<ID>_edit.mp4`, `.srt`, `.chapters.txt`, `.edit_report.json`.
3. Voice: set `CF_TTS_COMMAND` to the local TTS (same template as `cinefactory.audio.tts.CommandTTS`, text on stdin, `{output}` placeholder). Without it VO lines become subtitles only and the report says so - never ship narration-only formats that way.
4. Hand off to QC: `python tools/cf_qc.py <episode>/edit/<ID>_edit.mp4 --profile <profile>` and the qc-reviewer agent.
5. QC FIX notes come back as `qc_notes.md`. Fix the cause in the right place (DC timing/lines -> this skill; picture -> blender-td re-renders the shot; sound sources -> audio-post), then re-run steps 2-4. Max 2 loops, then escalate to the owner.

Never hand-edit the output video; change the DC and rebuild so every version is reproducible.
