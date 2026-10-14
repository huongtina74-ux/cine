from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from .bridge import AdobeBridgeHTTPClient


class PremiereRuntimeProbe(BaseModel):
    installed: bool
    bridge_reachable: bool
    plugin_registered: bool
    host_version: str | None = None
    plugin_version: str | None = None
    capabilities: set[str] = Field(default_factory=set)
    findings: list[str] = Field(default_factory=list)


class PremiereOperationEvidence(BaseModel):
    operation: str
    passed: bool
    duration_ms: int = Field(default=0, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class PremiereSandboxResult(BaseModel):
    project_path: str
    operation_evidence: list[PremiereOperationEvidence] = Field(default_factory=list)
    export_output: str | None = None
    provenance_path: str | None = None
    cleaned_up: bool = False
    findings: list[str] = Field(default_factory=list)


class PremiereRuntimeAdapter:
    SUPPORTED_OPERATIONS = {
        "import media",
        "create sequence",
        "place clip",
        "trim",
        "markers",
        "audio edit",
        "effects",
        "export",
    }

    def __init__(
        self,
        root: str | Path,
        *,
        base_url: str | None = None,
        token: str | None = None,
        client: AdobeBridgeHTTPClient | Any | None = None,
    ) -> None:
        self.root = Path(root)
        self.base_url = (
            base_url
            or os.getenv(
                "CINEFACTORY_ADOBE_BRIDGE",
                "http://127.0.0.1:8791",
            )
        )
        self.token_path = (
            self.root
            / "data"
            / "studio"
            / "adobe_bridge"
            / "token.txt"
        )
        self._token = token
        self._client = client

    def _bridge(self):
        if self._client is not None:
            return self._client
        token = self._token
        if token is None:
            if not self.token_path.is_file():
                raise RuntimeError("ADOBE_BRIDGE_TOKEN_MISSING")
            token = self.token_path.read_text(
                encoding="utf-8"
            ).strip()
        self._client = AdobeBridgeHTTPClient(
            base_url=self.base_url,
            token=token,
            timeout_seconds=3,
        )
        return self._client

    def probe(
        self,
        *,
        installed: bool,
    ) -> PremiereRuntimeProbe:
        findings: list[str] = []
        try:
            client = self._bridge()
            registered = client.client("premiere")
        except Exception as exc:
            return PremiereRuntimeProbe(
                installed=installed,
                bridge_reachable=False,
                plugin_registered=False,
                findings=[
                    f"ADOBE_BRIDGE_UNAVAILABLE:{type(exc).__name__}:{exc}"
                ],
            )
        if registered is None:
            findings.append("PREMIERE_UXP_PLUGIN_NOT_REGISTERED")
            return PremiereRuntimeProbe(
                installed=installed,
                bridge_reachable=True,
                plugin_registered=False,
                findings=findings,
            )
        age = (
            time.time() - registered.last_seen.timestamp()
        )
        fresh = age <= 5.0
        if not fresh:
            findings.append("PREMIERE_UXP_PLUGIN_HEARTBEAT_STALE")
        if not installed:
            findings.append("PREMIERE_NOT_INSTALLED")
        return PremiereRuntimeProbe(
            installed=installed,
            bridge_reachable=True,
            plugin_registered=fresh,
            host_version=registered.host_version,
            plugin_version=registered.plugin_version,
            capabilities=set(registered.capabilities),
            findings=findings,
        )

    def execute(
        self,
        operation: str,
        payload: dict[str, Any] | None = None,
        *,
        timeout_seconds: float = 90.0,
    ) -> dict[str, Any]:
        if operation not in self.SUPPORTED_OPERATIONS and operation not in {
            "probe",
            "sandbox create",
            "sandbox close",
        }:
            raise ValueError(
                f"unsupported Premiere operation: {operation}"
            )
        result = self._bridge().execute(
            "premiere",
            operation,
            payload or {},
            timeout_seconds=timeout_seconds,
        )
        if not result.ok:
            raise RuntimeError(
                result.error
                or f"Premiere operation failed: {operation}"
            )
        return dict(result.payload)

    @staticmethod
    def _timed(
        operation: str,
        fn: Callable[[], dict[str, Any]],
    ) -> PremiereOperationEvidence:
        started = time.perf_counter()
        try:
            payload = fn()
            return PremiereOperationEvidence(
                operation=operation,
                passed=True,
                duration_ms=max(
                    0,
                    int((time.perf_counter() - started) * 1000),
                ),
                payload=payload,
            )
        except Exception as exc:
            return PremiereOperationEvidence(
                operation=operation,
                passed=False,
                duration_ms=max(
                    0,
                    int((time.perf_counter() - started) * 1000),
                ),
                findings=[f"{type(exc).__name__}:{exc}"],
            )

    def sandbox_exercise(
        self,
        *,
        input_media: str | Path,
        output_dir: str | Path,
        timeout_seconds: float = 120.0,
    ) -> PremiereSandboxResult:
        source = Path(input_media).resolve()
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        if not source.is_file():
            raise FileNotFoundError(source)

        project_path = output / "cinefactory_premiere_mastery.prproj"
        export_path = output / "cinefactory_premiere_mastery.mp4"
        evidence: list[PremiereOperationEvidence] = []
        findings: list[str] = []
        cleaned_up = False

        create = self._timed(
            "sandbox create",
            lambda: self.execute(
                "sandbox create",
                {"project_path": str(project_path)},
                timeout_seconds=timeout_seconds,
            ),
        )
        if not create.passed:
            return PremiereSandboxResult(
                project_path=str(project_path),
                operation_evidence=evidence,
                findings=create.findings,
            )

        try:
            evidence.append(
                self._timed(
                    "import media",
                    lambda: self.execute(
                        "import media",
                        {"paths": [str(source)]},
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "create sequence",
                    lambda: self.execute(
                        "create sequence",
                        {
                            "name": "CineFactory Mastery Sequence",
                            "media_paths": [str(source)],
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "place clip",
                    lambda: self.execute(
                        "place clip",
                        {
                            "media_path": str(source),
                            "seconds": 2.0,
                            "video_track": 0,
                            "audio_track": 0,
                            "mode": "insert",
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "trim",
                    lambda: self.execute(
                        "trim",
                        {
                            "video_track": 0,
                            "in_seconds": 0.05,
                            "out_seconds": 1.5,
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "markers",
                    lambda: self.execute(
                        "markers",
                        {
                            "name": "CineFactory Mastery",
                            "comments": "operation evidence",
                            "seconds": 0.5,
                            "duration_seconds": 0.1,
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "audio edit",
                    lambda: self.execute(
                        "audio edit",
                        {
                            "audio_track": 0,
                            "mute": False,
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "effects",
                    lambda: self.execute(
                        "effects",
                        {
                            "video_track": 0,
                            "match_name": "AE.ADBE Mosaic",
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
            evidence.append(
                self._timed(
                    "export",
                    lambda: self.execute(
                        "export",
                        {
                            "output_file": str(export_path),
                            "export_full": True,
                        },
                        timeout_seconds=timeout_seconds,
                    ),
                )
            )
        finally:
            try:
                self.execute(
                    "sandbox close",
                    {"project_path": str(project_path)},
                    timeout_seconds=30,
                )
                cleaned_up = True
            except Exception as exc:
                findings.append(
                    f"SANDBOX_CLOSE_FAILED:{type(exc).__name__}:{exc}"
                )

        provenance = {
            "adapter": "premiere-uxp",
            "project_path": str(project_path),
            "input_media": str(source),
            "export_output": (
                str(export_path) if export_path.is_file() else None
            ),
            "operations": [
                item.model_dump(mode="json")
                for item in evidence
            ],
            "cleaned_up": cleaned_up,
        }
        provenance_path = output / "cinefactory_premiere_provenance.json"
        provenance_path.write_text(
            json.dumps(
                provenance,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return PremiereSandboxResult(
            project_path=str(project_path),
            operation_evidence=evidence,
            export_output=(
                str(export_path) if export_path.is_file() else None
            ),
            provenance_path=str(provenance_path),
            cleaned_up=cleaned_up,
            findings=findings,
        )


def make_premiere_fixture(
    target: str | Path,
) -> Path:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFMPEG_REQUIRED_FOR_PREMIERE_MASTERY")
    proc = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=gray:s=320x180:r=24:d=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            "-shortest",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(target),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if (
        proc.returncode != 0
        or not target.is_file()
        or target.stat().st_size <= 0
    ):
        raise RuntimeError(
            "PREMIERE_FIXTURE_CREATE_FAILED:"
            + (proc.stderr or proc.stdout or "")[-800:]
        )
    return target
