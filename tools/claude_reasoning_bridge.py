#!/usr/bin/env python3
"""Claude Code as the CineFactory reasoning engine (CommandReasoningBridge contract).

CineFactory already supports a pluggable "reasoning command" (cinefactory/reasoning/command_bridge.py):
it writes ONE JSON request to stdin  {"stage", "prompt", "schema", "context"}
and expects ONLY schema-valid JSON on stdout. This script fulfils that contract by calling
Claude Code in headless print mode (`claude -p`), so every writing/directing/planning stage
can be reasoned by Claude on your existing subscription instead of a metered API key.

Enable (PowerShell, from the repo root):
    $env:CINEFACTORY_REASONING_COMMAND = "python tools/claude_reasoning_bridge.py"
    # optional:
    $env:CF_CLAUDE_MODEL = "opus"          # or sonnet / haiku
    $env:CF_CLAUDE_JSON_SCHEMA = "1"       # use --json-schema if your Claude Code version supports it

Environment:
    CF_CLAUDE_BIN          path to the claude executable (default: found on PATH)
    CF_CLAUDE_MODEL        model alias passed with --model (default: CLI default)
    CF_CLAUDE_MAX_TURNS    default 3
    CF_CLAUDE_TIMEOUT      seconds, default 900
    CF_CLAUDE_JSON_SCHEMA  "1" = pass the schema with --json-schema and read structured_output
    CF_BRIDGE_LOG          optional JSONL file; every request/response is appended (audit trail)

Exit codes: 0 ok, 1 Claude failed / invalid JSON after retry, 2 bad request on stdin.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SYSTEM_RULES = (
    "You are a stage of the CineFactory professional video production pipeline. "
    "Produce ORIGINAL work only: no copyrighted characters, lyrics, scripts or brand assets. "
    "Respond with exactly ONE JSON object that validates against the JSON Schema given below. "
    "No markdown fences, no commentary before or after the JSON."
)
MAX_CONTEXT_CHARS = 60_000


def build_prompt(req: dict, feedback: str | None = None) -> str:
    context = json.dumps(req.get("context", {}), ensure_ascii=False, indent=1)
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "\n...[context truncated]"
    parts = [
        SYSTEM_RULES,
        f"\n## Stage\n{req.get('stage', 'unknown')}",
        f"\n## Task\n{req.get('prompt', '')}",
        f"\n## Context (JSON)\n{context}",
        f"\n## JSON Schema the answer MUST satisfy\n{json.dumps(req.get('schema', {}), ensure_ascii=False)}",
    ]
    if feedback:
        parts.append(f"\n## Your previous answer was rejected\n{feedback}\nReturn a corrected JSON object only.")
    return "\n".join(parts)


def extract_json(text: str):
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def light_validate(obj, schema: dict) -> str | None:
    """Cheap structural check (pydantic does the full validation inside CineFactory)."""
    if schema.get("type", "object") == "object":
        if not isinstance(obj, dict):
            return "top-level value must be a JSON object"
        missing = [k for k in schema.get("required", []) if k not in obj]
        if missing:
            return "missing required keys: " + ", ".join(missing)
    return None


def call_claude(prompt: str, schema: dict) -> str:
    claude = os.environ.get("CF_CLAUDE_BIN") or shutil.which("claude") or shutil.which("claude.cmd")
    if not claude:
        raise RuntimeError("claude executable not found (set CF_CLAUDE_BIN)")
    argv = [claude, "-p", "--output-format", "json",
            "--max-turns", os.environ.get("CF_CLAUDE_MAX_TURNS", "3")]
    if os.environ.get("CF_CLAUDE_MODEL"):
        argv += ["--model", os.environ["CF_CLAUDE_MODEL"]]
    use_schema = os.environ.get("CF_CLAUDE_JSON_SCHEMA") == "1"
    if use_schema:
        argv += ["--json-schema", json.dumps(schema)]
    proc = subprocess.run(argv, input=prompt, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=int(os.environ.get("CF_CLAUDE_TIMEOUT", "900")))
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr[-2000:]}")
    envelope = json.loads(proc.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude reported error: {str(envelope.get('result'))[:2000]}")
    if use_schema and envelope.get("structured_output") is not None:
        return json.dumps(envelope["structured_output"])
    return envelope.get("result", "")


def log(entry: dict) -> None:
    path = os.environ.get("CF_BRIDGE_LOG")
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        req = json.loads(sys.stdin.read())
        schema = req.get("schema") or {}
    except Exception as exc:  # noqa: BLE001
        print(f"bad request on stdin: {exc}", file=sys.stderr)
        return 2
    feedback = None
    for attempt in (1, 2):
        started = time.time()
        try:
            raw = call_claude(build_prompt(req, feedback), schema)
            obj = extract_json(raw)
            problem = light_validate(obj, schema)
        except Exception as exc:  # noqa: BLE001
            raw, obj, problem = locals().get("raw", ""), None, f"{type(exc).__name__}: {exc}"
        log({"ts": time.time(), "stage": req.get("stage"), "attempt": attempt,
             "seconds": round(time.time() - started, 1), "ok": problem is None, "problem": problem})
        if problem is None:
            sys.stdout.write(json.dumps(obj, ensure_ascii=False))
            return 0
        feedback = problem
    print(f"reasoning failed after retry: {feedback}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
