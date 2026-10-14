from __future__ import annotations

import json
import secrets
import threading
import time
import urllib.parse
from collections import defaultdict, deque
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AdobeBridgeCommand(BaseModel):
    command_id: str = Field(
        default_factory=lambda: f"ADBCMD_{uuid4().hex[:16]}"
    )
    tool_id: str
    operation: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class AdobeBridgeResult(BaseModel):
    command_id: str
    tool_id: str
    operation: str
    ok: bool
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    completed_at: datetime = Field(default_factory=utcnow)


class AdobeBridgeClient(BaseModel):
    tool_id: str
    host_version: str | None = None
    plugin_version: str | None = None
    capabilities: set[str] = Field(default_factory=set)
    last_seen: datetime = Field(default_factory=utcnow)


class AdobeBridgeStore:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else None
        self._lock = threading.RLock()
        self._queues: dict[str, deque[AdobeBridgeCommand]] = defaultdict(deque)
        self._results: dict[str, AdobeBridgeResult] = {}
        self._clients: dict[str, AdobeBridgeClient] = {}
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
            (self.root / "commands").mkdir(exist_ok=True)
            (self.root / "results").mkdir(exist_ok=True)

    def enqueue(self, command: AdobeBridgeCommand) -> AdobeBridgeCommand:
        with self._lock:
            self._queues[command.tool_id].append(command)
            if self.root is not None:
                path = self.root / "commands" / f"{command.command_id}.json"
                path.write_text(command.model_dump_json(indent=2), encoding="utf-8")
            return command

    def next(self, tool_id: str) -> AdobeBridgeCommand | None:
        with self._lock:
            queue = self._queues[tool_id]
            return queue.popleft() if queue else None

    def result(self, result: AdobeBridgeResult) -> AdobeBridgeResult:
        with self._lock:
            self._results[result.command_id] = result
            if self.root is not None:
                path = self.root / "results" / f"{result.command_id}.json"
                path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
            return result

    def get_result(self, command_id: str) -> AdobeBridgeResult | None:
        with self._lock:
            return self._results.get(command_id)

    def register(self, client: AdobeBridgeClient) -> AdobeBridgeClient:
        with self._lock:
            client.last_seen = utcnow()
            self._clients[client.tool_id] = client
            return client

    def heartbeat(self, tool_id: str) -> AdobeBridgeClient | None:
        with self._lock:
            client = self._clients.get(tool_id)
            if client is not None:
                client.last_seen = utcnow()
            return client

    def client(self, tool_id: str) -> AdobeBridgeClient | None:
        with self._lock:
            return self._clients.get(tool_id)

    def healthy(self, tool_id: str, *, max_age_seconds: float = 5.0) -> bool:
        client = self.client(tool_id)
        if client is None:
            return False
        age = (utcnow() - client.last_seen).total_seconds()
        return age <= max_age_seconds


