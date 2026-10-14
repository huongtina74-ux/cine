from __future__ import annotations
from pathlib import Path


def require_under_root(path: str|Path, root: str|Path)->Path:
    p=Path(path).resolve(); r=Path(root).resolve()
    if p != r and r not in p.parents: raise ValueError(f'Path escapes allowed root: {p}')
    return p
