#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
mkdir -p data/projects data/artifacts workflows
cinefactory doctor
printf '\nCineFactory installed. Start API with: .venv/bin/uvicorn cinefactory.api.app:app --host 127.0.0.1 --port 8765\n'
