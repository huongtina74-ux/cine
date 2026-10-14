from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from cinefactory.adobe.bridge import (
    AdobeBridgeHTTPClient,
    AdobeBridgeServer,
)


def _request(
    base_url: str,
    token: str,
    method: str,
    path: str,
    payload: dict | None = None,
):
    data = (
        json.dumps(payload).encode("utf-8")
        if payload is not None
        else None
    )
    request = urllib.request.Request(
        base_url + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        raw = response.read()
        return response.status, (
            json.loads(raw.decode("utf-8")) if raw else None
        )


def test_bridge_rejects_non_loopback_binding(tmp_path: Path):
    with pytest.raises(ValueError, match="loopback"):
        AdobeBridgeServer(
            root=tmp_path / "bridge",
            host="0.0.0.0",
            port=0,
        )


def test_bridge_rejects_bad_token(tmp_path: Path):
    server = AdobeBridgeServer(
        root=tmp_path / "bridge",
        port=0,
        token="a" * 48,
    ).start()
    try:
        request = urllib.request.Request(
            server.base_url + "/v1/health",
            headers={"Authorization": "Bearer wrong"},
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request, timeout=2)
        assert error.value.code == 401
    finally:
        server.stop()


def test_cross_process_command_roundtrip_and_evidence(tmp_path: Path):
    root = tmp_path / "bridge"
    token = "b" * 48
    server = AdobeBridgeServer(
        root=root,
        port=0,
        token=token,
    ).start()
    client = AdobeBridgeHTTPClient(
        base_url=server.base_url,
        token=token,
    )
    try:
        status, _ = _request(
            server.base_url,
            token,
            "POST",
            "/v1/register",
            {
                "tool_id": "premiere",
                "host_version": "26.5.0-test",
                "plugin_version": "1.0.0",
                "capabilities": ["probe", "import media"],
            },
        )
        assert status == 200
        registered = client.client("premiere")
        assert registered is not None
        assert registered.host_version == "26.5.0-test"

        command = client.enqueue(
            "premiere",
            "probe",
            {"sandbox": True},
        )
        query = urllib.parse.urlencode(
            {"tool_id": "premiere"}
        )
        status, raw_command = _request(
            server.base_url,
            token,
            "GET",
            f"/v1/commands/next?{query}",
        )
        assert status == 200
        assert raw_command["command_id"] == command.command_id
        assert raw_command["operation"] == "probe"

        status, _ = _request(
            server.base_url,
            token,
            "POST",
            "/v1/results",
            {
                "command_id": command.command_id,
                "tool_id": "premiere",
                "operation": "probe",
                "ok": True,
                "payload": {
                    "hostVersion": "26.5.0-test",
                    "capabilities": ["probe"],
                },
            },
        )
        assert status == 200
        result = client.wait(
            command.command_id,
            timeout_seconds=2,
        )
        assert result.ok is True
        assert result.payload["hostVersion"] == "26.5.0-test"

        assert (
            root
            / "evidence"
            / "commands"
            / f"{command.command_id}.json"
        ).is_file()
        assert (
            root
            / "evidence"
            / "results"
            / f"{command.command_id}.json"
        ).is_file()
    finally:
        server.stop()


def test_http_client_refuses_non_loopback():
    with pytest.raises(ValueError, match="loopback"):
        AdobeBridgeHTTPClient(
            base_url="http://192.168.1.10:8791",
            token="c" * 48,
        )


def test_server_token_persists(tmp_path: Path):
    root = tmp_path / "bridge"
    first = AdobeBridgeServer(root=root, port=0)
    token = first.token
    assert len(token) >= 32
    second = AdobeBridgeServer(root=root, port=0)
    assert second.token == token
