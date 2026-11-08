# HaoHao integration — CINE owns the workflows and artifacts

HaoHao is ONE installed desktop application, not 67 installed copies. The user's Downloads clutter resulted from temporary Python/PowerShell UI experiments and debugging screenshots. It was an organizational mistake and must not recur.

## Where things live

| Responsibility | Canonical location | Rule |
|---|---|---|
| Series story | docs/story/bell_leaf/ and config/series/bell_leaf/memory_manifest_v1.json | EP001 v2; don't use v1.1 as final |
| Character/location reference images | assets/canon/, config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json | Original owner SHA and geometry locked |
| NEW integration scripts | tools/haohao/ | Code review required, never write scripts to Downloads |
| NEW run results | data/haohao/runs/BL-XXXX/RUN-ID/ | Prompts/screenshots/videos/QC and status, all kept locally |
| Historical one-off scripts | data/haohao/legacy_runs/20261108/legacy_scripts/ | Forensic archive, NOT production code |
| Historical screenshots | data/haohao/legacy_runs/20261108/screenshots/ | Private evidence, NOT GitHub |
| Archive SHA receipt | data/haohao/legacy_runs/20261108/migration_receipt.json | Includes source, destination and hash for 67 files |
| Existing EP001 pilot outputs | data/story_quality/ep001_haohao_actual_pilot_20261108/ | 10s video proofs/prompt packs, not final approved EP001 |
| Installed HaoHao app | C:\Users\ADMIN\AppData\Local\Programs\HaoHao\HaoHao.exe | External executable, do NOT relocate |
| HaoHao running state | C:\Users\ADMIN\AppData\Roaming\HaoHao | External user profile/projects/queue, do NOT relocate or publish |

## Correct operation for Bell & Leaf

1. CINE loads the full current v2 scene story, old/new world mechanics, character visual registry, location registry and relevant Skills. Use story_memory_resolver.py, not conversational guesses.
2. Produce one CGI animated 16:9 first-frame at a time, with exact OWNER face/body source and registered single-space location. Do not attach all actors from a scene. Never ask for an image grid.
3. In HaoHao Studio choose the existing BellLeaf_EP001_3D project and the correct @character / @location library entries. A task marked queued or complete does not mean visual QC has passed.
4. Compare the output image to approved face/body and real room geometry. Reject photoreal actors, wrong face/hair, shifted architecture, invented cast or clothing.
5. After STILL FRAME QC, submit image-to-video, a 10s continuous genuinely animated take; do not use zoom-only video. Keep separate voice/WAV identity and lip-sync QC.
6. Save all new prompts, source image, queue receipt, actual image/video if present, human approval and QC notes under data/haohao/runs/BL-XXXX/RUN-ID/ .
7. Do NOT queue 270 shots based only on the v1.1 draft. V2 has 30 detailed story scenes, 270 slots NOT signed off for production, and several supporting character/location gates.
8. Send only QC-passed outputs to CINE episode assembler; keep analytics/learning tied to the same episode/shot IDs.

## Developer storage rule

Import from tools.haohao.workspace import allocate_run, artifact_destination, then allocate_run("BL-0001", "pilot_S001_001"). Store screenshots and other artifacts in its category subfolder. The function refuses to use Downloads as a fallback; it refuses path traversal and duplicate run names.

## Legacy and security

- The 37 archived code scripts contain hardcoded Downloads paths and sometimes direct GUI control. Treat as READ-ONLY historical evidence; review and port a script into tools/haohao/ before using it in production.
- Do not modify the installed HaoHao.exe, its app.asar, studio.json, saved credentials, project IDs or live database when organizing the CINE repository.
- Do not commit screenshots, source character images, private reference text, cookies, tokens, queued project data or the raw migration receipt to GitHub. CINE's data/ directory is Git-ignored.
- Only safe workflow/code and sanitized documentation are intended for GitHub.
