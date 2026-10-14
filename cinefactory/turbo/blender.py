from __future__ import annotations

import json
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Literal, Sequence
from uuid import uuid4

from pydantic import BaseModel, Field

from cinefactory.block_animation.contracts import BlenderAnimationJob
from cinefactory.block_animation.execution import BlockExecutionPlanner


class Transform(BaseModel):
    location: tuple[float, float, float] = (0, 0, 0)
    rotation_euler: tuple[float, float, float] = (0, 0, 0)
    scale: tuple[float, float, float] = (1, 1, 1)


class BlenderEntity(BaseModel):
    entity_id: str
    primitive: Literal["cube", "sphere", "cylinder"] = "cube"
    transform: Transform = Field(default_factory=Transform)


class BlenderCamera(BaseModel):
    transform: Transform = Field(default_factory=Transform)
    lens_mm: float = 50


class BlenderPrevisJob(BaseModel):
    project_id: str
    shot_id: str
    entities: list[BlenderEntity] = Field(default_factory=list)
    camera: BlenderCamera = Field(default_factory=BlenderCamera)
    width: int = 640
    height: int = 360
    output_path: str


class BlenderHeadlessWorker:
    def __init__(self, root: Path, blender_executable: str = "blender"):
        self.root = Path(root).resolve()
        self.exe = shutil.which(blender_executable) or blender_executable
        self.script = (self.root / "scripts" / "blender_scene_worker.py").resolve()

    def execute(self, job):
        out = Path(job.output_path).resolve()
        if self.root not in out.parents:
            raise ValueError("Blender output must stay inside CineFactory root")
        out.parent.mkdir(parents=True, exist_ok=True)
        jp = out.with_suffix(".blender-job.json")
        jp.write_text(job.model_dump_json(indent=2), encoding="utf-8")
        p = subprocess.run(
            [self.exe, "-b", "--python", str(self.script), "--", str(jp)],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if p.returncode != 0:
            raise RuntimeError(f"Blender failed: {p.stderr[-4000:]}")
        if not out.exists():
            raise RuntimeError("Blender completed without expected output")
        return str(out)


PREFIX = "__CINEFACTORY_JSON__"


class PersistentBlenderWorker:
    def __init__(
        self,
        root: Path,
        blender_executable: str = "blender",
        *,
        command: Sequence[str] | None = None,
        startup_timeout: int = 120,
        job_timeout: int = 1800,
    ):
        self.root = Path(root).resolve()
        self.exe = shutil.which(blender_executable) or blender_executable
        self.script = (self.root / "scripts" / "blender_animation_worker.py").resolve()
        self.command = list(command) if command else None
        self.startup_timeout = startup_timeout
        self.job_timeout = job_timeout
        self._proc = None
        self._reader = None
        self._responses: queue.Queue = queue.Queue()
        self._lock = threading.RLock()
        self._logs: list[str] = []
        self.last_result = None

    @property
    def pid(self):
        return self._proc.pid if self._proc and self._proc.poll() is None else None

    @property
    def is_alive(self):
        return self._proc is not None and self._proc.poll() is None

    def _cmd(self):
        return list(self.command) if self.command else [
            self.exe,
            "-b",
            "--python",
            str(self.script),
            "--",
            "--persistent",
            "--root",
            str(self.root),
        ]

    def _read_stdout(self):
        for raw in self._proc.stdout:
            line = raw.rstrip("\r\n")
            if line.startswith(PREFIX):
                try:
                    self._responses.put(json.loads(line[len(PREFIX):]))
                except json.JSONDecodeError:
                    self._logs.append(line)
            elif line:
                self._logs.append(line)
                self._logs = self._logs[-250:]

    def _wait_response(self, *, request_id, timeout, allow_ready=False):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._proc is not None and self._proc.poll() is not None and self._responses.empty():
                raise RuntimeError(
                    f"persistent Blender worker exited rc={self._proc.returncode}: {' | '.join(self._logs[-20:])}"
                )
            try:
                msg = self._responses.get(timeout=min(.25, max(.01, deadline - time.monotonic())))
            except queue.Empty:
                continue
            if allow_ready and msg.get("type") == "ready":
                return msg
            if request_id is not None and msg.get("request_id") == request_id:
                return msg
        raise TimeoutError(
            f"persistent Blender worker response timeout; logs={' | '.join(self._logs[-20:])}"
        )

    def start(self):
        with self._lock:
            if self.is_alive:
                return {"type": "ready", "pid": self.pid, "reused": True}
            self._responses = queue.Queue()
            self._logs = []
            self._proc = subprocess.Popen(
                self._cmd(),
                cwd=self.root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self._reader = threading.Thread(target=self._read_stdout, daemon=True)
            self._reader.start()
            return self._wait_response(request_id=None, timeout=self.startup_timeout, allow_ready=True)

    def _request(self, op, payload=None, *, timeout=None):
        with self._lock:
            self.start()
            rid = f"BLREQ_{uuid4().hex[:12]}"
            msg = {"request_id": rid, "op": op, **(payload or {})}
            self._proc.stdin.write(PREFIX + json.dumps(msg, ensure_ascii=False, separators=(",", ":")) + "\n")
            self._proc.stdin.flush()
            r = self._wait_response(request_id=rid, timeout=timeout or self.job_timeout)
            if not r.get("ok", False):
                raise RuntimeError(r.get("error") or f"Blender worker operation {op} failed")
            return r

    def ping(self):
        return self._request("ping", timeout=min(10, self.startup_timeout))

    def execute_animation(self, job: BlenderAnimationJob):
        out = Path(job.output_path).resolve()
        if out != self.root and self.root not in out.parents:
            raise ValueError("Blender output must stay inside CineFactory root")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.unlink(missing_ok=True)
        plan = BlockExecutionPlanner.plan(job)
        payload = {"job": job.model_dump(mode="json"), "plan": plan}
        try:
            r = self._request("render", payload)
        except (BrokenPipeError, RuntimeError) as first:
            self.close(force=True)
            try:
                r = self._request("render", payload)
            except Exception:
                raise first
        if not out.exists():
            raise RuntimeError(f"Blender worker reported success without expected output {out}")
        self.last_result = r
        return str(out)

    def close(self, *, force=False):
        with self._lock:
            p = self._proc
            if p is None:
                return
            if p.poll() is None and not force:
                try:
                    self._request("shutdown", timeout=5)
                except Exception:
                    pass
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=5)
            self._proc = None
