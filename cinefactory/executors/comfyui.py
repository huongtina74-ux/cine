from __future__ import annotations

import hashlib
import ipaddress
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.core.policy import ExecutorDescriptor
from cinefactory.domain.enums import ExecutorKind, NetworkScope
from cinefactory.executors.base import ExecutionResult, Executor
from cinefactory.workflows.safety import WorkflowSafetyValidator


class ComfyUIPreflightReport(BaseModel):
    reachable: bool
    safe: bool
    valid: bool
    node_types_required: list[str] = Field(default_factory=list)
    node_types_available: list[str] = Field(default_factory=list)
    missing_node_types: list[str] = Field(default_factory=list)
    model_requirements: dict[str, str] = Field(default_factory=dict)
    invalid_model_inputs: list[str] = Field(default_factory=list)
    workflow_sha256: str | None = None
    object_info_sha256: str | None = None
    findings: list[str] = Field(default_factory=list)


class ComfyUIExecutor(Executor):
    """Local/LAN ComfyUI runtime adapter with fail-closed workflow preflight.

    It only accepts loopback/private-LAN endpoints, validates workflow safety,
    checks node classes and enumerable model/resource inputs against /object_info,
    submits API-format workflow JSON to /prompt, polls /history/{prompt_id},
    downloads outputs through /view, and records deterministic provenance.
    """

    descriptor = ExecutorDescriptor(
        executor_id="local.comfyui",
        kind=ExecutorKind.LOCAL,
        category="generation",
        network_scope=NetworkScope.LOOPBACK_LAN,
        notes="Local/LAN only. Never expose ComfyUI directly to the public Internet.",
    )

    def __init__(
        self,
        policy,
        base_url: str = "http://127.0.0.1:8188",
        poll_seconds: float = 1.0,
        timeout: int = 900,
    ):
        super().__init__(policy)
        self.base_url = base_url.rstrip("/")
        self.poll_seconds = poll_seconds
        self.timeout = timeout
        self.safety = WorkflowSafetyValidator()
        self._validate_local_url()

    def _validate_local_url(self) -> None:
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme != "http" or not parsed.hostname:
            raise ValueError("ComfyUIExecutor requires a local HTTP URL")
        if parsed.hostname == "localhost":
            return
        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError as exc:
            raise ValueError(
                "ComfyUIExecutor only accepts localhost or literal private IP addresses"
            ) from exc
        if not (address.is_loopback or address.is_private):
            raise ValueError(
                "ComfyUIExecutor only accepts loopback/private-LAN endpoints"
            )

    @staticmethod
    def _stable_hash(value: Any) -> str:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _json_request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        *,
        timeout: int = 10,
    ) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else {}
        except urllib.error.URLError as exc:
            raise RuntimeError(f"ComfyUI connection failed: {exc}") from exc

    def health(self) -> dict[str, Any]:
        """Return local service capability metadata without mutating queue state."""
        object_info = self._json_request("GET", "/object_info")
        return {
            "reachable": True,
            "base_url": self.base_url,
            "node_types": len(object_info),
            "object_info_sha256": self._stable_hash(object_info),
        }

    def object_info(self) -> dict[str, Any]:
        info = self._json_request("GET", "/object_info")
        if not isinstance(info, dict) or not info:
            raise RuntimeError("ComfyUI /object_info returned no node definitions")
        return info

    @staticmethod
    def _workflow_nodes(workflow: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
        nodes: list[tuple[str, dict[str, Any]]] = []
        for node_id, node in workflow.items():
            if not isinstance(node, dict):
                continue
            class_type = node.get("class_type")
            if isinstance(class_type, str) and class_type:
                nodes.append((str(node_id), node))
        return nodes

    @staticmethod
    def _enum_choices(definition: Any) -> list[Any] | None:
        # ComfyUI object_info commonly exposes enum inputs as [["a","b",...], {...}].
        if not isinstance(definition, (list, tuple)) or not definition:
            return None
        first = definition[0]
        if isinstance(first, list):
            return first
        return None

    def preflight(self, workflow: dict[str, Any]) -> ComfyUIPreflightReport:
        if not isinstance(workflow, dict) or not workflow:
            return ComfyUIPreflightReport(
                reachable=False,
                safe=False,
                valid=False,
                findings=["WORKFLOW_MISSING"],
            )

        safety = self.safety.review(workflow)
        workflow_hash = self._stable_hash(workflow)
        try:
            info = self.object_info()
        except Exception as exc:
            return ComfyUIPreflightReport(
                reachable=False,
                safe=safety.passed,
                valid=False,
                workflow_sha256=workflow_hash,
                findings=[*safety.findings, f"OBJECT_INFO_UNAVAILABLE:{exc}"],
            )

        required = sorted(
            {
                str(node.get("class_type"))
                for _, node in self._workflow_nodes(workflow)
                if node.get("class_type")
            }
        )
        available = sorted(set(required) & set(info))
        missing = sorted(set(required) - set(info))
        invalid_models: list[str] = []
        model_requirements: dict[str, str] = {}

        for node_id, node in self._workflow_nodes(workflow):
            class_type = str(node["class_type"])
            node_info = info.get(class_type)
            if not isinstance(node_info, dict):
                continue
            inputs_schema = node_info.get("input")
            if not isinstance(inputs_schema, dict):
                continue
            declared: dict[str, Any] = {}
            for group in ("required", "optional"):
                values = inputs_schema.get(group, {})
                if isinstance(values, dict):
                    declared.update(values)
            actual_inputs = node.get("inputs", {})
            if not isinstance(actual_inputs, dict):
                continue
            for input_name, actual in actual_inputs.items():
                choices = self._enum_choices(declared.get(input_name))
                if not choices or not isinstance(actual, str):
                    continue
                # Links are arrays; strings against finite enums are resource/model picks.
                if actual not in choices:
                    invalid_models.append(
                        f"{node_id}:{class_type}:{input_name}:{actual}"
                    )
                elif any(
                    token in input_name.lower()
                    for token in (
                        "model",
                        "ckpt",
                        "checkpoint",
                        "vae",
                        "lora",
                        "control_net",
                        "controlnet",
                        "clip",
                    )
                ):
                    model_requirements[
                        f"{node_id}:{class_type}:{input_name}"
                    ] = actual

        findings = list(safety.findings)
        findings.extend(f"MISSING_NODE_TYPE:{item}" for item in missing)
        findings.extend(
            f"INVALID_ENUM_OR_MODEL_INPUT:{item}" for item in invalid_models
        )
        valid = safety.passed and not missing and not invalid_models
        return ComfyUIPreflightReport(
            reachable=True,
            safe=safety.passed,
            valid=valid,
            node_types_required=required,
            node_types_available=available,
            missing_node_types=missing,
            model_requirements=model_requirements,
            invalid_model_inputs=invalid_models,
            workflow_sha256=workflow_hash,
            object_info_sha256=self._stable_hash(info),
            findings=findings,
        )

    def _download_outputs(
        self,
        item: dict[str, Any],
        *,
        output_dir: str | Path | None,
    ) -> list[str]:
        outputs = item.get("outputs", {})
        files: list[str] = []
        for node in outputs.values() if isinstance(outputs, dict) else []:
            for key in ("images", "gifs", "videos", "audio"):
                media_items = (
                    node.get(key, [])
                    if isinstance(node, dict)
                    else []
                )
                for media in media_items:
                    filename = (
                        media.get("filename")
                        if isinstance(media, dict)
                        else None
                    )
                    if not filename:
                        continue
                    if output_dir:
                        out_dir = Path(output_dir)
                        out_dir.mkdir(parents=True, exist_ok=True)
                        query = urllib.parse.urlencode(
                            {
                                "filename": filename,
                                "subfolder": media.get("subfolder", ""),
                                "type": media.get("type", "output"),
                            }
                        )
                        req = urllib.request.Request(
                            self.base_url + "/view?" + query,
                            method="GET",
                        )
                        with urllib.request.urlopen(
                            req,
                            timeout=60,
                        ) as response:
                            target = out_dir / Path(filename).name
                            target.write_bytes(response.read())
                            files.append(str(target))
                    else:
                        files.append(filename)
        return files

    def execute(self, payload: dict[str, Any]) -> ExecutionResult:
        self.validate_policy()
        workflow = payload.get("workflow")
        if not isinstance(workflow, dict) or not workflow:
            return ExecutionResult(
                False,
                [],
                {"executor": self.descriptor.executor_id},
                "Missing ComfyUI workflow JSON",
            )

        preflight = self.preflight(workflow)
        if not preflight.valid:
            return ExecutionResult(
                False,
                [],
                {
                    "executor": self.descriptor.executor_id,
                    "preflight": preflight.model_dump(mode="json"),
                },
                "ComfyUI workflow preflight failed",
            )

        seed = payload.get("seed")
        if seed is None:
            # Try to recover a seed embedded in common workflow inputs.
            for _, node in self._workflow_nodes(workflow):
                inputs = node.get("inputs", {})
                if not isinstance(inputs, dict):
                    continue
                for key in ("seed", "noise_seed"):
                    value = inputs.get(key)
                    if isinstance(value, int):
                        seed = value
                        break
                if seed is not None:
                    break

        submit_payload: dict[str, Any] = {"prompt": workflow}
        client_id = payload.get("client_id")
        if isinstance(client_id, str) and client_id:
            submit_payload["client_id"] = client_id
        submit = self._json_request("POST", "/prompt", submit_payload)
        prompt_id = submit.get("prompt_id")
        if not prompt_id:
            return ExecutionResult(
                False,
                [],
                {
                    "submit": submit,
                    "preflight": preflight.model_dump(mode="json"),
                },
                "ComfyUI did not return prompt_id",
            )

        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            history = self._json_request(
                "GET",
                f"/history/{urllib.parse.quote(str(prompt_id), safe='')}",
            )
            item = history.get(str(prompt_id))
            if item:
                status = item.get("status", {})
                status_str = (
                    status.get("status_str")
                    if isinstance(status, dict)
                    else None
                )
                if status_str == "error":
                    return ExecutionResult(
                        False,
                        [],
                        {
                            "prompt_id": prompt_id,
                            "history": item,
                            "preflight": preflight.model_dump(mode="json"),
                        },
                        "ComfyUI reported error",
                    )
                try:
                    files = self._download_outputs(
                        item,
                        output_dir=payload.get("output_dir"),
                    )
                except urllib.error.URLError as exc:
                    return ExecutionResult(
                        False,
                        [],
                        {
                            "prompt_id": prompt_id,
                            "preflight": preflight.model_dump(mode="json"),
                        },
                        f"Failed to download ComfyUI output: {exc}",
                    )
                provenance = {
                    "executor": self.descriptor.executor_id,
                    "base_url": self.base_url,
                    "prompt_id": prompt_id,
                    "workflow_sha256": preflight.workflow_sha256,
                    "object_info_sha256": preflight.object_info_sha256,
                    "node_types": preflight.node_types_required,
                    "model_requirements": preflight.model_requirements,
                    "seed": seed,
                    "workflow_id": payload.get("workflow_id"),
                    "workflow_version": payload.get("workflow_version"),
                    "model_id": payload.get("model_id"),
                    "model_revision": payload.get("model_revision"),
                }
                output_dir = payload.get("output_dir")
                if output_dir:
                    provenance_path = (
                        Path(output_dir) / "cinefactory_provenance.json"
                    )
                    provenance_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )
                    provenance_path.write_text(
                        json.dumps(
                            provenance,
                            ensure_ascii=False,
                            indent=2,
                            sort_keys=True,
                        ),
                        encoding="utf-8",
                    )
                    provenance["provenance_path"] = str(provenance_path)
                return ExecutionResult(
                    True,
                    files,
                    {
                        "prompt_id": prompt_id,
                        "history": item,
                        "preflight": preflight.model_dump(mode="json"),
                        "provenance": provenance,
                    },
                )
            time.sleep(self.poll_seconds)

        return ExecutionResult(
            False,
            [],
            {
                "prompt_id": prompt_id,
                "preflight": preflight.model_dump(mode="json"),
            },
            f"ComfyUI timed out after {self.timeout}s",
        )
