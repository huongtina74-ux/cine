"""Drive a LOCAL Minecraft Java server with RCON: stage sets, signs, time, datapack functions - no hands on the game.

    python tools/cf_minecraft_rcon.py --server-dir C:/.../cine_mc/server --cmd "time set night" --cmd "save-all flush"
    python tools/cf_minecraft_rcon.py --server-dir ... --file config/niches/minecraft/savewalker/sets/s01e01_house.mcfunction

Reads rcon.port / rcon.password from <server-dir>/server.properties (never printed). Refuses non-local hosts:
the server must bind 127.0.0.1 (server-ip=127.0.0.1). Prints one JSON line per command and a final status line.
OBSERVED 2026-11-02 on the owner PC (server 1.21.1, Java 21): fill/setblock/sign NBT/time/datapack function/save-all
all returned success over RCON. Stdlib only, so it also runs inside Blender's Python.
"""
from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
from pathlib import Path

LOCAL = {"127.0.0.1", "localhost", "::1"}


class Rcon:
    LOGIN, COMMAND = 3, 2

    def __init__(self, password: str, host: str = "127.0.0.1", port: int = 25575, timeout: float = 10.0, sock=None):
        if host not in LOCAL:
            raise ValueError("RCON is only allowed against a local server (127.0.0.1)")
        self.sock = sock or socket.create_connection((host, port), timeout=timeout)
        self.req = 0
        if self._send(self.LOGIN, password)[0] == -1:
            raise PermissionError("RCON authentication failed")

    def _recv(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("RCON connection closed")
            buf += chunk
        return buf

    def _send(self, kind: int, body: str) -> tuple[int, str]:
        self.req += 1
        payload = struct.pack("<ii", self.req, kind) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        size = struct.unpack("<i", self._recv(4))[0]
        pkt = self._recv(size)
        rid, _ = struct.unpack("<ii", pkt[:8])
        return rid, pkt[8:-2].decode("utf-8", "replace")

    def command(self, cmd: str) -> str:
        cmd = cmd.strip().lstrip("/")
        if len(cmd.encode("utf-8")) > 1440:
            raise ValueError("command too long for one RCON packet")
        return self._send(self.COMMAND, cmd)[1]

    def close(self) -> None:
        self.sock.close()


def read_props(server_dir: str | Path) -> dict[str, str]:
    props = {}
    for line in Path(server_dir, "server.properties").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            props[k.strip()] = v.strip()
    return props


def load_commands(path: str | Path) -> list[str]:
    return [ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]


FAIL_WORDS = ("Unknown or incomplete command", "Incorrect argument", "Test failed", "Could not", "Expected", "No entity")


def run(server_dir: str, commands: list[str], sock=None) -> int:
    p = read_props(server_dir)
    if p.get("enable-rcon") != "true":
        print("RCON_OFF::set enable-rcon=true in server.properties")
        return 2
    host = p.get("server-ip") or "127.0.0.1"
    r = Rcon(p.get("rcon.password", ""), host if host else "127.0.0.1", int(p.get("rcon.port", "25575")), sock=sock)
    bad = 0
    try:
        for c in commands:
            out = r.command(c)
            ok = not any(w in out for w in FAIL_WORDS)
            bad += not ok
            print(json.dumps({"cmd": c[:120], "ok": ok, "reply": out[:300]}, ensure_ascii=False))
    finally:
        r.close()
    print(f"RCON_{'OK' if not bad else 'FAIL'}::commands={len(commands)}::failed={bad}")
    return 0 if not bad else 1


def main(argv=None) -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--server-dir", required=True)
    a.add_argument("--cmd", action="append", default=[])
    a.add_argument("--file", default="")
    x = a.parse_args(argv)
    cmds = list(x.cmd) + (load_commands(x.file) if x.file else [])
    if not cmds:
        a.error("give --cmd or --file")
    return run(x.server_dir, cmds)


if __name__ == "__main__":
    sys.exit(main())
