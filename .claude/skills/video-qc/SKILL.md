---
name: video-qc
description: Technical + visual QC for any finished video file (loudness, black/frozen frames, dead air, resolution, pacing, contact-sheet review) that ends in a timecoded qc_notes.md the fixing agents can act on. Use after every export and before any approval.
---
# Video QC
1. `python tools/cf_qc.py <video> --profile youtube_long|kids_long|shorts [--min-seconds N --max-seconds N]`
   Exit 0 = technical PASS, 1 = FAIL, 2 = tool error. Report: `<name>.qc.json`, sheet: `<name>.contact.jpg`.
2. Open the contact sheet with Read. Then open 3-6 single frames from `<name>.frames/` around anything suspicious, and the `.edit_report.json` warnings if the video came from auto-edit.
3. Creative checklist: camera upright and motivated; no clipping/intersections; characters on-model and readable at phone size; title/end cards legible; something changes every 3-6 s; VO matches picture; subtitles in sync; ending lands; kid-safe.
4. Write `qc_notes.md` next to the video - one row per problem, so the fix goes to the right place:

```markdown
# QC notes — <ID> — verdict: APPROVE | FIX | REJECT
Frames inspected: <list of timestamps/files>   Technical: PASS/FAIL (<LUFS>, <issues>)
| # | Time | Shot | Problem | Fix owner | Fix |
| 1 | 0:28 | S004 | camera upside-down | blender-td | re-render module 4 with camera rig fix |
| 2 | 1:12 | S009 | VO ends after the cut | director-cut | shorten line to 9 words |
```
Never claim you "watched the whole video": list the frames you saw. The reviewer never fixes; it only writes notes.

## Bell & Leaf Muse/HaoHao specialization (2026-11-09)
For `bell_leaf` 10.0-second 24fps Muse clips, additionally read `../cine-bell-leaf-stylized-3d-prompt-director/references/MUSE_HAOHAO_OPERATING_STANDARD_20261109.md` before issuing a voice/face/scene PASS. Check actual `ffprobe` duration/frame count/native resolution, reference-frame continuity at 0/2/5/8/9.7s, uninterrupted character motion, English A2 spoken-text ASR, proper names, age/voice continuity and **human-assessed lip-sync**. Do not equate an OpenVoice-converted audio file or HaoHao "Xong" to approved media. Add subtitle overlays only after speech/audio QC.
