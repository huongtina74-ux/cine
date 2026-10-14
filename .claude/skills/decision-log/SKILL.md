---
name: decision-log
description: Record and read production decisions (topic, series, style, edit, QC, package, publish, tools) with why and evidence in data/decisions.jsonl. Use whenever the owner or an agent decides something that later work depends on, and before planning, to read what was already decided.
---
# Decision log

Write: `python tools/cf_decision.py add --kind <topic|series|style|script|render|edit|qc|package|publish|tool|fix|other> --decision "<what>" --why "<because>" --label <OBSERVED|INFERRED|OWNER> --by <owner|claude|agent> [--evidence <file/url>]... [--supersedes D-xxxx]`
- OBSERVED needs evidence (a report, a QC json, an analytics export). INFERRED is your reasoning from evidence. OWNER is the owner's call - record it in their words.
- Changing your mind? Add a new decision with `--supersedes <old id>`; never edit the file.

Read before acting: `python tools/cf_decision.py list --last 20 [--kind topic]`. Plans that contradict an active decision must say so and ask the owner.
Export for the owner: `python tools/cf_decision.py md --out reports/decisions.md`.

The three working rules behind every entry: measure, don't guess; label data vs inference; when information is missing, ask instead of deciding for the owner.
