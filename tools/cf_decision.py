"""Decision log: every production decision, why it was made and what it was based on.

    python tools/cf_decision.py add --kind topic --decision "Next season: winter slides" \
        --why "3 outliers >3x in 14 days are winter themed" --evidence reports/research/2026-10-15.md \
        --label OBSERVED --by owner
    python tools/cf_decision.py list --last 10 [--kind topic]
    python tools/cf_decision.py md --out reports/decisions.md

Stored as append-only JSON lines in data/decisions.jsonl (override with --log or CF_DECISION_LOG).
Labels: OBSERVED (measured, evidence attached), INFERRED (reasoned from evidence), OWNER (owner's call).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

KINDS = ("topic", "series", "style", "script", "render", "edit", "qc", "package", "publish", "tool", "fix", "other")
LABELS = ("OBSERVED", "INFERRED", "OWNER")


def log_path(arg: str) -> Path:
    return Path(arg or os.environ.get("CF_DECISION_LOG") or "data/decisions.jsonl")


def read(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def cmd_add(args) -> int:
    if args.label == "OBSERVED" and not args.evidence:
        print("BAD_INPUT::OBSERVED needs --evidence (a file, URL or command that shows it)")
        return 2
    row = {
        "id": "D-" + uuid.uuid4().hex[:8],
        "at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "kind": args.kind,
        "decision": args.decision.strip(),
        "why": args.why.strip(),
        "evidence": args.evidence,
        "label": args.label,
        "by": args.by,
        "project": args.project,
        "supersedes": args.supersedes or None,
    }
    path = log_path(args.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"DECISION_OK::{row['id']}::{path}")
    return 0


def active(rows: list[dict]) -> list[dict]:
    gone = {r.get("supersedes") for r in rows if r.get("supersedes")}
    return [r for r in rows if r["id"] not in gone]


def cmd_list(args) -> int:
    rows = read(log_path(args.log))
    if args.kind:
        rows = [r for r in rows if r.get("kind") == args.kind]
    if not args.all:
        rows = active(rows)
    for r in rows[-args.last:]:
        ev = ", ".join(r.get("evidence") or []) or "-"
        print(f"{r['at'][:16]} {r['id']} [{r['kind']}/{r['label']}/{r['by']}] {r['decision']}  | why: {r['why']}  | evidence: {ev}")
    if not rows:
        print("NO_DECISIONS")
    return 0


def cmd_md(args) -> int:
    rows = active(read(log_path(args.log)))
    lines = ["# Decision log", "", "| When | ID | Kind | Decision | Why | Label | By |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in reversed(rows):
        lines.append(f"| {r['at'][:16]} | {r['id']} | {r['kind']} | {r['decision']} | {r['why']} | {r['label']} | {r['by']} |")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"MD_OK::{out}::{len(rows)} decisions")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--log", default="")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--kind", choices=KINDS, required=True)
    a.add_argument("--decision", required=True)
    a.add_argument("--why", required=True)
    a.add_argument("--evidence", action="append", default=[])
    a.add_argument("--label", choices=LABELS, required=True)
    a.add_argument("--by", default="claude", help="owner | claude | <agent name>")
    a.add_argument("--project", default="")
    a.add_argument("--supersedes", default="", help="id of an earlier decision this replaces")
    a.set_defaults(func=cmd_add)
    ls = sub.add_parser("list")
    ls.add_argument("--last", type=int, default=20)
    ls.add_argument("--kind", default="")
    ls.add_argument("--all", action="store_true", help="include superseded decisions")
    ls.set_defaults(func=cmd_list)
    md = sub.add_parser("md")
    md.add_argument("--out", default="reports/decisions.md")
    md.set_defaults(func=cmd_md)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
