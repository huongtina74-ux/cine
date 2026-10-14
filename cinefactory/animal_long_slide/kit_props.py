"""CC0 set-dressing catalog: which real props dress each environment theme.

Rows are only handed to the Blender worker when their source pack is
registered as APPROVED for commercial use and the file sits inside the pack
folder. Missing files are skipped and reported, because set dressing is
decoration: a missing tree must never block an episode.
"""
from __future__ import annotations

import logging
from pathlib import Path, PurePosixPath
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from .contracts import LicenseState
from .foundry import AssetFoundry

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("config") / "animal_long_slide" / "kit_props.yaml"
PROP_SUFFIXES = {".glb", ".gltf", ".blend"}


class KitPropRow(BaseModel):
    pack: str
    file: str
    zone: Literal["backdrop", "start", "finish", "air"]
    count: int = Field(ge=1, le=30)
    height: float = Field(gt=0, le=12)

    @field_validator("file")
    @classmethod
    def _relative_prop_file(cls, value: str) -> str:
        if not _is_safe_relative(value):
            raise ValueError(f"prop file must be a relative path inside its pack: {value!r}")
        path = PurePosixPath(value.replace("\\", "/"))
        if path.suffix.lower() not in PROP_SUFFIXES:
            raise ValueError(f"prop file must be one of {sorted(PROP_SUFFIXES)}: {value!r}")
        return value


class KitPropConfig(BaseModel):
    version: int = 1
    packs: dict[str, str]
    common: list[KitPropRow] = Field(default_factory=list)
    themes: dict[str, list[KitPropRow]] = Field(default_factory=dict)

    @field_validator("packs")
    @classmethod
    def _relative_pack_dirs(cls, value: dict[str, str]) -> dict[str, str]:
        bad = {pack: folder for pack, folder in value.items() if not _is_safe_relative(folder)}
        if bad:
            raise ValueError(f"pack folders must be relative paths inside the project: {bad}")
        return value


def _is_safe_relative(value: str) -> bool:
    path = PurePosixPath(value.replace("\\", "/"))
    return bool(value) and not path.is_absolute() and ".." not in path.parts and ":" not in value


def approved_license_roots(root: str | Path) -> dict[str, Path]:
    """APPROVED commercial packs mapped to the local folder holding their licence file.

    A pack id that appears more than once is approved only if every entry is,
    and a pack whose licence evidence is not a local file is never approved
    for set dressing (the folder is what ties a file on disk to its licence).
    """
    root = Path(root).resolve()
    entries: dict[str, list] = {}
    for pack in AssetFoundry.load_source_packs(root):
        entries.setdefault(pack.pack_id, []).append(pack)
    roots: dict[str, Path] = {}
    for pack_id, packs in entries.items():
        if not all(p.license_state is LicenseState.APPROVED and p.commercial_use for p in packs):
            continue
        evidence = packs[-1].license_evidence_uri
        if "://" in evidence or not _is_safe_relative(evidence):
            continue
        evidence_path = (root / evidence).resolve()
        if evidence_path.is_file():
            roots[pack_id] = evidence_path.parent
    return roots


class KitPropCatalog:
    def __init__(self, root: str | Path, config: KitPropConfig, approved_packs: dict[str, Path]) -> None:
        self.root = Path(root).resolve()
        self.config = config
        # pack id -> folder holding its licence file; pack folders must sit inside it.
        self.approved_packs = {pack: Path(folder).resolve() for pack, folder in approved_packs.items()}
        unknown = {row.pack for row in self._all_rows()} - set(config.packs)
        if unknown:
            raise ValueError(f"kit_props.yaml uses undeclared packs: {sorted(unknown)}")
        self.findings: list[str] = []

    def _finding(self, code: str) -> None:
        if code not in self.findings:
            self.findings.append(code)
            logger.warning("kit prop skipped: %s", code)

    def _all_rows(self) -> list[KitPropRow]:
        rows = list(self.config.common)
        for theme_rows in self.config.themes.values():
            rows.extend(theme_rows)
        return rows

    @classmethod
    def load(cls, root: str | Path) -> "KitPropCatalog":
        root = Path(root)
        path = root / CONFIG_PATH
        if not path.is_file():
            return cls(root, KitPropConfig(packs={}), {})
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(root, KitPropConfig.model_validate(raw), approved_license_roots(root))

    def _resolve(self, row: KitPropRow) -> Path | None:
        license_root = self.approved_packs.get(row.pack)
        if license_root is None:
            self._finding(f"KIT_PACK_NOT_APPROVED:{row.pack}")
            return None
        pack_dir = (self.root / self.config.packs[row.pack]).resolve()
        if not pack_dir.is_relative_to(license_root):
            self._finding(f"KIT_PACK_OUTSIDE_LICENSE_ROOT:{row.pack}")
            return None
        path = (pack_dir / row.file).resolve()
        if not path.is_relative_to(pack_dir):
            self._finding(f"KIT_PATH_ESCAPES_PACK:{row.pack}:{row.file}")
            return None
        if not path.is_file():
            self._finding(f"KIT_FILE_MISSING:{row.pack}:{row.file}")
            return None
        return path

    def rows_for(self, theme_id: str | None) -> list[dict]:
        """Worker rows (absolute paths) for one theme; unthemed modules get none."""
        if not theme_id:
            return []
        rows = []
        for row in [*self.config.common, *self.config.themes.get(theme_id, [])]:
            path = self._resolve(row)
            if path is None:
                continue
            rows.append({
                "pack": row.pack,
                "name": PurePosixPath(row.file.replace("\\", "/")).stem,
                "path": str(path),
                "zone": row.zone,
                "count": row.count,
                "height": row.height,
            })
        return rows
