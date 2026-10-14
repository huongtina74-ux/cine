from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from cinefactory.core.policy import FactoryPolicy
from cinefactory.executors.comfyui import ComfyUIExecutor
from cinefactory.studio.execution_mastery import ExecutionMasteryRunner
from cinefactory.studio.kernel import build_studio_kernel


OBJECT_INFO = {
    "CheckpointLoaderSimple": {
        "input": {
            "required": {
                "ckpt_name": [["model-a.safetensors", "model-b.safetensors"]]
            }
        }
    },
    "KSampler": {
        "input": {
            "required": {
                "seed": ["INT"],
                "model": ["MODEL"],
            }
        }
    },
    "SaveImage": {
        "input": {
            "required": {
                "images": ["IMAGE"],
                "filename_prefix": ["STRING"],
            }
        }
    },
}

WORKFLOW = {
    "1": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "model-a.safetensors"},
    },
    "2": {
        "class_type": "KSampler",
        "inputs": {"seed": 12345, "model": ["1", 0]},
    },
    "3": {
        "class_type": "SaveImage",
        "inputs": {"images": ["2", 0], "filename_prefix": "mastery"},
    },
}


class _Handler(BaseHTTPRequestHandler):
    submitted: list[dict] = []

    def log_message(self, format, *args):  # noqa: A003
        return

    def _json(self, payload: dict, status: int = 200):
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/object_info":
            self._json(OBJECT_INFO)
            return
        if parsed.path == "/history/prompt-1":
            self._json(
                {
                    "prompt-1": {
                        "outputs": {
                            "3": {
                                "images": [
                                    {
                                        "filename": "mastery_00001_.png",
                                        "subfolder": "",
                                        "type": "output",
                                    }
                                ]
                            }
                        },
                        "status": {"status_str": "success"},
                    }
                }
            )
            return
        if parsed.path == "/view":
            raw = b"fake-png-bytes"
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        self._json({"error": "not found"}, 404)

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/prompt":
            self._json({"error": "not found"}, 404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(size).decode("utf-8"))
        self.__class__.submitted.append(payload)
        self._json({"prompt_id": "prompt-1"})


class FakeComfyServer:
    def __enter__(self):
        _Handler.submitted.clear()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"
        return self

    def __exit__(self, exc_type, exc, tb):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def _policy() -> FactoryPolicy:
    return FactoryPolicy(
        {
            "mode": "ZERO_METERED_API",
            "production": {"allow_free_non_metered_services": False},
            "network": {
                "production_worker_public_internet": False,
                "allow_loopback_lan": True,
            },
        }
    )


def test_preflight_validates_nodes_models_and_hashes():
    with FakeComfyServer() as server:
        executor = ComfyUIExecutor(
            _policy(),
            base_url=server.base_url,
            poll_seconds=0.01,
            timeout=2,
        )
        report = executor.preflight(WORKFLOW)
        assert report.reachable
        assert report.safe
        assert report.valid
        assert report.missing_node_types == []
        assert report.invalid_model_inputs == []
        assert report.model_requirements[
            "1:CheckpointLoaderSimple:ckpt_name"
        ] == "model-a.safetensors"
        assert len(report.workflow_sha256 or "") == 64
        assert len(report.object_info_sha256 or "") == 64


def test_preflight_fails_closed_for_missing_node_and_model():
    broken = {
        **WORKFLOW,
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "missing-model.safetensors"},
        },
        "9": {
            "class_type": "UnknownCustomNode",
            "inputs": {},
        },
    }
    with FakeComfyServer() as server:
        executor = ComfyUIExecutor(_policy(), base_url=server.base_url)
        report = executor.preflight(broken)
        assert report.valid is False
        assert report.missing_node_types == ["UnknownCustomNode"]
        assert report.invalid_model_inputs == [
            "1:CheckpointLoaderSimple:ckpt_name:missing-model.safetensors"
        ]


