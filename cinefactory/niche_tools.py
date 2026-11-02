"""Per-niche tool router: each niche declares, per production stage, which tools it may use.

    python -m cinefactory.niche_tools --niche slow_english_a2          # what would be used today
    python -m cinefactory.niche_tools --niche slow_english_a2 --json

config/niches/<niche>/toolkit.yaml lists candidates per stage in order of preference. The router
picks the first candidate that is (1) installed - every `requires` path exists under the repo -
(2) cleared for commercial use, and (3) marked production (unless allow_dev=True, used by tests
and dry runs). Nothing is guessed: a stage with no usable tool is reported as MISSING with the
reason each candidate was skipped, so the owner sees exactly what to install.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ToolChoice:
    stage: str
    tool: str | None
    kind: str | None = None
    production: bool = False
    license: str = ""
    skipped: list[str] = field(default_factory=list)
    notes: str = ""

    @property
    def ok(self) -> bool:
        return self.tool is not None


@dataclass
class NicheToolkit:
    niche: str
    label: str
    stages: dict[str, list[dict]]
    targets: dict
    hold: list[dict]
    root: Path

    @classmethod
    def load(cls, niche: str, root: Path | None = None) -> "NicheToolkit":
        root = Path(root or ROOT)
        path = root / "config" / "niches" / niche / "toolkit.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"no toolkit for niche '{niche}': {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if niche == "slow_english_a2":
            from cinefactory.slow_english_unified import audit
            report = audit(root)
            if report["logic_consistency"] != "PASS":
                raise ValueError("Bell & Leaf active toolkit/Canon mismatch: " + ", ".join(report["profile_failures"]))
        return cls(niche=data.get("niche", niche), label=data.get("label", niche), stages=data.get("stages") or {},
                   targets=data.get("targets") or {}, hold=data.get("hold") or [], root=root)

    def _requires(self, tool: dict) -> list[str]:
        if os.name != "nt" and "requires_posix" in tool:
            return list(tool.get("requires_posix") or [])
        return list(tool.get("requires") or [])

    def budget(self) -> dict:
        """config/budget.yaml: {monthly_usd: 0, approved_tools: []}. Paid tools need both."""
        path = self.root / "config" / "budget.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None
        return data or {"monthly_usd": 0, "approved_tools": []}

    def resolve(self, stage: str, *, allow_dev: bool = False, prefer: str | None = None) -> ToolChoice:
        skipped: list[str] = []
        held = {h.get("id") for h in self.hold}
        budget = self.budget()
        candidates = list(self.stages.get(stage, []))
        if prefer:
            candidates.sort(key=lambda t: t.get("id") != prefer)
        for tool in candidates:
            tid = tool.get("id")
            if tid in held:
                skipped.append(f"{tid}: on HOLD")
                continue
            if not tool.get("commercial", False):
                skipped.append(f"{tid}: not cleared for commercial use")
                continue
            if not tool.get("production", False) and not allow_dev:
                skipped.append(f"{tid}: dev/test only")
                continue
            if tool.get("paid") and not (float(budget.get("monthly_usd") or 0) > 0
                                         and tid in (budget.get("approved_tools") or [])):
                skipped.append(f"{tid}: paid - owner has not approved a budget for it (config/budget.yaml)")
                continue
            missing = [r for r in self._requires(tool) if not (self.root / r).exists()]
            if missing:
                skipped.append(f"{tid}: not installed (missing {missing[0]})")
                continue
            return ToolChoice(stage, tid, tool.get("kind"), bool(tool.get("production")), tool.get("license", ""),
                              skipped, tool.get("notes", ""))
        return ToolChoice(stage, None, skipped=skipped)

    def plan(self, *, allow_dev: bool = False, prefer: dict[str, str] | None = None) -> dict[str, ToolChoice]:
        prefer = prefer or {}
        return {stage: self.resolve(stage, allow_dev=allow_dev, prefer=prefer.get(stage)) for stage in self.stages}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--niche", required=True)
    p.add_argument("--allow-dev", action="store_true", help="allow test-only fallbacks")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    kit = NicheToolkit.load(args.niche)
    plan = kit.plan(allow_dev=args.allow_dev)
    if args.json:
        print(json.dumps({s: c.__dict__ for s, c in plan.items()}, indent=2, ensure_ascii=False))
    else:
        print(f"=== {kit.label} ===")
        for stage, c in plan.items():
            line = f"{stage:10s} -> {c.tool or 'MISSING'}" + ("" if c.production or not c.tool else "  (dev only)")
            print(line)
            for s in c.skipped:
                print(f"{'':14s}skip {s}")
    ready = all(c.ok and (c.production or args.allow_dev) for c in plan.values())
    print("TOOLKIT_READY" if ready else "TOOLKIT_INCOMPLETE")
    return 0 if ready else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
