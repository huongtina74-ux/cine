from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .contracts import AssetKind
from .execution import LongSlideRenderJob
from .kit_props import KitPropCatalog
from .registry import LongSlideAssetRegistry


class LongSlideBlenderBinder:
    """Compile a LongSlideRenderJob into a self-contained Blender worker payload."""

    def __init__(
        self,
        root: str | Path,
        *,
        blender_executable: str | Path,
        registry: LongSlideAssetRegistry | None = None,
        kit_props: KitPropCatalog | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.blender_executable = Path(blender_executable).resolve()
        self.registry = registry or LongSlideAssetRegistry.load(self.root)
        self.kit_props = kit_props or KitPropCatalog.load(self.root)
        self.worker_script = (
            self.root / "scripts" / "render_long_slide_job.py"
        )

    def _asset_path(self, asset_id: str) -> Path:
        asset = self.registry.get(asset_id)
        path = self.registry.resolve_local_path(self.root, asset)
        if path is None or not path.is_file():
            raise FileNotFoundError(f"{asset_id}: local asset file missing")
        return path.resolve()

    def _motion_rows(self, resolved) -> list[dict[str, Any]]:
        rows = []
        for item in resolved:
            row = item.model_dump(mode="json")
            if item.local_path:
                path = Path(item.local_path)
                if not path.is_absolute():
                    path = self.root / path
                row["local_path"] = str(path.resolve())
            rows.append(row)
        return rows

    def compile_payload(self, job: LongSlideRenderJob) -> dict[str, Any]:
        scene_id = f"scene.{job.module.scene_kind.value.lower()}"
        animal_id = f"animal.{job.module.animal_id}"
        obstacle_rows = []
        for placement in job.module.obstacles:
            if not placement.enabled:
                continue
            asset_id = f"obstacle.{placement.obstacle_id}"
            obstacle_rows.append({
                "asset_id": asset_id,
                "path": str(self._asset_path(asset_id)),
                "slot": placement.slot,
                "seed": placement.seed,
            })

        motions = self._motion_rows(job.resolved_motions)
        companions = []
        for companion_id, resolved in job.companion_motions.items():
            asset_id = f"animal.{companion_id}"
            companions.append({
                "asset_id": asset_id,
                "path": str(self._asset_path(asset_id)),
                "rig_profile": self.registry.get(asset_id).rig_profile,
                "motions": self._motion_rows(resolved),
            })

        output = Path(job.output_path)
        if not output.is_absolute():
            output = self.root / output
        output = output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        return {
            "schema_version": 1,
            "project_id": job.project_id,
            "episode_id": job.episode_id,
            "module": job.module.model_dump(mode="json"),
            "scene": {
                "asset_id": scene_id,
                "path": str(self._asset_path(scene_id)),
            },
            "animal": {
                "asset_id": animal_id,
                "path": str(self._asset_path(animal_id)),
                "rig_profile": self.registry.get(animal_id).rig_profile,
            },
            "obstacles": obstacle_rows,
            "motions": motions,
            "companions": companions,
            "kit_props": self.kit_props.rows_for(
                ((job.module.metadata.get("environment") or {}).get("theme_id"))
            ),
            "kit_prop_findings": list(self.kit_props.findings),
            "output_path": str(output),
            "width": job.width,
            "height": job.height,
            "fps": job.fps,
            "render_preview": job.render_preview,
        }

    def execute(
        self,
        job: LongSlideRenderJob,
        *,
        timeout_seconds: int = 600,
    ) -> Path:
        if not self.blender_executable.is_file():
            raise FileNotFoundError(
                f"Blender executable not found: {self.blender_executable}"
            )
        if not self.worker_script.is_file():
            raise FileNotFoundError(
                f"Long Slide worker script not found: {self.worker_script}"
            )
        payload = self.compile_payload(job)
        job_dir = (
            self.root / "data" / "animal_long_slide" / "jobs"
            / job.project_id / job.episode_id
        )
        job_dir.mkdir(parents=True, exist_ok=True)
        payload_path = job_dir / f"{job.module.module_id}.json"
        payload_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        output = Path(payload["output_path"])
        # A killed or failed earlier run can leave a partial clip that would pass
        # the size check below; always start from nothing.
        output.unlink(missing_ok=True)
        command = [
            str(self.blender_executable),
            "--background",
            "--factory-startup",
            # Without this Blender exits 0 even when the worker script raises.
            "--python-exit-code",
            "1",
            "--python",
            str(self.worker_script),
            "--",
            "--job",
            str(payload_path),
        ]
        result = subprocess.run(
            command,
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        log_path = payload_path.with_suffix(".blender.log")
        log_path.write_text(
            result.stdout + "\n--- STDERR ---\n" + result.stderr,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Long Slide Blender worker failed: {log_path}"
            )
        if not output.is_file() or output.stat().st_size <= 1024:
            raise RuntimeError(
                f"Long Slide Blender worker produced no valid output: {output}"
            )
        return output