def test_execute_queues_collects_output_and_provenance(tmp_path: Path):
    with FakeComfyServer() as server:
        executor = ComfyUIExecutor(
            _policy(),
            base_url=server.base_url,
            poll_seconds=0.01,
            timeout=2,
        )
        result = executor.execute(
            {
                "workflow": WORKFLOW,
                "output_dir": str(tmp_path / "outputs"),
                "workflow_id": "wf.test",
                "workflow_version": "1",
                "model_id": "model.test",
                "model_revision": "rev-123",
            }
        )
        assert result.ok
        assert len(result.artifacts) == 1
        assert Path(result.artifacts[0]).read_bytes() == b"fake-png-bytes"
        assert _Handler.submitted
        assert _Handler.submitted[0]["prompt"] == WORKFLOW
        provenance = result.metadata["provenance"]
        assert Path(provenance["provenance_path"]).is_file()
        sidecar = json.loads(
            Path(provenance["provenance_path"]).read_text(encoding="utf-8")
        )
        assert sidecar["prompt_id"] == "prompt-1"
        assert sidecar["seed"] == 12345
        assert provenance["prompt_id"] == "prompt-1"
        assert provenance["seed"] == 12345
        assert provenance["workflow_id"] == "wf.test"
        assert provenance["workflow_version"] == "1"
        assert provenance["model_id"] == "model.test"
        assert provenance["model_revision"] == "rev-123"
        assert provenance["model_requirements"][
            "1:CheckpointLoaderSimple:ckpt_name"
        ] == "model-a.safetensors"


def test_execute_blocks_unsafe_public_network_workflow():
    unsafe = {
        "1": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 7,
                "model": ["x", 0],
                "provider": "https://api.example.com/generate",
            },
        }
    }
    with FakeComfyServer() as server:
        executor = ComfyUIExecutor(_policy(), base_url=server.base_url)
        result = executor.execute({"workflow": unsafe})
        assert result.ok is False
        assert result.error == "ComfyUI workflow preflight failed"
        findings = result.metadata["preflight"]["findings"]
        assert any(item.startswith("PUBLIC_NETWORK_URL:") for item in findings)
        assert not _Handler.submitted


def test_adapter_registry_accepts_reachable_local_service_without_main_py(
    tmp_path: Path,
    monkeypatch,
):
    with FakeComfyServer() as server:
        monkeypatch.setenv("CINEFACTORY_COMFYUI", server.base_url)
        kernel = build_studio_kernel(tmp_path)
        probe = kernel.tool_adapters.probe(kernel, "comfyui")
        assert probe.installed is False
        assert probe.runtime_reachable is True
        assert probe.available is True
        assert probe.runtime_endpoint == server.base_url
        assert "TOOL_NOT_INSTALLED" not in probe.findings


def test_comfyui_execution_mastery_validates_approved_runtime(
    tmp_path: Path,
    monkeypatch,
):
    config = tmp_path / "config"
    config.mkdir(parents=True)
    (config / "factory_policy.yaml").write_text(
        """
mode: ZERO_METERED_API
production:
  allow_free_non_metered_services: false
network:
  production_worker_public_internet: false
  allow_loopback_lan: true
""".strip(),
        encoding="utf-8",
    )

    workflow_dir = tmp_path / "workflows" / "comfyui"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "mastery.json").write_text(
        json.dumps(WORKFLOW, indent=2),
        encoding="utf-8",
    )
    (workflow_dir / "mastery.manifest.yaml").write_text(
        """
workflow_id: comfy.mastery
version: "1"
executor_id: local.comfyui
media_type: image
model_id: model.test
model_revision: rev-123
workflow_file: mastery.json
local_only: true
notes:
  - deterministic mastery workflow
""".strip(),
        encoding="utf-8",
    )

    model_dir = tmp_path / "models"
    model_dir.mkdir(parents=True)
    (model_dir / "registry.yaml").write_text(
        """
models:
  - model_id: model.test
    revision: rev-123
    modality: image
    code_license: test
    weights_license: test
    commercial_use_reviewed: true
    output_terms_reviewed: true
    approved_for_production: true
""".strip(),
        encoding="utf-8",
    )

    with FakeComfyServer() as server:
        monkeypatch.setenv("CINEFACTORY_COMFYUI", server.base_url)
        kernel = build_studio_kernel(tmp_path)
        report = ExecutionMasteryRunner(kernel).evaluate("comfyui")

    assert report.runtime_available is True
    assert report.installed is False
    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    assert set(report.passed_operations) == {
        "workflow load",
        "node validation",
        "prompt queue",
        "seed control",
        "output collection",
        "provenance",
    }
    assert (
        kernel.skills.get(
            "tool.comfyui.generative",
            "current",
        ).status.value
        == "VALIDATED"
    )
