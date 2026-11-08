"""CineFactory-owned HaoHao file destinations. Do not write to Downloads root.

Use these utilities in all NEW HaoHao image/video UI and batch scripts.
This module does NOT control HaoHao.exe and never touches its user-data folder.
"""
from __future__ import annotations
from pathlib import Path
import re

CINE_ROOT = Path(__file__).resolve().parents[2]
CINE_DATA = CINE_ROOT / "data" / "haohao"
RUNS_ROOT = CINE_DATA / "runs"
LEGACY_ROOT = CINE_DATA / "legacy_runs"
APP_EXECUTABLE = Path.home() / "AppData" / "Local" / "Programs" / "HaoHao" / "HaoHao.exe"
APP_USER_DATA = Path.home() / "AppData" / "Roaming" / "HaoHao"

def allocate_run(episode_id: str, run_id: str) -> Path:
    """Allocate unique empty CINE-managed run. Never fallback to ~/Downloads."""
    if not re.fullmatch(r"BL-\d{4}", episode_id):
        raise ValueError("INVALID_BELL_LEAF_EPISODE_ID")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{2,79}", run_id):
        raise ValueError("INVALID_RUN_ID")
    path = RUNS_ROOT / episode_id / run_id
    path.mkdir(parents=True, exist_ok=False)
    return path

def artifact_destination(run_dir: Path, filename: str, category: str) -> Path:
    """Return a safe path for a screenshot, prompt, video or QC receipt."""
    if category not in ("screenshots","prompts","videos","qc","receipts"):
        raise ValueError("INVALID_OUTPUT_CATEGORY")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,179}", filename) or filename in (".",".."):
        raise ValueError("UNSAFE_ARTIFACT_NAME")
    resolved=run_dir.resolve()
    try:
        resolved.relative_to(RUNS_ROOT.resolve())
    except ValueError:
        raise ValueError("OUTSIDE_CINE_RUNS_ROOT")
    dest=resolved / category / filename
    if dest.exists():
        raise FileExistsError("ARTIFACT_ALREADY_EXISTS")
    dest.parent.mkdir(parents=True,exist_ok=True)
    return dest
