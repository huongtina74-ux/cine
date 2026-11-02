"""cf_minecraft_rcon: RCON protocol, local-only guard, success/failure detection (fake in-process server)."""
import socket
import struct
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cf_minecraft_rcon as rc  # noqa: E402


def _fake_server(password, replies):
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def serve():
        conn, _ = srv.accept()
        def read(n):
            b = b""
            while len(b) < n:
                b += conn.recv(n - len(b))
            return b
        while True:
            try:
                size = struct.unpack("<i", read(4))[0]
            except Exception:
                break
            pkt = read(size)
            rid, kind = struct.unpack("<ii", pkt[:8])
            body = pkt[8:-2].decode()
            if kind == 3:
                out_id, text = (rid if body == password else -1), ""
            else:
                out_id, text = rid, replies.get(body, "Unknown or incomplete command, see below for error")
            data = struct.pack("<ii", out_id, 0) + text.encode() + b"\x00\x00"
            conn.sendall(struct.pack("<i", len(data)) + data)
        conn.close()
        srv.close()

    threading.Thread(target=serve, daemon=True).start()
    return port


def _server_dir(tmp_path, port, pw="pw123", rcon="true"):
    (tmp_path / "server.properties").write_text(
        f"enable-rcon={rcon}\nrcon.port={port}\nrcon.password={pw}\nserver-ip=127.0.0.1\n", encoding="utf-8")
    return str(tmp_path)


def test_run_commands_and_detect_failures(tmp_path, capsys):
    port = _fake_server("pw123", {"time set night": "Set the time to 13000",
                                  "execute if block 2 101 -2 minecraft:gravel": "Test passed"})
    code = rc.run(_server_dir(tmp_path, port), ["/time set night", "execute if block 2 101 -2 minecraft:gravel", "bogus"])
    out = capsys.readouterr().out
    assert code == 1 and "RCON_FAIL::commands=3::failed=1" in out
    assert "pw123" not in out


def test_bad_password_and_remote_host_refused(tmp_path):
    port = _fake_server("right", {})
    with pytest.raises(PermissionError):
        rc.Rcon("wrong", "127.0.0.1", port)
    with pytest.raises(ValueError):
        rc.Rcon("x", "192.168.1.20", 25575)


def test_rcon_disabled_and_command_file(tmp_path, capsys):
    assert rc.run(_server_dir(tmp_path, 1, rcon="false"), ["list"]) == 2
    f = tmp_path / "set.mcfunction"
    f.write_text("# house\nfill -2 100 -2 2 103 2 minecraft:oak_planks hollow\n\nsave-all flush\n", encoding="utf-8")
    assert rc.load_commands(f) == ["fill -2 100 -2 2 103 2 minecraft:oak_planks hollow", "save-all flush"]
