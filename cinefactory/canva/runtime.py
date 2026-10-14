from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class CanvaRuntimeProbe(BaseModel):
    authorized: bool
    user_id: str | None = None
    team_id: str | None = None
    capabilities: set[str] = Field(default_factory=set)
    findings: list[str] = Field(default_factory=list)


class CanvaMasteryFixture(BaseModel):
    brand_template_id: str
    text_field: str
    image_field: str
    asset_id: str
    design_id: str
    resize_width: int = 1080
    resize_height: int = 1350
    export_type: str = "png"


class CanvaOperationEvidence(BaseModel):
    operation: str
    passed: bool
    duration_ms: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class CanvaSandboxResult(BaseModel):
    operation_evidence: list[CanvaOperationEvidence] = Field(default_factory=list)
    provenance_path: str | None = None
    findings: list[str] = Field(default_factory=list)


class CanvaRuntimeAdapter:
    API = "https://api.canva.com/rest/v1"

    def __init__(
        self,
        root: str | Path,
        *,
        access_token: str | None = None,
        api_base: str | None = None,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.root = Path(root)
        self.access_token = (
            access_token
            or os.getenv("CANVA_ACCESS_TOKEN")
        )
        self.api_base = (api_base or self.API).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.access_token:
            raise RuntimeError("CANVA_ACCESS_TOKEN_MISSING")
        data = (
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if payload is not None
            else None
        )
        request = urllib.request.Request(
            self.api_base + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw = response.read()
                return (
                    json.loads(raw.decode("utf-8"))
                    if raw else {}
                )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"CANVA_HTTP_{exc.code}:{detail[:1000]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"CANVA_CONNECTION_FAILED:{exc}"
            ) from exc

    def probe(self) -> CanvaRuntimeProbe:
        if not self.access_token:
            return CanvaRuntimeProbe(
                authorized=False,
                findings=["CANVA_ACCESS_TOKEN_MISSING"],
            )
        try:
            user = self._request("GET", "/users/me")
            capabilities = self._request(
                "GET",
                "/users/me/capabilities",
            )
        except Exception as exc:
            return CanvaRuntimeProbe(
                authorized=False,
                findings=[f"{type(exc).__name__}:{exc}"],
            )
        return CanvaRuntimeProbe(
            authorized=True,
            user_id=user.get("user", {}).get("id")
            or user.get("id"),
            team_id=user.get("team", {}).get("id")
            or user.get("team_id"),
            capabilities=set(capabilities.get("capabilities", [])),
        )

    def brand_template_dataset(self, template_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/brand-templates/{urllib.parse.quote(template_id, safe='')}/dataset",
        )

    def _wait_job(
        self,
        path: str,
        *,
        timeout_seconds: float = 120.0,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = self._request("GET", path)
            job = response.get("job", response)
            status = job.get("status")
            if status == "success":
                return response
            if status == "failed":
                raise RuntimeError(
                    "CANVA_JOB_FAILED:"
                    + json.dumps(job.get("error", {}))
                )
            time.sleep(0.5)
        raise TimeoutError(f"CANVA_JOB_TIMEOUT:{path}")

    def autofill(
        self,
        *,
        brand_template_id: str,
        data: dict[str, Any],
        title: str,
        timeout_seconds: float = 120.0,
    ) -> dict[str, Any]:
        created = self._request(
            "POST",
            "/autofills",
            {
                "type": "create_from_brand_template",
                "brand_template_id": brand_template_id,
                "title": title,
                "data": data,
            },
        )
        job = created.get("job", {})
        job_id = job.get("id")
        if not job_id:
            raise RuntimeError("CANVA_AUTOFILL_JOB_ID_MISSING")
        return self._wait_job(
            f"/autofills/{urllib.parse.quote(str(job_id), safe='')}",
            timeout_seconds=timeout_seconds,
        )

    def resize(
        self,
        *,
        design_id: str,
        width: int,
        height: int,
        timeout_seconds: float = 120.0,
    ) -> dict[str, Any]:
        created = self._request(
            "POST",
            "/resizes",
            {
                "design_id": design_id,
                "design_type": {
                    "type": "custom",
                    "width": width,
                    "height": height,
                },
            },
        )
        job_id = created.get("job", {}).get("id")
        if not job_id:
            raise RuntimeError("CANVA_RESIZE_JOB_ID_MISSING")
        return self._wait_job(
            f"/resizes/{urllib.parse.quote(str(job_id), safe='')}",
            timeout_seconds=timeout_seconds,
        )

    def export(
        self,
        *,
        design_id: str,
        export_type: str,
        output_dir: str | Path,
        timeout_seconds: float = 120.0,
    ) -> list[str]:
        created = self._request(
            "POST",
            "/exports",
            {
                "design_id": design_id,
                "format": {"type": export_type},
            },
        )
        job_id = created.get("job", {}).get("id")
        if not job_id:
            raise RuntimeError("CANVA_EXPORT_JOB_ID_MISSING")
        response = self._wait_job(
            f"/exports/{urllib.parse.quote(str(job_id), safe='')}",
            timeout_seconds=timeout_seconds,
        )
        urls = response.get("job", {}).get("urls", [])
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        artifacts: list[str] = []
        for index, url in enumerate(urls):
            target = output / f"canva_export_{index + 1}.{export_type}"
            with urllib.request.urlopen(
                urllib.request.Request(url, method="GET"),
                timeout=60,
            ) as downloaded:
                target.write_bytes(downloaded.read())
            if target.is_file() and target.stat().st_size > 0:
                artifacts.append(str(target))
        if not artifacts:
            raise RuntimeError("CANVA_EXPORT_DOWNLOAD_MISSING")
        return artifacts

    @staticmethod
    def _design_from_job(response: dict[str, Any]) -> str | None:
        job = response.get("job", {})
        result = job.get("result", {})
        design = result.get("design", {})
        return design.get("id")

    def sandbox_exercise(
        self,
        *,
        fixture: CanvaMasteryFixture,
        output_dir: str | Path,
        timeout_seconds: float = 120.0,
    ) -> CanvaSandboxResult:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        evidence: list[CanvaOperationEvidence] = []

        def record(operation: str, fn):
            started = time.perf_counter()
            try:
                metadata, artifacts = fn()
                evidence.append(
                    CanvaOperationEvidence(
                        operation=operation,
                        passed=True,
                        duration_ms=max(
                            0,
                            int((time.perf_counter() - started) * 1000),
                        ),
                        metadata=metadata,
                        artifacts=artifacts,
                    )
                )
            except Exception as exc:
                evidence.append(
                    CanvaOperationEvidence(
                        operation=operation,
                        passed=False,
                        duration_ms=max(
                            0,
                            int((time.perf_counter() - started) * 1000),
                        ),
                        findings=[f"{type(exc).__name__}:{exc}"],
                    )
                )

        dataset_holder: dict[str, Any] = {}
        text_design: dict[str, str | None] = {"id": None}
        image_design: dict[str, str | None] = {"id": None}
        resized_design: dict[str, str | None] = {"id": None}

        def brand_template():
            response = self.brand_template_dataset(
                fixture.brand_template_id
            )
            dataset = response.get("dataset", {})
            dataset_holder.update(dataset)
            passed_fields = {
                fixture.text_field,
                fixture.image_field,
            } <= set(dataset)
            if not passed_fields:
                raise RuntimeError("CANVA_AUTOFILL_FIELDS_MISSING")
            return (
                {
                    "fields": sorted(dataset),
                    "template_id": fixture.brand_template_id,
                },
                [],
            )

        record("brand template", brand_template)

        def text_replacement():
            if dataset_holder.get(fixture.text_field, {}).get("type") != "text":
                raise RuntimeError("CANVA_TEXT_FIELD_TYPE_MISMATCH")
            response = self.autofill(
                brand_template_id=fixture.brand_template_id,
                data={
                    fixture.text_field: {
                        "type": "text",
                        "text": "CineFactory Mastery",
                    }
                },
                title="CineFactory Text Mastery",
                timeout_seconds=timeout_seconds,
            )
            design_id = self._design_from_job(response)
            if not design_id:
                raise RuntimeError("CANVA_TEXT_AUTOFILL_DESIGN_MISSING")
            text_design["id"] = design_id
            return ({"design_id": design_id}, [])

        record("text replacement", text_replacement)

        def asset_replacement():
            field_type = dataset_holder.get(
                fixture.image_field, {}
            ).get("type")
            if field_type not in {"image", "video"}:
                raise RuntimeError("CANVA_ASSET_FIELD_TYPE_MISMATCH")
            response = self.autofill(
                brand_template_id=fixture.brand_template_id,
                data={
                    fixture.image_field: {
                        "type": field_type,
                        "asset_id": fixture.asset_id,
                    }
                },
                title="CineFactory Asset Mastery",
                timeout_seconds=timeout_seconds,
            )
            design_id = self._design_from_job(response)
            if not design_id:
                raise RuntimeError("CANVA_ASSET_AUTOFILL_DESIGN_MISSING")
            image_design["id"] = design_id
            return ({"design_id": design_id}, [])

        record("asset replacement", asset_replacement)

        def social_derivative():
            response = self.resize(
                design_id=fixture.design_id,
                width=fixture.resize_width,
                height=fixture.resize_height,
                timeout_seconds=timeout_seconds,
            )
            design_id = self._design_from_job(response)
            if not design_id:
                raise RuntimeError("CANVA_RESIZED_DESIGN_MISSING")
            resized_design["id"] = design_id
            return (
                {
                    "design_id": design_id,
                    "width": fixture.resize_width,
                    "height": fixture.resize_height,
                },
                [],
            )

        record("social derivative", social_derivative)

        def export_op():
            target_design = (
                resized_design["id"]
                or text_design["id"]
                or image_design["id"]
                or fixture.design_id
            )
            artifacts = self.export(
                design_id=str(target_design),
                export_type=fixture.export_type,
                output_dir=output / "exports",
                timeout_seconds=timeout_seconds,
            )
            return (
                {
                    "design_id": target_design,
                    "format": fixture.export_type,
                },
                artifacts,
            )

        record("export", export_op)

        provenance_path = output / "cinefactory_canva_provenance.json"
        provenance_path.write_text(
            json.dumps(
                {
                    "adapter": "canva-rest-v1",
                    "fixture": fixture.model_dump(mode="json"),
                    "operations": [
                        item.model_dump(mode="json") for item in evidence
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return CanvaSandboxResult(
            operation_evidence=evidence,
            provenance_path=str(provenance_path),
        )