class AdobeBridgeServer:
    def __init__(
        self,
        *,
        root: str | Path,
        host: str = "127.0.0.1",
        port: int = 8791,
        token: str | None = None,
    ) -> None:
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("Adobe bridge must bind to loopback only")
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.host = host
        self.port = port
        self.token_path = self.root / "token.txt"
        self.token = token or self._load_or_create_token()
        self.store = AdobeBridgeStore(self.root / "evidence")
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def _load_or_create_token(self) -> str:
        if self.token_path.is_file():
            value = self.token_path.read_text(encoding="utf-8").strip()
            if len(value) >= 32:
                return value
        value = secrets.token_urlsafe(48)
        self.token_path.write_text(value, encoding="utf-8")
        return value

    def _handler(self):
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "CineFactoryAdobeBridge/1.0"

            def log_message(self, fmt, *args):
                return

            def _authorized(self) -> bool:
                header = self.headers.get("Authorization", "")
                return secrets.compare_digest(
                    header,
                    f"Bearer {bridge.token}",
                )

            def _send_json(self, payload: Any, status: int = 200) -> None:
                raw = json.dumps(
                    payload,
                    ensure_ascii=False,
                    default=str,
                ).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header(
                    "Access-Control-Allow-Headers",
                    "Authorization, Content-Type",
                )
                self.send_header(
                    "Access-Control-Allow-Methods",
                    "GET, POST, OPTIONS",
                )
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _body(self) -> dict:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0:
                    return {}
                return json.loads(self.rfile.read(size).decode("utf-8"))

            def do_OPTIONS(self):
                self._send_json({"ok": True})

            def do_GET(self):
                if not self._authorized():
                    self._send_json(
                        {"error": "unauthorized"},
                        HTTPStatus.UNAUTHORIZED,
                    )
                    return
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/v1/health":
                    clients = {
                        key: item.model_dump(mode="json")
                        for key, item in bridge.store._clients.items()
                    }
                    self._send_json(
                        {
                            "ok": True,
                            "server": "cinefactory-adobe-bridge",
                            "clients": clients,
                        }
                    )
                    return
                if parsed.path.startswith("/v1/results/"):
                    command_id = parsed.path.rsplit("/", 1)[-1]
                    result = bridge.store.get_result(command_id)
                    if result is None:
                        self.send_response(HTTPStatus.NO_CONTENT)
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        return
                    self._send_json(result.model_dump(mode="json"))
                    return
                if parsed.path == "/v1/commands/next":
                    query = urllib.parse.parse_qs(parsed.query)
                    tool_id = (query.get("tool_id") or [""])[0]
                    if not tool_id:
                        self._send_json(
                            {"error": "tool_id required"},
                            HTTPStatus.BAD_REQUEST,
                        )
                        return
                    bridge.store.heartbeat(tool_id)
                    command = bridge.store.next(tool_id)
                    if command is None:
                        self.send_response(HTTPStatus.NO_CONTENT)
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        return
                    self._send_json(command.model_dump(mode="json"))
                    return
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

            def do_POST(self):
                if not self._authorized():
                    self._send_json(
                        {"error": "unauthorized"},
                        HTTPStatus.UNAUTHORIZED,
                    )
                    return
                try:
                    body = self._body()
                except Exception as exc:
                    self._send_json(
                        {"error": f"invalid json: {exc}"},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/v1/commands":
                    command = AdobeBridgeCommand.model_validate(body)
                    bridge.store.enqueue(command)
                    self._send_json(command.model_dump(mode="json"))
                    return
                if parsed.path == "/v1/register":
                    client = AdobeBridgeClient.model_validate(body)
                    bridge.store.register(client)
                    self._send_json({"ok": True})
                    return
                if parsed.path == "/v1/results":
                    result = AdobeBridgeResult.model_validate(body)
                    bridge.store.result(result)
                    bridge.store.heartbeat(result.tool_id)
                    self._send_json({"ok": True})
                    return
                self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

        return Handler

    def start(self) -> "AdobeBridgeServer":
        if self._server is not None:
            return self
        self._server = ThreadingHTTPServer(
            (self.host, self.port),
            self._handler(),
        )
        self.port = int(self._server.server_address[1])
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="cinefactory-adobe-bridge",
            daemon=True,
        )
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._server = None
        self._thread = None

    def enqueue(
        self,
        tool_id: str,
        operation: str,
        payload: dict[str, Any] | None = None,
    ) -> AdobeBridgeCommand:
        return self.store.enqueue(
            AdobeBridgeCommand(
                tool_id=tool_id,
                operation=operation,
                payload=payload or {},
            )
        )

    def wait(
        self,
        command_id: str,
        *,
        timeout_seconds: float = 30.0,
        poll_seconds: float = 0.05,
    ) -> AdobeBridgeResult:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            result = self.store.get_result(command_id)
            if result is not None:
                return result
            time.sleep(poll_seconds)
        raise TimeoutError(f"Adobe bridge command timed out: {command_id}")

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class AdobeBridgeHTTPClient:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8791",
        token: str,
        timeout_seconds: float = 10.0,
    ) -> None:
        parsed = urllib.parse.urlparse(base_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname
            not in {"127.0.0.1", "::1", "localhost"}
        ):
            raise ValueError(
                "Adobe bridge client only accepts loopback HTTP endpoints"
            )
        if len(token) < 32:
            raise ValueError("Adobe bridge token is too short")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        allow_no_content: bool = False,
    ) -> dict[str, Any] | None:
        import urllib.error
        import urllib.request

        data = (
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if payload is not None
            else None
        )
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw = response.read()
                if (
                    allow_no_content
                    and response.status == HTTPStatus.NO_CONTENT
                ):
                    return None
                return (
                    json.loads(raw.decode("utf-8"))
                    if raw
                    else {}
                )
        except urllib.error.HTTPError as exc:
            if (
                allow_no_content
                and exc.code == HTTPStatus.NO_CONTENT
            ):
                return None
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Adobe bridge HTTP {exc.code}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Adobe bridge connection failed: {exc}"
            ) from exc

    def health(self) -> dict[str, Any]:
        return dict(self._request("GET", "/v1/health") or {})

    def client(self, tool_id: str) -> AdobeBridgeClient | None:
        health = self.health()
        raw = health.get("clients", {}).get(tool_id)
        return (
            AdobeBridgeClient.model_validate(raw)
            if isinstance(raw, dict)
            else None
        )

    def enqueue(
        self,
        tool_id: str,
        operation: str,
        payload: dict[str, Any] | None = None,
    ) -> AdobeBridgeCommand:
        command = AdobeBridgeCommand(
            tool_id=tool_id,
            operation=operation,
            payload=payload or {},
        )
        raw = self._request(
            "POST",
            "/v1/commands",
            command.model_dump(mode="json"),
        )
        return AdobeBridgeCommand.model_validate(raw)

    def get_result(
        self,
        command_id: str,
    ) -> AdobeBridgeResult | None:
        raw = self._request(
            "GET",
            f"/v1/results/{urllib.parse.quote(command_id, safe='')}",
            allow_no_content=True,
        )
        return (
            AdobeBridgeResult.model_validate(raw)
            if isinstance(raw, dict)
            else None
        )

    def wait(
        self,
        command_id: str,
        *,
        timeout_seconds: float = 60.0,
        poll_seconds: float = 0.1,
    ) -> AdobeBridgeResult:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            result = self.get_result(command_id)
            if result is not None:
                return result
            time.sleep(poll_seconds)
        raise TimeoutError(
            f"Adobe bridge result timed out: {command_id}"
        )

    def execute(
        self,
        tool_id: str,
        operation: str,
        payload: dict[str, Any] | None = None,
        *,
        timeout_seconds: float = 60.0,
    ) -> AdobeBridgeResult:
        command = self.enqueue(tool_id, operation, payload)
        return self.wait(
            command.command_id,
            timeout_seconds=timeout_seconds,
        )
