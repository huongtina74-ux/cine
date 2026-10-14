"""Send a short message to the owner's phone when an unattended run ends or fails.

    python tools/cf_notify.py "Nightly: 1 episode APPROVE, QC 0 loops"  [--file data/logs/nightly/run.json]

Telegram (free bot): set CF_TELEGRAM_TOKEN and CF_TELEGRAM_CHAT.
Any webhook that accepts JSON {"text": ...} (Slack, Discord, n8n...): set CF_NOTIFY_WEBHOOK.
With nothing set it only appends to data/logs/notify.log, so runs never fail because of it.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass


def send(text: str) -> str:
    text = text[:3500]
    token, chat = os.environ.get("CF_TELEGRAM_TOKEN"), os.environ.get("CF_TELEGRAM_CHAT")
    hook = os.environ.get("CF_NOTIFY_WEBHOOK")
    try:
        if token and chat:
            data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
            urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data=data, timeout=15).read()
            return "telegram"
        if hook:
            req = urllib.request.Request(hook, data=json.dumps({"text": text, "content": text}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=15).read()
            return "webhook"
    except Exception as exc:  # noqa: BLE001 - notification must never break a run
        return f"failed: {exc}"
    return "log-only"


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("text", nargs="*")
    p.add_argument("--file", default="", help="append the result of a claude -p JSON log (or the tail of a text file)")
    args = p.parse_args()
    text = " ".join(args.text)
    path = Path(args.file) if args.file else None
    if path and path.is_file():
        raw = path.read_text(encoding="utf-8-sig", errors="ignore")
        try:
            data = json.loads(raw)
            text += "\n" + str(data.get("result") if isinstance(data, dict) else data)[:3000]
        except json.JSONDecodeError:
            text += "\n" + raw[-3000:]
    how = send(text.strip() or "CineFactory: (empty message)")
    log = Path("data/logs/notify.log")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now().isoformat(timespec='seconds')} [{how}] {text[:500]}\n")
    print(f"NOTIFY::{how}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
