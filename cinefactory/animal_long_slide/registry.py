from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import AssetManifest


class LongSlideAssetRegistry:
    def __init__(
        self,
        assets: list[AssetManifest] | None = None,
        *,
        root: str | Path | None = None,
    ) -> None:
        self.root = Path(root).resolve() if root is not None else None
        self._assets: dict[str, AssetManifest] = {}
        for asset in assets or []:
            self.add(asset)

    def add(self, asset: AssetManifest) -> None:
        if asset.asset_id in self._assets:
            raise ValueError(f"duplicate Long Slide asset: {asset.asset_id}")
        self._assets[asset.asset_id] = asset

    def get(self, asset_id: str) -> AssetManifest:
        try:
            return self._assets[asset_id]
        except KeyError as exc:
            raise KeyError(f"unknown Long Slide asset: {asset_id}") from exc

    def maybe_get(self, asset_id: str) -> AssetManifest | None:
        return self._assets.get(asset_id)

    def values(self) -> list[AssetManifest]:
        return list(self._assets.values())

    def local_file_exists(self, asset: AssetManifest) -> bool:
        if not asset.local_path:
            return False
        path = Path(asset.local_path)
        if not path.is_absolute():
            if self.root is None:
                return True
            path = self.root / path
        return path.is_file()

    def preview_qualified(self, asset: AssetManifest) -> bool:
        return (
            asset.license_state.value == "APPROVED"
            and asset.commercial_use
            and asset.technical_qc_passed
            and self.local_file_exists(asset)
        )

    def animal_ids(self, *, preview: bool = False) -> list[str]:
        rows = []
        for asset in self.values():
            if asset.kind.value != "ANIMAL" or not asset.asset_id.startswith("animal."):
                continue
            ready = self.preview_qualified(asset) if preview else not asset.production_blocked
            if ready:
                rows.append(asset.asset_id.split(".", 1)[1])
        return sorted(rows)

    @staticmethod
    def resolve_local_path(root: str | Path, asset: AssetManifest) -> Path | None:
        if not asset.local_path:
            return None
        path = Path(asset.local_path)
        return path if path.is_absolute() else Path(root).resolve() / path

    @classmethod
    def load(cls, root: str | Path) -> "LongSlideAssetRegistry":
        config_dir = Path(root) / "config" / "animal_long_slide"
        rows: list[dict] = []
        for filename in ("assets.yaml", "external_assets.yaml"):
            path = config_dir / filename
            if not path.exists():
                continue
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            file_rows = raw.get("assets", [])
            if not isinstance(file_rows, list):
                raise ValueError(f"animal_long_slide/{filename} must contain an assets list")
            rows.extend(file_rows)
        return cls(
            [AssetManifest.model_validate(row) for row in rows],
            root=root,
        )
