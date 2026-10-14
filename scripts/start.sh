#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec "${ROOT}/.venv/bin/uvicorn" cinefactory.api.app:app --host 127.0.0.1 --port 8765
