#!/usr/bin/env python3
"""PreToolUse guard for CineFactory: lets Claude work autonomously but never
publishes, spends credits, or destroys production data without the owner.

Claude Code sends the pending tool call as JSON on stdin.
  exit 0                      -> allow (normal permission rules still apply)
  exit 2 + message on stderr  -> BLOCK, the message is shown to Claude
  JSON "ask" decision         -> fall back to asking the human

Owner overrides (set only for a session where you really mean it):
  CF_ALLOW_PUBLISH=1   allow upload/publish tools and scripts
  CF_ALLOW_PAID=1      allow metered generation APIs / credit-spending MCP tools
"""
from __future__ import annotations

import json
import os
import re
import sys

PROTECTED_DIRS = r"(data|config|knowledge|models|profiles|workflows|\.git|cinefactory)"
DESTRUCTIVE = [
    (rf"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b.*\b{PROTECTED_DIRS}\b", "recursive delete of a production folder"),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(/|~|\.|\*)(\s|$)", "recursive delete of a root/home/cwd"),
    (rf"Remove-Item\b.*-Recurse.*\b{PROTECTED_DIRS}\b", "recursive delete of a production folder"),
    (r"\b(rd|rmdir)\s+/s\b", "recursive delete"),
    (r"\bgit\s+push\b.*(--force|-f\b)", "force push"),
    (r"\bgit\s+reset\s+--hard\b", "hard reset discards work"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean deletes untracked work"),
    (r"\b(DROP|TRUNCATE)\s+TABLE\b", "destroys database tables"),
    (r"\bformat\s+[a-zA-Z]:", "formats a drive"),
]
PUBLISH = [
    r"youtube.*(upload|videos\.insert|publish)", r"(upload|publish)_?(video|episode|to_youtube)",
    r"\bscripts?[\\/][\w-]*(upload|publish)[\w-]*\.(py|ps1)", r"tiktok.*upload", r"instagram.*publish",
]
PAID_HOSTS = [
    "api.openai.com", "api.runwayml.com", "api.elevenlabs.io", "higgsfield", "openart.ai", "api.replicate.com",
    "fal.run", "api.lumalabs.ai", "klingai", "api.minimax", "api.stability.ai", "api.pika", "api.heygen",
]
INSTALL = r"\b(pip|pip3|uv\s+pip|npm|pnpm|yarn|winget|choco|scoop)\s+(install|add|i)\b"
MCP_PUBLISH = re.compile(r"(upload|publish|update_video|update_video_thumbnail|instagram_publish_reel)", re.I)
MCP_PAID = re.compile(r"(generate_video|generate_broll|generate_music|generate_thumbnail|refine_thumbnail|"
                      r"voiceover_generate|motion_graphics|edit_media|generate_clips|video_watch)", re.I)
PROTECTED_WRITE = [r"[\\/]data[\\/]verification[\\/]", r"(^|[\\/])\.env$", r"[\\/]\.git[\\/]"]


def block(reason: str) -> None:
    sys.stderr.write(f"CF_GUARD BLOCKED: {reason}. If the owner really wants this, they must run it "
                     f"themselves or set the documented override for this session.\n")
    sys.exit(2)


def ask(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "ask",
                                             "permissionDecisionReason": f"CF_GUARD: {reason}"}}))
    sys.exit(0)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:  # noqa: BLE001 - never break the session on a malformed event
        sys.exit(0)
    tool = event.get("tool_name", "")
    tin = event.get("tool_input", {}) or {}
    allow_publish = os.environ.get("CF_ALLOW_PUBLISH") == "1"
    allow_paid = os.environ.get("CF_ALLOW_PAID") == "1"

    if tool.startswith("mcp__"):
        if MCP_PUBLISH.search(tool) and not allow_publish:
            block(f"{tool} publishes to a live channel")
        if MCP_PAID.search(tool) and not allow_paid:
            block(f"{tool} spends provider credits")
        sys.exit(0)

    if tool in ("Bash", "PowerShell"):
        cmd = str(tin.get("command", ""))
        for pattern, why in DESTRUCTIVE:
            if re.search(pattern, cmd, re.I):
                block(why)
        if not allow_publish and any(re.search(p, cmd, re.I) for p in PUBLISH):
            block("publishing/uploading needs the owner's explicit approval")
        if not allow_paid and any(h in cmd.lower() for h in PAID_HOSTS):
            block("metered generation API call (ZERO_METERED_API production policy)")
        if re.search(INSTALL, cmd, re.I):
            ask("installs new software into the studio environment")
        sys.exit(0)

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = str(tin.get("file_path", "") or tin.get("notebook_path", ""))
        for pattern in PROTECTED_WRITE:
            if re.search(pattern, path, re.I):
                block(f"{path} is an immutable receipt / secret / git internal")
    sys.exit(0)


if __name__ == "__main__":
    main()
