---
name: produce-episode
description: Golden-path SOP to take one channel episode from plan to an upload-ready package with ONE command (plan -> greenlight -> render -> Director Cut -> auto edit -> QC -> policy -> HANDOFF). Use for "make an episode", "produce N episodes", nightly factory runs.
---
# Produce an episode (CineFactory closed loop)

Arguments (from the request or defaults): CHANNEL=zoomi, COUNT=1, SECONDS=330 (5.5 min), RES=1280x720 (1920x1080 for final masters).
People step in at three points only: (1) **greenlight the plan**, (2) read QC notes when the fix loop escalates, (3) approve the draft.
The plan the owner greenlights is exactly the episode that gets rendered (same title, cast, scenes, seeds): the renderer reads
`varied_episode.json`, it no longer re-plans.

## 0. Ground truth and memory
`python tools/cf_status.py` — Blender/FFmpeg present, GPU free, which animals can be rendered today, where every series episode is
(planned / greenlit / render:failed / qc:failed / handoff). `python tools/cf_decision.py list --last 20` — respect active decisions.
Read the newest `reports/research/*_<CHANNEL>.md` proposals if any.

## 1. Plan (showrunner) -> human point 1
`python scripts/plan_long_slide_series.py --channel CHANNEL --count COUNT --duration SECONDS`
Plans only what the factory can render today (shared capability: renderable animals, proven 9.5 s modules, no unstaged scenes);
an unrenderable plan prints BLOCKED and is not written. Each folder gets `render_check.json`.
Show the owner the folder(s): title, synopsis, cast, module count, render estimate. Then STOP.
The owner greenlights: `python scripts/plan_long_slide_series.py --channel CHANNEL --greenlight EP_000N --by owner`.
Unattended runs never greenlight on the owner's behalf; they plan overnight and produce only episodes that are already greenlit.
Re-check an old plan against today's assets: `--check EP_000N`.

## 2. One command for everything after the greenlight
`python scripts/produce_long_slide_episode.py --channel CHANNEL --episode EP_000N [--res 1920x1080]`
Optional first: `--animatic` renders the same plan at 640x360 and stops with a contact sheet so the owner can look before the
full render is paid for. Stages (resumable; state in `<episode>/production.json`; `--redo <stage>` to repeat one):
gate -> render (Blender modules, timing to `data/production_ledger.jsonl`) -> cut (Director Cut + vo-fit + strict validate) ->
edit (`edit/<EP>_edit.mp4`, music bed, cue sounds, -14 LUFS measured on the delivered file, chapters) -> qc -> policy -> handoff.
Exit codes: 0 done · 2 blocked (read the message) · 3 QC failed · 4 policy FAIL · 8 not greenlit · 10 animatic ready.

## 3. QC loop (qc-reviewer, independent) -> human point 2 only on escalation
On exit 3 the qc-reviewer opens the contact sheet + `edit/<EP>_edit.qc.json` and writes `qc_notes.md` (video-qc skill format).
FIX notes go to the owner of the cause: blender-td (module re-render: delete nothing, fix the cause, `--redo render`),
showrunner/director-cut (timing, lines, emotion: edit `director_cut.json`, then `--redo edit`), audio-post (`--redo edit`).
Max 2 loops, then escalate to the owner with the notes.

## 4. Package + policy (packaging-seo, policy-check skill)
`upload_package.json` comes from the plan. packaging-seo may write 3 title options and a thumbnail brief into the folder; the
policy stage must not FAIL (exit 4 -> fix title/tags/description, then `--redo policy`).

## 5. Hand-off -> human point 3
The producer writes `<episode>/HANDOFF.md` (QC numbers, policy result, render and edit time, file list) and a decision-log row.
Upload is the owner's action, as a private draft first. After the owner approves the draft:
`python scripts/plan_long_slide_series.py --channel CHANNEL --approve EP_000N` and `cf_decision.py add --kind publish --label OWNER`.

Never: upload, spend credits, delete rendered modules, greenlight for the owner, or wait on competitor-research gates for ORIGINAL episodes.
