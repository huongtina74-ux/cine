from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from .bridge import AdobeBridgeHTTPClient


class PhotoshopRuntimeProbe(BaseModel):
    installed: bool
    bridge_reachable: bool
    plugin_registered: bool
    host_version: str | None = None
    plugin_version: str | None = None
    capabilities: set[str] = Field(default_factory=set)
    findings: list[str] = Field(default_factory=list)


class PhotoshopOperationEvidence(BaseModel):
    operation: str
    passed: bool
    duration_ms: int = Field(default=0, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class PhotoshopSandboxResult(BaseModel):
    operation_evidence: list[PhotoshopOperationEvidence] = Field(default_factory=list)
    exported_files: list[str] = Field(default_factory=list)
    provenance_path: str | None = None
    cleaned_up: bool = False
    findings: list[str] = Field(default_factory=list)


class PhotoshopRuntimeAdapter:
    SUPPORTED_OPERATIONS = {
        "layers",
        "masks",
        "smart objects",
        "text",
        "composite",
        "thumbnail",
        "batch export",
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
        self.base_url = base_url or os.getenv(
            "CINEFACTORY_ADOBE_BRIDGE",
            "http://127.0.0.1:8791",
        )
        self.token_path = (
            self.root / "data" / "studio" / "adobe_bridge" / "token.txt"
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
            token = self.token_path.read_text(encoding="utf-8").strip()
        self._client = AdobeBridgeHTTPClient(
            base_url=self.base_url,
            token=token,
            timeout_seconds=3,
        )
        return self._client

    def probe(self, *, installed: bool) -> PhotoshopRuntimeProbe:
        try:
            registered = self._bridge().client("photoshop")
        except Exception as exc:
            return PhotoshopRuntimeProbe(
                installed=installed,
                bridge_reachable=False,
                plugin_registered=False,
                findings=[
                    f"ADOBE_BRIDGE_UNAVAILABLE:{type(exc).__name__}:{exc}"
                ],
            )
        if registered is None:
            return PhotoshopRuntimeProbe(
                installed=installed,
                bridge_reachable=True,
                plugin_registered=False,
                findings=["PHOTOSHOP_UXP_PLUGIN_NOT_REGISTERED"],
            )
        age = time.time() - registered.last_seen.timestamp()
        fresh = age <= 5.0
        findings: list[str] = []
        if not fresh:
            findings.append("PHOTOSHOP_UXP_PLUGIN_HEARTBEAT_STALE")
        if not installed:
            findings.append("PHOTOSHOP_NOT_INSTALLED")
        return PhotoshopRuntimeProbe(
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
        timeout_seconds: float = 60.0,
    ) -> dict[str, Any]:
        if operation not in self.SUPPORTED_OPERATIONS and operation not in {
            "probe",
            "sandbox create",
            "sandbox close",
        }:
            raise ValueError(f"unsupported Photoshop operation: {operation}")
        result = self._bridge().execute(
            "photoshop",
            operation,
            payload or {},
            timeout_seconds=timeout_seconds,
        )
        if not result.ok:
            raise RuntimeError(
                result.error or f"Photoshop operation failed: {operation}"
            )
        return dict(result.payload)

    @staticmethod
    def _timed(
        operation: str,
        fn: Callable[[], dict[str, Any]],
    ) -> PhotoshopOperationEvidence:
        started = time.perf_counter()
        try:
            payload = fn()
            artifacts = [
                str(path)
                for path in payload.get("artifacts", [])
                if path
            ]
            return PhotoshopOperationEvidence(
                operation=operation,
                passed=True,
                duration_ms=max(
                    0,
                    int((time.perf_counter() - started) * 1000),
                ),
                payload=payload,
                artifacts=artifacts,
            )
        except Exception as exc:
            return PhotoshopOperationEvidence(
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
        output_dir: str | Path,
        timeout_seconds: float = 90.0,
    ) -> PhotoshopSandboxResult:
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        png_path = output / "cinefactory_photoshop_mastery.png"
        psd_path = output / "cinefactory_photoshop_mastery.psd"
        evidence: list[PhotoshopOperationEvidence] = []
        findings: list[str] = []
        cleaned_up = False

        create = self._timed(
            "sandbox create",
            lambda: self.execute(
                "sandbox create",
                {
                    "name": "CineFactory Photoshop Mastery",
                    "width": 512,
                    "height": 512,
                },
                timeout_seconds=timeout_seconds,
            ),
        )
        if not create.passed:
            return PhotoshopSandboxResult(
                operation_evidence=[],
                findings=create.findings,
            )

        try:
            calls = [
                (
                    "layers",
                    {
                        "name": "CineFactory Layer",
                        "opacity": 85,
                    },
                ),
                (
                    "text",
                    {
                        "name": "CineFactory Text",
                        "contents": "CineFactory",
                        "font_size": 32,
                        "x": 128,
                        "y": 256,
                    },
                ),
                ("masks", {}),
                ("smart objects", {}),
                ("composite", {}),
                (
                    "thumbnail",
                    {"width": 320, "height": 180},
                ),
                (
                    "batch export",
                    {
                        "png_path": str(png_path),
                        "psd_path": str(psd_path),
                    },
                ),
            ]
            for operation, payload in calls:
                evidence.append(
                    self._timed(
                        operation,
                        lambda op=operation, pl=payload: self.execute(
                            op,
                            pl,
                            timeout_seconds=timeout_seconds,
                        ),
                    )
                )
        finally:
            try:
                self.execute(
                    "sandbox close",
                    {},
                    timeout_seconds=30,
                )
                cleaned_up = True
            except Exception as exc:
                findings.append(
                    f"SANDBOX_CLOSE_FAILED:{type(exc).__name__}:{exc}"
                )

        exported = [
            str(path)
            for path in (png_path, psd_path)
            if path.is_file() and path.stat().st_size > 0
        ]
        provenance = {
            "adapter": "photoshop-uxp",
            "exported_files": exported,
            "operations": [
                item.model_dump(mode="json") for item in evidence
            ],
            "cleaned_up": cleaned_up,
        }
        provenance_path = output / "cinefactory_photoshop_provenance.json"
        provenance_path.write_text(
            json.dumps(
                provenance,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        return PhotoshopSandboxResult(
            operation_evidence=evidence,
            exported_files=exported,
            provenance_path=str(provenance_path),
            cleaned_up=cleaned_up,
            findings=findings,
        )
